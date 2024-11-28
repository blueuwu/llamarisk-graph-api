# LlamaRisk Assessment

Backend For the assessment, you can find the frontend repo [here](https://github.com/blueuwu/llamarisk-graph-frontend)

## Features

- Real-time cryptocurrency price tracking
- Historical price data (1h and 24h)
- Daily high/low price tracking
- GraphQL API for data queries
- Rate-limited API calls
- Celery-based scheduled tasks
- Docker containerization
- Comprehensive test coverage

## Tech Stack

- **Backend**: Django
- **Task Queue**: Celery
- **Cache/Message Broker**: Redis
- **API**: GraphQL with Graphene
- **Containerization**: Docker & Docker Compose
- **Rate Limiting**: Custom Redis-based implementation

## Configuration

### Environment Variables
- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `CELERY_BROKER_URL`: Redis URL (defaults to redis://redis:6379/0 in Docker)
- `CELERY_RESULT_BACKEND`: Redis URL (defaults to redis://redis:6379/0 in Docker)

### IMPORTANT
- The default Redis URL in the .env file is set to 'redis://127.0.0.1:6379/0'. This URL might need to be reconfigured depending on your setup:
  - For Docker: Use 'redis://redis:6379/0'
  - For local development: Use 'redis://127.0.0.1:6379/0'
  - For custom setups: Adjust according to your Redis instance configuration

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cryptocurrency-price-tracker
   ```

2. Create a .env file with required environment variables:
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

3. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## API Usage

### GraphQL Endpoints

The GraphQL API is available at `/graphql/` with GraphiQL interface enabled in development.

Example Queries:

#### Get all cryptocurrencies
```graphql
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

Get specific currency:
query {
  cryptocurrency(symbol: "CRV") {
    name
    price
    dailyHigh
    dailyLow
  }
}

## Testing
Run the test suite using:docker-compose run web python manage.py test

