
import discord
import asyncio
from threading import Thread
from discord.ext import commands
import ba
from ba._general import Call
import _ba
import json
import os
import _thread
import logging
logging.getLogger('asyncio').setLevel(logging.WARNING)
client = commands.Bot(command_prefix=['Bs.','bs.'], case_insensitive = True)


token = ''
roleid = [] #copy discord role id which have permission to use the commands

#Logging

stats = {}
pl = {}
logs= []


def push_log(msg):
    global logs
    logs.append(msg)
    get_logs()

def init():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(token))
    
    Thread(target=loop.run_forever).start()


@client.event
async def on_message(message):
    global channel
    if message.author == client.user:
        return
    channel=message.channel
    
    if message.channel.id==logsChannelID:
        _ba.pushcall(Call(_ba.chatmessage,message.content),from_other_thread=True)


@client.event
async def on_ready():
    print("Discord bot logged in as: %s, %s" % (client.user.name, client.user.id))

#Live Players
@client.command()
async def lobby(ctx):
    await ctx.send("Getting Lobby Players.....")
	await asyncio.sleep(1)
    lbby = get_live_players
    embed = discord.Embed(title ="Lobby Players", description = lbby, color = ctx.author.color)
	embed.set_footer(text = f"Made By ItsBlitz")
    await ctx.send(embed = embed)

@client.command()
@commands.has_role(i for i in roleid)
async def live(ctx):
	lbby = get_live_players()
	embed = discord.Embed(title ="Live Status", description = lbby, color = ctx.author.color)
	embed.set_footer(text = f"Made By ItsBlitz")
	msg = await ctx.send(embed = embed)
	while True:
		await asyncio.sleep(8)
		lbb = get_live_players()
		emd = discord.Embed(title ="Live Status", description = lbb, color = ctx.author.color)
		emd.set_footer(text = f"Made By ItsBlitz")
		await msg.edit(embed = emd)


@client.command()
@commands.has_role()
async def livechats(ctx):
	lbby = get_chats()
	embed = discord.Embed(title ="Live Chats", description = lbby, color = ctx.author.color)
	embed.set_footer(text = f"Made By ItsBlitz")
	msg = await ctx.send(embed = embed)
	while True:
		await asyncio.sleep(8)
		lbb = get_chats()
		emd = discord.Embed(title ="Live Chats", description = lbb, color = ctx.author.color)
		emd.set_footer(text = f"Made By ItsBlitz")
		await msg.edit(embed = emd)

@client.command()
@commands.has_role()
async def logs(ctx):
	lbby = get_logs().split("|")
	embed = discord.Embed(title =lbby[0], description = lbby[1], color = ctx.author.color)
	embed.set_footer(text = f"Made By ItsBlitz")
	await ctx.send(embed = embed)
	while True:
		await asyncio.sleep(3)
		lbb = get_logs().split("|")
		emd = discord.Embed(title =lbb[0], description = lbb[1], color = ctx.author.color)
		emd.set_footer(text = f"Made By ItsBlitz")
		await ctx.send(embed = emd)

def get_live_players():
    global stats
    livep = stats['live']
    return livep
    
def get_game():
    global stats
    liveg = stats['game']
    return liveg

def get_chats():
    global stats
    livec = stats['chats']
    while len(livec) > 15:
        for i in range(len(livec)-15):
            livec.pop(0)
    return livec

def get_logs():
    global logs
    log = logs[0]
    logs.pop[0]
    return log

def emd_maker(title,desc,color):
    embed = discord.Embed(title =title, description = desc, color = color)
	embed.set_footer(text = f"Made By ItsBlitz")
    return embed

class BsDataThread(object):
    def __init__(self):
        self.refreshStats()
        self.Timer = ba.Timer( 8,ba.Call(self.refreshStats),repeat = True)
        # self.Timerr = ba.Timer( 10,ba.Call(self.refreshLeaderboard),timetype = ba.TimeType.REAL,repeat = True)
        
    # def refreshLeaderboard(self):
    #     global leaderboard
    #     global top200
    #     _t200={}
    #     f=open(statsfile)
    #     lboard=json.loads(f.read())
    #     leaderboard=lboard
    #     entries = [(a['scores'], a['kills'], a['deaths'], a['games'], a['name_html'], a['aid'],a['last_seen']) for a in lboard.values()]
        
    #     entries.sort(reverse=True)
    #     rank=0
    #     for entry in entries:
    #         rank+=1
    #         if rank >201:
    #             break
    #         _t200[entry[5]]={"rank":rank,"scores":int(entry[0]),"games":int(entry[3]),"kills":int(entry[1]),"deaths":int(entry[2]),"name_html":entry[4],"last_seen":entry[6]}
    #         top200=_t200
            
    def refreshStats(self):
        
        nextMap=''
        currentMap=''
        global stats,pl
        liveplayers = u"{0:^16}{1:^15}{2:^10}\n--------------------------------------------------\n".format('Name','ClientID','PlayerID')
	    lname = None
	    lcid = None
	    lpid = None
        for i in _ba.get_game_roster():
            if i['players'] == []:
                lname = str(i['display_string'])
                lcid = str(i['client_id'])
                lpid = str('In Lobby')
                pl[lname] = [lcid,lpid]
                liveplayers += u"{0:^16}{1:^15}{2:^10}\n".format(lname, lcid, lpid)
            else:
                for lp in i['players']:
                    lname = lp['name_full']
                    lcid = i['client_id']
                    lpid = lp['id']
                    liveplayers += u"{0:^16}{1:^15}{2:^10}\n".format(lname, lcid, lpid)
                    pl[lname] = [lcid,lpid]
        try:    
            nextMap=_ba.get_foreground_host_session().get_next_game_description().evaluate()

            current_game_spec=_ba.get_foreground_host_session()._current_game_spec
            gametype: Type[GameActivity] =current_game_spec['resolved_type']
            
            currentMap=gametype.get_settings_display_string(current_game_spec).evaluate()
        except:
            pass
        minigame={'Current':currentMap,'Next':nextMap}
        # system={'cpu':p.cpu_percent(),'ram':p.virtual_memory().percent}
        #system={'cpu':80,'ram':34}
        # stats['system']=system
        stats['live']="#"+liveplayers
        stats['chats']=_ba.get_chat_messages()
        stats['game']=minigame

        
        # stats['teamInfo']=self.getTeamInfo()

