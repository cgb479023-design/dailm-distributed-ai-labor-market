"""
Social Listening Agent — The scouts of the DAILM system.

This agent utilizes the internet channels (Web, RSS, GitHub, etc.) to gather
real-time industry buzzwords, competitor mentions, and public sentiment.
Its intelligence is then fed into the BidMaster (PreBidAgent) to enrich proposals.
"""

from typing import Any, Dict, List
from loguru import logger
from channels import get_channel
from agents.matrix import ModelMatrix


class SocialListeningAgent:
    """Agent that gathers and synthesizes social/industry intelligence."""

    def __init__(self, matrix: ModelMatrix):
        self.node_id = "social_scout"
        self.matrix = matrix

    async def gather_industry_context(self, industry: str, keywords: List[str]) -> str:
        """
        Gather real-time industry context using internet channels and synthesize it.
        
        Args:
            industry: The target industry (e.g., "Smart City IT")
            keywords: Key focus areas (e.g., ["Surveillance", "Access Control"])
            
        Returns:
            A synthesized intelligence briefing (Markdown) to be injected into proposals.
        """
        logger.info(f"[SocialAgent] Scouting intelligence for: {industry} | {keywords}")
        
        raw_intel = []

        # 1. Fetch latest RSS feeds for industry news (Simulated specific targets for now)
        rss_ch = get_channel("rss")
        if rss_ch:
            logger.info("[SocialAgent] Fetching latest RSS trends...")
            # We would normally search dynamically, but here we query a generic IT feed 
            # or rely on the agent-reach Exa search.
            # For demonstration, we'll try to use EXA search if we had it, or just use 
            # WebChannel on a known search URL. Let's ask the LLM to synthesize based 
            # on the requested keywords instead if channels fail.
            intel = await rss_ch.safe_fetch("https://hnrss.org/newest?q=tech", limit=5)
            if intel.get("status") == "ok":
                raw_intel.append(f"### HackerNews Tech Trends\n{intel['content'][:1000]}")

        # 2. Search GitHub for open source solutions related to keywords
        gh_ch = get_channel("github")
        if gh_ch and keywords:
            logger.info(f"[SocialAgent] Searching GitHub for: {keywords[0]}...")
            gh_res = await gh_ch.safe_fetch(f"search:{keywords[0]} system", mode="search")
            if gh_res.get("status") == "ok":
                raw_intel.append(f"### Open Source Ecosystem ({keywords[0]})\n{gh_res['content'][:1000]}")

        # 3. Synthesize the findings into "Industry Context" via the ModelMatrix
        logger.info("[SocialAgent] Synthesizing gathered intelligence...")
        
        intel_text = "\n\n".join(raw_intel) if raw_intel else "No real-time channel data available."

        system_prompt = (
            "You are a Senior Industry Analyst. Based on the provided raw internet intelligence "
            "and your own knowledge of the industry, generate a short 'Industry Buzzword & Trend' "
            "briefing. This will be used by our Bid Writing team to sound highly professional and cutting-edge."
        )
        
        user_prompt = (
            f"Target Industry: {industry}\n"
            f"Focus Keywords: {', '.join(keywords)}\n\n"
            f"Raw Internet Intel:\n{intel_text}\n\n"
            "Output precisely 3-5 trending technical buzzwords and a 2 sentence summary of current industry standards."
        )

        try:
            # Route to a reasoning model
            response = await self.matrix.route_task("reasoning", user_prompt, system_prompt=system_prompt)
            result = response.get("content", "Intelligence gathering failed.")
            logger.success("[SocialAgent] Intelligence synthesis complete.")
            return result
        except Exception as e:
            logger.error(f"[SocialAgent] Synthesis failed: {e}")
            return f"*Fallback Intelligence: Focus on zero-trust architecture and AI-driven automation for {industry}.*"
