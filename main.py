import discord
from discord import app_commands
import dotenv
import logging
import os
import time
import pathlib
import asyncio
import config

if not os.path.exists(pathlib.Path(time.strftime("logs/%Y.%m.%d/"))):
    os.makedirs(pathlib.Path(time.strftime("logs/%Y.%m.%d/")))
    # make a folder if it doesn't already exist with the name of today's date
logtime = time.strftime("%Y.%m.%d/%H.%M.%S")
file = open(pathlib.Path("logs/%s.txt" % logtime), "w")
file.close()
logging.basicConfig(filename=pathlib.Path("logs/%s.txt" % logtime),
                    level=logging.INFO,
                    format='%(levelname)s: %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')  # activates logging


class DiscordClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=813656391310770198))
            self.synced = True

        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await self.change_presence(activity=discord.Game(name="the economy 😎"))
        await asyncio.sleep(config.TimeToCoin)



client = DiscordClient()
tree = app_commands.CommandTree(client)

dotenv.load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")  # retrieve token from .env file
CHANNEL = os.getenv("COIN_CHANNEL")


class CoinButton(discord.ui.View):

    @discord.ui.button(label = "Get Coin")
    async def GetCoin(self, interaction : discord.Interaction, button : discord.ui.button):
        await interaction.response.send_message(f"Congratulations, {interaction.user.display_name}! You now have 6 Coins!")
        await interaction.message.delete()

@tree.command(name = "coingen",
              description= "Generate a coin. This command is only in place temporarily.",
              guild=discord.Object(id=813656391310770198))
async def coingen(interaction: discord.Interaction):
    with open(pathlib.Path(f"files/images/gold.gif"), "rb") as f:
        picture = discord.File(f)
    view = CoinButton()
    await interaction.response.send_message(content = "A new coin has appeared! Click the button below to claim it!", file=picture, view=view)


class HelpButtons(discord.ui.View):
    def __init__(self, page : int, helpfile : list):
        super().__init__()
        self.page = page
        self.helpfile = helpfile

    @discord.ui.button(label = "⬅ Previous")
    async def PreviousButton(self, interaction: discord.Interaction, button: discord.ui.button):
        self.page -= 1
        if self.page < 0:
            self.page = 0
            await interaction.response.send_message("You're at the start already...", ephemeral = True)
        else:
            await interaction.message.edit(content=self.helpfile[self.page])
            await interaction.response.defer()

    @discord.ui.button(label="Next ➡")
    async def NextButton(self, interaction: discord.Interaction, button: discord.ui.button):
        try:
            self.page += 1
            await interaction.message.edit(content=self.helpfile[self.page])
            await interaction.response.defer()
        except IndexError:
            await interaction.response.send_message("You can't go any further forward...", ephemeral = True)

@tree.command(name="help", description="Get help with all of your CowardCoin needs.",
              guild=discord.Object(id=813656391310770198))
async def help(interaction: discord.Interaction, option : str = ''):
    helppages = {
        "start": f'''
        ```diff
PAGE 1 - ID: 'start'
+ Welcome to CowardCoin 3.0!
This Help Page is split into Pages to help you get around - 
however, you can also type `/help [ID]` to get to the page of a specific command.
The ID for a command is usually the word you'd use to run this command - however,
the ID for each page is shown at the top.
I hope you enjoy reading my silly documentation :)```
''',
        "get": f"""
        ```diff
PAGE 2 - ID: 'get'
+ To get a coin, simply click the button below the image!
Alternatively, you can also type '/get' to claim a coin.```
""",
        "whoknows": """
```diff
PAGE 3 - ID: 'whoknows'
Documentation coming soon...```
"""
    }
    if not option:
        pages = list(helppages.values())
        view = HelpButtons(0,pages)
        await interaction.response.send_message(pages[0], view = view)
    elif option.lower() in helppages.keys():
        await interaction.response.send_message(helppages[option])
    else:
        await interaction.response.send_message("I don't recognise that command, sorry...", ephemeral = True)


client.run(TOKEN)
