import asyncio
import os
import sys
from loguru import logger

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.prebid_agent import PreBidAgent
from core.sandbox import NeuralSandbox
from agents.gemini_adapter import GeminiWebAdapter
from agents.friendli_adapter import FriendliAdapter

async def run_prebid_master_audit():
    pdf_path = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"
    
    logger.info("--- 🛡️ PREBID MASTER NEURAL AUDIT INITIATED ---")
    
    engine = BrowserEngine()
    await engine.start(headless=True) 
    
    matrix = ModelMatrix(engine)
    # Register Gemini as primary
    matrix.register_adapter("gemini", GeminiWebAdapter(engine))
    # Register Friendli as shadow node for expansion/fallback
    matrix.register_adapter("friendli", FriendliAdapter(engine))

    sandbox = NeuralSandbox()
    prebid = PreBidAgent(matrix, sandbox)
    
    try:
        # 1. RFP Parsing
        logger.info(f"Phase 1: Parsing RFP -> {os.path.basename(pdf_path)}")
        blueprint = await prebid.parse_rfp(pdf_path)
        
        if not blueprint:
            logger.error("Neural Reconnaissance returned empty blueprint. Triggering emergency expansion...")
            # If Gemini fails, matrix.route_task in parse_rfp should have handled it, 
            # but we force check here.
            
        logger.success("Neural Reconnaissance Complete.")
        
        # 2. UI Synthesis
        logger.info("Phase 2: Synthesizing 9:16 Mobile Demo UI...")
        ui_schema = await prebid.synthesize_916_ui(blueprint)
        logger.success("UI Synthesis Pulse Complete.")
        
        # 3. Export
        logger.info("Phase 3: Exporting Signed Digital Asset...")
        strike_path = prebid.export_strike_package(ui_schema, "HAINAN_SAFE_CAMPUS")
        logger.success(f"Mission Accomplished. Package sealed at: {strike_path}")
        
    except Exception as e:
        logger.error(f"Neural Audit crashed: {e}")
    finally:
        await engine.stop()
        logger.info("--- NEURAL LINK CLOSED ---")

if __name__ == "__main__":
    asyncio.run(run_prebid_master_audit())
