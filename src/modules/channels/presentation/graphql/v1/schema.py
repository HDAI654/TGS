import strawberry
from src.modules.channels.presentation.graphql.v1.country.queries import CountryQuery
from src.modules.channels.presentation.graphql.v1.country.mutations import (
    CountryMutation,
)
from src.modules.channels.presentation.graphql.v1.channel.queries import ChannelQuery
from src.modules.channels.presentation.graphql.v1.channel.mutations import (
    ChannelMutation,
)


@strawberry.type
class Query(CountryQuery, ChannelQuery):
    pass


@strawberry.type
class Mutation(CountryMutation, ChannelMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
