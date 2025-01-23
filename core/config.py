import os

from asyncpg import create_pool
from dotenv import load_dotenv
load_dotenv()

ADMIN_ID = os.getenv('ADMIN_ID')
TOKEN = os.getenv('TOKEN')

PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_DB = os.getenv('PG_DB')

ARQ_REDIS_HOST = os.getenv('ARQ_REDIS_HOST')

FULL_LOCAL_PATH = os.getenv('FULL_LOCAL_PATH')

async def pool_settings():
    return await create_pool(user=PG_USER,
                             password=PG_PASSWORD,
                             host=PG_HOST,
                             database=PG_DB,
                             port=5432,
                             command_timeout=60)

HELP = '''
HELP
'''