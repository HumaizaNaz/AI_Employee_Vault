import time
from pathlib import Path
import shutil
import hashlib
import mimetypes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict
import re


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

        # Create all necessary folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done_folder = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.plans_folder = self.vault_path / 'Plans'

        self.needs_action.mkdir(exist_ok=True)
        self.done_folder.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)
        self.plans_folder.mkdir(exist_ok=True)

        # Analytics tracking
        self.analytics = {
            'files_processed': 0,
            'by_extension': defaultdict(int),
            'by_size': {'small': 0, 'medium': 0, 'large': 0},
            'by_category': defaultdict(int)
        }

        # Security patterns to watch for
        self.security_patterns = [
            r'\.(exe|bat|cmd|com|scr|vbs|js|jar)$',  # Executable files
            r'(password|credential|secret|key).*\.txt',  # Files with sensitive keywords
            r'.*\.(zip|rar|7z).*',  # Archive files (potential risk)
        ]

    def categorize_file(self, file_path: Path) -> str:
        """Categorize file based on extension and content"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()

        # Define categories
        categories = {
            'Document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'Data': ['.csv', '.json', '.xml', '.yaml', '.sql', '.db'],
            'Code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.php', '.rb', '.go', '.rs'],
            'Media': ['.mp3', '.mp4', '.avi', '.mov', '.wav', '.flv'],
            'Archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Financial': ['.inv', '.bill', '.invoice', '.tax', '.pay', '.receipt'],
            'Educational': ['.edu', 'course', 'lesson', 'quiz', 'exam', 'assignment']
        }

        # Check by extension
        for category, extensions in categories.items():
            if ext in extensions or any(keyword in name for keyword in extensions):
                return category

        # Default category
        return 'General'

    def scan_security_risks(self, file_path: Path) -> list:
        """Scan file for potential security risks"""
        risks = []

        # Check file extension against known risky patterns
        for pattern in self.security_patterns:
            if re.search(pattern, file_path.name, re.IGNORECASE):
                risks.append(f"Risky file type: {file_path.suffix}")

        # Check file size (very large files could be suspicious)
        size = file_path.stat().st_size
        if size > 100 * 1024 * 1024:  # 100MB
            risks.append("Large file (>100MB) - potential risk")

        # Check for suspicious filename patterns
        suspicious_patterns = [
            r'password',
            r'credential',
            r'login',
            r'key',
            r'secret',
            r'confidential',
            r'private'
        ]
        for pattern in suspicious_patterns:
            if pattern in file_path.name.lower():
                risks.append(f"Suspicious keyword in filename: {pattern}")

        return risks

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Skip temporary files
        if source.name.startswith('.') or source.suffix.lower() in ['.tmp', '.swp', '.lock']:
            return

        # Only process files that exist
        if not source.exists():
            return

        # Categorize file
        category = self.categorize_file(source)

        # Update analytics
        self.analytics['files_processed'] += 1
        self.analytics['by_extension'][source.suffix.lower()] = self.analytics['by_extension'][source.suffix.lower()] + 1
        self.analytics['by_category'][category] = self.analytics['by_category'][category] + 1

        # Track file size category
        size = source.stat().st_size
        if size < 1024 * 1024:  # < 1MB
            self.analytics['by_size']['small'] += 1
        elif size < 10 * 1024 * 1024:  # < 10MB
            self.analytics['by_size']['medium'] += 1
        else:
            self.analytics['by_size']['large'] += 1

        # Copy file to Needs_Action
        dest = self.needs_action / f'FILE_{source.name}'
        shutil.copy2(source, dest)

        # Scan for security risks
        security_risks = self.scan_security_risks(dest)

        # Calculate file hash
        file_hash = self.calculate_file_hash(dest)

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(source))
        if mime_type is None:
            mime_type = 'unknown'

        # Create metadata file with enhanced information
        meta_path = dest.with_name(f'FILE_{source.stem}_{int(time.time())}{dest.suffix}.md')
        meta_content = f'''---
type: file_drop
original_name: {source.name}
size_bytes: {source.stat().st_size}
size_formatted: {self.format_file_size(source.stat().st_size)}
mime_type: {mime_type}
extension: {source.suffix.lower()}
category: {category}
hash_sha256: {file_hash}
received: {time.strftime("%Y-%m-%d %H:%M:%S")}
priority: medium
status: pending
security_risks: {security_risks}
needs_approval: {len(security_risks) > 0 or category in ["Financial", "Document"]}
---

## File Details
- **Original Name**: `{source.name}`
- **Size**: {self.format_file_size(source.stat().st_size)} ({source.stat().st_size} bytes)
- **Type**: {mime_type}
- **Category**: {category}
- **Location**: {str(source.parent)}

## Security Analysis
- **Risks Detected**: {len(security_risks) > 0}
- **Risk Details**: {security_risks if security_risks else "None detected"}

## Processing Instructions
1. Review file content
2. Assess security risks
3. Determine appropriate action
4. Process according to category

## Suggested Actions
- [ ] Review file content
- [ ] Check for sensitive information
- [ ] Determine processing priority
- [ ] Archive after processing
'''
        meta_path.write_text(meta_content, encoding="utf-8")

        # Log the processing
        print(f"📁 New file processed: {source.name}")
        print(f"   🏷️ Category: {category}")
        print(f"   📏 Size: {self.format_file_size(source.stat().st_size)}")
        if security_risks:
            print(f"   ⚠️ Security risks: {security_risks}")
        if len(security_risks) > 0 or category in ["Financial", "Document"]:
            print(f"   🔒 Requires approval")

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"


class EnhancedFileSystemWatcher:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.handler = DropFolderHandler(vault_path)
        self.observer = Observer()
        self.observer.schedule(self.handler, path=vault_path, recursive=False)

    def start(self):
        self.observer.start()
        print(f"[FILES] Enhanced File Watcher running on: {self.vault_path}")
        print("[FILES] Monitoring for new files in vault root...")
        print("[FILES] Files will be categorized and processed automatically")

        # Print initial analytics
        print(f"[FILES] Analytics initialized:")
        print(f"   Files processed: 0")

        try:
            while True:
                time.sleep(1)

                # Print periodic analytics every 30 seconds
                if int(time.time()) % 30 == 0:
                    analytics = self.handler.analytics
                    print(f"📈 Analytics Update:")
                    print(f"   Total files processed: {analytics['files_processed']}")
                    print(f"   By category: {dict(analytics['by_category'])}")
                    print(f"   By extension: {dict(analytics['by_extension'])}")

        except KeyboardInterrupt:
            print("\n🛑 Stopping File Watcher...")
            self.observer.stop()
        finally:
            self.observer.join()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Run like: python filesystem_watcher.py F:/AI_Employee_Vault/AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]
    watcher = EnhancedFileSystemWatcher(vault_path)
    watcher.start()