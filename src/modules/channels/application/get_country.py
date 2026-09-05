from src.modules.channels.domain.ports.country_repo_interface import CountryRepository


class GetCountry:
    def __init__(
        self,
        country_repo: CountryRepository
    ):
        self.repo = country_repo

    def execute(self, country_id: str):
        country = self.repo.get_by_id(country_id)

        return country