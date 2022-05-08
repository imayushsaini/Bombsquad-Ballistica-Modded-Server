import _ba, ba
import time
""" 
End Vote by mr.smoothy 
with no timer and minimum message
for BCS scripts only
"""
last_end_vote_start_time = 0
end_vote_duration = 30
game_started_on = 0
min_game_duration_to_start_end_vote = 60

voters = []


def vote_end(pb_id, client_id):
    global voters
    global last_end_vote_start_time
    now = time.time()
    if now > last_end_vote_start_time + end_vote_duration:
        voters = []
        last_end_vote_start_time = now
    if now < game_started_on + min_game_duration_to_start_end_vote:
        _ba.screenmessage("Seems game just started, Try again after some time", transient=True,
                          clients=[client_id])
    if len(voters) == 0:
        _ba.chatmessage("end vote started")

    # clean up voters list
    active_players = []
    for player in _ba.get_game_roster():
        active_players.append(player['account_id'])
    for voter in voters:
        if voter not in active_players:
            voters.remove(voter)
    if pb_id not in voters:
        voters.append(pb_id)
        _ba.screenmessage("Thanks for vote , encourage other players to type 'end' too.", transient=True,
                          clients=[client_id])

    if len(voters) >= required_votes(len(active_players)):
        _ba.chatmessage("end vote succeed")
        try:
            with _ba.Context(_ba.get_foreground_host_activity()):
                _ba.get_foreground_host_activity().end_game()
        except:
            pass

    elif required_votes(len(active_players)) - len(
            voters) == 3:  # lets dont spam chat/screen message with votes required , only give message when only 3 votes left
        _ba.chatmessage("3 more end votes required")


def required_votes(players):
    if players == 2:
        return 2
    elif players == 3:
        return 3
    elif players == 4:
        return 2
    elif players == 5:
        return 3
    elif players == 6:
        return 3
    elif players == 7:
        return 4
    elif players == 8:
        return 4
    else:
        return players - 3
