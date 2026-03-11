import subprocess
import sys
import os
import uuid
import tempfile
import shutil
from loguru import logger

class NeuralSandbox:
    """
    Immutable Execution Environment for synthesized code.
    Prevents side effects and provides 100% clean-state verification.
    """
    def __init__(self, work_dir=None):
        self.work_dir = work_dir or os.path.join(tempfile.gettempdir(), f"dailm_sandbox_{uuid.uuid4().hex[:8]}")
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        logger.info(f"[SANDBOX]: Neural Containment Field established at {self.work_dir}")

    async def run_code(self, code: str, timeout: int = 30):
        """Executes code in a separate process and returns output/errors."""
        script_path = os.path.join(self.work_dir, "payload.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            # We use the current venv's python but in a jailed working directory
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=self.work_dir,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error("[SANDBOX]: Neural timeout. Termination sequence initiated.")
            return {"success": False, "error": "Execution Timed Out"}
        except Exception as e:
            logger.error(f"[SANDBOX]: Physical breach detected: {e}")
            return {"success": False, "error": str(e)}

    def cleanup(self):
        """Dissolve the containment field."""
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
            logger.info("[SANDBOX]: Neural Containment Field dissolved.")

if __name__ == "__main__":
    # Internal validation pulse
    import asyncio
    async def pulse():
        sb = NeuralSandbox()
        res = await sb.run_code("print('Hello from the Silicon Void')")
        print(res)
        sb.cleanup()
    asyncio.run(pulse())
