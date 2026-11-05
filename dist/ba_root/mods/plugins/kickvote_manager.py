"""Kick vote management plugin.

# ba_meta require api 9

Manages kick vote restrictions (players who cannot initiate kick votes)
and kick vote immunity (players who cannot be kick-voted against).
Supports in-memory caching and persistent database storage with async DB writes.
"""

from __future__ import annotations

import _thread
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import bacommon.docui.v2 as dui2
import bacommon.docui.routes.classichost as hroutes
from bacommon.docui.presets import section_button, SectionButtonSize
from bacommon.langstr import LangStrSpecValue
import babase
import bascenev1 as bs
from baclassic._hostuikick import (
    HostUIKickVotes,
    HostUIKickRequest,
    KickVoteRefusal,
)
from baclassic._hostuimembers import HostUIClientPage
from baclassic._hostuihandler import HostUIHandler, status_response
from baclassic._hostuiparts import host_ui_text

if TYPE_CHECKING:
    from typing import Awaitable, Sequence
    from bacommon.docui.routes import DocUIRoute


class KickVoteManager:
    """Manages player kick vote restrictions and immunity."""

    _instance: KickVoteManager | None = None

    def __init__(self) -> None:
        self.restricted_players: set[str] = set()
        self.immune_players: set[str] = set()
        self.load_from_db_and_cache()

    @classmethod
    def get(cls) -> KickVoteManager:
        """Returns the singleton instance of KickVoteManager."""
        if cls._instance is None:
            cls._instance = KickVoteManager()
        return cls._instance

    def load_from_db_and_cache(self) -> None:
        """Loads restricted and immune player IDs from pdata and database into memory."""
        try:
            from playersdata import pdata

            # Load restricted players from blacklist
            blacklist = pdata.get_blacklist()
            kv_disabled = blacklist.get("kick-vote-disabled", {})
            now = datetime.now()
            for acc_id, data in kv_disabled.items():
                till_str = data.get("till") if isinstance(data, dict) else None
                if till_str:
                    try:
                        till = datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S")
                        if now < till:
                            self.restricted_players.add(acc_id)
                    except Exception:
                        self.restricted_players.add(acc_id)
                else:
                    self.restricted_players.add(acc_id)

            # Load immune players from custom perks
            custom = pdata.get_custom()
            immune_data = custom.get("kick_vote_immune", {})
            if isinstance(immune_data, dict):
                for acc_id in immune_data:
                    self.immune_players.add(acc_id)
            elif isinstance(immune_data, (list, set)):
                for acc_id in immune_data:
                    self.immune_players.add(acc_id)
        except Exception as e:
            print(f"KickVoteManager: Error loading from cache/db: {e}")

    # ==================== Restriction Management ====================

    def add_restriction(
        self,
        account_id: str,
        duration_days: float = 30.0,
        reason: str = "kick vote restricted",
    ) -> None:
        """Restricts a player from starting kick votes.
        Updates in-memory cache immediately and performs DB write asynchronously in a thread.
        """
        if not account_id:
            return
        acc = account_id.strip('"')
        self.restricted_players.add(acc)
        try:
            from playersdata import pdata

            pdata.disable_kick_vote(acc, duration_days, reason)
        except Exception as e:
            print(f"KickVoteManager: Error persisting restriction for {acc}: {e}")

    def remove_restriction(self, account_id: str) -> None:
        """Removes kick vote restriction for a player.
        Updates in-memory cache immediately and performs DB write asynchronously in a thread.
        """
        if not account_id:
            return
        acc = account_id.strip('"')
        self.restricted_players.discard(acc)
        try:
            from playersdata import pdata

            pdata.enable_kick_vote(acc)
        except Exception as e:
            print(f"KickVoteManager: Error removing restriction for {acc}: {e}")

    def is_restricted(self, account_id: str) -> bool:
        """Checks if a player is restricted from starting a kick vote."""
        if not account_id:
            return False
        acc = account_id.strip('"')
        if acc in self.restricted_players:
            return True

        # Fallback check against pdata blacklist
        try:
            from playersdata import pdata

            blacklist = pdata.get_blacklist()
            kv_disabled = blacklist.get("kick-vote-disabled", {})
            if acc in kv_disabled:
                till_str = (
                    kv_disabled[acc].get("till")
                    if isinstance(kv_disabled[acc], dict)
                    else None
                )
                if till_str:
                    try:
                        till = datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S")
                        if datetime.now() < till:
                            self.restricted_players.add(acc)
                            return True
                        kv_disabled.pop(acc, None)
                        return False
                    except Exception:
                        pass
                self.restricted_players.add(acc)
                return True
        except Exception:
            pass
        return False

    # ==================== Immunity Management ====================

    def add_immune(self, account_id: str) -> None:
        """Grants kick vote immunity (perk) to a player.
        Updates in-memory cache immediately and performs DB write asynchronously in a thread.
        """
        if not account_id:
            return
        acc = account_id.strip('"')
        self.immune_players.add(acc)
        try:
            from playersdata import pdata

            pdata.set_kick_vote_immune(acc, True)
        except Exception as e:
            print(f"KickVoteManager: Error persisting immunity for {acc}: {e}")

    def remove_immune(self, account_id: str) -> None:
        """Removes kick vote immunity from a player.
        Updates in-memory cache immediately and performs DB write asynchronously in a thread.
        """
        if not account_id:
            return
        acc = account_id.strip('"')
        self.immune_players.discard(acc)
        try:
            from playersdata import pdata

            pdata.set_kick_vote_immune(acc, False)
        except Exception as e:
            print(f"KickVoteManager: Error removing immunity for {acc}: {e}")

    def is_immune(self, account_id: str) -> bool:
        """Checks if a player is immune from kick votes."""
        if not account_id:
            return False
        acc = account_id.strip('"')
        if acc in self.immune_players:
            return True

        # Fallback check against pdata custom perks
        try:
            from playersdata import pdata

            if pdata.is_kick_vote_immune(acc):
                self.immune_players.add(acc)
                return True
        except Exception:
            pass
        return False

    # ==================== Inspection & Kick Vote Handling ====================

    def get_restricted_list(self) -> list[str]:
        """Returns a list of restricted player account IDs."""
        return sorted(list(self.restricted_players))

    def get_immune_list(self) -> list[str]:
        """Returns a list of immune player account IDs."""
        return sorted(list(self.immune_players))

    def send_chat_message(self, account_id: str, message: str) -> None:
        """Sends a private chat message to the specific client matching account_id."""
        if not account_id:
            return
        client_id = None
        try:
            for client in bs.get_game_roster():
                if client.get("account_id") == account_id:
                    client_id = client.get("client_id")
                    break
        except Exception:
            pass

        if client_id is None:
            try:
                session = bs.get_foreground_host_session()
                if session:
                    for player in session.sessionplayers:
                        if (
                            getattr(player, "get_v1_account_id", None)
                            and player.get_v1_account_id() == account_id
                        ):
                            client_id = player.inputdevice.client_id
                            break
            except Exception:
                pass

        try:
            if client_id is not None:
                bs.chatmessage(str(message), clients=[client_id])
            else:
                bs.chatmessage(str(message))
        except Exception:
            try:
                import _bascenev1

                if client_id is not None:
                    _bascenev1.chatmessage(str(message), clients=[client_id])
                else:
                    _bascenev1.chatmessage(str(message))
            except Exception as e:
                print(f"KickVoteManager: Error sending chat message: {e}")

    def check_and_handle_kick_vote(self, starter_id: str, target_id: str) -> bool:
        """Validates if kick vote can start.
        Returns False and sends private chatmessage to starter if restricted or if target is immune.
        Returns True if allowed.
        """
        try:
            from tools import logger
        except Exception:
            logger = None

        starter = (starter_id or "").strip('"')
        target = (target_id or "").strip('"')

        if logger:
            logger.log(f"Kick vote attempt: {starter} -> {target}")

        # Check starter restriction
        if self.is_restricted(starter):
            if logger:
                logger.log(f"Kick vote blocked: {starter} is restricted from starting kick votes.")
            self.send_chat_message(starter, "Kick vote disabled for you")
            return False

        # Check target immunity
        if self.is_immune(target):
            if logger:
                logger.log(f"Kick vote blocked: {target} has special perks and is immune from kick votes.")
            self.send_chat_message(starter, "Target player is immune from kick vote")
            return False

        if logger:
            logger.log(f"{starter} started kick vote for {target}.")
        return True


def clientid_to_accountid(client_id: int) -> str | None:
    """Resolve a client ID to an account ID (pb-... or a-...)."""
    if client_id == -1:
        plus = getattr(babase.app, "plus", None)
        accounts = getattr(plus, "accounts", None) if plus else None
        primary = getattr(accounts, "primary", None) if accounts else None
        if primary is not None and getattr(primary, "accountid", None):
            return str(primary.accountid).strip('"')
        return None

    try:
        for entry in bs.get_game_roster():
            if entry.get("client_id") == client_id:
                acc = entry.get("account_id")
                if acc:
                    return str(acc).strip('"')
    except Exception:
        pass

    try:
        session = bs.get_foreground_host_session()
        if session:
            for player in session.sessionplayers:
                if (
                    player.inputdevice
                    and player.inputdevice.client_id == client_id
                ):
                    v1_id = getattr(player, "get_v1_account_id", None)
                    if callable(v1_id):
                        val = v1_id()
                        if val:
                            return str(val).strip('"')
    except Exception:
        pass
    return None


def is_admin_viewer(viewer: int) -> bool:
    """Whether a client viewer has admin or owner permissions in pdata.get_roles."""
    if viewer == -1:
        return True
    account_id = clientid_to_accountid(viewer)
    if not account_id:
        return False
    try:
        from playersdata import pdata
        roles = pdata.get_roles()
        for role_name, role_info in roles.items():
            ids = role_info.get("ids", [])
            if account_id in ids:
                cmds = role_info.get("commands", [])
                if "ALL" in cmds or any(c in cmds for c in ("kick", "ban", "mute")):
                    return True
                if role_name.lower() in ("owner", "admin"):
                    return True
        p_roles = pdata.get_player_roles(account_id)
        if any(r.lower() in ("owner", "admin") for r in p_roles):
            return True
    except Exception:
        pass
    return False


def is_muted_for_all(account_id: str) -> bool:
    """Check if an account is currently muted server-wide (in pdata blacklist)."""
    if not account_id:
        return False
    try:
        from playersdata import pdata
        blacklist = pdata.get_blacklist()
        muted_ids = blacklist.get("muted-ids", {})
        if account_id in muted_ids:
            data = muted_ids[account_id]
            till_str = data.get("till") if isinstance(data, dict) else None
            if till_str:
                till = datetime.strptime(till_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < till:
                    return True
                return False
            return True
    except Exception:
        pass
    return False


from tools.local_mute import LocalMuteManager


class CustomHostUIKickVotes(HostUIKickVotes):
    """Host UI kick votes customized for KickVoteManager, custom hooks, and server settings."""

    def is_admin(self, client_id: int) -> bool:
        """Whether a client is an admin or owner (or the host; client id -1)."""
        return is_admin_viewer(client_id) or super().is_admin(client_id)

    def get_kick_unavailable_text(
        self, request: HostUIKickRequest
    ) -> str | babase.LangStr | None:
        """Why get_kick_page offers no kick; displayed in DocUI beside a disabled kick button."""
        target_acc = clientid_to_accountid(request.client_id)
        viewer_acc = clientid_to_accountid(request.viewer)
        kvm = KickVoteManager.get()

        if target_acc and kvm.is_immune(target_acc) and not self.is_admin(request.viewer):
            return "Target player is immune from kick votes"

        if viewer_acc and kvm.is_restricted(viewer_acc) and not self.is_admin(request.viewer):
            return "Kick voting is disabled for you"

        return super().get_kick_unavailable_text(request)

    def get_kick_page(self, request: HostUIKickRequest):
        """Where a kick request goes (None if kicking is blocked/unavailable)."""
        target_acc = clientid_to_accountid(request.client_id)
        viewer_acc = clientid_to_accountid(request.viewer)
        kvm = KickVoteManager.get()

        if target_acc and kvm.is_immune(target_acc) and not self.is_admin(request.viewer):
            return None

        if viewer_acc and kvm.is_restricted(viewer_acc) and not self.is_admin(request.viewer):
            return None

        return super().get_kick_page(request)

    def get_refusal(
        self, starter_client_id: int, target_client_id: int
    ) -> KickVoteRefusal | None:
        starter_acc = clientid_to_accountid(starter_client_id)
        target_acc = clientid_to_accountid(target_client_id)
        kvm = KickVoteManager.get()

        if starter_acc and kvm.is_restricted(starter_acc):
            return KickVoteRefusal.DISABLED

        if target_acc and kvm.is_immune(target_acc):
            return KickVoteRefusal.ADMIN

        return super().get_refusal(starter_client_id, target_client_id)

    def get_refusal_text(
        self, refusal: KickVoteRefusal, starter_client_id: int
    ) -> str | babase.LangStr:
        starter_acc = clientid_to_accountid(starter_client_id)
        kvm = KickVoteManager.get()
        if starter_acc and kvm.is_restricted(starter_acc):
            return "Kick voting is disabled for you"
        return super().get_refusal_text(refusal, starter_client_id)

    def start_vote(
        self,
        starter_client_id: int,
        target_client_id: int,
        player_id: int | None = None,
    ) -> KickVoteRefusal | None:
        starter_acc = clientid_to_accountid(starter_client_id) or ""
        target_acc = clientid_to_accountid(target_client_id) or ""

        # Trigger existing custom_hooks.kick_vote_started (logs, checks immunity/restrictions)
        try:
            import custom_hooks
            if not custom_hooks.kick_vote_started(starter_acc, target_acc):
                return KickVoteRefusal.DISABLED
        except Exception as exc:
            print(f"Error in custom kick_vote_started: {exc}")

        refusal = super().start_vote(starter_client_id, target_client_id, player_id)
        if refusal is not None:
            return refusal

        # Broadcast announcement based on setting.json
        try:
            import setting
            settings = setting.get_settings_data()
        except Exception:
            settings = {}

        show_starter = settings.get("ShowKickVoteStarterName", True)
        msg_type = settings.get("KickVoteMsgType", "chat")

        target_name = (
            self.vote.target_name
            if self.vote is not None
            else self.get_target_name(target_client_id, player_id) or "?"
        )
        starter_name = self.get_host_ui().get_client_name(starter_client_id) or "Someone"

        if show_starter:
            announcement = f"{starter_name} started a kick vote for {target_name}."
        else:
            announcement = f"A kick vote has been started for {target_name}."

        if msg_type in ("chat", "both"):
            try:
                bs.chatmessage(announcement)
            except Exception:
                pass
        if msg_type in ("screen", "screenmessage", "both"):
            try:
                bs.broadcastmessage(announcement, color=(1.0, 0.8, 0.0))
            except Exception:
                pass

        return None

    def get_question_text(self, name: str) -> str | babase.LangStr:
        try:
            import setting
            settings = setting.get_settings_data()
            if settings.get("ShowKickVoteStarterName", True) and self.vote is not None:
                starter_name = self.get_host_ui().get_client_name(self.vote.starter_client_id)
                if starter_name:
                    return f"Kick {name}? (Started by {starter_name})"
        except Exception:
            pass
        return super().get_question_text(name)

    def end_vote(self, passed: bool, quiet: bool = False) -> None:
        super().end_vote(passed, quiet)
        try:
            import custom_hooks
            custom_hooks.on_kick_vote_end()
        except Exception as exc:
            print(f"Error in on_kick_vote_end: {exc}")

    def kick(self, client_id: int, name: str | None = None) -> None:
        account_id = clientid_to_accountid(client_id) or ""
        super().kick(client_id, name)
        try:
            import custom_hooks
            custom_hooks.on_kicked(account_id)
        except Exception as exc:
            print(f"Error in on_kicked: {exc}")


class CustomHostUIClientPage(HostUIClientPage):
    """Host UI member page showing custom server roles and action buttons."""

    def get_title(self, client_id: int) -> str | babase.LangStr:
        """The page's title: Server Host for client_id -1, else default."""
        if client_id == -1:
            try:
                import server_host_docui
                return server_host_docui.get_server_title()
            except Exception:
                return "Server Host"
        return super().get_title(client_id)

    def get_role_text(self, client_id: int) -> str | babase.LangStr | None:
        """The member's role row: custom server roles, host, admin or member."""
        if client_id == -1:
            return "Host"

        account_id = clientid_to_accountid(client_id)
        if account_id:
            try:
                from playersdata import pdata
                roles = pdata.get_player_roles(account_id)
                if roles:
                    # Clean up and capitalize role names (e.g. Owner, Admin, VIP)
                    return ", ".join(r.capitalize() for r in roles)
            except Exception:
                pass

        return super().get_role_text(client_id)

    def build(
        self, route: DocUIRoute, client_id: int, viewer: int
    ) -> dui2.Response:
        """Build the member page for client_id viewed by viewer."""
        if client_id == -1:
            try:
                import server_host_docui
                return server_host_docui.build_server_host_page(route, viewer)
            except Exception as exc:
                print(f"Error building server host page: {exc}")

        response = super().build(route, client_id, viewer)
        if response.page is None or not response.page.rows:
            return response

        viewer_acc = clientid_to_accountid(viewer)
        target_acc = clientid_to_accountid(client_id)
        is_self = (client_id == viewer) or (
            viewer_acc and target_acc and viewer_acc == target_acc
        )
        is_target_host = (client_id == -1)

        # Do not add action buttons for self
        if is_self:
            return response

        extra_rows: list[dui2.Row] = []

        # 1. Public Mute / Unmute button (visible to all)
        is_muted = LocalMuteManager.get().is_muted(
            viewer=viewer,
            target=client_id,
            viewer_acc=viewer_acc,
            target_acc=target_acc,
        )
        mute_label = "Unmute" if is_muted else "Mute"

        mute_button = section_button(
            host_ui_text(mute_label),
            dui2.Replace(
                request=dui2.Request(
                    path="/member/action",
                    args={"c": client_id, "a": "mute"},
                )
            ),
            size=SectionButtonSize.MEDIUM,
        )
        if is_muted:
            mute_button.color = (0.5, 0.45, 0.55, 1.0)
            mute_button.label_color = (0.9, 0.85, 0.95, 1.0)
        else:
            mute_button.color = (0.35, 0.45, 0.55, 1.0)
            mute_button.label_color = (0.85, 0.9, 1.0, 1.0)

        # 2. Admin-only buttons (check roles from pdata.get_roles)
        if is_admin_viewer(viewer) and not is_target_host:
            # Mute for all / Unmute for all
            target_muted_all = is_muted_for_all(target_acc or "")
            mute_all_label = (
                "Unmute for all" if target_muted_all else "Mute for all"
            )
            mute_all_button = section_button(
                host_ui_text(mute_all_label),
                dui2.Replace(
                    request=dui2.Request(
                        path="/member/action",
                        args={"c": client_id, "a": "mute_all"},
                    )
                ),
                size=SectionButtonSize.MEDIUM,
            )
            if target_muted_all:
                mute_all_button.color = (0.6, 0.4, 0.2, 1.0)
                mute_all_button.label_color = (1.0, 0.9, 0.7, 1.0)
            else:
                mute_all_button.color = (0.65, 0.5, 0.25, 1.0)
                mute_all_button.label_color = (1.0, 0.95, 0.8, 1.0)

            # Row with Mute and Mute for all side-by-side
            extra_rows.append(
                dui2.ButtonRow(
                    buttons=[mute_button, mute_all_button],
                    layout=dui2.ButtonRowLayout.FILL,
                    padding_top=15.0,
                )
            )

            # Kick w/o vote
            kick_button = section_button(
                host_ui_text("Kick w/o vote"),
                dui2.Replace(
                    request=dui2.Request(
                        path="/member/action",
                        args={"c": client_id, "a": "kick"},
                    )
                ),
                size=SectionButtonSize.MEDIUM,
            )
            kick_button.color = (0.75, 0.3, 0.2, 1.0)
            kick_button.label_color = (1.0, 0.8, 0.7, 1.0)

            # Ban
            ban_button = section_button(
                host_ui_text("Ban"),
                dui2.Replace(
                    request=dui2.Request(
                        path="/member/action",
                        args={"c": client_id, "a": "ban"},
                    )
                ),
                size=SectionButtonSize.MEDIUM,
            )
            ban_button.color = (0.7, 0.15, 0.15, 1.0)
            ban_button.label_color = (1.0, 0.7, 0.7, 1.0)

            # Row with Kick w/o vote and Ban side-by-side
            extra_rows.append(
                dui2.ButtonRow(
                    buttons=[kick_button, ban_button],
                    layout=dui2.ButtonRowLayout.FILL,
                    padding_top=10.0,
                )
            )
        else:
            # Non-admin: only public Mute button
            extra_rows.append(
                dui2.ButtonRow(
                    buttons=[mute_button],
                    layout=dui2.ButtonRowLayout.FILL,
                    padding_top=15.0,
                )
            )

        response.page.rows.extend(extra_rows)
        return response


class CustomHostUIHandler(HostUIHandler):
    """Custom HostUIHandler routing /member/action requests."""

    def __init__(self, prev_handler: HostUIHandler | None = None) -> None:
        super().__init__()
        self.prev_handler = prev_handler

    def fulfill_request(
        self, request: dui2.Request, client_id: int
    ) -> dui2.Response | Awaitable[dui2.Response]:
        if request.path == "/member/action":
            return self._handle_member_action(request, client_id)
        if self.prev_handler is not None:
            return self.prev_handler.fulfill_request(request, client_id)
        return super().fulfill_request(request, client_id)

    def _handle_member_action(
        self, request: dui2.Request, viewer: int
    ) -> dui2.Response:
        try:
            target_cl_id = int(request.args.get("c", -999))
            action = str(request.args.get("a", ""))
        except (ValueError, TypeError):
            return status_response(dui2.ResponseStatus.UNKNOWN_ERROR)

        classic = getattr(babase.app, "classic", None)
        host_ui = getattr(classic, "host_ui", None) if classic else None

        target_name = (
            host_ui.get_client_name(target_cl_id)
            if host_ui
            else f"Client {target_cl_id}"
        ) or f"Client {target_cl_id}"

        viewer_acc = clientid_to_accountid(viewer) or ""
        target_acc = clientid_to_accountid(target_cl_id) or ""

        # Server host actions (target_cl_id == -1)
        if target_cl_id == -1:
            try:
                import server_host_docui
                return server_host_docui.handle_server_action(
                    action=action,
                    viewer=viewer,
                    viewer_acc=viewer_acc,
                    target_name=target_name,
                )
            except Exception as exc:
                print(f"Error handling server host action: {exc}")
                return status_response(dui2.ResponseStatus.UNKNOWN_ERROR)

        # 1. Public Mute action
        if action == "mute":
            is_muted = LocalMuteManager.get().toggle_mute(
                viewer=viewer,
                target=target_cl_id,
                viewer_acc=viewer_acc,
                target_acc=target_acc,
            )
            status_word = "muted" if is_muted else "unmuted"
            if viewer != -1:
                try:
                    bs.chatmessage(
                        f"{target_name} is now {status_word} for you.",
                        clients=[viewer],
                    )
                except Exception:
                    pass

            if host_ui and host_ui.client_page:
                return host_ui.client_page.build(
                    hroutes.Client(client_id=target_cl_id), target_cl_id, viewer
                )
            return status_response(dui2.ResponseStatus.SUCCESS)

        # 2. Admin actions - verify permissions
        if not is_admin_viewer(viewer):
            return status_response(dui2.ResponseStatus.UNKNOWN_ERROR)

        if action == "mute_all":
            from chathandle.chatcommands.commands import management
            if is_muted_for_all(target_acc):
                management.unmute([str(target_cl_id)], viewer, viewer_acc)
            else:
                management.mute([str(target_cl_id)], viewer, viewer_acc)

            if host_ui and host_ui.client_page:
                return host_ui.client_page.build(
                    hroutes.Client(client_id=target_cl_id), target_cl_id, viewer
                )
            return status_response(dui2.ResponseStatus.SUCCESS)

        elif action == "kick":
            from chathandle.chatcommands.commands import management
            management.kick([str(target_cl_id)], viewer, viewer_acc)
            return dui2.Response(
                page=dui2.Page(
                    title=LangStrSpecValue.literal("Kick"),
                    rows=[
                        dui2.ButtonRow(
                            title=LangStrSpecValue.literal(f"Kicked {target_name}"),
                            buttons=[
                                dui2.Button(
                                    label=LangStrSpecValue.literal("Ok"),
                                    action=dui2.Local(close_window=True),
                                    size=(200.0, 70.0),
                                    style=dui2.ButtonStyle.MEDIUM,
                                )
                            ],
                            layout=dui2.ButtonRowLayout.FIXED,
                            center_title=True,
                            center_content=True,
                            padding_top=30.0,
                        )
                    ],
                    center_vertically=True,
                )
            )

        elif action == "ban":
            from chathandle.chatcommands.commands import management
            management.ban([str(target_cl_id)], viewer, viewer_acc)
            return dui2.Response(
                page=dui2.Page(
                    title=LangStrSpecValue.literal("Ban"),
                    rows=[
                        dui2.ButtonRow(
                            title=LangStrSpecValue.literal(f"Banned {target_name}"),
                            buttons=[
                                dui2.Button(
                                    label=LangStrSpecValue.literal("Ok"),
                                    action=dui2.Local(close_window=True),
                                    size=(200.0, 70.0),
                                    style=dui2.ButtonStyle.MEDIUM,
                                )
                            ],
                            layout=dui2.ButtonRowLayout.FIXED,
                            center_title=True,
                            center_content=True,
                            padding_top=30.0,
                        )
                    ],
                    center_vertically=True,
                )
            )

        return status_response(dui2.ResponseStatus.UNKNOWN_ERROR)


def apply_custom_kick_votes() -> None:
    """Installs CustomHostUIKickVotes, CustomHostUIClientPage, and CustomHostUIHandler onto host_ui."""
    try:
        classic = getattr(babase.app, "classic", None)
        if classic is not None and getattr(classic, "host_ui", None) is not None:
            if not isinstance(classic.host_ui.kick_votes, CustomHostUIKickVotes):
                classic.host_ui.kick_votes = CustomHostUIKickVotes()
            if not isinstance(classic.host_ui.client_page, CustomHostUIClientPage):
                classic.host_ui.client_page = CustomHostUIClientPage()
            if not isinstance(classic.host_ui.handler, CustomHostUIHandler):
                classic.host_ui.handler = CustomHostUIHandler(classic.host_ui.handler)
    except Exception as exc:
        print(f"KickVoteManager: Error applying custom host ui: {exc}")


# ba_meta export babase.Plugin
class KickVotePlugin(babase.Plugin):
    """Kick vote management plugin."""

    def on_app_running(self) -> None:
        KickVoteManager.get()
        apply_custom_kick_votes()


def enable() -> None:
    """Enables the kick vote manager plugin."""
    KickVoteManager.get()
    apply_custom_kick_votes()
