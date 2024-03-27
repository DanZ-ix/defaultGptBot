from datetime import datetime
import aiohttp

from loader import dp, types, bot, mongo_conn, FSMContext, bot_token
from filters.filter_commands import isPrivate
from utils.keyboards import keyboard
from utils.state_progress import accounts_state
from utils.other import other_commands


async def add_gpt_acc(tokens, user_id, chat, message, user_data):
  data = []
  async for acc in mongo_conn.db.accounts.find({'token': {'$in': tokens}}):
    tokens.remove(acc['token'])

  new_acc, no_valid_token = [], 0
  for i in range(0, len(tokens)):
    token = tokens[i]
    # balance = await gpt_api.get_grants(token)
    balance = 2
    if balance == 0.0:
      balance = 0.1
    if balance:
      if balance > 1:
        acc = {'user_id': user_id, 'chat_id': chat, 'token': token, 'date': datetime.now(), 'used': False, 'type': 'gpt', 'queue_count': 0}
        data.append(acc)
      else:
        no_valid_token += 1
    else:
      i -= 1

  if data:
    if len(data) > 1:
      await mongo_conn.db.accounts.insert_many(data)
    else:
      await mongo_conn.db.accounts.insert_one(data[0])

  await other_commands.set_trash(message, chat=chat)
  t, m = await keyboard.get_accounts_gpt()
  await bot.edit_message_text(f'Добавлено {len(data)} токенов для GPT, невалидных токенов: {no_valid_token}', chat, user_data['msg_id'], reply_markup=m)
  await accounts_state.control_accounts_gpt.set()


@dp.message_handler(isPrivate(), commands=['control_accounts'], state="*")
async def accounts_manager(message: types.Message):
  chat, username, user_id = message.chat.id, message.from_user.username and f"@{message.from_user.username}" or "", str(message.from_user.id)

  m = await keyboard.variant_add_account()
  await bot.send_message(chat, 'Добавить токены ChatGPT?', reply_markup=m)
  await accounts_state.select_type_control.set()



@dp.callback_query_handler(isPrivate(), state=accounts_state.select_type_control)
async def callback_data(message: types.CallbackQuery, state: FSMContext):
  chat, message_id = str(message.message.chat.id), message.message.message_id

  if message.data == 'gpt_add_acc':
    t, m = await keyboard.get_accounts_gpt()
    await bot.edit_message_text(t, chat, message_id, reply_markup=m)
    await accounts_state.control_accounts_gpt.set()




@dp.callback_query_handler(isPrivate(), state=accounts_state.control_accounts_gpt)
async def callback_data(message: types.CallbackQuery, state: FSMContext):
  chat, message_id = str(message.message.chat.id), message.message.message_id

  msg, d = '', message.data.split(":")

  if d[0] == 'add_acc_text':
    await other_commands.set_trash(chat=chat)
    msg = await bot.send_message(chat, 'Напишите каждый токен с новой строки')
    await accounts_state.add_accounts_gpt_with_text.set()

  if d[0] == 'add_acc_file':
    await other_commands.set_trash(chat=chat)
    msg = await bot.send_message(chat, 'Отправьте файл с токенами, где каждый токен написан с новой строки')
    await accounts_state.add_accounts_gpt_with_file.set()

  await other_commands.set_trash(msg)
  await state.update_data(msg_id=message_id)


@dp.message_handler(isPrivate(), state=accounts_state.add_accounts_gpt_with_text)
async def add(message: types.Message, state: FSMContext):
  chat, username, user_id = message.chat.id, message.from_user.username and f"@{message.from_user.username}" or "", str(message.from_user.id)
  tokens = message.text.strip().split('\n')
  user_data = await state.get_data()
  await add_gpt_acc(tokens, user_id, chat, message, user_data)


@dp.message_handler(isPrivate(), content_types='document', state=accounts_state.add_accounts_gpt_with_file)
async def get_tokens_with_file(message: types.document, state: FSMContext):
  chat, user_id = message.chat.id, str(message.from_user.id)
  user_data = await state.get_data()
  file_id = message.document.file_id
  f = await bot.get_file(file_id)
  async with aiohttp.ClientSession() as session:
    res = await session.get(f'https://api.telegram.org/file/bot{bot_token}/{f.file_path}')
    tokens = (await res.text()).strip().replace('\r', '').split('\n')
    await add_gpt_acc(tokens, user_id, chat, message, user_data)
