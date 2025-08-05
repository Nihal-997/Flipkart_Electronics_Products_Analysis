import requests
import os

def download_image(url, folder, title):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Clean title to use as filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        file_path = os.path.join(folder, f"{safe_title}.jpg")

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Image saved as {file_path}")
        else:
            print(f"⚠️ Failed to download image from {url}")
    except Exception as e:
        print(f"🚫 Error downloading image: {e}")