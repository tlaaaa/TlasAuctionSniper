# modules

import asyncio
from re import sub
import os, sys
op = os.name == 'nt'
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import time
import requests
import json

os.environ['TZ'] = 'Australia/Sydney'
time.tzset()


# auction api

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

# result and prices variables

lm_results = []
apiresponse = {}
prices = {}

# parts to remove

STARS = (" ✦", "⚚ ", " ✪", "✪")
MSTARS = ('➊', '➋', '➌', '➍', '➎')
REFORGES = ("Withered ", "Fabled ", "Gilded ", "Warped ", "Jaded ", "Loving ",
            "Renowned ", "Giant ", "Ancient ", "Spiritual ", "Submerged "
            )  #only those that arent in ignore reforges f2
COLOR = ("Red ", "Orange ", "Yellow ", "Lime ", "Green ", "Aqua ", "Purple ",
         "Pink ", "Black ")
GSLOTS = ("[§7", "§f[", "§a[", "§9[", "§5[", "§6[")


ignore_reforges_f2 = (  #rework to include all blacksmith and uselees stones
    #swords
    'Gentle ',
    'Odd ',
    'Fast ',
    'Fair ',
    'Epic ',
    'Sharp ',
    'Heroic ',
    'Spicy ',
    'Legendary ',
    #meh sword stones
    'Dirty ',
    'Suspicious ',
    'Bulky ',
    #bows
    'Deadly ',
    'Fine ',
    'Grand ',
    'Hasty ',
    'Neat ',
    'Rapid ',
    'Unreal ',
    'Awkward ',
    'Rich ',
    #meh bow stones
    'Headstrong ',
    'Precise ',
    #armour
    'Clean ',
    'Fierce ',
    'Heavy ',
    'Light ',
    'Mythic ',
    'Pure ',
    'Smart ',
    'Titanic ',
    'Wise ',
    #meh armour stones
    'Perfect ',
    'Necrotic ',
    'Spiked ',
    'Cubic ',
    'Hyper ',
    'Reinforced ',
    'Ridiculous ',
    'Empowered ',
    #special things
    'Very ',
    'Highly ',
    'Extremely ',
    'Not So ',
    'Thicc ',
    'Absolutely ',
    'Even More ',
    'Strong ',
    'Shiny ',
    #others
    "Stiff ",
    "Lucky ",
    "Jerry's ",
    "Stellar ",
    "Heated ",
    "Ambered ",
    "Fruitful ",
    "Magnetic ",
    "Fleet ",
    "Mithraic ",
    "Auspicious ",
    "Refined ",
    "Moil ",
    "Blessed ",
    "Toil ",
    "Bountiful ",
    "Sweet ",
    "Silky ",
    "Bloody ",
    "Shaded ",
    "Bizarre ",
    "Itchy ",
    "Ominous ",
    "Pleasant ",
    "Pretty ",
    "Simple ",
    "Strange ",
    "Vivid ",
    "Godly ",
    "Demonic ",
    "Forceful ",
    "Hurtful ",
    "Keen ",
    "Unpleasant ",
    "Zealous ",
    "Double-Bit ",
    "Lumberjack's ",
    "Great ",
    "Rugged ",
    "Lush ",
    "Green Thumb ",
    "Peasant's ",
    "Robust ",
    "Zooming ",
    "Unyielding ",
    "Prospector's ",
    "Excellent ",
    "Sturdy ",
    "Fortunate ",
    "Strengthened ",
    "Fortified ",
    "Waxed ",
    "Glistening ",
    "Treacherous ",
    "Salty ",
    "Candied ",
"Reforged ")

# reforge filters

SWORDFLIPREFORGES_Filter_I = ('Fabled', 'Withered', 'Suspicious')
ARMORFLIPREFORGES_Filter_I = ('Ancient', 'Renowned', 'Necrotic')

IGNOREARMOURS_Filter_LM = ('Glacite', 'Goblin', 'Crystal', 'Farm', 'Mushroom',
                           'Angler', 'Pumpkin', 'Cactus', 'Leaflet', 'Lapis',
                           'Miner\'s', 'Golem', 'Miner', 'Hardened Diamond',
                           'Fairy', 'Growth', 'Salmon', 'Zombie', 'Speedster',
                           'Holy', 'Rotten', 'Bouncy', 'Heavy',
                           'Skeleton Grunt', 'Skeleton Soldier', 'Super Heavy')

awmrf3r_withered_prelist = ('Flower of Truth', 'Livid Dagger', 'Shadow Fury',
                            'Emerald Blade', 'Giant\'s Sword', 'Soul Whip',
                            'Phantom Rod')
awmrf3r_fabled_prelist = ('Flower of Truth', 'Livid Dagger', 'Shadow Fury',
                          'Emerald Blade', 'Giant\'s Sword', 'Voidedge Katana',
                          'Reaper Falchion', 'Soul Whip', ' Phantom Rod')

armour_weapon_meta_reforge_f3_remake = {
    #reforge, items
    'Withered':
    awmrf3r_withered_prelist,
    'Fabled':
    awmrf3r_fabled_prelist,
    'Giant': ('Goldor\'s', 'Reaper Mask', 'Necromancer Lord'),
    'Ancient':
    ('Necron\'s', 'Maxor\'s', 'Final Destination', 'Shadow Assassin',
     'Tarantula', 'Superior', 'Golden Bonzo', 'Diamond Bonzo', 'Golden Scarf',
     'Diamond Scarf', 'Golden Professor', 'Diamond Professor', 'Golden Thorn',
     'Diamond Thorn', 'Golden Livid', 'Diamond Livid', 'Golden Sadan',
     'Diamond Sadan', 'Golden Necron', 'Diamond Necron'),
    'Loving': ('Storm\'s', 'Necromancer Lord'),
    'Jaded': ('Sorrow', 'Divan\'s'),
    'Spiritual': ('Juju Shortbow'),
    'Renowned': ('Sorrow'),
}

enchantstocheck = {
    'Soul Eater V': 'SE5',
    'One For All': 'OFA',
    'Overload V': 'Ov5',
    'Legion V': 'L5',
    'Ultimate Wise V': 'UW5',
    'Pristine V': 'P5',
    'Wisdom V': 'W5',
    'Swarm V': 'S5',
    'Last Stand V': 'LS5',
    'Inferno V': 'I5',
    'Flash V': 'F5',
    'Fatal Tempo V': 'FT5',
    'Duplex V': 'D5',
    'Chimera V': 'C5'
}

# the lowest price an item can have
LOWEST_PRICE = 1  #general lowest price

# config variables
LOWEST_PERCENT_MARGIN = 1 / 2  # percent diffences for super sniper
LARGE_MARGIN_P_M = 0.9  # percent differences for filtered snipers
LARGE_MARGIN = 1000000  # flips that are more than a mil profit
LARGE_MARGIN_MAXCOST = 2000000000  #2b limit lol
F3_MAXCOST = 2000000000  #^

START_TIME = default_timer()


def pricedump():
    with open("prices.txt", "w") as file:
        file.truncate(0)
        file.write(str(prices))


def auc(auction):
    try:
        if not auction['claimed'] and auction[
                'bin'] == True and not "Furniture" in auction[
                    "item_lore"] and auction['start'] + 60000 > now:  # if the auction isn't a) claimed and is b) BIN
            lore = str(auction['item_lore'])
            name = str(auction['item_name'])
            if "consumables" == auction['category']:
                return
            if auction['category'] == 'armor':
                for m in IGNOREARMOURS_Filter_LM:
                    if m in name:
                        return
            if "§dCake Soul" in lore:
                return  #can remove soon
            if "Rune I" in name:
                return

            #bad reforge fixing
            for reforge in ignore_reforges_f2:
                name = name.replace(reforge, "")
            for r in REFORGES:
                name = name.replace(r, "Reforged ")
            if ('✪'  in name and name.count('✪') != 5):
              name = name.replace(" ✪", "")
              name = name.replace("✪", "")
              
        #fix if wise/strong/sup/perfect/refined pick
            if auction['category'] == 'armor':
                if "Wise Blood" in lore:
                    name = str(" ".join(["Wise", name]))
                elif "Strong Blood" in lore:
                    name = str(" ".join(["Strong", name]))
                elif " - Tier" in name:
                    name = str(" ".join(["Perfect", name]))
            if "CLOAK" in lore and "abilities" in lore:
                name = str(" ".join(["Ancient", name]))
            if "Crab Hat of Celebration" in name or "Repelling Candle" in name:
                for color in COLOR:
                    name = name.replace(color, "")
            cleanindex = " ".join([name, auction['tier']])
            enchants = []
            #extra info
            if "§ka§r" in lore:
                name = str(" ".join([name, "(re)"]))
            for e in enchantstocheck:
                if e in lore:
                    enchants.append(enchantstocheck[e])
            slots = False
            for s in GSLOTS:
                if s in lore:
                  if "§8[§8" not in lore:
                    slots = True
            if slots:
                  enchants.append("slots")
            if len(enchants):
                ench = "".join([" ", "(", ", ".join(enchants), ")"])
                name = str("".join([name, ench]))
            else:
                ench = ""
            tier = str(auction['tier'])

            if 'Right-click to add this pet to' in auction['item_lore']:
                name = sub("[\[\]]", "", name)
                p = name.split(" ")
                plevel = int(p[1])
                if plevel != 100:
                    if plevel > 95:
                        plevel = "lvl>95"
                    elif plevel > 90:
                        plevel = "lvl>90"
                    elif plevel > 75:
                        plevel = "lvl>75"
                    else:
                        plevel = "lvl>0"
                else:
                    plevel = "lvl100"
                p = p[2:]
                name = " ".join(p)
                index = str(" ".join([plevel, name, tier]))
                cleanindex = index
            else:
                index = sub("\[[^\]]*\]", "", " ".join([name, tier]))
            for star in STARS:
                cleanindex = cleanindex.replace(star, "")
            for mstar in MSTARS:
                cleanindex = cleanindex.replace(mstar, "")
            for reforge in REFORGES:
                cleanindex = cleanindex.replace(reforge, "")
            if cleanindex == index:
                cleanindex = ""

    #print("indexes formatted "+ str(default_timer() - datastart))
#if price is bad, just return
            if index in prices:
                if prices[index][1] < auction['starting_bid']:
                    return

        # VV if the current item already has a price in the prices map, the price is updated
            if index in prices:
                if prices[index][0] > auction['starting_bid']:
                    prices[index][1] = prices[index][0]
                    prices[index][0] = auction['starting_bid']
                elif prices[index][1] > auction['starting_bid']:
                    prices[index][1] = auction['starting_bid']
# VV otherwise, it's added to the prices map
            else:
                prices[index] = [auction['starting_bid'], float("inf")]

                #do same for cleanindex!
            if cleanindex != "":
                if cleanindex in prices:
                    if prices[cleanindex][0] > auction['starting_bid']:
                        prices[cleanindex][1] = prices[cleanindex][0]
                        prices[cleanindex][0] = auction['starting_bid']
                    elif prices[cleanindex][1] > auction['starting_bid']:
                        prices[cleanindex][1] = auction['starting_bid']
                else:
                    prices[cleanindex] = [
                        auction['starting_bid'],
                        float("inf")
                    ]

            #print("indexed "+ str(default_timer() - datastart))

            if auction['start'] + 60000 < now:
                return


# vv since f3_maxcost is larger than large_margin_maxcost, i can check to see if large_margin_maxcost within f3_maxcost

            if prices[index][0] / prices[index][
                    1] < LARGE_MARGIN_P_M and prices[index][1] - prices[index][
                        0] >= LARGE_MARGIN and prices[index][0] <= F3_MAXCOST:
                if prices[index][0] <= LARGE_MARGIN_MAXCOST:
                    sendname = auction['item_name']
                    if ench != "":
                      sendname = "".join([sendname, ench])
                    if "§ka§r" in lore:
                      sendname = str(" ".join([sendname, "(re)"]))
                    sendname = " ".join([sendname, tier])
                    if cleanindex:
                        lm_results.append([
                            auction['uuid'], sendname, auction['starting_bid'],
                            index, cleanindex
                        ])
                    else:
                        lm_results.append([
                            auction['uuid'], sendname, auction['starting_bid'],
                            index
                        ])

    except Exception as e:
        print("error! " + str(e))
        return

def index(auction):
    try:
        if not auction['claimed'] and auction[
                'bin'] == True and not "Furniture" in auction[
                    "item_lore"]:  # if the auction isn't a) claimed and is b) BIN
            lore = str(auction['item_lore'])
            name = str(auction['item_name'])
            if "consumables" == auction['category']:
                return
            if auction['category'] == 'armor':
                for m in IGNOREARMOURS_Filter_LM:
                    if m in name:
                        return
            if "§dCake Soul" in lore:
                return  #can remove soon
            if "Rune I" in name:
                return

            #bad reforge fixing
            for reforge in ignore_reforges_f2:
                name = name.replace(reforge, "")
            for r in REFORGES:
                name = name.replace(r, "Reforged ")
            if ('✪'  in name and name.count('✪') != 5):
              name = name.replace(" ✪", "")
              name = name.replace("✪", "")
              
        #fix if wise/strong/sup/perfect/refined pick
            if auction['category'] == 'armor':
                if "Wise Blood" in lore:
                    name = str(" ".join(["Wise", name]))
                elif "Strong Blood" in lore:
                    name = str(" ".join(["Strong", name]))
                elif " - Tier" in name:
                    name = str(" ".join(["Perfect", name]))
            if "CLOAK" in lore and "abilities" in lore:
                name = str(" ".join(["Ancient", name]))
            if "Crab Hat of Celebration" in name or "Repelling Candle" in name:
                for color in COLOR:
                    name = name.replace(color, "")
            cleanindex = " ".join([name, auction['tier']])
            enchants = []
            #extra info
            if "§ka§r" in lore:
                name = str(" ".join([name, "(re)"]))
            for e in enchantstocheck:
                if e in lore:
                    enchants.append(enchantstocheck[e])
            slots = False
            for s in GSLOTS:
                if s in lore:
                  if "§8[§8" not in lore:
                    slots = True
            if slots:
                  enchants.append("slots")
            if len(enchants):
                ench = "".join([" ", "(", ", ".join(enchants), ")"])
                name = str("".join([name, ench]))
            else:
                ench = ""
            tier = str(auction['tier'])

            if 'Right-click to add this pet to' in auction['item_lore']:
                name = sub("[\[\]]", "", name)
                p = name.split(" ")
                plevel = int(p[1])
                if plevel != 100:
                    if plevel > 95:
                        plevel = "lvl>95"
                    elif plevel > 90:
                        plevel = "lvl>90"
                    elif plevel > 75:
                        plevel = "lvl>75"
                    else:
                        plevel = "lvl>0"
                else:
                    plevel = "lvl100"
                p = p[2:]
                name = " ".join(p)
                index = str(" ".join([plevel, name, tier]))
                cleanindex = index
            else:
                index = sub("\[[^\]]*\]", "", " ".join([name, tier]))
            for star in STARS:
                cleanindex = cleanindex.replace(star, "")
            for mstar in MSTARS:
                cleanindex = cleanindex.replace(mstar, "")
            for reforge in REFORGES:
                cleanindex = cleanindex.replace(reforge, "")
            if cleanindex == index:
                cleanindex = ""

    #print("indexes formatted "+ str(default_timer() - datastart))
#if price is bad, just return
            if index in prices:
                if prices[index][1] < auction['starting_bid']:
                    return

        # VV if the current item already has a price in the prices map, the price is updated
            if index in prices:
                if prices[index][0] > auction['starting_bid']:
                    prices[index][1] = prices[index][0]
                    prices[index][0] = auction['starting_bid']
                elif prices[index][1] > auction['starting_bid']:
                    prices[index][1] = auction['starting_bid']
# VV otherwise, it's added to the prices map
            else:
                prices[index] = [auction['starting_bid'], float("inf")]

                #do same for cleanindex!
            if cleanindex != "":
                if cleanindex in prices:
                    if prices[cleanindex][0] > auction['starting_bid']:
                        prices[cleanindex][1] = prices[cleanindex][0]
                        prices[cleanindex][0] = auction['starting_bid']
                    elif prices[cleanindex][1] > auction['starting_bid']:
                        prices[cleanindex][1] = auction['starting_bid']
                else:
                    prices[cleanindex] = [
                        auction['starting_bid'],
                        float("inf")
                    ]
    except Exception as e:
        print("error! " + str(e))
        return

def fetch(session, page):
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="
    with session.get(base_url + page) as response:
        # puts response in a dict
        try:
            data = response.json()
            toppage = data['totalPages']
            if data['success']:
                toppage = data['totalPages']
                for auction in data['auctions']:
                    index(auction)

            return data
        except Exception as e:
            print("error! " + str(e))
            return


async def get_data_asynchronous():
    # puts all the page strings
    pages = [str(x) for x in range(toppage)]
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, page
                      )  # Allows us to pass in multiple arguments to `fetch`
                )
                # runs for every page
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass


def find():
    try:
        data = requests.get(
            "https://api.hypixel.net/skyblock/auctions?page=0").json()
        if data['success']:
            for auction in data['auctions']:
                auc(auction)
        return data
    except Exception as e:
        print("error! " + str(e))
        return


def main():
    flipstart = default_timer()
    # Resets variables
    global lm_results, prices, START_TIME, apiresponse, apifinalresponse
    START_TIME = default_timer()
    lm_results = []

    find()

    # Makes sure all the results are still up to date

    if len(lm_results):
        for e in range(len(lm_results)):
            entry = lm_results[e]
            if (prices[entry[3]][1] != float('inf')
                    and prices[entry[3]][0] == entry[2]
                    and prices[entry[3]][0] / prices[entry[3]][1] <
                    LARGE_MARGIN_P_M and
                    prices[entry[3]][1] - prices[entry[3]][0] >= LARGE_MARGIN
                    and prices[entry[3]][0] <= LARGE_MARGIN_MAXCOST):
                if len(lm_results[e]) == 4:
                    lm_results[e] = lm_results[e] + [prices[entry[3]][1]]
                else:
                    lm_results[e] = lm_results[e] + [prices[entry[3]][1]]
                    lm_results[e] = lm_results[e] + [prices[entry[4]][0]]
            else:
                lm_results[e] = ""
    while '' in lm_results:
        lm_results.remove('')
      
    if len(lm_results):
        for result in lm_results:
          if result != "":
            #print(result)
            with open('./fliplogs/logs_f1.txt', 'a') as fAp2:
              if len(result) == 7:
                toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[5]) + " | Clean LBIN `{:,}`".format(result[6])
              else:
                toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[4])
              fAp2.write(toprint)
              #print(toprint)
            with open('./fliplogs/logs_f2.txt', 'a') as fAp3:
                  if len(result) == 7:
                    toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[5]) + " | Clean LBIN `{:,}`".format(result[6])
                  else:
                    toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[4])
                  fAp3.write(toprint)
            with open('./fliplogs/logs_f2_2.txt', 'a') as fAp3_2:
                if ('✪' not in str(result[1]) or str(result[1]).count('✪') == 5):
                  if len(result) == 7:
                    toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[5]) + " | Clean LBIN `{:,}`".format(result[6])
                  else:
                    toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[4])
                  fAp3_2.write(toprint)
            with open('./fliplogs/logs_f3.txt', 'a') as fAp4:
                for reforge, AorWs in armour_weapon_meta_reforge_f3_remake.items():
                    if reforge in str(result[1]) and any(substring in str(result[1]) for substring in AorWs) and ('✪' not in str(result[1]) or str(result[1]).count('✪') == 5):
                      if len(result) == 7:
                         toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[5]) + " | Clean LBIN `{:,}`".format(result[6])
                      else:
                        toprint = "\n" + "/viewauction `" + str(result[0]) + "` | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[4])
                      fAp4.write(toprint)
    

    print("time since api: " + str(round((time.time() - now/1000), 3)))
    print("main() done " + str(round(default_timer() - flipstart, 3)))
    with open("results.json", "w") as file:
        json.dump(lm_results, file)

    ##ah-sniper-f1 and #ah-sniper-filtered
    prices = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)
    pricedump()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time + ' prices cached')


prices = {}
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
future = asyncio.ensure_future(get_data_asynchronous())
loop.run_until_complete(future)
print("main started")
main()


def dostuff():
    global now, toppage

    # if 60 seconds have passed since the last update
    if time.time() * 1000 > now + 59000:
        prevnow = now
        now = float('inf')
        try:
            c = requests.get(
                "https://api.hypixel.net/skyblock/auctions?page=0")
            type = str(c.headers['Content-Type'])
            if c.ok and 'application/json; charset=utf-8' == type:
                try:
                    c = c.json()
                    if c:
                        if c['lastUpdated'] != prevnow:
                            now = c['lastUpdated']
                            toppage = c['totalPages']

                            t = time.localtime()
                            current_time = time.strftime("%H:%M:%S", t)
                            print(current_time + ' new data')
                            main()
                        else:
                            now = prevnow
                            return
                except ValueError:
                    print('bad response')
            else:
                print('not json response')
        except Exception as e:
            print('uh oh error ' + str(e))
            os.execv(sys.executable, ['python'] + sys.argv)


while 1:
    dostuff()
    time.sleep(0.05)
