from discord import Embed
from discord.ext import commands
from asyncio import sleep 
from os import path
from collections import OrderedDict
import time

import os
TOKEN = os.getenv("TOKEN")

os.environ['TZ'] = 'Australia/Sydney'
time.tzset()

replace = {'(re)':'🔼', 'COMMON':'Ⓒ', 'UNCOMMON':'Ⓤ', 'RARE':'Ⓡ', 'EPIC':'Ⓔ', 'LEGENDARY':'Ⓛ', 'MYTHIC':'Ⓜ', 'SPECIAL':'Ⓢ', 'VERY SPECIAL':'Ⓥ', 'DIVINE':'Ⓓ'}

bot = commands.Bot(command_prefix = '.')

def sort_margins(margins):
    try:
        sorteddict = OrderedDict(sorted(margins.items(), reverse=True))
        #sorted_dict_to_list = sorted(margins, key = lambda tup: tup[0], reverse=True)
        #return sorted_dict_to_list
        return sorteddict
    except AttributeError:
        pass

def get_margin(auctions):
    new_auction_list = {}
    for auc in auctions:
        if auc != '':
            pricei=int(auc.split("`")[5].replace(',',''))
            priceii=int(auc.split("`")[7].replace(',',''))
          
            '''pricei_i = auc.replace('`','')
            pricei_ii = pricei_i.split('Price: ')[1]
            pricei_iii = pricei_ii.split(' | ')[0]
            pricei_iv = pricei_iii.replace(',','')
            pricei_v = int(pricei_iv)
            priceii_i = auc.replace('`','')
            priceii_ii = priceii_i.split(' | Second LBIN: ')[1]
            priceii_iii = priceii_ii.split(' | CLean LBIN: ')[0]
            priceii_iv = priceii_iii.replace(',','')
            priceii_v = int(priceii_iv)'''

            margin = (priceii - pricei)
            #v nicer recom name

            if margin <= 500000000: 
                new_auction_list[margin] = auc
    if new_auction_list != {}: return new_auction_list

async def check_logs():
    lm_channel = bot.get_channel(977539449837731911)
    f2_2channel = bot.get_channel(977539531538567200)
    f3channel = bot.get_channel(977539588748890132)
    nodeletchannel = bot.get_channel(982478950288732180)
    lmlog = './fliplogs/logs_f1.txt'
    f2_2log = './fliplogs/logs_f2_2.txt'
    f3log = './fliplogs/logs_f3.txt'
    try:
        # part for #ah-sniper-f1
        with open(lmlog, 'r+') as f:
            if path.getsize('./fliplogs/logs_f1.txt') > 0:

                lines = [line.rstrip() for line in f]
                try:
                    slist = sort_margins(get_margin(lines))
                    await lm_channel.purge(limit=5)
                    
                    embed = Embed(title='Current Top Flips (1M Margin) 1st Filter')
                    
                    slistcut = list(slist.items())[:10]
                    
                    for i, (margin, aucstr) in enumerate(slistcut):
                        for rep in replace:
                          aucstr = aucstr.replace(rep, replace[rep])
                        #aucstr = tup[1]
                        embed.add_field(name=str(i+1)+'.', value=aucstr, inline=False)
                    await lm_channel.send(embed=embed)
                
                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)
                    print(current_time + ' flips sent')
                    f.truncate(0)
                except:
                    pass

        #ah-sniper-f2-v2

        with open(f2_2log, 'r+') as f:
            if path.getsize(f2_2log) > 0:
                lines = [line.rstrip() for line in f]
                try:
                    slist = sort_margins(get_margin(lines))
                    await f2_2channel.purge(limit=5)
                    embed = Embed(title='Current Top Flips (1M Margin) 2nd Filter v2')
                    slistcut = list(slist.items())[:10]
                    for i, (margin, aucstr) in enumerate(slistcut):
                        for rep in replace:
                          aucstr = aucstr.replace(rep, replace[rep])
                        embed.add_field(name=str(i+1)+'.', value=aucstr, inline=False)
                    await f2_2channel.send(embed=embed)
                    f.truncate(0)
                except:
                    pass

        with open(f3log, 'r+') as f:
            if path.getsize(f3log) > 0:
                lines = [line.rstrip() for line in f]
                try:
                    slist = sort_margins(get_margin(lines))
                    await f3channel.purge(limit=5)
                    embed = Embed(title='Top Flips (1M Margin) 3rd Filter')
                    slistcut = list(slist.items())[:10]
                    for i, (margin, aucstr) in enumerate(slistcut):
                        for rep in replace:
                          aucstr = aucstr.replace(rep, replace[rep])
                        await nodeletchannel.send(aucstr)
                        embed.add_field(name=str(i+1)+'.', value=aucstr, inline=False)
                    await f3channel.send(embed=embed)
                    f.truncate(0)
                except:
                    pass

    except Exception as e:
      print('uh oh error ' + str(e))
      pass


@bot.command(name = 'run')
async def start_check(ctx):
      print('bot started')
      while 1: #bro i dont get python
            await check_logs()
            await sleep(0.25)


@bot.event
async def on_ready():
      print('bot started')
      while 1:
            await check_logs()
            await sleep(0.25)

bot.run(TOKEN)