from extensions import user_class
class purchase:
    name: str
    cost: int
    emote: str
    id: int
    desc: str

    def __repr__(self):
        return f"Icon Store Item - {self.name}"

class storelist(list):
    def __init__(self):
        super().__init__()
    def find(self,name) -> purchase:
        return next((x for x in self if x.name == name), None)


TimeToCoin = [30, 60] # default: [30,1800]

coincount = 0
coinexpiry = 60 # default: 120
timebetweentricks = 14400 # in seconds - default: 14400

userlist = user_class.SearchableList()

storeicons = {
        "wayne": [25, "<:waynerTrick:726571399921139772>", 1058908672278925393, "Claim your Wayne Enjoyer Badge!"],
        "baaulp": [25, "<:baaulpPasta:757624627299090502>", 1058907806624919673, "Claim your Baaulp Enjoyer Badge!"],
        "holly": [25, "<:hollytonesBibi:757619654196985987>", 1058907905795047576, "Claim your Holly Enjoyer Badge!"],
        "gir": [25, "<:mastergirGirbot:757618605486637137>", 1058908071738474526, "Claim your Gir Enjoyer Badge!"],
        "mira": [25, "<:mirakuruPower:726574184452325517>", 1058907897775525888, "Claim your Mira Enjoyer Badge!"],
        "socpens": [25, "<:socpenBabie:757622293085159484>", 1058907911214076015, "Claim your Scorpy Enjoyer Badge!"],
        "logmore": [25, "<:logmorBanjo:757625482551230524>", 1058908079514734643, "Claim your Log Enjoyer Badge!"],
        "trog": [25, "<:tr0gDog:757626204122513558>", 1058908083981656074, "Claim your Trog Enjoyer Badge!"],
        "verified": [50, "<:verificationbadge:1058890128338194442>", 1054736944099246100, "Verify yourself!"],
        "bitcoin": [100, "<:waynerBitcoin:726571398641877002>", 1058908085365780550, "bit coin."],
        "premium": [500, "<:premium:1058929030717513799>", 1058929091870462022, "bit coin (GOLD)"],
        "diamond": [1000, "<:diamondclub:1058930102987149392>", 1058930387105104042, "Join the Diamond Elite Club!"]
    }

icons = storelist()
for item in storeicons:
    itemdesc = storeicons[item]
    newitem = purchase()
    newitem.name = item
    newitem.cost = itemdesc[0]
    newitem.emote = itemdesc[1]
    newitem.id = itemdesc[2]
    newitem.desc = f"Cost: {newitem.cost} - {itemdesc[3]}"
    icons.append(newitem)

print(icons)

