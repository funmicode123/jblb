from rest_framework import serializers
from .models import Club
class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('id','name','owner_wallet','nft_id','created_at')
