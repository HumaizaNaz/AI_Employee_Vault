# VaultOS - Personal AI Employee Command Center

**Tagline:** *"Your AI Employee. Always On."*

A modern, dark-themed dashboard for managing your AI-powered business operations.

## Features

- 📊 **Dashboard** - Real-time overview of all systems
- 📧 **Email Queue** - Gmail integration with draft approval
- 💬 **WhatsApp Queue** - WhatsApp Business message management
- ⚠️ **Approvals** - One-click approve/reject for emails and social posts
- 📱 **Social Media** - Multi-platform posting (Facebook, Instagram, Twitter)
- 🏦 **Accounting** - Odoo 18.0 integration for invoices
- ☁️ **Cloud Status** - VM health monitoring and PM2 process management
- 📋 **Logs** - Full audit trail of all activities

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v3
- **Components:** shadcn/ui patterns
- **Icons:** Lucide React
- **Charts:** Recharts
- **Animations:** Framer Motion
- **Real-time:** Server-Sent Events (SSE)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd vaultos
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
vaultos/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── page.tsx      # Dashboard (home)
│   │   ├── approvals/    # Approvals page
│   │   ├── emails/       # Email queue
│   │   ├── whatsapp/     # WhatsApp queue
│   │   ├── social/       # Social media
│   │   ├── accounting/   # Accounting/Odoo
│   │   ├── cloud/        # Cloud status
│   │   ├── logs/         # Activity logs
│   │   └── api/          # API routes
│   ├── components/       # React components
│   │   ├── Sidebar.tsx   # Navigation sidebar
│   │   └── ui/           # UI components (cards, buttons, etc.)
│   └── lib/
│       └── utils.ts      # Utility functions
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## Color Theme - "Dark Command"

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#09090B` | Main background |
| Card | `#18181B` | Card backgrounds |
| Border | `#27272A` | Borders and dividers |
| Primary | `#6366F1` | Buttons, links, active states |
| Success | `#22C55E` | Online, done, approved |
| Warning | `#F59E0B` | Pending, approval needed |
| Danger | `#EF4444` | Errors, urgent, rejected |
| Text Primary | `#FAFAFA` | Main text |
| Text Muted | `#71717A` | Secondary text |

## API Routes

- `GET /api/emails` - Read emails from Needs_Action/Email/
- `GET /api/approvals` - Read pending approvals
- `POST /api/approvals` - Approve/reject items
- `GET /api/cloud` - Cloud VM status and PM2 processes
- `GET /api/logs` - Read activity logs
- `GET /api/sse` - Server-Sent Events for real-time updates

## Deployment

### Oracle Cloud VM

```bash
# Install PM2 globally
npm install -g pm2

# Build the app
npm run build

# Start with PM2
pm2 start npm --name vaultos -- start
```

Access at: `http://YOUR_VM_IP:3000`

## Integration with Vault

VaultOS reads from your Obsidian-style vault:

- `Needs_Action/Email/` - Email drafts needing action
- `Pending_Approval/Email/` - Email drafts awaiting approval
- `Pending_Approval/Social/` - Social media posts awaiting approval
- `Signals/health_report.md` - VM health status
- `Logs/` - JSON activity logs

## License

MIT

---

**VaultOS** - Built with ❤️ for automated business operations
