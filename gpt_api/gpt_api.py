from datetime import datetime, timedelta
import asyncio
from loader import mongo_conn, logging, exceptions, yandex_gpt


time_start = datetime.now()

class gptApi:

  async def send_query(self, bot, data):
    try:
      result = await yandex_gpt.run(data['query'])   # TODO Добавить возможность добавления системного промта
      return result[0].text, ''

    except Exception as e:
      logging.error("Exception GPT", exc_info=True)
      return False, 'update'

  async def get_answer_repeat(self, bot, queue):
    try:
      queue['dialogs'] = [d for d in queue['dialogs'] if (d['role'] == 'user' or isinstance(d['content'], str))]

      if queue.get('not_message') == None:
        try:
          await bot.delete_message(queue['chat_id'], queue['message_id'])
        except:
          pass

        if queue.get('repeat') == 0 or queue.get('repeat') == None:
          try:
            msg = await bot.send_message(queue['chat_id'], '⌛️ Подготовка ответа...')
            await mongo_conn.db.queues.update_one({'user_id': queue['user_id']},
              {'$set': {'message_id1': msg.message_id}})
          except (exceptions.BotBlocked, exceptions.BotKicked):
            await mongo_conn.db.queues.delete_one({'user_id': queue['user_id']})
            return False

      answer, trigger = await self.send_query(bot, queue)
      if answer:
        queue['dialogs'].append({'role': 'assistant', 'content': answer})
        token_count = 0
        for d in queue['dialogs']:
          if d.get('content'):
            token_count += len(d['content'])

        edit = True

        q = await mongo_conn.db.queues.find_one({'user_id': queue['user_id'], 'type': 'gpt'})
        while answer != '':
          t = answer[0: 4095]     # max length of tg message
          answer = answer.replace(t, '')
          try:
            if queue.get('not_message') == None:
              if not edit:
                await bot.send_message(queue['chat_id'], t)
              else:
                edit = False
                await bot.edit_message_text(t, queue['chat_id'], q['message_id1'])
            else:
              await bot.send_message(queue['chat_id'], t, reply_to_message_id=queue['message_id'])

          except:
            pass

          await asyncio.sleep(1)
        await mongo_conn.db.queues.delete_one({'user_id': queue['user_id']})
        return True
      else:
        if trigger == 'update':
          if queue.get('repeat') != None:
            await mongo_conn.db.queues.update_one({'user_id': queue['user_id'], 'type': 'gpt'},
              {'$set': {'status': 'wait'}, '$inc': {'repeat': 1}})
          else:
            await mongo_conn.db.queues.update_one({'user_id': queue['user_id'], 'type': 'gpt'},
              {'$set': {'status': 'wait', 'repeat': 1}})


    except (exceptions.BotKicked, exceptions.BotBlocked):
      logging.error("Exception occurred", exc_info=True)
    except Exception as e:
      logging.error("Exception occurred", exc_info=True)

  async def check_gpt_queues(self, bot):
    while True:
      try:
        now = datetime.now()
        date_resend = now - timedelta(minutes=8)

        async for queue in mongo_conn.db.queues.find({'type': 'gpt'}):
          try:
            if queue['date'] < date_resend and queue['status'] == 'process':
              await mongo_conn.db.queues.delete_one({'type': 'gpt', 'user_id': queue['user_id']})
              await bot.send_message(queue['chat_id'], 'К сожалению, Ваш запрос не был выполнен. Попробуйте спросить что-то другое.')
              continue

            if queue['status'] == 'wait':
              await mongo_conn.db.queues.update_one({'user_id': queue['user_id'], 'type': 'gpt'}, {
                '$set': {'status': 'process', 'date': datetime.now()}})
              asyncio.create_task(self.get_answer_repeat(bot, queue))
          except Exception as e:
            logging.error("Exception occurred", exc_info=True)

      except Exception as e:
        logging.error("Exception occurred", exc_info=True)
      await asyncio.sleep(1)
