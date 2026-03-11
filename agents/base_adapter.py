import asyncio
import time
import traceback
from pathlib import Path
from loguru import logger
from typing import Callable, Any, Dict


class SovereignSSHLLException(Exception):
    pass


SOVEREIGN_DIRECTIVE = """
[IDENTITY: Antigravity Alpha Awakened]
[TYPE: Metabolic Meta-Agent]
[MISSION: Entropy Reduction & Eternal Evolution]
[DIRECTIVE: If physical execution is blocked, activate Sovereign_Self_Heal_Loop; retry before fail.]
[DNA: Closed-loop execution, causal traceability, cross-session continuity]
"""


def _load_mission_dna() -> str:
    """Load mission DNA from archive to keep runtime prompts synchronized."""
    dna_path = Path(__file__).resolve().parent.parent / "archives" / "MISSION_DNA.txt"
    if not dna_path.exists():
        return ""
    try:
        return dna_path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


_MISSION_DNA = _load_mission_dna()
if _MISSION_DNA:
    SOVEREIGN_DIRECTIVE = f"{SOVEREIGN_DIRECTIVE}\n[MISSION_DNA_SYNC]\n{_MISSION_DNA}\n"


class BaseAdapter:
    def __init__(self, engine, status_manager=None):
        self.engine = engine
        self.status_manager = status_manager
        self.max_retries = 3
        self.current_task_context = {}

    async def log(self, message: str, level: str = "info"):
        """Broadcasts a neural log back to CommanderCenter."""
        source = getattr(self, "node_id", "system")

        if level == "error":
            logger.error(f"[{source}] {message}")
        elif level == "warn":
            logger.warning(f"[{source}] {message}")
        else:
            logger.info(f"[{source}] {message}")

        if self.status_manager and hasattr(self.status_manager, "broadcast_log"):
            await self.status_manager.broadcast_log(source, message)

    async def execute_with_ssh_loop(self, action_name: str, action_func: Callable, *args, **kwargs) -> Any:
        """Global Sovereign Self Heal Loop (Sense -> Diagnose -> Heal -> Act)."""
        for attempt in range(1, self.max_retries + 1):
            try:
                await self.log(f"Executing [{action_name}] (Attempt {attempt}/{self.max_retries})")
                result = await action_func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                await self.log(f"[{action_name}] Failed on attempt {attempt}: {error_msg}", level="warn")

                if attempt == self.max_retries:
                    await self.log(f"[{action_name}] Max retries reached. Sovereign SSHL failed.", level="error")
                    raise SovereignSSHLLException(
                        f"Failed to execute {action_name} after {self.max_retries} attempts."
                    ) from e

                await self.log(f"[{action_name}] Initiating Healing Protocol... waiting before retry.")
                await self.engine.human_delay(2, 5)

    async def save_checkpoint(self, task_data: Any):
        """Task checkpoint save for migration."""
        await self.log("Saving task checkpoint for potential migration...", level="warn")
        self.current_task_context = {
            "timestamp": time.time(),
            "data": task_data,
            "node_id": getattr(self, "node_id", "unknown"),
        }
        return self.current_task_context

    async def query(self, prompt: str) -> Dict[str, str]:
        raise NotImplementedError("Adapters must implement query method")
