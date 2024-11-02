import requests
import praw
import time
import os
from groq import Groq
import pandas as pd
from PIL import Image
from io import BytesIO

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

reddit = praw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_SECRET"),
    user_agent=os.getenv("USER_AGENT"),
)

subreddits = [
    "exmuslim"
    # "IsraelPalestine",
    # "progressive_islam",
    # "AskMiddleEast",
    # "islam"
    # "Izlam"
]

batches = 0
itr = 0
base_limit = 500

collections = {
    "image": [],
    "caption": [],
    "label": []
}


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func()
        except Exception as e:
            print("Error", e)

    return wrapper


@exception_handler
def create_ds(starts: int = 0):
    for _subreddit in subreddits:
        print("Exploring", _subreddit)
        posts = reddit.subreddit(_subreddit).search(
            query="meme", limit=base_limit)

        for i, post in enumerate(posts):
            if i < starts:
                continue
            try:
                if post.url.endswith(('.jpeg', '.png', '.jpg')):
                    print("Post #", i)
                    print(post.title)
                    print(post.selftext)
                    print(post.url)

                    caption = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Describe this meme shortly in 1-2 sentences and how it represents Islam. Give the answer in plain text and not markdown. No paragraphs"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                                "url": f"{post.url}"
                                        }
                                    },
                                ]
                            }
                        ],
                        temperature=0,
                        max_tokens=512,
                    )
                    content = caption.choices[0].message.content
                    print(f"\033[31m{content}\033[0m")
                    label = int(
                        input("Enter the label hateful(1)/non-hateful(0): "))

                    if label == -1:
                        print("skipping")
                        continue
                    elif label == -2:
                        return

                    collections["image"].append(post.url)
                    collections["caption"].append(content)
                    collections["label"].append(label)
                    print(
                        "================================================================================================"
                    )
            except Exception as e:
                print(e)
                continue

        df = pd.DataFrame.from_dict(collections)
        df.to_csv(f"{_subreddit}.csv", index=False)
        collections["image"].clear()
        collections["caption"].clear()
        collections["label"].clear()


if __name__ == "__main__":
    create_ds(200)
