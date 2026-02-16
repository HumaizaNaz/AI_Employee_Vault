# WhatsApp Skill

## Overview
The WhatsApp skill enables the AI Employee to monitor, process, and manage WhatsApp communications automatically. This skill uses Playwright to automate WhatsApp Web and detect important messages containing specific keywords, creating action files for further processing.

## Capabilities
- Monitor WhatsApp Web for unread messages
- Detect messages containing predefined important keywords
- Extract message content and sender information
- Create action files in the `/Needs_Action/WhatsApp` folder
- Process messages based on keyword matching and importance
- Integrate with approval workflows for sensitive messages

## Technical Implementation
- Uses Playwright for browser automation
- Implements persistent session storage for WhatsApp Web
- Inherits from BaseWatcher class for standardized operation
- Creates markdown files with structured metadata
- Integrates with the orchestrator for workflow management

## Input Parameters
- `vault_path`: Path to the AI Employee vault directory
- `session_path`: Path to WhatsApp session storage (optional, defaults to vault directory)

## Output Format
Creates markdown files in `/Needs_Action/WhatsApp/` with the following structure:
```markdown
---
type: whatsapp_message
from: [contact name]
received: [timestamp]
priority: [high/medium]
status: pending
keywords_matched: [list of matched keywords]
---

## WhatsApp Message
**From:** [contact name]
**Time:** [timestamp]

**Message:**
[Message content]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Context
This message contained important keywords: [comma-separated keywords]
```

## Activation Triggers
- Scheduled monitoring every 30 seconds by default
- Detection of chats with unread message indicators
- Keyword matching in message content

## Dependencies
- Playwright library
- Chromium browser
- WhatsApp Web access
- BaseWatcher class
- Persistent session storage

## Security Considerations
- Sessions stored locally in vault directory
- No message content transmitted externally (except through WhatsApp Web)
- Requires manual WhatsApp Web login for initial authentication
- All message processing logged for audit trail

## Integration Points
- Works with orchestrator.py for workflow management
- Creates files for Claude Code processing
- Integrates with approval manager for sensitive messages
- Updates dashboard status through dashboard_updater.py

## Error Handling
- Handles browser automation failures gracefully
- Manages session persistence and restoration
- Continues operation despite individual message failures
- Provides detailed logging for troubleshooting

## Keywords Monitored
- Urgency: urgent, asap, now, emergency, critical
- Financial: invoice, payment, money, cash, transfer, pay, deadline, due
- Requests: help, need, please, thanks
- Communications: meeting, schedule, appointment, call
- General: important, today, regarding, concerning, hi, hello