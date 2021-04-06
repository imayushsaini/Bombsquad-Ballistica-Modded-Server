# Released under the MIT License. See LICENSE for details.
import ba,_ba,json,os
settingjson = os.path.join(_ba.env()['python_directory_user'],"setting.json")

def get_setting():
    s = {}
    f=open(settingjson,"r")
    d = json.loads(f.read())
    f.close()
    return d

def commit(updated_settings: dict):
    if updated_settings == {}: return
    f=open(settingjson,'w')
    json.dump(updated_settings,f,indent=4)
    f.close()

def sendError(msg: str, ID: int = None):
    if ID is not None:
        ba.screenmessage(msg, color=(1,0,0), clients=[ID], transient=True)
    else:
        ba.screenmessage(msg, color=(1,0,0), transient=True)

