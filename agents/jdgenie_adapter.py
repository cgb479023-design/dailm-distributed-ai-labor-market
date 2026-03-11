"""
JDGenie Adapter - Bridges JoyAgent-JDGenie's tool service into the DAILM ModelMatrix.

JDGenie's genie-tool exposes FastAPI endpoints on port 1601:
  - /code_interpreter  (smolagents-based code execution)
  - /report            (HTML/PPT/Markdown report generation)
  - /deepsearch        (multi-engine deep search with reflection)
  - /auto_analysis     (automated data analysis)
  - /table_rag         (table-aware RAG)

This adapter wraps those endpoints as an HTTP client, conforming to DAILM's
BaseAdapter.query() contract so the ModelMatrix can route tasks to JDGenie
just like it routes to Gemini, Claude, or Grok.
"""
import asyncio
import json
import os
import uuid
from typing import Dict, Optional, List

import httpx
from loguru import logger

from agents.base_adapter import BaseAdapter


# ---------------------------------------------------------------------------
# Configuration – override via env vars or constructor
# ---------------------------------------------------------------------------
DEFAULT_GENIE_TOOL_BASE_URL = os.getenv("GENIE_TOOL_BASE_URL", "http://127.0.0.1:1601")


class JDGenieAdapter(BaseAdapter):
    """
    DAILM adapter that delegates work to a running JDGenie genie-tool service.

    Supported capabilities (auto-detected from prompt keywords):
        • code_interpreter – data processing, chart generation, code tasks
        • report           – trend analysis, report generation (HTML/PPT/MD)
        • deepsearch       – web research, fact-finding
    """

    # Keywords used to auto-detect which JDGenie endpoint to hit
    CAPABILITY_KEYWORDS = {
        "code_interpreter": [
            "代码", "code", "编程", "program", "chart",
            "图表", "计算", "数据处理", "data process",
        ],
        "report": [
            "报告", "report", "分析报告", "走势分析",
            "趋势", "trend", "PPT", "ppt", "markdown",
        ],
        "deepsearch": [
            "搜索", "search", "查询", "查找",
            "research", "调研", "news", "新闻",
        ],
    }

    def __init__(
        self,
        engine,
        status_manager=None,
        base_url: str = DEFAULT_GENIE_TOOL_BASE_URL,
        timeout: float = 120.0,
    ):
        super().__init__(engine, status_manager)
        self.node_id = "jdgenie"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = 3

    # ------------------------------------------------------------------
    # Core query – conforms to BaseAdapter contract
    # ------------------------------------------------------------------
    async def query(self, prompt: str) -> Dict[str, str]:
        """
        Route *prompt* to the most appropriate JDGenie tool endpoint,
        collect the full SSE stream, and return a DAILM-compatible dict.
        """
        capability = self._detect_capability(prompt)
        await self.log(f"Detected capability: [{capability}] for prompt: {prompt[:60]}...")

        async def _execute():
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "PROCESSING", 75)

            result = await self._call_genie_tool(capability, prompt)

            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "READY", 10)

            return result

        try:
            return await self.execute_with_ssh_loop(f"JDGenie-{capability}", _execute)
        except Exception as e:
            if self.status_manager:
                await self.status_manager.update_node(self.node_id, "ERROR", 0)
            logger.error(f"JDGenie Node Failure: {e}")
            raise

    # ------------------------------------------------------------------
    # Capability detection
    # ------------------------------------------------------------------
    def _detect_capability(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        scores: Dict[str, int] = {cap: 0 for cap in self.CAPABILITY_KEYWORDS}

        for cap, keywords in self.CAPABILITY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in prompt_lower:
                    scores[cap] += 1

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best] == 0:
            # Default to deepsearch if nothing matched
            return "deepsearch"
        return best

    # ------------------------------------------------------------------
    # HTTP client calls to genie-tool
    # ------------------------------------------------------------------
    async def _call_genie_tool(self, capability: str, prompt: str) -> Dict[str, str]:
        request_id = uuid.uuid4().hex[:12]
        endpoint = f"{self.base_url}/{capability}"

        payload = self._build_payload(capability, prompt, request_id)

        await self.log(f"Calling JDGenie [{capability}] → {endpoint}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # genie-tool uses SSE streaming – we consume the full stream
            collected_text = ""
            file_info: List[dict] = []

            try:
                async with client.stream("POST", endpoint, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue  # heartbeat / comment
                        if line.startswith("data:"):
                            data_str = line[len("data:"):].strip()
                        elif line.startswith("data: "):
                            data_str = line[len("data: "):].strip()
                        else:
                            continue

                        if data_str == "[DONE]":
                            break
                        if data_str == "heartbeat":
                            continue

                        try:
                            data = json.loads(data_str)
                            # Accumulate text
                            if "data" in data:
                                collected_text += data["data"]
                            if "codeOutput" in data:
                                collected_text += data["codeOutput"]
                            # Capture file info
                            if "fileInfo" in data and data["fileInfo"]:
                                file_info.extend(data["fileInfo"])
                        except json.JSONDecodeError:
                            # Plain text chunk
                            collected_text += data_str

            except httpx.HTTPStatusError as e:
                await self.log(f"JDGenie HTTP Error: {e.response.status_code}", level="error")
                raise
            except httpx.ConnectError:
                await self.log(
                    f"Cannot connect to JDGenie at {self.base_url}. "
                    "Ensure genie-tool is running (python server.py --port 1601).",
                    level="error",
                )
                raise

        result = {"text": collected_text.strip()}
        if file_info:
            result["files"] = file_info
        result["source"] = f"jdgenie:{capability}"
        result["request_id"] = request_id

        await self.log(
            f"JDGenie [{capability}] returned {len(collected_text)} chars, "
            f"{len(file_info)} files."
        )
        return result

    # ------------------------------------------------------------------
    # Payload builders per capability
    # ------------------------------------------------------------------
    @staticmethod
    def _build_payload(capability: str, prompt: str, request_id: str) -> dict:
        base = {"requestId": request_id, "stream": True}

        if capability == "code_interpreter":
            base["task"] = prompt
            base["fileNames"] = []
        elif capability == "report":
            base["task"] = prompt
            base["fileNames"] = []
            base["fileType"] = "html"
        elif capability == "deepsearch":
            base["request_id"] = request_id
            base["query"] = prompt
            base["maxLoop"] = 2
        else:
            base["task"] = prompt

        return base

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    async def health_check(self) -> bool:
        """Quick connectivity check to genie-tool."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/docs")
                return resp.status_code == 200
        except Exception:
            return False
