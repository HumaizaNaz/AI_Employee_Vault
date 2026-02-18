# LinkedIn Skill

## Overview
The LinkedIn skill enables the AI Employee to post professional content to a LinkedIn profile using the LinkedIn UGC Posts API v2. Code is fully implemented and ready — requires access token once LinkedIn Developer App is approved.

## Capabilities
- Post text updates to LinkedIn profile (public visibility)
- Check LinkedIn profile connection status
- Retrieve post ID after successful publish
- Integrate with approval workflow
- Log all posting activity

## Technical Implementation
- Uses LinkedIn API v2 endpoint: `POST https://api.linkedin.com/v2/ugcPosts`
- Authenticates via Bearer token: `Authorization: Bearer {LINKEDIN_ACCESS_TOKEN}`
- Requires `X-Restli-Protocol-Version: 2.0.0` header
- Post body format:
```json
{
  "author": "urn:li:person:{LINKEDIN_MEMBER_URN}",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": { "text": "your post text" },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```
- VaultOS UI: `/social` page, LinkedIn button (sky blue) — shows "Token Pending" until configured
- Next.js API route: `vaultos/src/app/api/social/route.ts` — `postToLinkedIn()` function

## Input Parameters
- `text`: Post content (text only for now)
- `LINKEDIN_ACCESS_TOKEN`: OAuth 2.0 access token (scope: `w_member_social`)
- `LINKEDIN_MEMBER_URN`: LinkedIn member ID (numeric, from `/v2/me` API)

## Output Format
```markdown
---
type: social_post
platform: linkedin
post_id: [returned URN]
timestamp: [ISO timestamp]
status: success/failed
error: [error if failed]
---
## Posted Content
[post text]
```

## Activation Triggers
- User selects LinkedIn in VaultOS Social page and clicks Post
- Orchestrator processes approved file from `/Approved/Social/`
- Manual invocation via `/linkedin` skill

## Dependencies
- LinkedIn Developer App (App name: VaultOS)
- Product added: "Share on LinkedIn" (gives `w_member_social` scope)
- `LINKEDIN_ACCESS_TOKEN` environment variable
- `LINKEDIN_MEMBER_URN` environment variable

## Current Status
- ⏳ Token Pending — LinkedIn account is new, needs maturity before API access granted
- Code: ✅ Fully implemented in `vaultos/src/app/api/social/route.ts`
- UI: ✅ LinkedIn button visible in VaultOS `/social` page
- Activation: Add token to `.env.local` and Vercel env vars

## Setup Steps (when ready)
1. Go to `https://developer.linkedin.com/`
2. Create app named "VaultOS"
3. Add product: "Share on LinkedIn"
4. Go to Auth tab → OAuth 2.0 tools
5. Generate token with scope `w_member_social`
6. Call `GET https://api.linkedin.com/v2/me` to get your member URN
7. Add both values to `.env.local` and Vercel environment variables

## Security Considerations
- Tokens stored in `.env.local` — never committed to git
- OAuth 2.0 with minimal required scope
- All posts require human approval
- Audit log maintained

## Error Handling
- Token not configured → returns `{ success: false, error: "LinkedIn token not configured" }`
- Token expired → LinkedIn returns 401, clear error shown in UI
- Post fails → error message logged and shown in VaultOS result
