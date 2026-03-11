import asyncio
from core.engine import BrowserEngine

async def research_model_selector():
    engine = BrowserEngine()
    await engine.start(headless=False)
    page = await engine.get_page("arena.ai")
    await page.goto("https://arena.ai/text/direct", wait_until="networkidle")
    
    # Wait for Agree
    try:
        agree_btn = await page.wait_for_selector("button:has-text('Agree')", timeout=5000)
        if agree_btn: await agree_btn.click()
    except: pass

    print("Opening model selector...")
    try:
        # The selector from previous code
        model_selector = await page.wait_for_selector("button:has-text('Max'), button:has-text('Direct')", timeout=10000)
        await model_selector.click()
        await asyncio.sleep(2)
        
        # Capture all options in the dropdown
        options = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[role="option"], [role="menuitem"], div, span'))
                .filter(el => el.innerText && el.innerText.length < 50)
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText.trim(),
                    classes: el.className,
                    role: el.getAttribute('role') || ''
                }));
        }""")
        
        import json
        with open("arena_models.json", "w", encoding="utf-8") as f:
            json.dump(options, f, indent=2)
        print("Model options saved to arena_models.json")
    except Exception as e:
        print(f"Failed to open model selector: {e}")
        await page.screenshot(path="arena_selector_err.png")

    await engine.stop()

if __name__ == "__main__":
    asyncio.run(research_model_selector())
