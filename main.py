import discord
from discord import app_commands
from discord.ext import tasks
import dotenv
import logging
import os
import pathlib
import asyncio
import config
from config import userlist
import random
import time
import math

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

class coin:

    def __init__(self):

        coinrarities = [
            ["undefined", "[error]", "error", 0, [0,0]],
            ["bronze", "<a:bronzecoin:844545666201288755>", "bronze", 50, [1,5]],
            ["silver", "<a:silvercoin:844545665911881788>", "silver", 80, [5,10]],
            ["gold", "<a:goldcoin:813889535699189871>", "gold", 99, [10,20]],
            ["SUPER RARE red", "<a:redcoin:844545670709772290>", "ultrarare", 100, [20,50]],
        ]
           
        # Sets default coin rarities
        # FORMAT:
        # type[0] = name
        # type[1] = emote
        # type[2] = filename
        # type[3] = if rarity >= type[3]= this is chosen
        # type[4] = value calculator

        rarity = random.randint(1,100) # randomly generate style points
        for item in coinrarities: # go through each type of coins
            if rarity <= item[3]: # if it is this current coin rarity:
                type = item # save it, break the loop
                break
        else:
            raise ValueError(f"Invalid Coin Rarity - {rarity}") # else return an error
        
        self.name = type[0] # save name from dict
        self.emote = type[1] # save emote
        self.filename = type[2] # save filename
        self.value = random.randint(type[4][0],type[4][1]) # calculate cost



class DiscordClient(discord.Client):  # create a new class from discord.py's Client

    def __init__(self):  # when this class is initialised
        super().__init__(intents=discord.Intents.all())  # run discord.Client's __init__
        # also, set the intents to default
        self.synced = False  # set synced to False
        self.coinactive = False

    async def setup_hook(self) -> None:
        self.coin_creation_task.start()

    async def on_ready(self):  # this code defines how it knows it's connected
        await self.wait_until_ready()  # wait until the bot is connected to discord
        if not self.synced:  # if not synced
            await tree.sync(guild=discord.Object(id=813656391310770198))  # force a sync to the test server
            self.synced = True  # mark synced as True

        dotenv.load_dotenv(".env")
        channelID = os.getenv("COIN_CHANNEL")
        self.coinchannel = self.get_channel(int(channelID))
        print(f'Logged in as {self.user} (ID: {self.user.id})')  # output username & ID
        print('------')
        await self.change_presence(activity=discord.Game(name="the economy 😎"))  # sets the status to Online
        userlist.loadstate(client)

    @tasks.loop(seconds=10)
    async def coin_creation_task(self):
        if self.coinactive:
            print("Coin is currently active - counting down")
            await asyncio.sleep(config.coinexpiry)
            if self.coinactive:
                try:
                    await self.sentmsg.delete()
                    expirymsg = await interaction.response.send_message("The coin expired...")
                    await asyncio.sleep(config.coinexpiry)
                    await expirymsg.delete()
                except:
                    pass
                self.coinactive = False
        elif self.synced:
            timetowait = random.randint(config.TimeToCoin[0], config.TimeToCoin[1])  # decide how long to wait
            print(f"Coin will appear in {timetowait} seconds")
            await asyncio.sleep(timetowait)

            # The coin is created
            self.coin = coin()
            current = self.coin
            print(f"{current.name} coin generated")
            with open(pathlib.Path(f"files/images/{current.filename}.gif"), "rb") as f:
                # noinspection PyTypeChecker
                picture = discord.File(f)
            view = CoinButton()
            self.sentmsg = await self.coinchannel.send(
                content=f"{current.emote} A new {current.name} coin has appeared! Click the button below to claim it!",
                file=picture, view=view)
            self.coinactive = True

    @coin_creation_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


client = DiscordClient()
# initialises the client to the class that's just been created
tree = app_commands.CommandTree(client)
# initialises the Command Tree, which allows us to use Discord's native Slash Commands

global CHANNEL
dotenv.load_dotenv(".env")
TOKEN: str = os.getenv("DISCORD_TOKEN")  # retrieve token from .env file


class CoinButton(discord.ui.View):

    @discord.ui.button(label="Get Coin")
    async def getcoin(self, interaction: discord.Interaction, button: discord.ui.button):
        current = client.coin
        user = userlist.find(interaction.user.id)
        user.coins += current.value
        userlist.savestate()
        s = "s" if user.coins != 1 else ""
        await interaction.response.send_message(
            f"""
{current.emote} Congratulations, {interaction.user.display_name}! You gained {current.value} CowardCoins!
You now have {user.coins} coin{s}."""
        )
        client.coinactive = False
        await interaction.message.delete()

# ============================================================================================
# ================================ GIVE COMMAND ==============================================
# ============================================================================================
@tree.command(name="give", description="Give coins to your friends!",
              guild=discord.Object(id=813656391310770198))
async def give(interaction: discord.Interaction, recipient: discord.User, count: int):
    if count <= 0:
        await interaction.response.send_message(content="That's not how coins work...", ephemeral=True)
    else:
        sender = userlist.find(interaction.user.id)
        localrecipient = userlist.find(recipient.id)
        if sender == localrecipient:
            currenttime = time.time()
            timediff = currenttime-sender.lasttrick
            if timediff < config.timebetweentricks:
                timeleft = round(config.timebetweentricks-timediff)
                output = ""
                hours = math.floor(timeleft / 3600)
                if hours > 0:
                    plural = ""
                    timeleft -= (hours * 3600)
                    if hours != 1:
                        plural = "s"
                    output += str(hours) + " hour" + plural + ", "
                minutes = math.floor(timeleft / 60)
                if minutes > 0:
                    timeleft -= (minutes * 60)
                    plural = ""
                    if minutes != 1:
                        plural = "s"
                    output += str(minutes) + " minute" + plural + ", "
                if hours > 0 or minutes > 0:
                    output += "and "
                plural = ""
                if timeleft != 1:
                    plural = "s"
                output += str(timeleft) + " second" + plural
                await interaction.response.send_message("You're too tired after your last trick! Give it another try in " + output + " 😎")
            else:
                if sender.coins >= count:

                    style = random.randint(1, 100)
                    print(str(style))
                    tricks = [
    f"You juggle {count} coins while grinding on a rail!",
    f"You balance {count} coins on your head while doing a kickflip!",
    f"You jump in the air, throw your skateboard at a wall, bounce it off the wall and land back on it, with {count} coins in your mouth!"
                    ]
                    output = random.choice(tricks)
                    if style <= 25:
                        amountlost = math.ceil(count / 3)
                        if amountlost == 1:
                            plural = ""
                        else:
                            plural = "s"
                        output += f"\nBut... oh no! You get distracted, and send {amountlost}coin{plural} flying!\n"
                        sender.coins-=amountlost
                    elif style > 25 and style < 90:
                        output += "\nIt's cool as hell, and everyone is applauding.\n"
                    else:
                        output += "\nBut... what's this? You kick off the wall and do a full somersault before landing " \
                                  "back on your skateboard and catching all of the coins in your hand, and... there's " \
                                  f"twice as many in there than there were before?\nYou gained {count} coins!\n"
                    sender.coins += count
                    sender.style += style
                    output += f"You gain {style} Style Points™!\nYou now have {sender.style} " \
                              f"Style Points™."

                    await interaction.response.send_message(output)
                    sender.lasttrick = time.time()

                else:
                    await interaction.response.send_message("You can't afford to do *that* cool a trick!",ephemeral=True)

        elif sender.coins >= count:
            sender.coins -= count
            localrecipient.coins += count
            userlist.savestate()
            s = "s" if count != 1 else ""
            await interaction.response.send_message(f"""
{interaction.user.mention} sends {count} coin{s} to {recipient.mention}!
{interaction.user.display_name} now has {sender.coins} coins.
{recipient.display_name} now has {localrecipient.coins} coins.
""")
        else:
            await interaction.response.send_message("You can't afford that...",ephemeral=True)

    userlist.savestate()

# ============================================================================================
# ============================= LEADERBOARD COMMAND ==========================================
# ============================================================================================
@tree.command(name="leaderboard",description="See the highest ranked Collectors in the server!",
              guild=discord.Object(id=813656391310770198))
async def leaderboard(interaction:discord.Interaction, option: str = None):
    if not option:
        option = "temp"
    if option.lower() == "style":
        sorted_list = sorted(userlist, key=lambda x: x.style, reverse=True)
    else:
        sorted_list = sorted(userlist, key=lambda x: x.coins, reverse=True)

    if option.lower() == "full":
        max = len(sorted_list)
    else:
        max = 5
    leaderboard = []
    for x in range(0,max):
        if option.lower() == "style":
            if sorted_list[x].style != 0:
                leaderboard.append(sorted_list[x])
        else:
            if sorted_list[x].coins != 0:
                leaderboard.append(sorted_list[x])

    if len(leaderboard) == 0:
        await interaction.response.send_message("The leaderboard is empty, sorry...",ephemeral=True)
    else:
        counter = 0
        if option.lower() == "style":
            temp = "Style "
        else:
            temp = ""
        output = f"<a:gold:1038495846074941440> ***{temp}Leaderboard*** <a:gold:1038495846074941440>\n"

        for item in leaderboard:
            counter += 1
            if option.lower() == "style":
                output += f"{counter}. **{client.get_user(item.id).display_name}** - {item.style}\n"
            else:
                output += f"{counter}. **{client.get_user(item.id).display_name}** - {item.coins}\n"

        await interaction.response.send_message(output)


# ============================================================================================
# =============================== COUNT COMMAND ==============================================
# ============================================================================================
@tree.command(name="count", description="Find out how many coins you have!",
              guild=discord.Object(id=813656391310770198))
# currently this command only works on my test version
async def count(interaction: discord.Interaction, collector: discord.User = None):
    if collector:
        localuser = userlist.find(collector.id)
        discorduser = collector
    else:
        localuser = userlist.find(interaction.user.id)
        discorduser = interaction.user
    s = "s" if localuser.coins != 1 else ""
    output = f"{discorduser.display_name} has {localuser.coins} coin{s}."
    print(localuser.style)
    if localuser.style:
        output += f"\nThey also have {localuser.style} StylePoints™!"
    await interaction.response.send_message(output)


# ============================================================================================
# =============================== HELP COMMAND ===============================================
# ============================================================================================

# define a class, inherited from Discord's default view
# this will allow us to define buttons with specific behaviour
class HelpButtons(discord.ui.View):
    def __init__(self, page: int, helpfile: list):
        super().__init__()  # run discord.ui.View's __init__() function
        self.page = page
        self.helpfile = helpfile
        # saves 'page' and 'helpfile' to the class itself. this allows them to be interacted with later

    @discord.ui.button(label="⬅ Previous")  # make a button with this label
    async def PreviousButton(self, interaction: discord.Interaction, button: discord.ui.button):
        self.page -= 1  # go back a page
        if self.page < 0:  # if you're going below page 0...
            self.page = 0  # set page back to 0
            await interaction.response.send_message("You're at the start already...", ephemeral=True)
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
            self.page += 1  # go forward a page
            await interaction.message.edit(content=self.helpfile[self.page])
            # edit the message with the content of the current page
            await interaction.response.defer()
            # tell discord that we've read the message, so it doesn't come up with an error

        # if you go past the end of the list:
        except IndexError:
            await interaction.response.send_message("You can't go any further forward...", ephemeral=True)
            # pop up an error message that's only visible to the clicker of the button


@tree.command(name="help", description="Get help with all of your CowardCoin needs.",
              guild=discord.Object(id=813656391310770198))
# currently this command only works on my test version
async def help(interaction: discord.Interaction, option: str = ''):
    helppages = {  # this dictionary holds all of the information in the 'help' command.
        # to add a new command, define the name of it with the key
        # (this can be used to find it later)
        # and add the content of the page to the list.
        "start": f'''
        ```diff
PAGE 1 - ID: 'start'
+ Welcome to CowardCoin 3.0!
This Help Page is split into Pages to help you get around - 
however, you can also type '/help [ID]' to get to the page of a specific command.
The ID for a command is usually the word you'd use to run this command - however,
the ID for each page is shown at the top.
I hope you enjoy reading my silly documentation :)```
''',
        "get": f"""
        ```diff
PAGE 2 - ID: 'get'
+ To get a coin, simply click the button below the image!
Any coins you collect will be stored forever in your Coin Pocket.
```
""",
        "count": """
```diff
PAGE 3 - ID: 'count'
+ Type '/count' to see how many coins/StylePoints™ you have.
Additionally, you can type in anyone's name after the command, to see how many coins they have!```
""",
        "rarities": """
```diff
PAGE 4 - ID: 'rarities'
+ Whenever a coin is created, it will be one of 4 types.
1. Bronze - worth 1-5 coins
2. Silver - worth 5-10 coins
3. Gold - worth 10-20 coins
4. Red - worth ????? coins
The more coins a variant is worth, the rarer it is.```
""",
        "leaderboard": """
```diff
PAGE 5 - ID: 'leaderboard'
+ You can type '/leaderboard' to see the Top 5 Collectors in the server.
Additionally, you can add a modifier - 'full' will show all collectors in the server, 
and 'style' will show StylePoints instead of Coins.```
""",
        "give": """
```diff
PAGE 6 - ID: 'give'
+ You can type '/give' to give coins to anyone in the server.
Fill in the 'recipient' space with whoever you'd like to give coins to,
and the 'count' space with how many coins you'd like to give.
If you give yourself coins, then...```
""",
        "style": f"""
```diff
PAGE 7 - ID: 'style'
+ If you '/give' yourself any amount of coins, you will do a Coin Trick!
You can do one coin trick every ~{math.ceil(config.timebetweentricks/3600)} hours (by default).
This will give you a random number of StylePoints™, between 1 and 100.
If you score fewer than 15 StylePoints, you will lose 1/3 of the coins you put into the Trick -
however, if you score more than 90, you will double the coins you put in.```"""
    }
    helppages["start"]+=f"This is page 1/{len(helppages)}!\nThese are all of the pages in the documentation currently:\n"
    count = 1
    for page in helppages:
        helppages["start"] += f"{count} - {page}\n"
        count += 1
    if not option:  # if the user hasn't included the name of a page
        pages = list(helppages.values())  # show all pages
        view = HelpButtons(0, pages)  # add the buttons
        await interaction.response.send_message(content=pages[0], view=view)  # send the message
    elif option.lower() in helppages.keys():  # otherwise if the user has put in a valid page name
        await interaction.response.send_message(content=helppages[option], ephemeral=True)  # send that page
    else:  # otherwise
        await interaction.response.send_message("I don't recognise that command, sorry...", ephemeral=True)
        # come up with an error message only visible to the user


client.run(TOKEN)
