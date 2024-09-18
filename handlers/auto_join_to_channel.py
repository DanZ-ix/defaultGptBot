
from loader import dp, types, bot, auto_join_message, logging, FSMContext, channels_auto_join, mongo_conn
import asyncio


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
