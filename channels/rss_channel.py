"""
RSS Channel — Parse RSS/Atom feeds via feedparser.

Zero-config. Requires: pip install feedparser
"""

import asyncio
from typing import Any, Dict, Tuple
from .channel_base import Channel
from loguru import logger


class RSSChannel(Channel):
    name = "rss"
    description = "RSS/Atom feed reader"
    description_zh = "RSS/Atom 订阅源解析"
    backends = ["feedparser"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        url_lower = url.lower()
        return any(k in url_lower for k in ("/rss", "/feed", "/atom", ".xml", "rss.xml"))

    def check(self) -> Tuple[str, str]:
        try:
            import feedparser
            return "ok", f"feedparser {feedparser.__version__} ready"
        except ImportError:
            return "off", "feedparser not installed. Install: pip install feedparser"

    async def fetch(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Parse an RSS/Atom feed.
        
        Args:
            target: Feed URL
            limit: Max entries to return (default 20)
        """
        limit = kwargs.get("limit", 20)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._parse_feed, target, limit)

    def _parse_feed(self, url: str, limit: int) -> Dict[str, Any]:
        """Synchronous feed parsing."""
        try:
            import feedparser
        except ImportError:
            return {
                "status": "error",
                "content": "",
                "source": self.name,
                "metadata": {"error": "feedparser not installed"},
            }

        logger.info(f"[RSSChannel] Parsing feed: {url[:80]}...")
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            return {
                "status": "error",
                "content": "",
                "source": self.name,
                "url": url,
                "metadata": {"error": str(feed.bozo_exception)},
            }

        title = feed.feed.get("title", "Unknown Feed")
        entries = feed.entries[:limit]

        lines = [f"# {title}\n"]
        for entry in entries:
            pub = entry.get("published", entry.get("updated", ""))
            lines.append(f"- **{entry.get('title', 'Untitled')}** ({pub})")
            if entry.get("summary"):
                # Strip HTML tags crudely
                import re
                clean = re.sub(r"<[^>]+>", "", entry["summary"])[:200]
                lines.append(f"  {clean}")
            if entry.get("link"):
                lines.append(f"  [Link]({entry['link']})")
            lines.append("")

        content = "\n".join(lines)
        logger.success(f"[RSSChannel] Parsed {len(entries)} entries from {title}")

        return {
            "status": "ok",
            "content": content,
            "source": self.name,
            "url": url,
            "metadata": {
                "feed_title": title,
                "entry_count": len(entries),
                "backend": "feedparser",
            },
        }
