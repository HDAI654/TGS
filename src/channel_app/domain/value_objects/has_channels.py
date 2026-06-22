from src.core.exceptions import InvalidHasChannelsError
from src.channel_app.domain.value_objects.base_bool_vo import BaseBoolVO


class HasChannels(BaseBoolVO):
    def __init__(self, value: bool):
        super().__init__(InvalidHasChannelsError, value)
