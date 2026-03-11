"""
Channel Registry — All registered internet data channels.

Provides:
  - ALL_CHANNELS: list of all channel instances
  - get_channel(name): lookup by name
  - get_channel_for_url(url): auto-route URL to correct channel
  - check_all(): health diagnostics for all channels
"""

from typing import Dict, List, Optional, Tuple
from .channel_base import Channel

# Import all channels
from .web_channel import WebChannel
from .youtube_channel import YouTubeChannel
from .github_channel import GitHubChannel
from .rss_channel import RSSChannel


# Channel registry — order matters for URL routing (first match wins)
# Web channel is last because it's the fallback (can_handle always returns True)
ALL_CHANNELS: List[Channel] = [
    YouTubeChannel(),
    GitHubChannel(),
    RSSChannel(),
    WebChannel(),       # Fallback — must be last
]


def get_channel(name: str) -> Optional[Channel]:
    """Get a channel by name."""
    for ch in ALL_CHANNELS:
        if ch.name == name:
            return ch
    return None


def get_channel_for_url(url: str) -> Optional[Channel]:
    """Auto-route a URL to the correct channel (first match wins)."""
    for ch in ALL_CHANNELS:
        if ch.can_handle(url):
            return ch
    return None


def get_all_channels() -> List[Channel]:
    """Get all registered channels."""
    return ALL_CHANNELS


def check_all() -> Dict[str, Tuple[str, str]]:
    """Run health diagnostics on all channels. Returns {name: (status, message)}."""
    results = {}
    for ch in ALL_CHANNELS:
        try:
            status, msg = ch.check()
            results[ch.name] = {
                "status": status,
                "message": msg,
                "description": ch.description_zh or ch.description,
                "backends": ch.backends,
                "tier": ch.tier,
            }
        except Exception as e:
            results[ch.name] = {
                "status": "error",
                "message": str(e),
                "description": ch.description,
                "backends": ch.backends,
                "tier": ch.tier,
            }
    return results


__all__ = [
    "Channel",
    "ALL_CHANNELS",
    "get_channel",
    "get_channel_for_url",
    "get_all_channels",
    "check_all",
]
