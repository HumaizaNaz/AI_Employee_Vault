#!/usr/bin/env python3
"""
Comprehensive Logging System for AI Employee
Provides detailed action logging, audit trails, and compliance logging
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, Any, Optional
from enum import Enum
import threading
import atexit
from collections import deque
import gzip
import shutil

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"

class AuditEventType(Enum):
    FILE_CREATED = "file_created"
    FILE_MOVED = "file_moved"
    EMAIL_SENT = "email_sent"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    MCP_CALL = "mcp_call"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SECURITY_EVENT = "security_event"
    CONFIG_CHANGE = "config_change"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"

class AILogger:
    """
    Comprehensive logging system for AI Employee
    """
    def __init__(self, vault_path: str, max_log_size_mb: int = 100, backup_count: int = 5):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / "Logs"
        self.logs_path.mkdir(exist_ok=True)
        
        # Configuration
        self.max_log_size_mb = max_log_size_mb
        self.backup_count = backup_count
        self.max_log_size_bytes = max_log_size_mb * 1024 * 1024
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # In-memory log buffer for performance
        self.log_buffer = deque(maxlen=1000)
        
        # Set up logging
        self.setup_logging()
        
        # Register cleanup function
        atexit.register(self.flush_logs)
    
    def setup_logging(self):
        """
        Set up the logging configuration
        """
        # Create logs directory
        self.logs_path.mkdir(exist_ok=True)
        
        # Get today's log file
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_path / f"log_{today}.json"
        
        # Set up file handler
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        
        # Set up formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        
        # Set up logger
        self.logger = logging.getLogger('AI_Employee_Logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)
    
    def get_current_log_file(self) -> Path:
        """
        Get the current log file path
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return self.logs_path / f"log_{today}.json"
    
    def rotate_log_if_needed(self):
        """
        Rotate log file if it exceeds the maximum size
        """
        current_log = self.get_current_log_file()
        
        if current_log.exists() and current_log.stat().st_size > self.max_log_size_bytes:
            # Compress the old log file
            compressed_log = current_log.with_suffix('.json.gz')
            with open(current_log, 'rb') as f_in:
                with gzip.open(compressed_log, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove the uncompressed log file
            current_log.unlink()
            
            # Set up new log file
            self.file_handler.close()
            self.file_handler = logging.FileHandler(current_log, encoding='utf-8')
            self.file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.file_handler.setFormatter(formatter)
            self.logger.removeHandler(self.file_handler)
            self.logger.addHandler(self.file_handler)
    
    def log_action(self, 
                   action_type: str, 
                   details: Dict[str, Any], 
                   actor: str = "system", 
                   level: LogLevel = LogLevel.INFO,
                   approval_status: Optional[str] = None,
                   approved_by: Optional[str] = None,
                   result: Optional[str] = None):
        """
        Log an action with comprehensive details
        """
        with self.lock:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "action_type": action_type,
                "actor": actor,
                "details": details,
                "approval_status": approval_status,
                "approved_by": approved_by,
                "result": result
            }
            
            # Add to in-memory buffer
            self.log_buffer.append(log_entry)
            
            # Write to file
            self._write_log_entry(log_entry)
            
            # Rotate log if needed
            self.rotate_log_if_needed()
    
    def log_audit_event(self, 
                       event_type: AuditEventType, 
                       actor: str, 
                       resource: str, 
                       details: Dict[str, Any] = None,
                       success: bool = True):
        """
        Log an audit event for compliance
        """
        with self.lock:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": LogLevel.AUDIT.value,
                "event_type": event_type.value,
                "actor": actor,
                "resource": resource,
                "details": details or {},
                "success": success
            }
            
            # Add to in-memory buffer
            self.log_buffer.append(log_entry)
            
            # Write to file
            self._write_log_entry(log_entry)
            
            # Rotate log if needed
            self.rotate_log_if_needed()
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """
        Write a log entry to the current log file
        """
        current_log = self.get_current_log_file()
        
        # Read existing content
        existing_content = []
        if current_log.exists():
            try:
                with open(current_log, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        existing_content = json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_content = []
        
        # Append new entry
        existing_content.append(log_entry)
        
        # Write back to file
        with open(current_log, 'w', encoding='utf-8') as f:
            json.dump(existing_content, f, indent=2)
    
    def log_security_event(self, 
                          event_type: str, 
                          actor: str, 
                          severity: str, 
                          description: str,
                          details: Dict[str, Any] = None):
        """
        Log a security-related event
        """
        self.log_audit_event(
            event_type=AuditEventType.SECURITY_EVENT,
            actor=actor,
            resource=event_type,
            details={
                "severity": severity,
                "description": description,
                "details": details or {}
            },
            success=True
        )
    
    def get_recent_logs(self, count: int = 100) -> list:
        """
        Get recent log entries from the buffer
        """
        return list(self.log_buffer)[-count:]
    
    def search_logs(self, 
                   start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None,
                   level: Optional[LogLevel] = None,
                   action_type: Optional[str] = None) -> list:
        """
        Search logs based on criteria
        """
        results = []
        
        # Get today's log file
        current_log = self.get_current_log_file()
        
        # Read log file
        if current_log.exists():
            try:
                with open(current_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                for log in logs:
                    # Apply filters
                    if start_date and datetime.fromisoformat(log['timestamp']) < start_date:
                        continue
                    if end_date and datetime.fromisoformat(log['timestamp']) > end_date:
                        continue
                    if level and log['level'] != level.value:
                        continue
                    if action_type and log.get('action_type') != action_type:
                        continue
                    
                    results.append(log)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return results
    
    def flush_logs(self):
        """
        Flush any remaining logs to disk
        """
        # In this implementation, logs are written immediately
        # But we could add any cleanup here if needed
        pass
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the logs
        """
        stats = {
            'total_entries': len(self.log_buffer),
            'levels': {},
            'actions': {},
            'actors': {}
        }
        
        for log in self.log_buffer:
            # Count by level
            level = log['level']
            stats['levels'][level] = stats['levels'].get(level, 0) + 1
            
            # Count by action type
            action_type = log.get('action_type', 'unknown')
            stats['actions'][action_type] = stats['actions'].get(action_type, 0) + 1
            
            # Count by actor
            actor = log.get('actor', 'unknown')
            stats['actors'][actor] = stats['actors'].get(actor, 0) + 1
        
        return stats

class LogAggregator:
    """
    Aggregates logs from multiple sources for analysis
    """
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / "Logs"
    
    def aggregate_daily_logs(self, date: str) -> list:
        """
        Aggregate logs for a specific date
        """
        log_file = self.logs_path / f"log_{date}.json"
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate a compliance report for a date range
        """
        report = {
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_events': 0,
                'audit_events': 0,
                'security_events': 0,
                'errors': 0
            },
            'events': []
        }
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Get all log files in the date range
        for log_file in self.logs_path.glob("log_*.json"):
            # Extract date from filename
            date_str = log_file.stem.replace('log_', '')
            try:
                log_date = datetime.strptime(date_str, '%Y-%m-%d')
                if start_dt <= log_date <= end_dt:
                    # Read and process this log file
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            logs = json.load(f)
                        
                        for log in logs:
                            timestamp = datetime.fromisoformat(log['timestamp'])
                            if start_dt <= timestamp <= end_dt:
                                report['events'].append(log)
                                
                                # Update summary
                                report['summary']['total_events'] += 1
                                if log['level'] == LogLevel.AUDIT.value:
                                    report['summary']['audit_events'] += 1
                                elif log['level'] == LogLevel.ERROR.value:
                                    report['summary']['errors'] += 1
                                elif log.get('event_type') == AuditEventType.SECURITY_EVENT.value:
                                    report['summary']['security_events'] += 1
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
            except ValueError:
                continue  # Skip files that don't match the expected format
        
        return report

def main():
    """
    Example usage of the logging system
    """
    print("AI Employee Logging System")
    print("=" * 30)
    
    # Initialize the logger
    vault_path = "F:/AI_Employee_Vault/AI_Employee_Vault"
    logger = AILogger(vault_path)
    
    # Log some example actions
    print("\n1. Logging example actions:")
    
    # Log a file creation
    logger.log_action(
        action_type="file_created",
        details={"filename": "EMAIL_example.md", "folder": "Needs_Action/Email"},
        actor="gmail_watcher",
        level=LogLevel.INFO
    )
    
    # Log an email send
    logger.log_action(
        action_type="email_sent",
        details={"to": "user@example.com", "subject": "Test email"},
        actor="mcp_email_server",
        level=LogLevel.INFO,
        approval_status="approved",
        approved_by="user",
        result="success"
    )
    
    # Log an audit event
    logger.log_audit_event(
        event_type=AuditEventType.APPROVAL_GRANTED,
        actor="user",
        resource="EMAIL_example.md",
        details={"reason": "Invoice approval"}
    )
    
    # Log a security event
    logger.log_security_event(
        event_type="unauthorized_access_attempt",
        actor="unknown_user",
        severity="high",
        description="Attempted access to restricted resource",
        details={"ip_address": "192.168.1.100", "resource": "sensitive_data"}
    )
    
    print("✅ Actions logged successfully")
    
    # Get log statistics
    stats = logger.get_log_statistics()
    print(f"\n2. Log Statistics:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Levels: {stats['levels']}")
    print(f"   Actors: {stats['actors']}")
    
    # Generate a compliance report
    aggregator = LogAggregator(vault_path)
    today = datetime.now().strftime('%Y-%m-%d')
    report = aggregator.generate_compliance_report(today, today)
    
    print(f"\n3. Compliance Report for {today}:")
    print(f"   Total events: {report['summary']['total_events']}")
    print(f"   Audit events: {report['summary']['audit_events']}")
    print(f"   Security events: {report['summary']['security_events']}")
    print(f"   Errors: {report['summary']['errors']}")
    
    print("\n✅ Logging system ready for use in AI Employee system!")

if __name__ == "__main__":
    main()