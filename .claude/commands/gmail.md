# Gmail Skill

Monitor and process Gmail inbox for the AI Employee vault.

## What to do when invoked:

1. Check `/Needs_Action/Email/` for any unread email files
2. For each email file found:
   - Read the metadata (from, subject, date, priority)
   - Analyze content to determine if it needs approval or can be auto-processed
   - If sensitive (new contact, financial, legal) → move to `/Pending_Approval/Email/`
   - If routine → draft a reply in `/Drafts/` and move to `/Pending_Approval/Email/` for review
3. Update Dashboard.md with email processing stats
4. Log all actions to `/Logs/` in JSON format

## Output format for email action files:
```
---
type: email
from: [sender]
subject: [subject]
received: [timestamp]
priority: high/medium/low
status: pending
needs_approval: true/false
---
## Email Content
[content]
## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Rules:
- Never send email directly — always create approval file first
- Flag any payment/invoice/legal email for human approval
- Process routine emails (scheduling, info requests) automatically
- All actions must be logged
