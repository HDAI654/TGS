from src.modules.channels.domain.ports.country_repo_interface import CountryRepository


class GetCountry:
    def __init__(
        self,
        country_repo: CountryRepository
    ):
        self.repo = country_repo

    async def execute(self, country_code: str):
        country = await self.repo.get_by_code(country_code)

        return country