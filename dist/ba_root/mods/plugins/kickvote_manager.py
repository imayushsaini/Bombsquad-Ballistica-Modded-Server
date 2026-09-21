from __future__ import annotations

import _thread
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import babase
import bascenev1 as bs

if TYPE_CHECKING:
    from typing import Sequence


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


# ba_meta export babase.Plugin
class KickVotePlugin(babase.Plugin):
    """Kick vote management plugin."""

    def on_app_running(self) -> None:
        KickVoteManager.get()


def enable() -> None:
    """Enables the kick vote manager plugin."""
    KickVoteManager.get()
