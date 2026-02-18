# Twitter / X Skill

## Overview
The Twitter/X skill enables the AI Employee to post tweets using the Twitter API v2. OAuth 1.0a authentication is verified and working. Currently paused due to API credit reset (resumes March 1, 2026).

## Capabilities
- Post tweets to Twitter/X account (@NazHumo)
- Check Twitter authentication status
- Retrieve tweet ID after successful post
- Integrate with approval workflow
- Log all tweet activity

## Technical Implementation
- Uses Twitter API v2 endpoint: `POST https://api.twitter.com/2/tweets`
- Authenticates via OAuth 1.0a (4 credentials required)
- Request body: `{ "text": "tweet content" }`
- VaultOS UI: `/social` page — Twitter button disabled with "Credits Reset Mar 1" badge
- Will be enabled once API credits are restored

## Input Parameters
- `text`: Tweet content (max 280 characters)
- `TWITTER_API_KEY`: Consumer Key
- `TWITTER_API_SECRET`: Consumer Secret
- `TWITTER_ACCESS_TOKEN`: Access Token
- `TWITTER_ACCESS_TOKEN_SECRET`: Access Token Secret

## Output Format
```markdown
---
type: social_post
platform: twitter
tweet_id: [returned tweet ID]
timestamp: [ISO timestamp]
status: success/failed
error: [error if failed]
---
## Tweet Content
[tweet text]
```

## Activation Triggers
- User selects Twitter in VaultOS Social page (when re-enabled after Mar 1)
- Orchestrator processes approved file from `/Approved/Social/`
- Manual invocation via `/twitter` skill

## Dependencies
- Twitter Developer Account (Verified: @NazHumo)
- OAuth 1.0a credentials (4 values)
- API credits available (reset March 1, 2026)

## Current Status
- Auth: ✅ Verified working (@NazHumo)
- Credits: ⏳ Reset March 1, 2026
- UI Button: Disabled in VaultOS until credits restored
- Re-enable: Add Twitter credentials to `.env.local` and uncomment button in social page

## Security Considerations
- All 4 OAuth credentials stored in `.env.local` — never committed
- All tweets require human approval before posting
- Audit log maintained for all tweet attempts

## Integration Points
- Shared social media approval workflow
- VaultOS `/api/social` route (extend to add Twitter)
- Logs stored in `/Logs/`

## Error Handling
- Insufficient credits → clear error returned
- Auth failure → 401 response with message
- Rate limit exceeded → 429 response, retry after delay
