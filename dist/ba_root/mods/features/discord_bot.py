
import discord
import asyncio
from threading import Thread
from discord.ext.commands import Bot
import ba
from ba._general import Call
import _ba
import ba.internal
import json
import os
import _thread
import logging
logging.getLogger('asyncio').setLevel(logging.WARNING)
client = Bot(command_prefix='!')

# client = discord.Client()


stats={}
livestatsmsgs=[]
logsChannelID=859519868838608970
liveStatsChannelID=924697770554687548
liveChat=True
token=''
logs=[]


def push_log(msg):
    global logs
    logs.append(msg)

def init():
    

    
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(token))
    
    Thread(target=loop.run_forever).start()

channel=None
@client.event
async def on_message(message):
    global channel
    if message.author == client.user:
        return
    channel=message.channel
    
    if message.channel.id==logsChannelID:
        _ba.pushcall(Call(ba.internal.chatmessage,message.content),from_other_thread=True)


@client.event
async def on_ready():
    print("Discord bot logged in as: %s, %s" % (client.user.name, client.user.id))
    
    await verify_channel()

async def verify_channel():
    global livestatsmsgs
    channel=client.get_channel(liveStatsChannelID)
    botmsg_count=0
    msgs = await channel.history(limit=5).flatten()
    for msg in msgs:
        if msg.author.id==client.user.id:
            botmsg_count+=1
            livestatsmsgs.append(msg)

    livestatsmsgs.reverse()
    while(botmsg_count<2):
        new_msg=await channel.send("msg reserved for live stats")
        livestatsmsgs.append(new_msg)
        botmsg_count+=1
    asyncio.run_coroutine_threadsafe(refresh_stats(),client.loop)
    asyncio.run_coroutine_threadsafe(send_logs(),client.loop)
    # client.loop.create_task(refresh_stats())
    # client.loop.create_task(send_logs())

async def refresh_stats():
    await client.wait_until_ready()

    while not client.is_closed():
        
        await livestatsmsgs[0].edit(content=get_live_players_msg())
        await livestatsmsgs[1].edit(content=get_chats())
        await asyncio.sleep(5)

async def send_logs():
    global logs
    #  safely dispatch logs to dc channel , without being rate limited and getting ban from discord
    # still we sending 2 msg and updating 2 msg within 5 seconds , umm still risky ...nvm not my problem
    channel=client.get_channel(logsChannelID)
    await client.wait_until_ready()
    while not client.is_closed():
        if logs:
            msg=''
            for msg_ in logs:
                msg+=msg_+"\n"
            logs=[]
            if msg:
                await channel.send(msg)

        await asyncio.sleep(5)



def get_live_players_msg():
    global stats
    msg_1='***Live Stats :***\n\n ***Players in server***\n\n'
    msg=''
    try:
        for id in stats['roster']:
            name=stats['roster'][id]['name']
            device_id=stats['roster'][id]['device_id']
            msg+=id +" -> "+name+" -> "+device_id+" \n"
    except:
        pass
    if not msg:
        msg="```No one``` \n"
    msg_2="\n\n***Current: *** "+stats['playlist']['current'] +"\n ***Next: ***"+stats['playlist']['next'] +"\n\n."
    return msg_1+msg+msg_2

def get_chats():
    msg_1='***Live Chat***\n\n'
    msg=''
    try:
        for msg_ in stats['chats']:
            msg+=msg_+"\n"
    except:
        pass
    if not msg:
        msg= "```Empty```\n"
    if not liveChat:
        return '```disabled```'
    return msg_1+msg




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
        
        liveplayers={}
        nextMap=''
        currentMap=''
        global stats
        
        for i in ba.internal.get_game_roster():
            try:
                liveplayers[i['account_id']]={'name':i['players'][0]['name_full'],'client_id':i['client_id'],'device_id':i['display_string']}
            except:
                liveplayers[i['account_id']]={'name':"<in-lobby>",'clientid':i['client_id'],'device_id':i['display_string']}
        try:    
            nextMap=ba.internal.get_foreground_host_session().get_next_game_description().evaluate()

            current_game_spec=ba.internal.get_foreground_host_session()._current_game_spec
            gametype: Type[GameActivity] =current_game_spec['resolved_type']
            
            currentMap=gametype.get_settings_display_string(current_game_spec).evaluate()
        except:
            pass
        minigame={'current':currentMap,'next':nextMap}
        # system={'cpu':p.cpu_percent(),'ram':p.virtual_memory().percent}
        #system={'cpu':80,'ram':34}
        # stats['system']=system
        stats['roster']=liveplayers
        stats['chats']=ba.internal.get_chat_messages()
        stats['playlist']=minigame

        
        # stats['teamInfo']=self.getTeamInfo()

