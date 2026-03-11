"""
System Doctor — Unified health diagnostics for DAILM.

Checks:
  1. All internet data channels (YouTube, GitHub, Web, RSS...)
  2. All AI adapter nodes (Gemini, Claude, Grok...)
  3. System resources (CPU, Memory, Disk)
  
Usage:
    GET /api/system/doctor → JSON health report
"""

import os
import time
from typing import Any, Dict
from loguru import logger

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class SystemDoctor:
    """Diagnose the health of the entire DAILM system."""

    def __init__(self, status_manager=None):
        self.status_manager = status_manager

    async def diagnose(self) -> Dict[str, Any]:
        """Run full system diagnostics."""
        start = time.time()
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "channels": self._check_channels(),
            "adapters": self._check_adapters(),
            "system": self._check_system(),
        }

        # Summary
        ch_statuses = [v["status"] for v in report["channels"].values()]
        ad_statuses = [v["status"] for v in report["adapters"].values()]
        
        ok_count = ch_statuses.count("ok") + ad_statuses.count("ok")
        warn_count = ch_statuses.count("warn") + ad_statuses.count("warn")
        off_count = ch_statuses.count("off") + ad_statuses.count("off")
        error_count = ch_statuses.count("error") + ad_statuses.count("error")
        total = len(ch_statuses) + len(ad_statuses)

        if error_count > 0:
            overall = "DEGRADED"
        elif warn_count > total * 0.5:
            overall = "PARTIAL"
        elif ok_count == total:
            overall = "HEALTHY"
        else:
            overall = "OPERATIONAL"

        report["summary"] = {
            "overall": overall,
            "ok": ok_count,
            "warn": warn_count,
            "off": off_count,
            "error": error_count,
            "total": total,
            "diagnosis_time_ms": round((time.time() - start) * 1000, 1),
        }

        logger.info(f"[Doctor] Diagnosis complete: {overall} ({ok_count}/{total} ok)")
        return report

    def _check_channels(self) -> Dict[str, Any]:
        """Check all internet data channels."""
        try:
            from channels import check_all
            return check_all()
        except ImportError:
            return {"error": {"status": "error", "message": "channels module not found"}}

    def _check_adapters(self) -> Dict[str, Any]:
        """Check AI adapter node statuses from StatusManager."""
        adapters = {}

        if self.status_manager and hasattr(self.status_manager, "nodes"):
            for node_id, node_data in self.status_manager.nodes.items():
                status_raw = node_data.get("status", "UNKNOWN")
                load = node_data.get("load", 0)

                # Map internal statuses to doctor format
                if status_raw == "READY":
                    status = "ok"
                    msg = f"Ready (load: {load}%)"
                elif status_raw == "BUSY" or status_raw == "PROCESSING":
                    status = "ok"
                    msg = f"Active (load: {load}%)"
                elif status_raw == "STANDBY":
                    status = "warn"
                    msg = "Standby — not actively registered"
                elif status_raw == "OFFLINE":
                    status = "off"
                    msg = "Offline"
                else:
                    status = "warn"
                    msg = f"Unknown state: {status_raw}"

                adapters[node_id] = {
                    "status": status,
                    "message": msg,
                    "load": load,
                    "raw_status": status_raw,
                }
        else:
            adapters["system"] = {
                "status": "warn",
                "message": "StatusManager not available",
            }

        return adapters

    def _check_system(self) -> Dict[str, Any]:
        """Check system hardware resources."""
        if not HAS_PSUTIL:
            return {
                "cpu": "N/A (psutil not installed)",
                "memory": "N/A",
                "disk": "N/A",
            }

        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())

            return {
                "cpu_percent": cpu_percent,
                "cpu_status": "ok" if cpu_percent < 80 else "warn",
                "memory_used_gb": round(mem.used / (1024**3), 1),
                "memory_total_gb": round(mem.total / (1024**3), 1),
                "memory_percent": mem.percent,
                "memory_status": "ok" if mem.percent < 85 else "warn",
                "disk_used_gb": round(disk.used / (1024**3), 1),
                "disk_total_gb": round(disk.total / (1024**3), 1),
                "disk_percent": round(disk.percent, 1),
                "disk_status": "ok" if disk.percent < 90 else "warn",
            }
        except Exception as e:
            return {"error": str(e)}
