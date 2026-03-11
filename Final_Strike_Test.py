import asyncio
import os
import time
from loguru import logger
from core.engine import BrowserEngine
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter
from agents.lmsys_adapter import LmsysAdapter
from agents.grok_adapter import GrokAdapter
from tasks.exporter import AuditLogExporter
from utils.terminal_visuals import CyberTerminal

async def run_final_strike():
    # 1. 初始化引擎
    engine = BrowserEngine()
    exporter = AuditLogExporter()
    await engine.start(headless=False) # 实战建议可见，观察流光效果
    
    # 2. 算力矩阵握手
    matrix = ModelMatrix(engine)
    matrix.register_adapter("gemini", GeminiWebAdapter(engine))
    matrix.register_adapter("claude", LmsysAdapter(engine, None)) # 传入 None 忽略 GUI 状态
    matrix.register_adapter("grok", GrokAdapter(engine))
    
    mission_data = {"coherence": "99.8%"}
    
    try:
        # --- 阶段 A: Gemini 创意提取 ---
        CyberTerminal.decrypt_bar("TARGETING_GEMINI_DIRECTOR", duration=1.5)
        # 目标：你正在查看的 [YouTube Studio Pro AI](https://gemini.google.com/gem/e31600358942)
        gemini_prompt = "提取我之前关于'仿生人超市'视频策划的核心关键词和留存率优化策略，以 JSON 格式输出。"
        res_gemini = await matrix.adapters["gemini"].query(gemini_prompt)
        mission_data["gemini_insight"] = res_gemini["text"]
        logger.success("Gemini Data Harvested.")

        # --- 阶段 B: Arena AI 剧本升维 ---
        CyberTerminal.decrypt_bar("NEURAL_REWRITE_VIA_CLAUDE", duration=2.0)
        # 目标：[Arena AI (LMSYS)](https://arena.ai/)
        claude_prompt = f"基于以下分析，为我写一段充满赛博朋克电影感的开场旁白，侧重于霓虹、机械与孤独感：\n{res_gemini['text']}"
        res_claude = await matrix.adapters["claude"].query(claude_prompt)
        mission_data["claude_output"] = res_claude["text"]
        logger.success("Claude Script Synthesized.")

        # --- 阶段 C: Grok 实时趋势审计 ---
        CyberTerminal.decrypt_bar("AUDITING_TRENDS_VIA_GROK", duration=1.2)
        # 目标：[Grok 实时监测](https://grok.com/)
        grok_prompt = "搜索 2026 年 3 月最新的 YouTube Cyberpunk 视频流行视觉标签和热门 BGM 趋势。"
        res_grok = await matrix.adapters["grok"].query(grok_prompt)
        mission_data["grok_audit"] = res_grok["text"]
        logger.success("Grok Audit Complete.")

        # --- 阶段 D: 档案导出与仪式感 ---
        CyberTerminal.decrypt_bar("FINALIZING_MISSION_ARCHIVE", duration=1.0)
        file_path = await exporter.save_mission("STRIKE_001", mission_data)
        
        # 触发终端流式成功提示
        CyberTerminal.matrix_stream(f">>> MISSION COMPLETE. ARCHIVE SAVED AT: {file_path}")
        logger.critical("--- DAILM FULL STRIKE SUCCESSFUL ---")

    except Exception as e:
        logger.error(f"Strike Aborted: {e}")
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(run_final_strike())
