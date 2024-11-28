import requests
from celery import shared_task
from django.conf import settings
from .models import CryptoCurrency
from decimal import Decimal
from datetime import datetime, timedelta
import time
import math
from .utils import rate_limit

@shared_task
@rate_limit(max_requests=8, time_window=30)
def update_crypto_prices():
    print("Starting price update task...")
    
    coins_url = 'https://coins.llama.fi'
    
    try:
        cryptos = CryptoCurrency.objects.all()
        print(f"Found {len(cryptos)} cryptocurrencies to update")
        
        # Get current timestamp and historical timestamps
        current_ts = math.floor(time.time())
        hour_ago_ts = current_ts - (60 * 60)
        day_ago_ts = current_ts - (24 * 60 * 60)
        
        for crypto in cryptos:
            coin_id = None
            if crypto.symbol == 'CRV':
                coin_id = 'ethereum:0xD533a949740bb3306d119CC777fa900bA034cd52'
            elif crypto.symbol == 'crvUSD':
                coin_id = 'ethereum:0xf939E0A03FB07F59A73314E73794Be0E57ac1b4E'
            elif crypto.symbol == 'scrvUSD':
                coin_id = 'ethereum:0x0655977feb2f289a4ab78af67bab0d17aab84367'
            
            if not coin_id:
                print(f"No contract address configured for {crypto.symbol}")
                continue
            
            # Get current price
            current_price_response = requests.get(f"{coins_url}/prices/current/{coin_id}")
            current_price_response.raise_for_status()
            current_price_data = current_price_response.json()
            
            # Get historical price data
            chart_response = requests.get(
                f"{coins_url}/chart/{coin_id}?"
                f"start={day_ago_ts}&"
                f"span=24&"
                f"period=1h&"
                f"searchWidth=600"
            )
            chart_response.raise_for_status()
            chart_data = chart_response.json()
            
            if current_price_data and current_price_data.get('coins'):
                price_data = current_price_data['coins'].get(coin_id)
                if price_data:
                    current_price = Decimal(str(price_data['price']))
                    
                    # Process historical data
                    if chart_data and chart_data.get('coins'):
                        prices = chart_data['coins'][coin_id]['prices']
                        if prices:
                            # Get high/low prices
                            price_values = [p['price'] for p in prices]
                            daily_high = Decimal(str(max(price_values)))
                            daily_low = Decimal(str(min(price_values)))
                            
                            # Get historical prices
                            prices_dict = {p['timestamp']: p['price'] for p in prices}
                            
                            # Find closest timestamps for 1h and 24h ago
                            price_1h = next((p['price'] for p in prices 
                                           if abs(p['timestamp'] - hour_ago_ts) < 3600), 0)
                            price_24h = next((p['price'] for p in prices 
                                            if abs(p['timestamp'] - day_ago_ts) < 3600), 0)
                            
                            # Update the cryptocurrency
                            crypto.price = current_price
                            crypto.daily_high = daily_high
                            crypto.daily_low = daily_low
                            crypto.price_1h_ago = Decimal(str(price_1h))
                            crypto.price_24h_ago = Decimal(str(price_24h))
                            crypto.last_updated = datetime.now()
                            crypto.save()
                            
                            print(f"Updated {crypto.symbol} - Current: {current_price}, "
                                  f"1h ago: {price_1h}, 24h ago: {price_24h}, "
                                  f"High: {daily_high}, Low: {daily_low}")
                    
    except Exception as e:
        print(f"Error updating prices: {str(e)}")
        raise e

    print("Price update task completed")
    return "Success"