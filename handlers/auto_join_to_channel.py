from filters import isAdmin
from loader import dp, types, bot, auto_join_message, logging, FSMContext, channels_auto_join, mongo_conn
import asyncio

from utils.state_progress import state_profile


@dp.chat_join_request_handler()
async def join_request(update: types.ChatJoinRequest, state: FSMContext):
  chat, user_id = update.chat.id, update.from_user.id

  if str(chat) in channels_auto_join:
    try:
      await update.approve()
      await bot.send_message(user_id, auto_join_message, parse_mode='html', disable_web_page_preview=True)
      await asyncio.sleep(10)

      message_dict = await mongo_conn.db.saved_messages.find_one({"message_id": {"$gt": 0}})
      if message_dict is not None:
        new_message = types.Message.to_object(message_dict)
        if new_message.caption is not None:
          await bot.send_message(user_id, new_message.caption,
                                 entities=new_message.caption_entities,
                                 reply_markup=new_message.reply_markup,
                                 disable_web_page_preview=True)
        else:
          await bot.send_message(user_id, new_message.text,
                                 entities=new_message.entities,
                                 reply_markup=new_message.reply_markup,
                                 disable_web_page_preview=True)

    except Exception as e:
      logging.error("Exception WHILE AUTO JOIN", exc_info=True)


@dp.message_handler(isAdmin(), commands=['update_join_message'], state="*")
async def update_join_message(message: types.Message, state: FSMContext):
    await message.answer('Отправьте сообщение для сохранения, необходимо отправить его через кнопку "Ответить". '
                         'Напиши в сообщении "delete" чтобы выключить отправку сообщений')
    await state_profile.await_message.set()


@dp.message_handler(state=state_profile.await_message)
async def save_message(message: types.Message):
    chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, \
                                        message.from_user.username and f"@{message.from_user.username}" or "", \
                                        str(message.from_user.id)

    try:
        if message.text.lower() == 'delete':
            await mongo_conn.db.saved_messages.delete_many({})
            await bot.send_message(user_id, "Приветственное сообщение удалено")
            await state_profile.start_state.set()
        else:
            message_json = message.reply_to_message.to_python()
            await mongo_conn.db.saved_messages.delete_many({})
            await mongo_conn.db.saved_messages.insert_one(message_json)
            await bot.send_message(user_id, "Приветственное сообщение добавлено")

    except Exception as e:
        logging.error(e)
    await state_profile.start_state.set()


@dp.message_handler(isAdmin(), commands=['check_join_message'], state="*")
async def check_join_message(message: types.Message, state: FSMContext):
    chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, message.from_user.username and f"@{message.from_user.username}" or "", str(
        message.from_user.id)
    try:
        message_dict = await mongo_conn.db.saved_messages.find_one({"message_id": {"$gt": 0}})
        if message_dict is not None:
            new_message = types.Message.to_object(message_dict)
            if new_message.caption is not None:
                await bot.send_message(user_id, new_message.caption,
                                       entities=new_message.caption_entities,
                                       reply_markup=new_message.reply_markup,
                                       disable_web_page_preview=True)
            else:
                await bot.send_message(user_id, new_message.text,
                                       entities=new_message.entities,
                                       reply_markup=new_message.reply_markup,
                                       disable_web_page_preview=True)
        else:
            await bot.send_message(user_id, "Приветственное сообщение не найдено")
    except Exception as e:
        logging.error(e)


