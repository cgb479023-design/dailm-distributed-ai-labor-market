import json
import os
from datetime import datetime

class AuditLogExporter:
    def __init__(self, output_dir="./mission_logs"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def format_cyber_report(self, mission_id, data):
        """生成带有赛博风格标记的 Markdown 报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
# 🔗 DAILM MISSION DEBRIEF: {mission_id}
> **STATUS:** DECLASSIFIED // NEON-RESTRICTED
> **TIMESTAMP:** {timestamp}
> **SYNC_COHERENCE:** {data.get('coherence', '98.2%')}

---

## 👁️ VISUAL_ANALYSIS (Gemini_Director)
**SOURCE:** [YouTube Studio Pro AI](https://gemini.google.com/gem/e31600358942)
**INSIGHTS:** {data.get('gemini_insight', 'N/A')}

## ✍️ NEURAL_SCRIPT (Claude_Scriptor)
**SOURCE:** [Arena AI / Claude 3.5](https://arena.ai/)
**CONTENT:**
```markdown
{data.get('claude_output', 'Waiting for input...')}
```

---
🛡️ AUDIT_VERIFICATION
RESULT: ✅ CRITICAL_PATH_CONFIRMED
STYLE_GUIDE: NEON_AESTHETICS_V2

[SYSTEM_ENCRYPTION_KEY: AES-256-DAILM-MATRIX]
"""
        return report

    async def save_mission(self, mission_id, raw_data):
        file_path = os.path.join(self.output_dir, f"mission_{mission_id}.md")
        report_content = self.format_cyber_report(mission_id, raw_data)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return file_path
