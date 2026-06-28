import strawberry
from src.channel_app.domain.entities.country import CountryEntity


@strawberry.type
class CountryType:
    country_code: str
    country_name: str
    capital: str
    timezone: str
    has_channels: bool
    channel_count: int

    @staticmethod
    def from_entity(entity: CountryEntity) -> "CountryType":
        return CountryType(
            country_code=entity.country_code.value,
            country_name=entity.country_name.value,
            capital=entity.capital.value,
            timezone=entity.timezone.value,
            has_channels=entity.has_channels.value,
            channel_count=entity.channel_count.value,
        )
