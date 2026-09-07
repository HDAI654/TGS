# Channels Endpoints

## HTTP

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | none | Liveness/readiness; checks DB connectivity |
| POST | `/graphql` | none | GraphQL endpoint (queries only) |

## GraphQL queries

### `channel(id: UUID!): ChannelType`

Return a single channel by id, or null.

### `channels(limit: Int!, offset: Int!, search: String): ChannelConnection`

Search channels. Requires non-blank `search`. Pagination: `limit` 1–100, `offset` ≥ 0.
Returns null when `search` is missing or blank.

Searchable fields: channel name, category name, language, country code, country name.

### `country(country_code: String!): CountryType`

Return a single country by ISO code, or null.

### `countries(limit: Int!, offset: Int!, search: String): CountryConnection`

Search countries. Same pagination and blank-search rules as `channels`.

Searchable fields: country code, country name, timezone.

There are no mutations.
