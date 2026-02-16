# Secure Vault Sync Configuration

## Overview
This document outlines the secure synchronization setup between local and cloud instances of the AI Employee. The primary goal is to synchronize only necessary operational files while keeping all sensitive information local and secure.

## Security Principles

### 1. Data Classification
- **Syncable Data**: Markdown files, task statuses, plans, non-sensitive logs
- **Non-Syncable Data**: Environment variables, API keys, credentials, session files

### 2. Sync-Only Files (Safe to Sync)
- `.md` files containing task information
- Status updates and progress reports
- Public configuration settings
- Audit logs (without sensitive details)
- Completed tasks in `/Done/`
- Drafts in `/Drafts/`

### 3. Non-Syncable Files (Blocked from Sync)
- `.env` files containing credentials
- WhatsApp session files
- Banking credentials
- API tokens and keys
- Private certificates
- Any file containing personally identifiable information (PII)

## Git Configuration for Security

### .gitignore Configuration
```
# Environment variables and secrets
.env
*.env
.env.local
.env.production

# Session files
**/whatsapp_session/**
**/session/**

# Credentials
**/*.key
**/*.pem
**/credentials.json
**/tokens.json

# Banking information
**/banking/**
**/finance/private/**

# Private configurations
**/private_config.json
**/secrets/**

# Operating system files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Logs with potential sensitive info
logs/
*.log
```

## Synchronization Methods

### Method 1: Git-based Sync (Recommended)
- Use Git with proper .gitignore configuration
- Separate repositories for public and private components
- SSH key-based authentication
- Regular audit of committed files

### Method 2: Syncthing-based Sync
- Peer-to-peer synchronization
- End-to-end encryption
- Selective folder sharing
- Device-specific access controls

## Implementation Steps

### 1. Set up Git Repository
1. Initialize a Git repository in the vault directory
2. Configure .gitignore with the patterns above
3. Create a remote repository (public or private depending on sensitivity)
4. Perform initial commit with only safe files

### 2. Verification Script
Create a script to verify that no sensitive files are being synced:

```bash
#!/bin/bash
# verify_sync_safety.sh
echo "Checking for sensitive files that shouldn't be synced..."

# Check for common sensitive file patterns
find . -name ".env*" -type f
find . -name "*credential*" -type f
find . -name "*token*" -type f
find . -name "*.key" -type f
find . -name "*.pem" -type f

echo "Verification complete. If any files were listed above, review your .gitignore."
```

### 3. Pre-commit Hooks
Set up Git hooks to prevent accidental committing of sensitive files:

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Prevent committing sensitive files

echo "Running pre-commit security check..."

# Check for sensitive file patterns in the commit
for file in $(git diff --cached --name-only --diff-filter=ACM); do
  if [[ "$file" =~ \.(env|key|pem|secret|token)$ ]] || [[ "$file" =~ .*credential.* ]] || [[ "$file" == ".env" ]]; then
    echo "ERROR: Attempting to commit sensitive file: $file"
    exit 1
  fi
done

echo "Pre-commit check passed."
```

## Testing Security Measures

### 1. Dry Run Test
Before any sync operation, perform a dry run to see what would be transferred:
- For Git: `git add --dry-run .`
- For Syncthing: Use preview feature

### 2. Regular Audits
- Periodically review committed files
- Check that .gitignore is working correctly
- Verify no sensitive information appears in logs

## Recovery Procedures

### If Sensitive Data is Accidentally Synced:
1. Immediately remove the sensitive data from source
2. Update .gitignore to block the file type
3. Perform hard reset to remove from Git history if needed
4. Change any exposed credentials immediately
5. Notify relevant parties if data breach occurred

## Best Practices

1. **Principle of Least Privilege**: Only sync what's necessary
2. **Regular Reviews**: Periodically audit synchronized files
3. **Access Controls**: Use appropriate authentication for sync methods
4. **Monitoring**: Log and monitor sync activities
5. **Separation**: Keep sensitive and nonsensitive data in separate paths when possible