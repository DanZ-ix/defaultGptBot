from loader import dp, types, FSMContext, bot, mongo_conn, logging
from filters.filter_commands import isPrivate, isAdmin


#                   -------------------------ADD LINK ----- CHECK LINKS ------------------------------
from utils.state_progress import state_profile


@dp.message_handler(isPrivate(), commands=['add_link'], state="*")
async def add_invite_link(message: types.Message, state: FSMContext):
  chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, message.from_user.username and f"@{message.from_user.username}" or "", str(
    message.from_user.id)
  id = await mongo_conn.db.links.count_documents({})

  link = {'link_id': id, 'admin_id': user_id, 'invited_number': 0, 'deleted': False}
  await mongo_conn.db.links.insert_one(link)
  await bot.send_message(chat, 'Ссылка создана: ' + f'<code>https://t.me/{bot["username"]}?start={id}</code>', parse_mode='html')



@dp.message_handler(isPrivate(), commands=['show_links'], state="*")
async def show_links(message: types.Message, state: FSMContext):
  chat, fullname, username, user_id = message.chat.id, message.from_user.full_name, message.from_user.username and f"@{message.from_user.username}" or "", str(
    message.from_user.id)

  user_links = []
  async for link in mongo_conn.db.links.find({'deleted': False}):
    if link.get('admin_id') == user_id:
      user_links.append(link)

  ret_message = 'Ваши ссылки: \n'

  if (len(user_links) == 0):
    await bot.send_message(chat, 'У вас пока нет ссылок, нужно создзать их с помощью команды /add_link', parse_mode='html')
    return


  for link in user_links:
    ret_message += f'<code>https://t.me/{bot["username"]}?start={link.get("link_id")}</code>\nКоличество откликов по ней: {link.get("invited_number")}\n\n'

  await bot.send_message(chat, ret_message, parse_mode='html')
#                   -------------------------ADD LINK ----- CHECK LINKS ------------------------------




#                   -------------------------JOIN MESSAGE------------------------------

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

#                   -------------------------JOIN MESSAGE------------------------------









