import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from config import API_ID, API_HASH, BOT_TOKEN
from downloader import download_file
from youtube_meta import get_metadata
from gdrive import convert_to_direct
from premium import is_premium
from forcejoin import force_join
from admin import admin_commands
from queue_system import add_to_queue

app = Client(
    "OTTBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- START ---------------- #

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "🔥 Premium Downloader Bot Ready\n\n"
        "Send me:\n"
        "• Direct File Link\n"
        "• Google Drive Link\n"
        "• YouTube Link (Metadata Only)"
    )

# ---------------- ADMIN ---------------- #

@app.on_message(filters.command(["addpremium", "removepremium"]))
async def admin_panel(client, message: Message):
    await admin_commands(client, message)

# ---------------- MAIN HANDLER ---------------- #

@app.on_message(filters.text & ~filters.command(["start", "addpremium", "removepremium"]))
async def handle_links(client, message: Message):

    user_id = message.from_user.id
    url = message.text.strip()

    # 🔒 Force Join Check
    if not await force_join(client, message):
        return

    # 👑 Premium Check (optional logic)
    premium_user = await is_premium(user_id)

    # ---------------- YOUTUBE METADATA ---------------- #
    if "youtube.com" in url or "youtu.be" in url:
        try:
            status = await message.reply("🔎 Fetching YouTube info...")

            data = await get_metadata(url)

            await message.reply_photo(
                data["thumb"],
                caption=f"🎬 {data['title']}\n"
                        f"⏱ {data['duration']} sec\n"
                        f"👁 {data['views']} views"
            )

            await status.delete()

        except Exception:
            await message.reply("❌ Failed to fetch YouTube info.")
        return

    # ---------------- GOOGLE DRIVE ---------------- #
    if "drive.google.com" in url:
        await add_to_queue(user_id, url)
        await message.reply("📥 Added to queue (Google Drive).")
        return

    # ---------------- DIRECT DOWNLOAD ---------------- #
    if url.startswith("http"):
        await add_to_queue(user_id, url)
        await message.reply("📥 Added to queue (Direct Link).")
        return

    await message.reply("❌ Invalid link sent.")


# ---------------- QUEUE WORKER ---------------- #

from queue_system import get_next

async def queue_worker():
    while True:
        data = await get_next()
        if data:
            user_id = data["user_id"]
            url = data["url"]

            try:
                user = await app.get_users(user_id)
                msg = await app.send_message(user_id, "⬇️ Downloading...")

                file_path = await download_file(url, msg)

                await app.send_video(
                    user_id,
                    file_path,
                    caption="🎬 Uploaded Successfully"
                )

            except Exception as e:
                await app.send_message(user_id, "❌ Download Failed.")

        await asyncio.sleep(3)


# ---------------- RUN ---------------- #

async def main():
    await app.start()
    asyncio.create_task(queue_worker())
    print("🚀 Bot Started")
    await idle()

from pyrogram import idle

app.run()
