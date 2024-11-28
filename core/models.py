from django.db import models

class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=30, decimal_places=18)
    daily_high = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    daily_low = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    price_1h_ago = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    price_24h_ago = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cryptocurrencies"

    def __str__(self):
        return f"{self.name} ({self.symbol})"