"""
Twitter/X Poster for AI Employee System
Posts tweets using Twitter API v2 with OAuth 1.0a
"""

import os
import json
import hmac
import hashlib
import time
import base64
import urllib.parse
import uuid
import requests
from pathlib import Path
from datetime import datetime


def load_twitter_config() -> dict:
    """Load Twitter API credentials from .env file."""
    config = {}
    env_paths = [
        Path(os.environ.get("VAULT_PATH", "F:/AI_Employee_Vault/AI_Employee_Vault")) / "Accounting" / ".env",
        Path("F:/AI_Employee_Vault/AI_Employee_Vault/Accounting/.env"),
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
            break

    return config


def create_oauth_signature(method, url, params, consumer_secret, token_secret):
    """Create OAuth 1.0a signature for Twitter API."""
    # Sort parameters
    sorted_params = sorted(params.items())
    param_string = '&'.join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" for k, v in sorted_params)

    # Create signature base string
    base_string = '&'.join([
        method.upper(),
        urllib.parse.quote(url, safe=''),
        urllib.parse.quote(param_string, safe='')
    ])

    # Create signing key
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"

    # Generate signature
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    return signature


def post_tweet(text: str) -> dict:
    """Post a tweet to Twitter/X using API v2 with OAuth 1.0a."""
    config = load_twitter_config()

    api_key = config.get('TWITTER_API_KEY', '')
    api_secret = config.get('TWITTER_API_SECRET', '')
    access_token = config.get('TWITTER_ACCESS_TOKEN', '')
    access_token_secret = config.get('TWITTER_ACCESS_TOKEN_SECRET', '')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        return {"success": False, "error": "Twitter API credentials not configured. Check Accounting/.env"}

    url = "https://api.twitter.com/2/tweets"

    # OAuth parameters
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }

    # Create signature
    signature = create_oauth_signature('POST', url, oauth_params, api_secret, access_token_secret)
    oauth_params['oauth_signature'] = signature

    # Create Authorization header
    auth_header = 'OAuth ' + ', '.join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )

    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }

    payload = {"text": text}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            data = response.json()
            tweet_id = data.get('data', {}).get('id', 'unknown')
            print(f"[TWITTER] Tweet posted successfully! ID: {tweet_id}")
            return {"success": True, "tweet_id": tweet_id, "data": data}
        else:
            error_msg = response.text
            print(f"[TWITTER] Failed to post: {response.status_code} - {error_msg}")
            return {"success": False, "error": error_msg, "status_code": response.status_code}

    except Exception as e:
        print(f"[TWITTER] Error: {e}")
        return {"success": False, "error": str(e)}


def get_twitter_profile() -> dict:
    """Get authenticated user's Twitter profile to verify credentials."""
    config = load_twitter_config()

    api_key = config.get('TWITTER_API_KEY', '')
    api_secret = config.get('TWITTER_API_SECRET', '')
    access_token = config.get('TWITTER_ACCESS_TOKEN', '')
    access_token_secret = config.get('TWITTER_ACCESS_TOKEN_SECRET', '')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        return {"success": False, "error": "Twitter API credentials not configured"}

    url = "https://api.twitter.com/2/users/me"

    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }

    signature = create_oauth_signature('GET', url, oauth_params, api_secret, access_token_secret)
    oauth_params['oauth_signature'] = signature

    auth_header = 'OAuth ' + ', '.join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )

    headers = {'Authorization': auth_header}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            username = data.get('data', {}).get('username', 'unknown')
            name = data.get('data', {}).get('name', 'unknown')
            print(f"[TWITTER] Authenticated as: @{username} ({name})")
            return {"success": True, "username": username, "name": name, "data": data}
        else:
            return {"success": False, "error": response.text, "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def post_to_all_platforms(message: str, image_url: str = None) -> dict:
    """Post to Twitter, Facebook, and Instagram simultaneously."""
    results = {}

    # Twitter
    print("\n[POST] Posting to Twitter/X...")
    results['twitter'] = post_tweet(message[:280])  # Twitter 280 char limit

    # Facebook
    print("[POST] Posting to Facebook...")
    config = load_twitter_config()
    fb_token = config.get('FACEBOOK_PAGE_ACCESS_TOKEN', '')
    if fb_token:
        try:
            r = requests.get(f"https://graph.facebook.com/v18.0/me?access_token={fb_token}&fields=id")
            if r.status_code == 200:
                page_id = r.json().get('id')
                post_data = {'message': message, 'access_token': fb_token}
                r2 = requests.post(f"https://graph.facebook.com/v18.0/{page_id}/feed", data=post_data)
                results['facebook'] = {"success": r2.status_code == 200, "data": r2.json()}
                print(f"[POST] Facebook: {'Success' if r2.status_code == 200 else 'Failed'}")
            else:
                results['facebook'] = {"success": False, "error": "Invalid token"}
        except Exception as e:
            results['facebook'] = {"success": False, "error": str(e)}
    else:
        results['facebook'] = {"success": False, "error": "No Facebook token"}

    # Instagram (requires image)
    if image_url:
        print("[POST] Posting to Instagram...")
        ig_token = config.get('INSTAGRAM_USER_TOKEN', '')
        ig_account = config.get('INSTAGRAM_ACCOUNT_ID', '')
        if ig_token and ig_account:
            try:
                r1 = requests.post(
                    f"https://graph.facebook.com/v18.0/{ig_account}/media",
                    data={'image_url': image_url, 'caption': message, 'access_token': ig_token}
                )
                if r1.status_code == 200:
                    container_id = r1.json().get('id')
                    time.sleep(5)
                    r2 = requests.post(
                        f"https://graph.facebook.com/v18.0/{ig_account}/media_publish",
                        data={'creation_id': container_id, 'access_token': ig_token}
                    )
                    results['instagram'] = {"success": r2.status_code == 200, "data": r2.json()}
                    print(f"[POST] Instagram: {'Success' if r2.status_code == 200 else 'Failed'}")
                else:
                    results['instagram'] = {"success": False, "error": r1.json()}
            except Exception as e:
                results['instagram'] = {"success": False, "error": str(e)}
        else:
            results['instagram'] = {"success": False, "error": "No Instagram token"}
    else:
        results['instagram'] = {"success": False, "error": "Image URL required for Instagram"}

    # Summary
    print("\n[POST] === Results ===")
    for platform, result in results.items():
        status = "OK" if result.get('success') else "FAIL"
        print(f"  {platform}: {status}")

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python twitter_poster.py test          - Verify credentials")
        print("  python twitter_poster.py tweet <text>   - Post a tweet")
        print("  python twitter_poster.py all <text>     - Post to all platforms")
        sys.exit(1)

    action = sys.argv[1]

    if action == "test":
        result = get_twitter_profile()
        if result['success']:
            print(f"Credentials valid! Logged in as @{result['username']}")
        else:
            print(f"Failed: {result.get('error')}")

    elif action == "tweet" and len(sys.argv) > 2:
        text = ' '.join(sys.argv[2:])
        result = post_tweet(text)
        if result['success']:
            print(f"Tweet posted! ID: {result['tweet_id']}")
        else:
            print(f"Failed: {result.get('error')}")

    elif action == "all" and len(sys.argv) > 2:
        text = ' '.join(sys.argv[2:])
        post_to_all_platforms(text)

    else:
        print("Invalid arguments. Run without args for usage.")
