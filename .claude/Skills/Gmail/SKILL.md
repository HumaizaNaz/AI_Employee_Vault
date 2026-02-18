# Gmail Skill

## Overview
The Gmail skill enables the AI Employee to monitor, process, and manage Gmail communications automatically. This skill integrates with the Gmail API to check for important emails, create action files, and facilitate automated responses through the MCP server.

## Capabilities
- Monitor Gmail for unread and important emails
- Extract email metadata (sender, subject, content)
- Create action files in the `/Needs_Action/Email` folder
- Process emails based on importance and content
- Facilitate automated email responses when approved
- Integrate with approval workflows for sensitive emails

## Technical Implementation
- Uses Google Gmail API via Python client library
- Implements OAuth2 authentication with stored credentials
- Inherits from BaseWatcher class for standardized operation
- Creates markdown files with structured metadata
- Integrates with the orchestrator for workflow management

## Input Parameters
- `vault_path`: Path to the AI Employee vault directory
- `credentials_path`: Path to Gmail API credentials file

## Output Format
Creates markdown files in `/Needs_Action/Email/` with the following structure:
```markdown
---
type: email
from: [sender email/name]
subject: [email subject]
received: [timestamp]
priority: [high/medium/low]
status: pending
needs_approval: [true/false]
---

## Email Content
[Email snippet/content]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Context
[Additional context based on content analysis]
```

## Activation Triggers
- Scheduled monitoring every 120 seconds by default
- Detection of new unread important emails
- Integration with the orchestrator's processing loop

## Dependencies
- Google API client libraries
- Gmail API credentials
- BaseWatcher class
- MCP email server for responses

## Security Considerations
- Uses OAuth2 with limited scope access
- Credentials stored separately from vault
- Sensitive emails require human approval before action
- All email processing logged for audit trail

## Integration Points
- Works with orchestrator.py for workflow management
- Creates files for Claude Code processing
- Integrates with MCP server for email sending
- Updates dashboard status through dashboard_updater.py

## Error Handling
- Gracefully handles API rate limits
- Manages authentication token refresh
- Continues operation despite individual email failures
- Logs errors for troubleshooting