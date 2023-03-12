from common import *
import pickle
'''
class Pet:
    def __init__(self, ownerid: int, name: str = None):
        self.name = name if name else f"Pet {petslist.countuserspets(ownerid)}"

        self.health = 100
        self.stomach = 100
        self.marlboros = 100
        self.ownerid = ownerid

class PetList(list):
    def listfromuserid(self, id: int):
        return PetList(x for x in self if x.ownerid == id)

    def countuserspets(self, id: int) -> int:
        petlist = [x for x in self if x.ownerid == id]
        return len(petlist)

    def savestate(self):
        result = self.convtolist()



    def convtolist(self) -> list:
        result = []
        for item in self:
            result.append(item)
        return result

petslist = PetList()


@tree.command(name="pets",description="See your little group of friends!",
              guild=discord.Object(id=guildID))
async def livingcoin(interaction: discord.Interaction, command: str = None) -> None:
    await interaction.response.send_message(command)

@tree.command(name="givepet", description="birth a pet into this world",
              guild=discord.Object(id=guildID))
async def makepet(interaction: discord.Interaction, name: str = None) -> None:
    petslist.append(Pet(name=name,ownerid=interaction.user.id))
    await interaction.response.send_message(
        f"Congratulations! You now have a beautiful baby {petslist[-1].name}!"
    )
'''