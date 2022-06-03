# modules

import asyncio
from re import sub
import os
op = os.name == 'nt'
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import time
import requests

os.environ['TZ'] = 'Australia/Sydney'
time.tzset()

# auction api

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

# result and prices variables

results = []
lm_results = []
f3_results = []
pet_results = []


prices = {}
pet_prices = {}

# parts to remove

STARS = (" ✦", "⚚ ", " ✪", "✪")
REFORGES = ("Withered ", "Fabled ", "Gilded ", "Warped ", "Jaded ", "Loving ", "Renowned ", "Giant ", "Ancient ", "Spiritual ", "Submerged "
) #only those that arent in ignore reforges f2
COLOR = ("Red ", "Orange ", "Yellow ", "Lime ", "Green ", "Aqua ", "Purple ", "Pink ", "Black ")

ignore_reforges_f2 = ( #rework to include all blacksmith and uselees stones
    #swords
    'Gentle ', 'Odd ', 'Fast ', 'Fair ', 'Epic ', 'Sharp ', 'Heroic ', 'Spicy ', 'Legendary ',
    #meh sword stones
    'Dirty ', 'Suspicious ', 'Bulky ',
    #bows
    'Deadly ', 'Fine ', 'Grand ', 'Hasty ', 'Neat ', 'Rapid ', 'Unreal ', 'Awkward ', 'Rich ',
    #meh bow stones
    'Headstrong ', 'Precise ',
    #armour
    'Clean ', 'Fierce ', 'Heavy ', 'Light ', 'Mythic ', 'Pure ', 'Smart ', 'Titanic ', 'Wise ',
    #meh armour stones
    'Perfect ', 'Necrotic ', 'Spiked ', 'Cubic ', 'Hyper ', 'Reinforced ', 'Ridiculous ', 'Empowered ',
  #special things
   'Very ', 'Highly ', 'Extremely ', 'Not So ', 'Thicc ', 'Absolutely ', 'Even More ', 'Strong ', 'Shiny ',
#others
  "Stiff ", "Lucky ", "Jerry's ", "Stellar ", "Heated ", "Ambered ", "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ",  "Moil ", "Blessed ", "Toil ", "Bountiful ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ", "Forceful ", "Hurtful ", "Keen ", "Unpleasant ", "Zealous ", "Double-Bit ", "Lumberjack's ", "Great ", "Rugged ", "Lush ", "Green Thumb ", "Peasant's ", "Robust ", "Zooming ", "Unyielding ", "Prospector's ", "Excellent ", "Sturdy ", "Fortunate ", "Strengthened ", "Fortified ", "Waxed ", "Glistening ", "Treacherous ", "Salty " 
)

# reforge filters

SWORDFLIPREFORGES_Filter_I = ('Fabled', 'Withered', 'Suspicious')
ARMORFLIPREFORGES_Filter_I = ('Ancient', 'Renowned', 'Necrotic')

IGNOREARMOURS_Filter_LM = ('Glacite', 'Goblin', 'Crystal', 'Farm', 'Mushroom', 'Angler', 'Pumpkin', 'Cactus', 'Leaflet', 'Lapis', 'Miner\'s', 'Golem', 'Miner', 'Hardened Diamond', 'Fairy', 'Growth', 'Salmon', 'Zombie', 'Speedster', 'Holy', 'Rotten', 'Bouncy', 'Heavy', 'Skeleton Grunt', 'Skeleton Soldier', 'Super Heavy')

awmrf3r_withered_prelist = ('Flower of Truth', 'Livid Dagger', 'Shadow Fury', 'Emerald Blade', 'Giant\'s Sword', 'Soul Whip', 'Phantom Rod')
awmrf3r_fabled_prelist = ('Flower of Truth', 'Livid Dagger', 'Shadow Fury', 'Emerald Blade', 'Giant\'s Sword', 'Voidedge Katana', 'Reaper Falchion', 'Soul Whip',' Phantom Rod')

armour_weapon_meta_reforge_f3_remake = {
    #reforge, items
    'Withered': awmrf3r_withered_prelist,
    'Fabled': awmrf3r_fabled_prelist,
    'Giant': ('Goldor\'s', 'Reaper Mask', 'Necromancer Lord'),
    'Ancient': ('Necron\'s', 'Maxor\'s', 'Final Destination', 'Shadow Assassin', 'Tarantula', 'Superior', 'Golden Bonzo', 'Diamond Bonzo', 'Golden Scarf', 'Diamond Scarf', 'Golden Professor', 'Diamond Professor', 'Golden Thorn', 'Diamond Thorn', 'Golden Livid', 'Diamond Livid', 'Golden Sadan', 'Diamond Sadan', 'Golden Necron', 'Diamond Necron'),
    'Loving': ('Storm\'s', 'Necromancer Lord'),
    'Jaded': ('Sorrow', 'Divan\'s'),
    'Spiritual': ('Juju Shortbow'),
    'Renowned': ('Sorrow'),
}


# the lowest price an item can have
LOWEST_PRICE = 1 #general lowest price


# config variables
LOWEST_PERCENT_MARGIN = 1/2 # percent diffences for super sniper
LARGE_MARGIN_P_M = 0.9 # percent differences for filtered snipers
LARGE_MARGIN = 1000000 # flips that are more than a mil profit
LARGE_MARGIN_MAXCOST = 200000000 #200m
F3_MAXCOST = 200000000 #200m

START_TIME = default_timer()

def pricedump():
  with open("prices.txt","w") as file:
    file.truncate(0)
    file.write(str(prices))  
  with open("petprices.txt","w") as file:
    file.truncate(0)
    file.write(str(pet_prices))  


def auc(auction):
  try:
    if not auction['claimed'] and auction['bin'] == True and not "Furniture" in auction["item_lore"]: # if the auction isn't a) claimed and is b) BIN
      name = str(auction['item_name'])
      if auction['category'] == 'armor':
        for m in IGNOREARMOURS_Filter_LM:
          if m in name:
              return
      if "consumables" == auction['category']:
        return
      if "§dCake Soul" in auction["item_lore"]:
        return #can remove soon
      if "Rune I" in name:
        return
      if "§ka§r" in auction["item_lore"]:
         name = str(" ".join([name,"(re)"]))
      if "One For All" in auction["item_lore"]:
        name = str(" ".join([name,"(OFA)"]))
      for reforge in ignore_reforges_f2:
        name = name.replace(reforge, "")

    #fix if wise/strong/sup/perfect/refined pick
      if auction['category'] == 'armor':
        if "Wise Blood" in auction["item_lore"]:
          name = str(" ".join(["Wise",name]))
        elif "Strong Blood" in auction["item_lore"]:
          name = str(" ".join(["Strong",name]))
        elif " - Tier" in name:
          name = str(" ".join(["Perfect",name]))
      if "CLOAK" in auction["item_lore"] and "abilities" in auction["item_lore"]:
        name = str(" ".join(["Ancient",name]))
      if "Crab Hat of Celebration" in name:
        for color in COLOR:
          name = name.replace(color, "")

      
      tier = str(auction['tier'])
                      
      if 'Right-click to add this pet to' in auction['item_lore']:
        petname = name
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
        petindex = str(" ".join([plevel, name, tier]))
        index = sub("\[[^\]]*\]", "", " ".join([petname, tier]))
      else:
        index = sub("\[[^\]]*\]", "", " ".join([name, tier]))                        
        petindex = ""

   #print("indexes formatted "+ str(default_timer() - datastart))

#if price is bad and not pet, just return
      if index in prices:
        if prices[index][1] < auction['starting_bid'] and petindex == "":
          return

          
    # VV if the current item already has a price in the prices map, the price is updated                     
      if index in prices:
          if prices[index][0] > auction['starting_bid']:
              prices[index][1] = prices[index][0]
              prices[index][0] = auction['starting_bid']
          elif prices[index][1] > auction['starting_bid']:
              prices[index][1] = auction['starting_bid']
          #elif prices[index][1] < auction['starting_bid']:
              #return
# VV otherwise, it's added to the prices map
      else:
        prices[index] = [auction['starting_bid'], float("inf")]
                          

#pet flipper
      if petindex != "":
        if petindex in pet_prices:
          if pet_prices[petindex][0] > auction['starting_bid']:
            pet_prices[petindex][1] = pet_prices[petindex][0]
            pet_prices[petindex][0] = auction['starting_bid']
          elif pet_prices[petindex][1] > auction['starting_bid']:
            pet_prices[petindex][1] = auction['starting_bid']
        else:
          pet_prices[petindex] = [auction['starting_bid'], float("inf")]


      #print("indexed "+ str(default_timer() - datastart))

      if auction['start']+60000 < now:
        return
                              

      if petindex != "":
        if pet_prices[petindex][0]/pet_prices[petindex][1] < LARGE_MARGIN_P_M and pet_prices[petindex][1] - pet_prices[petindex][0] >= LARGE_MARGIN:
            pet_results.append([auction['uuid'], petindex, auction['starting_bid'], petindex])         
# vv since f3_maxcost is larger than large_margin_maxcost, i can check to see if large_margin_maxcost within f3_maxcost
          
      if prices[index][0]/prices[index][1] < LARGE_MARGIN_P_M and prices[index][1] - prices[index][0] >= LARGE_MARGIN and prices[index][0] <= F3_MAXCOST:
        if prices[index][0] <= LARGE_MARGIN_MAXCOST:
            lm_results.append([auction['uuid'], sub(tier, "", index), auction['starting_bid'], index])
          
  except Exception as e:
    print("error! "+ str(e))
    return

    
def fetch(session, page):
    global scanned
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="
    with session.get(base_url + page) as response:
        # puts response in a dict
        try:
            data = response.json()
            toppage = data['totalPages']
            if data['success']:
                toppage = data['totalPages']
                #datastart = default_timer()
                for auction in data['auctions']:
                    scanned = scanned + 1
                    auc(auction)
                #print("flip calc "+ str(default_timer() - datastart))
            
            return data
        except Exception as e:
            print("error! "+ str(e))
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
                    *(session, page) # Allows us to pass in multiple arguments to `fetch`
                )
                # runs for every page
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass

def main():
    flipstart = default_timer()
    pricedump()
    # Resets variables
    global results, lm_results, prices, pet_results, pet_prices, START_TIME, scanned
    scanned = int(0)
    START_TIME = default_timer()
    results = []
    lm_results = []
    pet_results = []
    pet_prices = {}
    prices = {}
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    # Makes sure all the results are still up to date

    if len(lm_results): 
      lm_results = [[entry, prices[entry[3]][1]] for entry in lm_results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LARGE_MARGIN_P_M and prices[entry[3]][1] - prices[entry[3]][0] >= LARGE_MARGIN and prices[entry[3]][0] <= LARGE_MARGIN_MAXCOST)]
    if len(pet_results): pet_results = [[entry, pet_prices[entry[3]][1]] for entry in pet_results if (entry[2] > LOWEST_PRICE and pet_prices[entry[3]][1] != float('inf') and pet_prices[entry[3]][0] == entry[2] and pet_prices[entry[3]][0]/pet_prices[entry[3]][1] < LARGE_MARGIN_P_M and pet_prices[entry[3]][1] - pet_prices[entry[3]][0] >= LARGE_MARGIN and pet_prices[entry[3]][0] <= LARGE_MARGIN_MAXCOST)]
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print("main() done " + str(round(default_timer() - flipstart, 3)))
    print(str(scanned) + ' auctions scanned')
    print(current_time + ' flips calculated')
 

    ##ah-sniper-f1 and #ah-sniper-filtered

    if len(lm_results):
        for result in lm_results:
            #print(result)
            with open('./fliplogs/logs_f1.txt', 'a') as fAp2:
                toprint = "\n" + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fAp2.write(toprint)
                #fAp.close()
                #print(toprint)
            with open('./fliplogs/logs_f2.txt', 'a') as fAp3:
                truechecker = []
                if not False in truechecker:
                    toprint = "\n" + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                    fAp3.write(toprint)
            with open('./fliplogs/logs_f2_2.txt', 'a') as fAp3_2:
                truechecker2 = []
                if ('✪' not in str(result[0][1]) or str(result[0][1]).count('✪') == 5):
                  truechecker2.append(True)
                else:
                  truechecker2.append(False)
                if not False in truechecker2:
                    toprint = "\n" + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                    fAp3_2.write(toprint)
            with open('./fliplogs/logs_f3.txt', 'a') as fAp4:
                for reforge, AorWs in armour_weapon_meta_reforge_f3_remake.items():
                    if reforge in str(result[0][1]) and any(substring in str(result[0][1]) for substring in AorWs) and ('✪' not in str(result[0][1]) or str(result[0][1]).count('✪') == 5):
                        toprint = "\n" + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                        fAp4.write(toprint)
    
    if len(pet_results):
        for result in pet_results:
            with open('./fliplogs/pet_logs.txt', 'a') as fAp5:
                toprint = "\n" + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fAp5.write(toprint)


print("main started")
main()

def dostuff():
  global now, toppage

    # if 60 seconds have passed since the last update
  if time.time()*1000 > now + 58000:
    prevnow = now
    now = float('inf')
    try:
      c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0").json()
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
    except Exception as e:
      print('uh oh error ' + str(e))
      pass





while 1:
    dostuff()
    time.sleep(0.25)
