import time
from pathlib import Path
from datetime import datetime
import sys
import os
import re
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
                
                # Navigate to WhatsApp Web
                page = browser.new_page()
                page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded')
                
                # Wait for WhatsApp to load completely
                print("Waiting for WhatsApp Web to load...")
                
                # Wait for the main app to load
                try:
                    # Wait for the chat list container to appear
                    page.wait_for_selector('div[aria-label="Chat list"]', timeout=30000)
                    print("WhatsApp Web loaded successfully - chat list found")
                except:
                    # Try alternative selectors for the chat list
                    try:
                        page.wait_for_selector('#pane-side', timeout=30000)
                        print("WhatsApp Web loaded successfully - pane-side found")
                    except:
                        # Check if QR code is still there
                        try:
                            page.wait_for_selector('canvas', timeout=5000)
                            print("QR code detected - please scan with your phone")
                            print("Waiting 30 seconds for you to scan...")
                            page.wait_for_timeout(30000)
                            
                            # Check again if we're logged in after user scans
                            try:
                                page.wait_for_selector('div[aria-label="Chat list"]', timeout=10000)
                                print("Successfully logged in to WhatsApp Web after QR scan")
                            except:
                                print("Still not logged in after waiting. Please make sure you scan the QR code.")
                                browser.close()
                                return []
                        except:
                            print("WhatsApp Web might not be loaded properly")
                            browser.close()
                            return []
                
                print("Looking for chats...")
                
                # Different selectors for chats - depending on WhatsApp Web version
                chat_selectors = [
                    'div[aria-label="Chat list"] div[role="row"]',  # Newer version
                    '#pane-side div[role="gridcell"]',  # Older version
                    'div[tabindex][role="button"]',  # General button approach
                    '[data-testid="chat-list-row"]',  # Another possible selector
                    '._3quh._30yy._2t_']  # Legacy selector
                ]
                
                chats = []
                for selector in chat_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"Found {len(elements)} chats using selector: {selector}")
                            chats = elements
                            break
                    except:
                        continue
                
                if not chats:
                    print("No chats found with any selector. Trying to find any clickable chat elements...")
                    # Try to find any elements that look like chats
                    all_divs = page.query_selector_all('div')
                    for div in all_divs:
                        class_attr = div.get_attribute('class') or ''
                        aria_label = div.get_attribute('aria-label') or ''
                        if any(keyword in class_attr.lower() or keyword in aria_label.lower() 
                               for keyword in ['chat', 'conversation', 'contact', 'pane']):
                            chats.append(div)
                    
                    print(f"Found {len(chats)} potential chat elements")
                
                print(f"Processing {len(chats)} chats...")
                
                for i, chat in enumerate(chats[:5]):  # Only process first 5 chats to avoid too much processing
                    try:
                        # Get chat name/phone number - try multiple selectors
                        chat_name = f"Chat {i+1}"  # Default name
                        
                        # Try different ways to get the chat name
                        name_selectors = [
                            '[title]',
                            'span[title]',
                            'div:nth-child(2) span:first-child',
                            'div:nth-child(2) div:first-child',
                            '.emoji-text',  # For contacts with emojis
                            '.selectable-text',
                            '*:first-child span',
                            '*:nth-child(2)'
                        ]
                        
                        for name_selector in name_selectors:
                            try:
                                name_elem = chat.query_selector(name_selector)
                                if name_elem:
                                    name_text = name_elem.text_content().strip()
                                    if name_text and len(name_text) > 0:
                                        chat_name = name_text
                                        break
                            except:
                                continue
                        
                        print(f"Processing chat: {chat_name}")
                        
                        # Click on the chat to view messages
                        try:
                            chat.click()
                            # Wait for messages to load
                            page.wait_for_timeout(2000)  # Wait for chat to load
                            
                            # Look for messages in this chat
                            message_selectors = [
                                'div[data-testid="msg"]',  # Standard message
                                '.message-in',  # Incoming message
                                '.copyable-text',  # Text content
                                '[data-pre-plain-text]',  # Messages with sender info
                                'div.message'  # Generic message
                            ]
                            
                            messages_found = []
                            for msg_selector in message_selectors:
                                try:
                                    msg_elements = page.query_selector_all(msg_selector)
                                    if msg_elements:
                                        print(f"Found {len(msg_elements)} messages with selector: {msg_selector}")
                                        messages_found.extend(msg_elements)
                                        break  # Use first successful selector
                                except:
                                    continue
                            
                            print(f"Found {len(messages_found)} messages in {chat_name}")
                            
                            for msg_element in messages_found[-5:]:  # Check last 5 messages
                                # Get message text - try multiple approaches
                                msg_text = ""
                                
                                # Try different ways to get message text
                                text_selectors = [
                                    'span.selectable-text',
                                    'span',
                                    '*',  # Get all text content
                                    '.copyable-text'
                                ]
                                
                                for text_selector in text_selectors:
                                    try:
                                        text_elem = msg_element.query_selector(text_selector)
                                        if text_elem:
                                            text_content = text_elem.text_content().strip()
                                            if text_content and len(text_content) > 0:
                                                msg_text = text_content
                                                break
                                    except:
                                        continue
                                
                                # If still no text, try getting all text content from the message element
                                if not msg_text:
                                    try:
                                        msg_text = msg_element.text_content().strip()
                                    except:
                                        msg_text = ""
                                
                                if msg_text:
                                    print(f"Found message: {msg_text[:50]}...")
                                    
                                    # Check if message contains any of our keywords
                                    matched_keywords = []
                                    for keyword in self.keywords:
                                        if keyword.lower() in msg_text.lower():
                                            if keyword not in matched_keywords:
                                                matched_keywords.append(keyword)
                                    
                                    if matched_keywords:
                                        print(f"Matched keywords: {matched_keywords}")
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
                            print(f"Error clicking chat {chat_name}: {e}")
                            continue
                    
                    except Exception as e:
                        print(f"Error processing chat element: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            print(f"Error: {e}")
            
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
        sender_clean = ''.join(c for c in message.get('from', 'unknown') if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')[:20]
        filepath = self.needs_action / f'WHATSAPP_{timestamp}_{sender_clean}.md'
        filepath.write_text(content, encoding='utf-8')
        
        self.logger.info(f"Created WhatsApp action file: {filepath.name}")
        return filepath

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python whatsapp_watcher_debug.py <vault_path> [session_path]")
        print("Example: python whatsapp_watcher_debug.py \"F:/AI_Employee_Vault/AI_Employee_Vault\"")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = WhatsAppWatcher(vault_path, session_path)
    
    print(f"WhatsApp Watcher initialized.")
    print(f"Vault path: {vault_path}")
    print(f"Session path: {watcher.session_path}")
    print(f"Monitoring for keywords: {', '.join(watcher.keywords)}")
    print("Starting WhatsApp monitoring...")
    
    # Run once to test
    messages = watcher.check_for_updates()
    print(f"Found {len(messages)} important messages")
    
    for message in messages:
        print(f"Creating action file for: {message['from']} - {message['text'][:50]}...")
        watcher.create_action_file(message)
    
    print("Test completed. Check the Needs_Action folder for new files.")