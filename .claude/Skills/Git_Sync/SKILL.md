# Git Sync Skill

## Overview
The Git Sync skill manages automated vault synchronization between Cloud VM and Local PC using Git. Cloud pushes drafts and signals every 5 minutes; Local pulls and merges changes. Strict security rules ensure no credentials or secrets ever enter the repository.

## Capabilities
- Auto-commit and push new vault files from Cloud every 5 minutes
- Local pulls cloud changes (drafts, signals, logs)
- Security filtering: only `.md` and `.json` files synced
- Protect secrets: `.env`, tokens, sessions never synced
- Conflict resolution via single-writer rules
- Provide audit trail via Git history

## Technical Implementation
- Script: `sync_manager.py`
- Runs as PM2 process: `sync-manager`
- Cloud: `git add`, `git commit`, `git push` every 5 minutes
- Local: `git pull` to fetch cloud changes
- GitHub repo: `https://github.com/HumaizaNaz/AI_Employee_Vault`
- Uses `.gitsyncignore` pattern for extra secret protection

## Sync Rules
| File Type | Synced? |
|-----------|---------|
| `.md` markdown files | ✅ Yes |
| `.json` log files | ✅ Yes |
| `.env` files | ❌ NEVER |
| Access tokens | ❌ NEVER |
| WhatsApp sessions | ❌ NEVER |
| Banking credentials | ❌ NEVER |
| `.next/` build folder | ❌ No |
| `node_modules/` | ❌ No |

## Input Parameters
- None required — runs autonomously via PM2
- Git credentials configured on both Cloud VM and Local

## Output Format
Commits appear in GitHub with messages like:
```
[Cloud] Auto-sync 2026-02-18T16:30:00Z
- Added: Needs_Action/Email/EMAIL_xyz.md
- Added: Signals/health_report.md
- Added: Logs/2026-02-18.json
```

## Activation Triggers
- Runs continuously via PM2 (every 5 minutes)
- Manual sync: `python sync_manager.py --once`
- Local pull: `git pull origin master`

## Dependencies
- Git installed on both Cloud VM and Local PC
- GitHub repository with push/pull access
- PM2 running `sync-manager` process
- `.gitignore` properly configured

## Security Considerations
- `.gitignore` blocks: `.env*`, `*.pem`, `node_modules/`, `.next/`, `sessions/`
- Double protection: `.gitsyncignore` in sync_manager.py
- Cloud never stores or syncs: WhatsApp session, banking creds, payment tokens
- All secrets stay on each machine locally only

## Integration Points
- Cloud orchestrator pushes drafts → Local agent pulls and processes
- `/Signals/` folder used for Cloud → Local communication
- `/Updates/` folder: Cloud writes status, Local merges to Dashboard.md
- Single-writer rule: only Local writes to Dashboard.md directly

## Work-Zone Sync Rules (Platinum)
- Cloud pushes to: `/Needs_Action/`, `/Drafts/`, `/Signals/`, `/Logs/`
- Local pushes to: `/Done/`, `/Approved/`, `/Rejected/`, `Dashboard.md`
- Claim-by-move: first agent to move file to `/In_Progress/` owns it

## Error Handling
- Push conflict → pull first, then push
- Network unavailable → queue commits locally, push when restored
- Auth failure → log error, alert human via signal file
- Large file detected → skip, log warning

## Current Status
- GitHub: ✅ https://github.com/HumaizaNaz/AI_Employee_Vault
- Auto-sync: ✅ Running via PM2 (sync-manager)
- Last push: 2026-02-18 (LinkedIn integration + README)
