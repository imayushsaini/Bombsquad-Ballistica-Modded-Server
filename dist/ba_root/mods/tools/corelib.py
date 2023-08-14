import bascenev1
import _babase
def set_speed(x):
    try:
        activity = bascenev1.get_foreground_host_activity()
        with activity.context:
            _babase.set_game_speed(x)
    except:
        print("Error: feature available only in BCS server scripts.")
