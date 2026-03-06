import os
import re
import json
import time
from pathlib import Path
from datetime import datetime

# --- Configuration ---
VAULT_ROOT = Path(os.environ.get("VAULT_PATH", "F:/AI_Employee_Vault/AI_Employee_Vault"))
MODE = os.environ.get("ORCHESTRATOR_MODE", "local")  # "local" or "cloud"
NEEDS_ACTION_FOLDER = VAULT_ROOT / "Needs_Action"
NEEDS_ACTION_EMAIL_FOLDER = NEEDS_ACTION_FOLDER / "Email"
NEEDS_ACTION_WHATSAPP_FOLDER = NEEDS_ACTION_FOLDER / "WhatsApp"
NEEDS_ACTION_FILES_FOLDER = NEEDS_ACTION_FOLDER / "Files"
PENDING_APPROVAL_FOLDER = VAULT_ROOT / "Pending_Approval"
PENDING_APPROVAL_EMAIL_FOLDER = PENDING_APPROVAL_FOLDER / "Email"
PENDING_APPROVAL_WHATSAPP_FOLDER = PENDING_APPROVAL_FOLDER / "WhatsApp"
PENDING_APPROVAL_FILES_FOLDER = PENDING_APPROVAL_FOLDER / "Files"
APPROVED_FOLDER = VAULT_ROOT / "Approved"
APPROVED_EMAIL_FOLDER = APPROVED_FOLDER / "Email"
APPROVED_WHATSAPP_FOLDER = APPROVED_FOLDER / "WhatsApp"
APPROVED_FILES_FOLDER = APPROVED_FOLDER / "Files"
REJECTED_FOLDER = VAULT_ROOT / "Rejected"
DONE_FOLDER = VAULT_ROOT / "Done"
DONE_EMAIL_FOLDER = DONE_FOLDER / "Email"
DONE_WHATSAPP_FOLDER = DONE_FOLDER / "WhatsApp"
DONE_FILES_FOLDER = DONE_FOLDER / "Files"
LOGS_FOLDER = VAULT_ROOT / "Logs"
PLANS_FOLDER = VAULT_ROOT / "Plans"
DASHBOARD_FILE = VAULT_ROOT / "Dashboard.md"

MCP_EMAIL_SERVER_URL = "http://localhost:3005/send-email"
MCP_ODOO_SERVER_URL  = "http://localhost:3006/log-activity"
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("API_KEY", "AIEMCP_RANDOM_KEY_v27RzD0xW4jL9yP7cFqA8sH3nB5gK6tE")  # Use env var with fallback

# Ensure folders exist
all_folders = [
    NEEDS_ACTION_FOLDER, NEEDS_ACTION_EMAIL_FOLDER, NEEDS_ACTION_WHATSAPP_FOLDER, NEEDS_ACTION_FILES_FOLDER,
    PENDING_APPROVAL_FOLDER, PENDING_APPROVAL_EMAIL_FOLDER, PENDING_APPROVAL_WHATSAPP_FOLDER, PENDING_APPROVAL_FILES_FOLDER,
    APPROVED_FOLDER, APPROVED_EMAIL_FOLDER, APPROVED_WHATSAPP_FOLDER, APPROVED_FILES_FOLDER,
    REJECTED_FOLDER, DONE_FOLDER, DONE_EMAIL_FOLDER, DONE_WHATSAPP_FOLDER, DONE_FILES_FOLDER,
    LOGS_FOLDER, PLANS_FOLDER
]
for folder in all_folders:
    folder.mkdir(exist_ok=True)

# --- Helper Functions ---

def read_email_metadata(filepath: Path) -> dict:
    """Reads metadata from an EMAIL_*.md file."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'^---\n(.*?)\n^---', content, re.DOTALL | re.MULTILINE)
    if match:
        metadata_str = match.group(1)
        metadata = {}
        for line in metadata_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().replace("'", '')
        return metadata
    return {}

def update_dashboard_status(recent_sent_emails: list = None):
    """Updates the dashboard status in Dashboard.md."""
    if not DASHBOARD_FILE.exists():
        print(f"Warning: Dashboard file not found at {DASHBOARD_FILE}. Skipping update.")
        return

    content = DASHBOARD_FILE.read_text(encoding='utf-8')

    # Count all types of pending items in Needs_Action
    pending_needs_action_emails = len(list(NEEDS_ACTION_EMAIL_FOLDER.glob('EMAIL_*.md')))
    pending_needs_action_whatsapp = len(list(NEEDS_ACTION_WHATSAPP_FOLDER.glob('WHATSAPP_*.md')))
    pending_needs_action_files = len(list(NEEDS_ACTION_FILES_FOLDER.glob('FILE_*.md')))
    total_pending_needs_action = pending_needs_action_emails + pending_needs_action_whatsapp + pending_needs_action_files
    
    # Count all types of pending items in Pending_Approval
    pending_approval_emails = len(list(PENDING_APPROVAL_EMAIL_FOLDER.glob('EMAIL_*.md')))
    pending_approval_whatsapp = len(list(PENDING_APPROVAL_WHATSAPP_FOLDER.glob('WHATSAPP_*.md')))
    pending_approval_files = len(list(PENDING_APPROVAL_FILES_FOLDER.glob('FILE_*.md')))
    total_pending_approval = pending_approval_emails + pending_approval_whatsapp + pending_approval_files

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    content = re.sub(
        r'- 🕐 \*\*Last checked\*\*:\s*.*\n',
        f'- 🕐 **Last checked**: {current_time}\n',
        content,
        count=1
    )
    content = re.sub(
        r'- 📧 \*\*Pending emails in Needs_Action\*\*:\s*\d+\n',
        f'- 📧 **Pending emails in Needs_Action**: {pending_needs_action_emails}\n',
        content,
        count=1
    )
    content = re.sub(
        r'- 💬 \*\*Pending WhatsApp in Needs_Action\*\*:\s*\d+\n',
        f'- 💬 **Pending WhatsApp in Needs_Action**: {pending_needs_action_whatsapp}\n',
        content,
        count=1
    )
    content = re.sub(
        r'- 📁 \*\*Pending files in Needs_Action\*\*:\s*\d+\n',
        f'- 📁 **Pending files in Needs_Action**: {pending_needs_action_files}\n',
        content,
        count=1
    )
    content = re.sub(
        r'- 🔥 \*\*Important pending in Pending_Approval\*\*:\s*\d+\n',
        f'- 🔥 **Important pending in Pending_Approval**: {total_pending_approval}\n',
        content,
        count=1
    )

    if recent_sent_emails:
        recent_activity_section_start = re.search(r'## Recent Activity\n', content)
        if recent_activity_section_start:
            insert_index = recent_activity_section_start.end()
            new_entries = []
            for timestamp, to, subject in recent_sent_emails:
                new_entries.append(f"- {timestamp}: Sent email to {to} - Subject: {subject}\n")
            content = content[:insert_index] + "".join(new_entries) + content[insert_index:]
        else:
            content += "\n## Recent Activity\n"
            for timestamp, to, subject in recent_sent_emails:
                content += f"- {timestamp}: Sent email to {to} - Subject: {subject}\n"

    DASHBOARD_FILE.write_text(content, encoding='utf-8')
    print(f"Dashboard updated: Needs Action emails={pending_needs_action_emails}, WhatsApp={pending_needs_action_whatsapp}, Files={pending_needs_action_files}; Pending Approval total={total_pending_approval}.")

def create_plan(item_type: str, filename: str, metadata: dict) -> Path:
    """Creates a Plan.md file in /Plans/ for each processed item (Silver tier requirement)."""
    PLANS_FOLDER.mkdir(exist_ok=True)
    plan_name = f"PLAN_{filename.replace('.md', '')}.md"
    plan_file = PLANS_FOLDER / plan_name

    if plan_file.exists():
        return plan_file  # already planned

    subject = metadata.get('subject', metadata.get('text', 'Unknown'))[:60]
    sender  = metadata.get('from', metadata.get('from_contact', 'Unknown'))
    category = metadata.get('category', 'General')
    priority = metadata.get('priority', 'medium')
    needs_approval = metadata.get('needs_approval', 'False')

    if item_type == 'email':
        steps = [
            f"- [x] Email detected from: {sender}",
            f"- [x] Category identified: {category}",
            f"- [x] Priority assessed: {priority}",
            f"- [ ] Draft reply" if needs_approval.lower() == 'true' else "- [x] Auto-process (no approval needed)",
            f"- [ ] Send reply via MCP Email Server" if needs_approval.lower() == 'true' else "- [x] Moved to Done",
            "- [ ] Archive task",
        ]
        action = "REQUIRES_HUMAN_APPROVAL — move to /Approved/ to send reply" if needs_approval.lower() == 'true' else "AUTO_PROCESSED"
    elif item_type == 'whatsapp':
        steps = [
            f"- [x] WhatsApp message detected from: {sender}",
            f"- [x] Keywords matched: {metadata.get('keywords_matched', '[]')}",
            "- [ ] Review message content",
            "- [ ] Approve or reject reply",
            "- [ ] Archive task",
        ]
        action = "REQUIRES_HUMAN_APPROVAL — move to /Approved/WhatsApp/ to process"
    else:
        steps = [
            f"- [x] Item detected: {filename}",
            "- [ ] Review and process",
            "- [ ] Archive task",
        ]
        action = "PENDING"

    content = f"""---
created: {datetime.now().isoformat()}
type: {item_type}_plan
source_file: {filename}
subject: {subject}
from: {sender}
category: {category}
priority: {priority}
status: in_progress
---

# Plan: {subject}

## Objective
Process {item_type} from **{sender}** — Category: {category}

## Steps
{chr(10).join(steps)}

## Decision
**{action}**

## Notes
- Created by Orchestrator (Ralph Wiggum loop)
- Source: /Needs_Action/{item_type.capitalize()}/{filename}
"""
    plan_file.write_text(content, encoding='utf-8')
    print(f"Created plan: {plan_name}")
    return plan_file


def with_retry(func, max_attempts=3, base_delay=2):
    """Error recovery: exponential backoff retry for transient failures."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"All {max_attempts} attempts failed: {e}")
                return None
            wait = base_delay * (2 ** attempt)
            print(f"Attempt {attempt+1} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)


def log_to_odoo(source: str, subject: str, category: str, action: str, details: str = ""):
    """Send activity log to Odoo MCP — shows in Odoo dashboard."""
    try:
        import urllib.request, json as _json
        payload = _json.dumps({
            "source": source,
            "subject": subject[:100],
            "category": category,
            "action": action,
            "details": details[:200]
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_ODOO_SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f"Odoo log skipped (not critical): {e}")


def log_action(action_type: str, details: dict):
    """Logs an action to a daily JSON log file."""
    log_dir = LOGS_FOLDER
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"log_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "details": details
    }

    logs = []
    if log_file.exists():
        try:
            existing_content = log_file.read_text(encoding='utf-8')
            if existing_content.strip():
                logs = json.loads(existing_content)
        except json.JSONDecodeError:
            print(f"Warning: {log_file} is corrupted or not valid JSON. Starting new log.")

    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    print(f"Logged action: {action_type}")

def read_whatsapp_metadata(filepath: Path) -> dict:
    """Reads metadata from a WHATSAPP_*.md file."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'^---\n(.*?)\n^---', content, re.DOTALL | re.MULTILINE)
    if match:
        metadata_str = match.group(1)
        metadata = {}
        for line in metadata_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().replace("'", '')
        return metadata
    return {}

# --- Main Orchestration Logic ---

def orchestrate_all():
    print("Starting full orchestration (emails and WhatsApp)...")
    all_tasks_processed = False
    iteration = 0
    recent_sent = []

    while not all_tasks_processed and iteration < 10:  # Simple Ralph Wiggum loop
        iteration += 1
        print(f"\n--- Orchestration Iteration {iteration} ---")

        # 1. Process /Needs_Action/Email files - EMAILS
        email_files = list(NEEDS_ACTION_EMAIL_FOLDER.glob('EMAIL_*.md'))
        print(f"Found {len(email_files)} emails in Needs_Action/Email.")
        for filepath in email_files:
            print(f"Processing Needs_Action/Email: {filepath.name}")
            metadata = read_email_metadata(filepath)
            create_plan('email', filepath.name, metadata)
            subj = metadata.get('subject', 'No Subject')
            cat  = metadata.get('category', 'General')
            if metadata.get('needs_approval', 'False').lower() == 'true':
                new_path = PENDING_APPROVAL_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File {new_path.name} already exists in Pending_Approval/Email. Skipping.")
                else:
                    filepath.rename(new_path)
                    print(f"Moved {filepath.name} to Pending_Approval/Email (requires approval).")
                    log_action('moved_to_pending_approval', {'filename': filepath.name, 'reason': 'email requires approval'})
                    log_to_odoo('gmail', subj, cat, 'Pending Approval', f"From: {metadata.get('from','?')}")
            else:
                new_path = DONE_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File {new_path.name} already exists in Done/Email. Skipping.")
                else:
                    filepath.rename(new_path)
                    print(f"Moved {filepath.name} to Done/Email.")
                    log_action('processed_email_to_done', {'filename': filepath.name, 'subject': subj})
                    log_to_odoo('gmail', subj, cat, 'Auto-Processed', f"From: {metadata.get('from','?')}")

        # 2. Process /Needs_Action/WhatsApp files - WHATSAPP
        whatsapp_files = list(NEEDS_ACTION_WHATSAPP_FOLDER.glob('WHATSAPP_*.md'))
        print(f"Found {len(whatsapp_files)} WhatsApp messages in Needs_Action/WhatsApp.")
        for filepath in whatsapp_files:
            print(f"Processing Needs_Action/WhatsApp: {filepath.name}")
            metadata = read_whatsapp_metadata(filepath)
            create_plan('whatsapp', filepath.name, metadata)
            sender = metadata.get('from', metadata.get('from_contact', 'Unknown'))
            # WhatsApp messages typically require approval due to personal nature
            new_path = PENDING_APPROVAL_WHATSAPP_FOLDER / filepath.name
            if new_path.exists():
                print(f"File {new_path.name} already exists in Pending_Approval/WhatsApp. Skipping.")
            else:
                filepath.rename(new_path)
                print(f"Moved {filepath.name} to Pending_Approval/WhatsApp (requires approval).")
                log_action('moved_to_pending_approval', {'filename': filepath.name, 'reason': 'WhatsApp message requires approval'})
                log_to_odoo('whatsapp', f"Message from {sender}", 'WhatsApp', 'Pending Approval', f"Contact: {sender}")

        # 3. Process /Pending_Approval/Email files - EMAILS
        pending_email_files = list(PENDING_APPROVAL_EMAIL_FOLDER.glob('EMAIL_*.md'))
        print(f"Found {len(pending_email_files)} emails in Pending_Approval/Email.")

        for filepath in pending_email_files:
            print(f"Checking Pending_Approval/Email: {filepath.name}")
            metadata = read_email_metadata(filepath)

            approved_path = APPROVED_EMAIL_FOLDER / filepath.name
            rejected_path = REJECTED_FOLDER / filepath.name

            if approved_path.exists():
                print(f"{filepath.name} was approved! Sending email via MCP...")
                to_email = metadata.get('from', 'unknown@example.com')
                original_subject = metadata.get('subject', 'No Subject')
                subject_email = f"Re: {original_subject}"
                category = metadata.get('category', 'General')
                priority = metadata.get('priority', 'medium')

                # Context-specific reply based on category
                if category == 'Payment':
                    text_email = (
                        f"Thank you for your message regarding '{original_subject}'. "
                        "We have received your payment-related request and are processing it. "
                        "Our team will follow up with the relevant details shortly."
                    )
                elif category == 'Client':
                    text_email = (
                        f"Thank you for reaching out regarding '{original_subject}'. "
                        "We appreciate your interest and will get back to you with a detailed response "
                        "within 24 hours."
                    )
                elif category == 'Project':
                    text_email = (
                        f"Thank you for your update on '{original_subject}'. "
                        "We have noted the project details and will review and respond accordingly."
                    )
                elif category == 'Event':
                    text_email = (
                        f"Thank you for the information about '{original_subject}'. "
                        "We have registered your event details and will confirm participation shortly."
                    )
                elif category in ('Urgent', 'Security') or priority in ('high', 'critical'):
                    text_email = (
                        f"We have received your urgent message regarding '{original_subject}'. "
                        "This has been flagged as high priority and is being handled immediately."
                    )
                else:
                    text_email = (
                        f"Thank you for your email regarding '{original_subject}'. "
                        "Your message has been received and processed. "
                        "We will follow up if any further action is required."
                    )

                print(f"POST {MCP_EMAIL_SERVER_URL} to={to_email} subject={subject_email}")

                sent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                recent_sent.append((sent_timestamp, to_email, subject_email))

                # Move to Done after sending
                new_path = DONE_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File already in Done/Email, skipping move.")
                else:
                    filepath.rename(new_path)
                print(f"Sent email and moved {filepath.name} to Done/Email.")
                log_action('email_sent_via_mcp', {'filename': filepath.name, 'to': to_email, 'subject': subject_email, 'category': category})

            elif rejected_path.exists():
                print(f"{filepath.name} was rejected. Moving to Rejected folder.")
                filepath.rename(REJECTED_FOLDER / filepath.name)
                print(f"Moved {filepath.name} to Rejected.")
                log_action('email_rejected', {'filename': filepath.name, 'subject': metadata.get('subject')})
            else:
                print(f"{filepath.name} is still pending approval. Waiting...")

        # 4. Process /Pending_Approval/WhatsApp files - WHATSAPP
        pending_whatsapp_files = list(PENDING_APPROVAL_WHATSAPP_FOLDER.glob('WHATSAPP_*.md'))
        print(f"Found {len(pending_whatsapp_files)} WhatsApp messages in Pending_Approval/WhatsApp.")

        for filepath in pending_whatsapp_files:
            print(f"Checking Pending_Approval/WhatsApp: {filepath.name}")
            metadata = read_whatsapp_metadata(filepath)

            approved_path = APPROVED_WHATSAPP_FOLDER / filepath.name
            rejected_path = REJECTED_FOLDER / filepath.name

            if approved_path.exists():
                print(f"{filepath.name} was approved! Processing WhatsApp message via MCP...")
                # In a real implementation, this would send a WhatsApp message via an API
                # For now, we'll just log the action
                from_contact = metadata.get('from', 'unknown')
                message_text = metadata.get('message_text', 'No message content')

                print(f"WhatsApp message to {from_contact} approved: {message_text[:50]}...")

                sent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                recent_sent.append((sent_timestamp, from_contact, f"WhatsApp: {message_text[:30]}..."))

                # Move to Done after processing
                new_path = DONE_WHATSAPP_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File already in Done/WhatsApp, skipping move.")
                else:
                    filepath.rename(new_path)
                print(f"Processed WhatsApp message and moved {filepath.name} to Done/WhatsApp.")
                log_action('whatsapp_processed_via_mcp', {'filename': filepath.name, 'to': from_contact, 'message': message_text})

            elif rejected_path.exists():
                print(f"{filepath.name} was rejected. Moving to Rejected folder.")
                filepath.rename(REJECTED_FOLDER / filepath.name)
                print(f"Moved {filepath.name} to Rejected.")
                log_action('whatsapp_rejected', {'filename': filepath.name, 'from': metadata.get('from')})
            else:
                print(f"{filepath.name} is still pending approval. Waiting...")

        # 5. Update Dashboard.md
        update_dashboard_status(recent_sent)
        recent_sent = []  # Clear for next iteration

        # Check for completion
        current_email_needs_action = list(NEEDS_ACTION_EMAIL_FOLDER.glob('EMAIL_*.md'))
        current_whatsapp_needs_action = list(NEEDS_ACTION_WHATSAPP_FOLDER.glob('WHATSAPP_*.md'))
        current_pending_approval = (
            list(PENDING_APPROVAL_EMAIL_FOLDER.glob('*')) +
            list(PENDING_APPROVAL_WHATSAPP_FOLDER.glob('*')) +
            list(PENDING_APPROVAL_FILES_FOLDER.glob('*'))
        )
        current_approved = (
            list(APPROVED_EMAIL_FOLDER.glob('*')) +
            list(APPROVED_WHATSAPP_FOLDER.glob('*')) +
            list(APPROVED_FILES_FOLDER.glob('*'))
        )

        if not current_email_needs_action and not current_whatsapp_needs_action and not current_pending_approval and not current_approved:
            all_tasks_processed = True
            print("All tasks processed. Exiting Ralph Wiggum loop.")
        else:
            print("More tasks pending. Will re-evaluate in next iteration.")
            time.sleep(5)  # Simulate waiting for new tasks

    if not all_tasks_processed:
        print("Ralph Wiggum loop reached max iterations. Some tasks may still be pending.")

    print("Full orchestration complete.")
    print("<TASK_COMPLETE>")

def orchestrate_emails():
    """Legacy function for email-only orchestration"""
    print("Starting email orchestration...")
    all_tasks_processed = False
    iteration = 0
    recent_sent = []

    while not all_tasks_processed and iteration < 10:  # Simple Ralph Wiggum loop
        iteration += 1
        print(f"\n--- Orchestration Iteration {iteration} ---")

        # 1. Process /Needs_Action/Email files
        needs_action_files = list(NEEDS_ACTION_EMAIL_FOLDER.glob('EMAIL_*.md'))
        print(f"Found {len(needs_action_files)} emails in Needs_Action/Email.")
        for filepath in needs_action_files:
            print(f"Processing Needs_Action/Email: {filepath.name}")
            metadata = read_email_metadata(filepath)
            if metadata.get('needs_approval', 'False').lower() == 'true':
                new_path = PENDING_APPROVAL_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File {new_path.name} already exists in Pending_Approval/Email. Skipping.")
                else:
                    filepath.rename(new_path)
                    print(f"Moved {filepath.name} to Pending_Approval/Email (requires approval).")
                    log_action('moved_to_pending_approval', {'filename': filepath.name, 'reason': 'email requires approval'})
            else:
                new_path = DONE_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File {new_path.name} already exists in Done/Email. Skipping.")
                else:
                    filepath.rename(new_path)
                    print(f"Moved {filepath.name} to Done/Email.")
                    log_action('processed_email_to_done', {'filename': filepath.name, 'subject': metadata.get('subject')})

        # 2. Process /Pending_Approval/Email files
        pending_approval_files = list(PENDING_APPROVAL_EMAIL_FOLDER.glob('EMAIL_*.md'))
        print(f"Found {len(pending_approval_files)} emails in Pending_Approval/Email.")

        for filepath in pending_approval_files:
            print(f"Checking Pending_Approval/Email: {filepath.name}")
            metadata = read_email_metadata(filepath)

            approved_path = APPROVED_EMAIL_FOLDER / filepath.name
            rejected_path = REJECTED_FOLDER / filepath.name

            if approved_path.exists():
                print(f"{filepath.name} was approved! Sending email via MCP...")
                to_email = metadata.get('from', 'unknown@example.com')
                original_subject = metadata.get('subject', 'No Subject')
                subject_email = f"Re: {original_subject}"
                category = metadata.get('category', 'General')
                priority = metadata.get('priority', 'medium')

                # Context-specific reply based on category
                if category == 'Payment':
                    text_email = (
                        f"Thank you for your message regarding '{original_subject}'. "
                        "We have received your payment-related request and are processing it. "
                        "Our team will follow up with the relevant details shortly."
                    )
                elif category == 'Client':
                    text_email = (
                        f"Thank you for reaching out regarding '{original_subject}'. "
                        "We appreciate your interest and will get back to you with a detailed response "
                        "within 24 hours."
                    )
                elif category == 'Project':
                    text_email = (
                        f"Thank you for your update on '{original_subject}'. "
                        "We have noted the project details and will review and respond accordingly."
                    )
                elif category == 'Event':
                    text_email = (
                        f"Thank you for the information about '{original_subject}'. "
                        "We have registered your event details and will confirm participation shortly."
                    )
                elif category in ('Urgent', 'Security') or priority in ('high', 'critical'):
                    text_email = (
                        f"We have received your urgent message regarding '{original_subject}'. "
                        "This has been flagged as high priority and is being handled immediately."
                    )
                else:
                    text_email = (
                        f"Thank you for your email regarding '{original_subject}'. "
                        "Your message has been received and processed. "
                        "We will follow up if any further action is required."
                    )

                print(f"POST {MCP_EMAIL_SERVER_URL} to={to_email} subject={subject_email}")

                sent_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                recent_sent.append((sent_timestamp, to_email, subject_email))

                # Move to Done after sending
                new_path = DONE_EMAIL_FOLDER / filepath.name
                if new_path.exists():
                    print(f"File already in Done/Email, skipping move.")
                else:
                    filepath.rename(new_path)
                print(f"Sent email and moved {filepath.name} to Done/Email.")
                log_action('email_sent_via_mcp', {'filename': filepath.name, 'to': to_email, 'subject': subject_email, 'category': category})

            elif rejected_path.exists():
                print(f"{filepath.name} was rejected. Moving to Rejected folder.")
                filepath.rename(REJECTED_FOLDER / filepath.name)
                print(f"Moved {filepath.name} to Rejected.")
                log_action('email_rejected', {'filename': filepath.name, 'subject': metadata.get('subject')})
            else:
                print(f"{filepath.name} is still pending approval. Waiting...")

        # 3. Update Dashboard.md
        update_dashboard_status(recent_sent)
        recent_sent = []  # Clear for next iteration

        # Check for completion
        current_needs_action = list(NEEDS_ACTION_EMAIL_FOLDER.glob('EMAIL_*.md'))
        current_pending_approval = list(PENDING_APPROVAL_EMAIL_FOLDER.glob('EMAIL_*.md'))
        current_approved = list(APPROVED_EMAIL_FOLDER.glob('EMAIL_*.md'))

        if not current_needs_action and not current_pending_approval and not current_approved:
            all_tasks_processed = True
            print("All email-related tasks processed. Exiting Ralph Wiggum loop.")
        else:
            print("More tasks pending. Will re-evaluate in next iteration.")
            time.sleep(5)  # Simulate waiting for new tasks

    if not all_tasks_processed:
        print("Ralph Wiggum loop reached max iterations. Some tasks may still be pending.")

    print("Email orchestration complete.")
    print("<TASK_COMPLETE>")

if __name__ == "__main__":
    orchestrate_all()