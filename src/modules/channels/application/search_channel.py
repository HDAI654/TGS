from src.modules.channels.domain.ports.channel_repo_interface import ChannelRepository


class SearchChannel:
    def __init__(
        self,
        channel_repo: ChannelRepository
    ):
        self.repo = channel_repo

    def execute(self, text: str, limit: int = 10, offset: int = 0):
        channel = self.repo.search(text, limit, offset)

        return channel