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
from .models import Waitlist
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
                waitlist = serializer.save(is_verified=False)
                waitlist.verification_token = generate_unique_token()
                waitlist.token_created = timezone.now()
                waitlist.save()

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
                    verify_url
                )

                queue_email(
                    to=waitlist.email,
                    subject=f"#{waitlist.custom_id} – Confirm Your JBLB Spot!",
                    html=html_body
                )

            return Response({
                "message": "Waitlist saved. Verification email queued.",
                "your_id": waitlist.custom_id
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