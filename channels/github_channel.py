"""
GitHub Channel — Repo info, issues, and code search via gh CLI.

Requires: gh CLI (https://cli.github.com)
"""

import asyncio
import json
from typing import Any, Dict, Tuple
from urllib.parse import urlparse
from .channel_base import Channel
from loguru import logger


class GitHubChannel(Channel):
    name = "github"
    description = "GitHub repos, issues, and code search"
    description_zh = "GitHub 仓库、Issue 和代码搜索"
    backends = ["gh CLI"]
    tier = 1  # Needs auth for full access

    def can_handle(self, url: str) -> bool:
        domain = urlparse(url).netloc.lower()
        return "github.com" in domain

    def check(self) -> Tuple[str, str]:
        if not self._which("gh"):
            return "off", "gh CLI not installed. Install: https://cli.github.com"

        # Check auth
        rc, stdout, stderr = self._run_cli(["gh", "auth", "status"], timeout=10)
        if rc != 0:
            return "warn", "gh CLI installed but not authenticated. Run: gh auth login"

        return "ok", "gh CLI ready — repos, issues, search, PRs"

    async def fetch(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch GitHub content.
        
        Args:
            target: GitHub URL or "search:query" for repo search
            mode: "repo" | "issues" | "readme" | "search" (auto-detected)
        """
        mode = kwargs.get("mode", self._detect_mode(target))
        loop = asyncio.get_event_loop()

        if mode == "search":
            query = target.replace("search:", "").strip()
            return await loop.run_in_executor(None, self._search_repos, query)
        elif mode == "issues":
            return await loop.run_in_executor(None, self._get_issues, target)
        else:
            return await loop.run_in_executor(None, self._get_repo_info, target)

    def _detect_mode(self, target: str) -> str:
        if target.startswith("search:"):
            return "search"
        if "/issues" in target:
            return "issues"
        return "repo"

    def _get_repo_info(self, url: str) -> Dict[str, Any]:
        """Get repo overview via gh repo view."""
        # Extract owner/repo from URL
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) < 2:
            return {"status": "error", "content": "", "source": self.name,
                    "metadata": {"error": f"Invalid GitHub URL: {url}"}}

        repo = f"{parts[0]}/{parts[1]}"
        rc, stdout, stderr = self._run_cli(
            ["gh", "repo", "view", repo, "--json",
             "name,description,stargazerCount,forkCount,primaryLanguage,readme"],
            timeout=15,
        )

        if rc != 0:
            return {"status": "error", "content": stderr[:500], "source": self.name,
                    "metadata": {"error": stderr[:200]}}

        try:
            data = json.loads(stdout)
            readme = data.get("readme", "")
            content = (
                f"# {data.get('name', repo)}\n\n"
                f"⭐ {data.get('stargazerCount', 0)} | "
                f"🍴 {data.get('forkCount', 0)} | "
                f"🔤 {data.get('primaryLanguage', {}).get('name', 'N/A')}\n\n"
                f"{data.get('description', 'No description')}\n\n"
                f"---\n\n{readme[:3000]}"
            )
            return {"status": "ok", "content": content, "source": self.name,
                    "url": url, "metadata": data}
        except Exception as e:
            return {"status": "error", "content": stdout[:500], "source": self.name,
                    "metadata": {"error": str(e)}}

    def _search_repos(self, query: str) -> Dict[str, Any]:
        """Search GitHub repos."""
        rc, stdout, stderr = self._run_cli(
            ["gh", "search", "repos", query, "--json",
             "name,owner,description,stargazerCount,language", "--limit", "10"],
            timeout=15,
        )

        if rc != 0:
            return {"status": "error", "content": stderr[:500], "source": self.name,
                    "metadata": {"error": stderr[:200]}}

        try:
            results = json.loads(stdout)
            lines = [f"# GitHub Search: {query}\n"]
            for r in results:
                owner = r.get("owner", {}).get("login", "?")
                lines.append(
                    f"- **{owner}/{r['name']}** ⭐{r.get('stargazerCount', 0)} "
                    f"({r.get('language', 'N/A')}) — {r.get('description', '')[:100]}"
                )
            return {"status": "ok", "content": "\n".join(lines), "source": self.name,
                    "metadata": {"count": len(results)}}
        except Exception as e:
            return {"status": "error", "content": "", "source": self.name,
                    "metadata": {"error": str(e)}}

    def _get_issues(self, url: str) -> Dict[str, Any]:
        """Get repo issues."""
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) < 2:
            return {"status": "error", "content": "", "source": self.name,
                    "metadata": {"error": "Invalid URL"}}

        repo = f"{parts[0]}/{parts[1]}"
        rc, stdout, stderr = self._run_cli(
            ["gh", "issue", "list", "-R", repo, "--json",
             "title,state,createdAt,author", "--limit", "15"],
            timeout=15,
        )

        if rc != 0:
            return {"status": "error", "content": stderr[:500], "source": self.name,
                    "metadata": {"error": stderr[:200]}}

        try:
            issues = json.loads(stdout)
            lines = [f"# Issues: {repo}\n"]
            for i in issues:
                author = i.get("author", {}).get("login", "?")
                lines.append(f"- [{i['state']}] {i['title']} (by @{author})")
            return {"status": "ok", "content": "\n".join(lines), "source": self.name,
                    "metadata": {"count": len(issues)}}
        except Exception as e:
            return {"status": "error", "content": "", "source": self.name,
                    "metadata": {"error": str(e)}}
