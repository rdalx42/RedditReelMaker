
import requests
import time 
import os
import json
import random

class rrm_api:
    
    def __init__(self,req_limit,main_limit,subreddit="AskReddit"):
        self.headers = {"User-Agent": "Mozilla/5.0"} # mask browser
        self.request_limit=req_limit
        self.total_limit = main_limit

        self.subreddit = subreddit 
        self.ans = []

    def get_first_comment(self,post_id):
        
        url = f"https://www.reddit.com/r/{self.subreddit}/comments/{post_id}.json"
        response = requests.get(url, headers=self.headers)
        
        comments = response.json()[1]["data"]["children"]
        for comment in comments:
            if comment["kind"] == "t1":
                return comment["data"]["body"]
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
        with open("ans.json", "w", encoding="utf-8") as f:
            json.dump(self.ans, f, ensure_ascii=False, indent=4)

        self.ans=[] # empty list

    def get_post(self,word_count_min,word_count_max):

        # only get post comment when selecting the post itself

        with open("ans.json", "r", encoding="utf-8") as f:
            posts = json.load(f)

        selected_post = random.choice(posts)
        pid = selected_post["body"]["id"]
        pname = selected_post["body"]["title"]
        pcomment = self.get_first_comment(pid)

        if pcomment==None:
            return self.get_post(word_count_min,word_count_max)

        while len(pcomment.split())<word_count_min or len(pcomment.split())>word_count_max:
            return self.get_post(word_count_min,word_count_max)
        
        return [pid,pname,pcomment]
    

    def output(self):
        with open("ans.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=4, ensure_ascii=False))

        