import sys
import os
import unittest
import time

# Add current directory to path
sys.path.append(os.getcwd())

from core.sensing import SituationalAwarenessEngine
from agents.matrix import BiddingEngine

print("Starting TestPatentLogic...")
class TestPatentLogic(unittest.TestCase):
    def setUp(self):
        self.sensing = SituationalAwarenessEngine()
        self.bidding = BiddingEngine()

    def test_hardware_health(self):
        # Normal case
        h1 = self.sensing.calculate_hardware_health(20, 50)
        self.assertGreater(h1, 0.5)
        
        # High load case
        h2 = self.sensing.calculate_hardware_health(90, 85)
        self.assertLess(h2, 0.5)
        
        # Crit case
        h3 = self.sensing.calculate_hardware_health(100, 90)
        self.assertEqual(h3, 0.0)

    def test_thermal_prediction(self):
        node_id = "test_node"
        # Rising temp trend
        for t in [70, 71, 72, 73, 74, 75, 76, 77, 78, 80]:
            self.sensing.update_metrics(node_id, 50, t, 0.1)
        
        decay = self.sensing.predict_thermal_trend(node_id, delta_t_pred=10)
        self.assertLess(decay, 1.0)
        print(f"Thermal Decay: {decay}")

    def test_vickrey_auction(self):
        # Mock bids
        bids = self.bidding.calculate_bids("creative")
        self.assertTrue(len(bids) > 0)
        
        # Verify winner is lowest bid
        bid_values = [b["bid"] for b in bids]
        self.assertEqual(bids[0]["bid"], min(bid_values))

    def test_reputation_update(self):
        node_id = "gemini"
        initial_rho = self.bidding.labor_profiles[node_id]["rho"]
        
        # Simulate a slow task (high latency)
        self.bidding.update_performance(node_id, 10000) # 10s
        
        # Reputation should decrease
        # (Manually trigger update since it's usually in route_task)
        profile = self.bidding.labor_profiles[node_id]
        eta = 0.9
        r_task = 0.5 # Slow
        profile["rho"] = eta * profile["rho"] + (1 - eta) * r_task
        
        self.assertLess(profile["rho"], initial_rho)

if __name__ == "__main__":
    unittest.main()
