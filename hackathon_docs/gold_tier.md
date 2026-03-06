# Gold Tier — Complete Workflow & Status

---

## What is Gold Tier?

Full business automation — Personal (Gmail, WhatsApp) and Business (Odoo, Social Media) working together. The CEO receives a weekly briefing, invoices are tracked in Odoo, and social media posts automatically every weekday.

---

## Complete Gold Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│                                                                 │
│  Gmail Watcher     WhatsApp Watcher    Filesystem Watcher       │
│  (every 2 min)     (every 30 sec)      (realtime)               │
│       ↓                  ↓                   ↓                  │
│  EMAIL_*.md        WHATSAPP_*.md        FILE_*.md               │
│  /Needs_Action/    /Needs_Action/       /Needs_Action/          │
│  Email/            WhatsApp/            Files/                  │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              SCHEDULING LAYER (PM2 Cron)                        │
│                                                                 │
│  LinkedIn Poster    → 9am  Mon-Fri → LinkedIn API              │
│  Social Auto-Poster → 10am Mon-Fri → Facebook + IG + Twitter   │
│  CEO Briefing       → 11pm Sunday  → Briefings/ folder         │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│         REASONING LAYER — Orchestrator (Ralph Wiggum Loop)      │
│                  Max 10 iterations per cycle                    │
│                                                                 │
│  STEP 1: Check /Needs_Action/Email/                             │
│    → create_plan() writes PLAN_EMAIL_*.md to /Plans/            │
│    → needs_approval=true  → /Pending_Approval/Email/            │
│    → needs_approval=false → /Done/Email/                        │
│    → log_to_odoo() → activity note created in Odoo             │
│                                                                 │
│  STEP 2: Check /Needs_Action/WhatsApp/                          │
│    → create_plan() writes PLAN_WHATSAPP_*.md to /Plans/         │
│    → always → /Pending_Approval/WhatsApp/                       │
│    → log_to_odoo() → activity note created in Odoo             │
│                                                                 │
│  STEP 3: Check /Pending_Approval/Email/                         │
│    → File in /Approved/Email/ → Send email via MCP (port 3005) │
│    → File in /Rejected/ → Move to rejected, log action          │
│                                                                 │
│  STEP 4: Update Dashboard.md                                    │
│    → Live counts updated, timestamp refreshed                   │
│                                                                 │
│  STEP 5: Check completion                                       │
│    → All queues empty → Exit loop                              │
│    → Items remain → Next iteration                             │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (MCP Servers)                   │
│                                                                 │
│  Email MCP (port 3005)                                          │
│  → Sends actual email via nodemailer                            │
│  → Moves file to /Done/Email/                                   │
│  → Logs to /Logs/YYYY-MM-DD.json                               │
│                                                                 │
│  Odoo MCP (port 3006)                                           │
│  → Logs Gmail and WhatsApp activities as Odoo notes            │
│  → Pulls invoice and revenue data for CEO Briefing             │
│  → Supports: partner search, invoice search, create invoice    │
│                                                                 │
│  Social Media (direct API calls)                                │
│  → Facebook Graph API  → page post                             │
│  → Instagram Graph API → feed post                             │
│  → Twitter API v2      → tweet                                 │
│  → LinkedIn API v2     → professional post                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              CEO WEEKLY BRIEFING (Sunday 11pm)                  │
│                                                                 │
│  Reads:                                                         │
│  → /Done/ folder — counts tasks completed this week            │
│  → /Logs/ folder — counts actions logged                       │
│  → /Plans/ folder — counts plans created                       │
│  → Business_Goals.md — revenue targets and KPIs               │
│  → Odoo MCP (port 3006) — live revenue and invoice data        │
│                                                                 │
│  Writes:                                                        │
│  → /Briefings/YYYY-MM-DD_Monday_Briefing.md                    │
│  → Dashboard.md Recent Activity section updated                │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD (Obsidian)                         │
│                                                                 │
│  Dashboard.md  → Live counts, last checked, recent activity     │
│  VaultOS       → Web dashboard on Vercel                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Recovery — Graceful Degradation

```
Any failure → Does NOT crash — handles gracefully

Email send fails    → File stays in Pending_Approval
Social post fails   → Draft saved to Pending_Approval/
                      3 retry attempts: 2s → 4s → 8s (exponential backoff)
Odoo offline        → CEO Briefing writes "Odoo offline" note
Token expired       → Draft saved, error written to logs
WhatsApp offline    → PM2 auto-restarts the watcher
API rate limited    → Retry with backoff, then save to pending
```

---

## PM2 Processes — Gold Tier

| ID | Name | Type | Schedule | Port |
|----|------|------|----------|------|
| 0 | gmail-watcher | Continuous | Every 2 min | — |
| 1 | whatsapp-watcher | Continuous | Every 30 sec | — |
| 2 | filesystem-watcher | Continuous | Realtime | — |
| 3 | orchestrator | Continuous | Every 5 sec | — |
| 4 | mcp-email-server | Continuous | Always on | 3005 |
| 5 | linkedin-poster | Cron | 9am Mon-Fri | — |
| 6 | odoo-mcp-server | Continuous | Always on | 3006 |
| 7 | ceo-briefing | Cron | Sunday 11pm | — |
| 8 | social-auto-poster | Cron | 10am Mon-Fri | — |

```bash
# Fresh start all processes
pm2 kill
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
pm2 start Setup/ecosystem.config.js
pm2 save
```

---

## Obsidian — What to Check Where

### Dashboard.md (root folder)
- Live processing counts (auto-updated by orchestrator)
- Recent Activity log
- System health status
- MCP server status

### Email tracking
```
Needs_Action/Email/      → New emails waiting to be processed
Pending_Approval/Email/  → Emails waiting for your approval
Approved/Email/          → Emails you approved
Done/Email/              → Fully processed and sent
```

### WhatsApp tracking
```
Needs_Action/WhatsApp/      → New messages detected
Pending_Approval/WhatsApp/  → Awaiting your approval
Done/WhatsApp/              → Processed messages
```

### AI Plans (one per email/WhatsApp)
```
Plans/PLAN_EMAIL_*.md     → Reasoning plan for each email
Plans/PLAN_WHATSAPP_*.md  → Reasoning plan for each message
```
Each plan contains:
- Who the message is from
- Category detected (Payment, Client, Project, Event, Urgent)
- Priority level
- Steps taken
- Decision: Auto-Processed or Requires Approval

### CEO Briefing
```
Briefings/YYYY-MM-DD_Monday_Briefing.md
```
Contains:
- Weekly revenue pulled from Odoo
- Task counts (emails, WhatsApp, files)
- Social posts published
- Active projects status
- Proactive suggestions

### Audit Logs
```
Logs/log_YYYY-MM-DD.json           → All actions in JSON format
Logs/social_summary_YYYY-MM-DD.md  → Daily social media summary
```

### Social Media Results
```
Done/FACEBOOK_POST_*.md       → Successfully posted to Facebook
Done/TWITTER_POST_*.md        → Successfully posted to Twitter
Done/LINKEDIN_POSTED_*.md     → Successfully posted to LinkedIn
Pending_Approval/FACEBOOK_POST_*.md  → Failed posts for manual review
Pending_Approval/LINKEDIN_POST_*.md  → LinkedIn drafts (no token yet)
```

### Business Goals
```
Business_Goals.md → Revenue targets, active projects, KPIs
```

---

## Odoo Links (localhost:8069)

| Page | URL |
|------|-----|
| Home | http://localhost:8069 |
| Invoices | http://localhost:8069/odoo/accounting/customer-invoices |
| Contacts/Partners | http://localhost:8069/odoo/contacts |
| AI Activity Notes | http://localhost:8069/odoo/contacts/1 |
| Accounting Dashboard | http://localhost:8069/odoo/accounting |

**Login credentials:**
- Email: humaizaasghar@gmail.com
- Password: 123Ai_emply

**What shows in Odoo:**
- Every Gmail email processed → appears as a note on Company (Contacts → My Company)
- Every WhatsApp message → appears as a note
- Invoices created by AI Employee → visible in Invoicing module

---

## Social Media Status

| Platform | Status | Schedule | Action Required |
|----------|--------|----------|-----------------|
| Facebook | Working | 10am Mon-Fri | None — live posting |
| Instagram | Token invalid | 10am Mon-Fri | Generate new token from Facebook Developer |
| Twitter/X | Credits depleted | 10am Mon-Fri | Resets monthly — auto-resumes |
| LinkedIn | Token pending | 9am Mon-Fri | Add token to .env file |

### Get Instagram token:
1. Go to `https://developers.facebook.com/apps`
2. Your app → Instagram Basic Display → Generate Token
3. Update `.env`: `INSTAGRAM_USER_TOKEN=your_new_token`

### Get LinkedIn token:
See: `hackathon_docs/bronze_silver_workflow.md` → LinkedIn Token Setup section

---

## All Gold Tier Work Done

### New Scripts Created
| File | Purpose |
|------|---------|
| `Social_Media/linkedin_poster.py` | LinkedIn auto-post, cron 9am Mon-Fri |
| `Social_Media/social_auto_poster.py` | Facebook + Instagram + Twitter, cron 10am Mon-Fri |
| `System/ceo_briefing.py` | Weekly CEO briefing with live Odoo data |
| `watchers_gmail/gmail_auth.py` | Gmail OAuth2 token setup tool |

### Modified Scripts
| File | What Changed |
|------|-------------|
| `System/orchestrator.py` | Plan.md creation, Odoo activity logging, retry logic added |
| `Accounting/odoo_mcp_server.js` | `/log-activity` endpoint added for AI Employee events |
| `Setup/ecosystem.config.js` | social-auto-poster, odoo-mcp-server, ceo-briefing added |
| `Dashboard.md` | Live status section added, LinkedIn row added |
| `.env` | All tokens consolidated in one file |

### Key Folders
| Folder | Purpose |
|--------|---------|
| `Plans/` | AI-generated reasoning plan per email/WhatsApp |
| `Briefings/` | Monday morning CEO briefings |
| `Logs/` | JSON audit trail and social media summaries |
| `Done/` | Completed tasks (Email/, WhatsApp/, Files/) |
| `Pending_Approval/` | Items waiting for human review |

---

## Quick Commands

```bash
# Generate CEO Briefing manually
python System/ceo_briefing.py

# Test social media poster manually
python Social_Media/social_auto_poster.py

# Test LinkedIn poster manually
python Social_Media/linkedin_poster.py

# Test Odoo MCP connection
curl http://localhost:3006/health
curl -X POST http://localhost:3006/search-invoices -H "Content-Type: application/json" -d "{}"

# View logs
pm2 logs orchestrator --lines 30
pm2 logs social-auto-poster --lines 20
pm2 logs ceo-briefing --lines 20
pm2 logs odoo-mcp-server --lines 20
```

---

## Gold Tier Achievement Checklist

- [x] 3 Watchers running 24/7 (Gmail, WhatsApp, Filesystem)
- [x] Orchestrator with Ralph Wiggum loop (max 10 iterations)
- [x] Plan.md auto-created for every email and WhatsApp message
- [x] Odoo Community running locally + MCP server integrated (JSON-RPC)
- [x] Gmail and WhatsApp activities logged to Odoo dashboard
- [x] Facebook auto-posting — live and working
- [x] CEO Briefing with live Odoo revenue data (Sunday 11pm)
- [x] Error recovery with 3x retry and exponential backoff
- [x] Comprehensive audit logs (JSON files + Odoo notes)
- [x] 15 Agent Skills in `.claude/skills/`
- [x] Multiple MCP servers: Email (3005) + Odoo (3006)
- [ ] Instagram — needs new token from Facebook Developer Portal
- [ ] Twitter — credits depleted, resumes automatically next month
- [ ] LinkedIn — add token to `.env` when ready
