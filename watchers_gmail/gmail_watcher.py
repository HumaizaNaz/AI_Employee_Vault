import sys
import io
import time
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

CATEGORIES = {
    'Payment':     ['payment', 'invoice', 'bill', 'fee', 'cost', 'charge', 'receipt', 'transaction', 'amount'],
    'Project':     ['project', 'assignment', 'task', 'deliverable', 'milestone', 'deadline'],
    'Event':       ['event', 'meeting', 'conference', 'seminar', 'workshop', 'hackathon'],
    'Educational': ['exam', 'quiz', 'grade', 'course', 'study', 'learning', 'student'],
    'Client':      ['client', 'customer', 'contract', 'agreement', 'proposal'],
    'Security':    ['security', 'breach', 'suspicious', 'phishing', 'malware', 'compromised'],
    'Urgent':      ['urgent', 'asap', 'immediate', 'critical', 'emergency', 'attention'],
}


class GmailWatcher:
    def __init__(self, vault_path: str, token_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action' / 'Email'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        (self.vault_path / 'Done').mkdir(exist_ok=True)
        (self.vault_path / 'Pending_Approval').mkdir(exist_ok=True)
        (self.vault_path / 'Plans').mkdir(exist_ok=True)

        self.check_interval = 60
        self.processed_ids = set()

        self.analytics = {
            'emails_processed': 0,
            'by_category': defaultdict(int),
            'by_priority': defaultdict(int),
        }

        self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            Path(token_path).write_text(self.creds.to_json(), encoding='utf-8')

        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Gmail Watcher connected")
        print("Watching: unread + important emails")

    def categorize_email(self, subject: str, snippet: str) -> tuple:
        text = f"{subject} {snippet}".lower()
        category = 'General'
        priority = 'medium'

        for cat, keywords in CATEGORIES.items():
            if any(kw in text for kw in keywords):
                category = cat
                break

        if any(kw in text for kw in CATEGORIES['Urgent']):
            priority = 'high'
        elif any(kw in text for kw in CATEGORIES['Security']):
            priority = 'critical'

        if category == 'Payment':
            amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
            for amt in amounts:
                val = float(amt.replace('$', '').replace(',', ''))
                if val > 100:
                    priority = 'high'
                    break

        return category, priority

    def needs_approval_check(self, category: str, priority: str, snippet: str) -> tuple:
        if category in ['Payment', 'Client'] or 'hackathon' in snippet.lower():
            if priority in ['high', 'critical']:
                if category == 'Payment':
                    return True, "Payment over $100 detected"
                elif category == 'Client':
                    return True, "New client contact"
                else:
                    return True, "Hackathon registration or fee"
        return False, ""

    def check_for_updates(self) -> list:
        keyword_filters = [
            '"hackathon"', '"event"', '"exam"', '"project"',
            '"meeting"', '"deadline"', '"payment"', '"invoice"',
            '"urgent"', '"important"'
        ]
        q = f'(is:unread OR is:important) AND ({" OR ".join(keyword_filters)})'
        response = self.service.users().messages().list(
            userId='me', q=q, maxResults=20
        ).execute()
        messages = response.get('messages', [])
        return [m for m in messages if m['id'] not in self.processed_ids]

    def get_body(self, message_id: str) -> str:
        msg = self.service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
        payload = msg.get('payload', {})
        parts = payload.get('parts', [])
        if not parts:
            data = payload.get('body', {}).get('data', '')
            if data:
                import base64
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            return ''
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    import base64
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        return ''

    def create_action_file(self, message: dict):
        msg = self.service.users().messages().get(
            userId='me', id=message['id'], format='full',
            metadataHeaders=['From', 'Subject', 'Date', 'Cc']
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        snippet = msg.get('snippet', '')
        subject = headers.get('Subject', 'No Subject')
        sender  = headers.get('From', 'Unknown')

        category, priority = self.categorize_email(subject, snippet)
        needs_approval, approval_reason = self.needs_approval_check(category, priority, snippet)

        self.analytics['emails_processed'] += 1
        self.analytics['by_category'][category] += 1
        self.analytics['by_priority'][priority] += 1

        content = f"""---
type: email
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
date: {headers.get('Date', 'Unknown')}
priority: {priority}
category: {category}
status: pending
needs_approval: {str(needs_approval).lower()}
approval_reason: {approval_reason}
---

## Email Preview
{snippet}

## Classification
- Category: {category}
- Priority: {priority}
- Needs Approval: {needs_approval}
{f'- Approval Reason: {approval_reason}' if approval_reason else ''}

## Suggested Actions
- [ ] Review email content
- [ ] Assess priority and respond accordingly
- [ ] Archive after processing
"""
        filepath = self.needs_action / f"EMAIL_{message['id']}.md"
        filepath.write_text(content, encoding='utf-8')

        self.service.users().messages().modify(
            userId='me', id=message['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        self.processed_ids.add(message['id'])
        print(f"New email saved: {filepath.name}")
        print(f"  Category: {category} | Priority: {priority}")
        if needs_approval:
            print(f"  Requires approval: {approval_reason}")

    def run(self):
        print("Gmail Watcher running...")
        while True:
            try:
                messages = self.check_for_updates()
                for msg in messages:
                    self.create_action_file(msg)
                if self.analytics['emails_processed'] > 0 and self.analytics['emails_processed'] % 10 == 0:
                    print(f"Analytics — Total: {self.analytics['emails_processed']} | "
                          f"By category: {dict(self.analytics['by_category'])}")
            except Exception as e:
                print(f"Watcher error: {e}")
            time.sleep(self.check_interval)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python gmail_watcher.py <vault_path> <token_path>")
        sys.exit(1)
    watcher = GmailWatcher(sys.argv[1], sys.argv[2])
    watcher.run()
