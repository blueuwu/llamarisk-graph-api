import graphene
from graphene_django import DjangoObjectType
from .models import CryptoCurrency
from decimal import Decimal
from graphql import GraphQLError

class CryptoCurrencyType(DjangoObjectType):
    class Meta:
        model = CryptoCurrency
        fields = ('id', 'name', 'symbol', 'price', 'price_1h_ago', 'price_24h_ago',
                 'daily_high', 'daily_low', 'last_updated')

class Query(graphene.ObjectType):
    all_cryptocurrencies = graphene.List(CryptoCurrencyType)
    cryptocurrency = graphene.Field(CryptoCurrencyType, symbol=graphene.String())

    def resolve_all_cryptocurrencies(self, info):
        return CryptoCurrency.objects.all()

    def resolve_cryptocurrency(self, info, symbol):
        return CryptoCurrency.objects.get(symbol=symbol)

class CreateCryptoCurrency(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        symbol = graphene.String(required=True)

    cryptocurrency = graphene.Field(CryptoCurrencyType)

    def mutate(self, info, name, symbol):
        if not symbol:
            raise GraphQLError("Symbol cannot be empty")
            
        if CryptoCurrency.objects.filter(symbol=symbol).exists():
            raise GraphQLError(f"Cryptocurrency with symbol {symbol} already exists")
            
        cryptocurrency = CryptoCurrency.objects.create(
            name=name,
            symbol=symbol,
            price=Decimal('0.0')
        )
        return CreateCryptoCurrency(cryptocurrency=cryptocurrency)

class Mutation(graphene.ObjectType):
    create_cryptocurrency = CreateCryptoCurrency.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)