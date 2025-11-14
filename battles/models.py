from django.db import models
import uuid
from django.conf import settings
from clubs.models import Club, CLUB_TIERS
from users.models import User
from blockchain.models import Token


class Basket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="baskets", null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="baskets", null=True, blank=True)
    creator_wallet =models.CharField(max_length=100, null=True, blank=True)
    name=models.CharField(max_length=100, null=True, blank=True)
    tokens= models.JSONField(default=list)
    total_weight = models.FloatField(default=0)
    initial_value = models.FloatField(default=100.0)
    oracle_source=models.CharField(max_length=50, default="pyth", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket by {self.creator_wallet}"


class Battle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    token = models.CharField(max_length=50, default='ETH')
    tier = models.IntegerField(CLUB_TIERS, default="COMMON")
    duration_seconds = models.IntegerField(default=3600)
    velocity = models.IntegerField(default=2)
    stake_amount = models.FloatField(default=100)
    status = models.CharField(max_length=50, default='waiting_for_players')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Tier {self.tier})"


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="players")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="players")
    nft_token_id = models.CharField(max_length=100, blank=True, null=True)
    chain = models.CharField(max_length=20, choices=[('hedera', 'Hedera'), ('anoma', 'Anoma')], default="Hedera")
    is_verified = models.BooleanField(default=False)
    active_battle = models.ForeignKey('Battle', on_delete=models.SET_NULL, null=True, blank=True, related_name="participants")
    staked_token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True, blank=True)
    staked_amount = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    roi = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)  # % ROI in current battle
    jsparks_earned = models.DecimalField(max_digits=15, decimal_places=4, default=0.0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players"
        verbose_name = "Player"
        verbose_name_plural = "Players"
        unique_together = ("user", "active_battle")

    def __str__(self):
        return f"{self.user.username} in {self.club.name} has {self.chain}"


class PlayerToken(models.Model):
    """
    Intermediate table to track how many tokens a player holds.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="token_balances")
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "player_tokens"
        verbose_name = "Player Token"
        verbose_name_plural = "Player Tokens"
        unique_together = ("player", "token")

    def __str__(self):
        return f"{self.player.user.username} - {self.amount} {self.token.symbol}"
