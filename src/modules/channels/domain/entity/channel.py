from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Channel:
    id: str
    name: str
    category: str
    language: str
    country_code: str
    urls: tuple[str, ...]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "language": self.language,
            "country_code": self.country_code,
            "urls": list(self.urls),
        }