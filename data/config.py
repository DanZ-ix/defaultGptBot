from configobj import ConfigObj
from mongodb.bot_data_connection import mongo_conn

conf = ConfigObj("data/settings.ini", encoding='UTF8')

bot_token = conf['token']['token']

class configs:
    def __init__(self):
        self.gpt_host_api = None
        self.dialog_max_tokens = None
        self.admin_ids = None
        self.channels_auto_join = None
        self.account_number = None
        self.welcome_message = None
        self.auto_join_message = None
        self.db_name = None
        self.yandex_gpt_folder_id = None
        self.yandex_gpt_api_key = None


    async def set_configs(self, bot_name):
        await mongo_conn.connect_server()
        bot = await mongo_conn.db.bots.find_one({"bot_name": bot_name})
        local = False
        try:
            if local:
                self.dialog_max_tokens = 100                          # bot.get('dialog_max_tokens')
                self.admin_ids = "123" # bot.get('admins')
                self.channels_auto_join = "123" #bot.get('auto_join_channel_id')
                self.account_number = '4100111127436736'
                self.welcome_message = "start" # bot.get('start_message')
                self.auto_join_message = "start" #  bot.get('auto_join_message')
                self.db_name = "Midjourney"  #  bot.get('db_name')
                self.yandex_gpt_folder_id = '123' #bot.get('yandex_gpt_folder_id')
                self.yandex_gpt_api_key = '123' #bot.get('yandex_gpt_api_key')
            else:
                self.dialog_max_tokens = bot.get('dialog_max_tokens')
                self.admin_ids = bot.get('admins')
                self.channels_auto_join = bot.get('auto_join_channel_id')
                self.account_number = '4100111127436736'
                self.welcome_message = bot.get('start_message')
                self.auto_join_message = bot.get('auto_join_message')
                self.db_name = bot.get('db_name')
                self.yandex_gpt_folder_id = bot.get('yandex_gpt_folder_id')
                self.yandex_gpt_api_key = bot.get('yandex_gpt_api_key')

        except Exception as e:
            print("Не удалось загрузить настройки", e)


