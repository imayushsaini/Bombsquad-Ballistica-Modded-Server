# Released under the MIT License. See LICENSE for details.
import ba,_ba,json,os
from stats import mystats
statsFile = mystats.statsfile

def get_setting():
	s = {}
	f=open("setting.json","r")
    d = json.loads(f.read())
    f.close()
    return d

def commit(updated_settings: dict):
    if updated_settings == {}: return
	f=open("setting.json",'w')
	json.dump(updated_settings,f,indent=4)
	f.close()

def sendError(msg: str, ID: int = None):
    if ID is not None:
        ba.screenmessage(msg, color=(1,0,0), clients=[ID], transient=True)
    else:
        ba.screenmessage(msg, color=(1,0,0), transient=True)

