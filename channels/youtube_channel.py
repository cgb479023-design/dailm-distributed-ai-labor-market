"""
YouTube Channel — Extract video metadata and subtitles via yt-dlp.

Requires: pip install yt-dlp (or system install)
Optional: Node.js or Deno for JS runtime (required for YouTube extraction)

Usage:
    yt-dlp --dump-json "URL"                    → video metadata
    yt-dlp --write-sub --skip-download "URL"    → subtitle extraction
"""

import asyncio
import json
import os
from typing import Any, Dict, Tuple
from urllib.parse import urlparse
from .channel_base import Channel
from loguru import logger


class YouTubeChannel(Channel):
    name = "youtube"
    description = "YouTube video metadata & subtitles"
    description_zh = "YouTube 视频元数据和字幕提取"
    backends = ["yt-dlp"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        return "youtube.com" in domain or "youtu.be" in domain

    def check(self) -> Tuple[str, str]:
        if not self._which("yt-dlp"):
            return "off", "yt-dlp not installed. Install: pip install yt-dlp"

        # Check JS runtime (required for YouTube)
        has_js = self._which("deno") or self._which("node")
        if not has_js:
            return "warn", (
                "yt-dlp installed but missing JS runtime (required for YouTube). "
                "Install Node.js or Deno."
            )

        return "ok", "yt-dlp ready — can extract video info and subtitles"

    async def fetch(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch YouTube video metadata and optionally subtitles.
        
        Args:
            target: YouTube video URL
            subtitles: If True, also extract subtitles (default False)
            lang: Subtitle language preference (default "zh,en")
        """
        extract_subs = kwargs.get("subtitles", False)
        lang = kwargs.get("lang", "zh,en")

        logger.info(f"[YouTubeChannel] Extracting metadata: {target[:80]}...")

        # Step 1: Get video metadata
        loop = asyncio.get_event_loop()
        meta_result = await loop.run_in_executor(
            None, self._extract_metadata, target
        )

        if meta_result["status"] == "error":
            return meta_result

        # Step 2: Optionally extract subtitles
        if extract_subs:
            subs = await loop.run_in_executor(
                None, self._extract_subtitles, target, lang
            )
            meta_result["metadata"]["subtitles"] = subs

        return meta_result

    def _extract_metadata(self, url: str) -> Dict[str, Any]:
        """Extract video metadata via yt-dlp --dump-json."""
        rc, stdout, stderr = self._run_cli(
            ["yt-dlp", "--dump-json", "--no-download", url],
            timeout=30,
        )

        if rc != 0:
            logger.error(f"[YouTubeChannel] yt-dlp failed: {stderr[:200]}")
            return {
                "status": "error",
                "content": "",
                "source": self.name,
                "url": url,
                "metadata": {"error": stderr[:500]},
            }

        try:
            data = json.loads(stdout)
            # Build a clean content summary
            title = data.get("title", "Unknown")
            description = data.get("description", "")[:1000]
            duration = data.get("duration", 0)
            uploader = data.get("uploader", "Unknown")
            view_count = data.get("view_count", 0)

            content = (
                f"# {title}\n\n"
                f"**Uploader:** {uploader}\n"
                f"**Duration:** {duration}s\n"
                f"**Views:** {view_count:,}\n\n"
                f"## Description\n{description}\n"
            )

            # Extract auto-captions if available
            auto_subs = data.get("automatic_captions", {})
            manual_subs = data.get("subtitles", {})
            available_langs = list(manual_subs.keys()) + list(auto_subs.keys())

            return {
                "status": "ok",
                "content": content,
                "source": self.name,
                "url": url,
                "metadata": {
                    "title": title,
                    "uploader": uploader,
                    "duration": duration,
                    "view_count": view_count,
                    "available_subtitle_langs": available_langs[:20],
                    "backend": "yt-dlp",
                },
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "content": stdout[:500],
                "source": self.name,
                "url": url,
                "metadata": {"error": f"JSON parse failed: {e}"},
            }

    def _extract_subtitles(self, url: str, lang: str = "zh,en") -> str:
        """Extract subtitles via yt-dlp."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            rc, stdout, stderr = self._run_cli(
                [
                    "yt-dlp",
                    "--write-sub",
                    "--write-auto-sub",
                    f"--sub-lang={lang}",
                    "--skip-download",
                    "--sub-format=srt/vtt/best",
                    "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
                    url,
                ],
                timeout=60,
            )

            # Find subtitle files
            for f in os.listdir(tmpdir):
                if f.endswith((".srt", ".vtt")):
                    with open(os.path.join(tmpdir, f), "r", encoding="utf-8", errors="replace") as fh:
                        return fh.read()

        return ""
