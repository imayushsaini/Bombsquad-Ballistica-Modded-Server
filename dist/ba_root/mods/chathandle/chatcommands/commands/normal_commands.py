# Released under the MIT License. See LICENSE for details.
"""Normal chat commands for players."""

import _thread
import _babase
import _bascenev1
import bascenev1 as bs
from babase._general import Call
from stats import mystats
from .handlers import send
from .registry import registry


def stats_thread(ac_id: str, clientid: int) -> None:
    """Fetch and format statistics in a separate thread."""
    stats_data = mystats.get_stats_by_id(ac_id)
    if stats_data:
        reply = (
            f"Score:{stats_data.get('scores', 0)}\n"
            f"Games:{stats_data.get('games', 0)}\n"
            f"Kills:{stats_data.get('kills', 0)}\n"
            f"Deaths:{stats_data.get('deaths', 0)}\n"
            f"Avg.:{stats_data.get('avg_score', 0.0)}"
        )
    else:
        reply = "Not played any match yet."

    _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)


@registry.register(['me', 'stats', 'score', 'rank', 'myself'], category='Normal')
def fetch_send_stats(arguments: list[str], clientid: int, accountid: str) -> None:
    """Fetch and send stats command."""
    _thread.start_new_thread(stats_thread, (accountid, clientid))


@registry.register(['list', 'l'], category='Normal')
def list_players(arguments: list[str], clientid: int, accountid: str) -> None:
    """Returns the list of players clientid and index."""
    p = '{0:^16}{1:^15}{2:^10}'
    separator = '\n______________________________\n'

    players_list = p.format('Name', 'Client ID', 'Player ID') + separator
    session = bs.get_foreground_host_session()
    if session:
        for index, player in enumerate(session.sessionplayers):
            players_list += p.format(
                player.getname(icon=False),
                player.inputdevice.client_id,
                index
            ) + "\n"

    send(players_list, clientid)


@registry.register(['uniqeid', 'id', 'pb-id', 'pb', 'accountid'], category='Normal')
def accountid_request(arguments: list[str], clientid: int, accountid: str) -> None:
    """Returns the account ID of players."""
    if not arguments or arguments == [] or arguments == ['']:
        send(f"Your account id is {accountid} ", clientid)
    else:
        try:
            session = bs.get_foreground_host_session()
            if session:
                idx = int(arguments[0])
                if 0 <= idx < len(session.sessionplayers):
                    player = session.sessionplayers[idx]
                    name = player.getname(full=True, icon=True)
                    player_accountid = player.get_v1_account_id()
                    send(f" {name}'s account id is '{player_accountid}' ", clientid)
        except (ValueError, TypeError, IndexError):
            pass


def ping_all(clientid: int) -> None:
    """Returns the ping list of all players."""
    p = '{0:^16}{1:^34}ms'
    separator = '\n______________________________\n'

    players_list = p.format('Name', 'Ping (ms)') + separator
    session = bs.get_foreground_host_session()
    if session:
        for player in session.sessionplayers:
            client_id = player.inputdevice.client_id
            ping = _bascenev1.get_client_ping(int(client_id))
            players_list += p.format(player.getname(icon=True), ping) + "\n"

    send(players_list, clientid)


@registry.register(['ping'], category='Normal')
def get_ping(arguments: list[str], clientid: int, accountid: str) -> None:
    """Get ping for self, all, or specific player."""
    if not arguments or arguments == [] or arguments == ['']:
        send(f"Your ping {_bascenev1.get_client_ping(clientid)}ms ", clientid)
    elif arguments[0] == 'all':
        ping_all(clientid)
    else:
        try:
            target_client_id = int(arguments[0])
            session = bs.get_foreground_host_session()
            if session:
                for player in session.sessionplayers:
                    if player.inputdevice.client_id == target_client_id:
                        name = player.getname(full=True, icon=False)
                        ping = _bascenev1.get_client_ping(target_client_id)
                        send(f" {name}'s ping {ping}ms", clientid)
                        break
        except (ValueError, TypeError, IndexError):
            pass
