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


def balance_thread(clientid: int, accountid: str) -> None:
    from shop.shop_system import get_tickets
    balance = get_tickets(accountid)
    reply = (
        f"Your balance: {balance} tickets.\n"
        f"Use '/shop' to view the shop, '/claim' for daily tickets, and '/transfer <player> <amount>' to pay someone."
    )
    _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)


@registry.register(['tickets', 'balance'], category='Normal')
def check_tickets_balance(arguments: list[str], clientid: int, accountid: str) -> None:
    """Check your tickets balance."""
    _thread.start_new_thread(balance_thread, (clientid, accountid))


def transfer_thread(clientid: int, accountid: str, target_accountid: str, target_name: str, target_clientid: int, amount: int) -> None:
    from shop.shop_system import transfer_tickets
    result = transfer_tickets(accountid, target_accountid, amount)
    if result == "success":
        reply = f"Successfully transferred {amount} tickets to {target_name}."
        _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)
        if target_clientid != -1:
            target_reply = f"You received {amount} tickets from a transfer! Check balance with '/balance'."
            _babase.pushcall(Call(send, target_reply, target_clientid), from_other_thread=True)
    else:
        _babase.pushcall(Call(send, result, clientid), from_other_thread=True)


@registry.register(['transfer', 'pay'], category='Normal')
def transfer_tickets_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """Transfer tickets to another player."""
    if len(arguments) < 2:
        send("Usage: /transfer <client_id/player_id/name> <amount>", clientid)
        return

    target_identifier = arguments[0]
    amount_str = arguments[1]

    try:
        amount = int(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        send("Error: Amount must be a positive integer.", clientid)
        return

    session = bs.get_foreground_host_session()
    if not session:
        send("Error: No active session.", clientid)
        return

    target_player = None

    # 1. Try client ID match
    try:
        cid = int(target_identifier)
        for p in session.sessionplayers:
            if p.inputdevice.client_id == cid:
                target_player = p
                break
    except ValueError:
        pass

    # 2. Try player index
    if target_player is None:
        try:
            if target_identifier.lower().startswith('p') and target_identifier[1:].isdigit():
                idx = int(target_identifier[1:])
            else:
                idx = int(target_identifier)
            if 0 <= idx < len(session.sessionplayers):
                target_player = session.sessionplayers[idx]
        except ValueError:
            pass

    # 3. Try name substring match
    if target_player is None:
        for p in session.sessionplayers:
            if target_identifier.lower() in p.getname(icon=False).lower():
                target_player = p
                break

    if target_player is None:
        send(f"Error: Player '{target_identifier}' not found.", clientid)
        return

    target_accountid = target_player.get_v1_account_id()
    if not target_accountid:
        send("Error: Target player account ID not found.", clientid)
        return

    target_name = target_player.getname(icon=False)
    target_clientid = target_player.inputdevice.client_id

    _thread.start_new_thread(transfer_thread, (clientid, accountid, target_accountid, target_name, target_clientid, amount))


def shop_thread(clientid: int, accountid: str, subcategory: str | None) -> None:
    from shop.shop_system import get_shop_commands, EFFECTS_SHOP, get_tickets
    balance = get_tickets(accountid)

    if not subcategory:
        reply = (
            f"--- SHOP (Your Balance: {balance} tickets) ---\n"
            f"Categories:\n"
            f"  /shop commands - Chat commands you can buy\n"
            f"  /shop effects - Spaz effects you can buy\n"
            f"To buy: /buy <item_name>\n"
            f"To equip effect: /equip <effect_name>"
        )
        _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)
        return

    if subcategory == 'commands':
        reply = f"--- Shop Commands (Balance: {balance} t) ---\n"
        shop_cmds = get_shop_commands()
        if not shop_cmds:
            reply += "No commands available in the shop currently."
        else:
            for name, info in shop_cmds.items():
                reply += f"  /{name} - Cost: {info['cost']} t - {info['description']}\n"
        _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)

    elif subcategory == 'effects':
        reply = f"--- Shop Effects (Balance: {balance} t) ---\n"
        for name, info in EFFECTS_SHOP.items():
            reply += f"  {name} - Cost: {info['cost']} t - {info['description']}\n"
        _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)
    else:
        _babase.pushcall(Call(send, "Invalid shop category. Use '/shop commands' or '/shop effects'.", clientid), from_other_thread=True)


@registry.register(['shop'], category='Normal')
def shop_list_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """List available items in the shop."""
    subcategory = arguments[0].lower() if arguments and arguments != [''] else None
    _thread.start_new_thread(shop_thread, (clientid, accountid, subcategory))


def buy_thread(clientid: int, accountid: str, item_name: str) -> None:
    from shop.shop_system import buy_item
    result = buy_item(accountid, item_name)
    _babase.pushcall(Call(send, result, clientid), from_other_thread=True)


@registry.register(['buy'], category='Normal')
def buy_item_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """Buy an item from the shop."""
    if not arguments or arguments == ['']:
        send("Usage: /buy <item_name>", clientid)
        return
    _thread.start_new_thread(buy_thread, (clientid, accountid, arguments[0]))


def equip_thread(clientid: int, accountid: str, effect_name: str) -> None:
    from shop.shop_system import equip_effect
    result = equip_effect(accountid, effect_name)
    _babase.pushcall(Call(send, result, clientid), from_other_thread=True)


@registry.register(['equip', 'use'], category='Normal')
def equip_effect_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """Equip a purchased effect."""
    if not arguments or arguments == ['']:
        send("Usage: /equip <effect_name> or /equip none", clientid)
        return
    _thread.start_new_thread(equip_thread, (clientid, accountid, arguments[0]))


def claim_thread(clientid: int, accountid: str) -> None:
    from shop.shop_system import claim_daily_tickets
    result = claim_daily_tickets(accountid)
    _babase.pushcall(Call(send, result, clientid), from_other_thread=True)


@registry.register(['claim', 'daily'], category='Normal')
def claim_daily_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """Claim daily free tickets."""
    _thread.start_new_thread(claim_thread, (clientid, accountid))


def give_tickets_thread(clientid: int, target_accountid: str, target_name: str, target_clientid: int, amount: int) -> None:
    from shop.shop_system import add_tickets
    new_balance = add_tickets(target_accountid, amount)
    reply = f"Gave {amount} tickets to {target_name}. New balance: {new_balance} tickets."
    _babase.pushcall(Call(send, reply, clientid), from_other_thread=True)
    if target_clientid != -1:
        target_reply = f"An admin gave you {amount} tickets! Your new balance: {new_balance} tickets."
        _babase.pushcall(Call(send, target_reply, target_clientid), from_other_thread=True)


@registry.register(['givetickets', 'addtickets'], category='Cheats')
def give_tickets_command(arguments: list[str], clientid: int, accountid: str) -> None:
    """Give tickets to a player (admin/cheats only)."""
    if len(arguments) < 2:
        send("Usage: /givetickets <client_id/player_id/name> <amount>", clientid)
        return

    target_identifier = arguments[0]
    amount_str = arguments[1]

    try:
        amount = int(amount_str)
    except ValueError:
        send("Error: Amount must be an integer.", clientid)
        return

    session = bs.get_foreground_host_session()
    if not session:
        send("Error: No active session.", clientid)
        return

    target_player = None

    # 1. Try client ID match
    try:
        cid = int(target_identifier)
        for p in session.sessionplayers:
            if p.inputdevice.client_id == cid:
                target_player = p
                break
    except ValueError:
        pass

    # 2. Try player index
    if target_player is None:
        try:
            if target_identifier.lower().startswith('p') and target_identifier[1:].isdigit():
                idx = int(target_identifier[1:])
            else:
                idx = int(target_identifier)
            if 0 <= idx < len(session.sessionplayers):
                target_player = session.sessionplayers[idx]
        except ValueError:
            pass

    # 3. Try name substring match
    if target_player is None:
        for p in session.sessionplayers:
            if target_identifier.lower() in p.getname(icon=False).lower():
                target_player = p
                break

    if target_player is None:
        send(f"Error: Player '{target_identifier}' not found.", clientid)
        return

    target_accountid = target_player.get_v1_account_id()
    if not target_accountid:
        send("Error: Target player account ID not found.", clientid)
        return

    target_name = target_player.getname(icon=False)
    target_clientid = target_player.inputdevice.client_id

    _thread.start_new_thread(give_tickets_thread, (clientid, target_accountid, target_name, target_clientid, amount))
