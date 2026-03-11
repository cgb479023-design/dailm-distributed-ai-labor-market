import asyncio
from loguru import logger
from agents.base_adapter import BaseAdapter
from utils.terminal_visuals import CyberTerminal

class FriendliAdapter(BaseAdapter):
    """
    Friendli AI Adapter: Meta-Agent for reaping free labor from friendli.ai.
    """
    def __init__(self, engine, status_manager=None):
        super().__init__(engine, status_manager)
        self.node_id = "friendli"
        self.playground_url = "https://friendli.ai/suite/C7BLx88kTHS2/d8GO9nV3Vnxw/serverless-endpoints/zai-org/GLM-5/overview"
        self.input_selector = '[placeholder*="prompt"]'
        self.send_button_selector = 'button:has(svg)'

    async def query(self, prompt: str) -> dict:
        await self.log(f"Routing to Friendli GLM-5: {prompt[:20]}...")
        
        if self.status_manager:
            await self.status_manager.update_node(self.node_id, "BUSY", 70)
            
        page = await self.engine.get_page("friendli.ai")
        
        async def _navigate_and_type():
            if self.playground_url not in page.url:
                await self.log(f"Navigating to Friendli Playground...")
                await page.goto(self.playground_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5) # Allow SPA to settle
            
            # 战术自愈：处理可能的 Overlay 或 登录提示 (虽然我们目前依赖持久化 Session)
            try:
                dismiss_btn = await page.wait_for_selector("button:has-text('Dismiss'), button:has-text('Close')", timeout=2000)
                if dismiss_btn:
                    await dismiss_btn.click()
            except:
                pass

            await self.log(f"Injecting prompt into GLM-5 node...")
            await page.wait_for_selector(self.input_selector, state="visible", timeout=15000)
            await page.click(self.input_selector)
            await page.keyboard.type(prompt, delay=10)
            
            await self.log("Pulsing 'Send' signal...")
            await page.click(self.send_button_selector)
            
        await self.execute_with_ssh_loop("Friendli-Input", _navigate_and_type)
        
        async def _extract_response():
            # 响应通常出现在特定的消息容器中。根据截图观察，类名可能包含 'bubble' 或 'content'
            # 我们先尝试通用的类名定位
            response_selector = "[class*='Chat_chat_content'], .chatbot-message-content, [class*='message_content']"
            await self.log("Awaiting neural pulse extraction...")
            await page.wait_for_selector(response_selector, state="visible", timeout=45000)
            
            # 等待流式输出完成
            await asyncio.sleep(5)
            
            elements = await page.query_selector_all(response_selector)
            if not elements:
                # 回退：尝试寻找所有包含文本的最新 div
                elements = await page.query_selector_all("div[class*='content']")
                
            if not elements:
                raise Exception("Friendli response capture failed.")
                
            text = await elements[-1].inner_text()
            CyberTerminal.matrix_stream(f">> FRIENDLI_SYNC: {len(text)} bytes received.")
            return {"text": f"[Friendli-GLM-5]\n{text.strip()}"}

        try:
            result = await self.execute_with_ssh_loop("Friendli-Output", _extract_response)
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "READY", 5)
            return result
        except Exception as e:
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "ERROR", 0)
            logger.error(f"Friendli.ai Node Failure: {e}")
            raise
