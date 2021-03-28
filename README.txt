To run this, simply cd into this directory and run ./ballisticacore_server
(on mac or linux) or launch_ballisticacore_server.bat (on windows).
You'll need to open a UDP port (43210 by default) so that the world can
communicate with your server.
You can configure your server by editing the config.yaml file.
(if you only see config_template.yaml, you can copy/rename that to config.yaml)

-Add your account-id in dist/ba_root/mods/privateserver.py  -> admin[]
-Restart server twice 
-Add players account-id (pb-id)  in whitelist.json manually or use chat command while whitelist is off.
-Use "/whitelist"   to turn on/off whitelist.
-Use "/spectators"   to turn on/off lobby kick.
-Use "/add <client-id>"  to whitelist player (turn off whitelist or spectators mode first).
-In config.yaml set party type to PUBLIC ; party will be PRIVATE automatically by smoothy haxx
-Increased Kickvote cooldown 
-Kickvote logs with be logged in terminal (who kicking whom).
-player joined the party/player left the party message removed 
 