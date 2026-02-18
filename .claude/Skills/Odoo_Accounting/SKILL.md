# Odoo Accounting Skill

## Overview
The Odoo Accounting skill enables the AI Employee to manage invoices, partners, and financial data via Odoo 18 Community Edition (self-hosted). It connects through a custom MCP server using Odoo's JSON-RPC API. Draft-only policy: AI creates drafts, human confirms.

## Capabilities
- Create invoice drafts in Odoo (never auto-confirm)
- Search and list existing invoices with status and amounts
- Search partners/clients by name or domain
- Calculate revenue stats (draft count, paid count, total revenue)
- Require human approval before confirming or posting any invoice
- Log all accounting actions for audit trail

## Technical Implementation
- Odoo running locally: `http://localhost:8069`
- Database: `ai_emp`
- MCP Server: `Accounting/odoo_mcp_server.js` running on port 3006 (PM2)
- JSON-RPC endpoints used:
  - `POST /web/dataset/call_kw` for model operations
  - Model: `account.move` for invoices
  - Model: `res.partner` for contacts
- VaultOS API route: `vaultos/src/app/api/accounting/route.ts`
- VaultOS UI: `/accounting` page with live invoice table and create dialog

## Input Parameters
- `partner_id`: Odoo partner ID for invoice creation
- `amount`: Invoice amount
- `description`: Invoice line description
- `ODOO_URL`: `http://localhost:8069`
- `ODOO_DB`: `ai_emp`
- `ODOO_USERNAME`: Odoo login email
- `ODOO_PASSWORD`: Odoo password

## Output Format
```markdown
---
type: accounting_action
action: create_invoice / list_invoices / search_partners
odoo_id: [returned Odoo record ID]
timestamp: [ISO timestamp]
status: draft (never confirmed without approval)
---
## Invoice Details
- Partner: [name]
- Amount: [amount]
- State: draft
- Odoo ID: [ID]
```

## Activation Triggers
- User opens VaultOS `/accounting` page (auto-loads invoices)
- User clicks "Create Invoice" in VaultOS dialog
- Orchestrator processes accounting-related file drops
- Manual invocation via `/odoo-accounting` skill

## Dependencies
- Odoo 18.0 Community installed and running on port 8069
- Database: `ai_emp` with Invoicing module installed
- PM2 running `odoo_mcp_server.js` on port 3006
- Environment variables in `Accounting/.env`

## Security Considerations
- Odoo credentials stored in `Accounting/.env` — never committed
- Draft-only policy: AI NEVER confirms/posts invoices directly
- All accounting actions require human approval
- Audit log maintained in `/Logs/`
- Odoo MCP not exposed to cloud — local only

## Integration Points
- VaultOS `/api/accounting` proxies to MCP on localhost:3006
- Dashboard shows Odoo connection status
- Orchestrator can create invoice approval files in `/Pending_Approval/`
- PM2 keeps MCP server alive with auto-restart

## Error Handling
- Odoo MCP not reachable → returns `{ error: "Odoo MCP not reachable", invoices: [], stats: {...} }`
- Auth failure → Odoo returns error, logged and shown in UI
- Module not installed → clear error about missing `account.move` model
- Network timeout → caught, empty data returned gracefully

## Current Status
- Odoo 18.0: ✅ Running on port 8069
- Database: ✅ ai_emp
- Invoicing Module: ✅ Installed
- Odoo MCP Server: ✅ Running on port 3006 (PM2)
- Test Invoices: ✅ 2 invoices created successfully
