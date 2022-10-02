# Bombsquad-Ballistica-Modded-Server

Modder server scripts to host ballistica (Bombsquad).Running on BS1.7.10.

## Requirements
- Ubuntu 20 and above
- python3.10

## Getting Started
- `sudo apt update; sudo apt install python3-pip python3.10-dev python3.10-venv` , or [Python3.10 on Ubuntu 20.04](https://computingforgeeks.com/how-to-install-python-on-ubuntu-linux-system/)
- `tmux new -s 43210`
- `git clone https://github.com/imayushsaini/Bombsquad-Ballistica-Modded-Server`
- `cd Bombsquad-Ballistica-Modded-Server`
- Now edit config.yaml in root dir change server name , port , admins , playlist , team name etc..
- `chmod 777 bombsquad_server`
- `chmod 777 dist/bombsquad_headless`
- `./bombsquad_server`
- If ports are open , you can connect to your server now

## More Configuration
Open dist/ba_root/mods/setting.json , change value according to you.

### adding yourself owner
- open dist/ba_root/mods/playersData/roles.json
- add your pb-id in owner id list
- restart your server

### managing players
open dist/ba_root/mods/playersData/profiles.json . 
Here you can ban player , mute them , disable their kick votes 


## Features
- Rank System.
- Chat commands.
- V2 Account with cloud console for server.
- Easy role management , create 1000 of roles as you wish add specific chat command to the role , give tag to role ..many more.
- Rejoin cooldown.
- Leaderboard , top 3 rank players name on top right corner.
- Restrict some player to start kick vote.
- Auto night mode .
- Transparent Kickvote , can see who started kick vote for whom.
- Kickvote msg to chat/screen , can choose to show kickvote start msg either as screen message or chat message.
- Players IP Address and Device UUID tracking and banning.
- Team Chat, send msg starting with (,) comma to deliver it to team mates only.
- In game popup chat , send msg starting with (.) Dot to send in game popup msg.
- End Vote System , type `end` in chat to start end vote.
- support for [Ballisitca-web-stats](https://github.com/imayushsaini/ballistica-web-stats).
- Integrated Discord bot to sync live stats(current players, chats , all logs) to discord.
- Execute chat command remotely from discord.
- Many New mini games and maps.
- Colourfull bomb explosion.
- Floater
- Auto stats reset after configured days .
- Auto remove afk/idle players.
- Auto check server updates.
- All settings at one place ,no coding exp. required just edit settings.json 
- Configurable Server Host name.
- Character chooser , players can choose any character while joining .
- Restrict New accounts to join or chat in server.
- Custom characters , easy to load and use characters made by character maker.
- Auto Team Balance , player shift to small team in dualteam mode.
- Integrated ElPatronPowerups.
- Auto switch to coop mode when players are less then threshold.
- Change playlist on fly with playlist code or name , i.e /playlist teams , /playlist coop , /playlist 34532
- rotate prop nodes with node.changerotation(x,y,z)
- set 2d mode with _ba.set_2d_mode(true)
- set 2d plane with _ba.set_2d_plane(z) - beta , not works with spaz.fly = true. 
- New Splitted Team in game score screen.
- New final score screen , StumbledScoreScreen.
- other small small feature improvement here there find yourself.
