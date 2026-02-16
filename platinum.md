# Platinum Tier: Always-On Cloud + Local Executive (Production-ish AI Employee)

## Overview
The Platinum Tier represents the most advanced level of the Personal AI Employee hackathon, focusing on creating a production-ready system with both cloud and local components working in coordination. This tier requires 60+ hours of development time.

## Core Requirements

### 1. Always-On Cloud Deployment
- Run the AI Employee on Cloud 24/7 (always-on watchers + orchestrator + health monitoring)
- Deploy on a Cloud VM (Oracle/AWS/etc.) - Oracle Cloud Free VMs can be used (subject to limits/availability)
- Implement health monitoring to ensure system reliability

### 2. Work-Zone Specialization
Establish clear domain ownership between Cloud and Local components:

#### Cloud Responsibilities:
- Email triage
- Draft replies to emails
- Social post drafts/scheduling (draft-only)
- Requires Local approval before send/post

#### Local Responsibilities:
- Approvals
- WhatsApp session management
- Payments/banking operations
- Final "send/post" actions

### 3. Delegation via Synced Vault (Phase 1)

#### Communication Channels:
Agents communicate by writing files into specific folders:
- `/Needs_Action/<domain>/`
- `/Plans/<domain>/`
- `/Pending_Approval/<domain>/`

#### Prevent Double-Work Mechanisms:
- `/In_Progress/<agent>/` claim-by-move rule
- Single-writer rule for Dashboard.md (Local)
- Cloud writes updates to `/Updates/` (or `/Signals/`), and Local merges them into Dashboard.md

#### Sync Mechanism:
- For Vault sync (Phase 1) use Git (recommended) or Syncthing
- Claim-by-move rule: first agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it; other agents must ignore it

### 4. Security Framework
- Vault sync includes only markdown/state files
- Secrets never sync (.env, tokens, WhatsApp sessions, banking credentials)
- Cloud never stores or uses WhatsApp sessions, banking credentials, or payment tokens

### 5. Advanced Odoo Integration
- Deploy Odoo Community on a Cloud VM (24/7) with HTTPS, backups, and health monitoring
- Integrate Cloud Agent with Odoo via MCP for draft-only accounting actions
- Implement Local approval for posting invoices/payments

### 6. Optional A2A Upgrade (Phase 2)
- Replace some file handoffs with direct A2A (Agent-to-Agent) messages later
- Keep the vault as the audit record

## Platinum Demo Requirement (Minimum Passing Gate)
Email arrives while Local is offline → Cloud drafts reply + writes approval file → when Local returns, user approves → Local executes send via MCP → logs → moves task to `/Done`.

## Prerequisites
- Complete all Gold Tier requirements
- Cloud VM access and configuration knowledge
- Advanced understanding of synchronization protocols
- Security best practices for distributed systems

## Success Metrics
- System operates continuously without manual intervention
- Seamless handoff between cloud and local components
- Proper security isolation maintained
- All Platinum demo criteria met