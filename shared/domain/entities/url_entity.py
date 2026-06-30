from shared.domain.entity import Entity
from shared.domain.id_vo import ID
from shared.domain.value_objects.url import URL


class URLEntity(Entity):
    def __init__(
        self,
        id: ID,
        url: URL,
    ):
        self.id = id
        self.url = url

        super().__init__()
