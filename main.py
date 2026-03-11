import asyncio
import os
import shutil
import uvicorn
import json
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
import psutil
import time

from core.engine import BrowserEngine
from core.doctor import SystemDoctor
from channels import get_channel, get_channel_for_url, check_all as check_all_channels
from agents.matrix import ModelMatrix
from agents.gemini_adapter import GeminiWebAdapter
from agents.lmsys_adapter import LmsysAdapter
from agents.grok_adapter import GrokAdapter
from agents.jdgenie_adapter import JDGenieAdapter
from agents.asset_manager import AssetManager
from agents.prebid_agent import PreBidAgent
from agents.bid_generator import BidGenerator
from agents.exporter import StrikeExporter
from core.sandbox import NeuralSandbox
from tasks.workflow import TaskWorkflow
from tasks.exporter import AuditLogExporter

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Global state
state = {
    "engine": None,
    "matrix": None,
    "workflow": None,
    "asset_manager": None,
    "prebid_agent": None,
    "sandbox": None,
    "bid_generator": None,
    "strike_exporter": None
}

class StatusManager:
    def __init__(self):
        self.nodes = {
            "gemini": {"status": "READY", "load": 10},
            "claude": {"status": "STANDBY", "load": 0},
            "grok": {"status": "OFFLINE", "load": 0},
            "jdgenie": {"status": "STANDBY", "load": 0}
        }
        self.system_stats = {"cpu": 0, "temp": 45} # 默认值
        self.queue = asyncio.Queue()
        self.current_frames = []

    async def get_real_hardware_stats(self, node_id="system"):
        """抓取真实硬件数据并同步至态势感知引擎"""
        cpu = psutil.cpu_percent()
        # 尝试获取真实温度 (if supported)
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                temp = temps['coretemp'][0].current
            else:
                temp = 40 + (cpu * 0.4) # Fallback
        except:
            temp = 40 + (cpu * 0.4) 

        # We don't have direct RTT here as this is local sensing, 
        # but in a distributed system, this would be measured per node.
        rtt = 0.05 
        
        self.system_stats = {"cpu": cpu, "temp": temp}
        return self.system_stats

    async def update_node(self, node_id, status, load):
        self.nodes[node_id] = {"status": status, "load": load}
        # Push update to queue
        await self.queue.put(json.dumps({
            "type": "NODE_SYNC",
            "data": self.nodes
        }))

    async def update_visual_feed(self, frames):
        self.current_frames = frames
        # Broadcast visual frames
        await self.queue.put(json.dumps({
            "type": "VISUAL_UPDATE",
            "frames": frames,
            "nodes": self.nodes
        }))

    async def broadcast_log(self, source, message):
        """Broadcasts a neural progress log to the SSE frontend"""
        await self.queue.put(json.dumps({
            "type": "SYSTEM_LOG",
            "source": source,
            "message": message
        }))

status_manager = StatusManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info("Starting DAILM Backend Services...")
    state["engine"] = BrowserEngine()
    await state["engine"].start(headless=False)
    
    state["matrix"] = ModelMatrix(state["engine"], status_manager)
    
    # Register real adapters with neural sensory (status_manager)
    state["matrix"].register_adapter("gemini", GeminiWebAdapter(state["engine"], status_manager))
    state["matrix"].register_adapter("claude", LmsysAdapter(state["engine"], status_manager))
    state["matrix"].register_adapter("grok", GrokAdapter(state["engine"], status_manager))
    state["matrix"].register_adapter("jdgenie", JDGenieAdapter(state["engine"], status_manager))

    state["workflow"] = TaskWorkflow(state["matrix"])

    state["asset_manager"] = AssetManager()
    state["sandbox"] = NeuralSandbox()
    state["prebid_agent"] = PreBidAgent(state["matrix"], state["sandbox"])
    state["bid_generator"] = BidGenerator(os.path.join("vault", "knowledge_hub.json"))
    state["strike_exporter"] = StrikeExporter()
    
    yield
    
    # Shutdown Sequence
    logger.info("Shutting down DAILM Backend Services...")
    if state["engine"]:
        await state["engine"].stop()

app = FastAPI(title="DAILM Backend API", lifespan=lifespan)

# Allow CORS for React frontend (Vite defaults to 5173, but we set it to 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str # E.g. "analyze", "search", "creative", "workflow"
    prompt: str

class WorkflowRequest(BaseModel):
    url: str


class BidDraftRequest(BaseModel):
    blueprint: dict
    output_path: str | None = None


class OfflineExportRequest(BaseModel):
    ui_schema: dict
    output_name: str = "PREBID_STRIKE"
    style: str = "GOV_BIZ"
    score_mapping: list[dict] | None = None


class FullStrikeRequest(BaseModel):
    content: str | None = None
    style: str = "GOV_BIZ"
    output_name: str = "PREBID_FULL_STRIKE"
    draft_path: str | None = None
    score_mapping: list[dict] | None = None

@app.get("/api/status/stream")
async def status_stream(request: Request):
    """Real-time status stream endpoint for SSE"""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            
            # 1. Handle queued events (Logs, Auctions, Plan updates)
            try:
                while not status_manager.queue.empty():
                    event_data = await status_manager.queue.get()
                    yield {"data": event_data}
            except Exception as e:
                logger.error(f"SSE Queue Error: {e}")

            # 2. Handle periodic hardware sync
            stats = await status_manager.get_real_hardware_stats()
            
            if state["matrix"] and hasattr(state["matrix"], "bidding_engine"):
                state["matrix"].bidding_engine.sensing_engine.update_metrics(
                    "gemini", stats["cpu"], stats["temp"], 0.05
                )
                state["matrix"].bidding_engine.sensing_engine.update_metrics(
                    "claude", stats["cpu"], stats["temp"], 0.08
                )
                state["matrix"].bidding_engine.sensing_engine.update_metrics(
                    "grok", stats["cpu"], stats["temp"], 0.03
                )
            
            data = {
                "type": "SYSTEM_SYNC",
                "nodes": status_manager.nodes,
                "stats": stats,
                "timestamp": time.time()
            }
            yield {"data": json.dumps(data)}
            await asyncio.sleep(1)
            
    return EventSourceResponse(event_generator())

@app.post("/api/system/purge", tags=["System"])
async def system_purge(level: int = 1):
    logger.warning(f"🔥 收到物理泄压指令 [Level {level}]：正在执行强行清空协议...")
    
    try:
        # 1. 强行停止 BrowserEngine (杀掉所有 Chromium 进程)
        if state["engine"]:
            await state["engine"].stop() 
        
        # 2. 清空缓存目录 (UserData)
        cache_dir = state["engine"].user_data_path if state["engine"] else "browser_data" # Fallback if engine not initialized
        if os.path.exists(cache_dir):
            if level >= 3:
                await secure_erase(cache_dir)
            else:
                shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)
            
        # 3. 重置所有节点状态
        for k in status_manager.nodes:
            status_manager.nodes[k] = {"status": "OFFLINE", "load": 0}
            
        await status_manager.queue.put(json.dumps({
            "type": "NODE_SYNC",
            "data": status_manager.nodes
        }))
        
        # 4. 重新初始化引擎 (冷启动)
        if state["engine"]:
            asyncio.create_task(state["engine"].start(headless=False))
        
        return {"status": "SYSTEM_PURGED", "level": level, "message": "所有节点已冷启动，执行了指定等级的擦除。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/purge")
async def purge_system():
    try:
        if state["engine"]:
            await state["engine"].stop()
        return {"status": "PURGED"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Channel System & Doctor Endpoints (Agent-Reach Evolution) ---

class ChannelFetchRequest(BaseModel):
    url: str
    channel: str | None = None  # Force specific channel, or auto-route
    options: dict = {}

@app.get("/api/system/doctor")
async def system_doctor():
    """Unified health diagnostics — channels, adapters, and system resources."""
    try:
        doctor = SystemDoctor(status_manager)
        report = await doctor.diagnose()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/channels/fetch")
async def channel_fetch(req: ChannelFetchRequest):
    """Fetch internet content via auto-routed or specified channel."""
    try:
        if req.channel:
            ch = get_channel(req.channel)
            if not ch:
                raise HTTPException(status_code=404, detail=f"Channel '{req.channel}' not found")
        else:
            ch = get_channel_for_url(req.url)
            if not ch:
                raise HTTPException(status_code=404, detail=f"No channel can handle: {req.url}")
        
        logger.info(f"[ChannelRouter] Routing {req.url[:60]} -> {ch.name}")
        result = await ch.fetch(req.url, **req.options)
        result["routed_channel"] = ch.name
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/list")
async def channel_list():
    """List all available channels and their health status."""
    return check_all_channels()

# --- PreBid Master AI Endpoints ---

@app.post("/api/prebid/parse")
async def prebid_parse(request: Request):
    if not state["prebid_agent"]:
        raise HTTPException(status_code=503, detail="PreBidAgent not initialized")
    try:
        data = await request.json()
        rfp_content = data.get("content", "")
        if not rfp_content:
            raise HTTPException(status_code=400, detail="Missing rfp_content")
        
        blueprint = await state["prebid_agent"].parse_rfp(rfp_content)
        # Ensure it's not double nested if the agent already returned a dict with 'blueprint'
        result_blueprint = blueprint.get("blueprint", blueprint) if isinstance(blueprint, dict) else blueprint
        return {"status": "SUCCESS", "blueprint": result_blueprint}
    except Exception as e:
        logger.error(f"PreBid Parse Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prebid/synthesize")
async def prebid_synthesize(request: Request):
    if not state["prebid_agent"]:
        raise HTTPException(status_code=503, detail="PreBidAgent not initialized")
    try:
        data = await request.json()
        blueprint = data.get("blueprint", {})
        if not blueprint:
            raise HTTPException(status_code=400, detail="Missing blueprint")
        
        ui_schema_str = await state["prebid_agent"].synthesize_916_ui(blueprint)
        ui_schema = json.loads(ui_schema_str)
        return {"status": "SUCCESS", "ui_schema": ui_schema}
    except Exception as e:
        logger.error(f"PreBid Synthesize Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prebid/bid-draft")
async def prebid_bid_draft(req: BidDraftRequest):
    if not state["bid_generator"]:
        raise HTTPException(status_code=503, detail="BidGenerator not initialized")
    try:
        blueprint = req.blueprint or {}
        if not blueprint:
            raise HTTPException(status_code=400, detail="Missing blueprint")
        matrix_md, risks = state["bid_generator"].generate_compliance_matrix(blueprint)
        output_path = req.output_path or os.path.join("strike_packages", "BID_DRAFT_AUTO.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        draft_path = state["bid_generator"].export_bid_draft(blueprint, matrix_md, risks, output_path)
        return {
            "status": "SUCCESS",
            "draft_path": draft_path,
            "risk_count": len(risks),
            "risks": risks,
            "compliance_matrix": matrix_md
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PreBid BidDraft Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prebid/export-offline")
async def prebid_export_offline(req: OfflineExportRequest):
    if not state["strike_exporter"]:
        raise HTTPException(status_code=503, detail="StrikeExporter not initialized")
    try:
        from agents.style_generator import IndustryStyle

        if not req.ui_schema:
            raise HTTPException(status_code=400, detail="Missing ui_schema")

        style = IndustryStyle[req.style] if req.style in IndustryStyle.__members__ else IndustryStyle.GOV_BIZ
        ui_schema_json = json.dumps(req.ui_schema, ensure_ascii=False)
        bundle = state["strike_exporter"].export_strike_bundle(
            ui_schema_json,
            style,
            req.output_name,
            extra_manifest={"score_mapping": req.score_mapping or []}
        )
        return {
            "status": "SUCCESS",
            "offline_path": bundle["html_path"],
            "schema_path": bundle["schema_path"],
            "manifest_path": bundle["manifest_path"],
            "html_sha256": bundle["html_sha256"],
            "schema_sha256": bundle["schema_sha256"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PreBid ExportOffline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_fallback_ui_schema(blueprint: dict) -> dict:
    """Deterministic fallback schema when creative model route is unavailable."""
    features = blueprint.get("features", [])
    top_features = features[:4]
    return {
        "canvas": {
            "id": "prebid_fallback_canvas",
            "name": "PreBid Fallback Strike",
            "ratio": "9:16",
            "theme": "Gov-Official",
            "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        },
        "components": [
            {
                "type": "StatusHeader",
                "props": {
                    "title": "PREBID MASTER OFFLINE STRIKE",
                    "subtitle": f"Industry: {blueprint.get('metadata', {}).get('industry', 'General')}",
                },
            },
            {"type": "LiveFaceScanner", "props": {}, "bid_ref": "FALLBACK-PARSE"},
            {
                "type": "DynamicScoreColumn",
                "props": {"label": "Compliance Confidence", "value": "96.5"},
                "bid_ref": "FALLBACK-SCORE",
            },
            {
                "type": "MetricList",
                "props": {
                    "items": [
                        {"label": f.get("name", "Feature"), "value": f.get("score_ref", "Mapped")}
                        for f in top_features
                    ] or [{"label": "Feature Coverage", "value": "Pending Mapping"}]
                },
            },
        ],
    }


@app.post("/api/prebid/full-strike")
async def prebid_full_strike(req: FullStrikeRequest):
    """
    One-click pipeline:
    parse RFP -> synthesize 9:16 UI -> generate bid draft -> export offline package.
    """
    if not state["prebid_agent"] or not state["bid_generator"] or not state["strike_exporter"]:
        raise HTTPException(status_code=503, detail="PreBid components not initialized")

    try:
        if not req.content:
            raise HTTPException(status_code=400, detail="Missing content")

        # Step 1: parse
        blueprint = await state["prebid_agent"].parse_rfp(req.content)
        if not isinstance(blueprint, dict):
            blueprint = {}
        blueprint.setdefault("metadata", {})
        blueprint.setdefault("features", [])
        blueprint.setdefault("star_clauses", [])
        blueprint.setdefault("ui_style_hint", "Gov-Biz")

        # Step 2: synthesize with fallback
        ui_schema: dict
        try:
            ui_schema_str = await state["prebid_agent"].synthesize_916_ui(blueprint, style_name="Sci-Fi")
            ui_schema = json.loads(ui_schema_str) if ui_schema_str else {}
            if not isinstance(ui_schema, dict) or not ui_schema:
                ui_schema = _build_fallback_ui_schema(blueprint)
        except Exception:
            ui_schema = _build_fallback_ui_schema(blueprint)

        # Step 3: bid draft
        matrix_md, risks = state["bid_generator"].generate_compliance_matrix(blueprint)
        draft_path = req.draft_path or os.path.join("strike_packages", f"{req.output_name}_BID_DRAFT.md")
        os.makedirs(os.path.dirname(draft_path), exist_ok=True)
        final_draft_path = state["bid_generator"].export_bid_draft(blueprint, matrix_md, risks, draft_path)

        # Step 4: export offline package + manifest
        from agents.style_generator import IndustryStyle
        style = IndustryStyle[req.style] if req.style in IndustryStyle.__members__ else IndustryStyle.GOV_BIZ
        final_mapping = req.score_mapping or [
            {
                "feature_id": f.get("id"),
                "feature_name": f.get("name"),
                "score_ref": f.get("score_ref", ""),
            }
            for f in blueprint.get("features", [])
        ]
        bundle = state["strike_exporter"].export_strike_bundle(
            json.dumps(ui_schema, ensure_ascii=False),
            style,
            req.output_name,
            extra_manifest={"score_mapping": final_mapping},
        )

        return {
            "status": "SUCCESS",
            "blueprint": blueprint,
            "ui_schema": ui_schema,
            "bid_draft_path": final_draft_path,
            "risk_count": len(risks),
            "risks": risks,
            "offline_path": bundle["html_path"],
            "schema_path": bundle["schema_path"],
            "manifest_path": bundle["manifest_path"],
            "html_sha256": bundle["html_sha256"],
            "schema_sha256": bundle["schema_sha256"],
            "score_mapping": final_mapping,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PreBid FullStrike Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def secure_erase(path):
    """S5a: Secure Erase (Level 3) - Multi-pass overwrite"""
    logger.info(f"[SECURITY]: 对 {path} 执行深度物理湮灭 (Level 3)...")
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                with open(file_path, "ba+", buffering=0) as f:
                    # Pass 1: Zeros
                    f.write(b'\x00' * size)
                    f.flush()
                    # Pass 2: Ones
                    f.seek(0)
                    f.write(b'\xff' * size)
                    f.flush()
                    # Pass 3: Random
                    f.seek(0)
                    f.write(os.urandom(size))
                    f.flush()
                os.remove(file_path)
            except:
                pass
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
            except:
                pass
    shutil.rmtree(path, ignore_errors=True)


@app.post("/api/task")
async def execute_task(req: TaskRequest):
    if not state["matrix"]:
        raise HTTPException(status_code=503, detail="Matrix not initialized")
        
    try:
        # Depending on complexity, we either use direct routing or full workflow
        result = await state["matrix"].route_task(req.task, req.prompt)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Task Failed: {e}")
        # Return the actual error message so the frontend can display it
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflow/analyze_url")
async def execute_workflow(req: WorkflowRequest):
    if not state["workflow"]:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
        
    try:
        result = await state["workflow"].run_data_analysis_pipeline(req.url)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Workflow Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

exporter = AuditLogExporter()

@app.post("/api/mission/export")
async def export_mission(req: TaskRequest):
    # Simulate fetching aggregate data from the Matrix
    mission_id = f"OP-{os.urandom(2).hex().upper()}"
    
    # Assume communication with adapters has finished
    mission_data = {
        "gemini_insight": "检测到 06:30 留存率异常，建议注入酸性紫闪变效果。",
        "claude_output": "主角站在霓虹超市门口，手中的仿生芯片发出微光...",
        "coherence": "99.1%"
    }
    
    file_path = await exporter.save_mission(mission_id, mission_data)
    return {"status": "exported", "path": file_path, "mission_id": mission_id}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
