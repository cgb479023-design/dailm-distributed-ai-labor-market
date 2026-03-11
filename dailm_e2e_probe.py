import asyncio
import json
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("DAILM_PROBE")

BASE_URL = "http://127.0.0.1:8000"
TARGET_FILE = "129海口市城市大脑二期项目招标文件.doc"

async def test_rest_api(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib.request.urlopen(req, timeout=120)
        if response.status == 200:
            resp_body = response.read().decode('utf-8')
            return json.loads(resp_body)
        else:
            logger.error(f"[{endpoint}] Failed with status {response.status}: {response.read().decode('utf-8')}")
            return None
    except Exception as e:
        logger.error(f"[{endpoint}] Exception: {str(e)}")
        return None

async def run_e2e_probe():
    logger.info("=========================================")
    logger.info("🚀 INITIALIZING DAILM REAL-BUSINESS PROBE")
    logger.info("=========================================")

    # 1. Check API Health / OpenAPI Specs Docs availability
    try:
        urllib.request.urlopen(f"{BASE_URL}/docs", timeout=5)
        logger.info(f"✅ API Gateway Online. Swagger UI -> {BASE_URL}/docs")
        logger.info(f"✅ OpenAPI JSON      -> {BASE_URL}/openapi.json")
    except Exception:
        logger.error(f"❌ Cannot reach {BASE_URL}. Is Backend running?")
        return

    # 2. Phase 1: Blueprint Extraction
    logger.info("\n--- PHASE 1: EXECUTE NEURAL RECON (Parse RFP) ---")
    parse_res = await test_rest_api("/api/prebid/parse", {"content": TARGET_FILE})
    if not parse_res or parse_res.get("status") != "SUCCESS":
        logger.error("Phase 1 Failed.")
        return
    
    blueprint = parse_res.get("blueprint", {})
    features = blueprint.get("features", [])
    logger.info(f"✅ Blueprint Extracted! Total Features: {len(features)}")
    
    # 3. Phase 2: UI Synthesis
    logger.info("\n--- PHASE 2: SYNTHESIZE 9:16 UI (GOV_BIZ) ---")
    synth_res = await test_rest_api("/api/prebid/synthesize", {
        "blueprint": blueprint,
        "style_name": "GOV_BIZ"
    })
    
    if not synth_res or synth_res.get("status") != "SUCCESS":
        logger.error("Phase 2 Failed.")
        return
    
    ui_schema = synth_res.get("ui_schema", {})
    logger.info(f"✅ UI Schema Generated! Components: {len(ui_schema.get('components', []))}")

    # 4. Phase 3: Bid Draft & Social Synergy
    logger.info("\n--- PHASE 3: COMPLIANCE MATRIX & SOCIAL SYNERGY ---")
    draft_res = await test_rest_api("/api/prebid/bid-draft", {
        "blueprint": blueprint
    })
    
    if not draft_res or draft_res.get("status") != "SUCCESS":
        logger.error("Phase 3 Failed.")
        return
        
    logger.info(f"✅ Bid Draft Saved -> {draft_res.get('draft_path')}")
    logger.info(f"✅ Risks Identified: {draft_res.get('risk_count')}")

    # 5. Phase 4: Full Strike (Atomic E2E) & Auditing
    logger.info("\n--- PHASE 4: FULL STRIKE & ASSET AUDIT (Atomic Execution) ---")
    strike_res = await test_rest_api("/api/prebid/full-strike", {
        "content": TARGET_FILE,
        "style": "GOV_BIZ",
        "output_name": "PROBE_AUTOMATED_STRIKE",
        "score_mapping": []
    })

    if strike_res and strike_res.get("status") == "SUCCESS":
        logger.info("\n=========================================")
        logger.info("   DAILM ASSET AUDIT REPORT (E2E PASS)   ")
        logger.info("=========================================")
        logger.info(f"📄 Draft Path     : {strike_res.get('bid_draft_path')}")
        logger.info(f"📦 Offline Bundle : {strike_res.get('offline_path')}")
        logger.info(f"🛡️ HTML SHA-256   : {strike_res.get('html_sha256')}")
        logger.info(f"🛡️ Schema SHA-256 : {strike_res.get('schema_sha256')}")
        logger.info("=========================================")
    else:
         logger.error("Phase 4 (Full Strike) Failed.")

if __name__ == "__main__":
    asyncio.run(run_e2e_probe())
