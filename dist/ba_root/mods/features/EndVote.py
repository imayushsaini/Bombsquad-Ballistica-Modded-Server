#  EndVote by -mr.smoothy

import _ba, ba
import ba.internal
import time

last_end_vote_start_time = 0
end_vote_duration = 30
game_started_on = 0
min_game_duration_to_start_end_vote = 30

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
        return
    if len(voters) == 0:
        ba.internal.chatmessage("end vote started")

    # clean up voters list
    active_players = []
    for player in ba.internal.get_game_roster():
        active_players.append(player['account_id'])
    for voter in voters:
        if voter not in active_players:
            voters.remove(voter)
    if pb_id not in voters:
        voters.append(pb_id)
        _ba.screenmessage("Thanks for vote , encourage other players to type 'end' too.", transient=True,
                          clients=[client_id])
        update_vote_text(required_votes(len(active_players)) - len(voters))
        if required_votes(len(active_players)) - len(
                voters) == 3:  # lets dont spam chat/screen message with votes required , only give message when only 3 votes left
            ba.internal.chatmessage("3 more end votes required")

    if len(voters) >= required_votes(len(active_players)):
        ba.internal.chatmessage("end vote succeed")
        try:
            with _ba.Context(_ba.get_foreground_host_activity()):
                _ba.get_foreground_host_activity().end_game()
        except:
            pass


def required_votes(players):
    if players == 2:
        return 1
    elif players == 3:
        return 2
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
        return players - 4


def update_vote_text(votes_needed):
    activity = _ba.get_foreground_host_activity()
    try:
        activity.end_vote_text.node.text = "{} more votes to end this map\ntype 'end' to vote".format(votes_needed)
    except:
        with _ba.Context(_ba.get_foreground_host_activity()):
            node = ba.NodeActor(ba.newnode('text',
                                           attrs={
                                               'v_attach': 'top',
                                               'h_attach': 'center',
                                               'h_align': 'center',
                                               'color': (1, 1, 0.5, 1),
                                               'flatness': 0.5,
                                               'shadow': 0.5,
                                               'position': (-200, -30),
                                               'scale': 0.7,
                                               'text': '{} more votes to end this map \n type \'end\' to vote'.format(
                                                   votes_needed)
                                           })).autoretain()
            activity.end_vote_text = node
            ba.timer(10, remove_vote_text)


def remove_vote_text():
    activity = _ba.get_foreground_host_activity()
    if hasattr(activity, "end_vote_text") and activity.end_vote_text.node.exists():
        activity.end_vote_text.node.delete()

