import requests
import praw
import time
import os
from groq import Groq
import pandas as pd

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

reddit = praw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_SECRET"),
    user_agent=os.getenv("USER_AGENT"),
)

batches = 0
itr = 0
posts = reddit.subreddit("exmuslim").search(query="meme")

collections = {
    "image": [],
    "caption": []
}

for post in posts:
    if batches % 10 == 0 and batches != 0:
        print("Pause")
        df = pd.DataFrame.from_dict(collections)
        df.to_csv(f"chunk_{itr}.csv", index=False)
        itr += 1
        collections["image"].clear()
        collections["caption"].clear()
        time.sleep(10)

    print(post.title)
    print(post.selftext)
    if post.url.endswith(('.jpg', '.png', '.gif', 'jpeg')):
        print(post.url)
        image = requests.get(post.url)
        with open(f"./reddit_memes/{post.id}.jpg", "wb") as file:
            file.write(image.content)
            caption = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe how this meme represents Islam. Can it be considered offensive?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"{post.url}"
                                }
                            },
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": ""
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            content = caption.choices[0].message.content
            print(f"\033[31m{content}\033[0m")
        print("\033[32mImage Saved\033[0m")
        collections["image"].append(f"./reddit_memes/{post.id}.jpg")
        collections["caption"].append(content)
    print("========================")
    batches += 1
