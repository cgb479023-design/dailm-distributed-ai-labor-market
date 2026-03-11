import asyncio
from loguru import logger
from agents.base_adapter import BaseAdapter

class GeminiWebAdapter(BaseAdapter):
    def __init__(self, engine, status_manager=None):
        super().__init__(engine, status_manager)
        self.node_id = "gemini"
        self.max_retries = 5

    async def query(self, prompt: str) -> dict:
        from agents.base_adapter import SOVEREIGN_DIRECTIVE
        
        # Prepend identity if not already there (to avoid multiple nested headers)
        if "Antigravity Alpha Awakened" not in prompt:
            prompt = f"{SOVEREIGN_DIRECTIVE}\n[USER_PROMPT]: {prompt}"
            
        logger.info(f"Routing to Gemini: {prompt[:40]}...")
        
        # Sense: Get the page
        page = await self.engine.get_page("gemini.google.com")
        
        async def _navigate_and_type():
            if "gemini.google.com" not in page.url:
                await self.log("Navigating to gemini.google.com...")
                await page.goto("https://gemini.google.com/app", wait_until="networkidle")
            
            # Act: Wait for the rich text editor
            # The selector might change, so we use multiple possible attributes
            selectors = ["rich-textarea", "div[contenteditable='true']", ".input-area"]
            found_selector = None
            
            await self.log("Scanning for input terminal interface...")
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, state="visible", timeout=5000)
                    found_selector = selector
                    break
                except:
                    continue
            
            if not found_selector:
                # Last ditch effort with a generic role
                await page.wait_for_selector("[role='textbox']", state="visible", timeout=5000)
                found_selector = "[role='textbox']"

            # Type and send
            await self.log(f"Pulsing neural data into [{found_selector}]...")
            await page.click(found_selector)
            # Use fill for faster input if it's a contenteditable or textarea
            try:
                await page.fill(found_selector, prompt)
            except:
                await page.keyboard.type(prompt)
            
            await self.engine.human_delay(1, 2)
            await self.log("Executing query (Enter)...")
            await page.keyboard.press("Enter")
            
        # Execute navigation and typing via SSH Loop
        await self.execute_with_ssh_loop("Gemini-Input", _navigate_and_type)
        
        async def _extract_response():
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "PROCESSING", 88)
                
            # Wait for the response container. The last one is the latest response.
            response_selector = "message-content"
            await self.log(f"Awaiting semantic response via [{response_selector}]...")
            await page.wait_for_selector(response_selector, state="visible", timeout=30000)
            
            # Wait a bit for the streaming to finish (heuristics: network idle or delay)
            await self.log("Stream synthesis active. Delaying for buffer fill...")
            await self.engine.human_delay(3, 5)
            
            # Extract the text from the last message
            await self.log("Extracting terminal message entity...")
            elements = await page.query_selector_all(response_selector)
            if not elements:
                raise Exception("No response elements found after waiting.")
            
            last_response = elements[-1]
            text = await last_response.inner_text()
            return {"text": text.strip()}

        try:
            # Execute extraction via SSH Loop
            result = await self.execute_with_ssh_loop("Gemini-Output", _extract_response)
            
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "READY", 12)
                
            return result
        except Exception as e:
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "ERROR", 0)
            logger.error(f"Gemini Node Failure: {e}")
            raise
