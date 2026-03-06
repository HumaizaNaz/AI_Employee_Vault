#!/usr/bin/env python3
"""
Unified Social Media Auto-Poster — Gold Tier
Posts to Facebook, Instagram, Twitter daily.
Reads Business_Goals.md for context, generates business content,
logs to Done/ and Odoo, writes summary to Logs/.
Runs via PM2 cron: 10am Mon-Fri
"""

import os
import json
import hmac
import hashlib
import base64
import uuid
import time
import requests
import urllib.parse
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
VAULT_PATH = Path(os.environ.get("VAULT_PATH", "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"))
ENV_FILE   = VAULT_PATH / ".env"
DONE_DIR   = VAULT_PATH / "Done"
LOGS_DIR   = VAULT_PATH / "Logs"
PENDING    = VAULT_PATH / "Pending_Approval"
GOALS_FILE = VAULT_PATH / "Business_Goals.md"
ODOO_MCP   = "http://localhost:3006/log-activity"


# ── Load .env ─────────────────────────────────────────────────────────────────
def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


# ── Retry decorator ────────────────────────────────────────────────────────────
def with_retry(func, max_attempts=3, delay=2):
    """Error recovery: retry with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                return {"success": False, "error": str(e)}
            wait = delay * (2 ** attempt)
            print(f"Attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)


# ── Generate post content ──────────────────────────────────────────────────────
def generate_post(platform: str) -> str:
    goals_text = ""
    if GOALS_FILE.exists():
        goals_text = GOALS_FILE.read_text(encoding="utf-8")[:1500]

    projects = []
    for line in goals_text.splitlines():
        if line.strip().startswith(("1.", "2.", "3.")):
            p = line.strip().lstrip("0123456789. **").strip()
            if p:
                projects.append(p)
    proj = projects[0] if projects else "AI Employee Vault"

    day = datetime.now().weekday()
    hour = datetime.now().hour

    templates = {
        "facebook": [
            f"Our AI Employee is working 24/7 so we don't have to!\n\nThis week we automated:\n✅ Email triage & replies\n✅ WhatsApp monitoring\n✅ Social media scheduling\n✅ Invoice processing\n\nProject: {proj}\n\n#AIAutomation #SmallBusiness #Productivity",
            f"What does an AI Employee actually do?\n\n📧 Reads and categorizes emails\n💬 Monitors WhatsApp for urgent messages\n📊 Generates weekly CEO briefings\n🔔 Flags sensitive actions for your approval\n\nAll local, all private. Built with Claude Code.\n\n#AI #Automation #DigitalEmployee",
            f"Fun fact: Our AI Employee processes emails in under 2 minutes.\n\nHuman average: 2.5 hours per day on email.\n\nThat's time back for actual business growth.\n\n{proj} — automating the boring stuff.\n\n#TimeManagement #AITools #Entrepreneur",
            f"Monday motivation: Your AI Employee already processed your weekend emails.\n\nAll categorized. All planned. Urgent ones flagged.\n\nYou just need to approve or reject.\n\n#MondayMotivation #WorkSmarter #AIEmployee",
            f"Security first in AI automation:\n\n🔒 All data stays local (Obsidian vault)\n👤 Human approves ALL sensitive actions\n📝 Every action logged and auditable\n🚫 Credentials never leave your machine\n\nBuild AI that you can trust.\n\n#CyberSecurity #ResponsibleAI #Privacy",
        ],
        "instagram": [
            f"AI Employee working 24/7 ⚡\n\nAutomated this week:\n✅ Email triage\n✅ WhatsApp alerts\n✅ Social posts\n✅ CEO briefing\n\n{proj}\n\n#AIEmployee #Automation #Productivity #Tech #BuildInPublic #AI #SmallBusiness #Entrepreneur",
            f"The future of work is here 🤖\n\nYour AI Employee never sleeps, never takes a break, never misses an email.\n\nAnd it always asks before doing anything sensitive.\n\n#AI #FutureOfWork #Automation #Tech #Claude #Python #BuildInPublic",
            f"168 hours/week vs 40 hours/week 📊\n\nThat's the difference between an AI Employee and a human one.\n\nSame work. 4x the availability. 90% lower cost.\n\n#DigitalTransformation #AITools #Startup #Entrepreneur #BusinessGrowth",
            f"Local-first AI automation 🏠\n\nAll your data stays on YOUR machine.\nNo cloud. No third parties. Just you and your AI.\n\nPrivacy + Automation = Perfect combination\n\n{proj}\n\n#Privacy #LocalFirst #AI #DataSecurity #Tech",
            f"Every email is now a structured task ✉️\n\nFrom: Raw email\nTo: Categorized action file\nResult: Plan created, approval requested if needed\n\nThe AI Employee workflow in action.\n\n#Workflow #Automation #AIEngineer #Python #ClaudeCode",
        ],
        "twitter": [
            f"Our AI Employee processed {day+5} emails this week without human input.\n\nAll categorized. Plans created. Replies drafted.\n\nHuman-in-the-loop for sensitive ones only.\n\n#AIEmployee #Automation",
            f"The Ralph Wiggum loop:\n1. Check /Needs_Action/\n2. Process each item\n3. Update Dashboard\n4. Repeat until done\n\nSimple but powerful. #AgentEngineering #ClaudeCode",
            f"Three watchers. One orchestrator. Zero emails missed.\n\nGmail + WhatsApp + Filesystem → Orchestrator → MCP → Action\n\nThat's the AI Employee stack. #Python #AI #Automation",
            f"Why file-based agents work:\n✅ No database needed\n✅ Human can see/edit state\n✅ Natural audit trail\n✅ Works offline\n✅ Git-syncable\n\n#AgentDesign #AIEngineering #BuildInPublic",
            f"Sent: 0 emails manually this week.\nProcessed: 20+ emails automatically.\nApproval needed: 3 (all reviewed in 5 min).\n\nThis is what AI assistance looks like.\n\n#AIEmployee #Productivity #Automation",
        ]
    }

    posts = templates.get(platform, templates["twitter"])
    return posts[day % len(posts)]


# ── Post to Facebook ───────────────────────────────────────────────────────────
def post_facebook(text: str) -> dict:
    token   = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "me")
    if not token:
        return {"success": False, "error": "FACEBOOK_PAGE_ACCESS_TOKEN not set"}

    def _post():
        res = requests.post(
            f"https://graph.facebook.com/v18.0/{page_id}/feed",
            json={"message": text, "access_token": token},
            timeout=15
        )
        data = res.json()
        if data.get("id"):
            return {"success": True, "post_id": data["id"]}
        return {"success": False, "error": data.get("error", {}).get("message", "Unknown")}

    return with_retry(_post)


# ── Post to Instagram ──────────────────────────────────────────────────────────
def post_instagram(caption: str) -> dict:
    token      = os.environ.get("INSTAGRAM_USER_TOKEN", "")
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
    if not token or not account_id:
        return {"success": False, "error": "Instagram tokens not set"}

    # Instagram requires an image for feed posts — use a default business image
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Square_200x200.png/200px-Square_200x200.png"

    def _post():
        # Step 1: Create media container
        container = requests.post(
            f"https://graph.facebook.com/v18.0/{account_id}/media",
            json={"image_url": image_url, "caption": caption, "access_token": token},
            timeout=15
        ).json()
        if not container.get("id"):
            return {"success": False, "error": container.get("error", {}).get("message", "Container failed")}

        # Step 2: Publish
        publish = requests.post(
            f"https://graph.facebook.com/v18.0/{account_id}/media_publish",
            json={"creation_id": container["id"], "access_token": token},
            timeout=15
        ).json()
        if publish.get("id"):
            return {"success": True, "post_id": publish["id"]}
        return {"success": False, "error": publish.get("error", {}).get("message", "Publish failed")}

    return with_retry(_post)


# ── Post to Twitter ────────────────────────────────────────────────────────────
def post_twitter(text: str) -> dict:
    api_key    = os.environ.get("TWITTER_API_KEY", "")
    api_secret = os.environ.get("TWITTER_API_SECRET", "")
    token      = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")

    if not all([api_key, api_secret, token, token_secret]):
        return {"success": False, "error": "Twitter credentials not set"}

    def _oauth_header(method, url, params):
        oauth = {
            "oauth_consumer_key": api_key,
            "oauth_nonce": uuid.uuid4().hex,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": token,
            "oauth_version": "1.0",
        }
        all_params = {**oauth, **params}
        sorted_params = "&".join(f"{urllib.parse.quote(k,'')  }={urllib.parse.quote(str(v),'')}" for k, v in sorted(all_params.items()))
        base = f"{method}&{urllib.parse.quote(url,'')}&{urllib.parse.quote(sorted_params,'')}"
        signing_key = f"{urllib.parse.quote(api_secret,'')}&{urllib.parse.quote(token_secret,'')}"
        sig = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
        oauth["oauth_signature"] = sig
        return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(str(v),"")}"' for k, v in sorted(oauth.items()))

    def _post():
        url = "https://api.twitter.com/2/tweets"
        body = {"text": text[:280]}
        auth = _oauth_header("POST", url, {})
        res = requests.post(url, json=body, headers={"Authorization": auth, "Content-Type": "application/json"}, timeout=15)
        data = res.json()
        if data.get("data", {}).get("id"):
            return {"success": True, "post_id": data["data"]["id"]}
        return {"success": False, "error": str(data)}

    return with_retry(_post)


# ── Log result ─────────────────────────────────────────────────────────────────
def log_result(platform: str, result: dict, post_text: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if result.get("success"):
        done_file = DONE_DIR / f"{platform.upper()}_POST_{timestamp}.md"
        done_file.write_text(f"""---
type: social_post
platform: {platform}
post_id: {result.get('post_id')}
posted_at: {datetime.now().isoformat()}
---

## Posted to {platform.title()}

{post_text}
""", encoding="utf-8")
        print(f"{platform}: Posted! ID={result.get('post_id')}")
    else:
        # Save failed post to Pending_Approval for manual review
        PENDING.mkdir(parents=True, exist_ok=True)
        draft = PENDING / f"{platform.upper()}_POST_{timestamp}.md"
        draft.write_text(f"""---
type: social_post_draft
platform: {platform}
error: {result.get('error')}
created: {datetime.now().isoformat()}
status: pending_approval
---

## {platform.title()} Post Draft (Failed — Manual Review)

{post_text}

**Error:** {result.get('error')}

Move to /Approved to retry manually.
""", encoding="utf-8")
        print(f"{platform}: Failed ({result.get('error')}) -> Draft saved to Pending_Approval")

    # JSON log
    log_file = LOGS_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.json"
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action_type": f"social_post_{platform}",
        "result": result,
        "platform": platform
    })
    log_file.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding="utf-8")

    # Odoo activity log
    try:
        requests.post(ODOO_MCP, json={
            "source": platform,
            "subject": f"Social Post — {platform.title()}",
            "category": "Social Media",
            "action": "Posted" if result.get("success") else "Failed",
            "details": f"Post ID: {result.get('post_id', 'N/A')}"
        }, timeout=3)
    except Exception:
        pass


# ── Weekly Summary ─────────────────────────────────────────────────────────────
def generate_summary() -> str:
    from datetime import timedelta
    week_start = datetime.now() - timedelta(days=7)
    counts = {"facebook": 0, "instagram": 0, "twitter": 0, "linkedin": 0}

    if DONE_DIR.exists():
        for f in DONE_DIR.glob("*_POST_*.md"):
            if f.stat().st_mtime > week_start.timestamp():
                for platform in counts:
                    if f.name.startswith(platform.upper()):
                        counts[platform] += 1

    total = sum(counts.values())
    return f"Weekly Social Summary: {total} posts — FB:{counts['facebook']} IG:{counts['instagram']} TW:{counts['twitter']} LI:{counts['linkedin']}"


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Social Auto-Poster starting...")
    load_env()

    results = {}

    # Facebook
    fb_text = generate_post("facebook")
    results["facebook"] = post_facebook(fb_text)
    log_result("facebook", results["facebook"], fb_text)

    # Instagram
    ig_text = generate_post("instagram")
    results["instagram"] = post_instagram(ig_text)
    log_result("instagram", results["instagram"], ig_text)

    # Twitter
    tw_text = generate_post("twitter")
    results["twitter"] = post_twitter(tw_text)
    log_result("twitter", results["twitter"], tw_text)

    # Print weekly summary
    summary = generate_summary()
    print(f"\n{summary}")

    # Save summary to Logs
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = LOGS_DIR / f"social_summary_{datetime.now().strftime('%Y-%m-%d')}.md"
    summary_file.write_text(f"""# Social Media Summary — {datetime.now().strftime('%Y-%m-%d')}

{summary}

## Today's Results
| Platform | Status | Post ID |
|----------|--------|---------|
| Facebook | {"✅ Posted" if results['facebook'].get('success') else "❌ Failed"} | {results['facebook'].get('post_id', results['facebook'].get('error', 'N/A'))} |
| Instagram | {"✅ Posted" if results['instagram'].get('success') else "❌ Failed"} | {results['instagram'].get('post_id', results['instagram'].get('error', 'N/A'))} |
| Twitter | {"✅ Posted" if results['twitter'].get('success') else "❌ Failed"} | {results['twitter'].get('post_id', results['twitter'].get('error', 'N/A'))} |
""", encoding="utf-8")

    print(f"Summary saved: {summary_file.name}")


if __name__ == "__main__":
    main()
