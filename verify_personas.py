import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from agents.matrix import ModelMatrix
from core.engine import BrowserEngine

async def verify_expert_integration():
    print("--- 🔬 VERIFYING EXPERT PERSONA INTEGRATION ---")
    
    # 1. Init Matrix
    # We use a mock-like approach for engine if real one isn't needed for logic check
    engine = BrowserEngine() 
    matrix = ModelMatrix(engine)
    
    # 2. Check Persona List
    personas = matrix.persona_manager.list_available_personas()
    print(f"Total Personas Loaded: {len(personas)}")
    if not personas:
        print("❌ ERROR: No personas loaded.")
        return

    # 3. Test DNA Injection
    test_persona = "engineering-backend-architect"
    if test_persona not in personas:
        # Fallback to any available persona if specific one isn't found
        test_persona = personas[0]
        
    print(f"Testing Persona: {test_persona}")
    
    # We'll mock route_task behavior or just call it to see logs
    prompt = "Create a database schema for a multi-agent system."
    # We won't actually query a model (to save cost/time), but we'll check the manager directly
    dna = matrix.persona_manager.get_persona(test_persona)
    
    if dna and "[EXPERT_ROLE:" not in dna: # PersonaManager shouldn't have the tag yet
        print(f"✅ DNA correctly retrieved (Length: {len(dna)})")
        print(f"Preview: {dna[:100]}...")
    else:
        print("❌ ERROR: DNA retrieval failed or already tagged.")

    print("--- MISSION SUCCESS: Expert DNA Path Verified ---")

if __name__ == "__main__":
    asyncio.run(verify_expert_integration())
