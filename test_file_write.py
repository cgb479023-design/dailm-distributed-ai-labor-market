import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter

async def test_and_write():
    with open('EXPANSION_RESULT.txt', 'w') as f:
        f.write("INITIATED\n")
        try:
            engine = BrowserEngine()
            await engine.start(headless=True)
            matrix = ModelMatrix(engine)
            matrix.register_adapter("gemini", GeminiWebAdapter(engine))
            
            # Spike stress
            matrix.bidding_engine.labor_profiles["gemini"]["mu"] = 800.0
            
            f.write("STRESS_SPIKED\n")
            
            # This should spawn friendli
            await matrix.route_task("analysis", "test")
            
            if "friendli" in matrix.adapters:
                f.write("SUCCESS: FRIENDLI_SPAWNED\n")
            else:
                f.write("FAILURE: NO_EXPANSION\n")
                
            await engine.stop()
        except Exception as e:
            f.write(f"CRASH: {str(e)}\n")
        f.write("FINISHED\n")

if __name__ == "__main__":
    asyncio.run(test_and_write())
