"""
Approval System for AI Employee

Implements the human-in-the-loop pattern for sensitive actions that require human authorization.
Monitors the Pending_Approval folder and executes actions when files are moved to Approved.
"""

import os
import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApprovalSystem:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.rejected_path = self.vault_path / "Rejected"
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        
        # Create necessary directories if they don't exist
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
        self.approved_path.mkdir(parents=True, exist_ok=True)
        self.rejected_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)
        
    def check_for_approvals(self) -> List[Path]:
        """Check the Approved folder for newly approved requests"""
        approved_requests = []
        
        for file_path in self.approved_path.glob("*.md"):
            # Check if this is a new file (not already processed)
            # We could use file modification time or maintain a processed list
            approved_requests.append(file_path)
                
        return approved_requests
    
    def check_for_rejections(self) -> List[Path]:
        """Check the Rejected folder for newly rejected requests"""
        rejected_requests = []
        
        for file_path in self.rejected_path.glob("*.md"):
            rejected_requests.append(file_path)
                
        return rejected_requests
    
    def execute_approved_action(self, request_path: Path):
        """Execute the action specified in an approved request"""
        try:
            content = request_path.read_text(encoding='utf-8')
            
            # Parse YAML frontmatter if it exists
            action_data = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    action_data = yaml.safe_load(frontmatter)
            
            action_type = action_data.get('action', 'unknown')
            logger.info(f"Executing approved {action_type} action from: {request_path.name}")
            
            # Execute different types of actions based on the request
            if action_type == 'payment':
                self._execute_payment(action_data)
            elif action_type == 'email':
                self._execute_email(action_data)
            elif action_type == 'file_operation':
                self._execute_file_operation(action_data)
            else:
                logger.warning(f"Unknown action type: {action_type}")
            
            # Move the request to Done after execution
            done_destination = self.done_path / request_path.name
            request_path.rename(done_destination)
            logger.info(f"Moved executed request to Done: {request_path.name}")
            
        except Exception as e:
            logger.error(f"Error executing action from {request_path.name}: {str(e)}")
    
    def handle_rejected_action(self, request_path: Path):
        """Handle a rejected action request"""
        try:
            content = request_path.read_text(encoding='utf-8')
            
            # Parse YAML frontmatter if it exists
            action_data = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    action_data = yaml.safe_load(frontmatter)
            
            reason = action_data.get('reason', 'unknown')
            logger.info(f"Handling rejected request: {reason} from {request_path.name}")
            
            # Move the request to Done after handling rejection
            done_destination = self.done_path / request_path.name
            request_path.rename(done_destination)
            logger.info(f"Moved rejected request to Done: {request_path.name}")
            
        except Exception as e:
            logger.error(f"Error handling rejected action from {request_path.name}: {str(e)}")
    
    def _execute_payment(self, action_data: Dict):
        """Execute a payment action"""
        amount = action_data.get('amount', 'unknown')
        recipient = action_data.get('recipient', 'unknown')
        logger.info(f"Processing payment of ${amount} to {recipient}")
        
        # In a real implementation, this would connect to a payment API
        # For now, we just log the action
        logger.info("Payment action would be executed here in a real implementation")
    
    def _execute_email(self, action_data: Dict):
        """Execute an email action"""
        to = action_data.get('to', 'unknown')
        subject = action_data.get('subject', 'no subject')
        logger.info(f"Sending email to {to} with subject: {subject}")
        
        # In a real implementation, this would send the actual email
        # For now, we just log the action
        logger.info("Email action would be executed here in a real implementation")
    
    def _execute_file_operation(self, action_data: Dict):
        """Execute a file operation action"""
        operation = action_data.get('operation', 'unknown')
        file_path = action_data.get('file_path', 'unknown')
        logger.info(f"Performing file operation {operation} on {file_path}")
        
        # In a real implementation, this would perform the file operation
        # For now, we just log the action
        logger.info("File operation would be executed here in a real implementation")
    
    def create_approval_request(self, action_details: Dict):
        """Create a new approval request file"""
        try:
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            action_type = action_details.get('action', 'generic')
            filename = f"APPROVAL_REQUEST_{action_type}_{timestamp}.md"
            
            # Create the content with YAML frontmatter
            frontmatter = {
                'type': 'approval_request',
                'action': action_details.get('action', 'unknown'),
                'created': datetime.now().isoformat(),
                'expires': (datetime.now().replace(day=datetime.now().day + 1)).isoformat(),  # Expires in 1 day
                'status': 'pending',
                'approver': 'human_operator'
            }
            
            # Add any additional fields from action_details
            for key, value in action_details.items():
                if key not in frontmatter:
                    frontmatter[key] = value
            
            # Create the markdown content
            content_lines = [
                "---",
                yaml.dump(frontmatter, default_flow_style=False).strip(),
                "---",
                "",
                "## Action Details",
                f"- **Action Type**: {action_details.get('action', 'unknown')}",
                f"- **Amount**: {action_details.get('amount', 'N/A')}",
                f"- **Recipient**: {action_details.get('recipient', 'N/A')}",
                f"- **Reason**: {action_details.get('reason', 'N/A')}",
                "",
                "## Approval Options",
                "- To Approve: Move this file to `/Approved/` folder",
                "- To Reject: Move this file to `/Rejected/` folder",
                "- To Defer: Add note and leave in `/Pending_Approval/`",
                "",
                "## Important Notes",
                "- Review all details carefully before approving",
                "- Contact administrator if details seem incorrect",
            ]
            
            content = "\n".join(content_lines)
            
            # Write the file to Pending_Approval
            request_path = self.pending_approval_path / filename
            request_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Created approval request: {filename}")
            return request_path
            
        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            return None
    
    def monitor_and_process(self, interval: int = 30):
        """Monitor for approved/rejected requests and process them"""
        logger.info("Starting approval system monitor...")
        
        while True:
            try:
                # Check for newly approved requests
                approved_requests = self.check_for_approvals()
                for request in approved_requests:
                    logger.info(f"Found approved request: {request.name}")
                    self.execute_approved_action(request)
                
                # Check for newly rejected requests
                rejected_requests = self.check_for_rejections()
                for request in rejected_requests:
                    logger.info(f"Found rejected request: {request.name}")
                    self.handle_rejected_action(request)
                
                # Wait before checking again
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Approval system monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in approval system monitor: {str(e)}")
                time.sleep(interval)

def main():
    """Example usage of the approval system"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python approval_system.py <vault_path>")
        print("Or to create a sample approval request:")
        print("Usage: python approval_system.py <vault_path> create_sample")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "create_sample":
        # Create a sample approval request for testing
        approval_system = ApprovalSystem(vault_path)
        
        sample_action = {
            'action': 'payment',
            'amount': '500.00',
            'recipient': 'Client A',
            'reason': 'Invoice #1234 payment',
            'description': 'Payment for completed project work'
        }
        
        approval_system.create_approval_request(sample_action)
        print("Sample approval request created in Pending_Approval folder")
    else:
        # Start monitoring for approvals
        approval_system = ApprovalSystem(vault_path)
        approval_system.monitor_and_process()

if __name__ == "__main__":
    main()