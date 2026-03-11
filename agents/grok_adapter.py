import asyncio
from loguru import logger
from agents.base_adapter import BaseAdapter

class GrokAdapter(BaseAdapter):
    def __init__(self, engine, status_manager=None):
        super().__init__(engine, status_manager)
        self.node_id = "grok"

    async def query(self, prompt: str) -> dict:
        logger.info(f"Routing to Search/Grok: {prompt[:20]}...")
        
        if self.status_manager:
            load_estimate = min(95, 20 + len(prompt) // 50)
            await self.status_manager.update_node(self.node_id, "BUSY", load_estimate)
        
        # For DAILM, if Grok isn't available, we fallback to a DuckDuckGo search to simulate real-time search logic
        page = await self.engine.get_page("duckduckgo.com")
        
        async def _navigate_and_type():
            await self.log("Accessing search terminal (DuckDuckGo)...")
            await page.goto("https://html.duckduckgo.com/html/", wait_until="networkidle")
            
            input_selector = "input[name='q']"
            await self.log(f"Locating search register via {input_selector}...")
            await page.wait_for_selector(input_selector, state="visible", timeout=10000)
            
            # Use LLM prompt as search query (simplified)
            search_term = prompt[:50] 
            await self.log(f"Injecting search query: {search_term}...")
            await page.click(input_selector)
            await page.keyboard.type(search_term)
            await self.log("Executing search (Enter)...")
            await page.keyboard.press("Enter")
            
        await self.execute_with_ssh_loop("Search-Input", _navigate_and_type)
        
        async def _extract_response():
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "PROCESSING", 92)
                
            result_selector = ".result__snippet, .result-snippet, .result__body"
            await self.log(f"Awaiting search results via [{result_selector}]...")
            await page.wait_for_selector(result_selector, state="visible", timeout=15000)
            
            await self.log("Harvesting data snippets...")
            elements = await page.query_selector_all(result_selector)
            snippets = []
            for el in elements[:3]: # Take top 3
                snippets.append(await el.inner_text())
                
            combined = "\n".join(snippets)
            return {"text": f"[Search Results]\n{combined}"}

        try:
            result = await self.execute_with_ssh_loop("Search-Output", _extract_response)
            
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "READY", 5)
                
            return result
        except Exception as e:
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "ERROR", 0)
            logger.error(f"Grok Node Failure: {e}")
            raise
