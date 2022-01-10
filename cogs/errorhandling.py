from discord.ext import commands
from tools.embedtools import embed_builder


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(f"Nyt meni joku vituiks:\n `{error}`")
        print(error)


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
