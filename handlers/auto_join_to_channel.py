
from loader import dp, types, keyboard, bot, start_state, auto_join_message, logging, FSMContext, channels_auto_join, connect_bd
import asyncio


@dp.chat_join_request_handler()
async def join_request(update: types.ChatJoinRequest, state: FSMContext):
  chat, user_id = update.chat.id, update.from_user.id

  user, channels = await connect_bd.mongo_conn.db.users.find_one({'user_id': str(user_id)}), []
  if user:
    if user.get('necessary_channel'):
      channels.append(user['necessary_channel']['id'])

  if str(chat) in channels_auto_join or str(chat) in channels:
    try:
      await update.approve()
      await bot.send_message(user_id, auto_join_message, parse_mode='html', disable_web_page_preview=True)
      await asyncio.sleep(20)

      m = await keyboard.call_gpt()
      await bot.send_message(user_id, f'Начать чат', reply_markup=m)

      await start_state.select_neiro.set()
    except Exception as e:
      logging.error("Exception WHILE AUTO JOIN", exc_info=True)
