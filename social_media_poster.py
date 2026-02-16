#!/usr/bin/env python3
"""
Social Media Poster for AI Employee System
This script helps post to Facebook and Instagram using your existing tokens
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path("F:/AI_Employee_Vault/AI_Employee_Vault/Accounting/.env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    return True

def post_to_facebook(message, link=None):
    """Post to Facebook page using the access token"""
    load_environment()
    
    access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
    if not access_token:
        print("❌ No Facebook access token found in environment")
        return False
    
    try:
        # Get page ID first (we need to know which page to post to)
        page_info_url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}&fields=id,name"
        page_response = requests.get(page_info_url)
        
        if page_response.status_code != 200:
            print(f"❌ Error getting page info: {page_response.text}")
            return False
        
        page_data = page_response.json()
        page_id = page_data.get('id')
        page_name = page_data.get('name', 'Unknown')
        
        print(f"🎯 Selected Facebook Page: {page_name} (ID: {page_id})")
        
        # Prepare post data
        post_data = {
            'message': message,
            'access_token': access_token
        }
        
        if link:
            post_data['link'] = link
        
        # Make the post
        post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        response = requests.post(post_url, data=post_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully posted to Facebook!")
            print(f"   Post ID: {result.get('id', 'Unknown')}")
            print(f"   Message: {message[:50]}...")
            return True
        else:
            print(f"❌ Facebook post failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting to Facebook: {str(e)}")
        return False

def post_to_instagram(caption, image_url=None):
    """Post to Instagram using the access token"""
    load_environment()
    
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    if not access_token:
        print("❌ No Instagram access token found in environment")
        return False
    
    try:
        # First, get Instagram account information
        account_url = f"https://graph.instagram.com/v18.0/me?fields=id,username,account_type&access_token={access_token}"
        account_response = requests.get(account_url)
        
        if account_response.status_code != 200:
            print(f"❌ Error getting Instagram account info: {account_response.text}")
            return False
        
        account_data = account_response.json()
        instagram_account_id = account_data.get('id')
        username = account_data.get('username', 'Unknown')
        
        print(f"🎯 Selected Instagram Account: @{username} (ID: {account_id})")
        
        if image_url:
            # For image posts, we need to create a media object first
            media_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': access_token
            }
            
            # Create media container
            creation_url = f"https://graph.instagram.com/v18.0/{account_id}/media"
            creation_response = requests.post(creation_url, data=media_data)
            
            if creation_response.status_code != 200:
                print(f"❌ Error creating Instagram media container: {creation_response.text}")
                return False
            
            creation_result = creation_response.json()
            container_id = creation_result.get('id')
            
            if not container_id:
                print("❌ No container ID returned from Instagram")
                return False
            
            print(f"📦 Media container created with ID: {container_id}")
            
            # Now publish the media (this might take a few seconds)
            publish_data = {
                'creation_id': container_id,
                'access_token': access_token
            }
            
            publish_url = f"https://graph.instagram.com/v18.0/{account_id}/media_publish"
            publish_response = requests.post(publish_url, data=publish_data)
            
            if publish_response.status_code == 200:
                publish_result = publish_response.json()
                post_id = publish_result.get('id')
                print(f"✅ Successfully published Instagram post!")
                print(f"   Post ID: {post_id}")
                print(f"   Caption: {caption[:50]}...")
                return True
            else:
                print(f"❌ Instagram publish failed: {publish_response.text}")
                return False
        else:
            # For text-only posts (though Instagram prefers images), we can try to post
            # Note: Instagram typically requires media, so this might fail
            media_data = {
                'caption': caption,
                'access_token': access_token
            }
            
            creation_url = f"https://graph.instagram.com/v18.0/{account_id}/media"
            creation_response = requests.post(creation_url, data=media_data)
            
            if creation_response.status_code == 200:
                creation_result = creation_response.json()
                container_id = creation_result.get('id')
                
                if container_id:
                    # Publish the media
                    publish_data = {
                        'creation_id': container_id,
                        'access_token': access_token
                    }
                    
                    publish_url = f"https://graph.instagram.com/v18.0/{account_id}/media_publish"
                    publish_response = requests.post(publish_url, data=publish_data)
                    
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        post_id = publish_result.get('id')
                        print(f"✅ Successfully published Instagram post!")
                        print(f"   Post ID: {post_id}")
                        print(f"   Caption: {caption[:50]}...")
                        return True
                    else:
                        print(f"❌ Instagram publish failed: {publish_response.text}")
                        return False
                else:
                    print("❌ No container ID returned from Instagram")
                    return False
            else:
                print(f"❌ Instagram media creation failed (this is expected for text-only posts): {creation_response.text}")
                print("💡 Note: Instagram typically requires an image/video URL to create posts")
                return False
                
    except Exception as e:
        print(f"❌ Error posting to Instagram: {str(e)}")
        return False

def main():
    print("[TARGET] AI Employee - Social Media Poster")
    print("=" * 50)
    print("This tool helps you post to Facebook and Instagram")
    print("using your configured access tokens.\n")
    
    while True:
        print("Choose an action:")
        print("1. Post to Facebook")
        print("2. Post to Instagram") 
        print("3. Post to both Facebook and Instagram")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '4':
            print("👋 Goodbye!")
            break
        elif choice in ['1', '2', '3']:
            message = input("Enter your message/post: ").strip()
            
            if not message:
                print("❌ Message cannot be empty!\n")
                continue
            
            if choice == '1':
                # Facebook only
                link = input("Enter link URL (optional, press Enter to skip): ").strip() or None
                print(f"\n📤 Posting to Facebook...")
                success = post_to_facebook(message, link)
                if success:
                    print("✅ Facebook post completed successfully!")
                else:
                    print("❌ Facebook post failed!")
                    
            elif choice == '2':
                # Instagram only
                image_url = input("Enter image URL (required for Instagram): ").strip()
                if not image_url:
                    print("❌ Instagram posts typically require an image URL!")
                    continue
                    
                print(f"\n📤 Posting to Instagram...")
                success = post_to_instagram(message, image_url)
                if success:
                    print("✅ Instagram post completed successfully!")
                else:
                    print("❌ Instagram post failed!")
                    
            elif choice == '3':
                # Both Facebook and Instagram
                link = input("Enter link URL for Facebook (optional, press Enter to skip): ").strip() or None
                image_url = input("Enter image URL for Instagram (required): ").strip()
                if not image_url:
                    print("❌ Instagram posts require an image URL!")
                    continue
                
                print(f"\n📤 Posting to Facebook...")
                fb_success = post_to_facebook(message, link)
                
                print(f"\n📤 Posting to Instagram...")
                ig_success = post_to_instagram(message, image_url)
                
                print(f"\n📊 Posting Results:")
                print(f"   Facebook: {'✅ Success' if fb_success else '❌ Failed'}")
                print(f"   Instagram: {'✅ Success' if ig_success else '❌ Failed'}")
                
                if fb_success and ig_success:
                    print("🎉 Both posts completed successfully!")
                elif fb_success or ig_success:
                    print("👍 At least one post succeeded!")
                else:
                    print("😞 Both posts failed!")
            
            print()  # Empty line for spacing
        else:
            print("❌ Invalid choice! Please enter 1, 2, 3, or 4.\n")

if __name__ == "__main__":
    main()