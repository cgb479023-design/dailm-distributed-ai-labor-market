import asyncio
import os
import sys
from loguru import logger

# Add current dir to path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.lmsys_adapter import LmsysAdapter
from agents.gemini_adapter import GeminiWebAdapter

async def final_evolution_strike():
    logger.info("🚀 [DAILM v2.0]: INITIATING FINAL EVOLUTION STRIKE...")
    
    engine = BrowserEngine()
    await engine.start(headless=True)
    
    matrix = ModelMatrix(engine)
    
    # Register Adapters (Claude and Gemini are both required for Verifier's auditor logic)
    lmsys = LmsysAdapter(engine)
    lmsys.node_id = "claude"
    matrix.register_adapter("claude", lmsys)
    
    gemini = GeminiWebAdapter(engine)
    gemini.node_id = "gemini"
    matrix.register_adapter("gemini", gemini)
    
    prompt = "Synthesize a robust Python function for calculating prime numbers up to N. Ensure it is optimized."
    
    try:
        logger.info(f"Issuing Evolutionary Mission: {prompt}")
        # This will trigger: Auction -> Query -> Adversarial Audit (Claude vs Gemini) -> Sandbox -> Asset Minting -> Archive
        handshake = await matrix.route_task("code", prompt)
        
        if handshake and handshake.get("source_model"):
            logger.success(f"✅ [STRIKE]: Mission SECURED via {handshake.get('source_model')}.")
            logger.info(f"Asset ID: {handshake.get('asset_id')}")
            logger.info(f"Neural Thought: {handshake.get('thought')}")
            
            # Export Archive for Commander Review
            manifest_path = matrix.archive.export_verification_bundle()
            logger.success(f"✅ [STRIKE]: Phase 4 Neural Bundle Sealed: {manifest_path}")
            
            # Proof of Asset Integrity
            content = handshake.get("data", "")
            is_valid = matrix.asset_manager.verify_integrity(handshake.get("asset_id"), content)
            logger.info(f"Asset Integrity Verified: {is_valid}")
            
        else:
            logger.error("❌ [STRIKE]: Mission Failed to yield a validated result.")
            
    except Exception as e:
        logger.error(f"🔥 [STRIKE]: Critical System Breach: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.stop()
        logger.info("🏁 [DAILM v2.0]: FINAL STRIKE SEQUENCE COMPLETE.")

if __name__ == "__main__":
    asyncio.run(final_evolution_strike())
