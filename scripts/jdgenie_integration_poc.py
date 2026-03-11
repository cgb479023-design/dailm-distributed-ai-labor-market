"""
JDGenie Integration Proof-of-Concept
=====================================

This script validates that the JDGenieAdapter can:
  1. Initialize properly within the DAILM framework
  2. Detect capabilities from prompt keywords
  3. (Optionally) Connect to a running genie-tool service

Run:  python scripts/jdgenie_integration_poc.py
"""
import asyncio
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from agents.jdgenie_adapter import JDGenieAdapter


class MockEngine:
    """Minimal mock for BrowserEngine – JDGenieAdapter uses HTTP not Playwright."""

    async def human_delay(self, lo, hi):
        await asyncio.sleep(0.1)


class MockStatusManager:
    """Minimal mock for StatusManager."""

    async def update_node(self, node_id, status, load):
        logger.info(f"[StatusManager] {node_id} → {status} (load={load})")

    async def broadcast_log(self, source, message):
        logger.info(f"[SSE-Log] [{source}] {message}")


async def test_capability_detection():
    """Test that the adapter correctly routes prompts to JDGenie endpoints."""
    adapter = JDGenieAdapter(engine=MockEngine())

    test_cases = [
        ("帮我写一个Python脚本来分析CSV数据", "code_interpreter"),
        ("搜索最近的AI新闻", "deepsearch"),
        ("生成一份关于黄金走势的分析报告", "report"),
        ("Write code to generate a chart", "code_interpreter"),
        ("Research the latest trends in quantum computing", "deepsearch"),
        ("Create a PPT about market analysis", "report"),
        ("随便聊聊天气吧", "deepsearch"),  # fallback
    ]

    print("\n" + "=" * 60)
    print("  JDGenie Capability Detection Test")
    print("=" * 60)

    all_passed = True
    for prompt, expected in test_cases:
        detected = adapter._detect_capability(prompt)
        status = "✓" if detected == expected else "✗"
        if detected != expected:
            all_passed = False
        print(f"  {status}  '{prompt[:40]}...' → {detected} (expected: {expected})")

    print("=" * 60)
    print(f"  Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 60 + "\n")
    return all_passed


async def test_health_check():
    """Test connectivity to genie-tool (requires running service)."""
    adapter = JDGenieAdapter(engine=MockEngine())

    print("\n" + "=" * 60)
    print("  JDGenie Health Check")
    print("=" * 60)

    is_healthy = await adapter.health_check()
    if is_healthy:
        print(f"  ✓ genie-tool is reachable at {adapter.base_url}")
    else:
        print(f"  ⚠ genie-tool is NOT reachable at {adapter.base_url}")
        print(f"    To start it: cd genie-tool && python server.py --port 1601")

    print("=" * 60 + "\n")
    return is_healthy


async def test_live_query():
    """Send a real query to genie-tool (only if healthy)."""
    adapter = JDGenieAdapter(engine=MockEngine(), status_manager=MockStatusManager())

    print("\n" + "=" * 60)
    print("  JDGenie Live Query Test (deepsearch)")
    print("=" * 60)

    try:
        result = await adapter.query("搜索最新的大模型Agent技术进展")
        print(f"  ✓ Response length: {len(result.get('text', ''))}")
        print(f"  ✓ Source: {result.get('source', 'N/A')}")
        text_preview = result.get("text", "")[:200]
        print(f"  ✓ Preview: {text_preview}...")
    except Exception as e:
        print(f"  ✗ Live query failed: {e}")

    print("=" * 60 + "\n")


async def main():
    print("\n🚀 JDGenie Integration PoC – Validating adapter within DAILM\n")

    # Test 1: Capability detection (always works, no service needed)
    await test_capability_detection()

    # Test 2: Health check
    is_healthy = await test_health_check()

    # Test 3: Live query (only if service is up)
    if is_healthy:
        await test_live_query()
    else:
        print("  Skipping live query test (genie-tool not running).\n")

    print("🏁 PoC Complete.\n")


if __name__ == "__main__":
    asyncio.run(main())
