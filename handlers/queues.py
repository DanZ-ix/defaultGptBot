
from loader import dp, types, FSMContext, bot, mongo_conn
from filters.filter_commands import isPrivate
from utils.state_progress import queues_state
from utils.keyboards import keyboard



@dp.message_handler(isPrivate(), commands=['queues'], state="*")
async def get_imagine_phrase(message: types.Message, state: FSMContext):
  chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, message.from_user.username and f"@{message.from_user.username}" or "", str(message.from_user.id)

  await state.update_data(type_check_queues='gpt')
  m, t = await keyboard.get_queues(type='gpt')
  await bot.send_message(chat, t, reply_markup=m, parse_mode='html')
  await queues_state.queues_update.set()


@dp.callback_query_handler(isPrivate(), state=queues_state.queues_update)
async def callback_data(message: types.CallbackQuery, state: FSMContext):
  chat, message_id = str(message.message.chat.id), message.message.message_id
  user_id = str(message.from_user.id)
  user_data = await state.get_data()
  d = message.data


  if d == 'queues_update':
    m, t = await keyboard.get_queues(update=True, type=user_data['type_check_queues'])
    try:
      await bot.edit_message_text(t, chat, message_id, reply_markup=m, parse_mode='html')
    except:
      pass

  if d == 'select_gpt':
    await state.update_data(type_check_queues='gpt')
    m, t = await keyboard.get_queues(type='gpt')
    try:
      await bot.edit_message_text(t, chat, message_id, reply_markup=m, parse_mode='html')
    except:
      pass
    await queues_state.queues_update.set()

  return True


@dp.message_handler(isPrivate(), commands=['purge_query'], state="*")
async def purge_query(message: types.Message):
  chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, message.from_user.username and f"@{message.from_user.username}" or "", str(
    message.from_user.id)
  await mongo_conn.db.queues.delete_many({})
  await bot.send_message(chat, 'Очереди были очищенны')


