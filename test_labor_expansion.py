import asyncio
import os
import sys
from loguru import logger

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter
from agents.grok_adapter import GrokAdapter

async def test_autonomous_expansion():
    print("--- DEBUG: STARTING TEST ---", flush=True)
    logger.info("--- DAILM LABOR EXPANSION TEST INITIATED ---")
    
    engine = BrowserEngine()
    await engine.start(headless=True)
    
    try:
        matrix = ModelMatrix(engine)
        # Register standard nodes
        matrix.register_adapter("gemini", GeminiWebAdapter(engine))
        matrix.register_adapter("grok", GrokAdapter(engine))
        
        # 1. Simulate Market Stress
        logger.info("Simulating Market Stress: Artificially spiking mu for standard nodes...")
        matrix.bidding_engine.labor_profiles["gemini"]["mu"] = 800.0
        matrix.bidding_engine.labor_profiles["grok"]["mu"] = 800.0
        
        stress = matrix.bidding_engine.analyze_market_stress()
        logger.info(f"Calculated Market Stress: {stress:.2f}")
        
        # 2. Trigger task that should force expansion
        logger.info("Dispatching task. Expecting autonomous Friendli spawning...")
        prompt = "Hello, are you online? This is a system stress test."
        
        # This should trigger spawn_weg_labor("friendli") inside route_task
        handshake = await matrix.route_task("analysis", prompt)
        
        if handshake and handshake.get("source_model") == "friendli":
            logger.success("SUCCESS: Task routed to autonomously spawned Friendli node.")
        else:
            logger.error(f"FAILURE: Task routed to {handshake.get('source_model') if handshake else 'None'} instead of friendli.")
            
        # 3. Check Manifest Synchronization
        logger.info("Verifying adapter registry expansion...")
        if "friendli" in matrix.adapters:
            logger.success("SUCCESS: Friendli adapter effectively registered in ModelMatrix.")
        else:
            logger.error("FAILURE: Friendli adapter not found in registry.")

    except Exception as e:
        logger.error(f"Test Aborted with error: {e}")
    finally:
        await engine.stop()
        logger.info("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_autonomous_expansion())
