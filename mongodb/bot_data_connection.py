import motor.motor_asyncio


class MongoControllerConnection:
  db_name = 'controller'
  client, db = None, None

  async def connect_server(self):
    self.client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://127.0.0.1:27017/?retryWrites=true&w=majority', serverSelectionTimeoutMS=5000)
    self.db = self.client[self.db_name]


mongo_conn = MongoControllerConnection()


