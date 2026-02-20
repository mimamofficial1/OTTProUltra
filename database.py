from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL
import datetime

client = AsyncIOMotorClient(MONGO_URL)
db = client.OTTBot

users = db.users
premium = db.premium
queue = db.queue
