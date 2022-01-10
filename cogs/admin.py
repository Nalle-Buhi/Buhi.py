from discord.ext import commands
from tools.embedtools import embed_builder
import aiohttp
from io import BytesIO
import discord
import asyncio


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
                        em = await embed_builder(
                            ctx, "Emoji lisätty", e_name, image=e_url
                        )
                        await ctx.send(embed=em)
                except Exception as err:
                    print(err)
                    await ctx.send("Tiedosto liian iso tai botti on paska")


"""    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def slide(self, ctx, member: discord.Member, slide_length, slide_time):
        slide_category = await ctx.guild.create_category(f"{member.name} liukumäki")
        for i in range (0, int(slide_length)):
            await ctx.guild.create_voice_channel(f"{member.name} liukumäki {i}", category=slide_category)
        await ctx.send("liukumäki valmis:DDDDDdd")
        slide_active = False
        slideable = slide_category.voice_channels
        slide_active = True
        while slide_active == True:
            for c in slideable:
                await member.move_to(c)
                await asyncio.sleep(1)
"""


def setup(bot):
    bot.add_cog(Admin(bot))
