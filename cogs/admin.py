from discord.ext import commands
from tools.embedtools import embed_builder
import aiohttp
from io import BytesIO

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis_and_stickers=True)
    async def es(self, ctx, e_url, e_name):
        async with aiohttp.ClientSession() as ses:
            async with ses.get(e_url) as resp:
                try:
                    value = BytesIO(await resp.read()).getvalue()
                    if resp.status in range(200, 299):
                        await ctx.guild.create_custom_emoji(image=value, name=e_name)
                        em = await embed_builder(ctx, "Emoji lisätty", e_name, image=e_url)
                        await ctx.send(embed=em)
                except Exception as err:
                    print(err)
                    await ctx.send("Tiedosto liian iso tai botti on paska")


def setup(bot):
    bot.add_cog(Admin(bot))