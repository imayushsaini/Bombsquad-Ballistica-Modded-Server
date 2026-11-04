"""In-memory personal/local mute manager.

Allows players to opt-out of receiving chat messages from specific account IDs or clients.
Preferences are kept strictly in-memory and not persisted to storage.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING
import bascenev1 as bs
from serverdata import serverdata

if TYPE_CHECKING:
    from typing import Sequence


def _debug_log(msg: str) -> None:
    """Writes immediate log entry for local mute debugging."""
    try:
        base_dir = getattr(serverdata, "SERVER_DATA_PATH", "")
        if not base_dir:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(base_dir, "mute_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def resolve_keys(
    client_id: int | None = None, account_id: str | None = None
) -> set[str]:
    """Resolves all matching identifier aliases for a client/account."""
    keys: set[str] = set()

    if client_id is not None:
        keys.add(str(client_id))
        keys.add(f"c_{client_id}")

    if account_id:
        acc = str(account_id).strip().strip('"')
        if acc:
            keys.add(acc)
            keys.add(f'"{acc}"')

    # 1. Enrich from game roster
    try:
        roster = bs.get_game_roster()
    except Exception:
        roster = []

    for entry in roster:
        cid = entry.get("client_id")
        cacc = entry.get("account_id")
        clean_cacc = str(cacc).strip().strip('"') if cacc else None

        if client_id is not None and cid == client_id:
            if clean_cacc:
                keys.add(clean_cacc)
                keys.add(f'"{clean_cacc}"')

        if account_id and clean_cacc:
            target_clean = str(account_id).strip().strip('"')
            if clean_cacc == target_clean and cid is not None:
                keys.add(str(cid))
                keys.add(f"c_{cid}")

    # 2. Enrich from serverdata.recents
    try:
        recents = getattr(serverdata, "recents", [])
        for rec in recents:
            rcid = rec.get("client_id")
            rpbid = rec.get("pbid")
            clean_rpbid = str(rpbid).strip().strip('"') if rpbid else None

            if client_id is not None and rcid == client_id:
                if clean_rpbid:
                    keys.add(clean_rpbid)
                    keys.add(f'"{clean_rpbid}"')

            if account_id and clean_rpbid:
                target_clean = str(account_id).strip().strip('"')
                if clean_rpbid == target_clean and rcid is not None:
                    keys.add(str(rcid))
                    keys.add(f"c_{rcid}")
    except Exception:
        pass

    # 3. Enrich from foreground host session players
    try:
        session = bs.get_foreground_host_session()
        if session:
            for player in session.sessionplayers:
                dev = player.inputdevice
                if dev and client_id is not None and dev.client_id == client_id:
                    v1_id = getattr(player, "get_v1_account_id", None)
                    if callable(v1_id):
                        val = v1_id()
                        if val:
                            cval = str(val).strip().strip('"')
                            keys.add(cval)
                            keys.add(f'"{cval}"')
    except Exception:
        pass

    return keys


class LocalMuteManager:
    """In-memory store for personal/public player-to-player mutes.
    Stored on serverdata in-memory globals. Not persisted to disk or database.
    """

    _instance: LocalMuteManager | None = None

    @classmethod
    def get(cls) -> LocalMuteManager:
        """Returns the singleton instance of LocalMuteManager."""
        if cls._instance is None:
            cls._instance = LocalMuteManager()
        return cls._instance

    @property
    def _muted_map(self) -> dict[str, set[str]]:
        if not hasattr(serverdata, "local_muted_map") or not isinstance(
            serverdata.local_muted_map, dict
        ):
            serverdata.local_muted_map = {}
        return serverdata.local_muted_map

    @property
    def _muted_pairs(self) -> set[tuple[str, str]]:
        if not hasattr(serverdata, "local_muted_pairs") or not isinstance(
            serverdata.local_muted_pairs, set
        ):
            serverdata.local_muted_pairs = set()
        return serverdata.local_muted_pairs

    def _get_keys(
        self,
        identifier: str | int | Sequence[str | int] | set[str],
        account_id: str | None = None,
    ) -> set[str]:
        if isinstance(identifier, (set, list, tuple)):
            keys: set[str] = set()
            for item in identifier:
                keys.update(self._get_keys(item, account_id))
            return keys

        if isinstance(identifier, int):
            return resolve_keys(client_id=identifier, account_id=account_id)

        s = str(identifier).strip().strip('"')
        if s.startswith("c_"):
            try:
                return resolve_keys(client_id=int(s[2:]), account_id=account_id)
            except ValueError:
                pass
        try:
            cid = int(s)
            return resolve_keys(client_id=cid, account_id=account_id)
        except ValueError:
            pass

        return resolve_keys(account_id=s)

    def is_muted(
        self,
        viewer: str | int | Sequence[str | int] | set[str],
        target: str | int | Sequence[str | int] | set[str],
        viewer_acc: str | None = None,
        target_acc: str | None = None,
    ) -> bool:
        """Checks if viewer has muted target."""
        v_keys = self._get_keys(viewer, viewer_acc)
        t_keys = self._get_keys(target, target_acc)
        if not v_keys or not t_keys:
            return False

        # 1. Check pair set
        for vk in v_keys:
            for tk in t_keys:
                if (vk, tk) in self._muted_pairs:
                    return True

        # 2. Check map
        for vk in v_keys:
            muted_set = self._muted_map.get(vk)
            if muted_set and (muted_set & t_keys):
                return True

        return False

    def toggle_mute(
        self,
        viewer: str | int | Sequence[str | int] | set[str],
        target: str | int | Sequence[str | int] | set[str],
        viewer_acc: str | None = None,
        target_acc: str | None = None,
    ) -> bool:
        """Toggles mute status for target by viewer.
        Returns True if now muted, False if now unmuted.
        """
        v_keys = self._get_keys(viewer, viewer_acc)
        t_keys = self._get_keys(target, target_acc)
        if not v_keys or not t_keys:
            _debug_log(
                f"toggle_mute failed: empty keys v={viewer}({viewer_acc})->{v_keys}, "
                f"t={target}({target_acc})->{t_keys}"
            )
            return False

        already_muted = self.is_muted(v_keys, t_keys)
        if already_muted:
            # Unmute: remove all combinations
            for vk in v_keys:
                if vk in self._muted_map:
                    self._muted_map[vk].difference_update(t_keys)
                    if not self._muted_map[vk]:
                        del self._muted_map[vk]
                for tk in t_keys:
                    self._muted_pairs.discard((vk, tk))
            _debug_log(
                f"UNMUTED: viewer={viewer}({viewer_acc}), target={target}({target_acc}), "
                f"v_keys={v_keys}, t_keys={t_keys}"
            )
            return False
        else:
            # Mute: add all combinations
            for vk in v_keys:
                self._muted_map.setdefault(vk, set()).update(t_keys)
                for tk in t_keys:
                    self._muted_pairs.add((vk, tk))
            _debug_log(
                f"MUTED: viewer={viewer}({viewer_acc}), target={target}({target_acc}), "
                f"v_keys={v_keys}, t_keys={t_keys}, pairs_count={len(self._muted_pairs)}"
            )
            return True

    def get_muted(self, viewer: str | int) -> set[str]:
        """Returns all identifiers muted by viewer."""
        v_keys = self._get_keys(viewer)
        result: set[str] = set()
        for vk in v_keys:
            result.update(self._muted_map.get(vk, set()))
            for pair_v, pair_t in self._muted_pairs:
                if pair_v == vk:
                    result.add(pair_t)
        return result


def check_personal_mute_and_send(
    msg: str,
    sender_client_id: int,
    sender_account_id: str,
    display_name: str,
) -> str | None:
    """Checks if any connected player has locally muted sender.
    If yes, dispatches chatmessage only to unmuted players and returns None.
    If no, returns msg for standard C++ broadcast.
    """
    mute_mgr = LocalMuteManager.get()
    try:
        roster = bs.get_game_roster()
    except Exception as exc:
        _debug_log(f"check_personal_mute_and_send roster error: {exc}")
        return msg

    sender_keys = resolve_keys(client_id=sender_client_id, account_id=sender_account_id)

    muted_clients: set[int] = set()
    all_remote_clients: list[int] = []

    for entry in roster:
        cid = entry.get("client_id")
        if cid is None or cid < 0:
            continue
        all_remote_clients.append(cid)
        if cid == sender_client_id:
            continue
        cacc = entry.get("account_id")
        viewer_keys = resolve_keys(client_id=cid, account_id=cacc)
        if mute_mgr.is_muted(viewer=viewer_keys, target=sender_keys):
            muted_clients.add(cid)

    # Also check if host (-1) muted the sender
    host_keys = resolve_keys(client_id=-1)
    if mute_mgr.is_muted(viewer=host_keys, target=sender_keys):
        muted_clients.add(-1)

    # If nobody muted this sender, let C++ handle default broadcasting
    if not muted_clients:
        return msg

    # Someone muted this sender: send only to clients who did NOT mute
    # Note: sender_client_id is never in muted_clients, so sender receives their message
    allowed_clients = [cid for cid in all_remote_clients if cid not in muted_clients]
    _debug_log(
        f"FILTERING CHAT: sender={sender_client_id}({sender_account_id}), "
        f"muted={muted_clients}, allowed={allowed_clients}, msg='{msg}'"
    )

    if allowed_clients:
        try:
            bs.chatmessage(msg, clients=allowed_clients, sender_override=display_name)
        except Exception as exc1:
            try:
                import _bascenev1
                _bascenev1.chatmessage(
                    msg, clients=allowed_clients, sender_override=display_name
                )
            except Exception as exc2:
                _debug_log(f"chatmessage send error: {exc1} / {exc2}")

    # Return None so C++ does NOT broadcast to all clients
    return None
