from aiogram.utils.exceptions import MessageToDeleteNotFound

from filters import isAdmin
from loader import dp, types, bot, auto_join_message, logging, FSMContext, channels_auto_join, mongo_conn, user_states
import asyncio

from utils.state_progress import state_profile


@dp.chat_join_request_handler()
async def join_request(update: types.ChatJoinRequest, state: FSMContext):
    chat, user_id = update.chat.id, update.from_user.id

    if str(chat) in channels_auto_join:
        try:
            await update.approve()
            if user_id not in user_states:
                user_states[user_id] = {"stop": False}

            asyncio.create_task(send_cycle(user_id))

        except Exception as e:
            logging.error("Exception WHILE AUTO JOIN", exc_info=True)


async def send_cycle(user_id):
    total_time = 0
    time_limit = 150
    time_sleep = 30
    try:
        while total_time < time_limit:
            if user_states[user_id]["stop"]:
                break

            try:
                # Отправляем сообщение
                msg = await bot.send_message(user_id, auto_join_message, parse_mode='html', disable_web_page_preview=True)

                # Ждём 60 секунд
                await asyncio.sleep(time_sleep)

                # Удаляем сообщение
                if total_time + time_sleep < time_limit and not user_states[user_id][
                    "stop"]:  # Проверяем, что это не последняя итерация
                    await bot.delete_message(user_id, msg.message_id)

            except MessageToDeleteNotFound:
                pass

            total_time += time_sleep

        # Очищаем состояние пользователя после завершения цикла
        if user_id in user_states:
            del user_states[user_id]

    except Exception as e:
        logging.error("Exception occurred SEND_MESSAGE_CYCLE", exc_info=True)

    message_dict = await mongo_conn.db.saved_messages.find_one({"message_id": {"$gt": 0}})
    if message_dict is not None:
        try:
            new_message = types.Message.to_object(message_dict)
            file_json = sorted(new_message.photo, key=lambda d: d['file_size'])[-1]

            file = await bot.download_file_by_id(file_json.file_id)
            await bot.send_photo(user_id, file, caption=new_message.caption,
                                 caption_entities=new_message.caption_entities,
                                 reply_markup=new_message.reply_markup, disable_web_page_preview=True)
        except Exception:
            new_message = types.Message.to_object(message_dict)
            await bot.send_message(user_id, new_message.text,
                                   entities=new_message.entities,
                                   reply_markup=new_message.reply_markup, disable_web_page_preview=True)




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
