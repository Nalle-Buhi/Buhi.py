from discord.ext import commands
from tools.embedtools import embed_builder
from tools.reddittools import get_random

class Meems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cat_subreddits = ["standardissuecat", "cursedcats", "CursedCatImages", "cat", "cats"]
        self.meme_subreddits = ["memes", "dankmemes", "funny", "surrealmemes", "bonehurtingjuice", "nukedmemes", "MemeEconomy", "AmongUsMemes", "sus", "Memes_Of_The_Dank",
                                "meme", "okbuddyretard", "4PanelCringe", "dankchristianmemes", "comedyhomicide", "MinecraftMemes", "pcmemes", "thanksihateit"]


    @commands.command()
    async def kass(self, ctx):
        post, subreddit = await get_random(self.cat_subreddits, ctx)
        if post.url.startswith("https://v.redd.it/"):
            await ctx.send(post.url)
        else:
            em = await embed_builder(ctx, post.title, f"r/{subreddit}\n👍 {post.score}", image=post.url)
            await ctx.send(embed=em)

    @commands.command()
    async def meme(self, ctx):
        post, subreddit = await get_random(self.meme_subreddits, ctx)
        if post == None:
            await ctx.send("Mene nsfw kanavalle:D")
        if post.url.startswith("https://v.redd.it/"):
            await ctx.send(post.url)
        else:
            em = await embed_builder(ctx, post.title, f"r/{subreddit}\n👍 {post.score}", image=post.url)
            await ctx.send(embed=em)



def setup(bot):
    bot.add_cog(Meems(bot))