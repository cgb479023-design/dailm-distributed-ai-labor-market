import asyncio
import unittest
import sys
print("--- TEST BOOTSTRAP START ---", file=sys.stderr)
import os
import sqlite3
import json
from unittest.mock import MagicMock, AsyncMock
from agents.matrix import ModelMatrix
from core.engine import BrowserEngine

class TestPlannerIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Mock the engine since we don't want to launch a browser
        self.mock_engine = MagicMock(spec=BrowserEngine)
        self.matrix = ModelMatrix(self.mock_engine)
        
        # Mock a successful decomposition response
        mock_steps = [
            {
                "id": "step_1",
                "agent": "search",
                "goal": "research topic",
                "instructions": "search for AI",
                "dependencies": []
            },
            {
                "id": "step_2",
                "agent": "code",
                "goal": "write code",
                "instructions": "print hello world",
                "dependencies": ["step_1"]
            }
        ]
        
        # Mock route_task to return the decomposition plan
        self.matrix.route_task = AsyncMock()
        self.matrix.route_task.side_effect = [
            {"data": json.dumps(mock_steps)}, # Call for decomposition
            {"action": "complete", "data": "search results"}, # Call for step 1
            {"action": "complete", "data": "code snippet"}     # Call for step 2
        ]

    async def test_execute_plan_flow(self):
        goal = "Build an AI app"
        results = await self.matrix.execute_plan(goal)
        
        # Verify results
        self.assertIn("step_1", results)
        self.assertIn("step_2", results)
        self.assertEqual(results["step_1"], "search results")
        self.assertEqual(results["step_2"], "code snippet")
        
        # Verify database state
        conn = sqlite3.connect(self.matrix.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM task_steps WHERE step_id = ?", ("step_1",))
        status = cursor.fetchone()[0]
        self.assertEqual(status, "COMPLETED")
        
        cursor.execute("SELECT status FROM task_steps WHERE step_id = ?", ("step_2",))
        status = cursor.fetchone()[0]
        self.assertEqual(status, "COMPLETED")
        conn.close()

if __name__ == "__main__":
    unittest.main()
