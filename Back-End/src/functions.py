import  requests
from bs4 import BeautifulSoup
from .model import Categories, Countries, Channel
from peewee import fn
import json
import gzip
from .logger import logger

# function to find the category in the site
def CrawlCategories():
    logger.info("Crawling categories started")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://tv.garden/"
    
    categories = []
    
    try:
        # get the page's content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # check for any errors
        
        # parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        box = soup.find('div', class_='drawer-middle-section')
        
        if not box:
            logger.error("Couldn't find categories menu in the page")
            return False
                
        buttons = box.find_all('button', class_='drawer-menu-button drawer-menu-button-group')
        if buttons:
            for b in buttons:
                button_text = b.find(string=True, recursive=False).strip()
                if button_text and button_text != 'All Channels':
                    categories.append(button_text)
                else:
                    continue
                
        else:
            logger.error("Couldn't find any categories")
            return False
        
        
        if categories:
            logger.info("Categories Crawler completed successfully")
            return categories
        
        else:
            return False
        
    except Exception as e:
        logger.error(f"Error occurred while crawling categories: {e}")
        return False

# Update categories
def update_categories():
    try:
        logger.info("Updating categories started")
        UpdatedCategories = CrawlCategories()
        if not UpdatedCategories:
            logger.error("Couldn't update categories because of an error from the Categories Crawler")
            return False
        OldCategories = Categories.select()
        
        new_categories = [c for c in UpdatedCategories if c not in [ctg.title for ctg in OldCategories]]
        
        # remove old categories that are not in the new categories
        for ctg in OldCategories:
            try:
                if ctg.title not in UpdatedCategories:
                    ctg.delete_instance()
            except Exception as e:
                logger.error(f"Error in deleting {ctg.title} category from the database. Error: {e}")
                continue
        
        # add new categories to the database
        for category in new_categories:
            try:
                Categories.create(title=category)
            except Exception as e:
                logger.error(f"Error in adding {category} category to the database. Error: {e}")
                continue
            
        return True
    except Exception as e:
        logger.error(f"Error occurred while updating categories: {e}")
        return False

# function to unzip the json file
def unzip_json(url):
    try:
        logger.info(f"Unzipping json file started  URL: {url}")
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with gzip.GzipFile(fileobj=response.raw) as gz_file:
                json_data = json.loads(gz_file.read().decode('utf-8'))
                logger.info("Unzipping json file completed successfully")
                return json_data
        logger.error("The response status code is not 200")
        return False
    except Exception as e:
        logger.error(f"Error occurred while unzipping json file: {e}")
        return False

# function to get country flag
def get_country_flag(country_code):
    try:
        return ''.join(chr(127397 + ord(char)) for char in country_code.upper())
    except:
        return "??????"

# function to update countries data
def update_countries():
    try:
        logger.info("Updating countries started")
        # get data from json file
        data = unzip_json(url="https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/main/channels/compressed/countries_metadata.json")
        if not data:
            logger.error("Couldn't update countries because of an error from the json file")
            return False
        
        # parse the json data
        cleaned_data = []
        for country, values in data.items():
            cleaned_data.append({
                "country_code": country,
                "country_name": values["country"],
                "emoji" : None,
                "time_zone": values["timeZone"],
                "capital" : values["capital"]
            })
        
        if not cleaned_data:
            logger.error("Couldn't update countries because of an error in parsing the json file data")
            return False
        
        
        
        # update coutries data in the database if  are not in the database
        old_countries = Countries.select()
        new_countries = [c for c in cleaned_data if c['country_code'] not in [ctg.country_code for ctg in old_countries]]
        
        # remove old countries that are not in the clean data
        for ctg in old_countries:
            try:
                if ctg.country_code not in [c['country_code'] for c in cleaned_data]:
                    ctg.delete_instance()
            except:
                logger.error(f"Error in deleting {ctg.country_code}country from the database")
                continue
        
        # add new countries to the database 
        for country in new_countries:
            try:
                emoji = get_country_flag(country['country_code'])
                if not emoji:
                    emoji = "Unknown Emoji"
                country['emoji'] = emoji
                Countries.create(country_code=country['country_code'], country_name=country['country_name'], emoji=country['emoji'], time_zone=country['time_zone'], capital=country['capital'])
            except:
                logger.error(f"Error in adding {country['country_code']} country to the database")
                continue
        
        return True
    
    except:
        return False
    
# function to update channels data
def update_channels():
    try:
        logger.info("Updating channels started")
        # get all categories
        categories = Categories.select()    
        if not categories:
            logger.error("Couldn't update channels because of an error in getting categories from the database")
            return False
        
        # get all channnels of each category
        for category in categories:
            ctg_json_name = "".join(list(map(lambda a : "-" if str(a).strip() == "" else str(a), str(category.title).lower()))) + ".json"
            channels = unzip_json(url=f"https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/main/channels/compressed/categories/{ctg_json_name}")
            
            if not channels or len(channels) == 0:
                logger.error(f"Couldn't find channels for {category.title} category")
                continue
            
            # check each channel (add and update)
            for channel in channels:
                try:
                    isYoutube = True if len(channel["youtube_urls"]) != 0 else False
                    isGeoBlocked = channel["isGeoBlocked"]
                    category_id = category.id
                    
                    country_id = Countries.select().where(Countries.country_code == str(channel["country"]).upper()).get().id
                    if not country_id:
                        logger.error(f"Couldn't find counry for {channel['name']} channel")
                        continue
                    
                    # check if the channel is already in the database
                    if Channel.select().where(Channel.unique_code == channel['nanoid']).exists():
                        
                        exist_categories = Channel.select().where(Channel.unique_code == channel['nanoid']).get().category_ids
                        
                        # add category id to the channel if it is not in the category ids
                        if category_id not in exist_categories:
                            new_category_ids = [category_id] + exist_categories
                            Channel.update(category_ids=new_category_ids).where(Channel.unique_code == channel['nanoid']).execute()
                            
                        # update othe data of the channel
                        Channel.update(title=channel["name"], video_url=channel["iptv_urls"], youtube_url=channel["youtube_urls"], country=country_id, youtube=isYoutube, geo_block=isGeoBlocked).where(Channel.unique_code == channel['nanoid']).execute()
                    
                    # add channel if the channel is not in the database
                    else:
                        Channel.create(unique_code=channel["nanoid"], title=channel["name"], video_url=channel["iptv_urls"], youtube_url=channel["youtube_urls"], country=country_id, category_ids=[category_id], youtube=isYoutube, geo_block=isGeoBlocked)
                
                except Exception as e:
                    logger.error(f"Error in check {channel['name']} channel to update or add. Error: {e}")
                    continue
            
            # remove channels that are not in the site
            for channel in Channel.select().where(fn.JSON_CONTAINS(Channel.category_ids, str(category_id), '$')):
                try:
                    # if channel not in the category
                    if channel.unique_code not in [c['nanoid'] for c in channels]:
                        new_category_ids = [c for c in channel.category_ids if c != category_id]
                        
                        # remove channel if it is not in any category
                        if new_category_ids == []:
                            channel.delete_instance()
                        # remove category id from the channel if it is not in the category
                        else:
                            Channel.update(category_ids=new_category_ids).where(Channel.unique_code == channel.unique_code).execute()
                
                except Exception as e:
                    logger.error(f"Error in check {channel.title} channel to remove. Error: {e}")
                    continue
        
        return True
    
    except Exception as e:
        logger.error(f"Error in updating channels. Error: {e}")
        return False
