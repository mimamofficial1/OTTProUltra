from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL")

mongo = AsyncIOMotorClient(MONGO_URL)
db = mongo["OTTProUltra"]
users = db["users"]
