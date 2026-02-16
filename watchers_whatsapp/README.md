# WhatsApp Watcher

## Overview
The WhatsApp Watcher is a Python-based monitoring system that continuously checks WhatsApp Web for important messages containing specific keywords. It's part of the AI Employee Vault system that automates monitoring and processing of communications.

## Features
- Monitors WhatsApp Web for unread messages
- Detects messages containing predefined important keywords
- Creates markdown action files in the `/Needs_Action/WhatsApp` folder
- Integrates with the AI Employee orchestration system
- Includes comprehensive error handling and logging
- Supports persistent sessions via Playwright

## Prerequisites
- Python 3.13+
- Playwright: `pip install playwright`
- Install Playwright browsers: `playwright install chromium`
- Node.js (for PM2 if using continuous operation)

## Installation

1. Install required Python packages:
```bash
pip install playwright
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Ensure your AI Employee Vault structure is set up with the correct folder structure:
```
AI_Employee_Vault/
├── Needs_Action/
│   └── WhatsApp/
├── Pending_Approval/
│   └── WhatsApp/
├── Done/
│   └── WhatsApp/
└── whatsapp_session/
```

## Configuration

The WhatsApp watcher uses the following configuration:
- **Check Interval**: 30 seconds (adjustable in constructor)
- **Keywords Monitored**: urgent, asap, invoice, payment, help, need, now, important, emergency, critical, as soon as possible, today, deadline, due, money, cash, transfer, pay, meeting, schedule, appointment, call, please, thanks, regarding, concerning, hi, hello
- **Session Storage**: Stored in `whatsapp_session/` folder
- **Output Folder**: Creates markdown files in `Needs_Action/WhatsApp/`

## Usage

### Manual Operation
To run the WhatsApp watcher once for testing:
```bash
python whatsapp_watcher.py "F:/AI_Employee_Vault/AI_Employee_Vault"
```

### Continuous Operation with PM2
The WhatsApp watcher can run continuously using PM2 (like your Gmail watcher):

1. Install PM2:
```bash
npm install -g pm2
```

2. Start the WhatsApp watcher with PM2:
```bash
pm2 start whatsapp_watcher.py --name whatsapp-watcher --interpreter python
```

3. Save the PM2 configuration to start on boot:
```bash
pm2 save
```

4. View PM2 status:
```bash
pm2 status
```

5. View logs:
```bash
pm2 logs whatsapp-watcher
```

## File Structure
- `whatsapp_watcher.py` - Main watcher implementation
- `whatsapp_auth.py` - Authentication helper (if needed)
- `setup_whatsapp.bat` - Windows setup script
- `start_whatsapp_watcher.bat` - Windows startup script
- `whatsapp_session/` - Persistent WhatsApp Web session data

## How It Works

1. **Initialization**: Sets up the watcher with the vault path and creates necessary directories
2. **WhatsApp Connection**: Opens WhatsApp Web using Playwright with persistent session
3. **Chat Scanning**: Identifies chats with unread message indicators
4. **Message Analysis**: Checks messages for important keywords
5. **Action File Creation**: Creates markdown files in `Needs_Action/WhatsApp/` for important messages
6. **Repeat**: Continues monitoring at the specified interval

## Action File Format
When important messages are detected, the watcher creates markdown files with the following structure:
```markdown
---
type: whatsapp_message
from: [Contact Name]
received: [Timestamp]
priority: [high/medium]
status: pending
keywords_matched: [list of matched keywords]
---

## WhatsApp Message
**From:** [Contact Name]
**Time:** [Timestamp]

**Message:**
[Message Content]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Context
This message contained important keywords: [comma-separated keywords]
```

## Troubleshooting

### Common Issues:
1. **WhatsApp Web Not Loading**: Ensure you're logged in to WhatsApp Web in the browser first
2. **Permission Errors**: Check that the script has write access to the vault directories
3. **Playwright Errors**: Ensure Chromium browser is installed via `playwright install chromium`

### Session Issues:
- If experiencing session problems, clear the `whatsapp_session/` folder
- Log in to WhatsApp Web manually in a browser first to establish the session

### Network Issues:
- Ensure stable internet connection
- Check firewall settings if WhatsApp Web is blocked

## Integration with AI Employee System
- Action files created by this watcher are processed by the main `orchestrator.py`
- Files move through the workflow: `Needs_Action/WhatsApp` → `Pending_Approval/WhatsApp` → `Done/WhatsApp`
- Integrates with the dashboard updating system
- Works alongside Gmail and file system watchers

## Security Notes
- Sessions are stored locally in the vault directory
- No message content is transmitted externally (except through WhatsApp Web)
- Follows the same security protocols as the overall AI Employee system
- Requires manual WhatsApp Web login for initial authentication

## Keywords Monitored
The watcher currently monitors for these important keywords:
- Urgency: urgent, asap, now, emergency, critical
- Business: invoice, payment, money, cash, transfer, pay, deadline, due
- Requests: help, need, please, thanks
- Communications: meeting, schedule, appointment, call
- General: important, today, regarding, concerning, hi, hello

## Maintenance
- Regularly check PM2 logs for errors
- Monitor the `Needs_Action/WhatsApp` folder for accumulation of files
- Ensure sufficient disk space for session data
- Periodically verify WhatsApp Web login status

## Improvements Made to WhatsApp Watcher

### 1. Updated UI Selectors
- Fixed selectors to work with current WhatsApp Web UI
- Added multiple fallback selectors to handle UI changes
- Improved detection of chat list and unread indicators

### 2. Enhanced Message Detection
- Improved algorithm to detect unread messages with multiple indicator types
- Better chat name identification using multiple selector strategies
- More reliable message extraction from chat windows

### 3. Robust Click Mechanisms
- Implemented multiple click methods to handle different UI states
- Added scroll-into-view functionality before clicking
- Added fallback click methods if primary method fails

### 4. Improved Error Handling
- Added comprehensive try-catch blocks throughout the code
- Better error messages and logging for troubleshooting
- Graceful degradation when parts of the process fail

### 5. Enhanced Stability
- Added proper waits and timeouts to prevent race conditions
- Improved session management with persistent context
- Better handling of network timeouts and connection issues

### 6. File Creation Improvements
- Added fallback mechanisms for file creation
- Better filename sanitization to handle special characters
- Improved error handling during action file creation

### 7. Logging and Monitoring
- Enhanced logging throughout the process
- Better visibility into what the watcher is doing
- More detailed error reporting for debugging

### 8. Keyword Monitoring Expansion
- Expanded the list of monitored keywords to catch more important messages
- Added context-aware keywords like "meeting", "schedule", "appointment"
- Improved keyword matching algorithm

These improvements ensure the WhatsApp watcher is now more reliable, stable, and compatible with the current WhatsApp Web interface, making it a robust component of your AI Employee system.