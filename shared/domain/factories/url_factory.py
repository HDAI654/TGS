from shared.domain.entities.url_entity import URLEntity
from src.core.crypto_utils import IDGenerator
from src.core.id_vo import ID
from shared.domain.value_objects.url import URL


class URLFactory:
    @staticmethod
    def create(
        *,
        url: str,
        id: str | None = None,
    ) -> URLEntity:
        """
        Create a new URLEntity.
        """
        return URLEntity(
            id=ID(IDGenerator.generate()) if id is None else ID(id),
            url=URL(url),
        )
