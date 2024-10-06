import asyncio


async def start(dp):
  import asyncio
  import filters
  from loader import types, bot, mongo_conn, logging, admin_list
  from gpt_api import gpt_api
  from utils.other import other_commands
  from youmoney_hook.webhook import youmoney_web

  asyncio.create_task(youmoney_web.web_hooks())

  bot_info = await bot.get_me()
  bot['username'] = bot_info.username
  print(bot_info.username)

  other_commands.bot = bot
  other_commands.dp = dp
  other_commands.logging = logging
  other_commands.types = types

  gpt_api = gpt_api.gptApi()

  filters.setup(dp)
  await mongo_conn.connect_server()

  asyncio.create_task(gpt_api.check_gpt_queues(bot))

  await other_commands.set_commands()
  if admin_list:
    await other_commands.set_admin_commands(admin_list)


if __name__ == '__main__':
  from aiogram import executor
  from handlers import dp

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  executor.start_polling(dp, on_startup=start, skip_updates=True)
