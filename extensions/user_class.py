import os
import pickle
import pathlib

attributes = ["id","coins","style","lasttrick"]

class Collector:
    def __init__(self,id):
        self.id = id
        self.coins = 0

    def __getattr__(self,attr):
        if attr in attributes:
            self.__dict__[attr] = 0
            return 0
        else:
            # Default behaviour
            raise AttributeError

    def __repr__(self):
        return f"Collector with ID {self.id}"

class SearchableList(list):
    def find(self, userid):
        return next((x for x in self if x.id == userid), None)

    def savestate(self):
        listtosave = self.convtolist()
        with open("SaveState.bin", "wb") as file:
            pickle.dump(listtosave, file)
        print(f"Saved State {self}")

    def loadstate(self,client):
        if os.path.exists("SaveState.bin"):
            try:
                with open("SaveState.bin", "rb") as f:
                    loaded = pickle.load(f)
                    for item in loaded:
                        self.append(item)
                        print(f"Loaded user ID {item.id}")
            except EOFError:
                os.remove("SaveState.bin")

        for guild in client.guilds:
            for member in guild.members:
                if self.find(member.id):
                    print(f"Skipping {member.id}")
                else:
                    print(f"Adding {member.id}")
                    self.append(Collector(member.id))

        self.savestate()


    def convtolist(self):
        result = list()
        for item in self:
            result.append(item)
        return result

def convertlegacyfile():
    # legacyfile = {userid:[coins,stylepoints,...],userid2:[coins,stylepoints,...]}
    # newformat = [collector(userid), collector(userid2), ...]

    with open(pathlib.Path("files/text files/coins.txt"), "r") as f:
        legacyfile = f.read()

    newformat = [collector(userid), collector(userid2), ...]

    for item in legacyfile:
        user = collector(legacyfile[item]) # creates a new Collector item with the ID of the current user
        user.coins = legacyfile[item][0]
        user.style = legacyfile[item][1]

    legacyfile.savestate()
    
