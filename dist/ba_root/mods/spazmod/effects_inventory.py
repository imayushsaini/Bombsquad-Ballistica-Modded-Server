# Released under the MIT License. See LICENSE for details.
"""Unified Player Effects Inventory System.

Manages player effect ownership, equip states, expirations, and synchronization:
- Top 5 rank-based effects (temporary, e.g. 3 days)
- Shop-purchased effects (temporary, e.g. 6 days)
- Admin-gifted effects (permanent)
"""

from __future__ import annotations
import json
import threading
import time
from typing import Dict, List, Optional, Tuple

import setting
from repository.db import run_query

RANK_EFFECT_MAP: Dict[int, List[str]] = {
    1: ["rainbow", "shine"],
    2: ["sweat"],
    3: ["metal"],
    4: ["iceground"],
    5: ["fairydust"],
}

_inventory_lock = threading.Lock()
# Cache structure:
# { account_id: { effect_id: { "source": str, "expires_at": float|None, "is_equipped": bool, "added_at": float } } }
_inventory_cache: Dict[str, Dict[str, dict]] = {}


def init_effects_db() -> None:
    """Initializes SQLite tables for player effects inventory and runs migrations."""
    run_query("""
    CREATE TABLE IF NOT EXISTS player_effects_inventory (
        account_id TEXT,
        effect_id TEXT,
        source TEXT,
        expires_at REAL,
        is_equipped INTEGER DEFAULT 1,
        added_at REAL,
        PRIMARY KEY (account_id, effect_id)
    )
    """)
    run_query("""
    CREATE INDEX IF NOT EXISTS idx_pei_account ON player_effects_inventory(account_id)
    """)
    _migrate_existing_data()


def _migrate_existing_data() -> None:
    """Migrates existing perks from custom_perks and shop_equipped if not already migrated."""
    try:
        # 1. Migrate admin custom perks
        rows = run_query(
            "SELECT account_id, customeffects FROM custom_perks WHERE customeffects IS NOT NULL",
            fetch=True,
        )
        now = time.time()
        if rows:
            for acc_id, eff_data in rows:
                if not acc_id or not eff_data:
                    continue
                try:
                    eff_list = (
                        json.loads(eff_data)
                        if str(eff_data).startswith("[")
                        else [eff_data]
                    )
                except Exception:
                    eff_list = [eff_data]
                for eff in eff_list:
                    if eff:
                        eff = str(eff).strip().lower()
                        existing = run_query(
                            "SELECT 1 FROM player_effects_inventory WHERE account_id = ? AND effect_id = ?",
                            (acc_id, eff),
                            fetch=True,
                        )
                        if not existing:
                            run_query(
                                "INSERT INTO player_effects_inventory "
                                "(account_id, effect_id, source, expires_at, is_equipped, added_at) "
                                "VALUES (?, ?, 'admin', NULL, 1, ?)",
                                (acc_id, eff, now),
                            )
    except Exception as e:
        print(f"Error migrating custom_perks to player_effects_inventory: {e}")

    try:
        # 2. Migrate shop_equipped
        rows = run_query(
            "SELECT account_id, effect_id FROM shop_equipped WHERE effect_id IS NOT NULL",
            fetch=True,
        )
        now = time.time()
        if rows:
            for acc_id, eff_id in rows:
                if not acc_id or not eff_id or eff_id in ("none", "noeffect"):
                    continue
                eff = str(eff_id).strip().lower()
                existing = run_query(
                    "SELECT 1 FROM player_effects_inventory WHERE account_id = ? AND effect_id = ?",
                    (acc_id, eff),
                    fetch=True,
                )
                if not existing:
                    run_query(
                        "INSERT INTO player_effects_inventory "
                        "(account_id, effect_id, source, expires_at, is_equipped, added_at) "
                        "VALUES (?, ?, 'shop', ?, 1, ?)",
                        (acc_id, eff, now + 6 * 86400, now),
                    )
    except Exception as e:
        print(f"Error migrating shop_equipped to player_effects_inventory: {e}")


# Initialize table and migrations on module load
init_effects_db()


def format_duration(seconds: float) -> str:
    """Formats seconds into a human-friendly string like '3d 12h' or '45m'."""
    if seconds <= 0:
        return "Expired"
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{max(1, minutes)}m"


def _load_player_inventory(account_id: str) -> Dict[str, dict]:
    """Loads a player's effects inventory from SQLite into in-memory cache."""
    if not account_id:
        return {}

    with _inventory_lock:
        if account_id in _inventory_cache:
            return _inventory_cache[account_id]

    rows = run_query(
        "SELECT effect_id, source, expires_at, is_equipped, added_at "
        "FROM player_effects_inventory WHERE account_id = ?",
        (account_id,),
        fetch=True,
    )
    items: Dict[str, dict] = {}
    now = time.time()
    expired_ids = []

    if rows:
        for row in rows:
            eff_id, source, expires_at, is_equipped, added_at = row
            if expires_at is not None and expires_at <= now:
                expired_ids.append(eff_id)
                continue
            items[eff_id] = {
                "source": source,
                "expires_at": expires_at,
                "is_equipped": bool(is_equipped),
                "added_at": added_at or now,
            }

    if expired_ids:
        for eff_id in expired_ids:
            run_query(
                "DELETE FROM player_effects_inventory WHERE account_id = ? AND effect_id = ?",
                (account_id, eff_id),
            )

    with _inventory_lock:
        _inventory_cache[account_id] = items
        return _inventory_cache[account_id]


def cleanup_expired_effects(account_id: str) -> None:
    """Removes any expired effects for a player from memory and database."""
    if not account_id:
        return
    now = time.time()
    expired = []

    with _inventory_lock:
        player_items = _inventory_cache.get(account_id)
        if player_items:
            expired = [
                eff
                for eff, data in player_items.items()
                if data.get("expires_at") is not None and data["expires_at"] <= now
            ]
            for eff in expired:
                del player_items[eff]

    if expired:
        for eff in expired:
            run_query(
                "DELETE FROM player_effects_inventory WHERE account_id = ? AND effect_id = ?",
                (account_id, eff),
            )


def sync_rank_effects(account_id: str) -> None:
    """Awards temporary rank effects if player is currently in Top 5.

    When the temporary rank effect expires, it is removed; if the player is
    still qualified, it is re-awarded for a fresh duration.
    """
    if not account_id:
        return

    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)

    settings = setting.get_settings_data()
    if not settings.get("enablestats", True) or not settings.get(
        "enableTop5effects", True
    ):
        return

    try:
        from stats import mystats
        stats = mystats.get_cached_stats()
    except Exception:
        return

    if account_id not in stats:
        return

    rank = stats[account_id].get("rank")
    if rank not in RANK_EFFECT_MAP:
        return

    target_effects = RANK_EFFECT_MAP[rank]
    rank_duration = settings.get("rank_effect_duration_days", 3) * 86400
    max_equipped = settings.get("max_equipped_effects", 3)
    now = time.time()

    with _inventory_lock:
        player_items = _inventory_cache.setdefault(account_id, {})
        current_equipped = sum(
            1 for d in player_items.values() if d.get("is_equipped")
        )

        for eff in target_effects:
            if eff not in player_items:
                is_eq = current_equipped < max_equipped
                if is_eq:
                    current_equipped += 1
                player_items[eff] = {
                    "source": "rank",
                    "expires_at": now + rank_duration,
                    "is_equipped": is_eq,
                    "added_at": now,
                    "rank": rank,
                }
                run_query(
                    "INSERT OR REPLACE INTO player_effects_inventory "
                    "(account_id, effect_id, source, expires_at, is_equipped, added_at) "
                    "VALUES (?, ?, 'rank', ?, ?, ?)",
                    (account_id, eff, now + rank_duration, 1 if is_eq else 0, now),
                )
            else:
                existing = player_items[eff]
                # If rank effect had expired (cleaned up above), it was already re-added above.
                # If already present, don't overwrite user's manual equip/disable state.
                pass


def preload_player(account_id: str) -> None:
    """Preloads player's inventory in a background thread."""
    if not account_id:
        return
    import _thread

    def _worker():
        try:
            _load_player_inventory(account_id)
            cleanup_expired_effects(account_id)
            sync_rank_effects(account_id)
        except Exception as e:
            print(f"Error preloading effects inventory for {account_id}: {e}")

    _thread.start_new_thread(_worker, ())


def get_equipped_effects(account_id: str) -> List[str]:
    """Returns the list of currently equipped effect IDs for player Spaz."""
    if not account_id:
        return []

    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)
    sync_rank_effects(account_id)

    settings = setting.get_settings_data()
    max_equipped = settings.get("max_equipped_effects", 3)

    equipped = []
    now = time.time()
    with _inventory_lock:
        items = _inventory_cache.get(account_id, {})
        for eff_id, data in items.items():
            if data.get("is_equipped"):
                exp = data.get("expires_at")
                if exp is None or exp > now:
                    equipped.append(eff_id)

    return equipped[:max_equipped]


def add_shop_effect(account_id: str, effect_id: str) -> Tuple[bool, str]:
    """Purchases an effect from shop into inventory for configured duration.

    Player can only re-purchase an effect after the current rental has expired.
    """
    effect_id = effect_id.strip().lower()
    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)
    sync_rank_effects(account_id)

    settings = setting.get_settings_data()
    shop_days = settings.get("shop_effect_duration_days", 6)
    max_equipped = settings.get("max_equipped_effects", 3)
    duration_sec = shop_days * 86400
    now = time.time()

    with _inventory_lock:
        items = _inventory_cache.setdefault(account_id, {})
        if effect_id in items:
            item = items[effect_id]
            if item.get("expires_at") is None:
                return (
                    False,
                    f"You already own effect '{effect_id}' permanently as an admin gift!",
                )
            remaining = item["expires_at"] - now
            if remaining > 0:
                return (
                    False,
                    f"You already own effect '{effect_id}' ({format_duration(remaining)} remaining). You can buy it again only after it expires!",
                )

        current_equipped = sum(
            1 for d in items.values() if d.get("is_equipped")
        )
        is_eq = current_equipped < max_equipped
        expires_at = now + duration_sec

        items[effect_id] = {
            "source": "shop",
            "expires_at": expires_at,
            "is_equipped": is_eq,
            "added_at": now,
        }

    run_query(
        "INSERT OR REPLACE INTO player_effects_inventory "
        "(account_id, effect_id, source, expires_at, is_equipped, added_at) "
        "VALUES (?, ?, 'shop', ?, ?, ?)",
        (account_id, effect_id, expires_at, 1 if is_eq else 0, now),
    )

    if is_eq:
        msg = f"Equipped and valid for {shop_days} days. ({current_equipped + 1}/{max_equipped} equipped)"
    else:
        msg = f"Added to inventory (disabled, {max_equipped}/{max_equipped} slots full). Valid for {shop_days} days. Use '/effect enable {effect_id}' to equip."

    return True, msg


def add_admin_effect(account_id: str, effect_id: str) -> str:
    """Gifts an effect permanently into the player's inventory."""
    effect_id = effect_id.strip().lower()
    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)

    settings = setting.get_settings_data()
    max_equipped = settings.get("max_equipped_effects", 3)
    now = time.time()

    with _inventory_lock:
        items = _inventory_cache.setdefault(account_id, {})
        current_equipped = sum(
            1 for d in items.values() if d.get("is_equipped")
        )
        already_eq = items.get(effect_id, {}).get("is_equipped", False)
        is_eq = already_eq or (current_equipped < max_equipped)

        items[effect_id] = {
            "source": "admin",
            "expires_at": None,  # Permanent
            "is_equipped": is_eq,
            "added_at": now,
        }

    run_query(
        "INSERT OR REPLACE INTO player_effects_inventory "
        "(account_id, effect_id, source, expires_at, is_equipped, added_at) "
        "VALUES (?, ?, 'admin', NULL, ?, ?)",
        (account_id, effect_id, 1 if is_eq else 0, now),
    )
    return f"Effect '{effect_id}' gifted permanently."


def remove_effect(account_id: str, effect_id: Optional[str] = None) -> None:
    """Removes a specific effect or all effects from a player's inventory."""
    _load_player_inventory(account_id)
    with _inventory_lock:
        if account_id in _inventory_cache:
            if effect_id:
                _inventory_cache[account_id].pop(effect_id.lower(), None)
            else:
                _inventory_cache[account_id].clear()

    if effect_id:
        run_query(
            "DELETE FROM player_effects_inventory WHERE account_id = ? AND effect_id = ?",
            (account_id, effect_id.lower()),
        )
    else:
        run_query(
            "DELETE FROM player_effects_inventory WHERE account_id = ?",
            (account_id,),
        )


def equip_effect(account_id: str, effect_id: str) -> Tuple[bool, str]:
    """Enables/equips an effect from player's inventory up to max_equipped_effects."""
    effect_id = effect_id.strip().lower()
    if effect_id in ("none", "noeffect", "all", "clear", "off"):
        return True, disable_all_effects(account_id)

    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)
    sync_rank_effects(account_id)

    settings = setting.get_settings_data()
    max_equipped = settings.get("max_equipped_effects", 3)

    with _inventory_lock:
        items = _inventory_cache.get(account_id, {})
        if effect_id not in items:
            return (
                False,
                f"Error: You do not own effect '{effect_id}'. Purchase it from '/shop effects'!",
            )

        item = items[effect_id]
        if item.get("is_equipped"):
            return False, f"Effect '{effect_id}' is already equipped."

        current_equipped = sum(
            1 for d in items.values() if d.get("is_equipped")
        )
        if current_equipped >= max_equipped:
            return (
                False,
                f"Cannot equip '{effect_id}'. Maximum limit reached ({max_equipped}/{max_equipped} equipped). Unequip one first using '/effect disable <name>'.",
            )

        item["is_equipped"] = True
        equipped_count = current_equipped + 1

    run_query(
        "UPDATE player_effects_inventory SET is_equipped = 1 WHERE account_id = ? AND effect_id = ?",
        (account_id, effect_id),
    )
    return (
        True,
        f"Successfully equipped effect '{effect_id}' ({equipped_count}/{max_equipped} equipped).",
    )


def unequip_effect(account_id: str, effect_id: str) -> Tuple[bool, str]:
    """Disables/unequips an effect from player's active list."""
    effect_id = effect_id.strip().lower()
    if effect_id in ("all", "none"):
        return True, disable_all_effects(account_id)

    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)
    sync_rank_effects(account_id)

    settings = setting.get_settings_data()
    max_equipped = settings.get("max_equipped_effects", 3)

    with _inventory_lock:
        items = _inventory_cache.get(account_id, {})
        if effect_id not in items:
            return False, f"Error: Effect '{effect_id}' is not in your inventory."

        item = items[effect_id]
        if not item.get("is_equipped"):
            return False, f"Effect '{effect_id}' is not currently equipped."

        item["is_equipped"] = False
        current_equipped = sum(
            1 for d in items.values() if d.get("is_equipped")
        )

    run_query(
        "UPDATE player_effects_inventory SET is_equipped = 0 WHERE account_id = ? AND effect_id = ?",
        (account_id, effect_id),
    )
    return (
        True,
        f"Disabled effect '{effect_id}' ({current_equipped}/{max_equipped} equipped).",
    )


def disable_all_effects(account_id: str) -> str:
    """Disables all effects completely for a player."""
    _load_player_inventory(account_id)
    with _inventory_lock:
        items = _inventory_cache.get(account_id, {})
        for item in items.values():
            item["is_equipped"] = False

    run_query(
        "UPDATE player_effects_inventory SET is_equipped = 0 WHERE account_id = ?",
        (account_id,),
    )
    return "All effects disabled. You will have no effects active on your Spaz."


def get_inventory_display(account_id: str) -> str:
    """Formats player effect inventory into a chat-friendly string."""
    _load_player_inventory(account_id)
    cleanup_expired_effects(account_id)
    sync_rank_effects(account_id)

    settings = setting.get_settings_data()
    max_equipped = settings.get("max_equipped_effects", 3)
    now = time.time()

    with _inventory_lock:
        items = _inventory_cache.get(account_id, {})
        if not items:
            return (
                "--- Effects Inventory ---\n"
                "Your inventory is empty!\n"
                "• Buy effects from '/shop effects'\n"
                "• Reach Top 5 rank in /stats for free rewards"
            )

        equipped_list = []
        disabled_list = []

        for eff, data in items.items():
            src = data.get("source", "unknown")
            exp = data.get("expires_at")
            if exp is None:
                duration_str = "Permanent"
            else:
                rem = exp - now
                duration_str = f"{format_duration(rem)} left"

            if src == "admin":
                label = f"{eff} (Admin: {duration_str})"
            elif src == "rank":
                label = f"{eff} (Rank Top 5: {duration_str})"
            else:
                label = f"{eff} (Shop: {duration_str})"

            if data.get("is_equipped"):
                equipped_list.append(label)
            else:
                disabled_list.append(label)

    msg = f"--- Effects Inventory ({len(equipped_list)}/{max_equipped} equipped) ---\n"
    if equipped_list:
        msg += "Equipped:\n  " + "\n  ".join(f"• {x}" for x in equipped_list) + "\n"
    else:
        msg += "Equipped: (None)\n"

    if disabled_list:
        msg += "Disabled:\n  " + "\n  ".join(f"• {x}" for x in disabled_list) + "\n"

    msg += "Commands: /effect enable <name> | /effect disable <name> | /effect none"
    return msg
