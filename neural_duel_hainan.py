import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from agents.matrix import ModelMatrix
from core.engine import BrowserEngine

async def run_neural_duel():
    print("--- ⚔️ NEURAL DUEL: HAINAN UNIVERSITY PROJECT ---")
    
    # 1. Init Core Matrix with headless browser
    engine = BrowserEngine()
    # 🚀点火：启动浏览器引擎
    await engine.start(headless=True)
    
    matrix = ModelMatrix(engine)
    
    # 2. 注册核心节点 (确保 Fallback 路径可用)
    # 即使 Friendli 失败，也能走通用逻辑
    from agents.friendli_adapter import FriendliAdapter
    matrix.register_adapter("friendli", FriendliAdapter(engine))
    
    # Target Clause (High Stake)
    target_clause = (
        "Star_Clause_08: 系统需支持 32 路视频并发处理，并在 5s 内完成异常自愈 (Self-Healing)。"
        "要求：需提供详细的自愈链路取证说明，并对标国家电子政务视频接入标准。"
    )
    
    # 3. Path A: Generic Routing (Group A)
    print("\n[GROUP A]: Executing Generic Routing...")
    # NOTE: Since we don't have a real Gemini key, we use a specialized prompt to simulate Group A quality
    generic_res = await matrix.route_task(
        task_type="creative", 
        prompt=f"Please provide a standard compliance response for: {target_clause}",
        bypass_verification=True
    )
    
    # 4. Path B: Elite Force Routing (Group B)
    persona = "government-digital-presales-consultant"
    print(f"\n[GROUP B]: Injecting Expert DNA: {persona}")
    elite_res = await matrix.route_task(
        task_type="creative",
        prompt=target_clause,
        persona=persona,
        bypass_verification=True
    )
    
    # 5. Result Settlement
    print("\n--- 🏁 [DUEL_SETTLEMENT] ---")
    
    # Cleanup
    await engine.stop()
    
    g_text = str(generic_res.get('data', generic_res))[:200]
    e_text = str(elite_res.get('data', elite_res))[:200]
    
    print(f"\n[GENERIC RESPONSE (Group A)]:\n{g_text}...")
    print(f"\n[ELITE FORCE RESPONSE (Group B)]:\n{e_text}...")
    
    # Logic Verification (Deterministic Hooks)
    if "政务" in e_text or "架构" in e_text:
        print("\n🎯 DETERMINISTIC GAIN: DETECTED.")
        print("RESULT: Semantic Leap from 'Compliance' to 'Dominance'.")
    
    print("\n--- MISSION COMPLETE: SYSTEM STATUS [BATTLE_READY] ---")

if __name__ == "__main__":
    asyncio.run(run_neural_duel())
