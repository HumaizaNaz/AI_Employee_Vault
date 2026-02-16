#!/usr/bin/env python3
"""
Approval Manager - A script to help manage the approval/pending system for 
Gmail, WhatsApp, and Files in the organized folder structure.
"""

import os
from pathlib import Path
import shutil
from datetime import datetime

def show_pending_items():
    """Show all pending items across all categories"""
    vault_root = Path("F:/AI_Employee_Vault/AI_Employee_Vault")
    
    # Categories
    categories = {
        'Email': vault_root / 'Pending_Approval' / 'Email',
        'WhatsApp': vault_root / 'Pending_Approval' / 'WhatsApp',
        'Files': vault_root / 'Pending_Approval' / 'Files'
    }
    
    print("=== PENDING APPROVAL ITEMS ===")
    total_pending = 0
    
    for category, folder in categories.items():
        if folder.exists():
            files = list(folder.glob('*'))
            print(f"\n{category} ({len(files)} items):")
            for file in files:
                print(f"  - {file.name}")
            total_pending += len(files)
    
    print(f"\nTotal pending items: {total_pending}")
    
    # Also show items in Needs_Action
    needs_action_categories = {
        'Email': vault_root / 'Needs_Action' / 'Email',
        'WhatsApp': vault_root / 'Needs_Action' / 'WhatsApp',
        'Files': vault_root / 'Needs_Action' / 'Files'
    }
    
    print("\n=== NEEDS ACTION ITEMS ===")
    total_needs_action = 0
    
    for category, folder in needs_action_categories.items():
        if folder.exists():
            files = list(folder.glob('*'))
            print(f"\n{category} ({len(files)} items):")
            for file in files:
                print(f"  - {file.name}")
            total_needs_action += len(files)
    
    print(f"\nTotal needs action items: {total_needs_action}")

def approve_item(category, filename):
    """Move an item from Pending_Approval to Approved folder"""
    vault_root = Path("F:/AI_Employee_Vault/AI_Employee_Vault")
    
    pending_folder = vault_root / 'Pending_Approval' / category
    approved_folder = vault_root / 'Approved' / category
    
    pending_file = pending_folder / filename
    approved_file = approved_folder / filename
    
    if not pending_file.exists():
        print(f"Error: File {filename} not found in Pending_Approval/{category}/")
        return False
    
    # Move to approved folder
    approved_folder.mkdir(exist_ok=True)
    shutil.move(str(pending_file), str(approved_file))
    print(f"Approved: {filename} -> Approved/{category}/")
    return True

def reject_item(category, filename):
    """Move an item from Pending_Approval to Rejected folder"""
    vault_root = Path("F:/AI_Employee_Vault/AI_Employee_Vault")
    
    pending_folder = vault_root / 'Pending_Approval' / category
    rejected_folder = vault_root / 'Rejected'
    
    pending_file = pending_folder / filename
    rejected_file = rejected_folder / filename
    
    if not pending_file.exists():
        print(f"Error: File {filename} not found in Pending_Approval/{category}/")
        return False
    
    # Move to rejected folder
    rejected_folder.mkdir(exist_ok=True)
    shutil.move(str(pending_file), str(rejected_file))
    print(f"Rejected: {filename} -> Rejected/")
    return True

def move_to_pending(category, filename):
    """Move an item from Needs_Action to Pending_Approval folder"""
    vault_root = Path("F:/AI_Employee_Vault/AI_Employee_Vault")
    
    needs_action_folder = vault_root / 'Needs_Action' / category
    pending_folder = vault_root / 'Pending_Approval' / category
    
    needs_action_file = needs_action_folder / filename
    pending_file = pending_folder / filename
    
    if not needs_action_file.exists():
        print(f"Error: File {filename} not found in Needs_Action/{category}/")
        return False
    
    # Move to pending folder
    pending_folder.mkdir(exist_ok=True)
    shutil.move(str(needs_action_file), str(pending_file))
    print(f"Moved to pending: {filename} -> Pending_Approval/{category}/")
    return True

def main():
    print("AI Employee Approval Manager")
    print("Commands:")
    print("  show - Show all pending and needs-action items")
    print("  approve <category> <filename> - Approve an item")
    print("  reject <category> <filename> - Reject an item")
    print("  pending <category> <filename> - Move item to pending approval")
    print("  categories: Email, WhatsApp, Files")
    print("")
    
    while True:
        try:
            command = input("Enter command (or 'quit' to exit): ").strip().split()
            
            if not command or command[0].lower() == 'quit':
                break
            elif command[0].lower() == 'show':
                show_pending_items()
            elif command[0].lower() == 'approve' and len(command) >= 3:
                category = command[1].capitalize()
                filename = command[2]
                if category in ['Email', 'Whatsapp', 'Files']:
                    if category == 'Whatsapp':
                        category = 'WhatsApp'  # Correct capitalization
                    approve_item(category, filename)
                else:
                    print("Invalid category. Use: Email, WhatsApp, or Files")
            elif command[0].lower() == 'reject' and len(command) >= 3:
                category = command[1].capitalize()
                filename = command[2]
                if category in ['Email', 'Whatsapp', 'Files']:
                    if category == 'Whatsapp':
                        category = 'WhatsApp'  # Correct capitalization
                    reject_item(category, filename)
                else:
                    print("Invalid category. Use: Email, WhatsApp, or Files")
            elif command[0].lower() == 'pending' and len(command) >= 3:
                category = command[1].capitalize()
                filename = command[2]
                if category in ['Email', 'Whatsapp', 'Files']:
                    if category == 'Whatsapp':
                        category = 'WhatsApp'  # Correct capitalization
                    move_to_pending(category, filename)
                else:
                    print("Invalid category. Use: Email, WhatsApp, or Files")
            else:
                print("Invalid command. Type 'show', 'approve', 'reject', 'pending', or 'quit'")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()