# AI Employee - Logging System

## Overview
This directory contains the comprehensive logging system for the AI Employee. It provides detailed action logging, audit trails, compliance reporting, and system monitoring capabilities across all components of the AI Employee system.

## Components

### 1. Logging System
- `logging_system.py` - Main logging implementation with comprehensive features
- Thread-safe logging for concurrent access
- JSON-formatted log entries for structured analysis
- Daily log rotation with configurable size limits
- Compression of archived logs
- Search and filtering capabilities
- Log aggregation and compliance reporting

### 2. Log Aggregation
- Multi-source log collection
- Date-range based reporting
- Compliance report generation
- Statistics and analytics

## Features

### Comprehensive Logging
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL, AUDIT)
- Structured JSON format for easy parsing
- Thread-safe operations for concurrent access
- In-memory buffering for performance

### Log Management
- Daily log rotation based on size limits
- Automatic compression of archived logs
- Configurable retention policies
- Automatic cleanup of old logs

### Audit and Compliance
- Immutable audit trails
- Compliance report generation
- Security event tracking
- Regulatory compliance features

### Search and Analysis
- Date-range filtering
- Log level filtering
- Action type filtering
- Actor-based filtering
- Full-text search capabilities
- Statistics and analytics

## Configuration

### Log Rotation
- `max_log_size_mb`: Maximum size of log files before rotation (default: 100 MB)
- `backup_count`: Number of backup files to keep (default: 5)

### Log Levels
- DEBUG: Detailed diagnostic information
- INFO: General system information
- WARNING: Indication of potential issues
- ERROR: Error conditions that don't stop operation
- CRITICAL: Severe errors that may stop operation
- AUDIT: Compliance and security events

## Usage

### Basic Logging
```python
from logging_system import AILogger

logger = AILogger("F:/AI_Employee_Vault/AI_Employee_Vault")

# Log an action
logger.log_action(
    action_type="email_sent",
    details={"to": "user@example.com", "subject": "Test email"},
    actor="mcp_email_server",
    level=LogLevel.INFO
)
```

### Audit Events
```python
from logging_system import AuditEventType

logger.log_audit_event(
    event_type=AuditEventType.APPROVAL_GRANTED,
    actor="user",
    resource="EMAIL_example.md",
    details={"reason": "Invoice approval"}
)
```

### Security Events
```python
logger.log_security_event(
    event_type="unauthorized_access_attempt",
    actor="unknown_user",
    severity="high",
    description="Attempted access to restricted resource"
)
```

### Log Search
```python
# Search logs with filters
logs = logger.search_logs(
    start_date=datetime(2026, 2, 1),
    level=LogLevel.ERROR,
    action_type="email_sent"
)
```

## Integration Points
- All system components (watchers, orchestrator, MCP servers)
- Error handling system for error logging
- Approval workflows for action logging
- Dashboard updates for status logging
- Security monitoring for event logging

## Security Considerations
- Structured logging prevents injection attacks
- Sanitized log entries to prevent sensitive data exposure
- Access controls on log files
- Protection against log tampering
- Integrity checking of log files

## Performance
- In-memory buffering for high-performance logging
- Asynchronous writing to prevent blocking
- Efficient JSON serialization
- Thread-safe operations
- Minimal impact on system performance

## Compliance Features
- Immutable audit trails
- Tamper-evident logging
- Regulatory compliance reporting
- Data retention policies
- Access logging for sensitive operations
- Security event correlation

## Log File Structure
- Daily log files: `log_YYYY-MM-DD.json`
- Compressed archives: `log_YYYY-MM-DD.json.gz`
- Located in: `/Logs/` directory

## Dependencies
- Python 3.x
- Standard library modules (json, datetime, pathlib, threading, etc.)
- Access to AI Employee vault structure