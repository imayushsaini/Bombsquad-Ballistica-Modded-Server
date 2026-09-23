
import _thread
import http.client
import json
import time
import urllib.request
from urllib.parse import urlparse

import babase
import bascenev1
from efro.terminal import Clr
from playersdata import pdata

VERSION = 81


def check():
    _thread.start_new_thread(checkChangelog, ())

    bascenev1.apptimer(15, postStatus)


def postStatus():
    link = 'https://bcsservers.ballistica.workers.dev/ping'
    data = {'name': babase.app.classic.server._config.party_name,
            'port': str(bascenev1.get_game_port()),
            'build': babase.app.env.engine_build_number,
            'bcsversion': VERSION}
    _thread.start_new_thread(postRequest, (link, data,))


def postRequest(link, data):
    try:
        url = urlparse(link)
        conn = http.client.HTTPSConnection(url.netloc)
        json_payload = json.dumps(data)
        headers = {
            "Content-Type": "application/json"
        }
        conn.request("POST", url.path, body=json_payload, headers=headers)
        response = conn.getresponse()
        response_data = response.read()
    except:
        pass


def checkSpammer(data):
    def checkMaster(data):
        try:
            url = urlparse(
                'https://bcsservers.ballistica.workers.dev/checkspammer')
            conn = http.client.HTTPSConnection(url.netloc)
            json_payload = json.dumps(data)
            headers = {
                "Content-Type": "application/json"
            }
            conn.request("POST", url.path, body=json_payload, headers=headers)
            response = conn.getresponse()
            response_data = response.read()
        except:
            pass
        # TODO handle response and kick player based on status

    _thread.start_new_thread(checkMaster, (data,))
    return


def fetchChangelogs():
    url = "https://raw.githubusercontent.com/imayushsaini/Bombsquad-Ballistica-Modded-Server/public-server/dist/ba_root/mods/changelogs.json"
    try:
        data = urllib.request.urlopen(url)
        changelog = json.loads(data.read())
    except:
        return None
    else:
        return changelog


def checkChangelog():
    changelog = fetchChangelogs()
    if changelog is None:
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
