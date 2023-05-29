#  Electronic Voting Machine (EVM) by -mr.smoothy

import _ba
import ba
import ba.internal
import time

game_started_on = 0


vote_machine = {"end": {"last_vote_start_time": 0, "vote_duration": 50,
                        "min_game_duration_to_start_vote": 30, "voters": []},
                "sm": {"last_vote_start_time": 0, "vote_duration": 50,
                       "min_game_duration_to_start_vote": 1, "voters": []},
                "nv": {"last_vote_start_time": 0, "vote_duration": 50,
                       "min_game_duration_to_start_vote": 1, "voters": []},
                "dv": {"last_vote_start_time": 0, "vote_duration": 50,
                       "min_game_duration_to_start_vote": 1, "voters": []}}


def vote(pb_id, client_id, vote_type):
    global vote_machine
    voters = vote_machine[vote_type]["voters"]
    last_vote_start_time = vote_machine[vote_type]["last_vote_start_time"]
    vote_duration = vote_machine[vote_type]["vote_duration"]
    min_game_duration_to_start_vote = vote_machine[vote_type]["min_game_duration_to_start_vote"]

    now = time.time()
    if now > last_vote_start_time + vote_duration:
        voters = []
        vote_machine[vote_type]["last_vote_start_time"] = now
    if now < game_started_on + min_game_duration_to_start_vote:
        _ba.screenmessage("Seems game just started, Try again after some time", transient=True,
                          clients=[client_id])
        return
    if len(voters) == 0:
        ba.internal.chatmessage(f"{vote_type} vote started")

    # clean up voters list
    active_players = []
    for player in ba.internal.get_game_roster():
        active_players.append(player['account_id'])
    for voter in voters:
        if voter not in active_players:
            voters.remove(voter)
    if pb_id not in voters:
        voters.append(pb_id)
        _ba.screenmessage(f'Thanks for vote , encourage other players to type {vote_type} too.', transient=True,
                          clients=[client_id])
        if vote_type == 'end':
            update_vote_text(max_votes_required(
                len(active_players)) - len(voters))
        else:
            activity = _ba.get_foreground_host_activity()
            if activity is not None:
                with _ba.Context(activity):
                    _ba.screenmessage(f"{max_votes_required(len(active_players)) - len(voters)} votes required for {vote_type}",
                                    image={"texture": ba.gettexture("achievementSharingIsCaring"),
                                            "tint_texture": ba.gettexture("achievementSharingIsCaring"),
                                                "tint_color": (0.5, 0.5, 0.5), "tint2_color": (0.7, 0.5, 0.9)},
                                    top=True)
    vote_machine[vote_type]["voters"] = voters

    if len(voters) >= max_votes_required(len(active_players)):
        ba.internal.chatmessage(f"{vote_type} vote succeed")
        vote_machine[vote_type]["voters"] = []
        if vote_type == "end":
            try:
                with _ba.Context(_ba.get_foreground_host_activity()):
                    _ba.get_foreground_host_activity().end_game()
            except:
                pass
        elif vote_type == "nv":
            _ba.chatmessage("/nv")
        elif vote_type == "dv":
            _ba.chatmessage("/dv")
        elif vote_type == "sm":
            _ba.chatmessage("/sm")


def reset_votes():
    global vote_machine
    for value in vote_machine.values():
        value["voters"] = []


def max_votes_required(players):
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
    elif players == 10:
        return 5
    else:
        return players - 5


def update_vote_text(votes_needed):
    activity = _ba.get_foreground_host_activity()
    try:
        activity.end_vote_text.node.text = "{} more votes to end this map\ntype 'end' to vote".format(
            votes_needed)
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
            ba.timer(20, remove_vote_text)


def remove_vote_text():
    activity = _ba.get_foreground_host_activity()
    if hasattr(activity, "end_vote_text") and activity.end_vote_text.node.exists():
        activity.end_vote_text.node.delete()
