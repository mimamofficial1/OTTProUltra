from pyrogram.errors import UserNotParticipant
from config import FORCE_CHANNEL

async def force_join(client, message):
    try:
        await client.get_chat_member(FORCE_CHANNEL, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply_text(
            f"⚠️ Join @{FORCE_CHANNEL} to use this bot."
        )
        return False
