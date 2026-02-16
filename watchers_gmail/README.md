# Gmail Watcher

This module monitors email accounts for new messages and processes attachments by moving them to the Needs_Action folder for further processing.

## Components

- `gmail_auth.py` - Handles Google OAuth2 authentication
- `client_secret_*.json` - Contains the client secret for the Google application
- `token.json` - Stores the authentication token (generated after initial setup)
- `setup_gmail.bat` - Windows batch file to help with setup

## Setup

1. Run the authentication script:
   ```
   python gmail_auth.py
   ```

2. A browser window will open asking you to sign in to your Google account and authorize the application.

3. After successful authorization, a `token.json` file will be created in this folder.

## Troubleshooting Authentication Issues

If you encounter a "mismatching_state" error during authentication:

1. **Close other applications** that might be using ports 80/443
2. **Temporarily disable** firewall or antivirus software that might interfere
3. **Use the setup batch file** (Windows): `setup_gmail.bat`
4. **Try a different network** if corporate firewall is blocking callbacks
5. **Run as administrator** (Windows) to avoid port conflicts

## Security Notice

- Keep your `token.json` and `client_secret_*.json` files secure
- These files contain sensitive authentication information
- Do not share these files publicly

## How It Works

Once authenticated, the Gmail watcher can monitor your inbox for new emails and automatically process attachments by placing them in the Needs_Action folder where they'll be picked up by the main file processing workflow.