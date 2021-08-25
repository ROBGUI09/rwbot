import os
import requests
import time
from datetime import datetime
import json
from math import floor
import math
lttts=0
def get_updates():
    global lttts
    out=''
    try:
        resp=json.loads(requests.get("https://map.reworlds.su/tiles/players.json",timeout=5).text)
    except:
        return "Ошибка! Время: "+str(time.time())
    lp=0
    plcount=0
    playyers=''
    for player in resp['players']:
        t=open(f"oplayers/{player['name']}.dat","w")
        t.write(f"{player['world']}\n{player['x']}\nidk\n{player['z']}\n{player['yaw']}")
        t.close()
        plcount+=1
        playyers+=f"{player['name']}\n"
    os.system('clear')
    out+=f"Игроков: {plcount}\nИгроки: {playyers}"
    return out

while 1:
    updates=get_updates()
    log=open("chatlog.txt","a")
    log.write(updates)
    log.close()
    if updates != '':
        print(updates.rstrip("\n"))
