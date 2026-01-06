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

from jblb import settings
from .models import Waitlist, EmailOutbox
from .serializers import WaitlistSerializer
from .services.email_service import render_verification_email
from .services.outbox_service import queue_email

resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_LIMIT = 3
EMAIL_WINDOW = 3600

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
                "your_referral_link": f"{settings.FRONTEND_URL}/waitlist?ref="
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

        position = Waitlist.objects.filter(is_verified=True).count()

        return Response(
            {
                "message": "Your JBLB waitlist spot has been confirmed! 🎉",
                "your_id": user.custom_id,
                "position": position,
                "total_verified": position,
            },
            status=status.HTTP_200_OK
        )

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
