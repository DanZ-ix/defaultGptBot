from configobj import ConfigObj

conf = ConfigObj("data/settings.ini", encoding='UTF8')

bot_token = conf['aio']['bot_token']

gpt_host_api = conf['gpt']['host']
dialog_max_tokens = int(conf['gpt']['limit_dialog_tokens'])

channel_subscribe = conf['subscribe']['channels']
channels_auto_join = conf['subscribe']['channels_auto_join']
attempts_channels = conf['subscribe']['attempts_channels']

account_number = conf['youmoney']['account']

invite_count_max_to_day = 20

channel_in = '<a href="https://t.me/+khaZwmg2C61lNjBi">тест подписки</a>'
channel_in1 = ''

welcome_message = conf['messages']['start_message']
auto_join_message = conf['messages']['auto_join_message']

