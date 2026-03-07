# Platinum Tier — Demo Guide (Step by Step)

---

## Demo Setup — Before You Start

Open these windows/tabs FIRST:

| What | Where |
|------|-------|
| Obsidian Vault | Open `F:/AI_Employee_Vault/AI_Employee_Vault - Copy` in Obsidian |
| Dashboard | Obsidian -> Dashboard.md |
| Odoo | http://localhost:8069 |
| PM2 Terminal | CMD -> `pm2 status` |
| Cloud VM | CMD -> `ssh -i C:\Users\km\.ssh\ai_employee_cloud.key ubuntu@80.225.222.19` |

---

## DEMO SCRIPT — Platinum Flow

### STEP 1 — Show the System is Running (30 seconds)

Open CMD and run:
```
pm2 status
```

**What to say:**
"Ye AI Employee ke sab processes hain jo 24/7 chal rahe hain.
Gmail watcher har 2 minute mein emails check karta hai.
WhatsApp watcher har 30 second mein messages check karta hai.
Orchestrator sab kuch coordinate karta hai."

---

### STEP 2 — Show Cloud VM is Online (30 seconds)

Open second CMD window:
```
ssh -i C:\Users\km\.ssh\ai_employee_cloud.key ubuntu@80.225.222.19
pm2 status
```

**What to say:**
"Ye Oracle Cloud VM hai jo 24/7 on rehta hai.
Agar local machine band bhi ho, cloud pe kaam hota rehta hai.
Cloud-orchestrator drafts banata hai, local machine approve karti hai."

Then type `exit` to close SSH.

---

### STEP 3 — Show Dashboard (30 seconds)

Obsidian mein Dashboard.md open karo.

**What to say:**
"Ye AI Employee ka live dashboard hai Obsidian mein.
Har email, WhatsApp message, social media post — sab yahan track hota hai.
Orchestrator automatically counts aur timestamp update karta hai."

---

### STEP 4 — Show the Platinum Demo Flow (2 minutes)

**What to say:**
"Ab main aapko Platinum tier ka main demo dikhata hoon.
Email aata hai -> AI process karta hai -> Human approve karta hai -> Email send hoti hai."

#### 4A — Manually create a test email file:

Obsidian mein `Needs_Action/Email/` folder mein nayi file banao:

**File name:** `EMAIL_demo_test.md`

**File content:**
```
---
type: email
from: client@example.com
subject: Invoice Request
received: 2026-03-07T10:00:00
priority: high
needs_approval: true
status: pending
---

## Email Content

Hi, can you please send me the invoice for last month's project?
The amount was $1,500. Please confirm receipt.

## Suggested Actions
- [ ] Reply to confirm invoice will be sent
- [ ] Generate invoice in Odoo
```

**What to say:**
"Gmail watcher ne ye email detect ki aur Needs_Action mein save ki."

---

#### 4B — Wait for Orchestrator (or show Plans folder):

Obsidian mein `Plans/` folder open karo — PLAN_EMAIL_*.md file dikhao.

**What to say:**
"Orchestrator ne ye email padhi, reasoning ki, aur ek Plan.md file banai.
Plan mein likha hai: kaun hai, kya karna hai, approval chahiye ya nahi."

---

#### 4C — Show Pending Approval:

`Pending_Approval/Email/` folder open karo.

**What to say:**
"Email ko approval chahiye thi, isliye yahan aa gai.
Main as a CEO review karta hoon."

---

#### 4D — Approve the email:

File ko `Pending_Approval/Email/` se `Approved/Email/` mein move karo
(Obsidian mein drag and drop ya right-click -> Move).

**What to say:**
"Maine approve kar diya. Ab AI Employee khud email send karega via MCP server."

---

#### 4E — Show Done folder:

`Done/Email/` folder open karo — file wahan aa jaegi.

**What to say:**
"Email send ho gai. File automatically Done mein move ho gai.
Audit log bhi ban gaya Logs/ mein."

---

### STEP 5 — Show Social Media (1 minute)

`Done/` folder mein `FACEBOOK_POST_*.md` file dikhao.

**What to say:**
"AI Employee har weekday 10am pe automatically Facebook pe post karta hai.
Business goals padh ke relevant content generate karta hai.
Error aaye to 3 baar retry karta hai, phir Pending_Approval mein save karta hai."

---

### STEP 6 — Show Odoo Integration (1 minute)

Browser mein kholo: http://localhost:8069

Login:
- Email: humaizaasghar@gmail.com
- Password: 123Ai_emply

Contacts -> My Company -> Chatter section dikhao.

**What to say:**
"Har email aur WhatsApp message Odoo mein automatically log hota hai.
AI Employee ne khud ye notes create ki hain."

Phir: http://localhost:8069/odoo/accounting/customer-invoices

**What to say:**
"Invoices bhi Odoo mein hain. CEO Briefing live revenue data yahan se leta hai."

---

### STEP 7 — Show CEO Briefing (30 seconds)

Obsidian mein `Briefings/` folder open karo — latest briefing file dikhao.

**What to say:**
"Har Sunday raat 11 baje AI Employee automatically CEO briefing generate karta hai.
Weekly revenue, completed tasks, social posts — sab ek jagah."

---

### STEP 8 — Show Git Sync (30 seconds)

CMD mein:
```
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
git log --oneline -5
```

**What to say:**
"Local aur Cloud VM dono ek hi GitHub repo se sync hain.
Local changes push hote hain, Cloud automatically pull kar leta hai.
Ye Platinum tier ka Delegation via Synced Vault feature hai."

---

## Demo Summary — Kya Kya Dikha

| Feature | Tier | Dikha |
|---------|------|-------|
| Gmail Watcher | Bronze | Step 4A |
| Filesystem Watcher | Bronze | - |
| Orchestrator + Plan.md | Silver | Step 4B |
| MCP Email Send | Silver | Step 4D |
| Human-in-the-Loop | Silver | Step 4C/4D |
| LinkedIn auto-post | Silver | - |
| Odoo Integration | Gold | Step 6 |
| Facebook auto-post | Gold | Step 5 |
| CEO Briefing | Gold | Step 7 |
| Cloud VM 24/7 | Platinum | Step 2 |
| Git Sync | Platinum | Step 8 |
| Work-Zone Specialization | Platinum | Step 2+4 |
| Dashboard | All tiers | Step 3 |

---

## Quick Commands Cheat Sheet

```bash
# Check all local processes
pm2 status

# Check cloud VM
ssh -i C:\Users\km\.ssh\ai_employee_cloud.key ubuntu@80.225.222.19

# View orchestrator logs
pm2 logs orchestrator --lines 20

# Test social media poster manually
cd "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
python Social_Media/social_auto_poster.py

# Generate CEO briefing manually
python System/ceo_briefing.py

# Check git sync status
git log --oneline -5
git status
```

---

## URLs Quick Reference

| Page | URL |
|------|-----|
| Odoo Home | http://localhost:8069 |
| Odoo Invoices | http://localhost:8069/odoo/accounting/customer-invoices |
| Odoo Contacts | http://localhost:8069/odoo/contacts |
| Odoo Activity Log | http://localhost:8069/odoo/contacts/1 |
| GitHub Repo | https://github.com/HumaizaNaz/AI_Employee_Vault |

---

## Obsidian Folders Quick Reference

```
Dashboard.md              -> Live system status
Needs_Action/Email/       -> New emails waiting
Pending_Approval/Email/   -> Waiting for your approval
Approved/Email/           -> You approved these
Done/Email/               -> Completed and sent
Plans/                    -> AI reasoning plans
Briefings/                -> CEO weekly briefings
Logs/                     -> Full audit trail (JSON)
Business_Goals.md         -> Revenue targets + projects
```
