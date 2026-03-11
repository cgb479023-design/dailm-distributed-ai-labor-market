from loguru import logger
from agents.matrix import ModelMatrix

class TaskWorkflow:
    def __init__(self, matrix: ModelMatrix):
        self.matrix = matrix

    async def run_dynamic_pipeline(self, aggregate_goal: str):
        logger.info(f"Starting dynamic planning for: {aggregate_goal}")
        results = await self.matrix.execute_plan(aggregate_goal)
        return results
