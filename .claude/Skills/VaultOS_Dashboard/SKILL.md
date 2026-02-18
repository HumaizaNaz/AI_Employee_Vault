# VaultOS Dashboard Skill

## Overview
VaultOS is the Next.js 14 web dashboard for the AI Employee system. It provides a live UI for monitoring all vault activity, managing approvals, posting to social media, viewing accounting data, and checking cloud health — accessible from any browser, anywhere in the world.

## Capabilities
- View live dashboard with stats (emails, approvals, WhatsApp, cloud status)
- Approve or reject pending actions from any browser (mobile-friendly)
- Post to Facebook, Instagram, and LinkedIn directly from UI
- View and search email inbox from vault
- View WhatsApp messages and mark as done
- Create and view Odoo invoices
- Monitor cloud VM health (CPU, memory, disk, PM2 processes)
- View audit logs

## Technical Implementation
- Framework: Next.js 14 with TypeScript
- Styling: Tailwind CSS + shadcn/ui components
- Data: Custom `useData` hook with 30-second auto-refresh
- All API routes use `export const dynamic = 'force-dynamic'` (no static generation)
- Deployed on Vercel: `https://vaultos-two.vercel.app`
- Local dev: `http://localhost:3000`

## Pages & API Routes

| Page | Route | API | Data Source |
|------|-------|-----|-------------|
| Dashboard | `/` | `/api/sse` | All vault folders |
| Emails | `/emails` | `/api/emails` | `/Needs_Action/Email/` |
| Approvals | `/approvals` | `/api/approvals` | `/Pending_Approval/` |
| Social Media | `/social` | `/api/social` | Facebook/Instagram Graph API |
| Accounting | `/accounting` | `/api/accounting` | Odoo MCP localhost:3006 |
| Cloud | `/cloud` | `/api/cloud` | PM2 + health_report.md |
| WhatsApp | `/whatsapp` | `/api/whatsapp` | `/Needs_Action/WhatsApp/` |
| Logs | `/logs` | `/api/logs` | `/Logs/*.json` |

## Input Parameters
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Facebook posting token
- `INSTAGRAM_ACCOUNT_ID`: Instagram business account ID
- `INSTAGRAM_USER_TOKEN`: Instagram posting token
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn token (pending)
- `LINKEDIN_MEMBER_URN`: LinkedIn member ID (pending)

## Activation Triggers
- Run locally: `cd vaultos && npm run dev`
- Access live: `https://vaultos-two.vercel.app`
- Auto-refreshes data every 30 seconds on all pages

## Dependencies
- Node.js 20+ and npm
- All env vars in `vaultos/.env.local`
- Vercel account (humaizanaz) for cloud deployment
- Local vault folder structure for file-based APIs

## Security Considerations
- `.env.local` gitignored — never committed
- Env vars stored securely in Vercel dashboard
- File-based APIs (emails, approvals) only work locally — return empty on Vercel (by design)
- Social media posting works on both local and Vercel

## Integration Points
- Reads from all vault folders via Next.js API routes
- Approvals page calls POST `/api/approvals` to move files
- Social page calls POST `/api/social` to post to platforms
- Accounting page calls `/api/accounting` → Odoo MCP proxy
- Sidebar shows live badge counts (emails, approvals, WhatsApp)

## Error Handling
- Missing vault directories → returns empty arrays gracefully
- Odoo MCP not running → shows empty accounting data
- Social token expired → shows error in post result card
- PM2 not available → cloud page uses mock fallback data

## Deployment
```bash
# Local
cd vaultos && npm run dev

# Deploy to Vercel
vercel deploy --yes --prod
```
