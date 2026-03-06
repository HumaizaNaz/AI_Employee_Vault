"""
Cloud Orchestrator - Draft-Only Mode

This orchestrator runs on the cloud VM and NEVER sends directly.
All actions create drafts and approval requests for the Local machine to review.
"""

import os
import re
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
VAULT_ROOT = Path(os.environ.get("VAULT_PATH", "/home/ubuntu/ai-employee-vault"))
POLL_INTERVAL = int(os.environ.get("CLOUD_POLL_INTERVAL", "30"))  # seconds

# Folders
NEEDS_ACTION_FOLDER = VAULT_ROOT / "Needs_Action"
NEEDS_ACTION_EMAIL = NEEDS_ACTION_FOLDER / "Email"
NEEDS_ACTION_WHATSAPP = NEEDS_ACTION_FOLDER / "WhatsApp"
NEEDS_ACTION_FILES = NEEDS_ACTION_FOLDER / "Files"
DRAFTS_FOLDER = VAULT_ROOT / "Drafts"
PENDING_APPROVAL_FOLDER = VAULT_ROOT / "Pending_Approval"
PENDING_APPROVAL_EMAIL = PENDING_APPROVAL_FOLDER / "Email"
SIGNALS_FOLDER = VAULT_ROOT / "Signals"
UPDATES_FOLDER = VAULT_ROOT / "Updates"
LOGS_FOLDER = VAULT_ROOT / "Logs"

# Ensure all folders exist
for folder in [
    NEEDS_ACTION_FOLDER, NEEDS_ACTION_EMAIL, NEEDS_ACTION_WHATSAPP, NEEDS_ACTION_FILES,
    DRAFTS_FOLDER, PENDING_APPROVAL_FOLDER, PENDING_APPROVAL_EMAIL,
    SIGNALS_FOLDER, UPDATES_FOLDER, LOGS_FOLDER
]:
    folder.mkdir(parents=True, exist_ok=True)


def read_metadata(filepath: Path) -> dict:
    """Reads YAML-like metadata from a markdown file's frontmatter."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'^---\n(.*?)\n^---', content, re.DOTALL | re.MULTILINE)
    if match:
        metadata = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().replace("'", '')
        return metadata
    return {}


def log_action(action_type: str, details: dict):
    """Logs an action to a daily JSON log file."""
    log_file = LOGS_FOLDER / f"cloud_log_{datetime.now().strftime('%Y-%m-%d')}.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "source": "cloud_orchestrator",
        "details": details
    }

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass

    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    print(f"[CLOUD LOG] {action_type}: {details}")


def create_draft(original_file: Path, metadata: dict) -> Path:
    """Create a draft file from a Needs_Action item. NEVER sends directly."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    draft_name = f"DRAFT_{original_file.stem}_{timestamp}.md"
    draft_path = DRAFTS_FOLDER / draft_name

    original_content = original_file.read_text(encoding='utf-8')

    draft_content = f"""---
type: draft_response
original_file: {original_file.name}
created: {datetime.now().isoformat()}
created_by: cloud_orchestrator
status: pending_approval
from: {metadata.get('from', 'unknown')}
subject: {metadata.get('subject', 'No Subject')}
priority: {metadata.get('priority', 'normal')}
---

# Draft Response

**Original:** {metadata.get('subject', original_file.name)}
**From:** {metadata.get('from', 'unknown')}
**Created by:** Cloud Orchestrator (draft-only mode)

## Original Content
{original_content}

## Suggested Response
> [AI Employee will generate response here based on context]

## Actions Required
- [ ] Review this draft on Local machine
- [ ] Approve: Move to `/Approved/` folder
- [ ] Reject: Move to `/Rejected/` folder
"""

    draft_path.write_text(draft_content, encoding='utf-8')
    return draft_path


def create_approval_request(original_file: Path, draft_path: Path, metadata: dict) -> Path:
    """Create an approval request file for the Local machine to pick up."""
    approval_name = f"APPROVAL_{original_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    approval_path = PENDING_APPROVAL_EMAIL / approval_name

    approval_content = f"""---
type: approval_request
original_file: {original_file.name}
draft_file: {draft_path.name}
created: {datetime.now().isoformat()}
created_by: cloud_orchestrator
status: pending
from: {metadata.get('from', 'unknown')}
subject: {metadata.get('subject', 'No Subject')}
needs_approval: 'True'
---

# Approval Request

**From:** {metadata.get('from', 'unknown')}
**Subject:** {metadata.get('subject', 'No Subject')}
**Draft:** {draft_path.name}
**Priority:** {metadata.get('priority', 'normal')}

## Action Required
This item was processed by the Cloud Orchestrator and requires your approval.

- To **approve**: Move this file to `/Approved/Email/`
- To **reject**: Move this file to `/Rejected/`
"""

    approval_path.write_text(approval_content, encoding='utf-8')
    return approval_path


def write_signal(signal_type: str, details: dict):
    """Write a signal file for Local to pick up."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    signal_name = f"SIGNAL_{signal_type}_{timestamp}.json"
    signal_path = SIGNALS_FOLDER / signal_name

    signal_data = {
        "type": signal_type,
        "timestamp": datetime.now().isoformat(),
        "source": "cloud_orchestrator",
        "details": details
    }

    signal_path.write_text(json.dumps(signal_data, indent=2), encoding='utf-8')
    print(f"[SIGNAL] {signal_type}: {signal_name}")


def update_cloud_status(stats: dict):
    """Update cloud status file (NOT Dashboard.md - that's Local-only)."""
    status_path = UPDATES_FOLDER / "cloud_status.md"

    content = f"""# Cloud Orchestrator Status

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode:** Draft-Only (NEVER sends directly)
**Status:** Running

## Counters
- Emails processed this session: {stats.get('emails_processed', 0)}
- Drafts created: {stats.get('drafts_created', 0)}
- Approval requests created: {stats.get('approvals_created', 0)}
- Signals sent: {stats.get('signals_sent', 0)}

## Recent Activity
"""
    for activity in stats.get('recent_activity', [])[-10:]:
        content += f"- {activity}\n"

    status_path.write_text(content, encoding='utf-8')


def process_needs_action_emails(stats: dict):
    """Process all emails in Needs_Action/Email -> create drafts + approval requests."""
    email_files = list(NEEDS_ACTION_EMAIL.glob('EMAIL_*.md'))

    if not email_files:
        return

    print(f"[CLOUD] Found {len(email_files)} emails in Needs_Action/Email")

    for filepath in email_files:
        try:
            metadata = read_metadata(filepath)
            print(f"[CLOUD] Processing: {filepath.name} from={metadata.get('from', '?')}")

            # Create draft (NEVER send directly)
            draft_path = create_draft(filepath, metadata)
            stats['drafts_created'] += 1

            # Create approval request
            approval_path = create_approval_request(filepath, draft_path, metadata)
            stats['approvals_created'] += 1

            # Signal Local that new items need attention
            write_signal("new_draft", {
                "original": filepath.name,
                "draft": draft_path.name,
                "approval": approval_path.name,
                "from": metadata.get('from', 'unknown'),
                "subject": metadata.get('subject', 'No Subject')
            })
            stats['signals_sent'] += 1

            # Move original out of Needs_Action (to avoid reprocessing)
            processed_folder = VAULT_ROOT / "Needs_Action" / "Processed"
            processed_folder.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(processed_folder / filepath.name))

            activity = f"{datetime.now().strftime('%H:%M:%S')} - Drafted response for: {metadata.get('subject', filepath.name)}"
            stats['recent_activity'].append(activity)
            stats['emails_processed'] += 1

            log_action('email_drafted', {
                'original': filepath.name,
                'draft': draft_path.name,
                'approval': approval_path.name,
                'from': metadata.get('from'),
                'subject': metadata.get('subject')
            })

        except Exception as e:
            print(f"[CLOUD ERROR] Failed to process {filepath.name}: {e}")
            log_action('processing_error', {
                'file': filepath.name,
                'error': str(e)
            })


def run_cloud_orchestrator():
    """Main loop for the cloud orchestrator."""
    print("=" * 60)
    print("  CLOUD ORCHESTRATOR - DRAFT-ONLY MODE")
    print("  NEVER sends emails, messages, or posts directly.")
    print("  All actions create drafts for Local approval.")
    print("=" * 60)
    print(f"  Vault: {VAULT_ROOT}")
    print(f"  Poll interval: {POLL_INTERVAL}s")
    print("=" * 60)

    stats = {
        'emails_processed': 0,
        'drafts_created': 0,
        'approvals_created': 0,
        'signals_sent': 0,
        'recent_activity': []
    }

    iteration = 0
    while True:
        iteration += 1
        try:
            print(f"\n--- Cloud Orchestration Cycle {iteration} ---")

            # Process emails
            process_needs_action_emails(stats)

            # Update cloud status
            update_cloud_status(stats)

            print(f"[CLOUD] Cycle {iteration} complete. "
                  f"Drafts={stats['drafts_created']}, "
                  f"Approvals={stats['approvals_created']}")

        except Exception as e:
            print(f"[CLOUD ERROR] Cycle {iteration} failed: {e}")
            log_action('cycle_error', {'iteration': iteration, 'error': str(e)})

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_cloud_orchestrator()
