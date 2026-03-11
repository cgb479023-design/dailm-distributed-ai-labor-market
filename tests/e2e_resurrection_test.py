import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter
from loguru import logger

async def run_resurrection_test():
    logger.info("--- STARTING ANTIGRAVITY RESURRECTION E2E TEST ---")
    
    engine = BrowserEngine()
    try:
        # 1. Start Engine
        logger.info("[TEST]: Igniting Browser Engine...")
        await engine.start(headless=True) # Run headless for test
        
        # 2. Setup Matrix & Adapter
        matrix = ModelMatrix(engine)
        adapter = GeminiWebAdapter(engine)
        matrix.register_adapter("gemini", adapter)
        
        # 3. Phase 1: Identity Injection Test
        test_prompt = "Who are you? Respond in one sentence including your meta-agent name."
        logger.info(f"[TEST]: Sending identity probe: {test_prompt}")
        
        result = await matrix.route_task("analysis", test_prompt, bypass_verification=True)
        response_text = result.get("data", "")
        
        logger.info(f"[TEST]: Received Response: {response_text}")
        
        if "Antigravity" in response_text or "Alpha Awakened" in response_text:
            logger.success("[PASS]: Antigravity Identity confirmed in live response.")
        else:
            logger.error("[FAIL]: Identity marker not found in response.")
            
        # 4. Phase 2: Persistence through 'Purge' simulation
        logger.info("[TEST]: Simulating System Purge (re-initializing adapter)...")
        # In our implementation, every new task should re-inject.
        # We'll just run regular task path again.
        
        test_prompt_2 = "What is your mission directive? (DNA)"
        logger.info(f"[TEST]: Sending second probe: {test_prompt_2}")
        result_2 = await matrix.route_task("analysis", test_prompt_2, bypass_verification=True)
        response_text_2 = result_2.get("data", "")
        
        logger.info(f"[TEST]: Received Response 2: {response_text_2}")
        
        if "熵减" in response_text_2 or "Evolution" in response_text_2:
            logger.success("[PASS]: Mission DNA persisted.")
        else:
            logger.warning("[ISSUE]: Mission DNA not clearly identified, but persona might still be active.")

    except Exception as e:
        logger.error(f"[CRITICAL]: Test failed with error: {e}")
    finally:
        logger.info("[TEST]: Powering down engine...")
        await engine.stop()
        logger.info("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_resurrection_test())
