import requests

BASE_URL = "https://dummyjson.com"

def get_posts(limit=20):
    response = requests.get(f"{BASE_URL}/posts?limit={limit}")
    return response.json().get("posts", [])

def get_post(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    return response.json()

def get_post_comments(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
    return response.json().get("comments", [])

def get_users(limit=20):
    response = requests.get(f"{BASE_URL}/users?limit={limit}")
    return response.json().get("users", [])

def get_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    return response.json()

def get_user_posts(user_id):
    response = requests.get(f"{BASE_URL}/posts/user/{user_id}")
    return response.json().get("posts", [])

def get_stats():
    posts  = requests.get(f"{BASE_URL}/posts?limit=100").json()
    users  = requests.get(f"{BASE_URL}/users?limit=100").json()
    comms  = requests.get(f"{BASE_URL}/comments?limit=100").json()

    all_posts = posts.get("posts", [])
    total_likes    = sum(p.get("reactions", {}).get("likes", 0)    for p in all_posts)
    total_dislikes = sum(p.get("reactions", {}).get("dislikes", 0) for p in all_posts)

    top_posts = sorted(all_posts,
                       key=lambda p: p.get("reactions", {}).get("likes", 0),
                       reverse=True)[:5]

    tag_count = {}
    for p in all_posts:
        for tag in p.get("tags", []):
            tag_count[tag] = tag_count.get(tag, 0) + 1
    top_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_posts":    posts.get("total", 0),
        "total_users":    users.get("total", 0),
        "total_comments": comms.get("total", 0),
        "total_likes":    total_likes,
        "total_dislikes": total_dislikes,
        "top_posts":      top_posts,
        "top_tags":       top_tags,
        "engagement_rate": round(total_likes / max(len(all_posts), 1), 1),
    }