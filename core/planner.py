import json
import uuid
from typing import List, Dict, Any
from loguru import logger

class TaskStep:
    def __init__(self, step_id: str, agent_type: str, goal: str, instructions: str, dependencies: List[str] = []):
        self.step_id = step_id
        self.agent_type = agent_type
        self.goal = goal
        self.instructions = instructions
        self.dependencies = dependencies or []
        self.status = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
        self.result = None

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "agent_type": self.agent_type,
            "goal": self.goal,
            "instructions": self.instructions,
            "dependencies": self.dependencies,
            "status": self.status,
            "result": self.result
        }

class TaskDecomposer:
    """
    Decomposes aggregate goals into discrete, executable steps for specialized agents.
    Inspired by snarktank/antfarm.
    """
    def __init__(self, matrix):
        self.matrix = matrix

    async def decompose(self, aggregate_goal: str) -> List[TaskStep]:
        logger.info(f"[PLANNER]: Decomposing goal: {aggregate_goal}")
        
        decomposition_prompt = f"""
        GOAL: {aggregate_goal}
        
        TASK:
        Break down the above goal into a sequence of discrete steps executable by specialized agents.
        Available Agents:
        - "search": Research, web surfing, data extraction.
        - "logic": Data analysis, reasoning, algorithm design.
        - "code": Implementation of Python/JS/HTML/CSS.
        - "creative": Content generation, UI design, copywriting.
        - "verifier": Security audit, logic verification.
        
        For each step, provide:
        1. A unique string ID.
        2. The required agent type.
        3. A concise goal for that step.
        4. Detailed instructions for the agent.
        5. A list of IDs for prerequisite steps (dependencies).
        
        Return ONLY a JSON list of objects:
        [
          {{
            "id": "step_1",
            "agent": "search",
            "goal": "...",
            "instructions": "...",
            "dependencies": []
          }},
          ...
        ]
        """
        
        try:
            # Use the matrix to perform the decomposition (usually via a high-reasoning model like Gemini or Claude)
            response = await self.matrix.route_task("logic", decomposition_prompt, bypass_verification=True)
            content = response.get("data", "[]")
            
            # Clean up potential markdown formatting in LLM response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            raw_steps = json.loads(content)
            steps = []
            for rs in raw_steps:
                steps.append(TaskStep(
                    step_id=rs["id"],
                    agent_type=rs["agent"],
                    goal=rs["goal"],
                    instructions=rs["instructions"],
                    dependencies=rs.get("dependencies", [])
                ))
            
            logger.success(f"[PLANNER]: Successfully decomposed into {len(steps)} steps.")
            return steps
        except Exception as e:
            logger.error(f"[PLANNER]: Decomposition failed: {e}")
            return []
