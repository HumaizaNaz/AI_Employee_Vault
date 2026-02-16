#!/usr/bin/env python3
"""
Direct Facebook Post Script
This script will make a direct post to Facebook using your configured access token
"""

import requests
import json
import os
from pathlib import Path

def load_config():
    """Load configuration from the .env file"""
    env_path = Path("F:/AI_Employee_Vault/AI_Employee_Vault/Accounting/.env")
    config = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    
    return config

def get_page_info(access_token):
    """Get the Facebook page information"""
    try:
        # Get list of pages the user manages
        url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                # Get the first page (you can modify this to select a specific page)
                page = data['data'][0]
                return page['id'], page['name'], page['access_token']
            else:
                print("❌ No Facebook pages found associated with this account")
                return None, None, None
        else:
            print(f"❌ Error getting page info: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"❌ Error getting page info: {str(e)}")
        return None, None, None

def post_to_facebook(message, link=None):
    """Post directly to Facebook page"""
    config = load_config()
    access_token = config.get('FACEBOOK_PAGE_ACCESS_TOKEN')
    
    if not access_token or access_token == "":
        print("❌ Facebook access token not found in configuration")
        print("💡 Please update your .env file with your Facebook page access token")
        return False
    
    try:
        # First, get the page information
        page_id, page_name, page_token = get_page_info(access_token)
        
        if not page_id:
            print("❌ Could not retrieve Facebook page information")
            return False
        
        print(f"🎯 Selected Facebook Page: {page_name} (ID: {page_id})")
        
        # Prepare the post data
        post_data = {
            'message': message,
            'access_token': page_token  # Use the page-specific token
        }
        
        if link:
            post_data['link'] = link
        
        # Make the post to the page
        post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        response = requests.post(post_url, data=post_data)
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id')
            print(f"✅ SUCCESS! Post published to Facebook!")
            print(f"📄 Post ID: {post_id}")
            print(f"🎯 Page: {page_name}")
            print(f"📝 Message: {message[:100]}...")
            return True
        else:
            print(f"❌ Failed to post to Facebook: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting to Facebook: {str(e)}")
        return False

def main():
    print("[TARGET] AI Employee - Direct Facebook Poster")
    print("=" * 50)
    print()

    # The Gold Tier achievement announcement
    gold_tier_post = """[ANNOUNCEMENT] AMAZING MILESTONE ACHIEVED! 

We're thrilled to announce that our AI Employee System has officially achieved GOLD TIER status! Our autonomous digital employee now seamlessly manages Gmail, WhatsApp, file systems, integrates with Odoo accounting, and handles social media - all while maintaining human-in-the-loop security.

This represents weeks of development to create a truly autonomous business assistant that operates 24/7.

Our AI Employee can now:
- Monitor and process Gmail automatically
- Monitor WhatsApp for important messages
- Process file drops and categorize them
- Integrate with Odoo for accounting
- Post to social media platforms
- Generate weekly business audits
- Operate with human oversight for security

A huge step forward in autonomous business management! 

#AIEmployee #GoldTier #Automation #BusinessEfficiency #Innovation #2026"""

    print("[INFO] Preparing to post Gold Tier achievement announcement...")
    print()
    print("[CONTENT] Post Content:")
    print("-" * 20)
    print(gold_tier_post)
    print("-" * 20)
    print()

    confirm = input("[CONFIRM] Do you want to post this to your Facebook page? (y/n): ")

    if confirm.lower() in ['y', 'yes', '1', 'true']:
        print("\n[POSTING] Posting to Facebook...")
        success = post_to_facebook(gold_tier_post)

        if success:
            print("\n[SUCCESS] CONGRATULATIONS! Your Gold Tier achievement has been posted to Facebook!")
            print("Your AI Employee system milestone is now public!")
        else:
            print("\n[ERROR] Failed to post to Facebook. Please check your configuration.")
    else:
        print("\n[CANCELLED] Post cancelled by user.")

    print("\n[TIP] You can use this script anytime to make direct posts to Facebook")
    print("[TIP] Just update the message content as needed")

if __name__ == "__main__":
    main()