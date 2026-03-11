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
    
    # Check for Arena crash
    content = await page.content()
    if "Something unexpected happened" in content:
        print("[ARENA]: Detected crash, performing tactical refresh...")
        await page.reload()
        await asyncio.sleep(5)
    
    # Check for Agree button
    try:
        agree_btn = await page.wait_for_selector("button:has-text('Agree')", timeout=5000)
        if agree_btn:
            await agree_btn.click()
            await asyncio.sleep(2)
    except:
        pass
        
    textarea_selector = "textarea[placeholder*='Ask anything']"
    try:
        await page.wait_for_selector(textarea_selector, timeout=10000)
        await page.click(textarea_selector)
        await page.keyboard.type("Hello", delay=30)
        await page.keyboard.press("Enter")
        print("Arena input successful.")
    except Exception as e:
        print(f"Arena input failed: {e}")
    
    await asyncio.sleep(10) # Wait for response
    arena_html = await page.content()
    with open("arena_diag.html", "w", encoding="utf-8") as f:
        f.write(arena_html)
    await page.screenshot(path="arena_diag.png")
    
    # Extract selectors for user review
    selectors = await page.evaluate("""() => {
        const results = [];
        document.querySelectorAll('textarea, button, .prose, [class*="message"]').forEach(el => {
            results.push({
                tag: el.tagName,
                classes: el.className,
                placeholder: el.placeholder || '',
                text: el.innerText.substring(0, 50)
            });
        });
        return results;
    }""")
    import json
    with open("arena_selectors.json", "w", encoding="utf-8") as f:
        json.dump(selectors, f, indent=2)
    print("Arena diagnostic data saved.")

    await engine.stop()

if __name__ == "__main__":
    asyncio.run(diagnose())
