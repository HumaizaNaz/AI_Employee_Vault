"""
Sync Manager - Git-based Vault Sync

Handles automated git sync between Cloud and Local machines.
Cloud: auto-commits and pushes new drafts/signals/logs every N minutes.
Local: pulls cloud changes.

SECURITY: Only syncs .md and .json files. Never syncs .env, tokens, credentials, sessions.
"""

import os
import re
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

VAULT_ROOT = Path(os.environ.get("VAULT_PATH", "/home/ubuntu/ai-employee-vault"))
SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", "300"))  # 5 minutes
SYNC_MODE = os.environ.get("SYNC_MODE", "cloud")  # "cloud" or "local"
SIGNALS_FOLDER = VAULT_ROOT / "Signals"
LOGS_FOLDER = VAULT_ROOT / "Logs"

SIGNALS_FOLDER.mkdir(parents=True, exist_ok=True)
LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

# Files/patterns that are SAFE to sync
SAFE_EXTENSIONS = {'.md', '.json'}

# Files/patterns that must NEVER be synced
BLOCKED_PATTERNS = [
    '.env',
    '*.env',
    '.env.*',
    'token.json',
    'tokens.json',
    'credentials.json',
    'client_secret*.json',
    '*.key',
    '*.pem',
    '*.p12',
    'session*',
    '*.session',
    '__pycache__/',
    'venv/',
    'node_modules/',
    '.git/',
    'nul',
]

# Folders that cloud is allowed to push changes from
CLOUD_SYNC_FOLDERS = [
    'Drafts',
    'Signals',
    'Updates',
    'Logs',
    'Pending_Approval',
    'Needs_Action/Processed',
]


def run_git(args: str, cwd: str = None) -> tuple:
    """Run a git command and return (success, output)."""
    cmd = f"git {args}"
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=60, cwd=cwd or str(VAULT_ROOT)
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        return result.returncode == 0, output or error
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def is_safe_file(filepath: str) -> bool:
    """Check if a file is safe to sync (only .md and .json, not in blocked list)."""
    path = Path(filepath)

    # Check extension
    if path.suffix.lower() not in SAFE_EXTENSIONS:
        return False

    # Check against blocked patterns
    name = path.name.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return False
        elif name == pattern.lower():
            return False

    # Check parent dirs aren't blocked
    parts = str(filepath).replace('\\', '/').split('/')
    for part in parts:
        if part in ('__pycache__', 'venv', 'node_modules', '.git'):
            return False

    return True


def get_changed_files() -> list:
    """Get list of changed files that are safe to sync."""
    success, output = run_git("status --porcelain")
    if not success:
        print(f"[SYNC] Git status failed: {output}")
        return []

    safe_files = []
    for line in output.split('\n'):
        if not line.strip():
            continue
        # Git status format: "XY filename" or "XY filename -> newname"
        filepath = line[3:].strip().split(' -> ')[-1].strip('"')
        if is_safe_file(filepath):
            safe_files.append(filepath)
        else:
            print(f"[SYNC] Skipping unsafe file: {filepath}")

    return safe_files


def cloud_sync():
    """Cloud sync: commit and push safe files."""
    print(f"\n[SYNC] Cloud sync cycle at {datetime.now().strftime('%H:%M:%S')}")

    # Get safe changed files
    changed = get_changed_files()
    if not changed:
        print("[SYNC] No safe files to sync")
        return

    print(f"[SYNC] Found {len(changed)} safe files to sync")

    # Stage only safe files
    for filepath in changed:
        success, output = run_git(f'add "{filepath}"')
        if not success:
            print(f"[SYNC] Failed to add {filepath}: {output}")

    # Commit
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"cloud-sync: {len(changed)} files at {timestamp}"
    success, output = run_git(f'commit -m "{commit_msg}"')
    if not success:
        if "nothing to commit" in output:
            print("[SYNC] Nothing to commit")
            return
        print(f"[SYNC] Commit failed: {output}")
        return

    print(f"[SYNC] Committed: {commit_msg}")

    # Push
    success, output = run_git("push")
    if success:
        print("[SYNC] Pushed to remote successfully")
        log_sync("cloud_push", {"files": changed, "commit_msg": commit_msg})
    else:
        print(f"[SYNC] Push failed: {output}")
        log_sync("cloud_push_failed", {"error": output})


def local_pull():
    """Local sync: pull changes from remote."""
    print(f"\n[SYNC] Local pull at {datetime.now().strftime('%H:%M:%S')}")

    success, output = run_git("pull --rebase")
    if success:
        if "Already up to date" in output:
            print("[SYNC] Already up to date")
        else:
            print(f"[SYNC] Pulled changes: {output}")
            log_sync("local_pull", {"output": output})
    else:
        print(f"[SYNC] Pull failed: {output}")
        # Try to recover from rebase conflict
        if "CONFLICT" in output:
            print("[SYNC] Conflict detected, aborting rebase")
            run_git("rebase --abort")
            log_sync("local_pull_conflict", {"error": output})


def log_sync(action: str, details: dict):
    """Log sync actions."""
    log_file = LOGS_FOLDER / f"sync_log_{datetime.now().strftime('%Y-%m-%d')}.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "mode": SYNC_MODE,
        "details": details
    }

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass

    logs.append(entry)
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def ensure_gitignore():
    """Ensure .gitignore blocks sensitive files."""
    gitignore_path = VAULT_ROOT / ".gitignore"
    required_entries = [
        "# Security: never sync secrets",
        ".env",
        ".env.*",
        "*.env",
        "token.json",
        "tokens.json",
        "credentials.json",
        "client_secret*.json",
        "*.key",
        "*.pem",
        "*.p12",
        "session*",
        "*.session",
        "__pycache__/",
        "venv/",
        "node_modules/",
        "nul",
        "",
        "# Only sync .md and .json via sync_manager",
        "# Python bytecode",
        "*.pyc",
        "*.pyo",
    ]

    existing = ""
    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding='utf-8')

    missing = []
    for entry in required_entries:
        if entry and entry not in existing:
            missing.append(entry)

    if missing:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n# === Sync Manager Security Rules ===\n')
            for entry in missing:
                f.write(entry + '\n')
        print(f"[SYNC] Updated .gitignore with {len(missing)} security rules")


def run_sync_manager():
    """Main sync loop."""
    print("=" * 50)
    print(f"  SYNC MANAGER - Mode: {SYNC_MODE.upper()}")
    print(f"  Interval: {SYNC_INTERVAL}s")
    print(f"  Safe extensions: {SAFE_EXTENSIONS}")
    print("=" * 50)

    ensure_gitignore()

    while True:
        try:
            if SYNC_MODE == "cloud":
                cloud_sync()
            elif SYNC_MODE == "local":
                local_pull()
            else:
                print(f"[SYNC] Unknown mode: {SYNC_MODE}")
        except Exception as e:
            print(f"[SYNC ERROR] {e}")
            log_sync("error", {"error": str(e)})

        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pull":
            local_pull()
        elif sys.argv[1] == "--push":
            cloud_sync()
        elif sys.argv[1] == "--check":
            ensure_gitignore()
            files = get_changed_files()
            print(f"Safe files to sync: {len(files)}")
            for f in files:
                print(f"  {f}")
        else:
            print("Usage: sync_manager.py [--pull|--push|--check]")
    else:
        run_sync_manager()
