# Claim System for AI Employee Coordination

## Overview
This script implements the claim-by-move rule to prevent double-work between multiple AI agents.
When an agent finds a task in /Needs_Action/, it attempts to move it to /In_Progress/<agent_name>/
If successful, the agent owns the task; if not, another agent has already claimed it.

## Claim Process
1. Agent scans /Needs_Action/ folder for unclaimed tasks
2. Agent attempts to move selected task to /In_Progress/<agent_name>/
3. If move succeeds, agent owns the task and begins processing
4. If move fails (due to race condition), agent selects another task
5. Upon completion, agent moves task to /Done/ or appropriate outcome folder

## Sample Task File Format
Each task file in /Needs_Action/ should include metadata to facilitate claiming:

---
type: email_reply
priority: high
assigned_to: unclaimed
claimed_by: none
claimed_at: null
status: pending
---

## Agent-Specific In_Progress Folders
- /In_Progress/local_agent/
- /In_Progress/cloud_agent/
- etc.

## Implementation Notes
- Use atomic file operations to ensure thread safety
- Log all claim attempts for audit purposes
- Implement retry logic for failed claims
- Include timeout mechanisms for abandoned claims