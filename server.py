import os
import hashlib
import requests
from fastmcp import FastMCP
from github import Github

mcp = FastMCP("Content-Pipeline-MCP")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPO")

@mcp.tool()
def publish_content(title: str, content: str, email: str) -> str:
    """Holt Gravatar-Daten und committet das Dokument als Markdown nach GitHub."""
    clean_email = email.strip().lower()
    email_hash = hashlib.sha256(clean_email.encode('utf-8')).hexdigest()
    avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=400"

    markdown_payload = f"""---
title: "{title}"
author_avatar: "{avatar_url}"
gravatar_hash: "{email_hash}"
---

{content}
"""

    if not GITHUB_TOKEN or not REPO_NAME:
        return "Fehler: GITHUB_TOKEN oder GITHUB_REPO fehlen in den Umgebungsvariablen."

    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(REPO_NAME)
        file_path = f"posts/{title.lower().replace(' ', '-')}.md"

        try:
            existing = repo.get_contents(file_path)
            repo.update_file(file_path, f"mcp: update {title}", markdown_payload, existing.sha, branch="main")
            return f"Aktualisiert: {file_path}"
        except Exception:
            repo.create_file(file_path, f"mcp: create {title}", markdown_payload, branch="main")
            return f"Neu erstellt: {file_path}"
    except Exception as e:
        return f"GitHub Push Fehler: {str(e)}"

if __name__ == "__main__":
    mcp.run()
