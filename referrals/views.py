from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import ReferralStats, LeaderboardEntry, ReferralNetwork
from .serializers import (
    ReferralDashboardSerializer, 
    ReferralNetworkSerializer, 
    LeaderboardEntrySerializer
)
from waitlist.models import Waitlist
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReferralDashboardView(APIView):
    """
    GET /api/referrals/dashboard/
    Returns referral dashboard data for authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        referral_stats, created = ReferralStats.objects.get_or_create(user=user)
        
        waitlist_position = referral_stats.verified_referrals
        
        try:
            user_waitlist = Waitlist.objects.get(user=user)
            referral_link = f"{settings.FRONTEND_URL}/waitlist?ref={user_waitlist.referral_code}"
        except Waitlist.DoesNotExist:
            try:
                user_waitlist = Waitlist.objects.get(email=user.email)
                referral_link = f"{settings.FRONTEND_URL}/waitlist?ref={user_waitlist.referral_code}"
            except Waitlist.DoesNotExist:
                referral_link = f"{settings.FRONTEND_URL}/waitlist?ref=DEFAULT_REFERRAL"
        
        dashboard_data = {
            'total_referrals': referral_stats.total_referrals,
            'waitlist_position': waitlist_position,
            'referral_link': referral_link,
            'earnings': referral_stats.total_earnings,
            'verified_referrals': referral_stats.verified_referrals,
            'pending_referrals': referral_stats.pending_referrals
        }
        
        serializer = ReferralDashboardSerializer(dashboard_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReferralNetworkView(APIView):
    """
    GET /api/referrals/network/
    Returns paginated list of referred users
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        user = request.user
        
        # Get referral network entries for this user
        referrals = ReferralNetwork.objects.filter(
            referrer=user
        ).select_related('referred_user', 'waitlist_entry')
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_referrals = paginator.paginate_queryset(referrals, request)
        
        serializer = ReferralNetworkSerializer(paginated_referrals, many=True)
        return paginator.get_paginated_response(serializer.data)

class LeaderboardView(APIView):
    """
    GET /api/referrals/leaderboard/
    Returns top 10 referrers - Rank (ascending), username, verified referrals, position (user ID)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get top 10 referrers by verified referrals (highest first)
            top_referrers = ReferralStats.objects.select_related('user').order_by(
                '-verified_referrals', 
                '-total_earnings'
            )[:10]
            
            # Add ranking and position data
            leaderboard_data = []
            for index, stats in enumerate(top_referrers, 1):  # index starts from 1 (rank)
                # Get the user's custom ID from their waitlist entry
                user_position = "N/A"  # Default if no waitlist entry
                try:
                    # Get the waitlist entry for this user to get their custom ID
                    # First check if the user has a waitlist entry
                    waitlist_entry = getattr(stats.user, 'waitlist', None)
                    if waitlist_entry and hasattr(waitlist_entry, 'custom_id') and waitlist_entry.custom_id:
                        user_position = waitlist_entry.custom_id
                    else:
                        # Try to find waitlist entry by email if direct relation doesn't exist
                        from waitlist.models import Waitlist
                        user_waitlist = Waitlist.objects.filter(user=stats.user).first()
                        if user_waitlist and user_waitlist.custom_id:
                            user_position = user_waitlist.custom_id
                        else:
                            # If no custom_id in waitlist, use user ID with format
                            user_position = f"JBLB-{str(stats.user.id).zfill(5)}"
                except Exception as e:
                    # If there's an issue getting waitlist entry, use user ID
                    user_position = f"JBLB-{str(stats.user.id).zfill(5)}"
                
                leaderboard_data.append({
                    'rank': index,  # This is the rank (ascending from 1)
                    'username': stats.user.username,
                    'verified_referrals': stats.verified_referrals,
                    'position': user_position  # This is the user's ID number (like #00030)
                })
            
            from .serializers import LeaderboardSerializer
            serializer = LeaderboardSerializer(leaderboard_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in LeaderboardView: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching leaderboard data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RefreshLeaderboardView(APIView):
    """
    POST /api/referrals/refresh-leaderboard/
    Manually refresh leaderboard cache (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        LeaderboardEntry.objects.all().delete()
        
        top_stats = ReferralStats.objects.select_related('user').order_by(
            '-verified_referrals',
            '-total_earnings'
        )[:50] 
        
        leaderboard_entries = []
        for index, stats in enumerate(top_stats, 1):
            leaderboard_entries.append(
                LeaderboardEntry(
                    user=stats.user,
                    username=stats.user.username,
                    verified_referrals=stats.verified_referrals,
                    total_earnings=stats.total_earnings,
                    rank=index
                )
            )
        
        LeaderboardEntry.objects.bulk_create(leaderboard_entries)
        
        return Response(
            {'message': f'Leaderboard refreshed with {len(leaderboard_entries)} entries'},
            status=status.HTTP_200_OK
        )