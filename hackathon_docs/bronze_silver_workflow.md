# Bronze & Silver Tier — Complete Workflow Guide

---

## BRONZE TIER

### What is Bronze?
Minimum viable AI Employee — monitors emails, organizes files, runs basic approval workflow.

### Bronze Workflow (Step by Step)

```
1. Gmail Watcher runs via PM2
       ↓
2. New important email arrives in Gmail
       ↓
3. EMAIL_abc123.md is created
   Saved to: /Needs_Action/Email/
       ↓
4. Orchestrator checks every cycle
       ├── needs_approval=true  → /Pending_Approval/Email/
       └── needs_approval=false → /Done/Email/
       ↓
5. If moved to Pending_Approval:
   You move the file to the /Approved/ folder
       ↓
6. Orchestrator detects the Approved file
   → Sends email reply via MCP server
   → Moves file to /Done/Email/
   → Writes log to: Logs/YYYY-MM-DD.json
   → Updates Dashboard.md
```

### Bronze Components

| Component | File | Status |
|-----------|------|--------|
| Gmail Watcher | `watchers_gmail/gmail_watcher.py` | PM2: online |
| Filesystem Watcher | `watchers/filesystem_watcher.py` | PM2: online |
| Orchestrator | `System/orchestrator.py` | PM2: online |
| Dashboard | `Dashboard.md` | Auto-updated |
| Base Watcher | `System/base_watcher.py` | Shared base class |

### Bronze Folder Flow

```
/Needs_Action/Email/     ← Gmail Watcher writes here
/Needs_Action/Files/     ← Filesystem Watcher writes here
        ↓
/Pending_Approval/Email/ ← Emails requiring approval
        ↓
/Approved/Email/         ← You move here to approve
/Rejected/               ← You move here to reject
        ↓
/Done/Email/             ← Task complete
/Logs/                   ← Full audit record
```

### Bronze Start Commands

```bash
# Start all processes
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
pm2 start Setup/ecosystem.config.js

# Check status
pm2 status

# Setup Gmail token (first time only)
python watchers_gmail/gmail_auth.py
```

---

## SILVER TIER

### What is Silver?
Bronze + WhatsApp monitoring + LinkedIn auto-post + MCP email server + scheduling.

### Silver Workflow (Complete)

```
┌─────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                      │
│                                                         │
│  Gmail Watcher        WhatsApp Watcher   Filesystem     │
│  (every 2 min)        (every 30 sec)     (realtime)     │
│       ↓                    ↓                 ↓          │
│  EMAIL_*.md          WHATSAPP_*.md       FILE_*.md      │
│       ↓                    ↓                 ↓          │
│  /Needs_Action/Email  /Needs_Action/    /Needs_Action/  │
│                       WhatsApp          Files           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              SCHEDULING LAYER (PM2 Cron)                │
│                                                         │
│  LinkedIn Poster runs at 9am Mon-Fri                   │
│  → Reads Business_Goals.md for context                 │
│  → Generates professional post for the day             │
│  → Token set    → Posts directly to LinkedIn           │
│  → No token     → Saves to /Pending_Approval/          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         REASONING LAYER (Orchestrator)                  │
│         Ralph Wiggum Loop (max 10 iterations)           │
│                                                         │
│  Check /Needs_Action/Email/                             │
│    needs_approval=true  → /Pending_Approval/Email/      │
│    needs_approval=false → /Done/Email/                  │
│                                                         │
│  Check /Needs_Action/WhatsApp/                          │
│    → Always goes to /Pending_Approval/WhatsApp/         │
│      (personal messages require human review)           │
│                                                         │
│  Check /Pending_Approval/Email/                         │
│    File found in Approved/ → Send email via MCP        │
│    File found in Rejected/ → Move to /Rejected/        │
│    Neither found           → Wait for next iteration   │
│                                                         │
│  Update Dashboard.md (counts + timestamp)               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  ACTION LAYER (MCP)                     │
│                                                         │
│  Email MCP Server (port 3005)                          │
│  → Sends actual email via nodemailer                   │
│  → Logs to: Logs/YYYY-MM-DD.json                       │
│  → Moves file to: /Done/Email/                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               DASHBOARD (Obsidian)                      │
│                                                         │
│  Dashboard.md — auto-updated by Orchestrator           │
│  VaultOS (Vercel) — live web dashboard                 │
└─────────────────────────────────────────────────────────┘
```

### Silver Components

| Component | File | PM2 Name | Schedule |
|-----------|------|----------|----------|
| Gmail Watcher | `watchers_gmail/gmail_watcher.py` | gmail-watcher | Continuous |
| WhatsApp Watcher | `watchers_whatsapp/whatsapp_watcher.py` | whatsapp-watcher | Continuous |
| Filesystem Watcher | `watchers/filesystem_watcher.py` | filesystem-watcher | Continuous |
| Orchestrator | `System/orchestrator.py` | orchestrator | Continuous |
| MCP Email Server | `watchers_gmail/mcp/mcp_email.js` | mcp-email-server | Continuous |
| LinkedIn Poster | `Social_Media/linkedin_poster.py` | linkedin-poster | 9am Mon-Fri |

### Silver Folder Flow (Full)

```
WATCHERS write to:
/Needs_Action/
    Email/      ← Gmail emails
    WhatsApp/   ← WhatsApp messages
    Files/      ← Dropped files

ORCHESTRATOR routes to:
/Pending_Approval/
    Email/      ← Emails requiring approval
    WhatsApp/   ← Messages requiring approval
    LINKEDIN_POST_*.md  ← LinkedIn drafts (no token)

YOU DECIDE:
/Approved/      ← Move here to approve
/Rejected/      ← Move here to reject

SYSTEM COMPLETES:
/Done/
    Email/      ← Sent emails
    WhatsApp/   ← Processed messages
    Files/      ← Processed files

RECORDS:
/Plans/         ← PLAN_*.md files (AI reasoning trail)
/Logs/          ← JSON logs (every action recorded)
/Briefings/     ← CEO briefings (Sunday)
```

### Human-in-the-Loop (HITL) — How It Works

```
Orchestrator detects email requiring approval
                     ↓
    /Pending_Approval/Email/EMAIL_abc.md created
                     ↓
         You review the file in Obsidian
                     ↓
        ┌────────────┴────────────┐
        ↓                        ↓
   Move file to              Move file to
   /Approved/                /Rejected/
        ↓                        ↓
   Orchestrator             Orchestrator
   sends email via          moves to /Rejected/
   MCP server               and logs the action
        ↓
   Moved to /Done/Email/
```

### Skills Available

```
.claude/skills/
├── Gmail/             → Email processing
├── WhatsApp/          → Message handling
├── LinkedIn/          → Post to LinkedIn
├── Facebook/          → Post to Facebook
├── Instagram/         → Post to Instagram
├── Twitter_X/         → Post to Twitter
├── Social_Media/      → All platforms combined
├── File_System/       → File operations
├── Orchestrator/      → Task routing
├── CEO_Briefing/      → Weekly briefing
├── VaultOS_Dashboard/ → Dashboard update
├── Git_Sync/          → Vault sync
├── Cloud_Health/      → VM monitoring
└── Odoo_Accounting/   → Invoice management
```

### LinkedIn Token Setup

```
1. Go to: linkedin.com/developers/apps → Create App
2. Products tab → Enable "Share on LinkedIn"
3. Get authorization code via OAuth URL
4. Exchange code for access token via curl
5. Add to .env file:
   LINKEDIN_ACCESS_TOKEN=AQX...
   LINKEDIN_MEMBER_URN=abc123
6. Next 9am: posts automatically
```

### Silver Start Commands

```bash
# Start all processes (first time)
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
pm2 start Setup/ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs gmail-watcher --lines 20
pm2 logs whatsapp-watcher --lines 20
pm2 logs orchestrator --lines 20

# Test LinkedIn poster manually
python Social_Media/linkedin_poster.py

# Save PM2 config (auto-start on reboot)
pm2 save
pm2 startup
```

---

## Quick Reference — What Is Where

| Item | Location |
|------|----------|
| New emails | `/Needs_Action/Email/` |
| New WhatsApp | `/Needs_Action/WhatsApp/` |
| Requires approval | `/Pending_Approval/` |
| Approve an action | Move file to `/Approved/` |
| Reject an action | Move file to `/Rejected/` |
| Completed tasks | `/Done/` |
| Audit logs | `/Logs/YYYY-MM-DD.json` |
| AI plans | `/Plans/PLAN_*.md` |
| LinkedIn drafts | `/Pending_Approval/LINKEDIN_POST_*.md` |
| Dashboard | `Dashboard.md` |
| Tokens & secrets | `.env` (not in git) |

---

## PM2 Processes — Silver Tier

| ID | Name | Type | Status |
|----|------|------|--------|
| 0 | gmail-watcher | Continuous | online |
| 1 | whatsapp-watcher | Continuous | online |
| 2 | filesystem-watcher | Continuous | online |
| 3 | orchestrator | Continuous | online |
| 4 | mcp-email-server | Continuous | online |
| 5 | linkedin-poster | Cron 9am Mon-Fri | stopped (normal) |
