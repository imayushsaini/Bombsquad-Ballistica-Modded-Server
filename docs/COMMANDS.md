# Server Chat Commands Documentation

> Auto-generated command list from Python server source code.

## Cheats Commands

| Command | Usage | Aliases | Cost | Description |
| --- | --- | --- | --- | --- |
| `/kill` | `/kill [all | <player_index>]` | `/die` | Free | Kill target player(s) immediately in game. |
| `/heal` | `/heal [all | <player_index>]` | `/heath` | Free | Heal target player(s) to full health. |
| `/curse` | `/curse [all | <player_index>]` | `/cur` | Free | Curse target player(s) causing them to explode after a short delay. |
| `/sleep` | `/sleep [all | <player_index>]` | - | Free | Knockout target player(s) for 8 seconds. |
| `/superpunch` | `/superpunch [all | <player_index>]` | `/sp` | Free | Toggle super punch (15x damage and 0 cooldown) for target player(s). |
| `/gloves` | `/gloves [all | <player_index>]` | `/punch` | Free | Give boxing gloves powerup to target player(s). |
| `/shield` | `/shield [all | <player_index>]` | `/protect` | Free | Give energy shield powerup to target player(s). |
| `/freeze` | `/freeze [all | <player_index>]` | `/ice` | Free | Freeze target player(s) in ice. |
| `/unfreeze` | `/unfreeze [all | <player_index>]` | `/thaw` | Free | Unfreeze target player(s) from ice. |
| `/godmode` | `/godmode [all | <player_index>]` | `/gm` | Free | Toggle invincibility and god mode for target player(s). |
| `/givetickets` | `/givetickets <client_id|player_index|name> <amount>` | `/addtickets` | Free | Grant tickets balance to a player by client ID, player index, or name substring (admin only). |


## Fun Commands

| Command | Usage | Aliases | Cost | Description |
| --- | --- | --- | --- | --- |
| `/speed` | `/speed <multiplier>` | - | 🎟️ 200 | Set the game simulation speed multiplier. |
| `/fly` | `/fly [all | <player_index>]` | - | 🎟️ 300 | Toggle flight mode allowing target player(s) to float in the air. |
| `/invisible` | `/invisible [all | <player_index>]` | `/inv` | 🎟️ 250 | Make target player(s) character meshes invisible. |
| `/headless` | `/headless [all | <player_index>]` | `/hl` | 🎟️ 150 | Remove head mesh from target player(s). |
| `/creepy` | `/creepy [all | <player_index>]` | `/creep` | 🎟️ 150 | Make target player(s) creepy (remove head, add punch and shield powerups). |
| `/celebrate` | `/celebrate [all | <player_index>]` | `/celeb` | 🎟️ 100 | Make target player(s) perform a victory dance animation. |
| `/spaz` | `/spaz` | - | Free | Spaz command placeholder. |
| `/floater` | `/floater [<client_id>]` | `/flo` | 🎟️ 200 | Assign floater controls to yourself or a specific client ID. |
| `/tnt` | `/tnt [all | <player_index>]` | `/spawntnt`, `/spawn` | 🎟️ 200 | Spawn a TNT crate at target player position or arena center. |


## Manage Commands

| Command | Usage | Aliases | Cost | Description |
| --- | --- | --- | --- | --- |
| `/unban` | `/unban <client_id>` | - | Free | Unban a player by client ID from recent connections log. |
| `/recents` | `/recents` | - | Free | List recent connected players with client ID, device ID, and account ID (pbid). |
| `/info` | `/info <client_id>` | - | Free | Get detailed account information for a connected or recent player by client ID. |
| `/maxplayers` | `/maxplayers <number>` | `/max` | Free | Change the maximum public party player slots. |
| `/createteam` | `/createteam <team_name>` | - | Free | Create a new custom team in the current session. |
| `/playlist` | `/playlist <playlist_name|coop>` | - | Free | Switch the server playlist by name or code, or switch to coop mode. |
| `/kick` | `/kick <client_id>` | - | Free | Kick a player immediately by client ID. |
| `/ban` | `/ban <client_id> [duration_in_days]` | - | Free | Ban a player by client ID for a duration (in days) and disconnect them. |
| `/end` | `/end` | `/next` | Free | End the current match or activity immediately and proceed to next. |
| `/kickvote` | `/kickvote <enable|disable|immune|unimmune|list> [target] [duration]` | - | Free | Manage kick voting settings, player restrictions, and immunities. |
| `/kickimmune` | `/kickimmune <client_id | pb-id>` | `/immune` | Free | Grant kick vote immunity to a player by client ID or account ID (pb-id). |
| `/kickunimmune` | `/kickunimmune <client_id | pb-id>` | `/unimmune` | Free | Remove kick vote immunity from a player. |
| `/disablekickvote` | `/disablekickvote <client_id | pb-id> [duration_days]` | `/dkv` | Free | Restrict a player from starting kick votes for specified days. |
| `/enablekickvote` | `/enablekickvote <client_id | pb-id>` | `/ekv` | Free | Allow a player to start kick votes again by removing restriction. |
| `/hideid` | `/hideid` | - | Free | Hide player device IDs from the party list. |
| `/showid` | `/showid` | - | Free | Show player device IDs in the party list. |
| `/lm` | `/lm` | - | Free | Send last chat messages to your client console/chat. |
| `/gp` | `/gp <player_index>` | - | Free | Get player profiles by player ID index. |
| `/party` | `/party <public | private>` | - | Free | Set server party visibility to public or private. |
| `/quit` | `/quit` | `/restart` | Free | Quit or restart the server host application. |
| `/mute` | `/mute [<client_id>] [duration_days]` | `/mutechat` | Free | Mute global server chat or a specific client ID for a duration in days. |
| `/unmute` | `/unmute [<client_id>]` | `/unmutechat` | Free | Unmute global chat or a specific client ID. |
| `/remove` | `/remove <client_id | all>` | `/rm` | Free | Remove a player from the active game session. |
| `/sm` | `/slowmo` | `/slow`, `/slowmo` | Free | Toggle game global slow motion speed mode. |
| `/nv` | `/nv` | - | Free | Toggle blue night vision ambient color filter for the host map. |
| `/dv` | `/dv` | - | Free | Set map ambient tint to standard daylight tint (1, 1, 1). |
| `/tint` | `/tint <r> <g> <b>` | - | Free | Set custom RGB tint multiplier for map globals node. |
| `/pause` | `/pause` | `/pausegame` | Free | Toggle match pause state. |
| `/cameraMode` | `/cameramode` | `/camera_mode`, `/rotate_camera` | Free | Toggle map camera mode between rotate and normal. |
| `/createrole` | `/createrole <role_name>` | - | Free | Create a new role rank in player database. |
| `/addrole` | `/addrole <role_name> <client_id>` | - | Free | Assign a role to a player by client ID. |
| `/removerole` | `/removerole <role_name> <client_id>` | - | Free | Remove a role from a player by client ID. |
| `/getroles` | `/getroles <client_id>` | - | Free | Get list of assigned roles for a player by client ID. |
| `/changetag` | `/changetag <role_name> <tag_text>` | - | Free | Change role display tag. |
| `/customtag` | `/customtag <tag_text> <client_id>` | - | Free | Set custom overhead tag for a player by client ID. |
| `/customeffect` | `/customeffect <effect_name> <client_id>` | `/addeffect`, `/gifteffect` | Free | Gift a custom spaz particle effect permanently to a player. |
| `/removetag` | `/removetag <client_id>` | - | Free | Remove custom overhead tag from a player by client ID. |
| `/removeeffect` | `/removeeffect <client_id> [effect_name]` | - | Free | Remove custom effect(s) from a player by client ID. |
| `/addcommand` | `/addcommand <command_name> <role_name>` | `/addcmd` | Free | Grant access to a command for a role. |
| `/removecommand` | `/removecommand <command_name> <role_name>` | `/removecmd` | Free | Revoke access to a command from a role. |
| `/spectators` | `/spectators <on | off>` | - | Free | Enable or disable whitelist spectator permissions. |
| `/lobbytime` | `/lobbytime <seconds>` | - | Free | Change lobby timeout check duration in seconds. |


## Normal Commands

| Command | Usage | Aliases | Cost | Description |
| --- | --- | --- | --- | --- |
| `/me` | `/me` | `/stats`, `/score`, `/rank`, `/myself` | Free | Fetch and send personal stats including scores, games, kills, deaths, and average. |
| `/list` | `/list` | `/l` | Free | Returns the list of online players with their client ID and player index. |
| `/uniqeid` | `/id [player_index]` | `/id`, `/pb-id`, `/pb`, `/accountid` | Free | Returns your account ID or the account ID of a specified player index. |
| `/ping` | `/ping [all | <client_id>]` | - | Free | Get ping for yourself, all players, or a specific client ID. |
| `/tickets` | `/balance` | `/balance` | Free | Check your total tickets balance. |
| `/transfer` | `/transfer <client_id|player_index|name> <amount>` | `/pay` | Free | Transfer tickets to another player by client ID, player index, or name substring. |
| `/shop` | `/shop [commands | effects]` | - | Free | View items, commands, and effects available for purchase in the server shop. |
| `/buy` | `/buy <item_name>` | - | Free | Purchase a chat command or spaz effect from the shop using your tickets balance. |
| `/effect` | `/effect [list | enable <effect_name> | disable <effect_name> | none]` | `/effects` | Free | Manage your active character particle effects inventory and equip/unequip effects. |
| `/equip` | `/equip <effect_name | none>` | `/use` | Free | Equip a specific character particle effect from your inventory. |
| `/unequip` | `/unequip <effect_name | all>` | - | Free | Unequip a character particle effect or remove all active effects. |
| `/claim` | `/claim` | `/daily` | Free | Claim your free daily login ticket reward. |
| `/hud` | `/hud [all | clean | leaderboard | next | notags | onlytags | <element> <on|off>]` | `/ui` | Free | Configure custom private HUD element visibility preferences and UI preset modes. |
| `/night` | `/night` | - | Free | Enable night mode lighting tint (0.5, 0.7, 1.0) for your client view. |
| `/day` | `/day` | - | Free | Enable standard daylight lighting tint (1.0, 1.0, 1.0) for your client view. |

