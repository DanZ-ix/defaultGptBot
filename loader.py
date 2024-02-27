import logging

from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.mongo import MongoStorage

from mongodb import connect_bd
from utils import other_commands, other_func, state_profile, start_state, imagine_state, gpt_state, accounts_state, queues_state, banlist_state, mailing_state, channels_state, channels_necessary_state, keyboard, throttling
from data.config import bot_token, channel_subscribe, attempts_channels, conf, welcome_message, account_number
from data.config import gpt_host_api, dialog_max_tokens, invite_count_max_to_day, channel_in, channel_in1, channels_auto_join, auto_join_message


from gpt_api import gpt_api
from youmoney_hook import webhook

isChat = filters.IDFilter

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger('aiohttp').setLevel(logging.ERROR)

gpt_api = gpt_api.gptApi(gpt_host_api, dialog_max_tokens)

storage = MongoStorage(host='localhost', port=27017, db_name=connect_bd.mongo_conn.db_name, with_destiny=False, with_bot_id=False)
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(throttling.ThrottlingMiddleware())
rate_limit = throttling.rate_limit

youmoney_web = webhook.NotifyYoumoney(account_number, bot)