# Ballistica Linux 1.6 Server build
A working BombSquad/Ballistica 1.6 server build for Linux Ubuntu v20
***
# SERVER SETUP INSTRUCTIONS
Follow the below steps after creating an EC2 Linux v20 AWS instance:
***
    #(1) After Creating an Ec2 instance in AWS, it should be Online, now execute the following command in SSH terminal:
        - sudo apt update && sudo apt dist-upgrade && sudo apt install python3-pip libopenal-dev libsdl2-dev libvorbis-dev cmake clang-format
 
    #(2) Now clone the 1.6 server build from github using, 
        - git clone https://github.com/imayushsaini/Bombsquad-Ballistica-Modded-Server.git
    #(or) with ssh:
        - git clone git@github.com:imayushsaini/Bombsquad-Ballistica-Modded-Server.git

    #(3) To get the Test branch, execute the followin:
        - cd Bombsquad-Ballistica-Modded-Server
        - git checkout test
 
    #(4) Now we are ready to go, But we have to configure the settings and add admins/owners, Edit the following, 
        # - Edit server name , size , port , admin in 'config.yaml' (Bombsquad-Ballistica-Modded-Server/config.yaml).
        # - Add pb-id in whitelist at 'whitelist.json' (Bombsquad-Ballistica-Modded-Server/dist/ba_root/tools/whitelist.json).
        # - Add owner/admin id in 'roles.json' (Bombsquad-Ballistica-Modded-Server/dist/ba_root/players data/roles.json) under owner role "ids". 
        # - Edit TeamNames, Teamscolors in '_multiteamsession.py' (/dist/ba_data/python/ba/_multiteamsession.py).
 
    #(5) Now get back to ssh terminal and execute the following cmds to start the server:
        - cd Bombsquad-Ballistica-Modded-Server #(to get back to our server folder)
        - chmod 777 ballisticacore_server
        - cd dist
        - chmod 777 ballisticacore_headless
        - cd ..
        - tmux new -s 43210 #(we used 43210 as name of that tmux, so we can connect back again using that name)
        - ./bombsquad_server
 
     #(6) Now Server should run :P
***
# Feedback and Support
Contact in discord server for all feedbacks, complaints/errors, suggestions, etc,
link = http://discord.gg/ucyaesh
***
# Credits
The Credits belongs to `mr.smoothy#5824`, `snow#0313`, `FireFighter1027#5948` in discord...
