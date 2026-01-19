import requests
import os
import json
from collections import defaultdict
from dotenv import load_dotenv

def get_facebook_likes_count(post_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{post_id}"

    params = {
        "fields": "reactions.summary(true)",
        "access_token": access_token
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("reactions", {}).get("summary", {}).get("total_count", 0)

def get_facebook_comments_count(post_id, access_token):
    url = f"https://graph.facebook.com/v24.0/{post_id}/comments"
    params = {
        "summary":"true",
        "limit":0,
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    print(response)
    response.raise_for_status()

    data = response.json()
    cnt=data.get("summary",{}).get("total_count",0)
    print(cnt)
    return cnt

def get_share_count(post_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{post_id}"
    params = {
        "fields": "shares",
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("shares", {}).get("count", 0)