import os
import time
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from database import users

app = Client("OTTProUltra", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def add_user(user_id):
    if not await users.find_one({"_id": user_id}):
        await users.insert_one({
            "_id": user_id,
            "premium": False,
            "downloads": 0
        })


async def check_limit(user_id):
    user = await users.find_one({"_id": user_id})
    if user["premium"]:
        return True
    return user["downloads"] < DAILY_LIMIT


async def increase_download(user_id):
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"downloads": 1}}
    )


@app.on_message(filters.command("start"))
async def start(client, message):
    await add_user(message.from_user.id)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Buy Premium", callback_data="buy")],
    ])

    await message.reply_text(
        "👋 Welcome to OTT Pro Ultra\n\nFree users have limited downloads.",
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex("buy"))
async def buy(client, query):
    await query.message.edit(
        "💎 Contact admin to buy premium access."
    )


@app.on_message(filters.text & ~filters.command(["start"]))
async def download(client, message):
    user_id = message.from_user.id
    await add_user(user_id)

    if not await check_limit(user_id):
        return await message.reply_text("❌ Daily limit reached. Buy Premium.")

    await increase_download(user_id)

    url = message.text.strip()
    filename = "video.mp4"

    status = await message.reply_text("🔄 Downloading...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(filename, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        f.write(chunk)

        await status.edit("📤 Uploading...")
        await message.reply_video(filename)
        os.remove(filename)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error: {e}")


app.run()
