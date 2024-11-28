from django.test import TestCase
from unittest.mock import patch, Mock
from .models import CryptoCurrency
from .tasks import update_crypto_prices
from .utils import rate_limit
from decimal import Decimal
from graphene.test import Client
from .schema import schema
import redis
import time
import json

class CryptoCurrencyTests(TestCase):
    def setUp(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal('0.0')
        )

    def test_cryptocurrency_creation(self):
        self.assertEqual(self.crypto.name, "Curve DAO")
        self.assertEqual(self.crypto.symbol, "CRV")
        self.assertEqual(self.crypto.price, Decimal('0.0'))

    def test_string_representation(self):
        self.assertEqual(str(self.crypto), "Curve DAO (CRV)")

    def test_default_values(self):
        self.assertEqual(self.crypto.daily_high, Decimal('0'))
        self.assertEqual(self.crypto.daily_low, Decimal('0'))
        self.assertEqual(self.crypto.price_1h_ago, Decimal('0'))
        self.assertEqual(self.crypto.price_24h_ago, Decimal('0'))

class UpdateCryptoPricesTaskTests(TestCase):
    def setUp(self):
        self.crv = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal('0.0')
        )
        
        self.mock_current_price_data = {
            'coins': {
                'ethereum:0xD533a949740bb3306d119CC777fa900bA034cd52': {
                    'price': 0.5
                }
            }
        }
        
        self.mock_chart_data = {
            'coins': {
                'ethereum:0xD533a949740bb3306d119CC777fa900bA034cd52': {
                    'prices': [
                        {'timestamp': int(time.time()) - 3600, 'price': 0.48},  # 1h ago
                        {'timestamp': int(time.time()) - 7200, 'price': 0.52},  # 2h ago
                        {'timestamp': int(time.time()) - 86400, 'price': 0.45},  # 24h ago
                    ]
                }
            }
        }

    @patch('requests.get')
    def test_successful_price_update(self, mock_get):
        def mock_response(url):
            mock = Mock()
            mock.raise_for_status.return_value = None
            if 'prices/current' in url:
                mock.json.return_value = self.mock_current_price_data
            else:
                mock.json.return_value = self.mock_chart_data
            return mock
            
        mock_get.side_effect = mock_response
        
        result = update_crypto_prices()
        
        self.assertEqual(result, "Success")
        
        self.crv.refresh_from_db()
        
        self.assertEqual(self.crv.price, Decimal('0.5'))
        self.assertEqual(self.crv.price_1h_ago, Decimal('0.48'))
        self.assertEqual(self.crv.price_24h_ago, Decimal('0.45'))
        self.assertEqual(self.crv.daily_high, Decimal('0.52'))
        self.assertEqual(self.crv.daily_low, Decimal('0.45'))

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        mock_get.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception) as context:
            update_crypto_prices()
        
        self.assertTrue("API Error" in str(context.exception))

class RateLimitTests(TestCase):
    def setUp(self):
        self.redis_mock = patch('redis.Redis.from_url').start()
        self.time_mock = patch('time.time').start()
        
        # Configure initial time
        self.current_time = 1000
        self.time_mock.return_value = self.current_time

    def tearDown(self):
        patch.stopall()

    def test_rate_limit_not_exceeded(self):
        self.redis_mock.return_value.zcard.return_value = 5
        
        @rate_limit(max_requests=50, time_window=60)
        def test_function():
            return "success"
            
        result = test_function()
        self.assertEqual(result, "success")

    def test_rate_limit_exceeded(self):
        self.redis_mock.return_value.zcard.return_value = 50
        

        self.current_time = 1000
        oldest_request_time = self.current_time - 10  # 10 seconds ago
        
        self.redis_mock.return_value.zrange.return_value = [str(oldest_request_time).encode()]
        
        @rate_limit(max_requests=50, time_window=60)
        def test_function():
            return "success"
            
        result = test_function()
        
        self.assertEqual(result, "success")

    def test_redis_error_handling(self):
        self.redis_mock.return_value.zcard.side_effect = redis.RedisError("Connection failed")
        
        @rate_limit(max_requests=50, time_window=60)
        def test_function():
            return "success"
            
        result = test_function()
        self.assertEqual(result, "success")

class GraphQLErrorTests(TestCase):
    def setUp(self):
        self.client = Client(schema)

    def test_query_nonexistent_cryptocurrency(self):
        query = '''
        query {
            cryptocurrency(symbol: "NONEXISTENT") {
                name
                symbol
                price
            }
        }
        '''
        response = self.client.execute(query)
        self.assertIsNotNone(response.get('errors'))
        self.assertIn('does not exist', str(response['errors'][0]))

    def test_create_duplicate_cryptocurrency(self):
        CryptoCurrency.objects.create(
            name="Test Token",
            symbol="TEST",
            price=Decimal('1.0')
        )
        
        mutation = '''
        mutation {
            createCryptocurrency(name: "Test Token 2", symbol: "TEST") {
                cryptocurrency {
                    symbol
                }
            }
        }
        '''
        response = self.client.execute(mutation)
        self.assertIsNotNone(response.get('errors'))
        self.assertIn('already exists', str(response['errors'][0]))

    def test_invalid_symbol_format(self):
        mutation = '''
        mutation {
            createCryptocurrency(name: "Invalid", symbol: "") {
                cryptocurrency {
                    symbol
                }
            }
        }
        '''
        response = self.client.execute(mutation)
        self.assertIsNotNone(response.get('errors'))

class GraphQLSchemaTests(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.eth = CryptoCurrency.objects.create(
            name="Ethereum",
            symbol="ETH",
            price=Decimal('2000.00'),
            price_1h_ago=Decimal('1990.00'),
            price_24h_ago=Decimal('1950.00'),
            daily_high=Decimal('2010.00'),
            daily_low=Decimal('1980.00')
        )
        self.weth = CryptoCurrency.objects.create(
            name="Wrapped Ethereum",
            symbol="WETH",
            price=Decimal('2001.00'),
            price_1h_ago=Decimal('1991.00'),
            price_24h_ago=Decimal('1951.00'),
            daily_high=Decimal('2011.00'),
            daily_low=Decimal('1981.00')
        )

    def test_query_all_ethereum_tokens(self):
        query = '''
        query {
            allCryptocurrencies {
                name
                symbol
                price
                price1hAgo
                price24hAgo
                dailyHigh
                dailyLow
            }
        }
        '''
        response = self.client.execute(query)
        self.assertIsNone(response.get('errors'))
        results = response['data']['allCryptocurrencies']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['symbol'], 'ETH')
        self.assertEqual(results[1]['symbol'], 'WETH')

    def test_query_ethereum(self):
        query = '''
        query {
            cryptocurrency(symbol: "ETH") {
                name
                symbol
                price
                price1hAgo
                price24hAgo
            }
        }
        '''
        response = self.client.execute(query)
        self.assertIsNone(response.get('errors'))
        result = response['data']['cryptocurrency']
        self.assertEqual(result['name'], 'Ethereum')
        self.assertEqual(result['symbol'], 'ETH')
        self.assertEqual(Decimal(result['price']), Decimal('2000.00'))
        self.assertEqual(Decimal(result['price1hAgo']), Decimal('1990.00'))
        self.assertEqual(Decimal(result['price24hAgo']), Decimal('1950.00'))

    def test_create_ethereum_token(self):
        mutation = '''
        mutation {
            createCryptocurrency(name: "Staked Ethereum", symbol: "stETH") {
                cryptocurrency {
                    name
                    symbol
                }
            }
        }
        '''
        response = self.client.execute(mutation)
        self.assertIsNone(response.get('errors'))
        result = response['data']['createCryptocurrency']['cryptocurrency']
        self.assertEqual(result['name'], 'Staked Ethereum')
        self.assertEqual(result['symbol'], 'stETH')

        # Verify it was created in the database
        self.assertTrue(CryptoCurrency.objects.filter(symbol='stETH').exists())
