import os
import pickle
import pathlib
import config
from time import strftime

attributes = ["id","coins","style","lasttrick"] # these are the valid attribute names

class Collector: # user class
    def __init__(self,id): # ID must be provided when instantiating class
        self.id = id # save ID
        self.coins = 0

    def __getattr__(self,attr): # this runs instead of an AttributeError if attribute is not found
        if attr in attributes: # if the attribute given is a valid name
            self.__dict__[attr] = 0 # set the value to 0, return it
            return 0
        else: # otherwise
            # Default behaviour
            raise AttributeError # raise an error

    def __repr__(self): # this shows when print(userlist) is run - useful for debugging
        return f"Collector with ID {self.id}"

class SearchableList(list): # new class can be used as a standard Python list, with additional functionality
    def find(self, userid) -> Collector: # iterates through userlist to find a user with the given ID
        return next((x for x in self if x.id == userid), None)

    def savestate(self): # saves list to SaveState.bin
        listtosave = self.convtolist() # converts to a standard list first
        # It's converted to a standard list as this means that I can add additional functionality
        # to the SearchableList class without having to recreate this list
        with open("SaveState.bin", "wb") as file:
            pickle.dump(listtosave, file)
        print(f"Saved State {self}")

        if not os.path.exists(pathlib.Path(strftime("backups/%Y.%m.%d/"))):
            os.makedirs(pathlib.Path(strftime("backups/%Y.%m.%d/")))  # make a folder if it doesn't already exist with the name of
            # today's date
        backuptime = pathlib.Path(strftime("%Y.%m.%d/%H.%M.%S"))
        with open(pathlib.Path("backups/%s.bin" % backuptime), "wb") as backup:
            pickle.dump(listtosave,backup)
        print(f"Saved to backups/{str(backuptime)}")

    def loadstate(self,client):
        if os.path.exists("SaveState.bin"):
            try:
                with open("SaveState.bin", "rb") as f:
                    loaded = pickle.load(f)
                    for item in loaded: # for each item in the loaded (standard) list
                        if not self.find(item.id):
                            self.append(item) # add this item to SearchableList if not already present
                            print(f"Loaded user ID {item.id}")
                        else:
                            print(f"User ID {item.id} already in list")
            except EOFError: # if there's been an error saving the file
                # EOFError only shows up if the file is empty
                os.remove("SaveState.bin") # delete the file

        for guild in client.guilds: # for each server the bot is in
            for member in guild.members: # for each member in those servers
                if self.find(member.id): # if this member is already in the list, skip
                    print(f"Skipping {member.id}")
                else: # otherwise, add
                    print(f"Adding {member.id}")
                    self.append(Collector(member.id))

        self.savestate() # save result


    def convtolist(self): # convert self to a list, return result
        result = list()
        for item in self:
            result.append(item)
        return result

def convertlegacyfile():
    # legacyfile = {userid:[coins,stylepoints,...],userid2:[coins,stylepoints,...]}
    # newformat = [collector(userid), collector(userid2), ...]

    with open(pathlib.Path("files/text files/coins.txt"), "r") as f:
        legacyfile = f.read()

    for item in legacyfile:
        user = Collector(legacyfile[item]) # creates a new Collector item with the ID of the current user
        user.coins = legacyfile[item][0]   # sets the new Collector item's coins to their old coin count
        user.style = legacyfile[item][1]   # sets the new Collector item's StylePoints™ to their old count
        config.userlist.append(user)
    
    config.userlist.savestate() # save result
    
