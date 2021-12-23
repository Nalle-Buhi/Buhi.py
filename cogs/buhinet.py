from discord.ext import commands
from tools.embedtools import embed_builder
from tools import uitools
import sqlite3
import discord
import datetime
import random

class Buhinet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # returns all items in user inventory with descriptons from store_data
    async def get_user_items(self, user_id):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT I.item_name, s.item_name, I.amount, s.item_desc, s.item_function FROM inventory_data I, store_data s WHERE I.user_id = ? AND I.item_name = s.item_name", (user_id, ))
        return cur.fetchall()
        con.close()


    async def get_user_item(self, user_id, item_name):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM inventory_data WHERE user_id=? AND item_name=?", (user_id, item_name))
        store_data = cur.fetchone()
        return store_data
        con.close()


    # update inventory, used when buiyng or using items
    async def update_inventory(self, user_id, item_name, change):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute(f"SELECT item_name FROM inventory_data WHERE user_id=? AND item_name=?", (user_id, item_name))
        inventory = cur.fetchone()
        if inventory == None:
            cur.execute("INSERT INTO inventory_data values (?, ?, ?)", (user_id, item_name, change))
            con.commit()
        else:
            cur.execute(f"UPDATE inventory_data SET amount = amount + ? WHERE user_id=? AND item_name=?", (change, user_id, item_name))
            con.commit()

        con.close()
    

    # update buhicoin balance in inventory, used when buiyng or using items
    async def update_buhicoin_balance(self, user_id, change):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute(f"SELECT item_name FROM inventory_data WHERE user_id=? AND item_name=?", (user_id, "Buhicoin"))
        inventory = cur.fetchone()
        if inventory == None:
            cur.execute("INSERT INTO inventory_data values (?, ?, ?)", (user_id, "Buhicoin", change))
            con.commit()
        else:
            cur.execute(f"UPDATE inventory_data SET amount = amount + ? WHERE user_id=? AND item_name=?", (change, user_id, "Buhicoin"))
            con.commit()

        con.close()

    async def get_buhicoin_balance(self, user_id):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM inventory_data WHERE user_id=? AND item_name=?", (user_id, "Buhicoin"))
        balance = cur.fetchone()
        if balance == None:
            return 0 # return 0 as balance. Otherwise it will throw errors when balance is 0
        else:
            return balance[2] # only return balance, others are not needed
        con.close()

    # get all store items which are in "buhinet"
    async def get_buhinet_store(self):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data WHERE in_buhinet = ?", (1, ))
        store_data = cur.fetchall()
        return store_data
        con.close()

    async def get_buhinet_item(self, item_name):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data WHERE in_buhinet = ? AND item_name=?", (1, item_name))
        store_data = cur.fetchone()
        return store_data
        con.close()

    @commands.command()
    async def buhinet(self, ctx):
        user_items = await self.get_user_items(ctx.author.id)
        result = [item for item in user_items if "Tietokone setup" in item]
        if result:
            view = uitools.ShopButtons(ctx)
            em = await embed_builder(ctx, "Tervetuloa buhinettiin", "buhinet on buhi botissa oleva peittoverkko, jota voidaan käyttää vain tietyllä ohjelmistolla, kokoonpanoilla tai valtuutuksilla ja joka käyttää usein ainutlaatuista mukautettua viestintäprotokollaa", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/buhnet.png")
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            if view.value == "buy":
                store_data = await self.get_buhinet_store()
                fields = []
                shop_list = []
                receipt = []
                for item in store_data:
                    fields.append([f'{item[0]}\nHinta: {item[2]}ඞ', item[1], False]) # append items to list where index 0 = item_name, 1 = item_desc, 2 = item_price
                for item in store_data:
                    shop_list.append([f'{item[0]}: {item[2]}ඞ', item[1], item[0]]) # append items to list where index 0 = item_id, 1 = item_name, 2 = item_desc, 3 = item_price
                view = uitools.ShopView(ctx, "Valitse tavarat jotka haluat ostaa", 1, len(shop_list), shop_list, True, 60)
                await sent_em.edit(embed=em, view=view)
                await view.wait()
                for i in view.values:
                    user_balance = await self.get_buhicoin_balance(ctx.author.id)
                    item_data = await self.get_buhinet_item(i)
                    price = item_data[2]
                    em = await embed_builder(ctx, "Kuinka monta haluat ostaa", f"{i}: {price}ඞ", fields = [["Sinulla on buhicoineja", f"{user_balance} BC", True]])
                    await sent_em.edit(embed=em, view=None)
                    amt = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
                    print((int(amt.content) * price))
                    if (int(amt.content) * price) <= user_balance:
                        await amt.delete() # delete amount message to not spam channels
                        await self.update_buhicoin_balance(ctx.author.id, -(int(amt.content) * price))
                        await self.update_inventory(ctx.author.id, i, int(amt.content))
                        total_price = (price * int(amt.content))
                        receipt.append([f"{i}: {amt.content} Kpl", f"{total_price}ඞ", False])
                        em = await embed_builder(ctx, "Buhinet ostokset tehty", "Ostit juuri nämä", fields=receipt)
                    else:
                        await ctx.send(f"Sinulla ei ole tarpeeksi buhicoineja ostaa {i}")
                await sent_em.edit(embed = em)
            """view = uitools.ShopButtons(ctx)
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            if view.value == "buy":
                store_data = await self.get_buhinet_store()
                shop_list = []
                for item in store_data:
                    shop_list.append([f'{item[0]}: {item[2]} BC', item[1], item[0]]) # append items to list where index 0 = item_id, 1 = item_name, 2 = item_desc, 3 = item_price
                view = uitools.ShopView(ctx, "Valitse tavarat jotka haluat ostaa", 1, len(shop_list), shop_list, True, 60)
                await sent_em.edit(embed=em, view=view)
                await view.wait()
                for i in view.values:
                    item_data = await self.get_buhinet_item(i)
                    price = item_data[2]
                    await sent_em.edit(f"Kuinka monta kappaletta haluat ostaa {i}, yhden hinta {price} BC", embed=None, view=None)
                    amt = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
                    print((int(amt.content) * price))
                    if (int(amt.content) * price) <= await self.get_buhicoin_balance(ctx.author.id):
                        await self.update_buhicoin_balance(ctx.author.id, -(int(amt.content) * price))
                        await self.update_inventory(ctx.author.id, i, int(amt.content))
                    else:
                        await ctx.send(f"Sinulla ei ole tarpeeksi buhicoineja ostaa {i}")
        else:
            await ctx.send("Sinulla ei ole tietokonetta")"""

def setup(bot):
    bot.add_cog(Buhinet(bot))