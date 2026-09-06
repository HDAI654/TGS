from dataclasses import dataclass
from uuid import UUID
from .category import Category


@dataclass(frozen=True, slots=True)
class Channel:
    id: UUID
    name: str
    category: Category
    language: str
    country_code: str
    urls: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.to_dict(),
            "language": self.language,
            "country_code": self.country_code,
            "urls": list(self.urls),
        }
