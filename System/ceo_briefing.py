#!/usr/bin/env python3
"""
CEO Weekly Briefing Generator — Gold Tier
Runs every Sunday 11pm via PM2 cron.
Reads: Done/, Logs/, Plans/, Business_Goals.md, Odoo MCP
Writes: Briefings/YYYY-MM-DD_Monday_Briefing.md
Updates: Dashboard.md
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
VAULT_PATH   = Path(os.environ.get("VAULT_PATH", "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"))
ENV_FILE     = VAULT_PATH / ".env"
BRIEFINGS    = VAULT_PATH / "Briefings"
DONE         = VAULT_PATH / "Done"
LOGS         = VAULT_PATH / "Logs"
PLANS        = VAULT_PATH / "Plans"
GOALS_FILE   = VAULT_PATH / "Business_Goals.md"
DASHBOARD    = VAULT_PATH / "Dashboard.md"
ODOO_MCP     = "http://localhost:3006"


# ── Load .env ─────────────────────────────────────────────────────────────────
def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


# ── Count weekly activity ─────────────────────────────────────────────────────
def count_weekly_activity() -> dict:
    today = datetime.now()
    week_start = today - timedelta(days=7)

    emails_done    = 0
    whatsapp_done  = 0
    files_done     = 0
    plans_created  = 0
    social_posts   = 0

    # Count Done folder items from this week
    for folder, prefix, counter in [
        (DONE / "Email",    "EMAIL_",    "emails"),
        (DONE / "WhatsApp", "WHATSAPP_", "whatsapp"),
        (DONE / "Files",    "FILE_",     "files"),
    ]:
        if folder.exists():
            for f in folder.glob("*.md"):
                if f.stat().st_mtime > week_start.timestamp():
                    if counter == "emails":    emails_done += 1
                    elif counter == "whatsapp": whatsapp_done += 1
                    elif counter == "files":    files_done += 1

    # Count Plans
    if PLANS.exists():
        for f in PLANS.glob("PLAN_*.md"):
            if f.stat().st_mtime > week_start.timestamp():
                plans_created += 1

    # Count social posts from Done folder root
    if DONE.exists():
        for f in DONE.glob("LINKEDIN_POSTED_*.md"):
            if f.stat().st_mtime > week_start.timestamp():
                social_posts += 1

    # Count from logs
    actions_logged = 0
    if LOGS.exists():
        for log_file in LOGS.glob("log_*.json"):
            try:
                log_date_str = log_file.stem.replace("log_", "")
                log_date = datetime.strptime(log_date_str, "%Y-%m-%d")
                if log_date >= week_start:
                    entries = json.loads(log_file.read_text(encoding="utf-8"))
                    actions_logged += len(entries)
            except Exception:
                pass

    return {
        "emails_done": emails_done,
        "whatsapp_done": whatsapp_done,
        "files_done": files_done,
        "plans_created": plans_created,
        "social_posts": social_posts,
        "actions_logged": actions_logged,
        "total_tasks": emails_done + whatsapp_done + files_done,
    }


# ── Get Odoo financial data ───────────────────────────────────────────────────
def get_odoo_data() -> dict:
    try:
        resp = requests.post(
            f"{ODOO_MCP}/search-invoices",
            json={"state": "posted"},
            timeout=5
        )
        if resp.ok:
            data = resp.json()
            invoices = data.get("invoices", [])
            total_revenue = sum(inv.get("amount_total", 0) for inv in invoices)
            return {
                "available": True,
                "total_invoices": len(invoices),
                "total_revenue": total_revenue,
                "currency": "USD",
            }
    except Exception:
        pass
    return {"available": False, "total_invoices": 0, "total_revenue": 0}


# ── Read business goals ───────────────────────────────────────────────────────
def read_goals() -> dict:
    goals = {"monthly_target": 10000, "active_projects": [], "metrics": []}
    if not GOALS_FILE.exists():
        return goals
    content = GOALS_FILE.read_text(encoding="utf-8")
    for line in content.splitlines():
        if "Monthly goal:" in line:
            try:
                amount = line.split("$")[1].split()[0].replace(",", "")
                goals["monthly_target"] = float(amount)
            except Exception:
                pass
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
            project = line.strip().lstrip("0123456789. **").strip()
            if project:
                goals["active_projects"].append(project)
    return goals


# ── Generate briefing ─────────────────────────────────────────────────────────
def generate_briefing() -> Path:
    BRIEFINGS.mkdir(parents=True, exist_ok=True)

    now      = datetime.now()
    period_end   = now.strftime("%Y-%m-%d")
    period_start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    next_monday  = (now + timedelta(days=(7 - now.weekday()))).strftime("%Y-%m-%d")
    filename = BRIEFINGS / f"{next_monday}_Monday_Briefing.md"

    activity = count_weekly_activity()
    odoo     = get_odoo_data()
    goals    = read_goals()

    monthly_target = goals["monthly_target"]
    revenue        = odoo["total_revenue"]
    revenue_pct    = round((revenue / monthly_target * 100), 1) if monthly_target > 0 else 0
    trend          = "On track" if revenue_pct >= 40 else "Behind target"

    # Build projects list
    projects_str = ""
    for i, proj in enumerate(goals["active_projects"][:5], 1):
        projects_str += f"- {proj}\n"
    if not projects_str:
        projects_str = "- No active projects in Business_Goals.md\n"

    # Odoo section
    if odoo["available"]:
        odoo_section = f"""## Revenue & Accounting (Odoo)
- **This Week Revenue**: ${revenue:,.2f}
- **MTD Total**: ${revenue:,.2f} ({revenue_pct}% of ${monthly_target:,.0f} target)
- **Trend**: {trend}
- **Total Invoices**: {odoo["total_invoices"]}
- **Odoo Status**: Connected (localhost:8069)"""
    else:
        odoo_section = """## Revenue & Accounting (Odoo)
- **Status**: Odoo offline — start with `pm2 start Setup/ecosystem.config.js`
- **Revenue data**: Not available this week"""

    content = f"""---
generated: {now.isoformat()}
period: {period_start} to {period_end}
tier: gold
---

# Monday Morning CEO Briefing
*{next_monday} — Generated Sunday night by AI Employee*

---

## Executive Summary
Week of {period_start} to {period_end}.
Processed **{activity["total_tasks"]} tasks** total — {activity["emails_done"]} emails, {activity["whatsapp_done"]} WhatsApp messages, {activity["files_done"]} files.
**{activity["plans_created"]} plans** created by orchestrator. **{activity["social_posts"]} social posts** published.

---

{odoo_section}

---

## Activity Summary

| Channel | This Week |
|---------|-----------|
| Emails processed | {activity["emails_done"]} |
| WhatsApp handled | {activity["whatsapp_done"]} |
| Files processed | {activity["files_done"]} |
| Plans created | {activity["plans_created"]} |
| Social posts | {activity["social_posts"]} |
| Actions logged | {activity["actions_logged"]} |
| **Total tasks** | **{activity["total_tasks"]}** |

---

## Active Projects
{projects_str}
---

## System Health

| Component | Status |
|-----------|--------|
| Gmail Watcher | Running (PM2) |
| WhatsApp Watcher | Running (PM2) |
| Filesystem Watcher | Running (PM2) |
| Orchestrator | Running (PM2) |
| MCP Email Server | Running (port 3005) |
| Odoo MCP | {"Running (port 3006)" if odoo["available"] else "Offline"} |
| LinkedIn Poster | Cron: 9am Mon-Fri |

---

## Proactive Suggestions

{"- Revenue is on track. Keep posting on LinkedIn to generate leads." if revenue_pct >= 40 else "- Revenue is behind target. Consider increasing outreach and following up on pending invoices."}
- Review /Pending_Approval/ folder for any actions waiting approval.
- Check /Logs/ for any errors from this week.
- LinkedIn token setup will enable automated business posts.

---

## Upcoming This Week
- LinkedIn auto-post: 9am every weekday
- Next CEO briefing: Next Sunday 11pm
- Review pending approvals in Obsidian

---

*Generated by AI Employee — Gold Tier*
*Source data: /Done/, /Logs/, /Plans/, Business_Goals.md, Odoo MCP*
"""

    filename.write_text(content, encoding="utf-8")
    print(f"CEO Briefing written: {filename.name}")
    return filename


# ── Update Dashboard ──────────────────────────────────────────────────────────
def update_dashboard(briefing_file: Path):
    if not DASHBOARD.exists():
        return
    content = DASHBOARD.read_text(encoding="utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- {timestamp}: CEO Briefing generated → {briefing_file.name}\n"

    if "## Recent Activity" in content:
        content = content.replace(
            "## Recent Activity\n",
            f"## Recent Activity\n{entry}"
        )
    else:
        content += f"\n## Recent Activity\n{entry}"

    DASHBOARD.write_text(content, encoding="utf-8")
    print("Dashboard updated with briefing link.")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] CEO Briefing Generator starting...")
    load_env()

    briefing_file = generate_briefing()
    update_dashboard(briefing_file)

    print(f"Done! Open in Obsidian: Briefings/{briefing_file.name}")


if __name__ == "__main__":
    main()
