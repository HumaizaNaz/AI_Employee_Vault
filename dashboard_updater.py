import re
from pathlib import Path
from datetime import datetime

def update_dashboard(vault_path: str):
    vault_root = Path(vault_path)
    dashboard_file = vault_root / 'Dashboard.md'
    needs_action_folder = vault_root / 'Needs_Action'

    if not dashboard_file.exists():
        print(f"Error: Dashboard.md not found at {dashboard_file}")
        return
    if not needs_action_folder.exists():
        print(f"Error: Needs_Action folder not found at {needs_action_folder}")
        return

    # Count pending actions (markdown files in Needs_Action)
    pending_emails = len(list(needs_action_folder.glob('EMAIL_*.md')))
    # Assuming other types of pending actions would also be markdown files,
    # you can refine this count if you have other file types.
    total_pending_actions = len(list(needs_action_folder.glob('*.md')))

    # Read existing dashboard content
    content = dashboard_file.read_text(encoding='utf-8')

    # Update "Pending actions"
    content = re.sub(
        r'- ✅ \*\*Pending actions\*\*:\s*\d+',
        f'- ✅ **Pending actions**: {total_pending_actions}',
        content
    )

    # Update "Pending emails in Needs_Action"
    content = re.sub(
        r'- 📧 \*\*Pending emails in Needs_Action\*\*:\s*\d+',
        f'- 📧 **Pending emails in Needs_Action**: {pending_emails}',
        content
    )

    # Update "Last checked" timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    content = re.sub(
        r'- 🕐 \*\*Last checked\*\*:\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}',
        f'- 🕐 **Last checked**: {current_time}',
        content
    )
    
    # You might also want to update the "Recent Activity" section.
    # For this simulation, we'll just focus on the counts and timestamp.

    # Write updated content back to Dashboard.md
    dashboard_file.write_text(content, encoding='utf-8')
    print(f"Dashboard.md updated successfully with {total_pending_actions} pending actions ({pending_emails} emails).")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python dashboard_updater.py <path_to_AI_Employee_Vault>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    update_dashboard(vault_path)
