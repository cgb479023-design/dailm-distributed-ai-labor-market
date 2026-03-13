import json

# 针对海南大学标书 HD2025-1-007 定制的业务蓝图
hainan_blueprint = {
    "project_name": "海南大学平安校园升级改造项目",
    "project_id": "HD2025-1-007",
    "star_clauses": 24, # 标书中识别到的 ★ 总数
    "features": [
        {
            "id": "points_600",
            "name": "★ 活体检测关键点 ≥ 600",
            "target_value": 600,
            "current_value": 0,
            "status": "pending",
            "description": "满足标书第24/32页：支持600个关键点以上的拓扑分析"
        },
        {
            "id": "latency_50",
            "name": "★ 识别响应延迟 < 50ms",
            "target_value": 50,
            "current_value": 0,
            "status": "pending",
            "description": "满足标书第29页：极速人脸抓拍与评分"
        },
        {
            "id": "offline_ready",
            "name": "★ 离线全量数据处理",
            "target_value": 1,
            "current_value": 0,
            "status": "pending",
            "description": "规避第10页提到的离线环境下实质性不满足风险"
        }
    ]
}

with open("blueprint.json", "w", encoding="utf-8") as f:
    json.dump(hainan_blueprint, f, ensure_ascii=False, indent=4)

print("blueprint.json generated. Please refresh GUI.")
