import asyncio
import logging

from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.mongo import MongoStorage


from utils import throttling
from data.config import bot_token, conf, configs


from mongodb.connect_bd import mongo_connection

isChat = filters.IDFilter

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger('aiohttp').setLevel(logging.ERROR)


async def get_config_data():
    bot_for_name = await bot.get_me()
    c = configs()
    await c.set_configs(bot_for_name.username)
    return c



bot = Bot(token=bot_token)

config = asyncio.run(get_config_data())


welcome_message = config.welcome_message
account_number = config.account_number
gpt_host_api = config.gpt_host_api
dialog_max_tokens = config.dialog_max_tokens
channels_auto_join = config.channels_auto_join
auto_join_message = config.auto_join_message
db_name = config.db_name
admin_list = config.admin_ids

mongo_conn = mongo_connection(db_name)
print('connected')

storage = MongoStorage(host='localhost', port=27017, db_name=mongo_conn.db_name, with_destiny=False, with_bot_id=False)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(throttling.ThrottlingMiddleware())
rate_limit = throttling.rate_limit





