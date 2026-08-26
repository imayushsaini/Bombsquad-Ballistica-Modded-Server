# Released under the MIT License. See LICENSE for details.
"""Database operations and schema initialization for player data."""

import json
import copy
from repository.db import run_query, get_connection


def init_db():
    """Initializes all database tables with complete schemas at once."""
    # 1. Full profiles table
    run_query("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        v2Tag TEXT UNIQUE,
        account_id TEXT UNIQUE,
        display_string TEXT,
        profiles TEXT,
        name TEXT,
        accountAge TEXT,
        creationDate TEXT,
        registerOn REAL,
        spamCount INTEGER,
        lastSpam REAL,
        totaltimeplayer REAL,
        warnCount INTEGER,
        lastWarned REAL,
        verified INTEGER,
        rejoincount INTEGER,
        lastJoin REAL,
        lastIP TEXT,
        deviceUUID TEXT,
        server_profile_created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Schema migration helper: ensure all required columns are present in case the table existed previously
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(profiles)")
        existing_cols = {row[1] for row in cur.fetchall()}
        conn.close()
    except Exception as e:
        print(f"Error checking table schema: {e}")
        existing_cols = set()

    if existing_cols:
        expected_columns = {
            "account_id": "TEXT",
            "display_string": "TEXT",
            "profiles": "TEXT",
            "name": "TEXT",
            "accountAge": "TEXT",
            "creationDate": "TEXT",
            "registerOn": "REAL",
            "spamCount": "INTEGER",
            "lastSpam": "REAL",
            "totaltimeplayer": "REAL",
            "warnCount": "INTEGER",
            "lastWarned": "REAL",
            "verified": "INTEGER",
            "rejoincount": "INTEGER",
            "lastJoin": "REAL",
            "deviceUUID": "TEXT"
        }
        for col_name, col_type in expected_columns.items():
            if col_name not in existing_cols:
                try:
                    run_query(
                        f"ALTER TABLE profiles ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Error adding column {col_name} to profiles: {e}")

    # Ensure v2Tag and account_id have unique indices for conflict resolution
    run_query(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_v2Tag ON profiles(v2Tag)")
    run_query(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_account_id ON profiles(account_id)")

    # 2. roles table
    run_query("""
    CREATE TABLE IF NOT EXISTS roles (
        name TEXT PRIMARY KEY,
        tag TEXT,
        tagcolor TEXT,
        commands TEXT,
        ids TEXT
    )
    """)

    # 3. custom_perks table
    run_query("""
    CREATE TABLE IF NOT EXISTS custom_perks (
        account_id TEXT PRIMARY KEY,
        customtag TEXT,
        customeffects TEXT
    )
    """)

    # 4. blacklist table
    run_query("""
    CREATE TABLE IF NOT EXISTS blacklist (
        type TEXT,
        target TEXT,
        till TEXT,
        reason TEXT,
        PRIMARY KEY (type, target)
    )
    """)

    # 5. whitelist table
    run_query("""
    CREATE TABLE IF NOT EXISTS whitelist (
        account_id TEXT PRIMARY KEY,
        display_names TEXT
    )
    """)


init_db()


def get_profile(v2Tag: str) -> dict | None:
    """Returns basic profile information. Keeps compatibility with servercheck.py."""
    rows = run_query(
        "SELECT id, v2Tag, lastIP FROM profiles WHERE v2Tag = ?",
        (v2Tag,),
        fetch=True,
    )
    if rows:
        return {
            'id': rows[0][0],
            'v2Tag': rows[0][1],
            'lastIP': rows[0][2],
        }
    return None


def upsert_ip(v2Tag: str, ip: str) -> None:
    """Inserts or updates the last IP address for an account. Keeps compatibility."""
    run_query("""
    INSERT INTO profiles (v2Tag, account_id, lastIP) VALUES (?, ?, ?)
    ON CONFLICT(account_id) DO UPDATE SET lastIP=excluded.lastIP
    """, (v2Tag, v2Tag, ip))


# --- Database CRUD helpers to map JSON structure to SQLite ---

def load_all_profiles() -> dict:
    """Loads all player profiles from database into memory dictionary structure."""
    rows = run_query("""
        SELECT v2Tag, display_string, profiles, name,
               accountAge, creationDate, registerOn,
               spamCount, lastSpam, totaltimeplayer, warnCount, lastWarned,
               verified, rejoincount, lastJoin, lastIP, deviceUUID
        FROM profiles
    """, fetch=True)

    profiles_dict = {}
    if not rows:
        return profiles_dict

    for r in rows:
        v2Tag = r[0]
        if not v2Tag:
            continue

        try:
            display_string = json.loads(r[1]) if r[1] else []
        except Exception:
            display_string = []

        try:
            profiles = json.loads(r[2]) if r[2] else []
        except Exception:
            profiles = []

        profiles_dict[v2Tag] = {
            "display_string": display_string,
            "profiles": profiles,
            "name": r[3],
            "accountAge": r[4],
            "creationDate": r[5],
            "registerOn": r[6],
            "spamCount": r[7] or 0,
            "lastSpam": r[8],
            "totaltimeplayer": r[9] or 0.0,
            "warnCount": r[10] or 0,
            "lastWarned": r[11],
            "verified": bool(r[12]) if r[12] is not None else False,
            "rejoincount": r[13] or 1,
            "lastJoin": r[14],
            "lastIP": r[15],
            "deviceUUID": r[16]
        }
    return profiles_dict


def save_all_profiles(profiles_dict: dict) -> None:
    """Bulk upserts player profiles to the database."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        for account_id, p in profiles_dict.items():
            display_string_str = json.dumps(p.get("display_string", []))
            profiles_str = json.dumps(p.get("profiles", []))
            verified = 1 if p.get("verified") else 0

            cur.execute("""
                INSERT INTO profiles (
                    v2Tag, account_id, display_string, profiles, name,
                    accountAge, creationDate, registerOn,
                    spamCount, lastSpam, totaltimeplayer, warnCount, lastWarned,
                    verified, rejoincount, lastJoin, lastIP, deviceUUID
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    display_string=excluded.display_string,
                    profiles=excluded.profiles,
                    name=excluded.name,
                    accountAge=excluded.accountAge,
                    creationDate=excluded.creationDate,
                    registerOn=excluded.registerOn,
                    spamCount=excluded.spamCount,
                    lastSpam=excluded.lastSpam,
                    totaltimeplayer=excluded.totaltimeplayer,
                    warnCount=excluded.warnCount,
                    lastWarned=excluded.lastWarned,
                    verified=excluded.verified,
                    rejoincount=excluded.rejoincount,
                    lastJoin=excluded.lastJoin,
                    lastIP=COALESCE(excluded.lastIP, profiles.lastIP),
                    deviceUUID=COALESCE(excluded.deviceUUID, profiles.deviceUUID),
                    v2Tag=COALESCE(excluded.v2Tag, profiles.v2Tag)
            """, (
                account_id, account_id, display_string_str, profiles_str, p.get(
                    "name"),
                p.get("accountAge"), p.get("creationDate"),
                p.get("registerOn"), p.get("spamCount", 0),
                p.get("lastSpam"), p.get(
                    "totaltimeplayer", 0), p.get("warnCount", 0),
                p.get("lastWarned"), verified, p.get("rejoincount", 1),
                p.get("lastJoin"), p.get("lastIP"), p.get("deviceUUID")
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving profiles to DB: {e}")
        raise
    finally:
        conn.close()


def save_profile_single(account_id: str, p: dict) -> None:
    """Saves or updates a single player profile in the database (non-blocking)."""
    import _thread
    # Make a copy of the dictionary to avoid mutating issues in the thread
    p_copy = copy.deepcopy(p)
    _thread.start_new_thread(_save_profile_single_thread, (account_id, p_copy))


def _save_profile_single_thread(account_id: str, p: dict) -> None:
    """Internal target to run single profile insert/update inside a background thread."""
    display_string_str = json.dumps(p.get("display_string", []))
    profiles_str = json.dumps(p.get("profiles", []))
    verified = 1 if p.get("verified") else 0

    try:
        run_query("""
            INSERT INTO profiles (
                v2Tag, account_id, display_string, profiles, name,
                accountAge, creationDate, registerOn,
                spamCount, lastSpam, totaltimeplayer, warnCount, lastWarned,
                verified, rejoincount, lastJoin, lastIP, deviceUUID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(account_id) DO UPDATE SET
                display_string=excluded.display_string,
                profiles=excluded.profiles,
                name=excluded.name,
                accountAge=excluded.accountAge,
                creationDate=excluded.creationDate,
                registerOn=excluded.registerOn,
                spamCount=excluded.spamCount,
                lastSpam=excluded.lastSpam,
                totaltimeplayer=excluded.totaltimeplayer,
                warnCount=excluded.warnCount,
                lastWarned=excluded.lastWarned,
                verified=excluded.verified,
                rejoincount=excluded.rejoincount,
                lastJoin=excluded.lastJoin,
                lastIP=COALESCE(excluded.lastIP, profiles.lastIP),
                deviceUUID=COALESCE(excluded.deviceUUID, profiles.deviceUUID),
                v2Tag=COALESCE(excluded.v2Tag, profiles.v2Tag)
        """, (
            account_id, account_id, display_string_str, profiles_str, p.get(
                "name"),
            p.get("accountAge"), p.get("creationDate"),
            p.get("registerOn"), p.get("spamCount", 0),
            p.get("lastSpam"), p.get(
                "totaltimeplayer", 0), p.get("warnCount", 0),
            p.get("lastWarned"), verified, p.get("rejoincount", 1),
            p.get("lastJoin"), p.get("lastIP"), p.get("deviceUUID")
        ))
    except Exception as e:
        print(f"Error saving single profile to DB in thread: {e}")


def get_profile_by_acc_id(account_id: str) -> ProfileDictProxy | None:
    """Loads a single profile by account_id and returns it wrapped in a ProfileDictProxy."""
    rows = run_query("""
        SELECT v2Tag, display_string, profiles, name,
               accountAge, creationDate, registerOn,
               spamCount, lastSpam, totaltimeplayer, warnCount, lastWarned,
               verified, rejoincount, lastJoin, lastIP, deviceUUID
        FROM profiles
        WHERE account_id = ? OR v2Tag = ?
    """, (account_id, account_id), fetch=True)

    if not rows:
        return None

    r = rows[0]
    try:
        display_string = json.loads(r[1]) if r[1] else []
    except Exception:
        display_string = []

    try:
        profiles = json.loads(r[2]) if r[2] else []
    except Exception:
        profiles = []

    return ProfileDictProxy(account_id, {
        "display_string": display_string,
        "profiles": profiles,
        "name": r[3],
        "accountAge": r[4],
        "creationDate": r[5],
        "registerOn": r[6],
        "spamCount": r[7] or 0,
        "lastSpam": r[8],
        "totaltimeplayer": r[9] or 0.0,
        "warnCount": r[10] or 0,
        "lastWarned": r[11],
        "verified": bool(r[12]) if r[12] is not None else False,
        "rejoincount": r[13] or 1,
        "lastJoin": r[14],
        "lastIP": r[15],
        "deviceUUID": r[16]
    })


def load_roles() -> dict:
    """Loads all roles from database."""
    rows = run_query(
        "SELECT name, tag, tagcolor, commands, ids FROM roles", fetch=True)
    roles_dict = {}
    if not rows:
        return roles_dict

    for r in rows:
        name = r[0]
        try:
            tagcolor = json.loads(r[2]) if r[2] else [1, 1, 1]
        except Exception:
            tagcolor = [1, 1, 1]

        try:
            commands = json.loads(r[3]) if r[3] else []
        except Exception:
            commands = []

        try:
            ids = json.loads(r[4]) if r[4] else []
        except Exception:
            ids = []

        roles_dict[name] = {
            "tag": r[1],
            "tagcolor": tagcolor,
            "commands": commands,
            "ids": ids
        }
    return roles_dict


def run_transaction(queries_list: list) -> None:
    """Executes multiple queries in a single transaction with database lock retry logic."""
    import sqlite3
    import time
    import random
    from repository.db import get_connection
    MAX_RETRIES = 5
    RETRY_DELAY = (0.1, 0.5)

    retries = 0
    while True:
        try:
            conn = get_connection()
            cur = conn.cursor()
            for query, params in queries_list:
                cur.execute(query, params)
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                retries += 1
                if retries > MAX_RETRIES:
                    raise RuntimeError(
                        "Max retries exceeded due to DB lock") from e
                time.sleep(random.uniform(*RETRY_DELAY))
            else:
                raise


def save_roles(roles_dict: dict) -> None:
    """Saves all roles to database."""
    queries = [("DELETE FROM roles", ())]
    for name, r in roles_dict.items():
        tagcolor_str = json.dumps(r.get("tagcolor", [1, 1, 1]))
        commands_str = json.dumps(r.get("commands", []))
        ids_str = json.dumps(r.get("ids", []))
        queries.append(("""
            INSERT INTO roles (name, tag, tagcolor, commands, ids)
            VALUES (?, ?, ?, ?, ?)
        """, (name, r.get("tag"), tagcolor_str, commands_str, ids_str)))
    run_transaction(queries)


def load_custom() -> dict:
    """Loads custom tags and effects from database."""
    rows = run_query(
        "SELECT account_id, customtag, customeffects FROM custom_perks", fetch=True)
    custom_dict = {"customtag": {}, "customeffects": {}}
    if not rows:
        return custom_dict

    for r in rows:
        acc_id = r[0]
        if r[1] is not None:
            custom_dict["customtag"][acc_id] = r[1]
        if r[2] is not None:
            try:
                effects = json.loads(r[2])
                custom_dict["customeffects"][acc_id] = effects
            except Exception:
                pass
    return custom_dict


def save_custom(custom_dict: dict) -> None:
    """Saves custom tags and effects to database."""
    queries = [("DELETE FROM custom_perks", ())]
    tags = custom_dict.get("customtag", {})
    effects = custom_dict.get("customeffects", {})
    all_accs = set(tags.keys()) | set(effects.keys())

    for acc_id in all_accs:
        tag = tags.get(acc_id)
        eff_list = effects.get(acc_id)
        eff_str = json.dumps(eff_list) if eff_list is not None else None
        queries.append(("""
            INSERT INTO custom_perks (account_id, customtag, customeffects)
            VALUES (?, ?, ?)
        """, (acc_id, tag, eff_str)))
    run_transaction(queries)


def load_blacklist() -> dict:
    """Loads blacklist from database."""
    rows = run_query(
        "SELECT type, target, till, reason FROM blacklist", fetch=True)
    blacklist = {
        "ban": {"ids": {}, "ips": {}, "deviceids": {}},
        "muted-ids": {},
        "kick-vote-disabled": {}
    }
    if not rows:
        return blacklist

    for r in rows:
        b_type, target, till, reason = r[0], r[1], r[2], r[3]
        entry = {"till": till, "reason": reason}
        if b_type == 'ban_id':
            blacklist["ban"]["ids"][target] = entry
        elif b_type == 'ban_ip':
            blacklist["ban"]["ips"][target] = entry
        elif b_type == 'ban_deviceid':
            blacklist["ban"]["deviceids"][target] = entry
        elif b_type == 'mute':
            blacklist["muted-ids"][target] = entry
        elif b_type == 'kickvote':
            blacklist["kick-vote-disabled"][target] = entry

    return blacklist


def save_blacklist(blacklist_dict: dict) -> None:
    """Saves blacklist to database."""
    queries = [("DELETE FROM blacklist", ())]

    for target, val in blacklist_dict.get("ban", {}).get("ids", {}).items():
        queries.append(("INSERT INTO blacklist (type, target, till, reason) VALUES ('ban_id', ?, ?, ?)",
                        (target, val.get("till"), val.get("reason"))))

    for target, val in blacklist_dict.get("ban", {}).get("ips", {}).items():
        queries.append(("INSERT INTO blacklist (type, target, till, reason) VALUES ('ban_ip', ?, ?, ?)",
                        (target, val.get("till"), val.get("reason"))))

    for target, val in blacklist_dict.get("ban", {}).get("deviceids", {}).items():
        queries.append(("INSERT INTO blacklist (type, target, till, reason) VALUES ('ban_deviceid', ?, ?, ?)",
                        (target, val.get("till"), val.get("reason"))))

    for target, val in blacklist_dict.get("muted-ids", {}).items():
        queries.append(("INSERT INTO blacklist (type, target, till, reason) VALUES ('mute', ?, ?, ?)",
                        (target, val.get("till"), val.get("reason"))))

    for target, val in blacklist_dict.get("kick-vote-disabled", {}).items():
        queries.append(("INSERT INTO blacklist (type, target, till, reason) VALUES ('kickvote', ?, ?, ?)",
                        (target, val.get("till"), val.get("reason"))))
    run_transaction(queries)


def load_whitelist() -> list:
    """Loads whitelist from database."""
    rows = run_query("SELECT account_id FROM whitelist", fetch=True)
    if not rows:
        return []
    return [r[0] for r in rows if r[0]]


def save_whitelist(whitelist_list: list) -> None:
    """Saves whitelist to database."""
    queries = [("DELETE FROM whitelist", ())]
    for account_id in whitelist_list:
        queries.append(
            ("INSERT INTO whitelist (account_id) VALUES (?)", (account_id,)))
    run_transaction(queries)


class ProfileDictProxy(dict):
    """A dictionary wrapper for a player profile that writes changes to the DB on modification."""

    def __init__(self, account_id: str, initial_dict: dict):
        import copy
        super().__init__(initial_dict)
        self._account_id = account_id

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        save_profile_single(self._account_id, dict(self))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        save_profile_single(self._account_id, dict(self))


class SQLiteLazyProfiles(dict):
    """A dictionary-like wrapper to lazy-load profiles from SQLite on demand."""

    def __init__(self):
        super().__init__()

    def __contains__(self, key):
        if not isinstance(key, str):
            return False
        return get_profile_by_acc_id(key) is not None

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError(key)
        p = get_profile_by_acc_id(key)
        if p is None:
            raise KeyError(key)
        return p

    def get(self, key, default=None):
        if not isinstance(key, str):
            return default
        p = get_profile_by_acc_id(key)
        return p if p is not None else default

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Keys must be strings (account IDs)")
        save_profile_single(key, value)

    def items(self):
        return load_all_profiles().items()

    def keys(self):
        return load_all_profiles().keys()

    def values(self):
        return load_all_profiles().values()

    def __iter__(self):
        return iter(load_all_profiles())

    def __len__(self):
        try:
            rows = run_query("SELECT count(*) FROM profiles", fetch=True)
            return rows[0][0] if rows else 0
        except Exception:
            return 0
