import aiohttp
import os

async def download_file(url, message):
    filename = "video.mp4"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024):
                    f.write(chunk)
                    downloaded += len(chunk)

                    percent = int(downloaded * 100 / total)
                    await message.edit(f"⬇️ Downloading... {percent}%")

    return filename
