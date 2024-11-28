from django.contrib import admin
from .models import CryptoCurrency

@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price', 'price_1h_ago', 'price_24h_ago', 
                   'daily_high', 'daily_low', 'last_updated')
    search_fields = ('name', 'symbol')
    readonly_fields = ('last_updated', 'daily_high', 'daily_low', 
                      'price_1h_ago', 'price_24h_ago')