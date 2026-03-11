import asyncio
import sys
import os
from loguru import logger
from core.engine import BrowserEngine
from agents.gemini_adapter import GeminiWebAdapter
from agents.lmsys_adapter import LmsysAdapter
from agents.grok_adapter import GrokAdapter
from agents.matrix import ModelMatrix

# Ensure the project root is in sys.path
sys.path.append(os.getcwd())

class SystemVerifier:
    def __init__(self):
        self.engine = BrowserEngine()
        self.matrix = None
        self.results = {}

    async def setup(self):
        logger.info("Initializing Verification Environment...")
        await self.engine.start(headless=True)
        self.matrix = ModelMatrix(self.engine)
        
        # Register adapters
        self.matrix.register_adapter("gemini", GeminiWebAdapter(self.engine))
        self.matrix.register_adapter("claude", LmsysAdapter(self.engine))
        self.matrix.register_adapter("grok", GrokAdapter(self.engine))
        logger.info("Environment Setup Complete.")

    async def verify_node(self, node_id, prompt="Hello, who are you? Please answer in one short sentence."):
        logger.info(f"--- Verifying Node: {node_id} ---")
        try:
            adapter = self.matrix.adapters.get(node_id)
            if not adapter:
                raise ValueError(f"Adapter not found for {node_id}")
            
            result = await adapter.query(prompt)
            logger.success(f"Node {node_id} Response: {result['text'][:100]}...")
            self.results[node_id] = {"status": "SUCCESS", "message": result['text'][:200]}
            return True
        except Exception as e:
            logger.error(f"Node {node_id} Failed: {e}")
            self.results[node_id] = {"status": "FAILED", "error": str(e)}
            return False

    async def verify_matrix(self):
        logger.info("--- Verifying Matrix Routing ---")
        try:
            # Task: simple greeting to test routing
            result = await self.matrix.route_task("text_gen", "What is 2+2?")
            logger.success(f"Matrix Routing Successful. Source: {result['source_model']}")
            self.results["matrix"] = {"status": "SUCCESS", "source": result['source_model']}
            return True
        except Exception as e:
            logger.error(f"Matrix Routing Failed: {e}")
            self.results["matrix"] = {"status": "FAILED", "error": str(e)}
            return False

    async def run_full_validation(self):
        await self.setup()
        
        # Sequential verification
        await self.verify_node("gemini")
        await self.verify_node("claude")
        await self.verify_node("grok")
        await self.verify_matrix()
        
        await self.engine.stop()
        self.generate_report()

    def generate_report(self):
        report_path = os.path.join(os.getcwd(), "validation_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# DAILM System Validation Report\n\n")
            f.write("| Component | Status | Details |\n")
            f.write("| --- | --- | --- |\n")
            for comp, data in self.results.items():
                status = "✅ PASS" if data["status"] == "SUCCESS" else "❌ FAIL"
                details = data.get("message") or data.get("error") or data.get("source") or ""
                f.write(f"| {comp} | {status} | {details} |\n")
        
        logger.info(f"Report generated at {report_path}")

if __name__ == "__main__":
    verifier = SystemVerifier()
    asyncio.run(verifier.run_full_validation())
