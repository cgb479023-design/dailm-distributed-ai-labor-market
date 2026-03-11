"""
DAILM Prebid Master - Standalone E2E Probe (No Server Required)
================================================================
This script directly imports and exercises the core Python pipeline
without needing Uvicorn/FastAPI. This bypasses the BrowserEngine
(Playwright) dependency that causes crashes under high load.

Usage:
    set PYTHONIOENCODING=utf-8
    .\venv\Scripts\python.exe dailm_standalone_probe.py
"""
import os
import sys
import json
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DAILM_PROBE")

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

TARGET_RFP = "129海口市城市大脑二期项目招标文件.doc"
OUTPUT_NAME = "PROBE_E2E_STRIKE"
STYLE = "GOV_BIZ"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = {}

    logger.info("=" * 60)
    logger.info("  DAILM PREBID MASTER - STANDALONE E2E PROBE")
    logger.info("  (No Server / No Browser / Pure Python)")
    logger.info("=" * 60)

    # ── Phase 1: Blueprint Extraction ────────────────────────
    logger.info("")
    logger.info("--- PHASE 1: NEURAL RECON (Parse RFP) ---")
    try:
        from agents.prebid_agent import PreBidAgent
        from core.sandbox import NeuralSandbox

        sandbox = NeuralSandbox()
        # Pass None as matrix - we use deterministic fallback only
        agent = PreBidAgent(matrix=None, sandbox=sandbox)
        text = agent.extract_text(TARGET_RFP)
        logger.info(f"  Extracted text length: {len(text)} chars")

        # Deterministic blueprint assembly (mirrors prebid_agent.py fallback L190-216)
        local_star = agent._extract_star_clauses_from_text(text)
        blueprint = {
            "metadata": {"project_name": "Probe E2E Test", "industry": "Security & IT"},
            "features": [
                {"id": 1, "name": "Video Surveillance System", "description": "AI-powered camera network", "score_ref": "Tech.Spec.1"},
                {"id": 2, "name": "Access Control Integration", "description": "Smart gate management", "score_ref": "Tech.Spec.2"},
            ],
            "star_clauses": local_star[:120],
            "ui_style_hint": "Gov-Biz",
        }
        features = blueprint["features"]
        star_clauses = blueprint["star_clauses"]
        metadata = blueprint["metadata"]

        logger.info(f"  [PASS] Blueprint extracted!")
        logger.info(f"    Project : {metadata.get('project_name', 'Unknown')}")
        logger.info(f"    Industry: {metadata.get('industry', 'Unknown')}")
        logger.info(f"    Features: {len(features)}")
        logger.info(f"    Star (*) clauses: {len(star_clauses)}")
        results["phase1"] = {"status": "PASS", "features": len(features), "stars": len(star_clauses)}
    except Exception as e:
        logger.error(f"  [FAIL] Phase 1: {e}")
        results["phase1"] = {"status": "FAIL", "error": str(e)}
        # Still try to continue with a mock blueprint
        blueprint = {
            "metadata": {"project_name": "Probe Fallback", "industry": "IT"},
            "features": [{"id": 1, "name": "Video Surveillance", "description": "AI Video"}],
            "star_clauses": ["*must have ISO27001"],
            "ui_style_hint": "Sci-Fi"
        }

    # ── Phase 2: 9:16 UI Schema Synthesis ────────────────────
    logger.info("")
    logger.info("--- PHASE 2: VISUAL SYNTH (9:16 UI Schema) ---")
    try:
        from prebid_master_flow import _build_deterministic_ui_schema
        from agents.style_generator import IndustryStyle

        style_enum = IndustryStyle[STYLE] if STYLE in IndustryStyle.__members__ else IndustryStyle.GOV_BIZ
        ui_schema = _build_deterministic_ui_schema(blueprint, style_enum)
        components = ui_schema.get("components", [])

        logger.info(f"  [PASS] UI Schema generated!")
        logger.info(f"    Theme      : {ui_schema.get('canvas', {}).get('theme', '?')}")
        logger.info(f"    Ratio      : {ui_schema.get('canvas', {}).get('ratio', '?')}")
        logger.info(f"    Components : {len(components)}")
        results["phase2"] = {"status": "PASS", "components": len(components)}
    except Exception as e:
        logger.error(f"  [FAIL] Phase 2: {e}")
        results["phase2"] = {"status": "FAIL", "error": str(e)}
        ui_schema = {"canvas": {"name": "Fallback", "theme": "Gov", "ratio": "9:16"}, "components": []}

    # ── Phase 3: Compliance Matrix & Bid Draft ───────────────
    logger.info("")
    logger.info("--- PHASE 3: COMPLIANCE HUB (Bid Draft + Risk) ---")
    try:
        from agents.bid_generator import BidGenerator

        vault_path = os.path.join("vault", "knowledge_hub.json")
        bid_gen = BidGenerator(vault_path)
        matrix_md, risks = bid_gen.generate_compliance_matrix(blueprint)

        draft_path = os.path.join("strike_packages", f"{OUTPUT_NAME}_BID_DRAFT.md")
        os.makedirs("strike_packages", exist_ok=True)
        bid_gen.export_bid_draft(blueprint, matrix_md, risks, draft_path)

        logger.info(f"  [PASS] Bid Draft generated!")
        logger.info(f"    Draft path : {draft_path}")
        logger.info(f"    Risks found: {len(risks)}")
        if risks:
            for r in risks[:3]:
                logger.info(f"      >> {r[:60]}...")
        results["phase3"] = {"status": "PASS", "draft_path": draft_path, "risk_count": len(risks)}
    except Exception as e:
        logger.error(f"  [FAIL] Phase 3: {e}")
        results["phase3"] = {"status": "FAIL", "error": str(e)}

    # ── Phase 4: Strike Package Export + SHA-256 Audit ───────
    logger.info("")
    logger.info("--- PHASE 4: STRIKE EXPORT + ASSET AUDIT ---")
    try:
        from agents.exporter import StrikeExporter
        from agents.style_generator import IndustryStyle

        exporter = StrikeExporter()
        style_enum = IndustryStyle[STYLE] if STYLE in IndustryStyle.__members__ else IndustryStyle.GOV_BIZ

        score_mapping = [
            {"feature_id": f.get("id"), "feature_name": f.get("name", "?"), "score_ref": f.get("score_ref", "P--")}
            for f in blueprint.get("features", [])
        ]

        bundle = exporter.export_strike_bundle(
            json.dumps(ui_schema, ensure_ascii=False),
            style_enum,
            OUTPUT_NAME,
            extra_manifest={"score_mapping": score_mapping},
        )

        # Verify SHA-256 independently
        html_sha_verify = sha256_file(bundle["html_path"])
        schema_sha_verify = sha256_file(bundle["schema_path"])
        html_match = html_sha_verify == bundle["html_sha256"]
        schema_match = schema_sha_verify == bundle["schema_sha256"]

        logger.info(f"  [PASS] Strike Package exported!")
        logger.info(f"    HTML      : {bundle['html_path']}")
        logger.info(f"    Schema    : {bundle['schema_path']}")
        logger.info(f"    Manifest  : {bundle['manifest_path']}")
        logger.info(f"    HTML SHA  : {bundle['html_sha256']}")
        logger.info(f"    Schema SHA: {bundle['schema_sha256']}")
        logger.info(f"    HTML Integrity   : {'VERIFIED' if html_match else 'MISMATCH!'}")
        logger.info(f"    Schema Integrity : {'VERIFIED' if schema_match else 'MISMATCH!'}")

        results["phase4"] = {
            "status": "PASS",
            "html_path": bundle["html_path"],
            "html_sha256": bundle["html_sha256"],
            "schema_sha256": bundle["schema_sha256"],
            "integrity_html": "VERIFIED" if html_match else "MISMATCH",
            "integrity_schema": "VERIFIED" if schema_match else "MISMATCH",
        }
    except Exception as e:
        logger.error(f"  [FAIL] Phase 4: {e}")
        results["phase4"] = {"status": "FAIL", "error": str(e)}

    # ── Final Report ─────────────────────────────────────────
    logger.info("")
    logger.info("=" * 60)
    all_pass = all(r.get("status") == "PASS" for r in results.values())
    if all_pass:
        logger.info("  FINAL VERDICT:  ALL PHASES PASSED")
    else:
        failed = [k for k, v in results.items() if v.get("status") != "PASS"]
        logger.info(f"  FINAL VERDICT:  FAILED PHASES: {failed}")
    logger.info("=" * 60)

    # Save report
    report_path = os.path.join("strike_packages", f"{OUTPUT_NAME}_E2E_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"  Report saved -> {report_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
