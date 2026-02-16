# Step-by-Step Guide to Setting Up Gmail Watcher for Personal AI Employee Hackathon

This README documents all the steps we took to set up the Gmail Watcher in the Personal AI Employee Hackathon project. It is written in English for clarity and serves as notes for future reference. The Gmail Watcher is a Python script that monitors your Gmail for unread important emails, creates .md files in the Obsidian vault's Needs_Action folder, and integrates with Claude Code for processing.  

The setup involves Google Cloud Console for API credentials, Python libraries installation, authorization for token generation, and running the watcher script. All steps are based on our conversation and troubleshooting from January 14, 2026.

## Prerequisites

- Python 3.13 or higher installed.
- Obsidian vault "AI_Employee_Vault" created with folders like Needs_Action, Plans, Done, etc.
- Claude Code set up with router.
- Stable internet for API calls.

## Step 1: Create a Google Cloud Project

1. Go to <https://console.cloud.google.com/>.
2. Log in with your Google account (e.g., <humaizaasghar@gmail.com> or <humaizanaz916@gmail.com>).
3. Click on the project dropdown at the top and select "New Project".
4. Give it a name, e.g., "AI-Employee-Gmail".
5. Click "Create" – the project is now ready.

## Step 2: Enable Gmail API

1. In the console, go to the left menu > APIs & Services > Library.
2. Search for "Gmail API".
3. Select it and click "Enable".
4. This allows your script to access Gmail.

## Step 3: Set Up OAuth Consent Screen

1. Left menu > APIs & Services > OAuth consent screen.
2. Select "External" as User Type (for personal use).
3. Fill in App name, e.g., "AI Employee Gmail Watcher".
4. Add your emails as test users:
   - <humaizaasghar@gmail.com>
   - <humaizanaz916@gmail.com>
5. Publishing status: Keep as "Testing".
6. Save and Continue.

## Step 4: Create OAuth Client ID

1. Left menu > APIs & Services > Credentials.
2. Click "+ Create Credentials" > "OAuth client ID".
3. Application type: "Desktop app" (since this is a local Python script).
4. Name: "AI Employee Gmail Watcher Desktop".
5. Click "Create".
6. Download the JSON file (it will have a long name like client_secret_xxx.json).
7. Rename it to "client_secret.json" and place it in the watchers_gmail folder.

## Step 5: Add Authorized Redirect URIs (To Fix Missing redirect_uri Error)

1. In Credentials tab, click the pencil icon (edit) on your OAuth client ID.
2. Scroll to "Authorized redirect URIs".
3. Click "+ ADD URI" and add these:
   - <http://localhost>
   - <http://localhost:8080>
   - <http://localhost:5000>
   - <http://localhost:53610>
   - <http://localhost:53449>
   - <http://localhost:53413>
4. Click "Save".
5. Wait 5-10 minutes for changes to apply.

## Step 6: Install Required Python Libraries

1. Open terminal in watchers_gmail folder.
2. Run:

   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

This installs libraries for Google authentication and API calls.

## Step 7: Generate Token.json (Authorization Step)

1. Create or update gmail_auth.py in watchers_gmail folder with this code (replace CLIENT_SECRET_FILE with your file name if needed):

   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   import os

   SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

   CLIENT_SECRET_FILE = 'client_secret.json'  # Your file name here

   flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

   # Generate authorization URL
   authorization_url, state = flow.authorization_url(
       access_type='offline',
       include_granted_scopes='true'
   )

   print("Step 1: Copy this URL and open in browser:")
   print(authorization_url)

   print("\nStep 2: Login, Allow the app.")
   print("Step 3: Copy the code from the browser URL bar (code= part).")

   auth_code = input("\nPaste the code here: ").strip()

   # Fetch token
   flow.fetch_token(code=auth_code)

   creds = flow.credentials
   with open('token.json', 'w') as token_file:
       token_file.write(creds.to_json())

   print("SUCCESS! token.json created.")
   ```

2. Run:

   ```bash
   python gmail_auth.py
   ```

3. Copy the URL from terminal, open in browser, login, Allow, copy the code from URL bar, paste in terminal.
4. Token.json will be created in the folder.

## Step 8: Create and Run Gmail Watcher Script

1. Create gmail_watcher.py in watchers_gmail folder with this code:

   ```python
   import time
   from pathlib import Path
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   from datetime import datetime

   class GmailWatcher:
       def __init__(self, vault_path: str, token_path: str):
           self.vault_path = Path(vault_path)
           self.needs_action = self.vault_path / 'Needs_Action'
           self.needs_action.mkdir(exist_ok=True)
           self.check_interval = 60

           creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/gmail.modify'])
           self.service = build('gmail', 'v1', credentials=creds)
           self.processed_ids = set()
           print("Gmail Watcher connected! Waiting for new emails...")

       def check_for_updates(self):
           results = self.service.users().messages().list(
               userId='me',
               q='is:unread is:important'
           ).execute()
           messages = results.get('messages', [])
           return [m for m in messages if m['id'] not in self.processed_ids]

       def create_action_file(self, message):
           msg = self.service.users().messages().get(
               userId='me', id=message['id']
           ).execute()

           headers = {h['name']: h['value'] for h in msg['payload']['headers']}

           content = f'''---

type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content

{msg.get('snippet', 'No content available')}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward if needed
- [ ] Archive after processing
'''

           filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
           filepath.write_text(content)
           self.processed_ids.add(message['id'])
           print(f"New email detected! File created: {filepath}")

       def run(self):
           while True:
               try:
                   items = self.check_for_updates()
                   for item in items:
                       self.create_action_file(item)
               except Exception as e:
                   print(f"Error: {e}")
               time.sleep(self.check_interval)

   if __name__ == "__main__":
       import sys
       if len(sys.argv) < 3:
           print("Run like: python gmail_watcher.py F:\\AI_Employee_Vault\\AI_Employee_Vault F:\\...\\token.json")
           sys.exit(1)

       vault_path = sys.argv[1]
       token_path = sys.argv[2]
       watcher = GmailWatcher(vault_path, token_path)
       watcher.run()

   ```

1. Run the watcher:

   ```bash
   python gmail_watcher.py "F:\AI_Employee_Vault\AI_Employee_Vault" "F:\AI_Employee_Vault\AI_Employee_Vault\watchers_gmail\token.json"
   ```

2. Test by sending an unread important email to yourself – check Needs_Action folder for new .md file.

## Troubleshooting Notes

- If state mismatch error: Use manual code paste from browser URL.
- If redirect_uri error: Add <http://localhost> in Credentials edit.
- If invalid_grant: Wait 5-10 min after saving changes or delete token.json and re-run.
