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


welcome_message = "{{start_message}}"
auto_join_message = "{{auto_join_message}}"

