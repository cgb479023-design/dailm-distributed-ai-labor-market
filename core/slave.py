"""
SLAVE Subsystem — Security & Load-balancing Agent for Variable Environments.

This module implements the "Risk Control System (SLAVE)" from the DAILM target architecture.
It acts as a shield for the internet channels, providing:
  1. Proxy Pool Rotation (Local IP / Residential Proxy switching)
  2. Circuit Breaking (Automatic fallback on 403/429 errors)
  3. Traffic Shaping & Rate Limiting (Anti-ban)

Channels should route HTTP/CLI requests through `execute_safe()` instead of raw calls.
"""

import asyncio
import os
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from loguru import logger


class ProxyPool:
    """Manages a pool of proxy URLs and their health scores."""
    def __init__(self, proxies: List[str] = None):
        # Format: {"http://proxy:port": {"score": 100, "failures": 0, "last_used": 0.0}}
        self.pool: Dict[str, Dict[str, Any]] = {}
        if not proxies:
            # Fallback to env vars if no explicit list provided
            env_proxy = os.getenv("DAILM_HTTP_PROXY") or os.getenv("HTTP_PROXY")
            if env_proxy:
                self.pool[env_proxy] = self._default_stats()
            # Always keep "direct" (no proxy) as the ultimate fallback
            self.pool["DIRECT"] = self._default_stats()
        else:
            for p in proxies:
                self.pool[p] = self._default_stats()

    def _default_stats(self) -> Dict[str, Any]:
        return {"score": 100, "failures": 0, "last_used": 0.0}

    def get_proxy(self) -> str:
        """Select a proxy using a score-weighted random choice, favoring healthy proxies."""
        if not self.pool:
            return "DIRECT"
        
        candidates = []
        for p, stats in self.pool.items():
            # Don't use proxies that have failed too many times recently
            if stats["score"] > 20:
                # Weight by score and decay slightly by recency to distribute load
                weight = stats["score"]
                if time.time() - stats["last_used"] < 5.0:
                    weight *= 0.5
                candidates.extend([p] * int(max(1, weight)))

        if not candidates:
            # If all proxies are depleted/banned, fallback to DIRECT
            logger.warning("[SLAVE] Proxy pool depleted! Falling back to DIRECT connection.")
            return "DIRECT"

        selected = random.choice(candidates)
        self.pool[selected]["last_used"] = time.time()
        return selected

    def report_success(self, proxy: str):
        """Reward a proxy for a successful request."""
        if proxy in self.pool:
            self.pool[proxy]["score"] = min(100, self.pool[proxy]["score"] + 10)
            self.pool[proxy]["failures"] = 0

    def report_failure(self, proxy: str, status_code: int = 0):
        """Penalize a proxy for failure (especially 403/429 bans)."""
        if proxy in self.pool:
            self.pool[proxy]["failures"] += 1
            penalty = 50 if status_code in (403, 429) else 20
            self.pool[proxy]["score"] = max(0, self.pool[proxy]["score"] - penalty)
            logger.warning(f"[SLAVE] Proxy {proxy} penalized (score: {self.pool[proxy]['score']}) after HTTP {status_code/0 if status_code==0 else status_code}")


class SlaveSubsystem:
    """The main risk control and execution wrapper."""
    
    def __init__(self, proxies: List[str] = None):
        self.proxy_pool = ProxyPool(proxies)
        self.total_requests = 0
        self.blocked_requests = 0

    def get_health_stats(self) -> Dict[str, Any]:
        """Return diagnostic stats for the System Doctor."""
        active_proxies = len([p for p, s in self.proxy_pool.pool.items() if s["score"] > 50])
        return {
            "module": "SLAVE",
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "active_proxies": active_proxies,
            "pool_size": len(self.proxy_pool.pool),
        }

    async def execute_safe(
        self, 
        operation_name: str,
        func: Callable, 
        *args, 
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an IO-bound function (like a channel fetch) with SLAVE protection.
        Automatically rotates proxies upon 403/429/Timeout errors.
        
        Args:
            operation_name: For logging (e.g., "WebChannel.fetch")
            func: Async function to execute. MUST accept a 'proxy' kwarg.
            max_retries: How many times to retry with different proxies.
        """
        self.total_requests += 1
        last_error = None

        for attempt in range(1, max_retries + 1):
            proxy = self.proxy_pool.get_proxy()
            logger.debug(f"[SLAVE] {operation_name} (Attempt {attempt}/{max_retries}) using proxy: {proxy}")

            # Inject the assigned proxy into the kwargs
            kwargs["proxy"] = proxy if proxy != "DIRECT" else None

            try:
                # Execute the actual network call
                result = await func(*args, **kwargs)
                
                # Check for synthetic errors returned by the channel
                if isinstance(result, dict) and result.get("status") == "error":
                    error_msg = str(result.get("metadata", {}).get("error", ""))
                    # Heuristic ban detection (403 Forbidden, 429 Too Many Requests, CAPTCHA)
                    if any(b in error_msg.lower() for b in ("403", "429", "forbidden", "captcha", "rate limit")):
                        raise PermissionError(f"Detected IP Block/Rate Limit: {error_msg}")
                
                # Success!
                self.proxy_pool.report_success(proxy)
                return result

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                status_code = 403 if "403" in err_str or "forbidden" in err_str else \
                              429 if "429" in err_str or "rate limit" in err_str else 0
                
                self.proxy_pool.report_failure(proxy, status_code=status_code)
                self.blocked_requests += 1
                
                logger.warning(f"[SLAVE] {operation_name} failed on {proxy}: {e}")
                
                if attempt < max_retries:
                    # Exponential backoff jitter
                    backoff = random.uniform(1.0, 3.0) * attempt
                    logger.info(f"[SLAVE] Circuit open. Backing off for {backoff:.1f}s before retry...")
                    await asyncio.sleep(backoff)

        logger.error(f"[SLAVE] {operation_name} exhausted all {max_retries} retries. Final error: {last_error}")
        return {
            "status": "error",
            "source": "SLAVE_SUBSYSTEM",
            "metadata": {"error": f"Max retries exhausted. Last error: {last_error}"}
        }
