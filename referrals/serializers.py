from rest_framework import serializers
from .models import ReferralStats, LeaderboardEntry, ReferralNetwork
from django.contrib.auth import get_user_model

User = get_user_model()

class ReferralStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralStats
        fields = [
            'total_referrals',
            'verified_referrals', 
            'pending_referrals',
            'total_earnings',
            'last_updated'
        ]

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardEntry
        fields = [
            'rank',
            'username',
            'verified_referrals',
            'total_earnings'
        ]

class LeaderboardSerializer(serializers.Serializer):
    """
    Serializer for leaderboard response - Rank, username, verified referrals, position
    """
    rank = serializers.IntegerField()
    username = serializers.CharField()
    verified_referrals = serializers.IntegerField()
    position = serializers.IntegerField()

class ReferralNetworkSerializer(serializers.ModelSerializer):
    referred_username = serializers.CharField(source='referred_user.username', read_only=True)
    referred_email = serializers.EmailField(source='referred_user.email', read_only=True)
    waitlist_custom_id = serializers.CharField(source='waitlist_entry.custom_id', read_only=True)
    is_verified = serializers.BooleanField(source='waitlist_entry.is_verified', read_only=True)
    
    class Meta:
        model = ReferralNetwork
        fields = [
            'referred_username',
            'referred_email', 
            'waitlist_custom_id',
            'is_verified',
            'created_at'
        ]

class ReferralDashboardSerializer(serializers.Serializer):
    total_referrals = serializers.IntegerField()
    waitlist_position = serializers.IntegerField()
    referral_link = serializers.URLField()
    earnings = serializers.DecimalField(max_digits=15, decimal_places=4)
    verified_referrals = serializers.IntegerField()
    pending_referrals = serializers.IntegerField()