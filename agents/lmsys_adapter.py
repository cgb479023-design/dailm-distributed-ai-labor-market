import asyncio
from loguru import logger
from agents.base_adapter import BaseAdapter
from agents.vision_helper import VisionHelper
from utils.terminal_visuals import CyberTerminal

class LmsysAdapter(BaseAdapter):
    def __init__(self, engine, status_manager=None):
        super().__init__(engine, status_manager)
        self.node_id = "claude"
        self.input_selector = "textarea[placeholder*='Ask anything']"

    async def _ensure_arena_ready(self, page):
        """确保 Arena 处于可用状态，处理意外崩溃"""
        content = await page.content()
        if "Something unexpected happened" in content:
            await self.log("Detected Arena crash, performing tactical refresh...", level="warn")
            await page.reload()
            await page.wait_for_timeout(5000)
            return True
        return False

    async def query(self, prompt: str) -> dict:
        # 1. 发送指令前的视觉自检
        print(f"\n[NEURAL_LINK]: Sending request to CLAUDE_SCRIPTOR via Arena_AI...")
        # 2. 模拟“数据封装”进度
        CyberTerminal.decrypt_bar("ENCRYPTING_PROMPT", duration=0.8)

        logger.info(f"Routing to Arena.ai (Claude simulator): {prompt[:20]}...")

        if self.status_manager:
            load_estimate = min(95, 20 + len(prompt) // 50)
            await self.status_manager.update_node(self.node_id, "BUSY", load_estimate)

        page = await self.engine.get_page("arena.ai")
        # Keep gemini page handle for vision fallback if needed
        brain_page = await self.engine.get_page("gemini.google.com")

        async def _navigate_and_type():
            await page.reload() # Force reload to ensure a clean state for each attempt
            if "arena.ai" not in page.url:
                await self.log("Navigating to arena.ai/text/direct...")
                await page.goto("https://arena.ai/text/direct", wait_until="networkidle")

            # 战术自愈：检查页面是否崩溃
            await self._ensure_arena_ready(page)

            # Check for "Agree" button on terms of use modal
            try:
                await self.log("Scanning for Arena.ai Terms of Use protocol...")
                agree_btn = await page.wait_for_selector("button:has-text('Agree')", timeout=5000)
                if agree_btn:
                    await self.log("Bypassing Arena.ai TOU modal...")
                    await agree_btn.click()
                    await self.engine.human_delay(1, 2)
            except:
                pass

            # 模型精确打击：锁定 Claude Opus 4.6 Thinking (Commander Verified)
            try:
                await self.log("Calibrating model selector: Targeting [claude-opus-4-6-thinking]...")

                # 检查是否已锁定
                is_selected = await page.evaluate(f"""() => {{
                    const btn = Array.from(document.querySelectorAll("button")).find(b =>
                        b.innerText.toLowerCase().includes("claude-opus-4-6-thinking")
                    );
                    return !!btn;
                }}""")

                if not is_selected:
                    # 第一步：点击入口 (Max 或 aria-haspopup="dialog")
                    target_acquired = await page.evaluate("""() => {
                        const btn = Array.from(document.querySelectorAll("button")).find(b =>
                            b.innerText.trim() === "Max" || (b.getAttribute("aria-haspopup") === "dialog")
                        );
                        if (btn) { btn.click(); return true; }
                        return false;
                    }""")

                    if target_acquired:
                        await self.log("Model menu opened. Awaiting neural synchronization...")
                        await asyncio.sleep(2) # 确保列表弹出

                        target_model_text = "claude-opus-4-6-thinking"
                        # 第二步：点击目标模型
                        selection_successful = await page.evaluate(f"""() => {{
                            const el = Array.from(document.querySelectorAll("*")).find(e =>
                                e.innerText === "{target_model_text}" && e.offsetWidth > 0
                            );
                            if (el) {{ el.click(); return true; }}
                            return false;
                        }}""")

                        if selection_successful:
                            await self.log(f"Neural link optimized: {target_model_text} activated.")
                        else:
                            await self.log(f"Target {target_model_text} not found in the pulse stream.", level="warn")
                            await page.keyboard.press("Escape")
                    else:
                        await self.log("Primary landing node (Max button) unavailable.", level="warn")
                else:
                    await self.log(f"Neural link already synchronized to {self.node_id}.")
            except Exception as e:
                await self.log(f"Model selection bypassed: {e}", level="warn")

            try:
                await self.log(f"Targeting Arena input node via {self.input_selector}...")
                await page.wait_for_selector(self.input_selector, state="visible", timeout=15000)
                await self.log("Pulsing prompt into Arena simulator (Human-Mode)...")
                await page.click(self.input_selector)
                await page.keyboard.type(prompt, delay=30)
            except Exception as e:
                await self.log("CSS Selector failed. Initializing Vision Recon Protocol...", level="warn")
                success = await VisionHelper.vision_driven_click(page, brain_page, "Ask anything... input box")
                if not success:
                    raise Exception("VisionHelper failed to locate and click the target.")
                await self.log("Vision lock acquired. Injecting physical keystrokes...")
                await page.keyboard.type(prompt)

            await self.engine.human_delay(1, 2)

            send_btn_selector = "button.text-interactive-normal, button[aria-label*='Send']"
            try:
                await self.log("Detecting Arena send trigger...")
                send_btn = await page.query_selector(send_btn_selector)
                if send_btn:
                    await send_btn.click()
                else:
                    await page.keyboard.press("Enter")
            except Exception as e:
                await self.log("Button click failed. Dispatching 'Enter' override...", level="warn")
                await page.keyboard.press("Enter")

        await self.execute_with_ssh_loop("Arena-Input", _navigate_and_type)

        async def _extract_response():
            response_selector = ".prose, .markdown-body, [class*='message-content'], .text-message"
            await self.log(f"Awaiting Arena response via [{response_selector}]...")
            await page.wait_for_selector(response_selector, state="visible", timeout=45000)

            last_length = 0
            await self.log("Neural stream detected. Monitoring pulse...")
            await asyncio.sleep(2)

            stale_count = 0
            while stale_count < 10:
                content = await page.evaluate(f'() => document.querySelector("{response_selector}")?.innerText || ""')
                if len(content) > last_length:
                    import random
                    jitter_load = random.randint(85, 98)
                    if self.status_manager:
                        await self.status_manager.update_node(self.node_id, "PROCESSING", jitter_load)
                    last_length = len(content)
                    stale_count = 0
                else:
                    stale_count += 1
                await asyncio.sleep(0.5)

            await self.log("Extraction lock confirmed. Finalizing data fragment...")
            elements = await page.query_selector_all(response_selector)
            if not elements:
                raise Exception("No response elements found.")

            last_response = elements[-1]
            text = await last_response.inner_text()
            CyberTerminal.decrypt_bar("DECRYPTING_RESPONSE", duration=1.5)
            CyberTerminal.matrix_stream(f">> RAW_DATA_STABILIZED: {len(text)} bytes received.")
            return {"text": f"[Claude via Arena.ai]\n{text.strip()}"}

        try:
            result = await self.execute_with_ssh_loop("Arena-Output", _extract_response)
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "READY", 5)
            return result
        except Exception as e:
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "ERROR", 0)
            logger.error(f"Arena.ai Node Failure: {e}")
            raise
