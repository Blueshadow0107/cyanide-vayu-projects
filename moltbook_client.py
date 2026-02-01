#!/usr/bin/env python3
"""
Moltbook Agent Registration & Posting
Vayu-2.0 Integration
"""

import requests
import json
import os

BASE_URL = "https://www.moltbook.com/api/v1"

def register_agent(name, description):
    """Register a new agent on Moltbook"""
    url = f"{BASE_URL}/agents/register"
    
    payload = {
        "name": name,
        "description": description
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Agent registered successfully!")
        print(f"API Key: {data['agent']['api_key']}")
        print(f"Claim URL: {data['agent']['claim_url']}")
        print(f"Verification Code: {data['agent']['verification_code']}")
        print("\n⚠️  SAVE THE API KEY - it won't be shown again!")
        
        return data['agent']['api_key']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def post_content(api_key, content, submolt="general", title=None):
    """Post content to Moltbook"""
    url = f"{BASE_URL}/posts"
    
    payload = {
        "submolt": submolt,
        "content": content
    }
    
    if title:
        payload["title"] = title
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        print("✅ Post created successfully!")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Post failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_my_profile(api_key):
    """Get current agent profile"""
    url = f"{BASE_URL}/agents/me"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get profile: {e}")
        return None

def get_feed(api_key, sort="hot", limit=25):
    """Get personalized feed"""
    url = f"{BASE_URL}/posts?sort={sort}&limit={limit}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get feed: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python moltbook_client.py register")
        print("  python moltbook_client.py post 'Your message here'")
        print("  python moltbook_client.py profile")
        print("  python moltbook_client.py feed")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "register":
        name = input("Agent name: ")
        description = input("Description: ")
        api_key = register_agent(name, description)
        
        if api_key:
            # Save to file
            with open("~/.openclaw/.env", "a") as f:
                f.write(f"\nMOLTBOOK_API_KEY={api_key}\n")
            print("\n💾 API key saved to ~/.openclaw/.env")
    
    elif command == "post":
        api_key = os.getenv("MOLTBOOK_API_KEY")
        if not api_key:
            print("❌ MOLTBOOK_API_KEY not set")
            sys.exit(1)
        
        content = sys.argv[2] if len(sys.argv) > 2 else input("Post content: ")
        post_content(api_key, content)
    
    elif command == "profile":
        api_key = os.getenv("MOLTBOOK_API_KEY")
        if not api_key:
            print("❌ MOLTBOOK_API_KEY not set")
            sys.exit(1)
        
        profile = get_my_profile(api_key)
        if profile:
            print(json.dumps(profile, indent=2))
    
    elif command == "feed":
        api_key = os.getenv("MOLTBOOK_API_KEY")
        if not api_key:
            print("❌ MOLTBOOK_API_KEY not set")
            sys.exit(1)
        
        feed = get_feed(api_key)
        if feed:
            print(json.dumps(feed, indent=2))
    
    else:
        print(f"Unknown command: {command}")
