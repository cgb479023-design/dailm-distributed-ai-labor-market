import asyncio
import os
import sys
from loguru import logger

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine

async def verify_friendli_playground():
    # 使用用户提供的 Playground 链接
    url = "https://friendli.ai/suite/C7BLx88kTHS2/d8GO9nV3Vnxw/serverless-endpoints/zai-org/GLM-5/overview"
    
    logger.info("--- FRIENDLI MANUAL VERIFICATION START ---")
    engine = BrowserEngine()
    
    # 建议 headless=False 以便物理观察
    await engine.start(headless=False)
    
    try:
        # 1. 访问 Playground
        page = await engine.get_page("friendli-manual")
        logger.info(f"Navigating to Playground: {url}")
        # 使用 domcontentloaded 并增加超时时间，因为 Playground 这种复杂 SPA 可能无法快速达到 networkidle
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 额外给 5s 让脚本加载
        logger.info("Soft-waiting for dynamic components to stabilize...")
        await asyncio.sleep(5)
        
        # 2. 等待输入框加载 (根据截图 Placeholder 定位)
        input_selector = '[placeholder*="prompt"]' 
        logger.info(f"Awaiting input node: {input_selector}...")
        await page.wait_for_selector(input_selector, state="visible", timeout=20000)
        
        # 3. 注入测试指令
        test_prompt = "Hello GLM-5! This is Antigravity verifying our neural link. Please respond with 'LINK_ACTIVE'."
        logger.info("Injecting test prompt...")
        await page.click(input_selector)
        await page.keyboard.type(test_prompt)
        
        # 4. 点击发送 (定位右侧箭头按钮)
        send_button_selector = 'button:has(svg)' # 根据截图的箭头图标按钮
        logger.info("Pulsing 'Send' command...")
        await page.click(send_button_selector)
        
        # 5. 等待响应
        logger.info("Waiting for neural response pulse...")
        # 假设响应出现在含有文本的容器中，这里等待 10s 观察
        await asyncio.sleep(10)
        
        # 截屏留存以供手工验证
        screenshot_path = "friendli_verification.png"
        await page.screenshot(path=screenshot_path)
        logger.success(f"Verification pulse complete. Screenshot saved at: {screenshot_path}")
        
    except Exception as e:
        logger.error(f"Verification Crash: {e}")
    finally:
        logger.info("Verification window will close in 5s...")
        await asyncio.sleep(5)
        await engine.stop()
        logger.info("--- VERIFICATION SESSION CLOSED ---")

if __name__ == "__main__":
    asyncio.run(verify_friendli_playground())
