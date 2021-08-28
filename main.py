from mcstatus import MinecraftServer
from tempfile import TemporaryFile
import discord
import requests,json,time,asyncio
from math import floor,modf
import math
from datetime import datetime
import os,random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import urllib.request
client = discord.Client()
inr=[]
tfcoords=[1100,100]
def get_updates(resp):
    for player in resp['players']:
        t=open(f"oplayers/{player['name']}.dat","w")
        t.write(f"{player['world']}\n{player['x']}\nidk\n{player['z']}\n{player['yaw']}")
        t.close()

def radd(client,radius, resp):
    global inr
    me={}

    for player in resp['players']:
        if player['name']=="robert300":
            me=player
            break
    if me=={}:
        return
    for player in resp['players']:
        if player['name']==me['name']:
            continue
        if player['world']!=me['world'] and player['name'] in inr:
            inr.remove(player['name'])
            return f"`{player['name']}` покинул ваш радиус"
        if player['world']!=me['world']:
            continue
        if player['x']-me['x']>100 and player['z']-me['z']>100 and player['name'] in inr:
            inr.remove(player['name'])
            return f"`{player['name']}` покинул ваш радиус "
        if player['x'] in range(me['x']-100,me['x']+100) and player['z'] in range(me['z']-100,me['z']+100):
            if player['name'] in inr:
                return
            inr.append(player['name'])
            return f"`{player['name']}` в вашем радиусе"

def sometext(link,yaw,pcx,pcz,cx,cz,plr,world,players):
    tfl=TemporaryFile()
    if plr==None:
        return {"err":False,"offline":True}
    urllib.request.urlretrieve(link,tfl)
    marker = Image.open("marker.png")
    marker=marker.rotate(yaw)
    img = Image.open(tfl)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Minecraft.otf", 10)
    shadowcolor="black"
    for player in players:
        if plr['world']!=player['world']:
            continue
        text=player['name']
        mark=marker.rotate(player['yaw'])
        pcx=player['x']-cx*512
        pcz=player['z']-cz*512
        draw.text((pcx+10-1, pcz-1), text, font=font, fill=shadowcolor)
        draw.text((pcx+10+1, pcz-1), text, font=font, fill=shadowcolor)
        draw.text((pcx+10, pcz-1-1), text, font=font, fill=shadowcolor)
        draw.text((pcx+10, pcz+1-1), text, font=font, fill=shadowcolor)
        draw.text((pcx+10, pcz-1),text,font=font,fill="white")
        img.paste(marker,(pcx,pcz),mark)
    table=['a','b','c','d','e','f','g','h','i','g','k','l','m','n','o','p','q','r','a','t','u','v','w','x','y','z']
    name=random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)+random.choice(table)
    fp = TemporaryFile()
    img.save(fp, "PNG")
    return {"err":False,"text":f"`{plr['name']}` X: `{plr['x']}` Z: `{plr['z']}` Yaw: `{plr['yaw']}`","file":fp}
def getmap(message):
    try:
        resp=json.loads(requests.get("https://map.reworlds.su/tiles/players.json", timeout=5).text)
    except:
        return {"err":True,"code":"RESP_ERR"}
    for player in resp['players']:
        if player['name']==message.content.split(" ")[1]:
            chunkx=floor(player['x']/512)
            chunkz=floor(player['z']/512)
            yaw=player['yaw']
            pcx=player['x']-chunkx*512
            pcz=player['z']-chunkz*512
            link=f"https://map.reworlds.su/tiles/{player['world']}/3/{chunkx}_{chunkz}.png"
            return sometext(link,yaw,pcx,pcz,chunkx,chunkz,player,player['world'],resp['players'])

async def radcord(client):
    await client.wait_until_ready()
    radius=client.get_user(458999331513696256)
    try:
        resp=json.loads(requests.get("https://map.reworlds.su/tiles/players.json",timeout=5).text)
    except:
        print("Ошибка! Время: "+str(time.time()))
    get_updates(resp)
    mess=radd(client, radius, resp)
    if mess!=None:
        await radius.send(mess)
    
    await asyncio.sleep(1)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('.tps'):
        sname=''
        tps={}
        if message.content.split(" ")[1]=='1':
            sname="Survival"
            tps=json.loads(requests.get("https://api.reworlds.su/server/metrics?server=1").text)['last_entries']
        elif message.content.split(" ")[1]=="2":
            sname="Creative"
            tps=json.loads(requests.get("https://api.reworlds.su/server/metrics?server=2").text)['last_entries']
        else:
            await message.channel.send(f"{message.author.mention}, Ты меня тут не путай! Не знаю я такого сервера!")
        max=json.loads(requests.get("https://api.reworlds.su/server/metrics?server=1").text)['max_online']
        players=json.loads(requests.get("https://map.reworlds.su/tiles/players.json").text)
        online=0
        for player in players['players']:
            online+=1
        bc=0x00ff00
        if tps[0]['tps']<15:
            bc=0xffff00
        elif tps[0]['tps']<10:
            bc=0xff0000
        embedVar = discord.Embed(title="RevolutionWorlds TPS", description=f"Сервер {sname}, online {online}, Вызвано {message.author.mention}\n(онлайн) сколько сек назад\ntps", color=bc)
        tpsa="{:.2f}".format(tps[0]['tps'])
        embedVar.add_field(name=f"(`{tps[0]['online']}`) `{int(time.time()-tps[0]['time'])}`s", value=f"`{tpsa}`", inline=False)
        tpsb="{:.2f}".format(tps[1]['tps'])
        embedVar.add_field(name=f"(`{tps[1]['online']}`) `{int(time.time()-tps[1]['time'])}`s", value=f"`{tpsb}`", inline=False)
        tpsc="{:.2f}".format(tps[2]['tps'])
        embedVar.add_field(name=f"(`{tps[2]['online']}`) `{int(time.time()-tps[2]['time'])}`s", value=f"`{tpsc}`", inline=False)
        embedVar.set_thumbnail(url="https://raw.githubusercontent.com/ROBGUI09/ROBGUI09/main/b534c131aa930c76dc6d6fc4c41145b6.webp")
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".records"):
        resp=json.loads(requests.get("https://api.reworlds.su/server/metrics?server=1").text)
        embedVar = discord.Embed(title="Рекорды сервера", description=f"Сервер Survival, Вызвано {message.author.mention}", color=0x00ff00)
        tpsa="{:.2f}".format(resp['max_entry']['tps'])
        tpsb="{:.2f}".format(resp['max_day_entry']['tps'])
        embedVar.add_field(name=f"Рекорд онлайна", value=f"Онлайн: `{resp['max_entry']['online']}` TPS: `{tpsa}`", inline=False)
        embedVar.add_field(name=f"Рекорд онлайна за сегодня", value=f"Онлайн: `{resp['max_day_entry']['online']}` TPS: `{tpsb}`", inline=False)
        embedVar.set_thumbnail(url="https://raw.githubusercontent.com/ROBGUI09/ROBGUI09/main/b534c131aa930c76dc6d6fc4c41145b6.webp")
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".ping"):
        ip=message.content.split(" ")[1]
        server = MinecraftServer.lookup(ip)
        try:
            status = server.status()
        except:
            embedVar = discord.Embed(title=f"{ip} status", description=f"Ping: ∞, Вызвано {message.author.mention}", color=0xff0000)
            embedVar.add_field(name="Ошибка!", value=f"Сервер не существует", inline=False)
            await message.channel.send(embed=embedVar)
            return
        embedVar = discord.Embed(title=f"{ip} status", description=f"Ping: {status.latency}, Вызвано {message.author.mention}", color=0x00ff00)
        embedVar.add_field(name="MOTD", value=f"{status.description}", inline=False)
        cm=status.description.replace("§1","").replace("§2","").replace("§3","").replace("§4","").replace("§5","").replace("§6","").replace("§7","").replace("§8","").replace("§c","").replace("§e","").replace("§a","").replace("§b","").replace("§d","").replace("§f","").replace("§0","").replace("§m","").replace("§l","").replace("§o","").replace("§k","").replace("§r","").replace("§R","").replace("§L","").replace("§n","")
        embedVar.add_field(name="ClearMOTD", value=f"{cm}", inline=False)
        embedVar.add_field(name="Players", value=f"{status.players.online}", inline=False)
        try:
            embedVar.add_field(name="Query", value=f"{status.query}", inline=False)
        except:
            embedVar.add_field(name="Query", value=f"Cервер отключил query", inline=False)
        embedVar.set_thumbnail(url="https://raw.githubusercontent.com/ROBGUI09/ROBGUI09/main/b534c131aa930c76dc6d6fc4c41145b6.webp")
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".list"):
        resp=json.loads(requests.get("https://map.reworlds.su/tiles/players.json").text)
        pls=''
        for i in resp['players']:
            world=''
            yaw="{:.2f}".format(i['yaw'])
            if i['world']=="world":
                if i['x'] in range(-100,100) and i['z'] in range(-100,100):
                    world="<:spawn:880149491016138812>"
                else:
                    world="<:world:879849723618549831>"
            if i['world']=="world_nether":
                if i['x'] in range(-100,100) and i['z'] in range(-100,100):
                    world="<:nether_hub:880142881225080912>"
                elif i['x']>100 and i['z'] in range(-4,4):
                    world="<:black:880157605492838450>"
                else:
                    world="<:world_nether:879849392415342612>"
            if i['world']=="world_the_end":
                if i['x'] in range(-150,150) and i['z'] in range(-150,150):
                    world="<:end_main:880144288837664859>"
                elif i['x'] in range(1100-150,1100+150) and i['z'] in range(100-150,100+150):
                    world="<:tf:880143064998481941>"
                else:
                    world="<:world_the_end:879849539291471872>"
            pls+=f"`{i['name']}` {world} X: `{i['x']}` Z: `{i['z']}` Yaw: `{yaw}`\n"
            if len(pls)>1900:
                await message.channel.send(pls)
                pls=''
        await message.channel.send(pls)
    if message.content.startswith(".player"):
        fm=''
        if message.content.split(" ")[1]=="robert300" or message.content.split(" ")[1]=="robert300_AFK" or message.content.split(" ")[1]=="robert300_AFK2":
            fm="не тычьте в моего хозяина пазезе\n"
        resp=json.loads(requests.get("https://map.reworlds.su/tiles/players.json").text)
        tpl={}
        for player in resp['players']:
            if player['name']==message.content.split(" ")[1]:
                tpl=player
                break
        if tpl=={}:
            embedVar = discord.Embed(title=f"Ошибка", description=f"Вызвана {message.author.mention}", color=0xff0000)
            embedVar.add_field(name=f"А ты уверен что он онлайн?", value="Юзай .oplayer пжлст", inline=False)
            embedVar.set_footer(text="ДОНАТЕРЫ МОГУТ СКРЫТЬСЯ\nбывают баги с тем что простые игроки тоже не видны\nсделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
            await message.channel.send(embed=embedVar)
            return
        embedVar = discord.Embed(title=f"Данные о {tpl['name']}", description=f"{fm}Координаты игрока:", color=0x00ff00)
        embedVar.add_field(name=f"Мир: `{tpl['world']}`", value=f"X: `{tpl['x']}`, Z: `{tpl['z']}` Yaw: `{tpl['yaw']}`", inline=False)
        embedVar.set_thumbnail(url="https://raw.githubusercontent.com/ROBGUI09/ROBGUI09/main/b534c131aa930c76dc6d6fc4c41145b6.webp")
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".oplayer"):
        fm=''
        if message.content.split(" ")[1]=="robert300" or message.content.split(" ")[1]=="robert300_AFK" or message.content.split(" ")[1]=="robert300_AFK2":
            fm="не тычьте в моего хозяина пазезе\n"
        msg=message.content.split(" ")
        try:
            resp=open(f"oplayers/{msg[1]}.dat","r").readlines()
        except:
            await message.channel.send("я хз о ком ты говоришь")
            return
        rep=json.loads(requests.get("https://map.reworlds.su/tiles/players.json").text)
        for player in rep['players']:
            if player['name']==message.content.split(" ")[1]:
                await message.channel.send("Игрок онлайн!")
                return
        x=resp[1].rstrip("\n")
        z=resp[3].rstrip("\n")
        i={"world":resp[0].rstrip("\n")}
        try:
            yaw="{:.2f}".format(float(resp[4]))
        except IndexError:
            yaw="???"
        world=''
        if i['world']=="world":
            if x in range(-100,100) and z in range(-100,100):
                world="<:spawn:880149491016138812>"
            else:
                world="<:world:879849723618549831>"
        if i['world']=="world_nether":
            if x in range(-100,100) and z in range(-100,100):
                world="<:nether_hub:880142881225080912>"
            elif x>100 and z in range(-4,4):
                world="<:black:880157605492838450>"
            else:
                world="<:world_nether:879849392415342612>"
            if i['world']=="world_the_end":
                if x in range(-150,150) and z in range(-150,150):
                    world="<:end_main:880144288837664859>"
                elif x in range(1100-150,1100+150) and z in range(100-150,100+150):
                    world="<:tf:88014306499841941>"
                else:
                    world="<:world_the_end:879849539291471872>"            
        name=message.content.split(" ")[1]
        embedVar = discord.Embed(title=f"Данные о {name}", description=f"{fm}Вызвано {message.author.mention}, Координаты игрока:", color=0x00ff00)
        embedVar.add_field(name=f"Мир: {world}", value=f"X: `{x}`, Z: `{z}` Yaw: `{yaw}`", inline=False)
        embedVar.set_thumbnail(url="https://raw.githubusercontent.com/ROBGUI09/ROBGUI09/main/b534c131aa930c76dc6d6fc4c41145b6.webp")
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".emoji"):
        print(message.content)
    if message.content.startswith(".help"):
        embedVar = discord.Embed(title=f"Команды", description=f"Команды бота, Вызвано {message.author.mention}", color=0x00ff00)
        embedVar.add_field(name=f".help", value=f"Вывести этот список", inline=False)
        embedVar.add_field(name=f".oplayer (игрок)", value=f"Получить место выхода игрока на сервере*", inline=False)
        embedVar.add_field(name=f".player (игрок)", value=f"Получить местоположение игрока на сервере*", inline=False)
        embedVar.add_field(name=f".list", value=f"Список игроков сервера*", inline=False)
        embedVar.add_field(name=f".ping (сервер)", value=f"Получить данные о сервере", inline=False)
        embedVar.add_field(name=f".records", value=f"Рекорды сервера*", inline=False)
        embedVar.add_field(name=f".tps 1(выживание)|2(креатив)", value=f"TPS сервера*", inline=False)
        embedVar.set_footer(text="сделано на коленке за 3 часа ночи\nбез любви - ROBGUI#3137\n* Подразумевает сервер RewolutionWorlds")
        await message.channel.send(embed=embedVar)
    if message.content.startswith(".map"):
        data=getmap(message)
        if data['err']:
            await message.channel.send(f"Ошибка! Код ошибки:`{data['code']}`. Сообщите об этом ROBGUI#3137")
        elif data['offline']:
            await message.channek.send("ищу приведений игроков")
        else:
            await message.channel.send(content=data['text'],file=data['file'])
        
client.loop.create_task(radcord(client))
client.run('ODc5NzgxNjgzOTA0MjYyMjA1.YSUuig.aq9yOxW0vu_LYHGbqBE5ptg-8xI')



