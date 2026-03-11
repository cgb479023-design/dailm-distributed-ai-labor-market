import asyncio
import os
import sys
from loguru import logger

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.engine import BrowserEngine

async def scout_selectors():
    url = "https://friendli.ai/suite/C7BLx88kTHS2/d8GO9nV3Vnxw/serverless-endpoints/zai-org/GLM-5/overview"
    
    logger.info("--- FRIENDLI SELECTOR SCOUT INITIATED ---")
    engine = BrowserEngine()
    await engine.start(headless=False)
    
    try:
        page = await engine.get_page("scout")
        logger.info(f"Navigating to: {url}")
        # Allow more time for initial load
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        logger.info("Waiting 10s for dynamic UI to inflate...")
        await asyncio.sleep(10)
        
        # Scout for inputs and buttons
        results = await page.evaluate("""() => {
            const scout = (selector) => {
                return Array.from(document.querySelectorAll(selector)).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    placeholder: el.placeholder || '',
                    text: el.innerText || '',
                    ariaLabel: el.ariaLabel || ''
                }));
            };
            return {
                textareas: scout('textarea'),
                buttons: scout('button'),
                inputs: scout('input')
            };
        }""")
        
        print("\n=== 🎯 POTENTIAL INPUT SELECTORS ===")
        for ta in results['textareas']:
            print(f"[TEXTAREA] ID: {ta['id']} | Class: {ta['className']} | Placeholder: '{ta['placeholder']}'")
        for inp in results['inputs']:
            print(f"[INPUT] ID: {inp['id']} | Class: {inp['className']} | Placeholder: '{inp['placeholder']}'")
            
        print("\n=== 🚀 POTENTIAL SEND BUTTONS ===")
        for btn in results['buttons']:
            print(f"[BUTTON] ID: {btn['id']} | Class: {btn['className']} | Text: '{btn['text'][:20]}' | Aria: '{btn['ariaLabel']}'")
            
        logger.success("Scouting cycle complete. Check the terminal output above.")
        
    except Exception as e:
        logger.error(f"Scout Crash: {e}")
    finally:
        logger.info("Closing in 10s...")
        await asyncio.sleep(10)
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(scout_selectors())
