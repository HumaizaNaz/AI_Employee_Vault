# Draft System for AI Employee

## Overview
The Draft System implements draft-only functionality for sensitive operations like emails and social media posts. Instead of directly executing these actions, the system creates drafts that require human approval before final publication.

## Components

### 1. Draft Creation Module
- Intercepts outgoing emails/social posts
- Creates draft versions instead of sending directly
- Stores drafts in `/Drafts/` folder with approval requirements

### 2. Draft Management System
- Organizes drafts by type (email, social post, etc.)
- Tracks approval status of each draft
- Manages scheduling for approved drafts

### 3. Approval Integration
- Links with the approval system to require authorization
- Creates approval requests for draft publications
- Ensures human oversight for all published content

## Draft File Format

```markdown
---
type: draft_email
status: pending_approval
created: 2026-01-07T10:30:00Z
scheduled: null
author: ai_employee
requires_approval: true
target_audience: client
---

# Draft: Project Update for Q1 Goals

Dear Client,

I wanted to provide you with an update on the Q1 project goals...

## Call to Action
Please review this draft and approve for sending by moving to `/Approved/` folder.

## Approval Options
- To Approve: Move this file to `/Approved/` folder
- To Revise: Edit content and keep in `/Drafts/`
- To Discard: Move to `/Discarded/` folder
```

## Supported Draft Types

### Email Drafts
- Drafts for outgoing emails
- Requires approval for sensitive clients/subjects
- Supports scheduling for timed delivery

### Social Media Drafts
- Drafts for Facebook, Twitter, LinkedIn posts
- Requires approval for brand-consistent messaging
- Supports optimal timing algorithms

### Document Drafts
- Drafts for reports, proposals, agreements
- Requires approval for official documents
- Supports collaborative review cycles

## Workflow

1. AI identifies need for communication (email/social post)
2. Instead of sending directly, AI creates draft in `/Drafts/` folder
3. Draft includes all necessary context and approval requirements
4. Human reviews and approves the draft
5. Once approved, draft is processed by the action executor
6. Completed communication is logged in `/Done/` folder

## Security Measures

- Drafts do not contain raw credentials
- Approval process ensures human oversight
- Audit trail maintained for all draft operations
- Sensitive drafts require elevated approval levels