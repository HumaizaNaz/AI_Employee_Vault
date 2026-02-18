# Instagram Skill

## Overview
The Instagram skill enables the AI Employee to publish posts to an Instagram Business Account using the Instagram Graph API (two-step: create container → publish). All posts require human approval and an image URL.

## Capabilities
- Publish photo posts with captions to Instagram Business Account
- Two-step container creation and publishing flow
- Check Instagram account connection status
- Use default fallback image when no image URL provided
- Integrate with approval workflow
- Log all posting activity

## Technical Implementation
- Uses Instagram Graph API via Facebook Graph API v18.0
- Step 1: `POST /{IG_ACCOUNT_ID}/media` → creates media container
- Step 2: `POST /{IG_ACCOUNT_ID}/media_publish` → publishes container
- Both steps use `INSTAGRAM_USER_TOKEN` for authentication
- Default image used if no URL provided (Wikipedia placeholder)
- VaultOS UI: `/social` page, Instagram toggle button (pink)
- Next.js API route: `vaultos/src/app/api/social/route.ts`

## Input Parameters
- `caption`: Text caption for the post (max 2200 characters)
- `image_url`: Public URL of the image to post (required by Instagram API)
- `access_token`: Instagram User Token from `INSTAGRAM_USER_TOKEN` env var
- `ig_account_id`: Instagram Business Account ID from `INSTAGRAM_ACCOUNT_ID` env var

## Output Format
```markdown
---
type: social_post
platform: instagram
post_id: [returned media ID]
timestamp: [ISO timestamp]
image_url: [used image URL]
status: success/failed
error: [error if failed]
---
## Posted Caption
[caption content]
```

## Activation Triggers
- User selects Instagram in VaultOS Social page and clicks Post
- Orchestrator processes approved file from `/Approved/Social/`
- Manual invocation via `/instagram` skill

## Dependencies
- Instagram Business Account connected to Facebook Page
- `INSTAGRAM_ACCOUNT_ID` environment variable (numeric ID)
- `INSTAGRAM_USER_TOKEN` environment variable
- Public image URL (Instagram does not accept local files)

## Security Considerations
- Tokens stored in `.env.local` — never committed to git
- Tokens added to Vercel environment variables
- All posts require human approval
- Audit log maintained

## Integration Points
- Shared with Facebook via `/api/social` route
- Same approval workflow as Facebook posts
- VaultOS dashboard shows "Business Account Linked" status
- Logs stored in `/Logs/`

## Error Handling
- Container creation fails → returns error, does not attempt publish
- Image URL invalid or not publicly accessible → API returns error
- Token expired → clear error message returned
- Network failure → caught and logged gracefully

## Important Notes
- Instagram REQUIRES a public image URL — text-only posts not supported
- Default fallback image used if field left empty in VaultOS UI
- Account must be Instagram Business or Creator (not personal)
- Account ID: 17841448370922983
