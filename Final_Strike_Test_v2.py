import asyncio
from loguru import logger
from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter
from agents.lmsys_adapter import LmsysAdapter
from tasks.storyboarder import Storyboarder
from utils.terminal_visuals import CyberTerminal

async def run_v2_strike():
    engine = BrowserEngine()
    storyboarder = Storyboarder()
    await engine.start(headless=False)
    
    matrix = ModelMatrix(engine)
    matrix.register_adapter("gemini", GeminiWebAdapter(engine))
    matrix.register_adapter("claude", LmsysAdapter(engine, None))
    
    try:
        # --- 阶段 1: Gemini 策略提取 ---
        CyberTerminal.decrypt_bar("HARVESTING_GEMINI_STRATEGY", duration=1.2)
        res_gemini = await matrix.adapters["gemini"].query("提取'仿生人超市'的核心视觉钩子和留存策略。")
        
        # --- 阶段 2: Claude 剧本升维 (带有优化后的抓取逻辑) ---
        CyberTerminal.decrypt_bar("CLAUDE_NEURAL_REWRITE", duration=2.5)
        prompt = f"基于这些视觉钩子：{res_gemini['text']}，写一段15秒充满孤独感的赛博朋克开场旁白。"
        res_claude = await matrix.adapters["claude"].query(prompt)
        
        # --- 阶段 3: Storyboarder 自动分镜 ---
        CyberTerminal.decrypt_bar("GENERATING_VISUAL_STORYBOARD", duration=1.8)
        visual_manifest = storyboarder.generate_prompts(res_claude["text"])
        
        # --- 终端实时展示分镜结果 ---
        print("\n" + "="*60)
        print("📊  DAILM VISUAL MANIFEST - V1.2 STORYBOARD")
        print("="*60)
        
        for shot in visual_manifest:
            CyberTerminal.matrix_stream(f"[{shot['id']}]: {shot['narrative']}")
            print(f"\033[93mPROMPT:\033[0m {shot['prompt']}\n")
            
        logger.success(f"Successfully generated {len(visual_manifest)} storyboard frames.")

    except Exception as e:
        logger.error(f"V2 Strike Aborted: {e}")
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(run_v2_strike())
