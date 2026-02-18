# AI Employee Vault — Platinum Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A fully autonomous Digital FTE (Full-Time Equivalent) built with Claude Code, Obsidian, Python, and Next.js. It monitors Gmail and WhatsApp 24/7, drafts replies, posts to social media, manages accounting via Odoo, and presents everything through a live web dashboard — all with human approval before any sensitive action is taken.

---

## Live Demo

**VaultOS Dashboard:** [https://vaultos-two.vercel.app](https://vaultos-two.vercel.app)

---

## Tier Achieved: Platinum ✓

| Tier | Status |
|------|--------|
| Bronze — Foundation | ✅ Complete |
| Silver — Functional Assistant | ✅ Complete |
| Gold — Autonomous Employee | ✅ Complete |
| Platinum — Always-On Cloud + Local Executive | ✅ Complete |

---

## Architecture Overview

```
LOCAL (Your PC)                        CLOUD (Vercel + Oracle VM)
├── WhatsApp Watcher (Playwright)      ├── VaultOS Next.js Dashboard (Vercel)
├── Human Approvals (final send)       ├── Gmail Watcher (24/7)
├── Banking / Payments                 ├── Cloud Orchestrator (draft-only)
├── Dashboard.md (single-writer)       ├── Social Media API (Facebook/Instagram)
├── Odoo MCP Server (:3006)            ├── Health Monitor
└── Git pull / push                    └── Git push (markdown only)

SYNC: Git — Cloud pushes drafts/signals → Local pulls, approves, executes
```

### Core Components

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Brain | Claude Code (claude-sonnet-4-6) | Reasoning, planning, task execution |
| Memory / GUI | Obsidian (local Markdown) | Vault, dashboard, knowledge base |
| Web UI | Next.js 14 + Tailwind CSS (Vercel) | Live dashboard & social posting |
| Watchers | Python 3.11 | Gmail + WhatsApp + filesystem monitoring |
| Hands | MCP Servers (Node.js) | Email send, Odoo actions |
| Accounting | Odoo 18 Community + JSON-RPC MCP | Invoice management, partner tracking |
| Social Media | Facebook Graph API v18 + Instagram API | Post directly from UI or CLI |
| Process Manager | PM2 | Keep all processes alive, auto-restart |
| Sync | Git (GitHub) | Cloud ↔ Local vault sync |

---

## Features

### Perception (Watchers)
- **Gmail Watcher** — Monitors inbox for important emails, saves them as `.md` files in `/Needs_Action/Email/`
- **WhatsApp Watcher** — Uses Playwright to detect messages with keywords (urgent, invoice, payment), saves to `/Needs_Action/WhatsApp/`
- **Filesystem Watcher** — Monitors drop folders for new files to process

### Reasoning (Claude Code)
- Reads `/Needs_Action/`, thinks, creates `Plan.md` files
- Drafts email replies in `/Drafts/`
- Creates approval requests in `/Pending_Approval/`
- **Ralph Wiggum Loop** — Stop hook keeps Claude iterating until tasks are fully complete

### Human-in-the-Loop (HITL)
- All sensitive actions require approval — Claude writes an approval file, never acts directly
- Move file to `/Approved/` → action executes
- Move file to `/Rejected/` → action cancelled
- VaultOS dashboard lets you approve/reject from any browser

### Action Layer (MCP Servers)
- **Email MCP** — Send drafted emails via Gmail API
- **Odoo MCP** (:3006) — Create/view invoices, manage partners via JSON-RPC
- **Social Media API** — Post to Facebook, Instagram, LinkedIn (token pending) directly from VaultOS

### Accounting (Odoo 18 Community)
- Self-hosted locally at `localhost:8069`
- Draft-only policy: AI creates invoice drafts, human approves before posting
- Live invoice table, partner management, revenue stats in VaultOS

### Social Media

| Platform | Status |
|----------|--------|
| Facebook | ✅ Connected — posts via Graph API |
| Instagram | ✅ Connected — two-step container/publish flow |
| LinkedIn | 🔄 Token pending — code fully ready |
| Twitter / X | ⏳ Credits reset soon — auth verified |

### VaultOS Web Dashboard
Built with Next.js 14, deployed on Vercel:
- **Dashboard** — Live stats: emails, approvals, WhatsApp, cloud status, bar chart
- **Emails** — View all `Needs_Action/Email/` files
- **Approvals** — Approve or reject pending actions from any browser
- **Social Media** — Post to Facebook/Instagram/LinkedIn from anywhere (mobile-friendly)
- **Accounting** — Live Odoo invoice data, create invoices
- **Cloud** — PM2 process health, CPU/memory/disk
- **WhatsApp** — View and process incoming messages
- **Logs** — Audit trail of all AI actions

### Cloud Deployment (Platinum)
- Cloud orchestrator runs in **draft-only mode** — never sends directly
- `/Signals/` folder for Cloud → Local communication
- Git-based sync (only `.md` and `.json` — secrets never sync to cloud)
- Health monitor auto-restarts failed processes via PM2
- Oracle Cloud Free Tier ready (`deploy_cloud.sh` included)

---

## Project Structure

```
AI_Employee_Vault/
├── vaultos/                     # Next.js web dashboard (live on Vercel)
│   ├── src/app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── social/              # Social media posting
│   │   ├── approvals/           # HITL approvals
│   │   ├── emails/              # Email inbox
│   │   ├── accounting/          # Odoo invoices
│   │   ├── cloud/               # System health
│   │   ├── whatsapp/            # WhatsApp messages
│   │   ├── logs/                # Audit logs
│   │   └── api/                 # Next.js API routes (all force-dynamic)
│   └── .env.local               # Tokens (gitignored)
│
├── Needs_Action/                # Watcher output — pending items
│   ├── Email/
│   └── WhatsApp/
├── Pending_Approval/            # HITL queue
├── Approved/                    # Approved → MCP executes
├── Rejected/                    # Rejected actions
├── Drafts/                      # AI-drafted replies
├── Done/                        # Completed tasks
├── Logs/                        # Audit logs (JSON)
├── Signals/                     # Cloud → Local signals
├── Updates/                     # Cloud status updates
│
├── orchestrator.py              # Main local orchestrator
├── cloud_orchestrator.py        # Cloud draft-only orchestrator
├── gmail_watcher.py             # Gmail monitoring
├── whatsapp_watcher.py          # WhatsApp monitoring
├── health_monitor.py            # Process health checks
├── sync_manager.py              # Git-based vault sync
├── deploy_cloud.sh              # One-command Oracle VM deploy
├── platinum_demo_test.py        # E2E demo verification
│
├── ecosystem.config.js          # PM2 local processes
├── cloud_ecosystem.config.js    # PM2 cloud processes
│
├── Accounting/
│   └── odoo_mcp_server.js       # Odoo MCP server (port 3006)
│
├── Dashboard.md                 # Real-time system status (Obsidian)
├── Company_Handbook.md          # AI Employee rules of engagement
└── README.md                    # This file
```

---

## Setup

### Prerequisites
- Node.js 20+ LTS
- Python 3.11+
- PM2 (`npm install -g pm2`)
- Odoo 18 Community (local)
- Claude Code (`npm install -g @anthropic/claude-code`)
- Git

### 1. Clone the repo
```bash
git clone https://github.com/HumaizaNaz/AI_Employee_Vault.git
cd AI_Employee_Vault
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install VaultOS dependencies
```bash
cd vaultos
npm install
```

### 4. Configure environment variables

**`Accounting/.env`**
```env
ODOO_URL=http://localhost:8069
ODOO_DB=ai_emp
ODOO_USERNAME=your@email.com
ODOO_PASSWORD=yourpassword
ODOO_MCP_PORT=3006
```

**`vaultos/.env.local`**
```env
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=me
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_USER_TOKEN=your_token
LINKEDIN_ACCESS_TOKEN=your_token_when_ready
LINKEDIN_MEMBER_URN=your_urn_when_ready
```

### 5. Start all processes (PM2)
```bash
pm2 start ecosystem.config.js
pm2 save
```

### 6. Run VaultOS locally
```bash
cd vaultos
npm run dev
# Open http://localhost:3000
```

---

## Cloud Deployment (Oracle VM)

```bash
# On your Oracle Cloud VM (Ubuntu 22.04)
bash deploy_cloud.sh
```

Fill in your `.env` on the VM, then start cloud processes:
```bash
pm2 start cloud_ecosystem.config.js
```

---

## Security

- All secrets in `.env` files — **never committed to git**
- Vault sync only includes `.md` and `.json` files
- WhatsApp sessions, banking credentials, tokens — **never synced to cloud**
- Human-in-the-loop for all sensitive actions: email sends, payments, social posts
- Audit logging for every AI action in `/Logs/YYYY-MM-DD.json`
- Draft-only policy on cloud — Local always has final say

---

## Tech Stack

- **Claude Code** — Primary reasoning engine (claude-sonnet-4-6)
- **Next.js 14** — VaultOS web dashboard
- **Tailwind CSS + shadcn/ui** — UI components
- **Python 3.11** — Watchers and orchestrator
- **Odoo 18 Community** — Self-hosted accounting (JSON-RPC MCP)
- **PM2** — Process management and auto-restart
- **Facebook Graph API v18** — Facebook + Instagram posting
- **LinkedIn API v2** — LinkedIn posting (UGC Posts)
- **Vercel** — VaultOS cloud hosting
- **Oracle Cloud Free Tier** — Always-on VM for watchers
- **Git / GitHub** — Vault sync + version control
- **Obsidian** — Local vault GUI and dashboard

---

## Hackathon Submission

**Tier:** Platinum — Always-On Cloud + Local Executive

**Hackathon:** Personal AI Employee Hackathon 0 — Building Autonomous FTEs in 2026
by [Panaversity](https://www.youtube.com/@panaversity)

**Submit Form:** https://forms.gle/JR9T1SJq5rmQyGkGA

---

## Author

**Humaiza Naz**
- GitHub: [HumaizaNaz](https://github.com/HumaizaNaz)
- LinkedIn: [know-how-coding](https://www.linkedin.com/in/know-how-coding-undefined-2654383a5/)
- VaultOS Live: [vaultos-two.vercel.app](https://vaultos-two.vercel.app)
