from peewee import Model, CharField, AutoField, ForeignKeyField, BooleanField
from playhouse.db_url import connect
from playhouse.mysql_ext import JSONField
from dotenv import load_dotenv
import os
from .logger import logger

#####################################
# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER', 'TEST')
DB_PASS = os.getenv('DB_PASS', '1234')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')  # Default MySQL port
DB_DATABASE = os.getenv('DB_DATABASE', 'tv_garden_db')

database = connect(f'mysql://{DB_USER}:{DB_PASS}@127.0.0.1:{DB_PORT}/{DB_DATABASE}?charset=utf8mb4')
#####################################


class BaseModel(Model):
    class Meta:
        database = database

    def __str__(self):
        return str(self.id)






class Categories(BaseModel):
    id = AutoField(primary_key=True)
    title = CharField(max_length=255)
    
class Countries(BaseModel):
    id = AutoField(primary_key=True)
    country_code = CharField(max_length=255, unique=True)
    country_name = CharField(max_length=255)
    emoji = CharField(max_length=255)
    time_zone = CharField(max_length=255)
    capital = CharField(max_length=255)
    
class Channel(BaseModel):
    id = AutoField(primary_key=True)
    unique_code = CharField(max_length=255, unique=True)
    title = CharField(max_length=255)
    video_url = JSONField()
    youtube_url = JSONField()
    country = ForeignKeyField(Countries, field='id')
    category_ids = JSONField()
    youtube = BooleanField(default=False)
    geo_block = BooleanField(default=False)
   
   
   
   
   
   
   
   
    
# Create tables if they don't exist
if __name__ == "__main__":
    try:
        with database:
            database.create_tables([Categories, Countries, Channel], safe=True)
    
    except Exception as e:
        logger.error(f"Error occurred while creating tables: {e}")