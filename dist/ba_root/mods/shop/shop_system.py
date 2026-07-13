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


def add_tickets(account_id: str, amount: int) -> int:
    """Modifies (adds/subtracts) the tickets of a player."""
    if not account_id:
        return 0
    # Ensure they exist in the DB first
    get_tickets(account_id)
    run_query("UPDATE shop_bank SET tickets = tickets + ? WHERE account_id = ?", (amount, account_id))
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

    add_tickets(sender_id, -amount)
    add_tickets(receiver_id, amount)
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
        "SELECT 1 FROM shop_purchases WHERE account_id = ? AND item_type = ? AND item_id = ?",
        (account_id, item_type, item_id),
        fetch=True
    )
    if rows:
        return f"You have already purchased the {display_name}."

    # 4. Check if they have enough tickets
    balance = get_tickets(account_id)
    if balance < cost:
        return f"Insufficient tickets! {display_name} costs {cost} tickets, but you only have {balance}."

    # 5. Process transaction
    add_tickets(account_id, -cost)
    run_query(
        "INSERT INTO shop_purchases (account_id, item_type, item_id) VALUES (?, ?, ?)",
        (account_id, item_type, item_id)
    )

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

    return f"Successfully purchased {display_name} for {cost} tickets! Remaining balance: {balance - cost}."


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
        "SELECT 1 FROM shop_purchases WHERE account_id = ? AND item_type = 'command' AND item_id = ?",
        (account_id, primary_name),
        fetch=True
    )
    if account_id not in _purchased_commands_cache:
        _purchased_commands_cache[account_id] = set()
    if rows:
        _purchased_commands_cache[account_id].add(primary_name)
    return len(rows) > 0


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
