from django.db import models
import uuid
class Basket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator_wallet = models.CharField(max_length=255)
    config = models.JSONField()
    initial_value = models.FloatField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
class Battle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    token = models.CharField(max_length=50, default='ETH')
    tier = models.IntegerField(default=1)
    duration_seconds = models.IntegerField(default=3600)
    velocity = models.IntegerField(default=2)
    stake_amount = models.FloatField(default=100)
    status = models.CharField(max_length=50, default='waiting_for_players')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    battle = models.ForeignKey(Battle, related_name='participants', on_delete=models.CASCADE)
    user_wallet = models.CharField(max_length=255)
    basket = models.ForeignKey(Basket, null=True, on_delete=models.SET_NULL)
    jsparks = models.FloatField(default=0)
    last_high_watermark = models.FloatField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
