import json
import os
import requests


def fetch_and_save_channels():
    # গিটহাব সিক্রেট থেকে URL রিড করা হচ্ছে
    url = os.getenv("API_URL")

    if not url:
        print("Error: API_URL Secret is missing!")
        exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        raw_channels = (
            data if isinstance(data, list) else data.get("channels", [])
        )
        channels_list = []

        for channel in raw_channels:
            channels_list.append(
                {
                    "name": channel.get("name") or channel.get("title"),
                    "logo": channel.get("logo") or channel.get("image"),
                    "category": channel.get("category", "General"),
                    "url": channel.get("url") or channel.get("stream_url"),
                }
            )

        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(channels_list, f, ensure_ascii=False, indent=4)

        print("Successfully updated channels.json")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    fetch_and_save_channels()
