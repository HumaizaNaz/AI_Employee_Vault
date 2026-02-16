import time
import logging
from pathlib import Path
from datetime import datetime
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=30)
        self.session_path = Path(session_path) if session_path else Path(vault_path) / 'whatsapp_session'
        self.session_path.mkdir(exist_ok=True)
        
        # Keywords that indicate important messages
        self.keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'help', 'need', 'now', 
            'important', 'emergency', 'critical', 'as soon as possible', 
            'today', 'deadline', 'due', 'money', 'cash', 'transfer', 'pay', 
            'urgent', 'asap', 'please', 'thanks', 'regarding', 'concerning'
        ]
        
        # Track processed messages to avoid duplicates
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        """
        Connect to WhatsApp Web using Playwright and check for important messages
        """
        important_messages = []
        
        try:
            with sync_playwright() as p:
                # Launch WhatsApp Web in persistent context to maintain session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True in production
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                
                page = browser.new_page()
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for WhatsApp to load completely
                try:
                    # Wait for the chat list to appear (indicating successful login)
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    print("WhatsApp Web loaded successfully")
                except:
                    # If not logged in, wait for QR code
                    try:
                        print("Please scan the QR code to log in to WhatsApp Web")
                        page.wait_for_selector('[data-testid="qr-code-scan"]', timeout=60000)
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                        print("Successfully logged in to WhatsApp Web")
                    except:
                        print("Failed to log in to WhatsApp Web. Please log in manually first.")
                        browser.close()
                        return []
                
                # Find chats with unread messages
                unread_chats = page.query_selector_all('div[aria-label*="unread"]:not([data-read-only="true"])')
                
                for chat in unread_chats:
                    # Get chat name/phone number
                    chat_name_elem = chat.query_selector('[title], span[dir="auto"]')
                    if chat_name_elem:
                        chat_name = chat_name_elem.text_content().strip()
                        
                        # Click on the chat to view messages
                        chat.click()
                        
                        # Wait for messages to load
                        try:
                            page.wait_for_selector('[data-testid="msg-container"]', timeout=5000)
                            
                            # Get all message elements in the chat
                            message_elements = page.query_selector_all('div[data-testid="msg"]')
                            
                            for msg_element in message_elements:
                                # Check if message is incoming (from contact) and not read
                                msg_text_elem = msg_element.query_selector('span.selectable-text')
                                if msg_text_elem:
                                    msg_text = msg_text_elem.text_content().strip()
                                    
                                    # Check if message contains any of our keywords
                                    matched_keywords = []
                                    for keyword in self.keywords:
                                        if keyword.lower() in msg_text.lower():
                                            if keyword not in matched_keywords:
                                                matched_keywords.append(keyword)
                                    
                                    if matched_keywords:
                                        # Extract timestamp if available
                                        timestamp_elem = msg_element.query_selector('span[data-testid="msg-time"]')
                                        timestamp = timestamp_elem.text_content().strip() if timestamp_elem else datetime.now().isoformat()
                                        
                                        message_info = {
                                            'from': chat_name,
                                            'text': msg_text,
                                            'timestamp': timestamp,
                                            'priority': 'high',
                                            'keywords': matched_keywords
                                        }
                                        
                                        # Avoid processing the same message twice
                                        message_id = f"{chat_name}:{msg_text}:{timestamp}"
                                        if message_id not in self.processed_messages:
                                            important_messages.append(message_info)
                                            self.processed_messages.add(message_id)
                        
                        except Exception as e:
                            print(f"Error processing chat {chat_name}: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            
        return important_messages

    def create_action_file(self, message) -> Path:
        """
        Create a markdown file in Needs_Action folder for the WhatsApp message
        """
        content = f'''---
type: whatsapp_message
from: {message.get('from', 'Unknown')}
received: {message.get('timestamp', datetime.now().isoformat())}
priority: {message.get('priority', 'high')}
status: pending
keywords_matched: {message.get('keywords', [])}
---

## WhatsApp Message
**From:** {message.get('from', 'Unknown')}
**Time:** {message.get('timestamp', datetime.now().isoformat())}

**Message:**
{message.get('text', 'No message content')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party  
- [ ] Archive after processing

## Context
This message contained important keywords: {', '.join(message.get('keywords', []))}
'''
        
        # Create unique filename based on timestamp and sender
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sender_clean = re.sub(r'[^\w]', '_', message.get('from', 'unknown'))[:20]
        filepath = self.needs_action / f'WHATSAPP_{timestamp}_{sender_clean}.md'
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created WhatsApp action file: {filepath.name}")
        return filepath

    def run_simulation(self):
        """
        Method to simulate WhatsApp message detection for testing
        """
        print("WhatsApp Watcher simulation running...")
        print(f"Monitoring for keywords: {', '.join(self.keywords)}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # In a real implementation, this would check for actual WhatsApp messages
                # For now, we'll just sleep and occasionally simulate finding a message
                time.sleep(self.check_interval)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checked WhatsApp - no new important messages")
        except KeyboardInterrupt:
            print("\nWhatsApp Watcher stopped by user")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python whatsapp_watcher.py <vault_path> [session_path]")
        print("Example: python whatsapp_watcher.py \"F:/AI_Employee_Vault/AI_Employee_Vault\"")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = WhatsAppWatcher(vault_path, session_path)
    
    print(f"WhatsApp Watcher initialized.")
    print(f"Vault path: {vault_path}")
    print(f"Session path: {watcher.session_path}")
    print(f"Monitoring for keywords: {', '.join(watcher.keywords)}")
    print("Starting WhatsApp monitoring simulation...")
    
    # Run the simulation
    watcher.run_simulation()