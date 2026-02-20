from config import OWNER_ID
from premium import add_premium

async def admin_commands(client, message):
    if message.from_user.id != OWNER_ID:
        return

    cmd = message.text.split()

    if cmd[0] == "/addpremium":
        user_id = int(cmd[1])
        days = int(cmd[2])
        await add_premium(user_id, days)
        await message.reply("✅ Premium Added")
