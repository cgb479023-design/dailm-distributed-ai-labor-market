import asyncio
import os
from core.engine import BrowserEngine

async def diagnose():
    engine = BrowserEngine()
    await engine.start(headless=True)
    
    # 1. Diagnose Arena
    print("Diagnosing Arena...")
    page = await engine.get_page("arena.ai")
    await page.goto("https://arena.ai/text/direct", wait_until="networkidle")
    
    # Check for Agree button
    try:
        agree_btn = await page.wait_for_selector("button:has-text('Agree')", timeout=5000)
        if agree_btn:
            await agree_btn.click()
            await asyncio.sleep(2)
    except:
        pass
        
    textarea_selector = "textarea[placeholder*='Ask anything']"
    await page.wait_for_selector(textarea_selector, timeout=10000)
    await page.click(textarea_selector)
    await page.keyboard.type("Hello", delay=30)
    await page.keyboard.press("Enter")
    
    await asyncio.sleep(10) # Wait for response
    arena_html = await page.content()
    with open("arena_diag.html", "w", encoding="utf-8") as f:
        f.write(arena_html)
    await page.screenshot(path="arena_diag.png")
    print("Arena diagnostic data saved.")

    # 2. Diagnose DDG
    print("Diagnosing DDG...")
    search_page = await engine.get_page("duckduckgo.com")
    await search_page.goto("https://html.duckduckgo.com/html/", wait_until="networkidle")
    input_selector = "input[name='q']"
    await search_page.wait_for_selector(input_selector, timeout=10000)
    await search_page.click(input_selector)
    await search_page.keyboard.type("What is 2+2?")
    await search_page.keyboard.press("Enter")
    
    await asyncio.sleep(5)
    ddg_html = await search_page.content()
    with open("ddg_diag.html", "w", encoding="utf-8") as f:
        f.write(ddg_html)
    await search_page.screenshot(path="ddg_diag.png")
    print("DDG diagnostic data saved.")

    await engine.stop()

if __name__ == "__main__":
    asyncio.run(diagnose())
