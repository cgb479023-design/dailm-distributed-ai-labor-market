"""
Web Channel — Read any URL via Jina Reader.

Zero-config, zero-cost. Converts any webpage to clean Markdown.
This replaces heavy Playwright browser automation for read-only tasks.

Usage:
    curl https://r.jina.ai/{url}  → clean markdown
"""

import asyncio
import urllib.request
import urllib.parse
from typing import Any, Dict, Tuple
from .channel_base import Channel
from loguru import logger


class WebChannel(Channel):
    name = "web"
    description = "Any webpage via Jina Reader"
    description_zh = "任意网页（Jina Reader 智能提取）"
    backends = ["Jina Reader"]
    tier = 0

    JINA_BASE = "https://r.jina.ai/"

    def can_handle(self, url: str) -> bool:
        # Fallback channel — handles any URL
        return True

    def check(self) -> Tuple[str, str]:
        # Jina Reader is a public API, always available
        return "ok", "Jina Reader API (https://r.jina.ai/) — zero-config"

    async def fetch(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch a webpage's content as clean Markdown via Jina Reader.
        
        Args:
            target: Any URL to read
            timeout: Request timeout in seconds (default 15)
        """
        timeout = kwargs.get("timeout", 15)
        jina_url = f"{self.JINA_BASE}{target}"

        logger.info(f"[WebChannel] Fetching via Jina Reader: {target[:80]}...")

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._sync_fetch, jina_url, timeout)
            
            logger.success(f"[WebChannel] Fetched {len(content)} chars from {target[:60]}")
            return {
                "status": "ok",
                "content": content,
                "source": self.name,
                "url": target,
                "metadata": {
                    "length": len(content),
                    "backend": "jina_reader",
                },
            }
        except Exception as e:
            logger.error(f"[WebChannel] Failed to fetch {target}: {e}")
            return {
                "status": "error",
                "content": "",
                "source": self.name,
                "url": target,
                "metadata": {"error": str(e)},
            }

    def _sync_fetch(self, url: str, timeout: int) -> str:
        """Synchronous HTTP GET via urllib (no extra dependencies)."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DAILM-Agent/2.0 (Metabolic Meta-Agent)",
                "Accept": "text/plain, text/markdown",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
