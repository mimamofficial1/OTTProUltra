import os
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, DAILY_LIMIT
from database import users

app = Client(
    "OTTProUltra",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ---------------- USER SYSTEM ---------------- #

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


# ---------------- START ---------------- #

@app.on_message(filters.command("start"))
async def start(client, message):
    await add_user(message.from_user.id)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Buy Premium", callback_data="buy")]
    ])

    await message.reply_text(
        "👋 Welcome to OTT Pro Ultra\n\n"
        f"Free users daily limit: {DAILY_LIMIT}\n"
        "Send direct video link (non-DRM).",
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex("buy"))
async def buy(client, query):
    await query.message.edit(
        "💎 Contact admin to buy premium access."
    )


# ---------------- DOWNLOAD SYSTEM ---------------- #

@app.on_message(filters.text & ~filters.command(["start", "addpremium", "removepremium"]))
async def download(client, message):
    user_id = message.from_user.id
    await add_user(user_id)

    if not await check_limit(user_id):
        return await message.reply_text("❌ Daily limit reached. Buy Premium.")

    url = message.text.strip()

    if not url.startswith("http"):
        return await message.reply_text("❌ Send valid direct link.")

    status = await message.reply_text("🔄 Downloading...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await status.edit("❌ Invalid or blocked link.")

                filename = "video.mp4"
                with open(filename, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        f.write(chunk)

        await increase_download(user_id)

        await status.edit("📤 Uploading...")
        await message.reply_video(filename, caption="🎬 Uploaded by OTTProUltra")

        os.remove(filename)
        await status.delete()

    except Exception as e:
        await status.edit("❌ Failed to download.")


# ---------------- ADMIN COMMANDS ---------------- #

@app.on_message(filters.command("addpremium") & filters.user(ADMIN_ID))
async def add_premium(client, message):
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Usage:\n/addpremium user_id")

    user = await users.find_one({"_id": user_id})

    if not user:
        await users.insert_one({
            "_id": user_id,
            "premium": True,
            "downloads": 0
        })
    else:
        await users.update_one(
            {"_id": user_id},
            {"$set": {"premium": True}}
        )

    await message.reply_text(f"✅ User {user_id} is now Premium!")


@app.on_message(filters.command("removepremium") & filters.user(ADMIN_ID))
async def remove_premium(client, message):
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Usage:\n/removepremium user_id")

    await users.update_one(
        {"_id": user_id},
        {"$set": {"premium": False}}
    )

    await message.reply_text(f"❌ User {user_id} premium removed.")


# ---------------- RUN ---------------- #

app.run()
