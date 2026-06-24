from src.core.entity import Entity
from src.core.id_vo import ID
from src.channel_app.domain.value_objects.url import URL


class URLEntity(Entity):
    def __init__(
        self,
        id: ID,
        url: URL,
    ):
        self.id = id
        self.url = url

        super().__init__()
