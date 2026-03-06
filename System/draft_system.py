"""
Draft System for AI Employee

Implements draft-only functionality for sensitive operations like emails and social media posts.
Instead of directly executing these actions, the system creates drafts that require human approval.
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DraftSystem:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.drafts_path = self.vault_path / "Drafts"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.discarded_path = self.vault_path / "Discarded"
        self.done_path = self.vault_path / "Done"
        
        # Create necessary directories if they don't exist
        self.drafts_path.mkdir(parents=True, exist_ok=True)
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
        self.approved_path.mkdir(parents=True, exist_ok=True)
        self.discarded_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)
    
    def create_draft(self, draft_type: str, content: str, title: str = "", metadata: Dict = {}) -> Path:
        """Create a new draft in the Drafts folder"""
        try:
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"DRAFT_{draft_type.upper()}_{title.replace(' ', '_')}_{timestamp}.md"
            
            # Create the content with YAML frontmatter
            draft_metadata = {
                'type': f'draft_{draft_type}',
                'status': 'pending_approval',
                'created': datetime.now().isoformat(),
                'scheduled': None,
                'author': 'ai_employee',
                'requires_approval': True,
                'target_audience': metadata.get('target_audience', 'general'),
                'priority': metadata.get('priority', 'normal')
            }
            
            # Add any additional metadata
            for key, value in metadata.items():
                if key not in draft_metadata:
                    draft_metadata[key] = value
            
            # Create the markdown content
            content_lines = [
                "---",
                yaml.dump(draft_metadata, default_flow_style=False).strip(),
                "---",
                "",
                f"# {title}" if title else "# Draft",
                "",
                content,
                "",
                "## Approval Options",
                "- To Approve: Move this file to `/Approved/` folder",
                "- To Revise: Edit content and keep in `/Drafts/`",
                "- To Discard: Move to `/Discarded/` folder",
                "",
                "## Review Notes",
                "- Check tone and appropriateness",
                "- Verify accuracy of information",
                "- Confirm alignment with brand guidelines",
            ]
            
            draft_content = "\\n".join(content_lines)
            
            # Write the file to Drafts
            draft_path = self.drafts_path / filename
            draft_path.write_text(draft_content, encoding='utf-8')
            
            logger.info(f"Created draft: {filename}")
            return draft_path
            
        except Exception as e:
            logger.error(f"Error creating draft: {str(e)}")
            return None
    
    def create_email_draft(self, to: str, subject: str, body: str, priority: str = "normal") -> Path:
        """Create a draft email"""
        content = f"""**TO:** {to}

**SUBJECT:** {subject}

**BODY:**
{body}"""
        
        metadata = {
            'to': to,
            'subject': subject,
            'priority': priority
        }
        
        return self.create_draft("email", content, f"Email_{subject.replace(' ', '_')}", metadata)
    
    def create_social_post_draft(self, platform: str, content: str, target_audience: str = "general") -> Path:
        """Create a draft social media post"""
        content_text = f"""**PLATFORM:** {platform}

**TARGET AUDIENCE:** {target_audience}

**CONTENT:**
{content}"""
        
        metadata = {
            'platform': platform,
            'target_audience': target_audience
        }
        
        return self.create_draft("social_post", content_text, f"SocialPost_{platform}", metadata)
    
    def create_document_draft(self, doc_type: str, title: str, content: str) -> Path:
        """Create a draft document"""
        full_content = f"""**DOCUMENT TYPE:** {doc_type}

**TITLE:** {title}

**CONTENT:**
{content}"""
        
        return self.create_draft("document", full_content, f"Document_{doc_type}_{title.replace(' ', '_')}")
    
    def move_to_approval(self, draft_path: Path) -> bool:
        """Move a draft to the approval queue"""
        try:
            # Create approval request based on the draft
            approval_filename = f"APPROVAL_{draft_path.name.replace('DRAFT_', '')}"
            approval_path = self.pending_approval_path / approval_filename
            
            # Copy the draft content to the approval request
            content = draft_path.read_text(encoding='utf-8')
            approval_content = content.replace(
                "status: pending_approval", 
                "status: pending_approval"
            ).replace(
                "type: draft_", 
                "type: approval_request_for_draft_"
            )
            
            approval_path.write_text(approval_content, encoding='utf-8')
            
            # Optionally, move the original draft to a reviewed queue
            reviewed_draft_path = self.drafts_path / f"REVIEWED_{draft_path.name}"
            draft_path.rename(reviewed_draft_path)
            
            logger.info(f"Moved draft to approval: {approval_filename}")
            return True
        except Exception as e:
            logger.error(f"Error moving draft to approval: {str(e)}")
            return False
    
    def get_drafts(self) -> List[Path]:
        """Get all drafts in the Drafts folder"""
        return list(self.drafts_path.glob("*.md"))
    
    def get_draft_by_id(self, draft_id: str) -> Optional[Path]:
        """Get a specific draft by its ID (filename)"""
        draft_path = self.drafts_path / draft_id
        return draft_path if draft_path.exists() else None

def main():
    """Example usage of the draft system"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python draft_system.py <vault_path>")
        print("Or to create a sample draft:")
        print("Usage: python draft_system.py <vault_path> create_sample_email")
        print("Usage: python draft_system.py <vault_path> create_sample_social")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    draft_system = DraftSystem(vault_path)
    
    if len(sys.argv) > 2:
        if sys.argv[2] == "create_sample_email":
            # Create a sample email draft
            draft_system.create_email_draft(
                to="client@example.com",
                subject="Project Update",
                body="This is a sample email draft that requires approval before sending.",
                priority="high"
            )
            print("Sample email draft created in Drafts folder")
        elif sys.argv[2] == "create_sample_social":
            # Create a sample social media draft
            draft_system.create_social_post_draft(
                platform="LinkedIn",
                content="Exciting company update: We've reached a major milestone in our project!",
                target_audience="professional"
            )
            print("Sample social media draft created in Drafts folder")
        else:
            print("Invalid option. Use 'create_sample_email' or 'create_sample_social'")
    else:
        # List existing drafts
        drafts = draft_system.get_drafts()
        print(f"Found {len(drafts)} drafts in the Drafts folder:")
        for draft in drafts:
            print(f"  - {draft.name}")

if __name__ == "__main__":
    main()