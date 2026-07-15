from src.modules.channels.presentation.graphql.v1.schema import schema
from src.modules.channels.presentation.graphql.v1.context import get_graphql_context
from strawberry.fastapi import GraphQLRouter

graphql_router_v1_channels = GraphQLRouter(
    schema,
    prefix="/graphql/v1",
    context_getter=get_graphql_context,
)
