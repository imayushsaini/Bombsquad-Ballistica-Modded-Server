# Bombsquad-Ballistica-Modded-Server

Modder server scripts to host ballistica (Bombsquad).Running on BS1.6.6.

## Requirements
- Ubuntu 20
- python3.9 

## Getting Started
- `sudo apt update; sudo apt install python3.9-dev`
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
- Easy role management , create 1000 of roles as you wish add specific chat command to the role , give tag to role ..many more.
- Rejoin cooldown.
- Leaderboard , top 3 rank players name on top right corner.
- Restrict some player to start kick vote.
- Auto night mode .
- Transparent Kickvote , can see who started kick vote for whom.
- Kickvote msg to chat/screen , can choose to show kickvote start msg either as screen message or chat message
- All settings at one place ,no coding exp. required just edit settings.json 
- Configurable Server Host name
- Character chooser , players can choose any character while joining .
- Restrict New accounts to join or chat in server.
- Custom characters , easy to load and use characters made by character maker.
- Auto Team Balance , player shift to small team in dualteam mode.
- Integrated ElPatronPowerups.
- Auto switch to coop mode when players are less then threshold.
- Change playlist on fly with playlist code or name , i.e /playlist teams , /playlist coop , /playlist 34532
- New Splitted Team score screen. 
- other small small feature improvement here there find yourself.
