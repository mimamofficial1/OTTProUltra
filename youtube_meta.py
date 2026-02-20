from pytube import YouTube

async def get_metadata(url):
    yt = YouTube(url)
    return {
        "title": yt.title,
        "duration": yt.length,
        "views": yt.views,
        "thumb": yt.thumbnail_url
    }
