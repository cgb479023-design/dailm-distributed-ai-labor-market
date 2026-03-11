import asyncio
import json
import os
from agents.prebid_agent import PreBidAgent
from agents.style_generator import IndustryStyle
from agents.matrix import ModelMatrix
from core.engine import BrowserEngine
from core.sandbox import NeuralSandbox

async def test_all_styles():
    engine = BrowserEngine()
    await engine.start(headless=True)
    matrix = ModelMatrix(engine)
    sandbox = NeuralSandbox()
    agent = PreBidAgent(matrix, sandbox)
    
    # Use existing blueprint if exists or mock one
    blueprint = {
        "metadata": {"industry": "Smart Campus"},
        "features": [{"id": 1, "name": "Face Scoring", "description": "AI driven face quality audit"}],
        "ui_style_hint": "Modern"
    }
    
    output_dir = "prebid_style_gallery"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"--- 🎨 GENERATING STYLE GALLERY ---")
    for style in IndustryStyle:
        print(f"Synthesizing Style: {style.value}...")
        # Since synthesis uses LLM, we mock the schema update for this test 
        # to focus on logic mapping, or run LLM if matrix is ready.
        from agents.style_generator import StyleGenerator
        gen = StyleGenerator()
        
        # Mock schema
        mock_schema = {
            "canvas": {"id": f"demo_{style.name}", "ratio": "9:16"},
            "components": [{"type": "Header", "props": {"accent_color": "#000"}}]
        }
        
        styled_schema = gen.inject_to_schema(mock_schema, style)
        
        path = os.path.join(output_dir, f"{style.name}_UI.json")
        with open(path, "w") as f:
            json.dump(styled_schema, f, indent=2)
        print(f"Saved: {path}")

    await engine.stop()
    print("--- GALLERY GENERATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_all_styles())
