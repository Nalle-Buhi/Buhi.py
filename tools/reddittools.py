import asyncpraw
import random
from creds import REDDIT_ID, REDDIT_SECRET


r = asyncpraw.Reddit(
    client_id=REDDIT_ID,
    client_secret=REDDIT_SECRET,
    user_agent="Buh.py Discord Bot 0.1 by /u/Lerzyy",
)


async def get_random(subreddit, ctx):
    if isinstance(subreddit, list):
        subreddit = await r.subreddit(random.choice(subreddit))
    else:
        subreddit = await r.subreddit(subreddit)
    post = await subreddit.random()
    if ctx.channel.is_nsfw() == False and post.over_18:
        return post == None
    else:
        return post, subreddit
