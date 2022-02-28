
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
import setting
logging.getLogger('asyncio').setLevel(logging.WARNING)
client = commands.Bot(command_prefix=['Bs.','bs.'], case_insensitive = True)

#Dont Change Anything(Head To Settings.json)
token = ''
roleid = "" #copy discord role id which have permission to use the commands
liveStatsChannelID = ""
logsChannelID = ""
liveChat = True

#Logging

stats = {}
pl = {}
logs= []


def push_log(msg):
    global logs
    logs.append(msg)

def init():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(token))
    
    Thread(target=loop.run_forever).start()

async def automatic():
    await client.wait_until_ready()
    while not client.is_closed():
        chnl = client.get_channel(liveStatsChannelID)
        msgs = await chnl.history(limit=5).flatten()
        for i in msgs:
            if i.author.id == client.user.id:
                idd = i.id
                msg = await chnl.fetch_message(idd)
                await msg.delete()

        new_msg1 = await chnl.send("Getting Stats........")
        new_msg2 = await chnl.send("Getting Game.........")
        new_msg3 = await chnl.send("Getting Chats........")

        lby = get_live_players()
        embed = discord.Embed(title ="Lobby Players", description = lby, color = discord.Colour.random())
	    embed.set_footer(text = f"Enjoy In Our Server")
        await new_msg1.edit(content = None,embed = embed)
        await new_msg2.edit(content = get_game())
        await new_msg3.edit(content = "```\n"+get_chats()+"\n```")
        await asyncio.sleep(8)

async def livelog():
    await client.wait_until_ready()
    while not client.is_closed():
        chnl = client.get_channel(logsChannelID)
        lby = get_logs().split("|")
        embed = discord.Embed(title =lby[0], description = lby[1], color = discord.Colour.random())
	    embed.set_footer(text = f"Server Logs")
        await chnl.send(embed = embed)
        await asyncio.sleep(9)

client.loop.create_task(automatic())
client.loop.create_task(livelog())

@client.event
async def on_ready():
    print("Discord bot logged in as: %s, %s" % (client.user.name, client.user.id))

#Live Players
@client.command()
async def lobby(ctx):
    await ctx.send("Getting Lobby Players.....")
	await asyncio.sleep(1)
    lbby = get_live_players()
    embed = discord.Embed(title ="Lobby Players", description = lbby, color = ctx.author.color)
	embed.set_footer(text = f"Requested By {ctx.author.name}")
    await ctx.send(embed = embed)

@client.command()
@commands.has_role(roleid)
async def statsid(ctx, chnl:discord.TextChannel):
    try:
        c_id = chnl.id
        setting.commit({"logsChannelID":c_id})
        await ctx.send("Logs Channel Updated")
    except:
        await ctx.send("Mention Channel Correctly")

@client.command()
@commands.has_role(roleid)
async def logsid(ctx, chnl:discord.TextChannel):
    try:
        c_id = chnl.id
        setting.commit({"logsChannelID":c_id})
        await ctx.send("Logs Channel Updated")
    except:
        await ctx.send("Mention Channel Correctly")

@client.command()
@commands.has_role(roleid)
async def roleid(ctx, role:discord.Role):
    try:
        r_id = role.id
        setting.commit({"roleID":r_id})
        await ctx.send("Role Updated")
    except:
        await ctx.send("Mention Role Correctly")

#Messaging
@client.command()
async def chatmsg(ctx,*,msg:str):
	if not msg.startswith("/"):
        _ba.pushcall(Call(_ba.chatmessage,msg),from_other_thread=True)
        await ctx.send("Message Delivered")
    else:
        await ctx.send("Error 404")


@client.command()
@commands.has_role(roleid)
async def cmd(ctx,*,msg:str):
	if msg.startswith("/"):
        _ba.pushcall(Call(_ba.chatmessage,msg),from_other_thread=True)
        await ctx.send("Command Executed")
    else:
        await ctx.send("Error 404")

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
    msg = ""
    for mg in livec:
        msg += mg + "\n"
    return msg
def get_logs():
    global logs
    log = logs[0]
    logs.pop[0]
    return log


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

