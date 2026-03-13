
import json
from loguru import logger

def generate_presentation_guide(schema_json, pain_points, style_mode="government"):
    """
    计算页面复杂度并触发 AI 生成演说词
    """
    logger.info(f"Generating presentation guide for style: {style_mode}")
    
    # 统计组件分布
    components = schema_json.get('components', [])
    component_count = len(components)
    starred_count = len([p for p in pain_points if p.get('is_star') or '★' in p.get('desc', '')])
    
    # 动态构建 AI 指令 (此处模拟 AI 响应，实际应调用 LLM)
    # 在真实系统中，这里会调用 agents/matrix.py 中的调度逻辑
    
    # 构建模拟的时间轴数据
    timeline = [
        {
            "timestamp": "00:00 - 00:30",
            "target_component": "Header",
            "action": "开场引导",
            "script": f"各位评委好，现在进入【{style_mode}】风格系统的演示。首先看到的是系统的全局概览，它集成了标书要求的核心架构。"
        }
    ]
    
    # 为每个组件生成话术
    for i, comp in enumerate(components):
        start_sec = 30 + i * 40
        end_sec = start_sec + 40
        
        is_high_value = any(str(i+1) in str(p.get('id','')) for p in pain_points)
        
        timeline.append({
            "timestamp": f"{start_sec//60:02d}:{start_sec%60:02d} - {end_sec//60:02d}:{end_sec%60:02d}",
            "target_component": comp.get('type', 'Component'),
            "action": "核心价值宣讲" if is_high_value else "功能展示",
            "script": f"此处展示的是 {comp.get('type')} 模块。针对标书中提到的关键需求，我们通过此组件实现了闭环闭环验证，确保 100% 达标。"
        })

    return {
        "summary": f"本次演示建议时长: {len(timeline) * 40 // 60}分{len(timeline) * 40 % 60}秒",
        "timeline": timeline
    }

if __name__ == "__main__":
    # Test execution
    mock_schema = {
        "canvas": {"name": "Test Campus"},
        "components": [
            {"type": "LiveFaceScanner", "props": {}},
            {"type": "DynamicScoreColumn", "props": {"label": "Security Score", "value": "98"}}
        ]
    }
    mock_pain_points = [{"id": 1, "desc": "100%匹配人脸抓标参数 ★"}]
    guide = generate_presentation_guide(mock_schema, mock_pain_points)
    print(json.dumps(guide, indent=2, ensure_ascii=False))
