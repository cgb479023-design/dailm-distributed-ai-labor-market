import time
import math
from loguru import logger

class SituationalAwarenessEngine:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.temp_history = {} # node_id -> list of temps
        self.rtt_history = {}  # node_id -> list of RTTs
        
        # Standards from patent
        self.T_base = 45.0
        self.T_warn = 80.0
        self.T_crit = 90.0
        self.H_threshold = 0.2
        
        # Weights for Si
        self.alpha = 0.4  # Performance
        self.beta = 0.35   # Health
        self.gamma = 0.25  # Network

    def update_metrics(self, node_id, cpu_usage, temperature, rtt, packet_loss=0.0):
        if node_id not in self.temp_history:
            self.temp_history[node_id] = []
            self.rtt_history[node_id] = []
            
        self.temp_history[node_id].append(temperature)
        if len(self.temp_history[node_id]) > self.window_size:
            self.temp_history[node_id].pop(0)
            
        self.rtt_history[node_id].append(rtt)
        if len(self.rtt_history[node_id]) > self.window_size:
            self.rtt_history[node_id].pop(0)

        return self.calculate_composite_score(node_id, cpu_usage, temperature, rtt, packet_loss)

    def calculate_hardware_health(self, cpu_usage, temperature):
        # Hi = 1 - 0.5 * (Ci/Cmax + max(Ti - Tbase, 0)/(Tcrit - Tbase))
        usage_ratio = cpu_usage / 100.0
        temp_diff = max(temperature - self.T_base, 0)
        temp_ratio = temp_diff / (self.T_crit - self.T_base)
        
        health = 1.0 - 0.5 * (usage_ratio + temp_ratio)
        return max(0.0, health)

    def predict_thermal_trend(self, node_id, delta_t_pred=30):
        temps = self.temp_history.get(node_id, [])
        if len(temps) < 2:
            return 1.0 # No trend yet
            
        w = len(temps)
        x = list(range(w))
        y = temps
        
        # Simple linear regression for slope k: k = (w*sum(xy) - sum(x)*sum(y)) / (w*sum(x^2) - (sum(x))^2)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i * j for i, j in zip(x, y))
        sum_xx = sum(i * i for i in x)
        
        denominator = (w * sum_xx - sum_x**2)
        if denominator == 0:
            k = 0
        else:
            k = (w * sum_xy - sum_x * sum_y) / denominator
        
        t_pred = temps[-1] + k * delta_t_pred
        
        if t_pred > self.T_warn:
            # delta_i_pred = max(0, 1 - (T_pred - T_warn) / (T_crit - T_warn))
            decay = max(0.0, 1.0 - (t_pred - self.T_warn) / (self.T_crit - self.T_warn))
            return decay
        return 1.0

    def calculate_network_consistency(self, node_id, rtt, packet_loss):
        rtt_history = self.rtt_history.get(node_id, [])
        if not rtt_history:
            return 0.0
            
        # RTT_max assume 500ms for normalization
        rtt_max = 0.5 
        rtt_score = max(0.0, 1.0 - (rtt / rtt_max))
        
        # Jitter Consistency JC = 1 / (1 + std_rtt)
        if len(rtt_history) > 1:
            mean_rtt = sum(rtt_history) / len(rtt_history)
            variance = sum((x - mean_rtt) ** 2 for x in rtt_history) / len(rtt_history)
            jitter = math.sqrt(variance)
            jc_score = 1.0 / (1.0 + jitter)
        else:
            jc_score = 1.0
            
        # Ni = l1*(1-RTT/RTTmax) + l2*(1-PLR) + l3*JC
        # Using default lambda: 0.4, 0.3, 0.3
        n_score = 0.4 * rtt_score + 0.3 * (1.0 - packet_loss) + 0.3 * jc_score
        return n_score

    def calculate_composite_score(self, node_id, cpu_usage, temperature, rtt, packet_loss, p_i=1.0):
        h_i = self.calculate_hardware_health(cpu_usage, temperature)
        delta_pred = self.predict_thermal_trend(node_id)
        n_i = self.calculate_network_consistency(node_id, rtt, packet_loss)
        
        # Si = alpha * Pi + beta * (Hi * delta_pred) + gamma * Ni
        s_i = self.alpha * p_i + self.beta * (h_i * delta_pred) + self.gamma * n_i
        
        # Trigger "Constrained Labor" if health is too low
        is_constrained = h_i <= self.H_threshold
        
        return {
            "s_i": s_i,
            "h_i": h_i,
            "n_i": n_i,
            "delta_pred": delta_pred,
            "is_constrained": is_constrained
        }
