from src.modules.channels.domain.ports.country_repo_interface import CountryRepository


class SearchCountry:
    def __init__(
        self,
        country_repo: CountryRepository
    ):
        self.repo = country_repo

    def execute(self, text: str, limit: int = 10, offset: int = 0):
        country = self.repo.search(text, limit, offset)

        return country