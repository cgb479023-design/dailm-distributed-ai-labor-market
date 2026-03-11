import asyncio
import os
import sys
import uuid
from loguru import logger
from typing import Any

# Add current dir to path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.base_adapter import BaseAdapter

class MockAdapter(BaseAdapter):
    def __init__(self, node_id, response_text):
        self.node_id = node_id
        self.response_text = response_text
        
    async def query(self, prompt: str) -> dict:
        logger.info(f"[MOCK]: {self.node_id} processing pulse...")
        await asyncio.sleep(0.1)
        return {"text": self.response_text}

async def verify_v2_internal_chain():
    logger.info("🧪 [DAILM v2.0]: INITIATING INTERNAL NEURAL CHAIN VERIFICATION...")
    
    # We don't need a real browser for this logic test
    # But ModelMatrix expects an engine instance
    class DummyEngine:
        pass
    
    engine = DummyEngine()
    matrix = ModelMatrix(engine)
    
    # 1. Register Mock Adapters
    # Claude will be the generator, Gemini the auditor (or vice versa)
    claude_mock = MockAdapter("claude", "print('Hello Silicon World')")
    gemini_mock = MockAdapter("gemini", '{"stable": true, "score": 0.99, "analysis": "Prime logic is sound."}')
    
    matrix.register_adapter("claude", claude_mock)
    matrix.register_adapter("gemini", gemini_mock)
    
    # 2. Execute Task: Synthesis
    prompt = "Generate a hello world script."
    logger.info(f"Targeting Code Synthesis: {prompt}")
    
    try:
        # This triggers the full chain:
        # Auction -> Claude Query -> Verifier (Gemini Audit) -> Sandbox -> Asset -> Archive
        handshake = await matrix.route_task("code", prompt)
        
        if handshake and handshake.get("asset_id") != "N/A":
            logger.success("✅ [VERIFY]: Internal Neural Chain CLOSED.")
            logger.info(f"Step ID: {handshake.get('step_id')}")
            logger.info(f"Asset ID: {handshake.get('asset_id')}")
            logger.info(f"Thought: {handshake.get('thought')}")
            
            # 3. Check Archive Manifest
            manifest_path = matrix.archive.export_verification_bundle()
            logger.success(f"✅ [VERIFY]: Archive Sealed at {manifest_path}")
            
            # 4. Check Vault Registry
            is_registered = handshake.get("asset_id") in matrix.asset_manager.registry
            logger.success(f"✅ [VERIFY]: Asset Registered in Registry: {is_registered}")
            
        else:
            logger.error("❌ [VERIFY]: Neural Chain BROKEN.")
            
    except Exception as e:
        logger.error(f"🔥 [VERIFY]: Simulation Crash: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_v2_internal_chain())
