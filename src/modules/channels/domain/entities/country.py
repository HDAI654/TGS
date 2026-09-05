from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Country:
    country_code: str
    country_name: str
    timezone: str
    has_channels: bool
    channel_count: int

    def to_dict(self) -> dict:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "timezone": self.timezone,
            "has_channels": self.has_channels,
            "channel_count": self.channel_count,
        }
