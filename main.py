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
# set 'logtime' to the current date/time
file = open(pathlib.Path("logs/%s.txt" % logtime), "w")
# open a file with that name then immediately close it, just to create it
file.close()
logging.basicConfig(filename=pathlib.Path("logs/%s.txt" % logtime),
                    level=logging.INFO,
                    format='%(levelname)s: %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')  # activates logging
# set logging settings


class DiscordClient(discord.Client): # create a new class from discord.py's Client
    def __init__(self): # when this class is initialised
        super().__init__(intents=discord.Intents.default()) # run discord.Client's __init__ 
                                                            # also, set the intents to default
        self.synced = False # set synced to False

    async def on_ready(self): # this code defines how it knows it's connected
        await self.wait_until_ready() # wait until the bot is connected to discord
        if not self.synced: # if not synced
            await tree.sync(guild=discord.Object(id=813656391310770198)) # force a sync to the test server
            self.synced = True # mark synced as True

        print(f'Logged in as {self.user} (ID: {self.user.id})') # output username & ID
        print('------')
        await self.change_presence(activity=discord.Game(name="the economy 😎")) # sets the status to Online
        await asyncio.sleep(config.TimeToCoin) # wait until it's time to create a coin



client = DiscordClient()
# initialises the client to the class that's just been created
tree = app_commands.CommandTree(client)
# initialises the Command Tree, which allows us to use Discord's native Slash Commands

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


# define a class, inherited from Discord's default view
# this will allow us to define buttons with specific behaviour
class HelpButtons(discord.ui.View):
    def __init__(self, page : int, helpfile : list):
        super().__init__() # run discord.ui.View's __init__() function
        self.page = page
        self.helpfile = helpfile
        # saves 'page' and 'helpfile' to the class itself. this allows them to be interacted with later
        
    @discord.ui.button(label = "⬅ Previous") # make a button with this label
    async def PreviousButton(self, interaction: discord.Interaction, button: discord.ui.button):
        self.page -= 1 # go back a page
        if self.page < 0: # if you're going below page 0...
            self.page = 0 # set page back to 0
            await interaction.response.send_message("You're at the start already...", ephemeral = True)
            # and pop up an error message (ephemeral means it's only visible to the user that clicked the button
        else:
            await interaction.message.edit(content=self.helpfile[self.page])
            # edit the message with the content of the current page
            await interaction.response.defer()
            # tell discord that we've read the message, so it doesn't come up with an error

    @discord.ui.button(label="Next ➡")
    async def NextButton(self, interaction: discord.Interaction, button: discord.ui.button):
        # using 'try' is required here, so that it dynamically changes as the list grows.
        try:
            self.page += 1 # go forward a page
            await interaction.message.edit(content=self.helpfile[self.page])
            # edit the message with the content of the current page
            await interaction.response.defer()
            # tell discord that we've read the message, so it doesn't come up with an error
            
        # if you go past the end of the list:
        except IndexError:
            await interaction.response.send_message("You can't go any further forward...", ephemeral = True)
            # pop up an error message that's only visible to the clicker of the button

@tree.command(name="help", description="Get help with all of your CowardCoin needs.",
              guild=discord.Object(id=813656391310770198))
# currently this command only works on my test version
async def help(interaction: discord.Interaction, option : str = ''):
    helppages = { # this dictionary holds all of the information in the 'help' command.
                  # to add a new command, define the name of it with the key
                  # (this can be used to find it later)
                  # and add the content of the page to the list.
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
    if not option: # if the user hasn't included the name of a page
        pages = list(helppages.values()) # show all pages 
        view = HelpButtons(0,pages) # add the buttons
        await interaction.response.send_message(pages[0], view = view) # send the message
    elif option.lower() in helppages.keys(): # otherwise if the user has put in a valid page name
        await interaction.response.send_message(helppages[option]) # send that page
    else: # otherwise
        await interaction.response.send_message("I don't recognise that command, sorry...", ephemeral = True)
        # come up with an error message only visible to the user


client.run(TOKEN)
