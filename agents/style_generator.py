import json
from enum import Enum
from typing import Dict, Any

class IndustryStyle(Enum):
    GOV_BIZ = "Gov-Biz"
    TECH_INDUSTRIAL = "Tech-Industrial"
    FINANCE_PRO = "Finance-Pro"
    MODERN_SAAS = "Modern-SaaS"
    HEALTHCARE = "Healthcare"
    LOGISTICS = "Logistics"
    RETAIL = "Retail"
    SCI_FI = "Sci-Fi"

class StyleGenerator:
    """
    Manages the 8 core industry style templates from the PreBid Master Whitepaper.
    """
    
    STYLE_TEMPLATES = {
        IndustryStyle.GOV_BIZ: {
            "theme": "Gov-Official",
            "bg": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            "accent": "#003366",
            "prompt_tags": "政务蓝, 商务正式, 大面积留白, 严谨稳重, 结构化排版",
            "canvas_props": {"ratio": "9:16", "mode": "light"}
        },
        IndustryStyle.TECH_INDUSTRIAL: {
            "theme": "Industrial-Future",
            "bg": "#0a0b1e",
            "accent": "#00f2ff",
            "prompt_tags": "深色模式, 藏青黑背景, 荧光青蓝点缀, 数据可视化, 霓虹微光",
            "canvas_props": {"ratio": "9:16", "mode": "dark"}
        },
        IndustryStyle.FINANCE_PRO: {
            "theme": "Finance-Gold",
            "bg": "#ffffff",
            "accent": "#8a6d3b",
            "prompt_tags": "极简高对比, 数据密集, 细线边框, 精确对齐, 沉稳色调",
            "canvas_props": {"ratio": "9:16", "mode": "light"}
        },
        IndustryStyle.MODERN_SAAS: {
            "theme": "SaaS-Glass",
            "bg": "linear-gradient(45deg, #f3f4f6 0%, #ffffff 100%)",
            "accent": "#6366f1",
            "prompt_tags": "扁平化, 大圆角卡片, 毛玻璃, 弥散微阴影, 交互灵动",
            "canvas_props": {"ratio": "9:16", "mode": "glass"}
        },
        IndustryStyle.HEALTHCARE: {
            "theme": "Medical-Pure",
            "bg": "#ffffff",
            "accent": "#10b981",
            "prompt_tags": "纯净留白, 生命绿, 无边框, 适老化交互, 数据高对比",
            "canvas_props": {"ratio": "9:16", "mode": "light"}
        },
        IndustryStyle.LOGISTICS: {
            "theme": "Logi-Track",
            "bg": "#f9fafb",
            "accent": "#ef4444",
            "prompt_tags": "高效紧凑, 状态指示灯, 垂直时间轴, 节点强调, GIS集成",
            "canvas_props": {"ratio": "9:16", "mode": "compact"}
        },
        IndustryStyle.RETAIL: {
            "theme": "Retail-Vibe",
            "bg": "linear-gradient(to bottom, #fff5f5, #ffffff)",
            "accent": "#f97316",
            "prompt_tags": "鲜明撞色, 瀑布流, 促销高亮, 转化漏斗, 沉浸式图文",
            "canvas_props": {"ratio": "9:16", "mode": "vibrant"}
        },
        IndustryStyle.SCI_FI: {
            "theme": "Hyper-Tech Neon",
            "bg": "linear-gradient(135deg, #0a0b1e 0%, #1a1b3a 100%)",
            "accent": "#bc13fe",
            "prompt_tags": "赛博朋克, 玻璃拟态, 渐变流光, 悬浮视效, 暗黑前卫",
            "canvas_props": {"ratio": "9:16", "mode": "dark"}
        }
    }

    def get_style_prompt(self, style: IndustryStyle) -> str:
        data = self.STYLE_TEMPLATES.get(style, self.STYLE_TEMPLATES[IndustryStyle.SCI_FI])
        return f"[STYLE_GEN]: {style.value} Mode. Tags: {data['prompt_tags']}. Force 9:16 Aspect Ratio."

    def inject_to_schema(self, schema: Dict[str, Any], style: IndustryStyle) -> Dict[str, Any]:
        if not isinstance(schema, dict) or "canvas" not in schema:
            # Create a minimal valid schema if it's missing the canvas
            schema = {
                "canvas": {"name": "Recovery View", "theme": "Sci-Fi", "background": "#000"},
                "components": []
            }
        
        template = self.STYLE_TEMPLATES[style]
        schema["canvas"]["theme"] = template["theme"]
        schema["canvas"]["background"] = template["bg"]
        # Update components accent colors if applicable
        for comp in schema.get("components", []):
            if "props" in comp and "accent_color" in comp["props"]:
                comp["props"]["accent_color"] = template["accent"]
        return schema


if __name__ == "__main__":
    # Internal Test
    gen = StyleGenerator()
    print(gen.get_style_prompt(IndustryStyle.GOV_BIZ))
