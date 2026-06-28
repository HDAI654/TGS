import strawberry
from src.channel_app.presentation.graphql.v1.country.queries import CountryQuery
from src.channel_app.presentation.graphql.v1.country.mutations import CountryMutation
from src.channel_app.presentation.graphql.v1.channel.queries import ChannelQuery
from src.channel_app.presentation.graphql.v1.channel.mutations import ChannelMutation


@strawberry.type
class Query(CountryQuery, ChannelQuery):
    pass


@strawberry.type
class Mutation(CountryMutation, ChannelMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
