#!/usr/bin/env python3
"""
LinkedIn Auto-Poster for AI Employee Vault
Reads Business_Goals.md, generates a professional LinkedIn post, and publishes it.
Token is loaded from .env or LINKEDIN_ACCESS_TOKEN environment variable.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
VAULT_PATH = Path(os.environ.get("VAULT_PATH", "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"))
ENV_FILE   = VAULT_PATH / ".env"
LOG_FILE   = VAULT_PATH / "Logs" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
DONE_DIR   = VAULT_PATH / "Done"
PENDING_DIR= VAULT_PATH / "Pending_Approval"


# ── Load .env ─────────────────────────────────────────────────────────────────
def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


# ── Read Business Goals ────────────────────────────────────────────────────────
def read_business_goals() -> str:
    goals_file = VAULT_PATH / "Business_Goals.md"
    if goals_file.exists():
        return goals_file.read_text(encoding="utf-8")[:2000]
    return "AI Employee automation, productivity, business growth."


# ── Generate Post Content ──────────────────────────────────────────────────────
def generate_post_content() -> str:
    """
    Generate a professional LinkedIn post based on current business goals.
    Uses a rotating template system based on day of week.
    """
    goals_text = read_business_goals()
    day = datetime.now().weekday()  # 0=Monday … 6=Sunday

    # Extract key info from goals
    projects = []
    for line in goals_text.splitlines():
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
            project = line.strip().lstrip("0123456789. **").rstrip("** —").strip()
            if project:
                projects.append(project)

    project_highlight = projects[0] if projects else "AI Employee Vault"

    templates = [
        # Monday — Week kickoff
        f"""Starting the week with AI-powered automation!

Our AI Employee is now running 24/7 — monitoring emails, WhatsApp, and files, then taking action automatically.

This week's focus: {project_highlight}

The future of work isn't about working harder — it's about building smarter systems.

#AI #Automation #Productivity #ArtificialIntelligence #BuildInPublic""",

        # Tuesday — Technical insight
        f"""How does our AI Employee actually work?

It uses 3 layers:
→ Watchers: Python scripts monitoring Gmail, WhatsApp & files
→ Orchestrator: Routes tasks to the right skill
→ MCP Servers: Execute real-world actions (send emails, post updates)

Result: Emails processed, plans created, approvals routed — all without manual input.

Built with Claude Code + Python + Node.js

#TechStack #AIEngineer #ClaudeCode #AgentEngineering""",

        # Wednesday — Business value
        f"""A Digital Employee works 168 hours/week. A human works 40.

The math on AI automation:
• Cost per task: ~$0.25 vs $5.00 (human)
• Availability: 24/7 vs 40hrs/week
• Consistency: 99%+ vs ~90%

We're building this for {project_highlight} and it's already changing how we work.

#BusinessAutomation #DigitalTransformation #Efficiency #AI""",

        # Thursday — Progress update
        f"""Weekly progress update from AI Employee Vault:

Completed this week:
- Emails auto-triaged and replied
- Social media posts scheduled
- CEO briefing generated
- Approval workflow processed

{project_highlight} — moving forward every day.

What are you automating this week?

#WeeklyUpdate #AIEmployee #Productivity #BuildInPublic""",

        # Friday — Inspiration
        f"""What if your business ran itself over the weekend?

Our AI Employee:
- Monitors your inbox while you sleep
- Creates action plans automatically
- Flags approvals for Monday morning
- Posts content on schedule

The goal: You focus on vision. AI handles execution.

Happy Friday! What repetitive task would you automate first?

#TGIF #AIAutomation #WorkSmarter #Entrepreneurship""",

        # Saturday — Learning
        f"""Weekend reading: How we built a Personal AI Employee

Key learnings:
1. Start with watchers — let AI listen before it acts
2. Always require human approval for sensitive actions
3. File-based state is more reliable than databases for agents
4. Claude Code + MCP = powerful local automation

Full architecture: {project_highlight}

#WeekendLearning #AgentEngineering #ClaudeCode #OpenSource""",

        # Sunday — Week ahead
        f"""Sunday planning session complete — AI Employee has the week scheduled.

This week's priorities:
- Client outreach automation
- Invoice processing workflow
- LinkedIn content calendar
- CEO briefing generation

The system is ready. Let's build.

#SundayPlanning #AIProductivity #SmallBusiness #Automation""",
    ]

    return templates[day]


# ── Post to LinkedIn ───────────────────────────────────────────────────────────
def post_to_linkedin(text: str) -> dict:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    urn   = os.environ.get("LINKEDIN_MEMBER_URN", "")

    if not token or token in ("YOUR_TOKEN_HERE", ""):
        return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN not set in .env"}
    if not urn or urn in ("YOUR_URN_HERE", ""):
        return {"success": False, "error": "LINKEDIN_MEMBER_URN not set in .env"}

    payload = {
        "author": f"urn:li:person:{urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        res = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "X-Restli-Protocol-Version": "2.0.0"
            },
            json=payload,
            timeout=30
        )
        if res.ok:
            post_id = res.json().get("id", "unknown")
            return {"success": True, "post_id": post_id}
        else:
            return {"success": False, "error": res.text, "status": res.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Write Approval File (HITL) ─────────────────────────────────────────────────
def write_approval_file(post_text: str) -> Path:
    """If token not set, write to Pending_Approval for human review."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = PENDING_DIR / f"LINKEDIN_POST_{timestamp}.md"
    filepath.write_text(f"""---
type: linkedin_post
action: social_media_post
platform: LinkedIn
created: {datetime.now().isoformat()}
status: pending_approval
---

## LinkedIn Post Draft

{post_text}

---
**To Approve:** Move this file to /Approved folder.
**To Reject:** Move this file to /Rejected folder.
""", encoding="utf-8")
    return filepath


# ── Log Action ─────────────────────────────────────────────────────────────────
def log_action(action: str, result: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logs = []
    if LOG_FILE.exists():
        try:
            logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            logs = []
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action_type": action,
        "actor": "linkedin_poster",
        "result": result
    })
    LOG_FILE.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] LinkedIn Auto-Poster starting...")
    load_env()

    post_text = generate_post_content()
    print(f"\n--- Generated Post ---\n{post_text}\n---\n")

    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")

    if not token or token in ("YOUR_TOKEN_HERE", ""):
        # Token not set — write approval file for human to review
        approval_file = write_approval_file(post_text)
        print(f"Token not configured. Draft saved for approval: {approval_file.name}")
        log_action("linkedin_draft_created", {"file": str(approval_file)})
        return

    result = post_to_linkedin(post_text)

    if result["success"]:
        print(f"Posted to LinkedIn! Post ID: {result.get('post_id')}")
        log_action("linkedin_post", result)

        # Move to Done
        DONE_DIR.mkdir(parents=True, exist_ok=True)
        done_file = DONE_DIR / f"LINKEDIN_POSTED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        done_file.write_text(f"""---
type: linkedin_post
status: posted
post_id: {result.get('post_id')}
posted_at: {datetime.now().isoformat()}
---

## Posted to LinkedIn

{post_text}
""", encoding="utf-8")
    else:
        print(f"LinkedIn post failed: {result.get('error')}")
        log_action("linkedin_post_failed", result)
        # Save as draft for manual review
        approval_file = write_approval_file(post_text)
        print(f"Draft saved for approval: {approval_file.name}")


if __name__ == "__main__":
    main()
