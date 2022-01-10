import discord
from discord.ext import commands
from tools.embedtools import embed_builder

# Simple confirm button


class Confirm(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.ctx.author == interaction.user:
            embed = discord.Embed(title="Hyväksytty!", color=0x00FF00)
            await interaction.message.edit("", embed=embed, view=None)
            self.value = True
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            embed = discord.Embed(title="Peruutettu.", color=0xFF0000)
            await interaction.message.edit("", embed=embed, view=None)
            self.value = False
            self.stop()


# creates emoji buttons from a list of emojis and assigns selected value as self.value.
class EmojiView(discord.ui.View):
    def __init__(self, ctx, emoji_list, timeout):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.emoji_list = emoji_list
        self.value = None
        self.buttonbuilder()

    def buttonbuilder(self):
        for emoji in self.emoji_list:
            self.add_item(EmojiButton(emoji=emoji, style=discord.ButtonStyle.primary))


class EmojiButton(discord.ui.Button):
    async def callback(self, interaction):
        if self.view.ctx.author == interaction.user:
            self.view.value = self.emoji
            self.view.stop()


class ShopView(discord.ui.View):
    def __init__(
        self,
        ctx,
        placeholder,
        min_values,
        max_values,
        builder_list,
        stop_on_select,
        timeout,
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.builder_list = builder_list
        self.stop_on_select = stop_on_select
        self.selectbuilder()
        self.values = None

    def selectbuilder(self):
        options = []
        for builder in self.builder_list:
            name, desc, value = builder
            options.append(
                discord.SelectOption(label=name, description=desc, value=value)
            )
        dropmenu = SelectDrop(
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            options=options,
        )
        self.add_item(dropmenu)


# creates select menu from a list and assigns selected value as self.value. Mostly used for jobs
class SelectFromList(discord.ui.View):
    def __init__(
        self,
        ctx,
        placeholder,
        min_values,
        max_values,
        builder_list,
        stop_on_select,
        timeout,
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.builder_list = builder_list
        self.stop_on_select = stop_on_select
        self.selectbuilder()
        self.values = None

    def selectbuilder(self):
        options = []
        for builder in self.builder_list:
            name, desc, emoji = builder
            if emoji == None:
                options.append(
                    discord.SelectOption(label=name, description=desc, value=name)
                )  # if there is no emoji dont add it
            else:
                options.append(
                    discord.SelectOption(
                        label=name, description=desc, emoji=emoji, value=name
                    )
                )
        dropmenu = SelectDrop(
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            options=options,
        )
        self.add_item(dropmenu)


class SelectDrop(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction):
        if self.view.ctx.author == interaction.user:
            self.view.values = self.values
            if self.view.stop_on_select == True:
                self.view.stop()


class ShopButtons(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.value = None

    @discord.ui.button(label="Osta", style=discord.ButtonStyle.green)
    async def buy(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            """embed = discord.Embed(title="Selvä", color=0x00FF00)
            await interaction.message.edit("", embed=embed, view=None)"""
            self.value = "buy"
            self.stop()

    @discord.ui.button(label="Myy", style=discord.ButtonStyle.blurple)
    async def sell(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            """embed = discord.Embed(title="Selvä", color=0x00FF00)
            await interaction.message.edit("", embed=embed, view=None)"""
            self.value = "sell"
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            embed = discord.Embed(title="Peruutettu", color=0x00FF00)
            await interaction.message.edit("", embed=embed, view=None)
            self.value = False
            self.stop()
