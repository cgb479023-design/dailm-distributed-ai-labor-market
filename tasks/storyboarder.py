import re

class Storyboarder:
    def __init__(self):
        # 定义全局赛博美学预设
        self.style_preset = (
            "Cyberpunk aesthetic, cinematic lighting, ultra-detailed 8k, "
            "neon purple and yellow duo-tone, anamorphic lens flare, sharp focus"
        )

    def generate_prompts(self, script_text):
        """将剧本拆解为视觉分镜"""
        # 简单的分句逻辑，提取最具描述性的段落
        scenes = [s.strip() for s in re.split(r'[。！!.\n]', script_text) if len(s.strip()) > 15]
        
        storyboard = []
        # 我们只取前 4 个核心分镜，避免过度生成
        for i, scene in enumerate(scenes[:4]):
            storyboard.append({
                "id": f"SHOT_{i+1}",
                "narrative": scene,
                "prompt": f"Extreme close-up, {scene}, {self.style_preset} --ar 16:9 --v 6.0"
            })
        return storyboard
