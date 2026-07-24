import json
import os
import sys
from typing import Any, Dict, List
import requests

# গিটহাব লগে সুন্দর কালারফুল ও প্রিমিয়াম আউটপুটের জন্য rich ব্যবহার
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
except ImportError:
    # যদি কোনো কারণে rich মিসিং থাকে তার জন্য পলব্যাক কাস্টম কনসোল
    class Console:

        def print(self, *args, **kwargs):
            print(*args)

    console = Console()


class ChannelFetcher:

    def __init__(self, output_file: str = "channels.json"):
        self.api_url = os.getenv("API_URL")
        self.output_file = output_file
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

    def fetch_data(self) -> List[Dict[str, Any]]:
        """API থেকে ডেটা ফেচ করে আনবে"""
        if not self.api_url:
            if hasattr(console, "print"):
                console.print(
                    "[bold red]✖ Error:[/bold red] 'API_URL' Environment"
                    " Variable missing!"
                )
            sys.exit(1)

        try:
            response = requests.get(
                self.api_url, headers=self.headers, timeout=20
            )
            response.raise_for_status()
            data = response.json()

            # রেসপন্স টাইপ হ্যান্ডলিং
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("channels") or data.get("data") or []
            return []

        except requests.exceptions.RequestException as e:
            if hasattr(console, "print"):
                console.print(
                    f"[bold red]✖ Network Error:[/bold red] {str(e)}"
                )
            sys.exit(1)

    def process_channels(
        self, raw_channels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """ডাটা প্রসেস ও ক্লিনিং"""
        processed = []
        for ch in raw_channels:
            name = ch.get("name") or ch.get("title") or "Unknown Channel"
            logo = ch.get("logo") or ch.get("image") or ""
            category = ch.get("category") or "General"
            stream_url = ch.get("url") or ch.get("stream_url") or ""

            # শুধুমাত্র ভ্যালিড চ্যানেল সেভ করবে
            if name and logo:
                processed.append(
                    {
                        "id": len(processed) + 1,
                        "name": str(name).strip(),
                        "logo": str(logo).strip(),
                        "category": str(category).strip(),
                        "stream_url": str(stream_url).strip(),
                    }
                )

        return processed

    def save_and_display(self, channels: List[Dict[str, Any]]):
        """JSON এ সেভ করবে এবং টার্মিনালে প্রিমিয়াম টেবিল দেখাবে"""
        # JSON সেভ
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=4)

        # সুন্দর UI ডিসপ্লে (Rich Table)
        if hasattr(console, "print"):
            console.print(
                Panel.fit(
                    "[bold green]✨ Live TV Channels Auto-Sync Completed"
                    " Successfully![/bold green]",
                    border_style="bright_blue",
                )
            )

            table = Table(
                title=f"Synced Channels Summary (Total: {len(channels)})",
                header_style="bold magenta",
                border_style="cyan",
            )

            table.add_column("ID", justify="center", style="dim", width=6)
            table.add_column("Channel Name", style="bold white")
            table.add_column("Category", style="yellow")
            table.add_column("Logo Status", justify="center")

            # প্রথম ১০টি চ্যানেল লগে প্রিভিউ হিসেবে দেখাবে
            for ch in channels[:10]:
                logo_status = (
                    "[green]✔ Available[/green]"
                    if ch["logo"]
                    else "[red]✘ Missing[/red]"
                )
                table.add_row(
                    str(ch["id"]), ch["name"], ch["category"], logo_status
                )

            console.print(table)
            if len(channels) > 10:
                console.print(
                    f"[dim italic]+ {len(channels) - 10} more channels saved in"
                    f" {self.output_file}[/dim italic]\n"
                )


if __name__ == "__main__":
    fetcher = ChannelFetcher()
    raw_data = fetcher.fetch_data()
    clean_data = fetcher.process_channels(raw_data)
    fetcher.save_and_display(clean_data)
