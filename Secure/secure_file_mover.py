"""
Secure File Mover

This script helps organize sensitive files into secure locations that won't be synced
according to the Platinum tier security requirements.
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

def identify_sensitive_directories(vault_path: str) -> List[Path]:
    """Identify directories that contain sensitive files"""
    vault_path = Path(vault_path)
    sensitive_dirs = []
    
    # Directories that should be kept private
    private_dirs = [
        "whatsapp_session",
        "watchers_gmail/mcp",
        "watchers_gmail",
        "watchers_whatsapp"
    ]
    
    for dir_name in private_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists():
            sensitive_dirs.append(dir_path)
    
    return sensitive_dirs

def create_secure_storage(vault_path: str) -> Path:
    """Create a secure storage location outside the vault"""
    vault_path = Path(vault_path)
    
    # Create a secure directory outside the vault for sensitive files
    secure_root = vault_path.parent / "AI_Employee_Private"
    secure_root.mkdir(exist_ok=True)
    
    # Create subdirectories for different types of sensitive data
    (secure_root / "credentials").mkdir(exist_ok=True)
    (secure_root / "sessions").mkdir(exist_ok=True)
    (secure_root / "tokens").mkdir(exist_ok=True)
    
    return secure_root

def move_sensitive_files(vault_path: str) -> Tuple[List[str], List[str]]:
    """Move sensitive files to secure locations"""
    vault_path = Path(vault_path)
    secure_root = create_secure_storage(str(vault_path))
    
    moved_files = []
    skipped_files = []  # Files that couldn't be moved (in use, etc.)
    
    # Define patterns of sensitive files to move
    sensitive_patterns = [
        ".env",
        "*.env",
        "*token.json",
        "*credential*",
        "*auth.py",
        "client_secret.json",
    ]
    
    # Move sensitive files to secure locations
    for pattern in sensitive_patterns:
        for file_path in vault_path.rglob(pattern):
            if file_path.is_file():
                try:
                    # Determine destination based on file type
                    if "token" in file_path.name:
                        dest_dir = secure_root / "tokens"
                    elif "credential" in file_path.name or "auth" in file_path.name:
                        dest_dir = secure_root / "credentials"
                    elif "client_secret" in file_path.name:
                        dest_dir = secure_root / "credentials"
                    else:
                        dest_dir = secure_root / "credentials"
                    
                    dest_path = dest_dir / file_path.name
                    shutil.move(str(file_path), str(dest_path))
                    moved_files.append(f"Moved {file_path} to {dest_path}")
                    print(f"Moved sensitive file: {file_path} -> {dest_path}")
                except Exception as e:
                    skipped_files.append(f"Could not move {file_path}: {str(e)}")
                    print(f"Warning: Could not move {file_path}: {str(e)}")
    
    # Specifically handle the whatsapp_session directory
    whatsapp_session = vault_path / "whatsapp_session"
    if whatsapp_session.exists():
        try:
            dest_path = secure_root / "sessions" / "whatsapp_session"
            if dest_path.exists():
                # If destination exists, we'll just warn the user
                skipped_files.append(f"Skipped moving whatsapp_session - destination exists: {dest_path}")
                print(f"Note: whatsapp_session not moved - destination exists at {dest_path}")
            else:
                shutil.move(str(whatsapp_session), str(dest_path))
                moved_files.append(f"Moved {whatsapp_session} to {dest_path}")
                print(f"Moved sensitive directory: {whatsapp_session} -> {dest_path}")
        except Exception as e:
            skipped_files.append(f"Could not move {whatsapp_session}: {str(e)}")
            print(f"Warning: Could not move {whatsapp_session}: {str(e)}")
    
    # Handle watchers credential directories
    watcher_dirs = ["watchers_gmail", "watchers_whatsapp"]
    for watcher_dir in watcher_dirs:
        watcher_path = vault_path / watcher_dir
        if watcher_path.exists():
            try:
                # Look for credential files in these directories
                for cred_file in watcher_path.rglob("*"):
                    if (cred_file.is_file() and 
                        ("token" in cred_file.name or 
                         "credential" in cred_file.name or 
                         "auth" in cred_file.name or
                         cred_file.name == "client_secret.json")):
                        dest_path = secure_root / "credentials" / cred_file.name
                        shutil.move(str(cred_file), str(dest_path))
                        moved_files.append(f"Moved {cred_file} to {dest_path}")
                        print(f"Moved sensitive file: {cred_file} -> {dest_path}")
            except Exception as e:
                skipped_files.append(f"Could not process {watcher_dir}: {str(e)}")
    
    return moved_files, skipped_files

def create_symlinks_or_placeholders(vault_path: str):
    """Create placeholders or symlinks for moved sensitive files"""
    vault_path = Path(vault_path)
    secure_root = vault_path.parent / "AI_Employee_Private"
    
    # Create a README in the vault explaining where sensitive files went
    readme_path = vault_path / "SENSITIVE_FILES_MOVED_README.md"
    readme_content = f"""# Sensitive Files Moved Notice

Sensitive files have been moved to a secure location outside the vault for security reasons.

Secure storage location: {secure_root}

Moved files include:
- Authentication tokens
- Credentials
- Session files
- Environment files

These files are not synced to maintain security as per Platinum tier requirements.
"""
    readme_path.write_text(readme_content)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python secure_file_mover.py <vault_path>")
        print("This script moves sensitive files to secure locations outside the vault.")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    print("=== Secure File Mover ===")
    print(f"Processing vault: {vault_path}")
    print()
    
    # First, show what will be moved
    print("Identifying sensitive files...")
    sensitive_patterns = [
        ".env", "*.env", "*token.json", "*credential*", "*auth.py", "client_secret.json"
    ]
    
    vault_path_obj = Path(vault_path)
    for pattern in sensitive_patterns:
        files = list(vault_path_obj.rglob(pattern))
        if files:
            print(f"Found {len(files)} files matching pattern '{pattern}':")
            for file in files:
                print(f"  - {file}")
    
    whatsapp_session = vault_path_obj / "whatsapp_session"
    if whatsapp_session.exists():
        print(f"Found sensitive directory: {whatsapp_session}")
    
    print("\nMoving sensitive files (non-interactive mode)...")
    moved_files, skipped_files = move_sensitive_files(vault_path)
    
    print(f"\nCreated secure storage at: {vault_path_obj.parent / 'AI_Employee_Private'}")
    create_symlinks_or_placeholders(vault_path)
    
    print(f"\nSummary:")
    print(f"- Successfully moved {len(moved_files)} files")
    print(f"- Skipped {len(skipped_files)} files")
    
    if moved_files:
        print("\nMoved files:")
        for item in moved_files:
            print(f"  - {item}")
    
    if skipped_files:
        print("\nSkipped files:")
        for item in skipped_files:
            print(f"  - {item}")
    
    print(f"\nThe sensitive files have been moved to a secure location outside the vault.")
    print(f"They will not be included in any sync operations, maintaining security as required by the Platinum tier.")

if __name__ == "__main__":
    main()