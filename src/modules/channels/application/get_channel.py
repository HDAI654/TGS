from src.modules.channels.domain.ports.channel_repo_interface import ChannelRepository


class GetChannel:
    def __init__(
        self,
        channel_repo: ChannelRepository
    ):
        self.repo = channel_repo

    def execute(self, channel_id: str):
        channel = self.repo.get_by_id(channel_id)

        return channel