from discord.ext import commands, tasks
from tools.embedtools import embed_builder


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptimeCounter.start()

        self.tsec = 0
        self.tmin = 0
        self.thour = 0
        self.tday = 0
        

    @tasks.loop(seconds=2.0)
    async def uptimeCounter(self):
        self.tsec += 2
        if self.tsec == 60:
            self.tsec = 0
            self.tmin += 1
            if self.tmin == 60:
                self.tmin = 0
                self.thour += 1
                if self.thour == 24:
                    self.thour = 0
                    self.tday += 1
    
    @uptimeCounter.before_loop
    async def beforeUptimeCounter(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def uptime(self, ctx):
        fields = [["Päivät:", self.tday, True],["Tunnit:", self.thour, True], ["Minuutit:", self.tmin, True], ["Sekunnit:", self.tsec, True]]
        em = await embed_builder(ctx, "Botin uptime", "Kuinka pitkään botti on kestänyt hengissä paskomatta alleen", fields=fields)
        await ctx.send(embed=em)

    @commands.command()
    async def source(self, ctx):
        em = await embed_builder(ctx, "Buhi botin source koodi", "https://github.com/Lerzy/Buh.py", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/source_code.png")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Info(bot))