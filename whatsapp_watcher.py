import time
from pathlib import Path
from datetime import datetime
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

        # Set the needs_action folder to the WhatsApp subdirectory
        self.needs_action = Path(vault_path) / 'Needs_Action' / 'WhatsApp'
        self.needs_action.mkdir(exist_ok=True)

        # Keywords that indicate important messages
        self.keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'help', 'need', 'now',
            'important', 'emergency', 'critical', 'as soon as possible',
            'today', 'deadline', 'due', 'money', 'cash', 'transfer', 'pay',
            'meeting', 'schedule', 'appointment', 'call', 'urgent', 'asap',
            'please', 'thanks', 'regarding', 'concerning', 'hi', 'hello'
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

                # Wait for the main app to load - try multiple selectors for current UI
                loaded = False
                selectors_to_try = [
                    '[data-testid="chat-list-search"]',  # Current search box in chat list
                    '[data-testid="default-user"]',     # Chat list items
                    'div[aria-label="Chat list"]',       # Chat list container
                    '[data-testid="chat"]',             # Chat elements
                    '#side',                            # Side panel containing chats
                    '._3quh._30yy._2t_',               # Legacy selector
                ]

                for selector in selectors_to_try:
                    try:
                        page.wait_for_selector(selector, timeout=15000)
                        print(f"WhatsApp Web loaded successfully - found selector: {selector}")
                        loaded = True
                        break
                    except Exception as e:
                        print(f"Selector {selector} failed: {str(e)}")
                        continue

                if not loaded:
                    print("Could not detect WhatsApp Web UI. Checking if QR code is present...")
                    try:
                        # Check for QR code canvas - this appears when not logged in
                        qr_selector = 'canvas'
                        if page.query_selector(qr_selector):
                            print("QR code detected - please scan with your phone")
                            print("Waiting 60 seconds for you to scan...")
                            page.wait_for_timeout(60000)  # Wait 60 seconds for user to scan

                            # Try again after potential QR scan
                            for selector in selectors_to_try:
                                try:
                                    page.wait_for_selector(selector, timeout=15000)
                                    print(f"Successfully logged in to WhatsApp Web after QR scan - found selector: {selector}")
                                    loaded = True
                                    break
                                except:
                                    continue
                    except Exception as e:
                        print(f"QR code check failed: {str(e)}")

                    if not loaded:
                        print("WhatsApp Web not loaded properly after waiting. Exiting.")
                        browser.close()
                        return []

                print("Looking for chats with unread messages...")

                # Updated approach to find chats with unread messages
                # Look for chat elements that have unread indicators
                chat_selectors = [
                    'div[data-testid="chat"]',  # Current WhatsApp Web chat selector
                    '[data-testid="default-user"]',  # Another common selector
                    'div[tabindex="-1"][role="button"]',  # Standard chat button
                    '#pane-side div[role="row"]',  # Chat rows in side panel
                ]

                chat_elements = []
                for selector in chat_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"Found {len(elements)} chat elements using selector: {selector}")
                            chat_elements = elements
                            break
                    except Exception as e:
                        print(f"Error querying selector {selector}: {str(e)}")
                        continue

                if not chat_elements:
                    print("No chat elements found with specific selectors")
                    browser.close()
                    return []

                print(f"Processing {len(chat_elements)} chat elements...")

                # Process each chat to look for unread/important messages
                for i, chat_element in enumerate(chat_elements[:20]):  # Limit to first 20 chats
                    try:
                        # Get the chat name/title - try multiple approaches for current UI
                        chat_name = f"Chat {i+1}"  # Default name
                        
                        # Try different ways to get the chat name for current UI
                        name_selectors = [
                            '[title]',  # Title attribute often contains contact name
                            '[data-testid="chat-list-name"]',  # WhatsApp Web specific
                            '._3j7s > span',  # Contact name span
                            '._1wjpf',  # Name element
                            '[data-testid="cell-frame-title"] span',  # Chat title
                            'span[title]',  # Span with title
                        ]

                        for name_selector in name_selectors:
                            try:
                                name_elem = chat_element.query_selector(name_selector)
                                if name_elem:
                                    name_text = name_elem.text_content().strip()
                                    if name_text and len(name_text) > 0 and not name_text.isspace():
                                        chat_name = name_text
                                        break
                            except:
                                continue

                        # If we still have a generic name, try to get text content directly
                        if chat_name.startswith("Chat "):
                            try:
                                # Try to get the first text element that looks like a name
                                text_elements = chat_element.query_selector_all('span, div')
                                for text_elem in text_elements:
                                    try:
                                        text_content = text_elem.text_content().strip()
                                        if (text_content and 
                                            len(text_content) > 1 and 
                                            not text_content.isdigit() and
                                            not text_content.startswith('Chat')):
                                            chat_name = text_content
                                            break
                                    except:
                                        continue
                            except:
                                pass

                        print(f"Examining chat: {chat_name}")

                        # Check if this chat has unread messages by looking for indicators
                        has_unread = False
                        unread_indicators = [
                            '[data-testid="unread-count"]',  # Current unread count
                            '.P6z4j',  # Unread message bubble class
                            '[data-icon="unreadMentionCount"]',  # Mention count icon
                            '[data-testid="icon-unread"]',  # Unread icon
                            '.unread',  # Unread class
                            'span[class*="unread"]',  # Unread spans
                            '[aria-label*="unread"]',  # Unread aria labels
                            '.P6z4j ._158g',  # Unread count specific class
                        ]

                        for indicator in unread_indicators:
                            try:
                                if chat_element.query_selector(indicator):
                                    has_unread = True
                                    print(f"Unread indicator found in {chat_name}")
                                    break
                            except:
                                continue

                        # Only process chats that have unread messages or are marked as important
                        if not has_unread:
                            print(f"No unread messages in {chat_name}, skipping...")
                            continue

                        print(f"Opening chat: {chat_name} (has_unread: {has_unread})")

                        # Click on the chat to open it and view messages
                        try:
                            # Scroll the element into view first to ensure it's clickable
                            chat_element.scroll_into_view_if_needed()
                            
                            # Try multiple methods to click the chat
                            clicked = False
                            click_methods = [
                                lambda: chat_element.click(),
                                lambda: chat_element.dispatch_event('click'),
                                lambda: page.evaluate('(element) => element.click()', chat_element)
                            ]
                            
                            for click_method in click_methods:
                                try:
                                    click_method()
                                    page.wait_for_timeout(1000)  # Small delay after click
                                    clicked = True
                                    break
                                except:
                                    continue
                            
                            if not clicked:
                                print(f"Could not click on chat {chat_name}")
                                continue

                            # Wait for messages to load in the chat
                            page.wait_for_timeout(3000)  # Wait 3 seconds for messages to load

                            # Look for messages in the chat window - updated selectors for current UI
                            message_selectors = [
                                '[data-testid="msg"]',  # Current message selector
                                'div.message-in',  # Incoming message
                                '[data-pre-plain-text]',  # Messages with sender info
                                '.copyable-text',  # Copyable message text
                                'span.selectable-text',  # Selectable message text
                                '.bubble',  # Message bubble
                                '.message',  # Generic message
                            ]

                            messages_found = []
                            for msg_selector in message_selectors:
                                try:
                                    msg_elements = page.query_selector_all(msg_selector)
                                    if msg_elements:
                                        print(f"Found {len(msg_elements)} elements with selector: {msg_selector}")
                                        # Filter out empty elements and get message text
                                        for elem in msg_elements:
                                            try:
                                                # For messages with sender info
                                                if elem.get_attribute('data-pre-plain-text'):
                                                    text = elem.text_content().strip()
                                                    if text and len(text) > 0:
                                                        messages_found.append((elem, text))
                                                else:
                                                    # For other message types
                                                    text = elem.text_content().strip()
                                                    if text and len(text) > 0:
                                                        messages_found.append((elem, text))
                                            except Exception as e:
                                                print(f"Error getting text from element: {str(e)}")
                                                continue
                                        break  # Use first successful selector
                                except Exception as e:
                                    print(f"Error querying message selector {msg_selector}: {str(e)}")
                                    continue

                            print(f"Found {len(messages_found)} actual messages in {chat_name}")

                            # Process each message
                            for msg_element, msg_text in messages_found[-10:]:  # Check last 10 messages
                                print(f"Analyzing message: {msg_text[:50]}...")

                                # Check if message contains any of our keywords
                                matched_keywords = []
                                for keyword in self.keywords:
                                    if keyword.lower() in msg_text.lower():
                                        if keyword not in matched_keywords:
                                            matched_keywords.append(keyword)

                                if matched_keywords or has_unread:  # Include unread messages even without keywords
                                    print(f"Matched keywords: {matched_keywords}")

                                    # Create message info
                                    message_info = {
                                        'from': chat_name,
                                        'text': msg_text,
                                        'timestamp': datetime.now().isoformat(),
                                        'priority': 'high' if matched_keywords else 'medium',
                                        'keywords': matched_keywords
                                    }

                                    # Avoid processing the same message twice
                                    message_id = f"{chat_name}:{msg_text}:{datetime.now().isoformat()}"
                                    if message_id not in self.processed_messages:
                                        important_messages.append(message_info)
                                        self.processed_messages.add(message_id)
                                        print(f"Added important message from {chat_name}")

                        except Exception as e:
                            print(f"Error clicking chat {chat_name}: {str(e)}")
                            continue

                    except Exception as e:
                        print(f"Error processing chat element {i+1}: {str(e)}")
                        continue

                browser.close()

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {str(e)}")
            print(f"Error: {str(e)}")

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
        # Clean sender name for filename
        sender_clean = ''.join(c for c in message.get('from', 'unknown') if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')[:20]
        filepath = self.needs_action / f'WHATSAPP_{timestamp}_{sender_clean}.md'
        
        # Write the file with proper error handling
        try:
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created WhatsApp action file: {filepath.name}")
        except Exception as e:
            self.logger.error(f"Error creating action file {filepath.name}: {str(e)}")
            # Create a simplified filename if the original fails
            fallback_filepath = self.needs_action / f'WHATSAPP_{timestamp}_unknown.md'
            fallback_content = content.replace(message.get('from', 'Unknown'), 'Unknown')
            fallback_filepath.write_text(fallback_content, encoding='utf-8')
            self.logger.info(f"Created fallback WhatsApp action file: {fallback_filepath.name}")
            return fallback_filepath
        
        return filepath

    def run_once(self):
        """
        Run a single check cycle - useful for testing
        """
        self.logger.info(f'Starting single check for {self.__class__.__name__}')
        try:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            return len(items)
        except Exception as e:
            self.logger.error(f"Error during single check: {str(e)}")
            return 0

    def run(self):
        """
        Run the WhatsApp watcher continuously with improved error handling
        """
        self.logger.info(f'Starting {self.__class__.__name__} with interval {self.check_interval}s')
        print(f'Starting {self.__class__.__name__} with interval {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                
                # Process each item found
                for item in items:
                    try:
                        self.create_action_file(item)
                        print(f"Created action file for message from {item.get('from', 'Unknown')}")
                    except Exception as e:
                        self.logger.error(f"Error creating action file: {str(e)}")
                        
                if items:
                    print(f"Processed {len(items)} important WhatsApp messages")
                    
                # Wait for the specified interval before next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\nWhatsApp Watcher stopped by user")
                self.logger.info("WhatsApp Watcher stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in WhatsApp watcher: {str(e)}")
                print(f"Error in WhatsApp watcher: {str(e)}")
                
                # Wait before retrying to avoid rapid error loops
                time.sleep(min(self.check_interval, 30))  # Wait at least 30 seconds or check_interval if smaller


if __name__ == "__main__":
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
    print("Starting WhatsApp monitoring...")

    # For initial testing, run once
    count = watcher.run_once()
    print(f"Found {count} important WhatsApp messages")

    # Uncomment the next line to run continuously
    # watcher.run()