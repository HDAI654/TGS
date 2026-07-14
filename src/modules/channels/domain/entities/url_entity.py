from src.modules.core.entity import Entity
from src.modules.channels.domain.value_objects.id import ID
from src.modules.channels.domain.value_objects.url import URL


class URLEntity(Entity):
    FIELD_TYPE_MAP = {
        "id": ID,
        "url": URL,
    }

    def __init__(
        self,
        id: ID,
        url: URL,
    ):
        self.id = id
        self.url = url

        super().__init__()

    @classmethod
    def create(
        cls,
        url: str,
        id: str | None = None,
    ) -> "URLEntity":
        """Create a new URLEntity."""

        return cls(
            id=ID(id) if id is not None else ID.generate(),
            url=URL(url),
        )
