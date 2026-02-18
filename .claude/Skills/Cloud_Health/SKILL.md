# Cloud Health Monitor Skill

## Overview
The Cloud Health Monitor skill tracks the health of all AI Employee processes — both local (Windows PC) and cloud (Oracle VM). It monitors CPU, memory, disk, PM2 processes, and writes health reports to `/Signals/health_report.md` for Local agent to read.

## Capabilities
- Monitor all PM2 processes (online/stopped/errored)
- Track system resources: CPU %, memory used/total, disk used/total
- Auto-restart failed processes via PM2
- Write health reports to `/Signals/health_report.md`
- Alert via signal file if critical issue detected
- Display live health data in VaultOS `/cloud` page

## Technical Implementation
- Script: `health_monitor.py`
- Runs as PM2 process: `health-monitor`
- Checks PM2 status via: `pm2 list --json`
- Reads system stats via `psutil` Python library
- Writes report to `/Signals/health_report.md` every 5 minutes
- VaultOS reads report via `/api/cloud` route
- Cloud VM IP: 80.225.222.19 (Oracle Free Tier)

## Input Parameters
- None required — runs autonomously
- Config in `cloud_ecosystem.config.js`

## Output Format — health_report.md
```markdown
---
generated: [ISO timestamp]
status: healthy/warning/critical
---
## System Health
- CPU: [%]
- Memory: [used MB] / [total MB]
- Disk: [used GB] / [total GB]

## PM2 Processes
| Name | Status | CPU | Memory | Restarts |
|------|--------|-----|--------|----------|
| cloud-orchestrator | online | 0.1% | 45 MB | 0 |
| health-monitor | online | 0.0% | 38 MB | 0 |
| sync-manager | online | 0.0% | 41 MB | 0 |

## Alerts
[Any critical issues listed here]
```

## Activation Triggers
- Runs continuously via PM2 (auto-start on boot)
- VaultOS `/cloud` page reads report on load and every 30 seconds
- Critical alert → writes to `/Signals/alert_[timestamp].md`

## Dependencies
- PM2 installed globally
- Python `psutil` library
- `health_monitor.py` script
- `/Signals/` folder in vault

## Security Considerations
- Health reports contain no credentials or sensitive data
- Only system metrics and process names synced
- Alert signals are plain markdown files

## Integration Points
- VaultOS `/api/cloud` reads health report
- Dashboard shows PM2 process table and resource bars
- Git sync picks up health reports for Local agent visibility
- Cloud orchestrator checks health before processing tasks

## Error Handling
- PM2 not available → use mock data (VaultOS fallback)
- Process crashed → PM2 auto-restarts, health report shows restart count
- Disk full alert → written to `/Signals/` immediately
- Script itself monitored by PM2 for auto-restart

## Current Status
- Cloud VM: ✅ Online — Oracle Free Tier (80.225.222.19)
- PM2 Processes: cloud-orchestrator, health-monitor, sync-manager
- Local PM2: gmail-watcher, whatsapp-watcher, odoo-mcp, orchestrator
