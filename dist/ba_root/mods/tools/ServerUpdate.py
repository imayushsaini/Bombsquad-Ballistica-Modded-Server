import _thread
import json
import time
import urllib.request

import requests
from playersdata import pdata

import babase
import bascenev1
from efro.terminal import Clr

VERSION = 71


def check():
    print(babase.app.classic)
    print(babase.app.classic.server)

    _thread.start_new_thread(updateProfilesJson, ())
    _thread.start_new_thread(checkChangelog, ())

    bascenev1.apptimer(15, postStatus)


def updateProfilesJson():
    profiles = pdata.get_profiles()

    for id in profiles:
        if "spamCount" not in profiles[id]:
            profiles[id]["spamCount"] = 0
            profiles[id]["lastSpam"] = time.time()

    pdata.commit_profiles(profiles)


def postStatus():
    link = 'https://bcsservers.ballistica.workers.dev/ping'
    data = {'name': babase.app.classic.server._config.party_name,
            'port': str(bascenev1.get_game_port()),
            'build': babase.app.build_number,
            'bcsversion': VERSION}
    _thread.start_new_thread(postRequest, (link, data,))


def postRequest(link, data):
    try:
        res = requests.post(link,
                            json=data)
    except:
        pass


def checkSpammer(data):
    def checkMaster(data):
        try:
            res = requests.post(
                'https://bcsservers.ballistica.workers.dev/checkspammer',
                json=data)
        except:
            pass
        # TODO handle response and kick player based on status

    _thread.start_new_thread(checkMaster, (data,))
    return


def fetchChangelogs():
    url = "https://raw.githubusercontent.com/imayushsaini/Bombsquad-Ballistica-Modded-Server/public-server/dist/ba_root/mods/changelogs.json"

    if 2 * 2 == 4:
        try:
            data = urllib.request.urlopen(url)
            changelog = json.loads(data.read())
        except:
            return None
        else:
            return changelog


def checkChangelog():
    changelog = fetchChangelogs()
    if changelog == None:
        print(
            f'{Clr.BRED} UNABLE TO CHECK UPDATES , CHECK MANUALLY FROM URL {Clr.RST}',
            flush=True)
    else:
        msg = ""
        avail = False
        for log in changelog:
            if int(log) > VERSION:
                avail = True

        if not avail:
            print(
                f'{Clr.BGRN}{Clr.WHT} YOU ARE ON LATEST VERSION {Clr.RST}',
                flush=True)
        else:
            print(f'{Clr.BYLW}{Clr.BLU} UPDATES AVAILABLE {Clr.RST}',
                  flush=True)
            for log in changelog:
                if int(log) > VERSION:
                    msg = changelog[log]["time"]
                    print(f'{Clr.CYN} {msg} {Clr.RST}', flush=True)

                    msg = changelog[log]["log"]
                    print(f'{Clr.MAG} {msg} {Clr.RST}', flush=True)
