import os
import discord
import sqlite3
import bot_setup
from discord.ext import commands
from creds import TOKEN


bot = commands.Bot(command_prefix=["b ", "B "], case_insensitive=True)

item_list = [
    ["Tietokone setup", "Tietokoneella pääsee nettiin", 750, 0, 0, ""],
    ["Buhicoin", "Buhicoin, cryptovaluutta", 500, 1, 0, ""],
    ["Buhicoin miner", "Louhii Buhicoineja", 2000, 0, 0, ""],
]


@bot.event
async def on_ready():
    print(f"Logged in {bot.user}")
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game("b help")
    )


def setup():  # create tables and add items to them, then load all cogs
    print("\nSetup\n")
    bot_setup.create_tables()
    bot_setup.add_items(item_list)

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"loaded: {filename}")


if __name__ == "__main__":
    # setup all databases and login
    setup()
    bot.run(TOKEN)
