import os
import sys
# Add root to path
sys.path.append(os.getcwd())

from agents.matrix import ModelMatrix
from core.engine import BrowserEngine
from core.sandbox import NeuralSandbox
from agents.prebid_agent import PreBidAgent

async def test_pdf():
    engine = BrowserEngine()
    # We don't need to start it if we only test extraction which is sync/pypdf based
    matrix = ModelMatrix(engine)
    sandbox = NeuralSandbox()
    agent = PreBidAgent(matrix, sandbox)
    
    rfp = r"E:\dailm---distributed-ai-labor-market\海南大学平安校园升级改造项目招标文件.pdf"
    text = agent.extract_text(rfp)
    print(f"--- EXTRACTED TEXT (First 500 chars) ---")
    print(text[:500])
    print(f"--- TOTAL LENGTH: {len(text)} ---")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pdf())
