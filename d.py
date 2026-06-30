from workers.tv_garden_crawler_imp import TVGardenCrawlerImp
import asyncio

cr = TVGardenCrawlerImp()
asyncio.run(cr.extract_all_channels())
