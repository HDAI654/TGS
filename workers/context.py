from workers.crawler_interface import ICrawler
from workers.tv_garden_crawler_imp import TVGardenCrawlerImp
from workers.repo_interface import IRepo
from workers.sqlal_repo import SQLAL_Repo


def get_crawler() -> ICrawler:
    return TVGardenCrawlerImp()


def get_repo() -> IRepo:
    return SQLAL_Repo()
