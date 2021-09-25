import graphene
import graphql_jwt

import bankify.user.schema


class Query(
    bankify.user.schema.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    bankify.user.schema.Mutation,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
