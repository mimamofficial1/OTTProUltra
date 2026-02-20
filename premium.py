import datetime
from database import premium

async def add_premium(user_id, days):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    await premium.update_one(
        {"user_id": user_id},
        {"$set": {"expiry": expiry}},
        upsert=True
    )

async def is_premium(user_id):
    data = await premium.find_one({"user_id": user_id})
    if not data:
        return False

    if data["expiry"] < datetime.datetime.utcnow():
        await premium.delete_one({"user_id": user_id})
        return False

    return True
