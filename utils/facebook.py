import requests
import os
import json
from collections import defaultdict
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()

GRAPH_VERSION = "v19.0"
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN")

if not PAGE_ACCESS_TOKEN:
    raise Exception("FB_PAGE_TOKEN not found")

# ================= CORE HELPER =================
def graph_get(endpoint, params=None):
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{endpoint}"
    params = params or {}
    params["access_token"] = PAGE_ACCESS_TOKEN

    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

# ================= BASIC FETCHERS =================
def get_page_info():
    return graph_get("me")

def get_posts(page_id, limit=1):
    return graph_get(
        f"{page_id}/feed",
        {"limit": limit, "fields": "id,message,created_time"}
    ).get("data", [])

# ================= LIKES =================
def get_likes(post_id):
    visible = []

    data = graph_get(
        f"{post_id}/likes",
        {"limit": 100, "summary": "true"}
    )

    visible.extend(data.get("data", []))
    total = data.get("summary", {}).get("total_count", 0)

    next_url = data.get("paging", {}).get("next")
    while next_url:
        r = requests.get(next_url)
        r.raise_for_status()
        data = r.json()
        visible.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")

    return visible, total

def run_like_analytics():
    page = get_page_info()
    print(f"\nPage: {page['name']}\n")

    posts = get_posts(page["id"], limit=1)
    liker_counts = defaultdict(int)

    for post in posts:
        print("Post:", post.get("message", "Photo / Video"))

        visible, total = get_likes(post["id"])
        print(f"Total likes: {total}")
        print(f"Visible likers: {len(visible)}")

        for u in visible:
            liker_counts[u.get("name", "Anonymous / Restricted User")] += 1

        hidden = total - len(visible)
        if hidden > 0:
            liker_counts["Anonymous / Restricted Users"] += hidden

    print("\n" + "=" * 50)
    print("LIKE ANALYTICS")
    print("=" * 50)

    for i, (name, count) in enumerate(
        sorted(liker_counts.items(), key=lambda x: x[1], reverse=True), 1
    ):
        print(f"#{i:<3} {name} — {count} like(s)")

# ================= COMMENTS =================
def get_top_level_comments(post_id):
    comments = []

    data = graph_get(
        f"{post_id}/comments",
        {"limit": 100, "fields": "id,from{name,id},message,created_time"}
    )

    comments.extend(data.get("data", []))

    next_url = data.get("paging", {}).get("next")
    while next_url:
        r = requests.get(next_url)
        r.raise_for_status()
        data = r.json()
        comments.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")

    return comments

def get_replies(comment_id):
    replies = []

    data = graph_get(
        f"{comment_id}/comments",
        {"limit": 100, "fields": "from{name,id},message,created_time"}
    )

    replies.extend(data.get("data", []))

    next_url = data.get("paging", {}).get("next")
    while next_url:
        r = requests.get(next_url)
        r.raise_for_status()
        data = r.json()
        replies.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")

    return replies

def run_comment_analytics(debug=False):
    page = get_page_info()
    print(f"\nPage: {page['name']}\n")

    posts = get_posts(page["id"], limit=1)
    user_comments = defaultdict(int)

    for post in posts:
        print("Post:", post.get("message", "Photo / Video"))

        comments = get_top_level_comments(post["id"])
        print(f"Top-level comments: {len(comments)}")

        if debug:
            print(json.dumps(comments, indent=2))

        for c in comments:
            name = c.get("from", {}).get("name", "Anonymous / Restricted User")
            user_comments[name] += 1

            for r in get_replies(c["id"]):
                r_name = r.get("from", {}).get("name", "Anonymous / Restricted User")
                user_comments[r_name] += 1

    print("\n" + "=" * 50)
    print("COMMENT ANALYTICS")
    print("=" * 50)

    for i, (name, count) in enumerate(
        sorted(user_comments.items(), key=lambda x: x[1], reverse=True), 1
    ):
        print(f"#{i:<3} {name} — {count} comment(s)")

# ================= POST-WISE COMMENTS =================
def fetch_post_wise_comments():
    page = get_page_info()
    posts = get_posts(page["id"], limit=3)

    for post in posts:
        print("\n" + "=" * 60)
        print("POST:", post.get("message", "Photo / Video"))
        print("=" * 60)

        comments = get_top_level_comments(post["id"])
        for i, c in enumerate(comments, 1):
            print(f"\nComment {i}")
            print("Author:", c.get("from", {}).get("name", "Anonymous / Restricted User"))
            print("Text  :", c.get("message"))

            for j, r in enumerate(get_replies(c["id"]), 1):
                print(f"  ↳ Reply {j}")
                print("    Author:", r.get("from", {}).get("name", "Anonymous / Restricted User"))
                print("    Text  :", r.get("message"))

# ================= ENTRY POINT =================
if __name__ == "__main__":
    run_comment_analytics()
    run_like_analytics()
    fetch_post_wise_comments()
