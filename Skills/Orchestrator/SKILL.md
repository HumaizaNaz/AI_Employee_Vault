# Orchestrator Skill

## Overview
The Orchestrator skill manages the entire workflow of the AI Employee system, coordinating between different components and ensuring proper processing of tasks. It implements the "Ralph Wiggum" loop pattern for continuous operation and manages the movement of files between different status folders.

## Capabilities
- Coordinate processing of files across all categories (Email, WhatsApp, Files)
- Manage file movement between status folders (Needs_Action, Pending_Approval, Approved, Done, Rejected)
- Implement Ralph Wiggum loop for continuous operation
- Update dashboard status with current statistics
- Log all actions for audit trail
- Handle both email and WhatsApp processing workflows
- Manage approval workflows for sensitive actions

## Technical Implementation
- Implements Ralph Wiggum loop pattern for continuous operation (up to 10 iterations)
- Processes files in specific order: Needs_Action → Pending_Approval → Approved/Done
- Uses regex for updating dashboard statistics
- Implements JSON logging for all actions
- Manages multiple folder paths for different categories
- Integrates with MCP email server for sending emails
- Updates Dashboard.md with real-time status

## Input Parameters
- None required (uses hardcoded vault paths in the implementation)

## Output Format
- Moves files between the following folder structure:
  - `/Needs_Action/[Email|WhatsApp|Files]/`
  - `/Pending_Approval/[Email|WhatsApp|Files]/`
  - `/Approved/[Email|WhatsApp|Files]/`
  - `/Done/[Email|WhatsApp|Files]/`
  - `/Rejected/`
- Updates Dashboard.md with current statistics
- Creates JSON logs in `/Logs/` folder
- Sends emails via MCP server when approved

## Activation Triggers
- Manual execution via `python orchestrator.py`
- Can be scheduled via cron or Task Scheduler for automated operation
- Continuous operation through Ralph Wiggum loop pattern

## Dependencies
- Python standard libraries (os, re, json, time, pathlib, datetime)
- dotenv for environment variable management
- MCP email server for sending emails
- All other system components (watchers, approval manager, etc.)

## Security Considerations
- Uses API key authentication for MCP server communication
- Implements approval workflows for sensitive actions
- Maintains detailed logs of all actions for audit trail
- Separates sensitive actions requiring human approval
- Validates file movements to prevent conflicts

## Integration Points
- Works with all watcher components (Gmail, WhatsApp, File System)
- Communicates with MCP email server for sending emails
- Updates Dashboard.md with current status
- Creates JSON logs for audit trail
- Integrates with approval manager workflow
- Coordinates between all system components

## Error Handling
- Handles file conflicts by checking if destination files already exist
- Manages API communication failures with MCP server
- Continues operation despite individual file processing failures
- Implements retry logic through Ralph Wiggum loop
- Provides detailed logging for troubleshooting
- Gracefully handles missing files or folders

## Workflow Process
1. Process `/Needs_Action/Email` files → move to `/Pending_Approval/Email` if needs approval, otherwise to `/Done/Email`
2. Process `/Needs_Action/WhatsApp` files → move to `/Pending_Approval/WhatsApp` (all require approval)
3. Process `/Pending_Approval/Email` files → if approved file exists, send email and move to `/Done/Email`; if rejected, move to `/Rejected/`; otherwise wait
4. Process `/Pending_Approval/WhatsApp` files → if approved file exists, process message and move to `/Done/WhatsApp`; if rejected, move to `/Rejected/`; otherwise wait
5. Update Dashboard.md with current statistics
6. Repeat until all tasks are processed or max iterations reached

## Dashboard Updates
- Last checked timestamp
- Pending emails in Needs_Action
- Pending WhatsApp messages in Needs_Action
- Pending files in Needs_Action
- Important pending items in Pending_Approval
- Recent sent emails activity log