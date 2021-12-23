from discord.ext import commands
from tools.embedtools import embed_builder


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    async def sano(self, ctx, *, args):
        await ctx.message.delete()
        await ctx.send(args)




def setup(bot):
    bot.add_cog(Misc(bot))