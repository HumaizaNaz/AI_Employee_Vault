import time
from pathlib import Path
from datetime import datetime
import re
import json
from collections import defaultdict

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailWatcher:
    def __init__(self, vault_path: str, token_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Create additional folders for enhanced organization
        self.done_folder = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.plans_folder = self.vault_path / 'Plans'
        self.done_folder.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)
        self.plans_folder.mkdir(exist_ok=True)

        self.check_interval = 60  # seconds

        # 🔐 Load credentials
        self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # 🔄 Auto refresh token if expired
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            Path(token_path).write_text(self.creds.to_json(), encoding="utf-8")

        self.service = build('gmail', 'v1', credentials=self.creds)

        self.processed_ids = set()

        # 📊 Analytics tracking
        self.analytics = {
            'emails_processed': 0,
            'by_category': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_sender': defaultdict(int)
        }

        print("✅ Gmail Watcher connected")
        print("📥 Watching: unread + important emails")
        print("📁 Folders ready: Needs_Action, Done, Pending_Approval, Plans")

    def categorize_email(self, subject: str, snippet: str) -> tuple[str, str]:
        """Enhanced categorization and priority assignment"""
        subject_lower = subject.lower()
        snippet_lower = snippet.lower()

        # Define category keywords
        categories = {
            'Payment': ['payment', 'invoice', 'bill', 'fee', 'cost', 'charge', 'receipt', 'transaction', 'amount'],
            'Project': ['project', 'assignment', 'task', 'deliverable', 'milestone', 'deadline'],
            'Event': ['event', 'meeting', 'conference', 'seminar', 'workshop', 'hackathon'],
            'Educational': ['exam', 'quiz', 'grade', 'course', 'study', 'learning', 'student'],
            'Client': ['client', 'customer', 'contract', 'agreement', 'proposal'],
            'Security': ['security', 'breach', 'suspicious', 'phishing', 'malware', 'compromised'],
            'Urgent': ['urgent', 'asap', 'immediate', 'critical', 'emergency', 'attention']
        }

        # Determine category
        category = 'General'
        for cat, keywords in categories.items():
            if any(keyword in subject_lower or keyword in snippet_lower for keyword in keywords):
                category = cat
                break

        # Determine priority
        priority = 'medium'
        if any(word in subject_lower or word in snippet_lower for word in categories['Urgent']):
            priority = 'high'
        elif any(word in subject_lower or word in snippet_lower for word in categories['Security']):
            priority = 'critical'

        # Additional check for payment amounts
        if category == 'Payment':
            # Look for monetary amounts in the email
            money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|usd|eur|gbp)\b'
            amounts = re.findall(money_pattern, snippet_lower)
            if amounts:
                for amount_str in amounts:
                    # Extract numeric value from the amount string
                    num_match = re.search(r'\d+(?:,\d{3})*(?:\.\d{2})?', amount_str.replace(',', ''))
                    if num_match:
                        amount = float(num_match.group().replace(',', ''))
                        if amount > 100:
                            priority = 'high'

        return category, priority

    def check_security_threats(self, subject: str, snippet: str) -> dict:
        """Check for security threats in the email"""
        threats = {
            'phishing_indicators': [],
            'suspicious_links': [],
            'malicious_keywords': []
        }

        # Phishing indicators
        phishing_patterns = [
            r'urgent.*action.*required',
            r'click.*here.*now',
            r'act.*within.*hours?',
            r'account.*suspend',
            r'verify.*account',
            r'confirm.*details'
        ]

        for pattern in phishing_patterns:
            if re.search(pattern, snippet, re.IGNORECASE):
                threats['phishing_indicators'].append(pattern)

        # Suspicious links
        link_pattern = r'https?://[^\s<>"\']+'
        links = re.findall(link_pattern, snippet)
        suspicious_domains = ['bit.ly', 'tinyurl', 'goo.gl', 'shorturl']
        for link in links:
            if any(domain in link for domain in suspicious_domains):
                threats['suspicious_links'].append(link)

        # Malicious keywords
        malicious_keywords = [
            'malware', 'virus', 'trojan', 'ransomware', 'keylogger',
            'password reset', 'unauthorized access', 'security breach'
        ]
        for keyword in malicious_keywords:
            if keyword.lower() in snippet.lower():
                threats['malicious_keywords'].append(keyword)

        return threats

    def check_for_updates(self):
        messages = []
        # Enhanced query to catch more important emails
        query_parts = [
            'is:unread',  # All unread emails
            'OR is:important',  # Plus important emails
            'OR label:inbox'  # And inbox emails with specific keywords
        ]

        # Combine with keyword filters
        keyword_filters = [
            '"hackathon"', '"event"', '"exam"', '"project"',
            '"Panaversity"', '"meeting"', '"deadline"', '"submission"',
            '"payment"', '"invoice"', '"urgent"', '"important"'
        ]

        q = f'({" OR ".join(query_parts)}) AND ({" OR ".join(keyword_filters)})'

        request = self.service.users().messages().list(
            userId='me',
            q=q,
            maxResults=20  # Limit results to prevent overwhelming
        )

        while request is not None:
            response = request.execute()
            for msg in response.get('messages', []):
                if msg['id'] not in self.processed_ids:
                    messages.append(msg)
            request = self.service.users().messages().list_next(
                request, response
            )

        return messages

    def get_full_message_content(self, message_id: str):
        """Get full message content including body"""
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        # Extract message body
        body = ""
        payload = msg.get('payload', {})
        parts = payload.get('parts', [])

        if not parts:
            # Handle simple messages without parts
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                import base64
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            # Handle multipart messages
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        import base64
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break

        return body

    def create_action_file(self, message):
        msg = self.service.users().messages().get(
            userId='me',
            id=message['id'],
            format='full',
            metadataHeaders=['From', 'Subject', 'Date', 'Cc', 'Bcc']
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Get full content for analysis
        full_body = self.get_full_message_content(message['id'])
        snippet = msg.get('snippet', 'No preview available')
        combined_content = f"{headers.get('Subject', '')} {snippet} {full_body}"

        # 🏷️ Categorize and prioritize
        category, priority = self.categorize_email(headers.get('Subject', ''), combined_content)

        # 🔍 Check for security threats
        security_threats = self.check_security_threats(headers.get('Subject', ''), combined_content)

        # 📊 Update analytics
        self.analytics['emails_processed'] += 1
        self.analytics['by_category'][category] += 1
        self.analytics['by_priority'][priority] += 1
        sender = headers.get('From', 'Unknown')
        self.analytics['by_sender'][sender] += 1

        # Check if email needs approval (payment > $100, new client, hackathon fee)
        needs_approval = False
        approval_reason = ""

        if category in ['Payment', 'Client'] or 'hackathon' in combined_content.lower():
            if priority == 'high' or category in ['Client']:
                needs_approval = True
                if category == 'Payment':
                    approval_reason = "Payment > $100"
                elif category == 'Client':
                    approval_reason = "New client contact"
                else:
                    approval_reason = "Hackathon registration fee"

        # Create content with enhanced metadata
        content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
category: {category}
needs_approval: {needs_approval}
threats: {json.dumps(security_threats, indent=2)}
---

## Email Preview
{snippet}

## Full Content Preview
{full_body[:500]}...

## Sender Info
Date: {headers.get('Date', 'Unknown')}
Cc: {headers.get('Cc', 'None')}
Bcc: {headers.get('Bcc', 'None')}

## Security Analysis
Threats detected: {len(security_threats['phishing_indicators']) + len(security_threats['suspicious_links']) + len(security_threats['malicious_keywords']) > 0}
Phishing indicators: {security_threats['phishing_indicators']}
Suspicious links: {security_threats['suspicious_links']}
Malicious keywords: {security_threats['malicious_keywords']}

## Email Classification
Category: {category}
Priority: {priority}
Needs Approval: {needs_approval}
Approval Reason: {approval_reason}

## Suggested Actions
- [ ] Review email content
- [ ] Assess security risks
- [ ] Determine appropriate response
- [ ] Archive after processing
"""

        filepath = self.needs_action / f"EMAIL_{message['id']}.md"
        filepath.write_text(content, encoding="utf-8")

        # ✔ Mark email as READ
        self.service.users().messages().modify(
            userId='me',
            id=message['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        self.processed_ids.add(message['id'])

        print(f"📧 New email → file created: {filepath.name}")
        print(f"   🏷️ Category: {category}, Priority: {priority}")
        if needs_approval:
            print(f"   ⚠️  Requires approval: {approval_reason}")

    def run(self):
        print(f"📊 Starting Gmail Watcher...")
        print(f"📈 Tracking: {self.analytics['emails_processed']} emails processed")

        while True:
            try:
                messages = self.check_for_updates()
                for msg in messages:
                    self.create_action_file(msg)

                # Print periodic analytics
                if self.analytics['emails_processed'] % 10 == 0:
                    print(f"📈 Analytics Update:")
                    print(f"   Total processed: {self.analytics['emails_processed']}")
                    print(f"   By category: {dict(self.analytics['by_category'])}")
                    print(f"   By priority: {dict(self.analytics['by_priority'])}")

            except Exception as e:
                print("❌ Watcher error:", e)

            time.sleep(self.check_interval)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "python gmail_watcher.py "
            "F:\\AI_Employee_Vault\\AI_Employee_Vault "
            "F:\\AI_Employee_Vault\\AI_Employee_Vault\\watchers_gmail\\token.json"
        )
        sys.exit(1)

    vault_path = sys.argv[1]
    token_path = sys.argv[2]

    watcher = GmailWatcher(vault_path, token_path)
    watcher.run()
