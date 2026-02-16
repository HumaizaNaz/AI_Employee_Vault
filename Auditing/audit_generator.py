#!/usr/bin/env python3
"""
Audit Generator for AI Employee System
This script generates weekly business audits and CEO briefings
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import re
from collections import defaultdict

class AuditGenerator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / "Logs"
        self.briefings_path = self.vault_path / "Briefings"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        
        # Create necessary directories
        self.briefings_path.mkdir(exist_ok=True)
        
        # Subscription patterns for identifying recurring expenses
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'microsoft.com': 'Microsoft 365',
            'google.com': 'Google Workspace',
            'amazon.com': 'Amazon Prime',
            'apple.com': 'Apple Services',
            'dropbox.com': 'Dropbox',
            'zoom.us': 'Zoom',
            'salesforce.com': 'Salesforce',
            'hubspot.com': 'HubSpot',
        }

    def analyze_logs(self, days=7):
        """Analyze log files for the specified number of days"""
        logs = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Look for log files in the Logs directory
        for log_file in self.logs_path.glob(f"log_*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        file_logs = json.loads(content)
                        logs.extend(file_logs)
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        # Filter logs from the specified period
        filtered_logs = []
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                if timestamp >= start_date:
                    filtered_logs.append(log)
            except ValueError:
                continue
                
        return filtered_logs

    def analyze_done_folder(self, days=7):
        """Analyze files in the Done folder for the specified number of days"""
        done_files = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Check all Done subfolders
        for folder in self.done_path.iterdir():
            if folder.is_dir():
                for file in folder.glob("*.md"):
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if mod_time >= start_date:
                        done_files.append({
                            'filename': file.name,
                            'folder': folder.name,
                            'modified': mod_time.isoformat(),
                            'size': file.stat().st_size
                        })
        
        return done_files

    def analyze_needs_action(self):
        """Analyze current items in Needs_Action folder"""
        needs_action_items = {}
        
        # Check all Needs_Action subfolders
        for folder in self.needs_action_path.iterdir():
            if folder.is_dir():
                files = list(folder.glob("*"))
                needs_action_items[folder.name] = {
                    'count': len(files),
                    'files': [f.name for f in files[:10]]  # Limit to first 10 files
                }
        
        return needs_action_items

    def identify_bottlenecks(self, logs):
        """Identify potential bottlenecks based on logs"""
        bottlenecks = []
        
        # Group logs by action type
        action_counts = defaultdict(int)
        for log in logs:
            action_type = log.get('action_type', 'unknown')
            action_counts[action_type] += 1
        
        # Identify actions that occurred more than average (potential bottlenecks)
        avg_count = sum(action_counts.values()) / len(action_counts) if action_counts else 0
        
        for action_type, count in action_counts.items():
            if count > avg_count * 1.5:  # 50% more than average
                bottlenecks.append({
                    'action': action_type,
                    'count': count,
                    'avg_expected': round(avg_count, 2)
                })
        
        return bottlenecks

    def identify_subscription_costs(self, logs):
        """Identify potential subscription costs from logs"""
        subscriptions = []
        
        for log in logs:
            details = log.get('details', {})
            description = details.get('description', '').lower()
            
            for pattern, name in self.subscription_patterns.items():
                if pattern in description:
                    subscriptions.append({
                        'name': name,
                        'amount': details.get('amount', 'N/A'),
                        'date': log.get('timestamp', 'N/A'),
                        'description': description
                    })
        
        return subscriptions

    def generate_ceo_briefing(self, period_days=7):
        """Generate a CEO briefing for the specified period"""
        start_date = datetime.now() - timedelta(days=period_days)
        end_date = datetime.now()
        
        # Gather data
        logs = self.analyze_logs(period_days)
        done_files = self.analyze_done_folder(period_days)
        needs_action = self.analyze_needs_action()
        bottlenecks = self.identify_bottlenecks(logs)
        subscriptions = self.identify_subscription_costs(logs)
        
        # Calculate metrics
        total_logs = len(logs)
        completed_tasks = len(done_files)
        
        # Identify revenue-related activities (based on keywords in logs)
        revenue_keywords = ['payment', 'invoice', 'sale', 'revenue', 'income', 'billing']
        revenue_logs = []
        for log in logs:
            if any(keyword in json.dumps(log).lower() for keyword in revenue_keywords):
                revenue_logs.append(log)
        
        # Generate the briefing
        briefing_content = f"""# Monday Morning CEO Briefing
---
generated: {datetime.now().isoformat()}
period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
---

## Executive Summary
Weekly audit covering {period_days} days from {start_date.strftime('%B %d')} to {end_date.strftime('%B %d')}. 
System processed {total_logs} actions and completed {completed_tasks} tasks.

## Revenue
- **Revenue Activities**: {len(revenue_logs)} identified
- **Potential Revenue**: Data available in logs (requires manual review for exact amounts)
- **Trend**: {(len(revenue_logs)/period_days)*7:0.1f} activities per week

## Completed Tasks
- **Total Completed**: {completed_tasks}
- **Breakdown by type**:
  - Email: {[f for f in done_files if 'EMAIL_' in f['filename']]}
  - WhatsApp: {[f for f in done_files if 'WHATSAPP_' in f['filename']]}
  - Files: {[f for f in done_files if 'FILE_' in f['filename']]}

## Current Status
### Pending Actions
{self.format_needs_action_status(needs_action)}

### Bottlenecks
{self.format_bottlenecks(bottlenecks)}

## Proactive Suggestions
### Cost Optimization
{self.format_subscription_suggestions(subscriptions)}

### Upcoming Considerations
- Review pending items in Needs_Action folders
- Monitor any identified bottlenecks
- Follow up on revenue-generating activities

---
*Generated by AI Employee v1.0*
"""
        
        # Save the briefing
        briefing_filename = f"{end_date.strftime('%Y-%m-%d')}_Week_{end_date.strftime('%U')}_CEO_Briefing.md"
        briefing_path = self.briefings_path / briefing_filename
        
        with open(briefing_path, 'w', encoding='utf-8') as f:
            f.write(briefing_content)
        
        return briefing_path

    def format_needs_action_status(self, needs_action):
        """Format the needs action status for the briefing"""
        if not needs_action:
            return "No pending items in queue"
        
        status_lines = []
        for folder, info in needs_action.items():
            status_lines.append(f"- **{folder}**: {info['count']} items")
            if info['files']:
                status_lines.append(f"  - Sample: {', '.join(info['files'][:3])}")
        
        return '\n'.join(status_lines)

    def format_bottlenecks(self, bottlenecks):
        """Format bottlenecks for the briefing"""
        if not bottlenecks:
            return "No significant bottlenecks identified"
        
        bottleneck_lines = []
        for bottleneck in bottlenecks:
            bottleneck_lines.append(f"- **{bottleneck['action']}**: Occurred {bottleneck['count']} times (expected ~{bottleneck['avg_expected']})")
        
        return '\n'.join(bottleneck_lines)

    def format_subscription_suggestions(self, subscriptions):
        """Format subscription suggestions for the briefing"""
        if not subscriptions:
            return "No recurring subscription costs identified in logs"
        
        suggestion_lines = []
        for sub in subscriptions:
            suggestion_lines.append(f"- **{sub['name']}**: ${sub['amount']} detected on {sub['date'][:10]}")
            suggestion_lines.append(f"  - [ACTION] Review necessity? Move to /Pending_Approval")
        
        return '\n'.join(suggestion_lines)

    def run_weekly_audit(self):
        """Run the weekly audit and generate CEO briefing"""
        print("Running weekly audit...")
        briefing_path = self.generate_ceo_briefing(period_days=7)
        print(f"Weekly CEO briefing generated: {briefing_path}")
        return briefing_path

def main():
    # Initialize the audit generator
    vault_path = "F:/AI_Employee_Vault/AI_Employee_Vault"
    audit_gen = AuditGenerator(vault_path)
    
    # Run the weekly audit
    audit_gen.run_weekly_audit()
    
    print("Audit completed successfully!")

if __name__ == "__main__":
    main()