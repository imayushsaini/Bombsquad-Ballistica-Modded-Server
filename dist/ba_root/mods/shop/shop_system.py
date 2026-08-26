# Released under the MIT License. See LICENSE for details.
"""Shop system logic and database operations with in-memory caching."""

from repository.db import run_query

EFFECTS_SHOP = {
    "spark": {"cost": 150, "description": "Spark effect around you"},
    "sparkground": {"cost": 150, "description": "Spark particles on ground"},
    "sweat": {"cost": 100, "description": "Sweating particles"},
    "sweatground": {"cost": 100, "description": "Sweating on ground"},
    "distortion": {"cost": 250, "description": "Distortion and smoke"},
    "glow": {"cost": 200, "description": "Glow with pink light"},
    "shine": {"cost": 200, "description": "Shining body color"},
    "highlightshine": {"cost": 200, "description": "Shining highlight color"},
    "scorch": {"cost": 250, "description": "Color-changing floor scorch"},
    "ice": {"cost": 250, "description": "Ice trails around you"},
    "iceground": {"cost": 200, "description": "Ice on the ground"},
    "slime": {"cost": 150, "description": "Slime particles"},
    "metal": {"cost": 150, "description": "Metal particles"},
    "splinter": {"cost": 150, "description": "Splinter particles"},
    "rainbow": {"cost": 350, "description": "Rainbow highlight color"},
    "fairydust": {"cost": 250, "description": "Fairy dust trailing"},
    "firespark": {"cost": 400, "description": "Fire spark burst"},
    "smoketrail": {"cost": 180, "description": "Puffing trail of thin smoke"},
    "frosty": {"cost": 300, "description": "Cold freezing ice trail and shards"},
    "hyper": {"cost": 320, "description": "Electrical sparks and light distortion"},
    "magical": {"cost": 350, "description": "Magical flashes and fairy dust"},
    "toxic": {"cost": 220, "description": "Dripping green slime and noxious fumes"},
    "heavymetal": {"cost": 240, "description": "Clanking metal chunks and sparks"},
    "meteor": {"cost": 380, "description": "Hot rock shards and burning sparks"},
}


def migrate_shop_db():
    """Performs schema migrations for shop tables (e.g. adding columns or new tables)."""
    from repository.db import get_connection
    # 1. Ensure usages_left column exists in shop_purchases
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(shop_purchases)")
        existing_cols = {row[1] for row in cur.fetchall()}
        conn.close()
    except Exception as e:
        print(f"Error checking shop_purchases schema: {e}")
        existing_cols = set()

    if existing_cols and "usages_left" not in existing_cols:
        try:
            run_query("ALTER TABLE shop_purchases ADD COLUMN usages_left INTEGER DEFAULT 3")
        except Exception as e:
            print(f"Error adding usages_left to shop_purchases: {e}")

    # 2. Ensure shop_transactions table exists
    run_query("""
    CREATE TABLE IF NOT EXISTS shop_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT,
        action TEXT,
        amount INTEGER DEFAULT 0,
        item_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)


def log_transaction(account_id: str, action: str, amount: int = 0, item_id: str = None) -> None:
    """Logs an economy transaction to the database."""
    try:
        run_query("""
            INSERT INTO shop_transactions (account_id, action, amount, item_id)
            VALUES (?, ?, ?, ?)
        """, (account_id, action, amount, item_id))
    except Exception as e:
        print(f"Error logging transaction: {e}")


def init_shop_db():
    """Initializes SQLite tables for the shop system."""
    run_query("""
    CREATE TABLE IF NOT EXISTS shop_bank (
        account_id TEXT PRIMARY KEY,
        tickets INTEGER DEFAULT 0
    )
    """)
    run_query("""
    CREATE TABLE IF NOT EXISTS shop_purchases (
        account_id TEXT,
        item_type TEXT,
        item_id TEXT,
        usages_left INTEGER DEFAULT 3,
        PRIMARY KEY (account_id, item_type, item_id)
    )
    """)
    run_query("""
    CREATE TABLE IF NOT EXISTS shop_equipped (
        account_id TEXT PRIMARY KEY,
        effect_id TEXT
    )
    """)
    run_query("""
    CREATE TABLE IF NOT EXISTS shop_claims (
        account_id TEXT PRIMARY KEY,
        last_claim REAL
    )
    """)
    migrate_shop_db()


# Ensure database tables are created when module is imported
init_shop_db()


# Caches to avoid database queries on the game main thread
_purchased_commands_cache = {}  # { account_id: set(command_names) }
_equipped_effects_cache = {}    # { account_id: effect_name_str }


def preload_player(account_id: str) -> None:
    """Spawns a thread to pre-load a player's shop purchases and equipped effects into cache."""
    if not account_id:
        return
    import _thread
    _thread.start_new_thread(_preload_player_thread, (account_id,))


def _preload_player_thread(account_id: str) -> None:
    """Worker to fetch player data from SQLite and populate in-memory cache."""
    try:
        # Load purchased commands
        cmd_rows = run_query(
            "SELECT item_id FROM shop_purchases WHERE account_id = ? AND item_type = 'command'",
            (account_id,),
            fetch=True
        )
        cmds = {row[0] for row in cmd_rows} if cmd_rows else set()
        _purchased_commands_cache[account_id] = cmds

        # Load equipped effect
        eff_rows = run_query(
            "SELECT effect_id FROM shop_equipped WHERE account_id = ?",
            (account_id,),
            fetch=True
        )
        effect = eff_rows[0][0] if eff_rows else None
        _equipped_effects_cache[account_id] = effect
    except Exception as e:
        print(f"Exception in _preload_player_thread for {account_id}: {e}")


def get_tickets(account_id: str) -> int:
    """Returns the ticket balance of a player, starting them with 100 if new."""
    if not account_id:
        return 0
    rows = run_query("SELECT tickets FROM shop_bank WHERE account_id = ?", (account_id,), fetch=True)
    if rows:
        return rows[0][0]
    else:
        # Give starting tickets
        run_query("INSERT OR IGNORE INTO shop_bank (account_id, tickets) VALUES (?, ?)", (account_id, 100))
        return 100


def _add_tickets_no_log(account_id: str, amount: int) -> None:
    """Internal helper to modify tickets directly in the database without logging."""
    get_tickets(account_id)
    run_query("UPDATE shop_bank SET tickets = tickets + ? WHERE account_id = ?", (amount, account_id))


def add_tickets(account_id: str, amount: int) -> int:
    """Modifies (adds/subtracts) the tickets of a player."""
    if not account_id:
        return 0
    _add_tickets_no_log(account_id, amount)
    action = "add_tickets" if amount >= 0 else "remove_tickets"
    log_transaction(account_id, action, abs(amount))
    return get_tickets(account_id)


def transfer_tickets(sender_id: str, receiver_id: str, amount: int) -> str:
    """Transfers tickets between two players."""
    if sender_id == receiver_id:
        return "Error: You cannot transfer tickets to yourself."
    if amount <= 0:
        return "Error: Amount must be a positive integer."

    sender_balance = get_tickets(sender_id)
    if sender_balance < amount:
        return f"Error: Insufficient balance. You only have {sender_balance} tickets."

    _add_tickets_no_log(sender_id, -amount)
    _add_tickets_no_log(receiver_id, amount)
    log_transaction(sender_id, "transfer_send", amount, receiver_id)
    log_transaction(receiver_id, "transfer_receive", amount, sender_id)
    return "success"


def buy_item(account_id: str, item_name: str) -> str:
    """Handles purchase of commands or effects by players."""
    item_name = item_name.strip().lower()

    # 1. Check if it's a configured effect
    is_effect = item_name in EFFECTS_SHOP

    # 2. Check if it's a registered shop command
    from chathandle.chatcommands.commands.registry import registry
    cmd = registry.get_command(item_name)
    is_command = cmd is not None and cmd.shop_cost > 0

    if not is_effect and not is_command:
        return f"Error: '{item_name}' is not available for purchase in the shop."

    if is_effect:
        item_type = "effect"
        item_id = item_name
        cost = EFFECTS_SHOP[item_name]["cost"]
        display_name = f"effect '{item_name}'"
    else:
        item_type = "command"
        item_id = cmd.names[0]  # Store using the primary name
        cost = cmd.shop_cost
        display_name = f"command '/{item_id}'"

    # 3. Check if already owned
    rows = run_query(
        "SELECT usages_left FROM shop_purchases WHERE account_id = ? AND item_type = ? AND item_id = ?",
        (account_id, item_type, item_id),
        fetch=True
    )
    if rows:
        if item_type == "effect" or (rows[0][0] is not None and rows[0][0] > 0):
            return f"You have already purchased the {display_name}."

    # 4. Check if they have enough tickets
    balance = get_tickets(account_id)
    if balance < cost:
        return f"Insufficient tickets! {display_name} costs {cost} tickets, but you only have {balance}."

    # 5. Process transaction
    _add_tickets_no_log(account_id, -cost)
    run_query(
        "INSERT OR REPLACE INTO shop_purchases (account_id, item_type, item_id, usages_left) VALUES (?, ?, ?, ?)",
        (account_id, item_type, item_id, 3 if item_type == "command" else None)
    )
    log_transaction(account_id, "purchase", cost, f"{item_type}:{item_id}")

    # Update in-memory cache
    if item_type == "command":
        if account_id not in _purchased_commands_cache:
            _purchased_commands_cache[account_id] = set()
        _purchased_commands_cache[account_id].add(item_id)
    elif item_type == "effect":
        if account_id not in _purchased_commands_cache:
            _purchased_commands_cache[account_id] = set()
        _purchased_commands_cache[account_id].add(item_id)

    # 6. If effect, equip it automatically
    if is_effect:
        equip_effect(account_id, item_id)
        return f"Successfully purchased and equipped {display_name} for {cost} tickets! Remaining balance: {balance - cost}."

    return f"Successfully purchased {display_name} for {cost} tickets! remaining 3 usages. Remaining balance: {balance - cost}."


def equip_effect(account_id: str, effect_name: str) -> str:
    """Equips an effect if owned."""
    effect_name = effect_name.strip().lower()

    if effect_name in ("none", "noeffect"):
        run_query("INSERT OR REPLACE INTO shop_equipped (account_id, effect_id) VALUES (?, ?)", (account_id, "noeffect"))
        _equipped_effects_cache[account_id] = "noeffect"
        return "Your effect has been unequipped."

    if effect_name not in EFFECTS_SHOP:
        return f"Error: '{effect_name}' is not a valid effect."

    # Verify ownership
    rows = run_query(
        "SELECT 1 FROM shop_purchases WHERE account_id = ? AND item_type = 'effect' AND item_id = ?",
        (account_id, effect_name),
        fetch=True
    )
    if not rows:
        return f"Error: You do not own the effect '{effect_name}'. Purchase it first from '/shop effects'!"

    run_query("INSERT OR REPLACE INTO shop_equipped (account_id, effect_id) VALUES (?, ?)", (account_id, effect_name))
    _equipped_effects_cache[account_id] = effect_name
    return f"Successfully equipped effect '{effect_name}'."


def get_equipped_effect(account_id: str) -> str | None:
    """Returns the currently equipped effect ID for a player, using cache if available."""
    if not account_id:
        return None

    # Check cache first
    if account_id in _equipped_effects_cache:
        return _equipped_effects_cache[account_id]

    # Fallback to database query
    rows = run_query("SELECT effect_id FROM shop_equipped WHERE account_id = ?", (account_id,), fetch=True)
    effect = rows[0][0] if rows else None
    _equipped_effects_cache[account_id] = effect
    return effect


def has_purchased_command(account_id: str, command_name: str) -> bool:
    """Returns True if the player has purchased the command or if the command is free."""
    from chathandle.chatcommands.commands.registry import registry
    cmd = registry.get_command(command_name)
    if not cmd:
        return False
    # If it is not a shop command (has no cost), we don't enforce shop purchases
    if cmd.shop_cost <= 0:
        return False
    primary_name = cmd.names[0]

    # Check cache first
    if account_id in _purchased_commands_cache:
        return primary_name in _purchased_commands_cache[account_id]

    # Fallback to database query
    rows = run_query(
        "SELECT usages_left FROM shop_purchases WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
        (account_id, primary_name),
        fetch=True
    )
    if account_id not in _purchased_commands_cache:
        _purchased_commands_cache[account_id] = set()
    if rows and (rows[0][0] is None or rows[0][0] > 0):
        _purchased_commands_cache[account_id].add(primary_name)
        return True
    return False


def consume_command_usage(account_id: str, command_name: str) -> None:
    """Decrements the usage count of a purchased command. Removes the purchase if usages reach 0."""
    from chathandle.chatcommands.commands.registry import registry
    cmd = registry.get_command(command_name)
    if not cmd:
        return
    primary_name = cmd.names[0]

    # Query how many usages are left
    rows = run_query(
        "SELECT usages_left FROM shop_purchases WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
        (account_id, primary_name),
        fetch=True
    )
    if not rows:
        return

    usages_left = rows[0][0]
    if usages_left is None:
        usages_left = 3

    usages_left -= 1
    if usages_left <= 0:
        # Delete purchase
        run_query(
            "DELETE FROM shop_purchases WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
            (account_id, primary_name)
        )
        # Update cache
        if account_id in _purchased_commands_cache:
            _purchased_commands_cache[account_id].discard(primary_name)
    else:
        # Update DB
        run_query(
            "UPDATE shop_purchases SET usages_left = ? WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
            (usages_left, account_id, primary_name)
        )


def set_tickets(account_id: str, amount: int) -> int:
    """Sets the tickets balance of a player directly."""
    if not account_id:
        return 0
    amount = max(0, amount)
    # Ensure bank account exists
    get_tickets(account_id)
    run_query("UPDATE shop_bank SET tickets = ? WHERE account_id = ?", (amount, account_id))
    log_transaction(account_id, "set_tickets", amount)
    return amount


def get_transactions(account_id: str = None, page: int = 1, per_page: int = 50) -> dict:
    """Returns a paginated list of transaction logs."""
    import math
    try:
        page = max(1, int(page))
        per_page = max(1, min(100, int(per_page)))
    except Exception:
        page, per_page = 1, 50

    query_where = ""
    params = []
    if account_id:
        query_where = "WHERE account_id = ?"
        params = [account_id]

    count_res = run_query(f"SELECT COUNT(*) FROM shop_transactions {query_where}", tuple(params), fetch=True)
    total = count_res[0][0] if count_res else 0

    offset = (page - 1) * per_page
    fetch_params = list(params)
    fetch_params.extend([per_page, offset])

    rows = run_query(f"""
        SELECT id, account_id, action, amount, item_id, timestamp
        FROM shop_transactions
        {query_where}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, tuple(fetch_params), fetch=True)

    transactions = []
    if rows:
        for r in rows:
            transactions.append({
                "id": r[0],
                "account_id": r[1],
                "action": r[2],
                "amount": r[3],
                "item_id": r[4],
                "timestamp": r[5]
            })

    total_pages = math.ceil(total / per_page)
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


def get_player_purchases(account_id: str) -> list:
    """Returns all purchase records for a player."""
    if not account_id:
        return []
    rows = run_query(
        "SELECT item_type, item_id, usages_left FROM shop_purchases WHERE account_id = ?",
        (account_id,),
        fetch=True
    )
    purchases = []
    if rows:
        for r in rows:
            purchases.append({
                "item_type": r[0],
                "item_id": r[1],
                "usages_left": r[2]
            })
    return purchases


def add_purchase_admin(account_id: str, item_type: str, item_id: str, usages_left: int = None) -> bool:
    """Adds a purchase record on behalf of a player."""
    if not account_id or not item_type or not item_id:
        return False
    item_type = item_type.strip().lower()
    item_id = item_id.strip().lower()

    if item_type == "command" and usages_left is None:
        usages_left = 3

    run_query(
        "INSERT OR REPLACE INTO shop_purchases (account_id, item_type, item_id, usages_left) VALUES (?, ?, ?, ?)",
        (account_id, item_type, item_id, usages_left)
    )

    # Sync cache
    if item_type == "command":
        if account_id not in _purchased_commands_cache:
            _purchased_commands_cache[account_id] = set()
        _purchased_commands_cache[account_id].add(item_id)

    log_transaction(account_id, "admin_grant_purchase", 0, f"{item_type}:{item_id}")
    return True


def remove_purchase_admin(account_id: str, item_type: str, item_id: str) -> bool:
    """Removes a purchase record on behalf of a player."""
    if not account_id or not item_type or not item_id:
        return False
    item_type = item_type.strip().lower()
    item_id = item_id.strip().lower()

    run_query(
        "DELETE FROM shop_purchases WHERE account_id = ? AND item_type = ? AND item_id = ?",
        (account_id, item_type, item_id)
    )

    # Sync cache
    if item_type == "command" and account_id in _purchased_commands_cache:
        _purchased_commands_cache[account_id].discard(item_id)

    log_transaction(account_id, "admin_revoke_purchase", 0, f"{item_type}:{item_id}")
    return True


def update_purchase_usages(account_id: str, item_id: str, usages_left: int) -> bool:
    """Updates the remaining usages of a command purchase."""
    if not account_id or not item_id:
        return False
    item_id = item_id.strip().lower()

    # Verify purchase exists
    rows = run_query(
        "SELECT 1 FROM shop_purchases WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
        (account_id, item_id),
        fetch=True
    )
    if not rows:
        return False

    if usages_left <= 0:
        return remove_purchase_admin(account_id, "command", item_id)

    run_query(
        "UPDATE shop_purchases SET usages_left = ? WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
        (usages_left, account_id, item_id)
    )
    # Ensure it's in cache
    if account_id not in _purchased_commands_cache:
        _purchased_commands_cache[account_id] = set()
    _purchased_commands_cache[account_id].add(item_id)

    log_transaction(account_id, "admin_set_usages", usages_left, f"command:{item_id}")
    return True


def claim_daily_tickets(account_id: str) -> str:
    """Claims daily tickets for a player (once every 24 hours)."""
    import time
    now = time.time()
    rows = run_query("SELECT last_claim FROM shop_claims WHERE account_id = ?", (account_id,), fetch=True)
    if rows:
        last_claim = rows[0][0]
        elapsed = now - last_claim
        if elapsed < 86400:
            remaining = 86400 - elapsed
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            return f"You've already claimed your daily reward! Try again in {hours}h {minutes}m."

    run_query("INSERT OR REPLACE INTO shop_claims (account_id, last_claim) VALUES (?, ?)", (account_id, now))
    add_tickets(account_id, 100)
    return "Successfully claimed 100 daily tickets! Come back tomorrow."


def get_shop_commands() -> dict:
    """Helper to return all registered commands that are in the shop."""
    from chathandle.chatcommands.commands.registry import registry
    shop_cmds = {}
    for name, cmd in registry.get_all_commands().items():
        primary_name = cmd.names[0]
        if cmd.shop_cost > 0 and primary_name not in shop_cmds:
            shop_cmds[primary_name] = {
                "cost": cmd.shop_cost,
                "description": cmd.handler.__doc__.strip().split("\n")[0] if cmd.handler.__doc__ else "No description",
                "aliases": cmd.names[1:]
            }
    return shop_cmds


def get_economy_leaderboard(limit: int = 10) -> list:
    """Returns top players by ticket balance."""
    try:
        limit = max(1, min(100, int(limit)))
    except Exception:
        limit = 10

    rows = run_query("""
        SELECT b.account_id, b.tickets, p.name, p.v2Tag
        FROM shop_bank b
        LEFT JOIN profiles p ON b.account_id = p.account_id
        ORDER BY b.tickets DESC
        LIMIT ?
    """, (limit,), fetch=True)

    leaderboard = []
    if rows:
        for r in rows:
            leaderboard.append({
                "account_id": r[0],
                "tickets": r[1],
                "name": r[2] or "Unknown",
                "v2Tag": r[3]
            })
    return leaderboard


def get_purchasers_paginated(page: int = 1, per_page: int = 50) -> dict:
    """Returns paginated active purchases joined with player profiles."""
    import math
    try:
        page = max(1, int(page))
        per_page = max(1, min(100, int(per_page)))
    except Exception:
        page, per_page = 1, 50

    count_res = run_query("SELECT COUNT(*) FROM shop_purchases", fetch=True)
    total = count_res[0][0] if count_res else 0

    offset = (page - 1) * per_page
    rows = run_query("""
        SELECT sp.account_id, sp.item_type, sp.item_id, sp.usages_left, p.name, p.v2Tag
        FROM shop_purchases sp
        LEFT JOIN profiles p ON sp.account_id = p.account_id
        ORDER BY sp.account_id
        LIMIT ? OFFSET ?
    """, (per_page, offset), fetch=True)

    purchases = []
    if rows:
        for r in rows:
            purchases.append({
                "account_id": r[0],
                "item_type": r[1],
                "item_id": r[2],
                "usages_left": r[3],
                "name": r[4] or "Unknown",
                "v2Tag": r[5]
            })

    total_pages = math.ceil(total / per_page)
    return {
        "purchases": purchases,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


