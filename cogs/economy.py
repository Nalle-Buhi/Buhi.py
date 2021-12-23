from discord.ext import commands, tasks
from tools.embedtools import embed_builder
from tools import uitools
import sqlite3
import discord
import datetime
import random
from random import gauss
from math import sqrt, exp
from discord.commands import slash_command, Option


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.startmoney = 50 # money amount which will be given on bank account creation
        self.buhicoin_from_miner = 0.020
        self.buhicoin_gbm = None
        self.buhicoin_crash = None
        self.buhicoin_miner.start()
        self.buhicoin_price_change.start()


    async def aexec(self, ctx, code):
        # Make an async function with the code and `exec` it
        exec(
            f'async def __ex(self, ctx): ' +
            ''.join(f'\n {l}' for l in code.split('\n'))
        )

        # Get `__ex` from local variables, call it and return the result
        return await locals()['__ex'](self, ctx)

    # tasks

    @tasks.loop(seconds=25)
    async def buhicoin_price_change(self):
        if self.buhicoin_gbm == None:
            gbm = await self.create_GBM(500, 0.1, 0.05)
            self.buhicoin_gbm = gbm
            self.buhicoin_crash = random.randint(500, 1000)
        else:
            st = await self.buhicoin_gbm()
            if st >= self.buhicoin_crash:
                await self.buhicoin_price("update", 250)
                self.buhicoin_gbm = None
                print("crashed")
            else:
                await self.buhicoin_price("update", st)


    @tasks.loop(minutes=60)
    async def buhicoin_miner(self):
        results = await self.buhiminer_checker()
        # miner amount [2]
        # id [0]
        for i in results:
            await self.update_buhicoin_balance(i[0], self.buhicoin_from_miner * i[2])
            print(f"{i[0]} louhi: {self.buhicoin_from_miner * i[2]}")


    async def create_GBM(self, s0, mu, sigma):
        st = s0

        async def generate_value():
            nonlocal st

            st *= exp((mu - 0.5 * sigma ** 2) * (1. / 365.) + sigma * sqrt(1./365.) * gauss(mu=0, sigma=1))
            return st

        return generate_value


    # create tables for user balance data, also open account and inventory
    async def open_account(self, user_id):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute(f"SELECT balance FROM user_data WHERE user_id=?", (user_id, ))
        results = cur.fetchone()
        if results:
            return False
        else:
            cur.execute(f"INSERT INTO user_data VALUES (?, ?)", (user_id, self.startmoney))
            con.commit()
        con.close()

    # check user balance from database and return balance
    async def check_balance(self, user_id):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute(f"SELECT balance FROM user_data WHERE user_id=?", (user_id, ))
        balance = cur.fetchone()[0]
        if not balance is None:
            return balance
        else:
            return False

        con.close()


    # adds item to store database with new items
    async def add_store(self, item_name, item_desc, item_price, in_buhinet, usable, item_function = ""):
        store_data = await self.get_all_store()
        for i in store_data:
            if item_name in i:
                return False
                break

        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("INSERT INTO store_data VALUES (?, ?, ?, ?, ?, ?)", (item_name, item_desc, item_price, in_buhinet, usable, item_function))
        con.commit()
    
        con.close()

    # update store if item exists
    async def update_store(self, item_name, new_name, item_desc, item_price, in_buhinet, usable, item_function = ""):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT item_name FROM store_data WHERE item_name=?", (item_name, ))
        store_item = cur.fetchone()
        if store_item:
            cur.execute(""" UPDATE store_data
                            SET item_name=?, item_desc=?, item_price=?, in_buhinet=?, usable=?, item_function=?
                            WHERE item_name=?""", (new_name, item_desc, item_price, in_buhinet, usable, item_function, item_name))
            con.commit()
        else:
            return False

        con.close()

    # update user balance with change
    async def update_balance(self, user_id, change):
        await self.open_account(user_id)
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute(f"UPDATE user_data SET balance = balance + ? WHERE user_id=?", (change, user_id))
        con.commit()
        con.close()


    # update buhicoin balance in inventory, used when on miner
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


    # update inventory, used when buying or using items
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
    
    # remove items from store
    async def remove_store(self, item_name):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("DELETE FROM store_data WHERE item_name = ?", (item_name,))
        con.commit()
        con.close()


    async def get_all_store(self):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data")
        store_data = cur.fetchall()
        return store_data
        con.close()


    # gets all in store_data table and returns
    async def get_store(self):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data WHERE in_buhinet = ?", (0, ))
        store_data = cur.fetchall()
        return store_data
        con.close()


    # get all store items which are in "buhinet"
    async def get_buhinet_store(self):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data WHERE in_buhinet = ?", (1, ))
        store_data = cur.fetchall()
        return store_data
        con.close()


    # get specific item from store with item id and return it
    async def get_store_item(self, item_name):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM store_data WHERE item_name=?", (item_name, ))
        store_data = cur.fetchone()
        return store_data
        con.close()


    # returns all user items which can be used
    async def get_usable(self, user_id):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT I.item_name, s.item_name, I.amount, s.item_desc, s.item_function FROM inventory_data I, store_data s WHERE I.user_id = ? AND usable = ? AND I.item_name = s.item_name", (user_id, 1))
        return cur.fetchall()
        con.close()

    # returns all user items with store descriptions
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

    async def buhicoin_price(self, action, price = None):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        if action == "check":
            cur.execute(f"SELECT item_price FROM store_data WHERE item_name=?", ("Buhicoin", ))
            price = cur.fetchone()
        elif action == "update":
            cur.execute(f"UPDATE store_data SET item_price = ? WHERE item_name=?", (price, "Buhicoin"))
            con.commit()
        return price # only return price as int
        
    async def buhiminer_checker(self):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM inventory_data WHERE item_name=? AND amount > ?", ("Buhicoin miner", 0)) # get all rows which have miner and its value is over 1
        results = cur.fetchall()
        return results

    # bot commands

    @commands.command()
    async def tili(self, ctx):
        await self.open_account(ctx.author.id)
        balance = await self.check_balance(ctx.author.id)
        if balance < 101:
            image_url = "https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/ei_raha_apu.jpg"
        elif balance < 1000:
            image_url = "https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/massimies.jpg"
        elif balance < 2501:
            image_url = "https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/raha500stack.png"
        elif balance <= 10000:
            image_url = "https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/rahaasataa.jpg"
        elif balance > 1000:
            image_url = "https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/massikeisari.png"

        em = await embed_builder(ctx, title="Tilisi tiedot", description=f"Tililläsi on {balance:.2f}ඞ!", image=image_url)
        await ctx.send(embed=em)

    # buy item from store and update balances base on store prices
    async def buy_item(self, user_id, item_name, amount):
        if int(amount) < 0:
            return False
        user_balance = await self.check_balance(user_id)
        item = await self.get_store_item(item_name)
        if (item[2] * int(amount)) > user_balance:
            return False

        await self.update_balance(user_id, -(item[2] * int(amount)))
        await self.update_inventory(user_id, item_name, int(amount))


    async def buy_handler(self, ctx, item_name, amt):
        if int(amt) <= 0:
            await ctx.send("Skipattiin itemi")
        else:
            """view = uitools.Confirm(ctx)
            await ctx.send(f"Oletko varma että haluat ostaa {amt} kappaletta {item_name}", view=view)
            await view.wait()
            if view.value == True:"""
            buy_items = await self.buy_item(ctx.author.id, item_name, amt)
            if buy_items == False:
                await ctx.send("Transaction failed (Vitun köyhä)")
                return False
            else:
                return True
                """item = await self.get_store_item(item_name)
                await ctx.send(f"Ostit juuri {amt} kappaletta {item[1]}")"""


    @commands.command()
    async def kauppa(self, ctx):
        await self.open_account(ctx.author.id)
        store_data = await self.get_store()
        fields = []
        shop_list = []
        receipt = []
        for item in store_data:
            fields.append([f'{item[0]}\nHinta: {item[2]}ඞ', item[1], False]) # append items to list where index 0 = item_name, 1 = item_desc, 2 = item_price
            shop_list.append([f'{item[0]}: {item[2]}ඞ', item[1], item[0]]) # append items to list where index 0 = item_id, 1 = item_name, 2 = item_desc, 3 = item_price
        view = uitools.ShopView(ctx, "Valitse tavarat jotka haluat ostaa", 1, len(shop_list), shop_list, True, 60)
        em = await embed_builder(ctx, "Buhin kauppa", "valikoima saattaa vaihdella, ostaminen: select menun kautta", fields=fields, image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/buhit%C3%B6is.png")
        sent_em = await ctx.send(embed=em, view=view)
        await sent_em.edit(embed=em)
        await view.wait()
        results = view.values
        for i in view.values:
            item_data = await self.get_store_item(i)
            user_balance = await self.check_balance(ctx.author.id)
            price = item_data[2]
            em = await embed_builder(ctx, "Kuinka monta haluat ostaa", f"{i}: {price}ඞ", fields = [["Tililläsi on rahaa", f"{user_balance}ඞ", True]])
            await sent_em.edit(embed=em, view=None)
            amt = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
            receipt_checker = await self.buy_handler(ctx, i, str(amt.content))
            if receipt_checker == True:
                await amt.delete() # delete amount message to not spam channels
                total_price = (price * int(amt.content))
                receipt.append([f"{i}: {amt.content} Kpl", f"{total_price}ඞ", False])
                em = await embed_builder(ctx, "Kuitti", "Ostit juuri nämä buhin kaupasta", fields=receipt)
            else:
                pass
        await sent_em.edit(embed = em)

            

    @commands.command()
    async def inv(self, ctx):
        await self.open_account(ctx.author.id)
        inventory = await self.get_user_items(ctx.author.id)
        if inventory == False:
            await ctx.send("Sinulla ei ole tavaroita inventoryssa")
        else:
            fields = []
            print(await self.get_user_items(ctx.author.id))
            for item in await self.get_user_items(ctx.author.id):
                fields.append([f'Nimi: {item[0]}\nMäärä: {item[2]}', item[3], False])
            em = await embed_builder(ctx, "Sinun inventorysi", "on", fields=fields)
            await ctx.send(embed=em)


    @commands.command()
    async def käytä(self, ctx):
        user_items = []
        data = await self.get_usable(ctx.author.id)
        if data:
            for i in data:
                user_items.append([i[0], f"Sinulla on {i[2]}", None])
            view = uitools.SelectFromList(ctx, "Valitse tavarat", 1, 1, user_items, True, 60)
            em = await embed_builder(ctx, "Valitse tavara jotka haluat käyttää", "On")
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            item_name = "".join(view.values)
            em = await embed_builder(ctx, "Kuinka monta haluat käyttää", f"{user_items[0][1]} kappaletta {item_name}")
            await sent_em.edit(embed = em, view=None)
            msg = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
            amt = int(msg.content)
            if int(amt) > 5 or int(amt) <= 0:
                await ctx.send("Et voi käyttää yli viittä itemiä, tai amount on 0")
            else:
                user_item = await self.get_user_item(ctx.author.id, item_name)
                if user_item:
                    if user_item[2] >= int(amt):
                        item_from_shop = await self.get_store_item(item_name)
                        view = uitools.Confirm(ctx)
                        await ctx.send(f"Oletko varma että haluat käyttää {amt} kappaletta {item_name}", view=view)
                        await view.wait()
                        if view.value == True:
                            await self.update_inventory(ctx.author.id, item_name, -int(amt))
                            try:
                                if int(amt) > 1 and int(amt) <= 5:
                                    for i in range(int(amt)):
                                        await self.aexec(ctx, item_from_shop[5])
                                else:
                                    await self.aexec(ctx, item_from_shop[5])
                            except BaseException as err:
                                print(err)
                else:
                    await ctx.send("Virheellinen itemi")


    @commands.command()
    async def myy(self, ctx, item_name, amt):
        if int(amt) <= 0:
            await ctx.send("Et voi myydä 0 itemiä kehari")
        else:
            user_item = await self.get_user_item(ctx.author.id, item_name)
            if user_item:
                if user_item[2] >= int(amt):
                    item_from_shop = await self.get_store_item(item_name)
                    view = uitools.Confirm(ctx)
                    await ctx.send(f"Oletko varma että haluat käyttää {amt} kappalettä {item_from_shop[1]}", view=view)
                    await view.wait()
                    if view.value == True:
                        await self.update_inventory(ctx.author.id, item_name, -int(amt))
                        await self.update_balance(ctx.author.id, (int(amt) * item_from_shop[3] * 0.25))
                        await ctx.send(f"Myit juuri {item[1]}")


    @commands.command()
    async def top5(self, ctx):
        con = sqlite3.connect("economy.db")
        cur = con.cursor()
        cur.execute("SELECT balance, user_id FROM user_data ORDER BY balance DESC LIMIT 5")
        leaderboard = cur.fetchall()
        con.close()
        fields = []
        for place in range(1, len(leaderboard) + 1):
            user = leaderboard[place-1]
            member = await self.bot.fetch_user(user[1])
            fields.append([f'{place}: {member.name}', f"{user[0]}ඞ", False])
        em = await embed_builder(ctx, "Top 5 serverin rikkaimmat", " ", fields=fields, image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/avatar.png")
        await ctx.send(embed=em)


    @commands.command()
    async def buhicoin(self, ctx):
        user_items = await self.get_user_items(ctx.author.id)
        result = [item for item in user_items if "Tietokone setup" in item]
        if result:
            item_name = "Buhicoin"
            check = await self.buhicoin_price("check")
            price = check[0]
            view = uitools.ShopButtons(ctx)
            em = await embed_builder(ctx, "Buhicoin market:", f"Buhicoinin hinta on: {price}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/buh_coin_better.png")
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            if view.value == "buy":
                user_balance = await self.check_balance(ctx.author.id)
                em = await embed_builder(ctx, "Kuinka monta haluat ostaa", f"{item_name}: {price}ඞ", fields = [["Tililläsi on rahaa", f"{user_balance:.2f}ඞ", True]])
                await sent_em.edit(embed=em, view=None)
                amt = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
                amount = float(amt.content)
                total_price = (price * amount)
                if amount > 0 and user_balance >= total_price:
                    await amt.delete() # delete amount message to not spam channels
                    await self.update_inventory(ctx.author.id, item_name, amount)
                    await self.update_balance(ctx.author.id, -(amount * price))
                    em = await embed_builder(ctx, "Kuitti", "Ostit juuri buhkolikkeja", fields=[[f"{item_name}: {amt.content} Kpl", f"{total_price:.2f}ඞ", False]])
                else:
                    await ctx.send("Sinulla ei ole rahaa noihin")
                await sent_em.edit(embed = em)

            elif view.value == "sell":
                user_coins = await self.get_user_item(ctx.author.id, item_name)
                em = await embed_builder(ctx, "Kuinka monta haluat myydä", f"{item_name}: {price}ඞ", fields = [["Sinulla on ", f"{user_coins[2]:.2f} buhicoinia", True]])
                await sent_em.edit(embed=em, view=None)
                amt = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
                amount = float(amt.content)
                if amount <= 0:
                    await ctx.send("Et voi myydä 0 itemiä kehari")
                    await amt.delete() # delete amount message to not spam channels
                elif amount > 0 and user_coins[0] > amount:
                    await amt.delete() # delete amount message to not spam channels
                    await self.update_inventory(ctx.author.id, item_name, -amount)
                    await self.update_balance(ctx.author.id, (amount * price))
                    em = await embed_builder(ctx, "Kuitti", "Myit juuri buhkolikkeja", fields=[[f"{item_name}: {amt.content} Kpl", f"Sait {(price * amount):.2f}ඞ", False]])
                else:
                    await ctx.send("Sinulla ei ole noin paljon kolikkeja")
                await sent_em.edit(embed = em)
        else:
            await ctx.send("Tarvitset tietokoneen ostaaksesi ja myydäksesi buhicoineja")


# jobs and money earning

    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.command()
    async def kerjää(self, ctx):
        if self.kerjää.is_on_cooldown(ctx):
            await ctx.send("Nyt loppu kerjäys noin nopeasti")
        else:
            money_got = random.randint(0, 2)
            if random.randint(0, 100) == 100:
                lost_money = random.randint(60, 85)
                balance = await self.check_balance(ctx.author.id)
                lost_money = min(balance, lost_money)
                await self.update_balance(ctx.author.id, -lost_money) 
                await ctx.send(f"sinut ryöstettiin ja menetit {lost_money}ඞ")
            elif money_got == 0:
                await ctx.send("Et saanut mitään, myy vaikka persettäsi ensi kerralla")
            else:
                await self.update_balance(ctx.author.id, money_got)
                em = await embed_builder(ctx, "Kerjäsit rahaa", f"Ja sait rahaa {money_got}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/ei_raha_apu.jpg")
                await ctx.send(embed=em)

    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.command()
    async def pizza(self, ctx):
        if self.pizza.is_on_cooldown(ctx):
            await ctx.send("Ei tilauksia")
        else:
            building_emojis = ["🏕️","⛺","🏠","🏡","🏘️","🏚️","🛖","🏭","🏢","🏬","🏣","🏤","🏥","🏦","🏨","🏪","🏫","🏛️", "🏩", "📮"]
            delivery_address = random.choice(building_emojis)
            random.shuffle(building_emojis)
            view = uitools.EmojiView(ctx, building_emojis, 5)
            em = await embed_builder(ctx, "Vie pizza oikeaan osoitteeseen", f"Oikea osoite {delivery_address}")
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            print(view.value)
            if str(view.value) in delivery_address:
                earned = random.randint(10, 25)
                new_em = await embed_builder(ctx, "Toimitit pizzan onnistuneesti", f"Sait pizzan toimituksesta {earned}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/pizza_apu.jpg")
                await self.update_balance(ctx.author.id, earned)
            else:
                reimbursement = random.randint(20, 30)
                new_em = await embed_builder(ctx, "Vitun tunari et toimittanut pitsaa", f"Jouduit maksamaan korvauksia {reimbursement}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/suruviha_apu.jpg")
                await self.update_balance(ctx.author.id, -reimbursement)
            await sent_em.edit(embed=new_em, view=None)

    @commands.cooldown(2, 120, commands.BucketType.user)
    @commands.command()
    async def pizzeria(self, ctx):
        if self.pizzeria.is_on_cooldown(ctx):
            await ctx.send("Ei tilauksia")
        else:
            orderlist = []
            toppings = [["Kebab", "", None], 
                        ["Sipuli", "", None],
                        ["Aurajuusto", "", None],
                        ["Kinkku", "", None],
                        ["Salami", "", None],
                        ["Suolakurkku", "", None],
                        ["Tomaatti", "", None],
                        ["Oliivi", "", None],
                        ["Katkarapu", "", None],
                        ["Majoneesi", "", None],
                        ["Herkkusieni", "", None],
                        ["Ananas", "", None],
                        ["Amongus", "", None]]

            for i in toppings:
                orderlist.append(i[0])
            order = random.sample(orderlist, random.randint(3,4))
            view = uitools.SelectFromList(ctx, "Valitse pitsan täytteet oikein", 1, len(order), toppings, True,  10)
            em = await embed_builder(ctx, "Pizzatilaus, tee pizza asiakkaan tilauksen mukaan", f"Tilaus: {', '.join(order)}", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/buhi_pizzeria.png")
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            if view.values == None: # view.values is none on timeout error
                reimbursement = random.randint(5, 10)
                new_em = await embed_builder(ctx, "Et ehtinyt tekemään pizzaa", f"Maksoit asiakkaalle korvauksia myöhästyneestä pizzasta {reimbursement}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/suruviha_apu.jpg")
                await self.update_balance(ctx.author.id, -reimbursement)
            elif set(order) == set(view.values): #checks if order list and selected values are the same, selected order doesn't matter
                    earned = random.randint(15, 30)
                    new_em = await embed_builder(ctx, "Teit pizzan asiakkaan tilauksen mukaan!", f"Sait pizzan teosta {earned}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/pizza_apu.jpg")
                    await self.update_balance(ctx.author.id, earned)
            elif set(order) != set(view.values): #
                if random.randint(0, 50) == 0:
                    reimbursement = random.randint(50, 100)
                    new_em = await embed_builder(ctx, "Asiakas oli allerginen tekemällesi pitsalle ja melkein kuoli saatana", f"Maksoit sairaala kuluja {reimbursement}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/suruviha_apu.jpg")
                else:
                    reimbursement = random.randint(15, 30)
                    new_em = await embed_builder(ctx, "Teit väärän pizzan ja asiakas oli vihainen", f"Maksoit korvauksia {reimbursement}ඞ", image="https://raw.githubusercontent.com/Lerzy/Buh.py/main/images/suruviha_apu.jpg")
                await self.update_balance(ctx.author.id, -reimbursement)
            else:
                await ctx.send("Paskoin pitsaan")

            await sent_em.edit(embed=new_em, view=None)

    @commands.cooldown(2, 300, commands.BucketType.user)
    @commands.command()
    async def kassa(self, ctx):
        if self.kassa.is_on_cooldown(ctx):
            await ctx.send("Mitä koitat laskea ei täällä oo asiakkaita:DDD")
        else:
            em = await embed_builder(ctx, "Olet töissä kaupan kassalla, laske vaihtorahat", "Vastaukset kahden desimaalin tarkkuudella, paina confirm kun olet valmis")
            view = uitools.Confirm(ctx)
            sent_em = await ctx.send(embed=em, view=view)
            await view.wait()
            if view.value == True:
                item_prices = round(random.uniform(1, 1000), 2)
                given_change = round(random.uniform(item_prices, (item_prices + 100)), 2)
                em = await embed_builder(ctx, "Laske vaihtorahat", f"Tavaroiden arvo {item_prices}ඞ. Asiakas antoi {given_change}ඞ")
                await sent_em.edit(embed=em, view=None)
                message = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
                if float(message.content) == round(given_change - item_prices, 2):
                    earned = random.randint(20, 40)
                    await self.update_balance(ctx.author.id, earned)
                    em = await embed_builder(ctx, "Laskit vaihtorahat oikein", f"Buhi maksoi sinulle {earned}ඞ tuuraamisesta")
                else:
                    reimbursement = random.randint(15, 30)
                    await self.update_balance(ctx.author.id, -reimbursement)
                    em = await embed_builder(ctx, "Vitun tunari", f"Buhin kauppa menetti asiakkaan, sinä menetit {reimbursement}ඞ ja kaupanpäälle sait buhilta turpaan")
                await sent_em.edit(embed=em)
            else:
                await ctx.send("Vittu ei sit")

                
    # ultimate spaghetti coded with no sleep at 10 am
    # this mf has so many lines of codes because of custom emojis
    @commands.command()
    async def flip(self, ctx):
        balance = await self.check_balance(ctx.author.id)
        await ctx.send(f"paljonko haluat betata? sinulla on käytössä: {balance}ඞ, voittokerroin on 1.9x ja minimi panos on 10ඞ")
        message = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
        bet = float(message.content)
        if bet > balance or bet < 10:
            await ctx.send("Sinulla ei ole noin paljon rahaa, tai minimipanos liian pieni")
        else:
            emojis = [899778843148165191, 784516182639247360]
            flip = random.choice(emojis)
            print(flip)
            em = await embed_builder(ctx, "Kumman valitset?", "<:kassbuhi:899778843148165191>: Kassbuhi vai <:mulkkuankka:784516182639247360>: Mulkkuankka")
            choose = await ctx.send(embed=em)
            for emoji in emojis:
                await choose.add_reaction(self.bot.get_emoji(emoji))
            r, u  = await self.bot.wait_for("reaction_add", timeout=30, check=lambda r, u: r.emoji.id in emojis and u == ctx.author)
            if flip == r.emoji.id:
                await self.update_balance(ctx.author.id, (bet * 0.9))
                em = await embed_builder(ctx, "voitit", "onneksi onlkoo", image=self.bot.get_emoji(flip).url)
                await choose.edit(embed=em)
            else:
                await self.update_balance(ctx.author.id, -bet)
                em = await embed_builder(ctx, "hävisit pelin", "onneksi voit pelata uudellen", image=self.bot.get_emoji(flip).url)
                await choose.edit(embed=em)

    @commands.command()
    @commands.is_owner()
    async def add_item(self, ctx, *, args):

        """b add_item name(str) | desc(str) | price(int) | buhinet(0/1) | usable(0/1) | function(python code)"""

        item_name, item_desc, item_price, in_buhinet, usable, func = map(lambda x: x.strip(),args.split("|"))
        view = uitools.Confirm(ctx)
        await ctx.send(f"Lisätäänkö kauppaan: {item_name}, {item_desc}, {item_price}ඞ, buhinetissä?: {in_buhinet}, käytettävissä?: {usable} ```python\n{func}```?", view=view)
        await view.wait()
        if view.value == True:
            adder = await self.add_store(item_name, item_desc, item_price, in_buhinet, usable, func)
            if adder == False:
                await ctx.send("Kaupassa on jo kyseinen itemi, koita poistaa itemi tai päivittää sitä")
            else:
                await ctx.send(f"Kauppaan lisätty: {item_name}, {item_desc}, {item_price}ඞ, buhinetissä?: {in_buhinet}, käytettävissä?: {usable} ```python\n{func}```")


    @commands.command()
    @commands.is_owner()
    async def delete_item(self, ctx, *, item_name):
        view = uitools.Confirm(ctx)
        await ctx.send(f"oletko varma että haluat poistaa itemin id:llä {item_name}", view=view)
        await view.wait()
        if view.value == True:
            await self.remove_store(item_name)
            await ctx.send("Poistettu kaupasta")

    @commands.command()
    @commands.is_owner()
    async def update_item(self, ctx, *, args):

        """b update_item name(str) | new_name(str) | desc(str) | price(int) | buhinet(0/1) | usable(0/1) | function(python code)"""

        item_name, new_name, item_desc, item_price, in_buhinet, usable, func= map(lambda x: x.strip(),args.split("|"))
        view = uitools.Confirm(ctx)
        await ctx.send(f"Päivitetäänkö itemi?: {item_name}, {item_desc}, {item_price}ඞ, buhinetissä?: {in_buhinet}, käytettävissä?: {usable} ```python\n{func}```?", view=view)
        await view.wait()
        if view.value == True:
            updater = await self.update_store(item_name, new_name,item_desc, item_price, in_buhinet, usable, func)
            if updater == False:
                await ctx.send("itemiä ei olemassa")
            else:
                await ctx.send(f"Kauppa päivitetty: {item_name}, {item_desc}, {item_price}ඞ, buhinetissä?: {in_buhinet}, käytettävissä?: {usable} ```python\n{func}```")


def setup(bot):
    bot.add_cog(Economy(bot))