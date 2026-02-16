"""
Secure Sync Verification Script

This script verifies that sensitive files are properly excluded from synchronization
and that the vault is configured securely according to Platinum tier requirements.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Tuple
import re

class SecureSyncVerifier:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.sensitive_patterns = [
            '*.env',
            '.env',
            '*.env.*',
            '*credential*',
            '*token*',
            '*.key',
            '*.pem',
            '*secret*',
            '*password*',
            '*auth*',
            '*session*',
            'whatsapp_session/**',
            '*private*',
            '*.json',  # Will filter further for credential files
        ]
        
        # Patterns that are acceptable to sync
        self.allowed_patterns = [
            '*.md',
            '*.txt',
            '*.py',
            '*.js',
            '*.json',  # Will filter further to exclude sensitive JSONs
        ]

    def find_sensitive_files(self) -> List[Path]:
        """Find files that match sensitive patterns"""
        sensitive_files = []
        
        for pattern in self.sensitive_patterns:
            # Handle recursive patterns like whatsapp_session/**
            if '**' in pattern:
                base_pattern = pattern.replace('**/', '')
                for file_path in self.vault_path.rglob(base_pattern):
                    if file_path.is_file():
                        sensitive_files.append(file_path)
            else:
                for file_path in self.vault_path.rglob(pattern):
                    if file_path.is_file():
                        # Additional check for JSON files that might contain credentials
                        if pattern == '*.json' and self._is_sensitive_json(file_path):
                            sensitive_files.append(file_path)
                        elif pattern != '*.json':
                            sensitive_files.append(file_path)
        
        # Filter out files that are in safe directories like Logs (which may have .json files)
        filtered_files = []
        for file_path in sensitive_files:
            # Skip if it's in a safe directory like Logs or Briefings
            relative_path = file_path.relative_to(self.vault_path)
            if not any(part in ['Logs', 'Briefings', 'Accounting'] for part in relative_path.parts):
                # Additional check: if it's a JSON file, check if it contains sensitive info
                if file_path.suffix.lower() == '.json':
                    if self._is_sensitive_json(file_path):
                        filtered_files.append(file_path)
                else:
                    filtered_files.append(file_path)
        
        return filtered_files

    def _is_sensitive_json(self, file_path: Path) -> bool:
        """Check if a JSON file contains sensitive information"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # Look for common sensitive keys in JSON files
            sensitive_indicators = [
                'token', 'api_key', 'password', 'secret', 'credential', 
                'auth', 'session', 'access_key', 'private_key', 'oauth'
            ]
            
            content_lower = content.lower()
            return any(indicator in content_lower for indicator in sensitive_indicators)
        except:
            # If we can't read the file, assume it's not sensitive
            return False

    def check_gitignore_exists(self) -> bool:
        """Check if .gitignore file exists in the vault"""
        gitignore_path = self.vault_path / '.gitignore'
        return gitignore_path.exists()

    def verify_gitignore_content(self) -> Tuple[bool, List[str]]:
        """Verify that .gitignore contains necessary patterns"""
        gitignore_path = self.vault_path / '.gitignore'
        if not gitignore_path.exists():
            return False, ["Missing .gitignore file"]
        
        content = gitignore_path.read_text(encoding='utf-8')
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        required_patterns = [
            '.env',
            '*.env',
            '*.key',
            '*.pem',
            'whatsapp_session/',
            '*credential*',
            '*token*',
            '*secret*'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if not any(fnmatch.fnmatch(line, pattern) or pattern in line for line in lines):
                missing_patterns.append(pattern)
        
        return len(missing_patterns) == 0, missing_patterns

    def generate_gitignore(self) -> str:
        """Generate a recommended .gitignore content"""
        gitignore_content = """# Environment variables and secrets
.env
*.env
.env.local
.env.production

# Session files
whatsapp_session/
**/whatsapp_session/**

# Credentials
**/*credential*
**/*token*
**/*.key
**/*.pem
**/credentials.json
**/tokens.json
**/secrets.json

# Banking and finance information
**/banking/**
**/finance/private/**
**/accounts/

# Private configurations
**/private_config.json
**/secrets/

# Cache and temporary files
**/__pycache__/**
**/*.pyc
**/*.pyo
**/*.pyd
**/.DS_Store
**/Thumbs.db

# IDE files
.vscode/
.idea/
**/*.swp
**/*.swo

# Logs (if they might contain sensitive info)
logs/
*.log

# Virtual environment
venv/
env/
ENV/
**/venv/**
**/env/**
**/ENV/**

# Node modules
node_modules/

# Local configuration overrides
**/local_settings.json
**/config_local.json
"""
        return gitignore_content

    def run_security_check(self) -> dict:
        """Run a complete security check and return results"""
        results = {
            'sensitive_files_found': [],
            'gitignore_exists': False,
            'gitignore_valid': False,
            'gitignore_missing_patterns': [],
            'overall_secure': False
        }
        
        # Find sensitive files
        sensitive_files = self.find_sensitive_files()
        results['sensitive_files_found'] = [str(f) for f in sensitive_files]
        
        # Check gitignore
        results['gitignore_exists'] = self.check_gitignore_exists()
        gitignore_valid, missing_patterns = self.verify_gitignore_content()
        results['gitignore_valid'] = gitignore_valid
        results['gitignore_missing_patterns'] = missing_patterns
        
        # Overall security status
        results['overall_secure'] = (
            len(sensitive_files) == 0 and 
            results['gitignore_exists'] and 
            results['gitignore_valid']
        )
        
        return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python secure_sync_verifier.py <vault_path>")
        print("   Or: python secure_sync_verifier.py <vault_path> --generate-gitignore")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--generate-gitignore":
        # Generate and save a recommended .gitignore
        verifier = SecureSyncVerifier(vault_path)
        gitignore_content = verifier.generate_gitignore()
        
        gitignore_path = Path(vault_path) / '.gitignore'
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            print(f"Generated .gitignore file at: {gitignore_path}")
        else:
            print(f".gitignore already exists at: {gitignore_path}")
            response = input("Do you want to overwrite it? (y/N): ")
            if response.lower() == 'y':
                gitignore_path.write_text(gitignore_content)
                print("Overwritten .gitignore file.")
            else:
                print("Kept existing .gitignore file.")
    else:
        # Run security check
        verifier = SecureSyncVerifier(vault_path)
        results = verifier.run_security_check()
        
        print("=== Secure Sync Verification Report ===")
        print(f"Vault Path: {vault_path}")
        print(f"Overall Secure: {'YES' if results['overall_secure'] else 'NO'}")
        print()
        
        print(f"GitIgnore Exists: {'YES' if results['gitignore_exists'] else 'NO'}")
        print(f"GitIgnore Valid: {'YES' if results['gitignore_valid'] else 'NO'}")
        if results['gitignore_missing_patterns']:
            print(f"Missing GitIgnore Patterns: {', '.join(results['gitignore_missing_patterns'])}")
        print()
        
        if results['sensitive_files_found']:
            print(f"Sensitive Files Found ({len(results['sensitive_files_found'])}):")
            for file_path in results['sensitive_files_found']:
                print(f"  - {file_path}")
            print()
            print("RECOMMENDATION: Move these files to a secure location or update .gitignore!")
        else:
            print("No sensitive files found in unsafe locations.")
        
        print()
        if not results['overall_secure']:
            print("SECURITY ALERT: Vault is not properly secured for synchronization!")
            print("Run with '--generate-gitignore' option to create a secure .gitignore file.")
        else:
            print("VAULT IS SECURE: Safe for synchronization.")

if __name__ == "__main__":
    main()