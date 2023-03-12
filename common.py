import discord
from discord import app_commands
from discord.ext import tasks
import dotenv
import os
global CHANNEL
import random
from config import userlist
import config
import asyncio
import pathlib

dotenv.load_dotenv(".env")
TOKEN: str = os.getenv("DISCORD_TOKEN")  # retrieve token from .env file
guildID: int = int(os.getenv("COIN_GUILD"))


class coin:

    def __init__(self):

        coinrarities = [
            ["undefined", "[error]", "error", 0, [0, 0]],
            ["bronze", "<a:bronzecoin:844545666201288755>", "bronze", 50, [1, 5]],
            ["silver", "<a:silvercoin:844545665911881788>", "silver", 80, [5, 10]],
            ["gold", "<a:goldcoin:813889535699189871>", "gold", 99, [10, 20]],
            ["SUPER RARE red", "<a:redcoin:844545670709772290>", "ultrarare", 100, [20, 50]],
        ]

        # Sets default coin rarities
        # FORMAT:
        # type[0] = name
        # type[1] = emote
        # type[2] = filename
        # type[3] = if rarity >= type[3]= this is chosen
        # type[4] = value calculator

        rarity = random.randint(1, 100)  # randomly generate style points
        for item in coinrarities:  # go through each type of coins
            if rarity <= item[3]:  # if it is this current coin rarity:
                type = item  # save it, break the loop
                break
        else:
            raise ValueError(f"Invalid Coin Rarity - {rarity}")  # else return an error

        self.name = type[0]  # save name from dict
        self.emote = type[1]  # save emote
        self.filename = type[2]  # save filename
        self.value = random.randint(type[4][0], type[4][1])  # calculate cost


class CoinButton(discord.ui.View):

    @discord.ui.button(label="Get Coin", style=discord.ButtonStyle.success)
    async def getcoin(self, interaction: discord.Interaction, button: discord.ui.button):
        if client.coinactive:
            client.coinactive = False  # disable coin
            await interaction.message.delete()  # delete coin message
            current = client.coin  # save the current coin to a variable
            user = userlist.find(interaction.user.id)  # find the user who clicked the button
            #               ^^^^                        see extensions.user_class for definition of 'find'
            user.coins += current.value  # give the user coins
            userlist.savestate()  # save
            s = "s" if user.coins != 1 else ""  # add an "s" to the message if there is more than 1 coin
            await interaction.response.send_message(
                f"""
    {current.emote} Congratulations, {interaction.user.display_name}! You gained {current.value} CowardCoins!
    You now have {user.coins} coin{s}."""
            )
        else:
            await interaction.response.send_message("Too slow... Sorry!", ephemeral=True)


class DiscordClient(discord.Client):  # create a new class from discord.py's Client

    def __init__(self):  # when this class is initialised
        super().__init__(intents=discord.Intents.all())  # run discord.Client's __init__
        # also, set the intents to default
        self.synced = False  # set synced to False
        self.coinactive = False  # make sure there is no coin active

    async def setup_hook(self) -> None:  # once the bot has been set up
        self.coin_creation_task.start()  # start the process for generating coins

    async def on_ready(self):  # this code defines how it knows it's connected
        await self.wait_until_ready()
        '''if not self.synced:  # if not synced
            print("Syncing to tree...")
            await tree.sync(guild=discord.Object(id=guildID))  # force a sync to the test server
            self.synced = True  # mark synced as True
            print("Synced")'''

        dotenv.load_dotenv(".env")  # load file '.env'
        channelID = os.getenv("COIN_CHANNEL")  # load channel in '.env' - this is where coins will be sent
        self.coinchannel = self.get_channel(int(channelID))  # set client.coinchannel to the coin channel object
        print(f'Logged in as {self.user} (ID: {self.user.id})')  # output username & ID
        print('------')
        await self.change_presence(activity=discord.Game(name="the economy 😎"))  # sets the status to Online
        userlist.loadstate(client)  # loads the current list of users from file

    #   ^^^^^^^^                     see config.py for definition of userlist
    #            ^^^^^^^^^           see extensions.user_class for definition of loadstate

    @tasks.loop(seconds=10)  # loop every 10 seconds
    async def coin_creation_task(self):
        # this task's job is to check if a coin is required. if a coin *is* required, create one
        # otherwise, start the process of a coin expiring
        if self.coinactive:  # if there is currently a coin
            print(f"Coin is expiring in {config.coinexpiry} seconds.")  # coin must expire
            await asyncio.sleep(config.coinexpiry)  # wait until the coin expires
            if self.coinactive:  # if the coin still exists
                try:  # this is here so that no error message is raised if the coin message is already gone
                    await self.sentmsg.delete()  # delete the coin message
                    messages = ["ran away!", "passed away peacefully in its sleep...", "expired...", "escaped!",
                                "exploded!"]
                    expirymsg = await self.coinchannel.send(f"The coin {random.choice(messages)}")
                    # send an alert that the coin has expired
                    await asyncio.sleep(config.coinexpiry)  # wait for {config.coinexpiry} seconds again
                    await expirymsg.delete()  # delete the expiry alert
                except:
                    pass  # ignore any errors
                self.coinactive = False  # deactivate coin
        elif self.synced:  # otherwise, if the bot is synced to Discord (to avoid errors)
            timetowait = random.randint(config.TimeToCoin[0], config.TimeToCoin[1])  # decide how long to wait
            print(f"Coin will appear in {timetowait} seconds")
            await asyncio.sleep(timetowait)  # wait for the coin to appear

            # The coin is created
            self.coin = coin()  # new instance of class 'coin'
            current = self.coin  # saves it temporarily to a local variable
            print(f"{current.name} coin generated")  # announce coin in log
            with open(pathlib.Path(f"files/images/{current.filename}.gif"), "rb") as f:  # open image file
                # noinspection PyTypeChecker
                picture = discord.File(f)  # attach image file
            view = CoinButton()  # add the 'get coin' button to the message
            self.sentmsg = await self.coinchannel.send(
                content=f"{current.emote} A new {current.name} coin has appeared! Click the button below to claim it!",
                file=picture, view=view)  # send the message - include the attached image, and the button

            self.coinactive = True  # set new coin to active

            # at this point, the task will repeat itself
            # after 10 seconds, it will discover that client.coinactive is true
            # and start the process for expiring the coin.

    @coin_creation_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in before creating a coin


client = DiscordClient()
# initialises the client to the class that's just been created
tree = app_commands.CommandTree(client)
# initialises the Command Tree, which allows us to use Discord's native Slash Commands