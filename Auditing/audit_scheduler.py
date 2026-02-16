#!/usr/bin/env python3
"""
Scheduler for AI Employee Audit Generator
This script schedules the weekly audit and CEO briefing generation
"""

import schedule
import time
from datetime import datetime
import subprocess
import sys
from pathlib import Path

def run_audit():
    """Run the audit generator"""
    print(f"[{datetime.now()}] Running weekly audit...")
    
    try:
        # Get the path to the audit generator
        audit_script = Path("F:/AI_Employee_Vault/AI_Employee_Vault/Auditing/audit_generator.py")
        
        # Run the audit generator
        result = subprocess.run([sys.executable, str(audit_script)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] Audit completed successfully!")
            print(result.stdout)
        else:
            print(f"[{datetime.now()}] Audit failed!")
            print(result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now()}] Error running audit: {str(e)}")

def main():
    print("AI Employee Audit Scheduler Started")
    print("Scheduling weekly audits...")
    
    # Schedule the audit to run every Sunday at 7:00 AM
    schedule.every().sunday.at("07:00").do(run_audit)
    
    # For testing purposes, we can also schedule it to run every 5 minutes
    # schedule.every(5).minutes.do(run_audit)
    
    print("Scheduler is running. Waiting for scheduled times...")
    print("Next audit scheduled for:", schedule.next_run())
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
        return 0

if __name__ == "__main__":
    sys.exit(main())