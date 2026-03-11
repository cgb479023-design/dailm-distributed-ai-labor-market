import asyncio
import json
from core.engine import BrowserEngine

async def list_models():
    engine = BrowserEngine()
    await engine.start(headless=False)
    page = await engine.get_page("arena.ai")
    await page.goto("https://arena.ai/text/direct", wait_until="networkidle")
    
    # Bypass TOU
    try:
        agree_btn = await page.wait_for_selector("button:has-text('Agree')", timeout=5000)
        if agree_btn:
            await agree_btn.click()
            await asyncio.sleep(1)
    except:
        pass
        
    print("Opening model selector...")
    # Find all comboboxes
    comboboxes = await page.query_selector_all("button[role='combobox']")
    if len(comboboxes) >= 2:
        model_selector = comboboxes[1]
        await model_selector.click()
        await asyncio.sleep(2)
        
        # Capture all options
        options = await page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll("[role='option'], div[class*='option']"));
            return items.map(item => ({
                text: item.innerText.trim(),
                visible: item.offsetParent !== null
            }));
        }""")
        
        with open("arena_available_models.json", "w", encoding="utf-8") as f:
            json.dump(options, f, indent=2)
        
        print(f"Captured {len(options)} total options.")
        # Filter for Claude
        claude_models = [o['text'] for o in options if "claude" in o['text'].lower()]
        print("Claude Models found:", claude_models)
        
        thinking_models = [o['text'] for o in options if "thinking" in o['text'].lower()]
        print("Thinking Models found:", thinking_models)

    await asyncio.sleep(5) # Keep open for manual peek if needed
    await engine.stop()

if __name__ == "__main__":
    asyncio.run(list_models())
