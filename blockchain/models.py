from django.db import models
import uuid

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, unique=True)  # e.g. ETH, BTC
    name = models.CharField(max_length=100)
    network = models.CharField(max_length=50, choices=[
        ("ETHEREUM", "Ethereum"),
        ("SOLANA", "Solana"),
        ("AVALANCHE", "Avalanche"),
        ("HEDERA", "Hedera"),
        ("ANOMA", "Anoma"),
    ])
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tokens"
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def __str__(self):
        return f"{self.symbol} ({self.network})"
