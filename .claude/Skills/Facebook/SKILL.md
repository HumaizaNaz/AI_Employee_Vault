# Facebook Skill

## Overview
The Facebook skill enables the AI Employee to post content directly to a Facebook Page using the Facebook Graph API v18. It handles text posts, tracks post IDs, and integrates with the approval workflow to ensure no post goes live without human sign-off.

## Capabilities
- Post text content to a Facebook Page feed
- Check Facebook Page connection status
- Retrieve post ID after successful publish
- Integrate with approval workflow for all posts
- Log all posting activity for audit trail
- Handle token expiry gracefully with clear error messages

## Technical Implementation
- Uses Facebook Graph API v18.0 endpoint: `POST /me/feed`
- Authenticates via Page Access Token stored in environment variable
- API call: `{ message: text, access_token: FB_TOKEN }`
- Returns post ID on success
- VaultOS UI: `/social` page with real-time connection status card
- Next.js API route: `vaultos/src/app/api/social/route.ts`

## Input Parameters
- `message`: Text content to post (max 2000 characters)
- `access_token`: Facebook Page Access Token (from `FACEBOOK_PAGE_ACCESS_TOKEN` env var)

## Output Format
Creates a post result log in `/Logs/`:
```markdown
---
type: social_post
platform: facebook
post_id: [returned post ID]
timestamp: [ISO timestamp]
status: success/failed
error: [error message if failed]
---
## Posted Content
[message content]
```

## Activation Triggers
- User clicks "Post" in VaultOS Social page
- Orchestrator processes an approved file from `/Approved/Social/`
- Manual Claude Code invocation via `/facebook` skill

## Dependencies
- Facebook Developer App with Pages API access
- Page Access Token (short-lived ~2hrs, or long-lived ~60 days)
- `FACEBOOK_PAGE_ACCESS_TOKEN` environment variable
- `FACEBOOK_PAGE_ID=me` environment variable

## Security Considerations
- Token stored in `.env.local` — never committed to git
- Token added to Vercel environment variables for cloud access
- All posts require human approval before execution
- Audit log maintained for every post attempt

## Integration Points
- VaultOS `/api/social` route handles POST requests
- Orchestrator checks `/Approved/Social/` and calls API
- Dashboard shows Facebook connection status
- Logs stored in `/Logs/YYYY-MM-DD.json`

## Error Handling
- Token expired → returns clear error "Token expired, please refresh"
- Invalid page → returns Facebook API error message
- Network failure → caught, logged, returns `{ success: false, error: message }`
- All errors logged without crashing the system

## Token Refresh Process
1. Go to Facebook Developer Portal → Graph API Explorer
2. Select your App and Page
3. Generate new Page Access Token
4. Update `FACEBOOK_PAGE_ACCESS_TOKEN` in `vaultos/.env.local`
5. Update same variable in Vercel dashboard → redeploy
