"""
Channel Base Class — Internet Data Acquisition Layer.

Inspired by Agent-Reach's pluggable channel architecture.
Each channel represents an internet platform (YouTube, Twitter, Web, etc.)
and provides:
  - can_handle(url) → does this URL belong to this platform?
  - check()         → is the upstream tool installed & configured?
  - fetch(target)   → retrieve data from the platform

After registration, the ModelMatrix can route URLs to the correct channel
just like it routes tasks to the correct AI adapter.
"""

import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
from core.slave import SlaveSubsystem

# Global SLAVE subsystem instance (shared proxy pool across all channels)
GLOBAL_SLAVE = SlaveSubsystem()


class Channel(ABC):
    """Base class for all internet data channels."""

    name: str = ""                     # e.g. "youtube"
    description: str = ""              # e.g. "YouTube 视频和字幕"
    description_zh: str = ""           # e.g. "YouTube 视频和字幕"
    backends: List[str] = []           # e.g. ["yt-dlp"] — what upstream tool powers this
    tier: int = 0                      # 0=zero-config, 1=needs free key, 2=needs setup

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this channel can handle the given URL."""
        ...

    def check(self) -> Tuple[str, str]:
        """
        Check if this channel's upstream tool is available.
        Returns (status, message) where status is one of:
          'ok'    — fully operational
          'warn'  — partially available or degraded
          'off'   — not installed / not configured
          'error' — broken / misconfigured
        """
        return "ok", f"{'、'.join(self.backends) if self.backends else 'built-in'}"

    @abstractmethod
    async def fetch(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the platform.
        Must be implemented by child classes. Use kwargs.get('proxy') if needed.
        """
        ...

    async def safe_fetch(self, target: str, use_slave: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Execute fetch with SLAVE protection (anti-ban, proxy rotation).
        
        Args:
            target: URL or search query
            use_slave: Process through Proxy Pool and Circuit Breaker
            **kwargs: Channel-specific options passed to fetch()
        """
        if not use_slave:
            return await self.fetch(target, **kwargs)
            
        logger.info(f"[Channel:{self.name}] Routing via SLAVE Subsystem...")
        # Wrap the fetch call so SLAVE can intercept and retry on 403/429
        return await GLOBAL_SLAVE.execute_safe(
            operation_name=f"{self.name}.fetch",
            func=self.fetch,
            target=target,
            **kwargs,
        )

    def _which(self, tool: str) -> Optional[str]:
        """Check if a CLI tool is available on PATH."""
        return shutil.which(tool)

    def _run_cli(self, cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """
        Run a CLI command and return (returncode, stdout, stderr).
        Safe wrapper with timeout.
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
        except FileNotFoundError:
            return -2, "", f"Command not found: {cmd[0]}"
        except Exception as e:
            return -3, "", str(e)

    def __repr__(self) -> str:
        return f"<Channel:{self.name} tier={self.tier} backends={self.backends}>"
