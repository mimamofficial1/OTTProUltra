import re

def convert_to_direct(url: str):
    file_id = None

    patterns = [
        r"/file/d/([^/]+)",
        r"id=([^&]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            break

    if not file_id:
        return None

    return f"https://drive.google.com/uc?export=download&id={file_id}"
