#!/usr/bin/env python3
"""
Migration script to move existing files from the main Needs_Action folder
to their respective subdirectories (Email, WhatsApp, Files).
"""
import os
from pathlib import Path
import shutil

def migrate_existing_files():
    # Define paths
    vault_root = Path("F:/AI_Employee_Vault/AI_Employee_Vault")
    needs_action_folder = vault_root / "Needs_Action"
    
    # Subdirectories
    email_folder = needs_action_folder / "Email"
    whatsapp_folder = needs_action_folder / "WhatsApp"
    files_folder = needs_action_folder / "Files"
    
    # Create subdirectories if they don't exist
    email_folder.mkdir(exist_ok=True)
    whatsapp_folder.mkdir(exist_ok=True)
    files_folder.mkdir(exist_ok=True)
    
    # Get all files in the main Needs_Action folder
    all_files = [f for f in needs_action_folder.iterdir() if f.is_file()]
    
    email_count = 0
    whatsapp_count = 0
    files_count = 0
    others_count = 0
    
    for file_path in all_files:
        filename = file_path.name
        
        # Skip directories and temporary files
        if file_path.is_dir() or filename.startswith('FILE_tmp'):
            continue
            
        # Determine destination based on filename prefix
        if filename.startswith('EMAIL_'):
            dest_path = email_folder / filename
            email_count += 1
        elif filename.startswith('WHATSAPP_'):
            dest_path = whatsapp_folder / filename
            whatsapp_count += 1
        elif filename.startswith('FILE_'):
            dest_path = files_folder / filename
            files_count += 1
        else:
            # For files that don't match known prefixes, put them in Files folder
            dest_path = files_folder / filename
            others_count += 1
        
        # Move the file
        shutil.move(str(file_path), str(dest_path))
        print(f"Moved: {filename} -> {dest_path.parent.name}/")
    
    print(f"\nMigration complete!")
    print(f"Email files moved: {email_count}")
    print(f"WhatsApp files moved: {whatsapp_count}")
    print(f"File files moved: {files_count}")
    print(f"Other files moved: {others_count}")

if __name__ == "__main__":
    migrate_existing_files()