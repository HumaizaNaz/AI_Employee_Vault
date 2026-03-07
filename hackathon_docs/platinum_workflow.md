# Platinum Tier — Complete Workflow

---

## What is Platinum?

Gold tier + Always-On Cloud VM. Two agents working together:
- **Cloud Agent** (Oracle VM): Monitors 24/7, creates drafts, never sends without approval
- **Local Agent** (Your PC): Approves actions, sends emails, handles WhatsApp, payments

---

## Platinum Architecture

```
                    INTERNET
                       |
          +------------+------------+
          |                         |
   ORACLE CLOUD VM             YOUR LOCAL PC
   (80.225.222.19)             (Windows 10)
          |                         |
   +------+------+          +-------+-------+
   | cloud-       |          | Gmail Watcher |
   | orchestrator |          | WhatsApp      |
   |              |          | Watcher       |
   | health-      |          | Filesystem    |
   | monitor      |          | Watcher       |
   |              |          | Orchestrator  |
   | sync-        |          | MCP Email     |
   | manager      |          | (port 3005)   |
   +------+------+          | Odoo MCP      |
          |                  | (port 3006)   |
          |                  +-------+-------+
          |                          |
          +----------+---------------+
                     |
              GITHUB REPO
         (HumaizaNaz/AI_Employee_Vault)
                     |
              +------+------+
              | Git Sync    |
              | Local push  |
              | Cloud pull  |
              +-------------+
```

---

## Work-Zone Specialization

| Zone | Owns | Never Does |
|------|------|------------|
| Cloud | Email triage, draft replies, social post drafts | Send emails, WhatsApp, payments |
| Local | Approvals, WhatsApp session, final send/post | Cannot run 24/7 (offline sometimes) |

---

## Full Platinum Flow

```
+--------------------------------------------------+
|              PERCEPTION LAYER                    |
|                                                  |
|  LOCAL:                    CLOUD:                |
|  Gmail Watcher (2 min)     cloud-orchestrator    |
|  WhatsApp Watcher (30 sec) (checks for files     |
|  Filesystem Watcher        in Needs_Action/)      |
|       |                         |                |
|       v                         v                |
|  EMAIL_*.md             drafts written to        |
|  WHATSAPP_*.md          Pending_Approval/        |
|  FILE_*.md                                       |
+------------------+-------------------------------+
                   |
                   v (Git sync both ways)
+--------------------------------------------------+
|           OBSIDIAN VAULT (Shared via Git)        |
|                                                  |
|  /Needs_Action/Email/     <- Gmail writes here   |
|  /Needs_Action/WhatsApp/  <- WA writes here      |
|  /Plans/                  <- AI plans here       |
|  /Pending_Approval/       <- Needs human review  |
|  /Approved/               <- Human approved      |
|  /Rejected/               <- Human rejected      |
|  /Done/                   <- Completed tasks     |
|  /Logs/                   <- Full audit trail    |
|  /Briefings/              <- CEO briefings       |
+------------------+-------------------------------+
                   |
                   v
+--------------------------------------------------+
|        REASONING LAYER (Orchestrator)            |
|        Ralph Wiggum Loop (max 10 iter)           |
|                                                  |
|  1. Check /Needs_Action/Email/                   |
|     -> create Plan.md in /Plans/                 |
|     -> needs_approval=true  -> /Pending_Approval/|
|     -> needs_approval=false -> /Done/            |
|     -> log_to_odoo() -> Odoo activity note       |
|                                                  |
|  2. Check /Needs_Action/WhatsApp/                |
|     -> create Plan.md                            |
|     -> always -> /Pending_Approval/WhatsApp/     |
|                                                  |
|  3. Check /Pending_Approval/Email/               |
|     -> File in /Approved/ -> Send via MCP        |
|     -> File in /Rejected/ -> Log and move        |
|                                                  |
|  4. Update Dashboard.md                          |
|                                                  |
|  5. All queues empty? Exit. Else next iteration. |
+------------------+-------------------------------+
                   |
                   v
+--------------------------------------------------+
|           ACTION LAYER (MCP Servers)             |
|                                                  |
|  Email MCP (port 3005)                           |
|  -> Sends actual email via nodemailer            |
|  -> Moves file to /Done/Email/                   |
|  -> Logs to /Logs/YYYY-MM-DD.json               |
|                                                  |
|  Odoo MCP (port 3006)                            |
|  -> Logs Gmail + WhatsApp events as Odoo notes  |
|  -> Invoice + revenue data for CEO Briefing      |
|                                                  |
|  Social Media (direct API)                       |
|  -> Facebook Graph API -> page post              |
|  -> Instagram Graph API -> feed post             |
|  -> Twitter API v2 -> tweet                      |
|  -> LinkedIn API v2 -> professional post         |
+--------------------------------------------------+
```

---

## Scheduling Layer (PM2)

### Local Processes

| ID | Name | Type | Schedule |
|----|------|------|----------|
| 0 | gmail-watcher | Continuous | Every 2 min |
| 1 | whatsapp-watcher | Continuous | Every 30 sec |
| 2 | filesystem-watcher | Continuous | Realtime |
| 3 | orchestrator | Continuous | Every 5 sec |
| 4 | mcp-email-server | Continuous | Always on (port 3005) |
| 5 | linkedin-poster | Cron | 9am Mon-Fri |
| 6 | odoo-mcp-server | Continuous | Always on (port 3006) |
| 7 | ceo-briefing | Cron | Sunday 11pm |
| 8 | social-auto-poster | Cron | 10am Mon-Fri |

### Cloud Processes (Oracle VM)

| ID | Name | Type | Purpose |
|----|------|------|---------|
| 0 | cloud-orchestrator | Continuous | Processes vault files on cloud |
| 1 | health-monitor | Continuous | Monitors VM health, writes status |
| 2 | sync-manager | Continuous | Git pull every 5 min from GitHub |

---

## Security Rules (Platinum)

```
What syncs via Git:        What NEVER syncs:
- Markdown files (.md)     - .env (tokens, passwords)
- Python scripts           - token.json (Gmail OAuth)
- Config files             - WhatsApp session files
- Logs (JSON)              - Banking credentials
- Plans and Briefings      - Payment tokens
```

---

## Claim-by-Move Rule (Multi-Agent Coordination)

Prevents Cloud and Local from processing the same file:

```
File arrives in /Needs_Action/Email/
         |
         v
First agent to move it to /In_Progress/<agent>/
         |
   OWNS the task
         |
Other agent sees it in /In_Progress/ -> SKIPS it
         |
         v
Processing complete -> moved to /Done/ or /Pending_Approval/
```

---

## Platinum Demo Flow (Minimum Passing Gate)

```
Scenario: Email arrives while Local PC is off

1. Email arrives in Gmail
         |
         v
2. Cloud sync-manager pulls latest vault from GitHub

3. cloud-orchestrator detects EMAIL_*.md in Needs_Action/

4. cloud-orchestrator creates:
   - Plans/PLAN_EMAIL_*.md       (reasoning plan)
   - Pending_Approval/Email/EMAIL_*.md  (approval request)

5. cloud-orchestrator pushes to GitHub

6. LOCAL PC comes back online

7. sync-manager (local) pulls from GitHub
   -> Pending_Approval/Email/ has new file

8. You (CEO) see it in Obsidian
   -> Review the plan
   -> Move file to /Approved/Email/

9. Local orchestrator detects Approved file
   -> Calls Email MCP (port 3005)
   -> Email is SENT

10. File moves to /Done/Email/
    Log written to /Logs/YYYY-MM-DD.json
    Odoo activity note created
    Dashboard.md updated
```

---

## Error Recovery

```
Email send fails    -> File stays in Pending_Approval (retry next cycle)
Social post fails   -> 3 retry attempts: 2s -> 4s -> 8s backoff
                    -> Draft saved to Pending_Approval/ after 3 fails
Odoo offline        -> CEO Briefing writes "Odoo offline" note
Token expired       -> Draft saved, error written to Logs/
WhatsApp offline    -> PM2 auto-restarts watcher
Cloud VM reboots    -> PM2 startup auto-starts all processes
Git conflict        -> sync-manager resolves with fast-forward only
```

---

## Key Files and Folders

| File/Folder | Purpose |
|-------------|---------|
| `Dashboard.md` | Live counts, last checked, recent activity |
| `Business_Goals.md` | Revenue targets, projects, KPIs |
| `Company_Handbook.md` | Rules of engagement for AI Employee |
| `System/orchestrator.py` | Main brain — Ralph Wiggum loop |
| `System/ceo_briefing.py` | Sunday briefing generator |
| `Social_Media/linkedin_poster.py` | LinkedIn 9am Mon-Fri |
| `Social_Media/social_auto_poster.py` | Facebook+Instagram+Twitter 10am |
| `watchers_gmail/gmail_watcher.py` | Gmail monitoring |
| `watchers_whatsapp/whatsapp_watcher.py` | WhatsApp monitoring |
| `watchers/filesystem_watcher.py` | File drop monitoring |
| `watchers_gmail/mcp/mcp_email.js` | Email MCP server (port 3005) |
| `Accounting/odoo_mcp_server.js` | Odoo MCP server (port 3006) |
| `Setup/ecosystem.config.js` | PM2 all processes config |
| `Setup/cloud_ecosystem.config.js` | PM2 cloud processes config |

---

## Start Commands

### Local (Windows)
```bash
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
pm2 start Setup/ecosystem.config.js
pm2 save
pm2 status
```

### Cloud VM
```bash
ssh -i C:\Users\km\.ssh\ai_employee_cloud.key ubuntu@80.225.222.19
cd ~/ai-employee-vault
pm2 start Setup/cloud_ecosystem.config.js
pm2 save
pm2 status
```

### Git Sync (Local -> Cloud)
```bash
# Local: commit and push
git add .
git commit -m "Update"
git push origin master

# Cloud: pull (sync-manager does this automatically every 5 min)
git pull origin master
```
