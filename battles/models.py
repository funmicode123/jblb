from django.db import models
import uuid
from decimal import Decimal

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
    total_weight = models.FloatField(default=0.0)
    initial_value = models.FloatField(default=100.0, null= False, blank=False,
                                      help_text="Initial value is starting from 100")
    current_value = models.FloatField(default=100.0, null= False, blank=False,)
    oracle_source=models.CharField(max_length=50, default="pyth", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket by {self.creator_wallet}"

    def save(self, *args, **kwargs):
        if self.pk is None and self.initial_value in [None, 0]:
            self.initial_value = 100.0
        super().save(*args, **kwargs)


class Battle(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Players'),
        ('active', 'Active'),
        ('settling', 'Settling'),
        ('finished', 'Finished'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,
                             related_name="battles", null=True, blank=True)
    token = models.CharField(max_length=50, default='HBAR')
    tier = models.IntegerField(CLUB_TIERS, default="COMMON")
    duration_seconds = models.IntegerField(default=3600* 24*7)
    velocity = models.IntegerField(default=2, )
    stake_per_player_usd = models.FloatField(default=100, null= False, blank=False,)
    total_pool_usd = models.FloatField(default=0)
    treasury_cut = models.FloatField(default=0)
    winner_prize = models.FloatField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,  default='waiting')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL,
                               related_name="winner", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_pool(self):
        player_count = self.participants.count()
        self.total_pool_usd = self.stake_per_player_usd * player_count
        self.treasury_cut = self.total_pool_usd * Decimal('0.10')
        self.winner_prize = self.total_pool_usd * Decimal('0.90')
        self.save()

    def __str__(self):
        return f"{self.title} (Tier {self.tier})"


class Player(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="players")
    battle = models.ForeignKey(Battle, on_delete=models.SET_NULL,
                               related_name="participants", null=True, blank=True)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE,
                               related_name="players", null=True, blank=True)
    reward_nft_token_id = models.CharField(max_length=100, blank=True, null=True)
    chain = models.CharField(max_length=20, choices=[('hedera', 'Hedera'), ('anoma', 'Anoma')], default="Hedera")
    is_verified = models.BooleanField(default=False)
    active_battle = models.ForeignKey(Battle, on_delete=models.SET_NULL, null=True, blank=True, related_name="active_players")
    staked_token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True, blank=True)
    staked_amount = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    initial_value = models.FloatField(default=0.0)
    current_value = models.FloatField(default=0.0)
    roi = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    jsparks_earned = models.DecimalField(max_digits=15, decimal_places=4, default=0.0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players"
        verbose_name = "Player"
        verbose_name_plural = "Players"
        unique_together = ("user", "battle")

    def __str__(self):
        return f"{self.user.username} in {self.club.name} has {self.chain}"


class PlayerToken(models.Model):
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
