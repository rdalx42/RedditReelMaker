
import requests
import time
import json
import random

class Api:

    def __init__(self,req_limit,main_limit,subreddit="AskReddit",ans_path = "ans.json"):
        self.headers = {"User-Agent": "Mozilla/5.0"} # mask browser
        self.request_limit=req_limit
        self.total_limit = main_limit
        self.ans_path = ans_path

        self.subreddit = subreddit
        self.ans = []

    def get_first_comment(self, post_id):
        time.sleep(1)
        url = f"https://www.reddit.com/r/{self.subreddit}/comments/{post_id}.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
        except requests.RequestException as e:
            print(f"Request error for post {post_id}: {e}")
            return None

        if response.status_code != 200:
            print(f"Failed to fetch post {post_id}: Status code {response.status_code}")
            return None

        try:
            data = response.json()
        except ValueError:
            print(f"Failed to decode JSON for post {post_id}. Response: {response.text[:200]}")
            return None

        if len(data) < 2 or "data" not in data[1]:
            print(f"No comments found for post {post_id}")
            return None

        comments = data[1]["data"]["children"]
        for comment in comments:
            if comment.get("kind") == "t1":
                print(comment["data"].get("body"))
                return comment["data"].get("body")
        return None

    
    def get_posts(self):
        
        after = None

        while len(self.ans)<self.total_limit:

            remaining = self.total_limit-len(self.ans)
            limit = min(self.request_limit,remaining)

            url = f"https://www.reddit.com/r/{self.subreddit}/hot.json?limit={limit}"

            if after:
                url+=f"&after={after}"

            response=requests.get(url,headers=self.headers)
            if response.status_code!=200:
                print("Error: ",response.status_code)
                break

            data=response.json()
            kids = data["data"]["children"]
            if not kids:
                break


            for i, post in enumerate(kids):
                post_data = post["data"]

                self.ans.append({
                    "kind":"PostData",
                    "body": {
                        "id": post_data["id"],
                        "title": post_data["title"],
                        "nsfw": post_data["over_18"]
                    }
                })

            print(f"{len(self.ans)} / {self.total_limit}")
            after = data["data"]["after"]
            time.sleep(1)

        

    def save_ans(self):
        with open(self.ans_path, "w", encoding="utf-8") as f:
            json.dump(self.ans, f, ensure_ascii=False, indent=4)

        self.ans=[] # empty list

    def get_post(self, word_count_min, word_count_max,nsfw=False):
        print("getting post")
        with open(self.ans_path, "r", encoding="utf-8") as f:
            posts = json.load(f)

        if posts is None:
            print("ans.json doesnt exist")
            return None 

        attempts = 0
        max_attempts = 100  # avoid infinite loop

        while attempts < max_attempts:
            print("attempt #",attempts)
            selected_post = random.choice(posts)
            
            if selected_post["body"]["nsfw"]==True and nsfw==False:
                attempts+=1
                continue
            
            pid = selected_post["body"]["id"]
            pname = selected_post["body"]["title"]
            pcomment = self.get_first_comment(pid)

            if not pcomment:
                attempts += 1
                continue

            word_count = len(pcomment.split())
            print(word_count)
            if word_count_min <= word_count <= word_count_max:
                
                return [pname, pcomment]

            attempts += 1

        # fallback if no comment found
        print("Error; Couldn't find any comment")
        return None

    def output(self):
        with open(self.ans_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=4, ensure_ascii=False))
