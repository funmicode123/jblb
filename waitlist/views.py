import os
import resend
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from jblb import settings
from .models import Waitlist, EmailOutbox
from .serializers import WaitlistSerializer
from .services.email_service import render_verification_email
from .services.outbox_service import queue_email

from users.services.hedera_service import create_hedera_account

resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_LIMIT = 3
EMAIL_WINDOW = 3600

User = get_user_model()


def can_send_verification(email, ip):
    email_key = f"waitlist_email:{email}"
    ip_key = f"waitlist_ip:{ip or 'unknown'}"

    email_count = cache.get(email_key, 0)
    ip_count = cache.get(ip_key, 0)

    if email_count >= EMAIL_LIMIT or ip_count >= EMAIL_LIMIT:
        return False

    cache.set(email_key, email_count + 1, EMAIL_WINDOW)
    cache.set(ip_key, ip_count + 1, EMAIL_WINDOW)
    return True


def generate_unique_token():
    while True:
        token = get_random_string(40)
        if not Waitlist.objects.filter(verification_token=token).exists():
            return token


class PostWaitlistAPIView(APIView):
    def post(self, request):
        client_ip = request.META.get("REMOTE_ADDR")
        email = request.data.get("email")
        referral_code = request.query_params.get("referral_code")

        if not can_send_verification(email, client_ip):
            return Response(
                {"error": "Too many attempts. Try again later."},
                status=429
            )

        serializer = WaitlistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            with transaction.atomic():
                waitlist = serializer.save(
                    is_verified=False,
                    verification_token=generate_unique_token(),
                    token_created=timezone.now()
                )

                if referral_code:
                    referrer = Waitlist.objects.filter(
                        referral_code=referral_code
                    ).first()
                    if referrer and referrer != waitlist:
                        waitlist.referred_by = referrer
                        waitlist.save(update_fields=["referred_by"])

                frontend_url = os.getenv('FRONTEND_URL')
                backend_base_url = os.getenv('BACKEND_BASE_URL')
                
                if frontend_url:
                    verify_url = f"{frontend_url.rstrip('/')}/verify?token={waitlist.verification_token}"
                elif backend_base_url:
                    verify_url = f"{backend_base_url.rstrip('/')}/api/waitlist/verify/?token={waitlist.verification_token}"
                else:
                    verify_url = request.build_absolute_uri(
                        reverse('verify-waitlist') + f"?token={waitlist.verification_token}"
                    )

                html_body = render_verification_email(
                    waitlist.custom_id,
                    verify_url,
                    waitlist.referral_code
                )

                queue_email(
                    to=waitlist.email,
                    subject=f"#{waitlist.custom_id} – Confirm Your JBLB Spot!",
                    html=html_body
                )

            return Response({
                "message": "Check your email! Share your link to earn rewards",
                "your_id": waitlist.custom_id,
                "your_referral_link": f"{frontend_url}/waitlist?ref="
                                      f"{waitlist.referral_code}"
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class VerifyWaitlistView(APIView):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response(
                {"error": "Missing verification token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(
            Waitlist,
            verification_token=token,
            is_verified=False
        )

        if user.token_created and (timezone.now() - user.token_created).total_seconds() > 86400:
            return Response(
                {"error": "Verification link has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.verification_token = None
        user.token_created = None
        user.save()

        # Create or get user account automatically with Hedera integration
        if not user.user:
            # Generate a secure password
            password = get_random_string(12)
            
            # Create Hedera blockchain account first
            try:
                hedera_account_data = create_hedera_account()
                
                # Create Django user account with Hedera integration
                django_user = User.objects.create_user(
                    username=user.username,
                    email=user.email,
                    password=password,
                    # Include Hedera account data
                    wallet_address=hedera_account_data["evm_address"],
                    hedera_account_id=hedera_account_data["hedera_account_id"],
                    hedera_public_key=hedera_account_data["hedera_public_key"],
                    hedera_private_key=hedera_account_data["hedera_private_key"]
                )
            except Exception as e:
                # If Hedera account creation fails, still create the user but log the error
                django_user = User.objects.create_user(
                    username=user.username,
                    email=user.email,
                    password=password
                )
                print(f"Error creating Hedera account for user {user.email}: {str(e)}")
            
            user.user = django_user
            user.save(update_fields=['user'])
            
            # TODO: Optionally send password via email for first login
            # For now, we'll use JWT tokens for immediate access
        else:
            django_user = user.user

        # Calculate new verified position
        position = Waitlist.objects.filter(is_verified=True).count()

        # Generate JWT tokens for immediate dashboard access
        refresh = RefreshToken.for_user(django_user)
        
        # Get referral stats if they exist
        try:
            from referrals.models import ReferralStats
            referral_stats = ReferralStats.objects.get(user=django_user)
            total_referrals = referral_stats.total_referrals
            verified_referrals = referral_stats.verified_referrals
        except:
            total_referrals = 0
            verified_referrals = 0

        response_data = {
            "message": "Welcome to JBLB! Your account is ready.",
            "your_id": user.custom_id,
            "position": position,
            "total_verified": position,
            "total_referrals": total_referrals,
            "verified_referrals": verified_referrals,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "dashboard_url": "/api/referrals/dashboard/",
            "instructions": "Use the access token for immediate dashboard access. No additional signup required!"
        }
        
        # Include Hedera account information if available
        if hasattr(django_user, 'hedera_account_id') and django_user.hedera_account_id:
            response_data.update({
                "wallet_address": django_user.wallet_address,
                "hedera_account_id": django_user.hedera_account_id
            })

        return Response(response_data, status=status.HTTP_200_OK)


class ListWaitlistAPIView(APIView):
    def get(self, request):
        total = Waitlist.objects.filter(is_verified=True).count()
        return Response({"total_on_waitlist": total})


class ReferralStatsView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        user = get_object_or_404(Waitlist, referral_code=code)
        count = user.referrals.filter(is_verified=True).count()

        return Response({
            "your_id": user.custom_id,
            "referral_code": user.referral_code,
            "total_referred": count,
            "message": f"You have {count} verified referrals!"
        })


class ClearWaitlistView(APIView):
    """
    Endpoint to clear waitlist entries and email outbox for testing purposes.
    Only accessible by admin users.
    """
    permission_classes = [IsAdminUser]
    
    def delete(self, request):
        # Get query parameters
        emails = request.query_params.getlist('email', [])
        delete_all = request.query_params.get('all', False)
        
        if emails:
            # Delete specific emails
            deleted_counts = {}
            for email in emails:
                waitlist_count = Waitlist.objects.filter(email=email).delete()[0]
                outbox_count = EmailOutbox.objects.filter(to=email).delete()[0]
                deleted_counts[email] = {
                    'waitlist': waitlist_count,
                    'outbox': outbox_count
                }
            
            return Response({
                'message': 'Successfully cleared waitlist entries',
                'deleted_counts': deleted_counts
            }, status=status.HTTP_200_OK)
            
        elif delete_all:
            # Delete all entries
            waitlist_count = Waitlist.objects.count()
            outbox_count = EmailOutbox.objects.count()
            
            Waitlist.objects.all().delete()
            EmailOutbox.objects.all().delete()
            
            return Response({
                'message': 'Successfully cleared all waitlist entries',
                'deleted_counts': {
                    'waitlist': waitlist_count,
                    'outbox': outbox_count
                }
            }, status=status.HTTP_200_OK)
            
        else:
            return Response({
                'error': 'Please specify either email parameters or all=true'
            }, status=status.HTTP_400_BAD_REQUEST)


class GoogleWaitlistView(APIView):
    """
    Handle waitlist registration via Google authentication
    """
    def post(self, request):
        try:
            # Get Google user data from social auth
            google_email = request.data.get('google_email')
            google_name = request.data.get('google_name')
            google_picture = request.data.get('google_picture')
            
            if not google_email:
                return Response(
                    {"error": "Google email is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract username from email (before @)
            username = google_email.split('@')[0]
            
            # Check if user already exists in waitlist
            existing_waitlist = Waitlist.objects.filter(
                email=google_email
            ).first()
            
            if existing_waitlist:
                return Response(
                    {"error": "User already registered in waitlist"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create waitlist entry with Google data
            waitlist_data = {
                'username': username,
                'email': google_email,
                'is_verified': True,  # Mark as verified since they authenticated via Google
            }
            
            serializer = WaitlistSerializer(data=waitlist_data)
            if serializer.is_valid():
                waitlist = serializer.save()
                
                # Generate referral code
                waitlist.referral_code = get_random_string(10).upper()
                waitlist.custom_id = f"JBLB-{str(waitlist.id).zfill(5)}"
                waitlist.save()
                
                # Create Django user account automatically
                password = get_random_string(12)
                django_user = User.objects.create_user(
                    username=username,
                    email=google_email,
                    password=password
                )
                waitlist.user = django_user
                waitlist.save(update_fields=['user'])
                
                # Generate JWT tokens for immediate access
                refresh = RefreshToken.for_user(django_user)
                
                return Response({
                    "message": f"Welcome {username}! You're on the waitlist.",
                    "your_id": waitlist.custom_id,
                    "username": username,
                    "email": google_email,
                    "is_verified": True,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "dashboard_url": f"{FRONTEND_URL}/api/referrals/dashboard/"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SupabaseAuthWaitlistView(APIView):
    """
    Handle waitlist registration via Supabase authentication
    Works with any provider supported by Supabase (Google, GitHub, Apple, Twitter, etc.)
    """
    def post(self, request):
        try:
            # Get user data from Supabase authentication
            email = request.data.get('email')
            username = request.data.get('username') or request.data.get('user_name') or request.data.get('full_name')
            provider = request.data.get('provider', 'supabase')  # Which provider was used (Google, GitHub, etc.)
            user_id = request.data.get('user_id')  # Supabase user ID
            referral_code_input = request.data.get('referral_code')  # Optional referral code from someone else
            
            if not email:
                return Response(
                    {"error": "Email is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not username:
                # Extract username from email if not provided
                username = email.split('@')[0]
            
            # Check if user already exists in waitlist
            existing_waitlist = Waitlist.objects.filter(
                email=email
            ).first()
            
            if existing_waitlist:
                # Debug: Check if user exists
                print(f"Existing waitlist user: {existing_waitlist.user}")
                
                # If user already exists, return their existing info
                if existing_waitlist.user:
                    refresh = RefreshToken.for_user(existing_waitlist.user)
                else:
                    # Handle case where waitlist exists but no user account created yet
                    return Response({
                        "error": "Waitlist entry exists but user account not created. Please contact support.",
                        "waitlist_id": existing_waitlist.custom_id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Return user's own referral link
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                referral_link = f"{frontend_url}?ref={existing_waitlist.referral_code}"
                
                response_data = {
                    "message": f"Welcome back {username}! You're already on the waitlist.",
                    "your_id": existing_waitlist.custom_id,
                    "username": existing_waitlist.username,
                    "email": email,
                    "is_verified": existing_waitlist.is_verified,
                    "referral_code": existing_waitlist.referral_code,
                    "referral_link": referral_link,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "dashboard_url": "/api/referrals/dashboard/"
                }
                
                # Only include wallet and Hedera info if user exists
                if existing_waitlist.user:
                    response_data.update({
                        "wallet_address": existing_waitlist.user.wallet_address,
                        "hedera_account_id": existing_waitlist.user.hedera_account_id
                    })
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            # Check if this user is joining via someone else's referral
            referred_by = None
            if referral_code_input:
                try:
                    referred_by = Waitlist.objects.get(referral_code=referral_code_input)
                    print(f"Found referrer: {referred_by}")  # Debug
                except Waitlist.DoesNotExist:
                    # Invalid referral code, continue without referral
                    print(f"Referral code {referral_code_input} not found")  # Debug
                    referred_by = None
                except Exception as e:
                    print(f"Error looking up referral code: {e}")  # Debug
                    referred_by = None

            waitlist_data = {
                'username': username,
                'email': email,
                'is_verified': True,  
            }
            
            serializer = WaitlistSerializer(data=waitlist_data)
            if serializer.is_valid():
                waitlist = serializer.save()
                
                waitlist.referral_code = get_random_string(10).upper()
                
                if referred_by:
                    waitlist.referred_by = referred_by
                
                waitlist.custom_id = f"JBLB-{str(waitlist.id).zfill(5)}"
                waitlist.save()
                
                try:
                    hedera_account_data = create_hedera_account()
                    
                    password = get_random_string(12)
                    django_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        wallet_address=hedera_account_data["evm_address"],
                        hedera_account_id=hedera_account_data["hedera_account_id"],
                        hedera_public_key=hedera_account_data["hedera_public_key"],
                        hedera_private_key=hedera_account_data["hedera_private_key"]
                    )
                except Exception as e:
                    # If Hedera account creation fails, still create the user but log the error
                    password = get_random_string(12)
                    django_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    print(f"Error creating Hedera account for user {email}: {str(e)}")
                
                waitlist.user = django_user
                waitlist.save(update_fields=['user'])
                
                # Generate JWT tokens for immediate access
                refresh = RefreshToken.for_user(django_user)
                
                # Generate referral link for sharing
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                referral_link = f"{frontend_url}?ref={waitlist.referral_code}"
                
                response_data = {
                    "message": f"Welcome {username}! You're on the waitlist.",
                    "your_id": waitlist.custom_id,
                    "username": username,
                    "email": email,
                    "provider": provider,
                    "is_verified": True,
                    "referral_code": waitlist.referral_code,
                    "referral_link": referral_link,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "dashboard_url": f"{frontend_url}/api/referrals/dashboard/"
                }
                
                # Include Hedera account information if available
                if 'hedera_account_data' in locals():
                    response_data.update({
                        "wallet_address": hedera_account_data["evm_address"],
                        "hedera_account_id": hedera_account_data["hedera_account_id"]
                    })
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClerkAuthWaitlistView(APIView):
    """
    Handle waitlist registration via Clerk authentication
    Works with Google, Twitter, and other providers supported by Clerk
    """
    def post(self, request):
        try:
            # Get user data from Clerk authentication
            clerk_user_id = request.data.get('clerk_user_id')
            email = request.data.get('email')
            username = request.data.get('username') or request.data.get('first_name') or request.data.get('full_name')
            provider = request.data.get('provider', 'clerk')  # Which provider was used (Google, Twitter, etc.)
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            picture = request.data.get('picture', '')
            referral_code_input = request.data.get('referral_code')  # Optional referral code from someone else
            
            # Validate required fields
            if not clerk_user_id or not email:
                return Response(
                    {"error": "clerk_user_id and email are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not username:
                # Extract username from email if not provided
                username = email.split('@')[0]
            
            # Check if user already exists in waitlist by clerk_user_id or email
            existing_waitlist = Waitlist.objects.filter(
                email=email
            ).first()
            
            if existing_waitlist:
                # If user already exists, return their existing info
                if existing_waitlist.user:
                    refresh = RefreshToken.for_user(existing_waitlist.user)
                else:
                    # Handle case where waitlist exists but no user account created yet
                    return Response({
                        "error": "Waitlist entry exists but user account not created. Please contact support.",
                        "waitlist_id": existing_waitlist.custom_id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Return user's own referral link
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                referral_link = f"{frontend_url}?ref={existing_waitlist.referral_code}"
                
                response_data = {
                    "message": f"Welcome back {username}! You're already on the waitlist.",
                    "your_id": existing_waitlist.custom_id,
                    "username": existing_waitlist.username,
                    "email": email,
                    "is_verified": existing_waitlist.is_verified,
                    "referral_code": existing_waitlist.referral_code,
                    "referral_link": referral_link,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "dashboard_url": "/api/referrals/dashboard/"
                }
                
                # Only include wallet and Hedera info if user exists
                if existing_waitlist.user:
                    response_data.update({
                        "wallet_address": existing_waitlist.user.wallet_address,
                        "hedera_account_id": existing_waitlist.user.hedera_account_id
                    })
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            # Check if this user is joining via someone else's referral
            referred_by = None
            if referral_code_input:
                try:
                    referred_by = Waitlist.objects.get(referral_code=referral_code_input)
                    print(f"Found referrer: {referred_by}")  # Debug
                except Waitlist.DoesNotExist:
                    # Invalid referral code, continue without referral
                    print(f"Referral code {referral_code_input} not found")  # Debug
                    referred_by = None
                except Exception as e:
                    print(f"Error looking up referral code: {e}")  # Debug
                    referred_by = None
            
            # Create waitlist entry with Clerk user data
            waitlist_data = {
                'username': username,
                'email': email,
                'is_verified': True,  # Mark as verified since they authenticated via Clerk
            }
            
            serializer = WaitlistSerializer(data=waitlist_data)
            if serializer.is_valid():
                waitlist = serializer.save()
                
                # Generate referral code for this user
                waitlist.referral_code = get_random_string(10).upper()
                
                # Set the referrer if applicable
                if referred_by:
                    waitlist.referred_by = referred_by
                
                waitlist.custom_id = f"JBLB-{str(waitlist.id).zfill(5)}"
                waitlist.save()
                
                # Create Hedera blockchain account first
                try:
                    hedera_account_data = create_hedera_account()
                    
                    # Create Django user account with Hedera integration and Clerk data
                    password = get_random_string(12)
                    django_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        # Include Hedera account data
                        wallet_address=hedera_account_data["evm_address"],
                        hedera_account_id=hedera_account_data["hedera_account_id"],
                        hedera_public_key=hedera_account_data["hedera_public_key"],
                        hedera_private_key=hedera_account_data["hedera_private_key"],
                        # Store Clerk user ID for future reference
                        first_name=first_name,
                        last_name=last_name,
                        clerk_user_id=clerk_user_id
                    )
                    
                except Exception as e:
                    # If Hedera account creation fails, still create the user but log the error
                    password = get_random_string(12)
                    django_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        clerk_user_id=clerk_user_id
                    )
                    print(f"Error creating Hedera account for user {email}: {str(e)}")
                
                waitlist.user = django_user
                waitlist.save(update_fields=['user'])
                
                # Generate JWT tokens for immediate access
                refresh = RefreshToken.for_user(django_user)
                
                # Generate referral link for sharing
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                referral_link = f"{frontend_url}?ref={waitlist.referral_code}"
                
                # Send welcome email to the user
                try:
                    # Create welcome email content
                    email_subject = f"Welcome to JBLB #{waitlist.custom_id}!"
                    email_html = f"""
                    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
                        <h2>Welcome to JBLB #{waitlist.custom_id}!</h2>
                        <p>Congratulations {first_name or username}! You've successfully joined the waitlist via {provider.title()} authentication.</p>
                        
                        <div style="background:#f0f8ff;padding:20px;border-radius:8px;margin:20px 0;">
                            <h3>Your Account Details:</h3>
                            <p><strong>User ID:</strong> {waitlist.custom_id}</p>
                            <p><strong>Username:</strong> {username}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Authentication Method:</strong> {provider.title()}</p>
                        </div>
                        
                        <div style="background:#fff3cd;padding:20px;border-radius:8px;margin:20px 0;">
                            <h3>Your Referral Link:</h3>
                            <p>Share this link to invite friends and climb the leaderboard:</p>
                            <input type="text" value="{referral_link}" readonly 
                                   style="width:100%;padding:12px;font-size:16px;border-radius:8px;border:1px solid #ccc;"
                                   onclick="this.select()">
                            <p><strong>Your Referral Code:</strong> {waitlist.referral_code}</p>
                        </div>
                        
                        <hr style="margin:30px 0;">
                        
                        <h3>What's Next?</h3>
                        <ul>
                            <li>Check your dashboard at any time using your access token</li>
                            <li>Invite friends using your referral link above</li>
                            <li>Watch your position on the leaderboard grow!</li>
                        </ul>
                        
                        <p>Thanks for joining us!<br><strong>Team JBLB</strong></p>
                    </div>
                    """
                    
                    # Queue the email
                    queue_email(
                        to=email,
                        subject=email_subject,
                        html=email_html
                    )
                    print(f"Welcome email queued for {email}")
                    
                except Exception as e:
                    print(f"Error queuing welcome email for {email}: {str(e)}")
                
                response_data = {
                    "message": f"Welcome {username}! You're on the waitlist.",
                    "your_id": waitlist.custom_id,
                    "username": username,
                    "email": email,
                    "provider": provider,
                    "is_verified": True,
                    "referral_code": waitlist.referral_code,
                    "referral_link": referral_link,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "dashboard_url": "/api/referrals/dashboard/",
                    "email_sent": True  # Indicate that email was sent
                }
                
                # Include Hedera account information if available
                if 'hedera_account_data' in locals():
                    response_data.update({
                        "wallet_address": hedera_account_data["evm_address"],
                        "hedera_account_id": hedera_account_data["hedera_account_id"]
                    })
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TokenRefreshView(APIView):
    """
    Refresh JWT tokens for verified waitlist users
    """
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        email = request.data.get('email')
        
        if not refresh_token or not email:
            return Response(
                {"error": "Missing refresh token or email"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify the user is a verified waitlist member
            waitlist_user = Waitlist.objects.get(
                email=email,
                is_verified=True
            )
            
            if not waitlist_user.user:
                return Response(
                    {"error": "User account not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate and refresh the token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken(refresh_token)
            
            # Check if token belongs to this user
            if refresh['user_id'] != str(waitlist_user.user.id):
                return Response(
                    {"error": "Invalid token for this user"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate new tokens
            new_refresh = RefreshToken.for_user(waitlist_user.user)
            
            return Response({
                "access_token": str(new_refresh.access_token),
                "refresh_token": str(new_refresh),
                "message": "Tokens refreshed successfully"
            })
            
        except Waitlist.DoesNotExist:
            return Response(
                {"error": "User not found in verified waitlist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
