# Channels Endpoints

## `GET /health`

Public health endpoint. It verifies that the Channels service can reach PostgreSQL.

## `POST /graphql`

Public read-only GraphQL API. The schema exposes no mutations.

### Queries

- `channel(id: UUID!): Channel`
- `channels(search: String, limit: Int!, offset: Int!): ChannelConnection`
- `country(countryCode: String!): Country`
- `countries(search: String, limit: Int!, offset: Int!): CountryConnection`

`limit` must be between 1 and 100. `offset` must be non-negative.

A missing entity returns `null`. A `null`, empty, or whitespace-only search returns `null`.

### Channel search fields

- `name`
- `category.name`
- `language`
- `country_code`
- `country.name`

### Country search fields

- `country_code`
- `country_name`
- `timezone`

`urls`, `has_channels`, and `channel_count` do not participate in search.
