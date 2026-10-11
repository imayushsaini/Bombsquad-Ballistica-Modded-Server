#  Custom kick idle player script by mr.smoothy#5824

import setting

import babase
import bascenev1 as bs

settings = setting.get_settings_data()
INGAME_TIME = settings["afk_remover"]["ingame_idle_time_in_secs"]
LOBBY_KICK = settings['afk_remover']["kick_idle_from_lobby"]
INLOBBY_TIME = settings['afk_remover']["lobby_idle_time_in_secs"]


class checkIdle(object):
    def start(self):
        self.t1 = babase.AppTimer(
            2, babase.CallStrict(self.check), repeat=True)
        self.lobbies = {}
        self.player_join_times = {}

    def check(self):
        current = int(bs.displaytime() * 1000)
        session = bs.get_foreground_host_session()
        if not session:
            return

        current_session_players = set()
        for player in session.sessionplayers:
            current_session_players.add(id(player))
            if id(player) not in self.player_join_times:
                self.player_join_times[id(player)] = current

            join_time = self.player_join_times[id(player)]
            last_input = 0
            try:
                if player.inputdevice:
                    last_input = int(player.inputdevice.get_last_input_time())
            except Exception:
                pass

            # If last_input is 0, negative, or earlier than join_time, treat join_time as baseline input time
            if last_input <= 0 or last_input < join_time:
                effective_last_input = join_time
            else:
                effective_last_input = last_input

            afk_time = int((current - effective_last_input) / 1000)

            if afk_time in range(INGAME_TIME, INGAME_TIME + 20):
                self.warn_player(player.get_account_id(),
                                 "Press any button within " + str(
                                     INGAME_TIME + 20 - afk_time) + " secs")
            elif afk_time >= INGAME_TIME + 20:
                player.remove_from_game()

        # Clean up stale session player join times
        stale_players = [
            pid for pid in self.player_join_times if pid not in current_session_players]
        for pid in stale_players:
            del self.player_join_times[pid]

        if LOBBY_KICK:
            current_players = []
            for player in bs.get_game_roster():
                if player['client_id'] != -1 and len(player['players']) == 0:
                    current_players.append(player['client_id'])
                    if player['client_id'] not in self.lobbies:
                        self.lobbies[player['client_id']] = current
                    lobby_afk = int(
                        (current - self.lobbies[player['client_id']]) / 1000)
                    if lobby_afk in range(INLOBBY_TIME, INLOBBY_TIME + 10):
                        bs.broadcastmessage("Join game within " + str(
                            INLOBBY_TIME + 10 - lobby_afk) + " secs",
                            color=(1, 0, 0), transient=True,
                            clients=[player['client_id']])
                    if lobby_afk >= INLOBBY_TIME + 10:
                        bs.disconnect_client(player['client_id'], 0)
            # clean the lobbies dict
            temp = self.lobbies.copy()
            for clid in temp:
                if clid not in current_players:
                    del self.lobbies[clid]

    def warn_player(self, pbid, msg):
        for player in bs.get_game_roster():
            if player["account_id"] == pbid:
                bs.broadcastmessage(msg, color=(1, 0, 0), transient=True,
                                    clients=[player['client_id']])
