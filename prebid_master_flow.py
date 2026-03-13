import asyncio
import os
import json
from loguru import logger
from agents.style_generator import IndustryStyle, StyleGenerator
from agents.bid_generator import BidGenerator
from agents.exporter import StrikeExporter
from agents.prebid_agent import PreBidAgent
from agents.social_agent import SocialListeningAgent
from core.sandbox import NeuralSandbox
from agents.context_manager import ContextWindow
from utils.handshake import strict_json_handshake


def _build_deterministic_ui_schema(blueprint: dict, style: IndustryStyle) -> dict:
    """
    Deterministic 9:16 UI Schema Builder.
    Bypasses browser-based AI when headless auth is unavailable.
    """
    template = StyleGenerator.STYLE_TEMPLATES.get(style, StyleGenerator.STYLE_TEMPLATES[IndustryStyle.GOV_BIZ])
    features = blueprint.get("features", [])
    star_clauses = blueprint.get("star_clauses", [])
    metadata = blueprint.get("metadata", {})
    
    top_features = features[:6]
    
    return {
        "canvas": {
            "id": f"prebid_{style.name.lower()}_canvas",
            "name": f"PREBID MASTER {metadata.get('project_name', 'Strike Package')}",
            "ratio": "9:16",
            "theme": template["theme"],
            "background": template["bg"],
        },
        "components": [
            {
                "type": "StatusHeader",
                "props": {
                    "title": metadata.get("project_name", "PREBID MASTER STRIKE"),
                    "subtitle": f"Industry: {metadata.get('industry', 'Government & Smart City')}",
                    "budget": metadata.get("budget", "N/A"),
                },
            },
            {
                "type": "LiveFaceScanner",
                "props": {
                    "resolution": "1080p",
                    "fps": 30,
                    "detection_mode": "multi-target"
                },
                "bid_ref": "FACE-CAPTURE-CORE"
            },
            {
                "type": "DynamicScoreColumn",
                "props": {
                    "label": "Compliance Confidence",
                    "value": "97.8",
                    "color": template.get("accent", "#22d3ee")
                },
                "bid_ref": "COMPLIANCE-SCORE",
            },
            {
                "type": "MetricList",
                "props": {
                    "items": [
                        {
                            "label": f.get("name", "Feature"),
                            "value": f.get("score_ref", "Mapped"),
                            "status": "COMPLIANT"
                        }
                        for f in top_features
                    ] or [{"label": "Feature Coverage", "value": "Pending Mapping"}]
                },
            },
            {
                "type": "StarClausePanel",
                "props": {
                    "clauses": [
                        {"text": sc[:60], "mandatory": True}
                        for sc in star_clauses[:8]
                    ]
                },
                "bid_ref": "MANDATORY-CLAUSES"
            },
            {
                "type": "NetworkTopology",
                "props": {
                    "nodes": len(features),
                    "connections": min(len(features) * 2, 20),
                    "throughput": "3200 req/s"
                }
            }
        ],
    }


async def run_prebid_master_flow(rfp_path: str, style: IndustryStyle):
    """
    PREBID MASTER AI: Full Objective Closure.
    W1 (Parse) + W2 (Synthesize) + W3 (Comply) + W4 (Export)
    Uses deterministic synthesis (no browser auth required).
    """
    logger.info(f"--- 🛡️ PREBID MASTER MISSION START: {rfp_path} ---")
    
    # 1. Init lightweight system (no browser needed)
    sandbox = NeuralSandbox()
    # Create a minimal PreBidAgent without Matrix (parse_rfp doesn't need it)
    agent = PreBidAgent.__new__(PreBidAgent)
    agent.sandbox = sandbox
    agent.asset_dir = os.path.join("prebid_assets")
    os.makedirs(agent.asset_dir, exist_ok=True)

    # 2. W1: RFP Analysis (Parse) - Pure local extraction, no AI needed
    logger.info("═══════════════════════════════════════════")
    logger.info("  PHASE 1: Extracting Blueprint & ★ Clauses")
    logger.info("═══════════════════════════════════════════")
    blueprint = await agent.parse_rfp(rfp_path)
    
    feat_count = len(blueprint.get("features", []))
    star_count = len(blueprint.get("star_clauses", []))
    metadata = blueprint.get("metadata", {})
    logger.success(f"Blueprint extracted: {feat_count} features, {star_count} ★ clauses")
    logger.info(f"  Project: {metadata.get('project_name', 'Unknown')}")
    logger.info(f"  Industry: {metadata.get('industry', 'Unknown')}")
    
    # Save blueprint
    bp_path = os.path.join("prebid_assets", "HAIKOU_CITY_BRAIN_BLUEPRINT.json")
    os.makedirs("prebid_assets", exist_ok=True)
    with open(bp_path, "w", encoding="utf-8") as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=2)
    logger.info(f"  Blueprint saved -> {bp_path}")
    
    # 3. W2: UI Synthesis (9:16 Vision) - Deterministic, no browser needed
    logger.info("═══════════════════════════════════════════")
    logger.info(f"  PHASE 2: Synthesizing 9:16 Demo Schema (Style: {style.value})")
    logger.info("═══════════════════════════════════════════")
    ui_schema = _build_deterministic_ui_schema(blueprint, style)
    ui_schema_json = json.dumps(ui_schema, ensure_ascii=False)
    
    ui_path = os.path.join("prebid_assets", "HAIKOU_CITY_BRAIN_UI.json")
    with open(ui_path, "w", encoding="utf-8") as f:
        json.dump(ui_schema, f, ensure_ascii=False, indent=2)
    logger.success(f"9:16 UI Schema generated -> {ui_path}")
    logger.info(f"  Theme: {ui_schema['canvas']['theme']}")
    logger.info(f"  Components: {len(ui_schema['components'])}")
    
    # 4. W3: Bid Generation (Compliance & Synergy)
    logger.info("═══════════════════════════════════════════")
    logger.info("  PHASE 3: Social Proxy Scouting & Compliance Hub")
    logger.info("═══════════════════════════════════════════")
    
    # [Moat 2] Agent Synergy: Scout the internet for industry trends
    from agents.matrix import ModelMatrix
    matrix = ModelMatrix(engine="gemini")
    social_agent = SocialListeningAgent(matrix)
    
    keywords = [f.get("name", "") for f in blueprint.get("features", [])[:3]]
    logger.info("[PreBidAgent] Consulting SocialAgent for dynamic industry context...")
    industry_context = await social_agent.gather_industry_context(metadata.get("industry", "IT Solutions"), keywords)

    vault_path = os.path.join("vault", "knowledge_hub.json")
    bid_gen = BidGenerator(vault_path)
    matrix_md, risks = bid_gen.generate_compliance_matrix(blueprint)
    
    bid_draft_path = os.path.join("strike_packages", "HAIKOU_CITY_BRAIN_COMPLIANCE.md")
    os.makedirs("strike_packages", exist_ok=True)
    bid_gen.export_bid_draft(blueprint, matrix_md, risks, bid_draft_path, industry_context=industry_context)
    logger.success(f"Compliance matrix generated -> {bid_draft_path}")
    logger.info(f"  Risks identified: {len(risks)}")
    for r in risks[:3]:
        logger.warning(f"  ⚠ {r}")
    
    # 5. Export: Strike Package (Offline Pack with Neural Manifest)
    logger.info("═══════════════════════════════════════════")
    logger.info("  PHASE 4: Sealing Offline Strike Package")
    logger.info("═══════════════════════════════════════════")
    exporter = StrikeExporter()
    
    # Derive UI Score Mapping from actual blueprint features
    score_mapping = [
        {"feature_name": f["name"], "score_ref": f.get("score_ref", "P--")}
        for f in blueprint.get("features", [])
    ]
    for sc in blueprint.get("star_clauses", [])[:5]:
        score_mapping.append({"feature_name": f"★ {sc[:30]}...", "score_ref": "MANDATORY"})
    
    offline_path = exporter.export_strike_package(
        ui_schema=ui_schema_json, 
        output_name="HAIKOU_CITY_BRAIN_STRIKE",
        style=style.name,
        score_mapping=score_mapping
    )
    
    # [Moat 4] True Offline Zip Package (100% Coverage Rule 2)
    import zipfile
    zip_path = "strike_packages/PreBid_Demo_HAIKOU_CITY_BRAIN.zip"
    def generate_mock_data(schema):
        return {"components_count": len(schema.get("components", [])), "live": True, "offline": True}
        
    with zipfile.ZipFile(zip_path, 'w') as z:
        # Include the newly enhanced 9:16 workbench as the offline player
        if os.path.exists("prebid_workbench.html"):
            z.write("prebid_workbench.html", "index.html")
        # Include AI-generated Schema
        z.writestr("data/project_schema.json", ui_schema_json)
        # Include Mock Data
        z.writestr("data/mock_db.json", json.dumps(generate_mock_data(ui_schema), ensure_ascii=False))
    
    logger.info("═══════════════════════════════════════════")
    logger.success("🎯 MISSION COMPLETE!")
    logger.info("═══════════════════════════════════════════")
    logger.info(f"  📋 Blueprint:  {bp_path}")
    logger.info(f"  🎨 UI Schema:  {ui_path}")
    logger.info(f"  📝 Bid Draft:  {bid_draft_path}")
    logger.info(f"  📦 Offline HTML: {offline_path}")
    logger.info(f"  🗜️ Offline ZIP:  {zip_path} (U盘即插即用)")
    logger.info("═══════════════════════════════════════════")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PREBID MASTER Flow Controller")
    parser.add_argument("--rfp", type=str, help="Path to the RFP document", required=True)
    parser.add_argument("--style", type=str, choices=[s.name for s in IndustryStyle], default="TECH_INDUSTRIAL", help="Design style for the 9:16 UI")
    
    args = parser.parse_args()
    selected_style = IndustryStyle[args.style]
    
    asyncio.run(run_prebid_master_flow(args.rfp, selected_style))
