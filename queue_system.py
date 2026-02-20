from database import queue

async def add_to_queue(user_id, url):
    await queue.insert_one({"user_id": user_id, "url": url})

async def get_next():
    return await queue.find_one_and_delete({})
