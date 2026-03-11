import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, List

from agents.style_generator import IndustryStyle, StyleGenerator


class StrikeExporter:
    """
    Export PreBid artifacts into a standalone offline package with checksum manifest.
    """

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        :root { --accent: {{ACCENT}}; --bg-canvas: {{BG}}; }
        body { margin: 0; background: #050505; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: Arial, sans-serif; color: #fff; }
        .phone-frame { width: 360px; height: 640px; background: #000; border: 8px solid #333; border-radius: 32px; box-shadow: 0 0 50px rgba(0,0,0,0.5); overflow: hidden; }
        .canvas { width: 100%; height: 100%; background: var(--bg-canvas); padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; gap: 15px; }
        .header { text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        .header h1 { font-size: 14px; color: var(--accent); margin: 0; }
        .scanner { width: 100%; height: 180px; background: rgba(0,0,0,0.3); border: 1px solid var(--accent); border-radius: 12px; position: relative; overflow: hidden; }
        .scan-line { position: absolute; width: 100%; height: 2px; background: var(--accent); top: 0; animation: scan 3s linear infinite; }
        @keyframes scan { 0% { top: 0; } 50% { top: 100%; } 100% { top: 0; } }
        .metric-card { background: rgba(0,0,0,0.4); padding: 15px; border-radius: 16px; border-left: 4px solid var(--accent); }
        .value { font-size: 28px; font-weight: 700; }
        .label { font-size: 10px; opacity: 0.7; text-transform: uppercase; }
        .footer-metrics { margin-top: auto; font-size: 11px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 10px; }
        .item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body>
    <div class="phone-frame"><div class="canvas" id="app"></div></div>
    <script>
        const schema = {{SCHEMA}};
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="header">
                <h1>${schema.canvas.name}</h1>
                <div style="font-size:9px;opacity:0.6;margin-top:5px;">${schema.canvas.theme} | Offline Package</div>
            </div>
            ${schema.components.map(c => {
                if (c.type === 'LiveFaceScanner') return '<div class="scanner"><div class="scan-line"></div></div>';
                if (c.type === 'DynamicScoreColumn') return `<div class="metric-card"><div class="label">${c.props.label}</div><div class="value">${c.props.value}</div></div>`;
                if (c.type === 'MetricList') return `<div class="footer-metrics">${c.props.items.map(m => `<div class="item"><span>${m.label}</span><span style="color:var(--accent)">${m.value}</span></div>`).join('')}</div>`;
                return '';
            }).join('')}
        `;
    </script>
</body>
</html>
"""

    @staticmethod
    def _sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def export_strike_package(self, ui_schema: str, output_name: str, style: str = "SCI_FI", score_mapping: List[dict] = None) -> str:
        """
        Generates a standalone, offline HTML package from a JSON schema.
        Now includes score_mapping integration for manifest generation.
        """
        # Convert style string to IndustryStyle enum
        try:
            style_enum = IndustryStyle[style.upper()]
        except KeyError:
            raise ValueError(f"Invalid style: {style}. Must be one of {list(IndustryStyle.__members__.keys())}")

        bundle = self.export_strike_bundle(ui_schema, style_enum, output_name, score_mapping=score_mapping)
        return bundle["html_path"]

    def export_strike_bundle(
        self,
        schema_json: str,
        style_enum: IndustryStyle,
        output_name: str,
        extra_manifest: Dict[str, Any] | None = None,
        score_mapping: List[dict] = None, # Added score_mapping parameter
    ) -> Dict[str, Any]:
        schema = json.loads(schema_json)
        gen = StyleGenerator()
        styled_schema = gen.inject_to_schema(schema, style_enum)
        template = gen.STYLE_TEMPLATES[style_enum]

        html = self.HTML_TEMPLATE.replace("{{TITLE}}", schema["canvas"]["name"])
        html = html.replace("{{ACCENT}}", template["accent"])
        html = html.replace("{{BG}}", template["bg"])
        html = html.replace("{{SCHEMA}}", json.dumps(styled_schema, ensure_ascii=False))

        output_dir = "strike_packages" # Define output_dir
        os.makedirs(output_dir, exist_ok=True)
        html_path = os.path.join(output_dir, f"{output_name}_OFFLINE.html")
        schema_path = os.path.join(output_dir, f"{output_name}_SCHEMA.json")
        manifest_path = os.path.join(output_dir, f"{output_name}_MANIFEST.json")

        # Generate neural_manifest.md if score_mapping is provided
        neural_manifest_path = None
        if score_mapping:
            neural_manifest_path = os.path.join(output_dir, f"{output_name}_NEURAL_MANIFEST.md")
            with open(neural_manifest_path, "w", encoding="utf-8") as f:
                f.write(f"# NEURAL MANIFEST: {output_name}\n\n")
                f.write("| ID | Score Point | Mapping Ref | Status |\n")
                f.write("|----|-------------|-------------|--------|\n")
                for i, item in enumerate(score_mapping):
                    f.write(f"| {i+1} | {item.get('feature_name', 'N/A')} | {item.get('score_ref', 'P--')} | SIGNED |\n")
            print(f"[EXPORTER]: Neural Manifest generated at {neural_manifest_path}") # Using print as logger is not defined

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(styled_schema, f, ensure_ascii=False, indent=2)

        html_sha = self._sha256(html_path)
        schema_sha = self._sha256(schema_path)
        manifest = {
            "package_name": output_name,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "style": style_enum.name,
            "files": [
                {"path": html_path, "sha256": html_sha, "size": os.path.getsize(html_path)},
                {"path": schema_path, "sha256": schema_sha, "size": os.path.getsize(schema_path)},
            ],
            "integrity": {
                "html_sha256": html_sha,
                "schema_sha256": schema_sha,
            },
        }
        if extra_manifest:
            manifest["extra"] = extra_manifest
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        return {
            "html_path": html_path,
            "schema_path": schema_path,
            "manifest_path": manifest_path,
            "html_sha256": html_sha,
            "schema_sha256": schema_sha,
        }


if __name__ == "__main__":
    exporter = StrikeExporter()
    with open(r"e:\dailm---distributed-ai-labor-market\prebid_assets\HAINAN_SAFE_CAMPUS_UI.json", "r", encoding="utf-8") as f:
        schema = f.read()
    result = exporter.export_strike_bundle(schema, IndustryStyle.GOV_BIZ, "HAINAN_GOV_VERSION")
    print(json.dumps(result, ensure_ascii=False, indent=2))
