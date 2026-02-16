"""
Claim System for AI Employee Coordination

Implements the claim-by-move rule to prevent double-work between multiple AI agents.
When an agent finds a task in /Needs_Action/, it attempts to move it to /In_Progress/<agent_name>/
If successful, the agent owns the task; if not, another agent has already claimed it.
"""

import os
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaimSystem:
    def __init__(self, vault_path: str, agent_name: str):
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.in_progress_path = self.vault_path / "In_Progress" / agent_name
        self.done_path = self.vault_path / "Done"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        
        # Create necessary directories if they don't exist
        self.in_progress_path.mkdir(parents=True, exist_ok=True)
        
    def scan_unclaimed_tasks(self) -> List[Path]:
        """Scan /Needs_Action/ folder for unclaimed tasks"""
        unclaimed_tasks = []
        
        for file_path in self.needs_action_path.glob("*.md"):
            # Check if the task is already claimed by looking at other agent folders
            is_claimed = False
            
            # Look for this specific file in other agent's in-progress folders
            in_progress_base = self.vault_path / "In_Progress"
            if in_progress_base.exists():
                for agent_folder in in_progress_base.iterdir():
                    if agent_folder.is_dir() and agent_folder.name != self.agent_name:
                        agent_task_path = agent_folder / file_path.name
                        if agent_task_path.exists():
                            is_claimed = True
                            break
            
            if not is_claimed:
                unclaimed_tasks.append(file_path)
                
        return unclaimed_tasks
    
    def claim_task(self, task_path: Path) -> bool:
        """
        Attempt to claim a task by moving it from Needs_Action to In_Progress/<agent_name>/
        Returns True if successful, False if another agent claimed it first
        """
        destination = self.in_progress_path / task_path.name
        
        try:
            # Atomic move operation
            shutil.move(str(task_path), str(destination))
            logger.info(f"Successfully claimed task: {task_path.name}")
            
            # Update the task file with claim information
            self._update_task_claim_info(destination)
            
            return True
        except FileNotFoundError:
            # Another agent claimed the task before us
            logger.info(f"Failed to claim task (already claimed): {task_path.name}")
            return False
        except Exception as e:
            logger.error(f"Error claiming task {task_path.name}: {str(e)}")
            return False
    
    def _update_task_claim_info(self, task_path: Path):
        """Update the task file with claim information"""
        try:
            content = task_path.read_text(encoding='utf-8')
            
            # Look for YAML frontmatter
            if content.startswith("---"):
                # Split the content to find the frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    rest_content = parts[2]
                    
                    # Check if claimed_by already exists
                    if "claimed_by:" not in frontmatter:
                        # Add claim information to frontmatter
                        updated_frontmatter = f"{frontmatter}\nclaimed_by: {self.agent_name}\nclaimed_at: {datetime.now().isoformat()}"
                        updated_content = f"---\n{updated_frontmatter}\n---{rest_content}"
                        
                        task_path.write_text(updated_content, encoding='utf-8')
                    else:
                        # Update existing claim information
                        import re
                        updated_frontmatter = re.sub(r'claimed_by:.*', f'claimed_by: {self.agent_name}', frontmatter)
                        updated_frontmatter = re.sub(r'claimed_at:.*', f'claimed_at: {datetime.now().isoformat()}', updated_frontmatter)
                        updated_content = f"---\n{updated_frontmatter}\n---{rest_content}"
                        
                        task_path.write_text(updated_content, encoding='utf-8')
            else:
                # If no frontmatter, add it at the beginning
                new_content = f"""---
claimed_by: {self.agent_name}
claimed_at: {datetime.now().isoformat()}
---

{content}"""
                task_path.write_text(new_content, encoding='utf-8')
                
        except Exception as e:
            logger.error(f"Error updating task claim info for {task_path.name}: {str(e)}")
    
    def release_task(self, task_path: Path, destination_folder: str = "Needs_Action"):
        """Release a task back to Needs_Action or move to another folder"""
        try:
            if destination_folder == "Needs_Action":
                destination = self.needs_action_path / task_path.name
            elif destination_folder == "Done":
                destination = self.done_path / task_path.name
            elif destination_folder == "Pending_Approval":
                destination = self.pending_approval_path / task_path.name
            else:
                # Custom destination
                destination = self.vault_path / destination_folder / task_path.name
                destination.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(task_path), str(destination))
            logger.info(f"Released task: {task_path.name} to {destination_folder}")
        except Exception as e:
            logger.error(f"Error releasing task {task_path.name}: {str(e)}")

def main():
    """Example usage of the claim system"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python claim_system.py <vault_path> <agent_name>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    agent_name = sys.argv[2]
    
    claim_system = ClaimSystem(vault_path, agent_name)
    
    print(f"Scanning for unclaimed tasks as agent '{agent_name}'...")
    unclaimed_tasks = claim_system.scan_unclaimed_tasks()
    
    print(f"Found {len(unclaimed_tasks)} unclaimed tasks")
    
    if unclaimed_tasks:
        for task in unclaimed_tasks[:3]:  # Only claim up to 3 tasks
            print(f"Attempting to claim: {task.name}")
            success = claim_system.claim_task(task)
            if success:
                print(f"Successfully claimed: {task.name}")
                break
            else:
                print(f"Failed to claim: {task.name} (already taken)")
    else:
        print("No unclaimed tasks found")

if __name__ == "__main__":
    main()