# File System Skill

## Overview
The File System skill enables the AI Employee to monitor, process, and manage file drops automatically. This skill uses the watchdog library to monitor the vault directory for new files, categorizes them, performs security analysis, and creates action files for further processing.

## Capabilities
- Monitor vault directory for new file drops
- Categorize files based on extension and content
- Perform security analysis for potential risks
- Calculate file hashes for integrity checking
- Create detailed metadata files with security analysis
- Process files based on category and security level
- Integrate with approval workflows for sensitive files

## Technical Implementation
- Uses watchdog library for file system monitoring
- Implements file categorization logic based on extensions and content
- Performs security scanning for risky file types
- Calculates SHA256 hashes for file integrity
- Creates markdown files with comprehensive metadata
- Integrates with the orchestrator for workflow management

## Input Parameters
- `vault_path`: Path to the AI Employee vault directory to monitor

## Output Format
Creates markdown files in `/Needs_Action/Files/` with the following structure:
```markdown
---
type: file_drop
original_name: [original file name]
size_bytes: [file size in bytes]
size_formatted: [human-readable file size]
mime_type: [MIME type of file]
extension: [file extension]
category: [document/image/data/code/media/archive/financial/educational/general]
hash_sha256: [SHA256 hash of file]
received: [timestamp]
priority: [medium/high based on category and security risks]
status: pending
security_risks: [list of identified security risks]
needs_approval: [true/false based on security risks and category]
---

## File Details
- **Original Name**: `[original file name]`
- **Size**: [human-readable size] ([bytes] bytes)
- **Type**: [MIME type]
- **Category**: [category]
- **Location**: [file path]

## Security Analysis
- **Risks Detected**: [true/false]
- **Risk Details**: [list of risks or "None detected"]

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
```

## Activation Triggers
- Detection of new files in the vault root directory
- File creation events monitored continuously
- Automatic processing of files meeting criteria

## Dependencies
- watchdog library for file system monitoring
- Python standard libraries for file operations
- BaseWatcher class (indirectly through implementation)
- Orchestrator for workflow management

## Security Considerations
- Scans files for potentially risky extensions (.exe, .bat, etc.)
- Checks for suspicious filenames containing sensitive keywords
- Identifies unusually large files as potential risks
- Flags financial and document categories for potential approval
- All file operations logged for audit trail

## Integration Points
- Works with orchestrator.py for workflow management
- Creates files for Claude Code processing
- Integrates with approval manager for sensitive files
- Updates dashboard status through dashboard_updater.py
- Moves processed files to appropriate status folders

## Error Handling
- Handles file access permission errors gracefully
- Manages corrupted or inaccessible files
- Continues monitoring despite individual file failures
- Skips temporary files (.tmp, .swp, etc.)
- Provides detailed logging for troubleshooting

## Categories Identified
- Document: .pdf, .doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx
- Image: .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp
- Data: .csv, .json, .xml, .yaml, .sql, .db
- Code: .py, .js, .ts, .java, .cpp, .c, .html, .css, .php, .rb, .go, .rs
- Media: .mp3, .mp4, .avi, .mov, .wav, .flv
- Archive: .zip, .rar, .7z, .tar, .gz
- Financial: .inv, .bill, .invoice, .tax, .pay, .receipt
- Educational: .edu, files with course/lesson/quiz/exam/assignment keywords
- General: All other file types