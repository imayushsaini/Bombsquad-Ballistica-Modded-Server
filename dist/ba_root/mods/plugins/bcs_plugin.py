# -*- coding: utf-8 -*-
# coding: utf-8

# ba_meta require api 9
# from gunicorn.app.base import BaseApplication
# from gunicorn.workers import ggevent as gevent_worker

import logging
import os
from functools import wraps
from threading import Thread

import _babase
import _bascenev1
from flask import Flask, request, jsonify, send_file

# import uvicorn
from . import bombsquad_service

os.environ['FLASK_APP'] = 'bombsquadflaskapi.py'
os.environ['FLASK_ENV'] = 'development'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["DEBUG"] = False
SECRET_KEY = 'default'


@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        return jsonify({"message": "OK"}), 200


@app.after_request
def add_cors_headers(response):
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    # Allow specific headers
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type,Authorization,Secret-Key,bs-host'
    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response


def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        secret = (
            request.headers.get("Secret-Key")
            or request.args.get("secret_key")
            or request.args.get("Secret-Key")
            or request.args.get("key")
        )
        if not secret or secret != SECRET_KEY:
            return jsonify({"message": "Invalid secret key provided."}), 401
        return func(*args, **kwargs)

    return wrapper


@app.route('/', methods=['GET'])
def home():
    return '''Nothing here :)'''


@app.route('/api/live-stats', methods=['GET'])
def get_live_stats():
    return jsonify(bombsquad_service.get_stats()), 200


@app.route('/api/top-200', methods=['GET'])
def get_top200():
    return jsonify(bombsquad_service.get_top_200()), 200


@app.route('/api/subscribe', methods=['POST'])
def subscribe_player():
    try:
        data = request.get_json()
        bombsquad_service.subscribe_player(
            data["subscription"], data["player_id"], data["name"])
        response = {
            'message': f'Subscribed {data["name"]} successfully , will send confirmation notification to test'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify(
            {'message': 'Error processing request', 'error': str(e)}), 400


#  ============ Admin only =========


@app.route('/api/login', methods=['POST'])
@check_admin
def login():
    return jsonify({"message": "Successful"}), 200


@app.route('/api/current-leaderboard', methods=['GET'])
@check_admin
def get_complete_leaderboard():
    return jsonify(bombsquad_service.get_complete_leaderboard()), 200


@app.route('/api/server-settings', methods=['GET'])
@check_admin
def get_server_settings():
    return jsonify(bombsquad_service.get_server_settings()), 200


@app.route('/api/roles', methods=['GET'])
@check_admin
def get_roles():
    return jsonify(bombsquad_service.get_roles()), 200


@app.route('/api/roles', methods=['POST'])
@check_admin
def update_roles():
    try:
        data = request.get_json()
        bombsquad_service.update_roles(data)
        response = {
            'message': 'Roles updated successfully'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify(
            {'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/api/perks', methods=['GET'])
@check_admin
def get_perks():
    return jsonify(bombsquad_service.get_perks()), 200


@app.route('/api/perks', methods=['POST'])
@check_admin
def update_perks():
    try:
        data = request.get_json()
        bombsquad_service.update_perks(data)
        response = {
            'message': 'Custom perks updated successfully'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify(
            {'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/api/server-settings', methods=['POST'])
@check_admin
def update_server_settings():
    try:
        data = request.get_json()
        bombsquad_service.update_server_settings(data)
        response = {
            'message': 'Settings updated successfully, server may need restart'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify(
            {'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/api/db-list', methods=['GET'])
@check_admin
def fetch_dB_list():
    key = request.args.get('type')
    if key is None:
        return "type required", 400
    if key == "logs":
        return jsonify(bombsquad_service.get_logs_db_list()), 200
    elif key == "players":
        return jsonify(bombsquad_service.get_profiles_db_list()), 200
    else:
        return jsonify({"message": "Invalid db type"}), 400


@app.route('/api/search-logs', methods=['GET'])
@check_admin
def search_logs():
    key = request.args.get('key')
    db = request.args.get('db')
    if key is None or db is None:
        return jsonify({"message": "key and db required"}), 400
    return jsonify(bombsquad_service.get_matching_logs(key, db)), 200


@app.route('/api/search-player', methods=['GET'])
@check_admin
def search_players():
    key = request.args.get('key')
    db = request.args.get('db')
    if key is None or db is None:
        return jsonify({"message": "key and db required"}), 400
    return jsonify(bombsquad_service.search_player_profile(key, db)), 200


@app.route('/api/get-player-info', methods=['GET'])
@check_admin
def get_player():
    account_id = request.args.get('account-id')
    if account_id is None:
        return jsonify({"message": "account-id required"}), 400
    return jsonify(bombsquad_service.get_player_details(account_id)), 200


@app.route('/api/update-player', methods=['POST'])
@check_admin
def update_player():
    account_id = request.args.get('account-id')
    action = request.args.get('action')
    duration = int(request.args.get('duration'))
    if account_id is None or action is None:
        return "account-id and action required", 400
    if action == "ban":
        bombsquad_service.ban_player(account_id, duration)
    elif action == "unban":
        bombsquad_service.unban_player(account_id)
    elif action == "mute":
        bombsquad_service.mute_player(account_id, duration)
    elif action == "unmute":
        bombsquad_service.unmute_player(account_id)
    elif action == "disable-kick-vote":
        bombsquad_service.disable_kick_vote(account_id, duration)
    elif action == "enable-kick-vote":
        bombsquad_service.enable_kick_vote(account_id)
    else:
        return jsonify({"message": "Invalid Action"}), 400
    return jsonify({"message": f"{action} done"}), 201


@app.route('/api/config', methods=['GET'])
@check_admin
def get_config():
    return jsonify(bombsquad_service.get_server_config()), 200


@app.route('/api/action', methods=['POST'])
@check_admin
def do_action():
    action = request.args.get('action')
    value = request.args.get('value')
    bombsquad_service.do_action(action, value)
    return jsonify({"message": f'{action} done'}), 200


@app.route('/api/config', methods=['POST'])
@check_admin
def update_server_config():
    try:
        data = request.get_json()
        bombsquad_service.update_server_config(data)
        response = {
            'message': 'config updated successfully, server will restart'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify(
            {'message': 'Error processing request', 'error': str(e)}), 400


#  ============ V2 API Endpoints =========


@app.route('/v2/player-stats', methods=['GET'])
def get_player_stats_v2():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"message": "account_id required"}), 400
    stats = bombsquad_service.get_player_stats(account_id)
    if stats is None:
        return jsonify({"message": "Player stats not found"}), 404
    return jsonify(stats), 200


@app.route('/v2/whitelist', methods=['GET'])
@check_admin
def get_whitelist_v2():
    return jsonify(bombsquad_service.get_whitelist()), 200


@app.route('/v2/whitelist', methods=['POST'])
@check_admin
def update_whitelist_v2():
    try:
        data = request.get_json()
        action = data.get("action")
        account_id = data.get("account_id")
        if not action or not account_id:
            return jsonify({"message": "action and account_id required"}), 400

        if action == "add":
            bombsquad_service.add_to_whitelist(account_id)
            return jsonify({"message": f"Added {account_id} to whitelist"}), 200
        elif action == "remove":
            bombsquad_service.remove_from_whitelist(account_id)
            return jsonify({"message": f"Removed {account_id} from whitelist"}), 200
        else:
            return jsonify({"message": f"Invalid action: {action}"}), 400
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/blacklist', methods=['GET'])
@check_admin
def get_blacklist_v2():
    return jsonify(bombsquad_service.get_blacklist()), 200


@app.route('/v2/kickvote', methods=['GET'])
@check_admin
def get_kickvote_v2():
    return jsonify(bombsquad_service.get_kickvote_data()), 200


@app.route('/v2/kickvote/restricted', methods=['POST'])
@check_admin
def add_kickvote_restricted_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        duration = float(data.get("duration", 30.0))
        reason = data.get("reason", "restricted via REST API")
        if not account_id:
            return jsonify({"message": "account_id required"}), 400
        bombsquad_service.disable_kick_vote(account_id, duration)
        return jsonify({"message": f"Kick vote restricted for {account_id} for {duration} days"}), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/kickvote/restricted', methods=['DELETE'])
@check_admin
def remove_kickvote_restricted_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id") or request.args.get("account_id")
        if not account_id:
            return jsonify({"message": "account_id required"}), 400
        bombsquad_service.enable_kick_vote(account_id)
        return jsonify({"message": f"Kick vote restriction removed for {account_id}"}), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/kickvote/immune', methods=['POST'])
@check_admin
def add_kickvote_immune_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        if not account_id:
            return jsonify({"message": "account_id required"}), 400
        bombsquad_service.set_kick_vote_immune(account_id, True)
        return jsonify({"message": f"Kick vote immunity granted to {account_id}"}), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/kickvote/immune', methods=['DELETE'])
@check_admin
def remove_kickvote_immune_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id") or request.args.get("account_id")
        if not account_id:
            return jsonify({"message": "account_id required"}), 400
        bombsquad_service.set_kick_vote_immune(account_id, False)
        return jsonify({"message": f"Kick vote immunity revoked from {account_id}"}), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


# ==================== Replays API Endpoints ====================


@app.route('/v2/replays', methods=['GET'])
@app.route('/api/replays', methods=['GET'])
@check_admin
def get_replays_v2():
    """List all available replay files with metadata, sorting, search, and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        sort_by = request.args.get('sort_by', 'modified', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        result = bombsquad_service.get_replays_list(
            page=page,
            per_page=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving replays', 'error': str(e)}), 500


@app.route('/v2/replays/download', methods=['GET'])
@app.route('/v2/replays/<path:filename>/download', methods=['GET'])
@app.route('/api/replays/download', methods=['GET'])
@check_admin
def download_replay_v2(filename: str = None):
    """Download a specific replay file."""
    try:
        if filename is None:
            filename = request.args.get('filename')
        if not filename:
            return jsonify({'message': 'filename query parameter or path required'}), 400

        filepath = bombsquad_service.get_replay_filepath(filename)
        if not filepath or not os.path.isfile(filepath):
            return jsonify({'message': f'Replay file not found: {filename}'}), 404

        download_name = os.path.basename(filepath)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/octet-stream',
        )
    except Exception as e:
        return jsonify({'message': 'Error downloading replay', 'error': str(e)}), 500


@app.route('/v2/replays/<path:filename>', methods=['DELETE'])
@app.route('/v2/replays', methods=['DELETE'])
@app.route('/api/replays', methods=['DELETE'])
@check_admin
def delete_replay_v2(filename: str = None):
    """Delete a single or batch of replay files."""
    try:
        # Check if multiple filenames are provided in request JSON body
        data = request.get_json(silent=True) or {}
        if 'filenames' in data and isinstance(data['filenames'], list):
            res = bombsquad_service.delete_replays_batch(data['filenames'])
            return jsonify(res), 200

        if filename is None:
            filename = data.get('filename') or request.args.get('filename')

        if not filename:
            return jsonify({'message': 'filename required in path, query parameter, or JSON body'}), 400

        success = bombsquad_service.delete_replay(filename)
        if success:
            return jsonify({'message': f'Replay {filename} deleted successfully'}), 200
        return jsonify({'message': f'Replay file not found or could not be deleted: {filename}'}), 404
    except Exception as e:
        return jsonify({'message': 'Error deleting replay', 'error': str(e)}), 500


@app.route('/v2/recents', methods=['GET'])
@check_admin
def get_recents_v2():
    return jsonify(bombsquad_service.get_recents()), 200


@app.route('/v2/players', methods=['GET'])
@app.route('/v1/player', methods=['GET'])
@app.route('/v1/players', methods=['GET'])
@check_admin
def get_players_v2():
    try:
        account_id = request.args.get('account_id') or request.args.get('account-id')
        if account_id:
            player = bombsquad_service.get_player_by_id(account_id)
            if player is None:
                return jsonify({"message": "Player profile not found"}), 404
            return jsonify(player), 200

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        sort_by = request.args.get(
            'sort_by', 'server_profile_created_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        result = bombsquad_service.get_players_paginated(
            page=page, per_page=per_page, search=search,
            sort_by=sort_by, sort_order=sort_order
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/players/<account_id>', methods=['GET'])
@app.route('/v1/player/<account_id>', methods=['GET'])
@app.route('/v1/players/<account_id>', methods=['GET'])
@check_admin
def get_player_by_id_v2(account_id):
    try:
        player = bombsquad_service.get_player_by_id(account_id)
        if player is None:
            return jsonify({"message": "Player profile not found"}), 404
        return jsonify(player), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


@app.route('/v2/players/<account_id>', methods=['PUT'])
@app.route('/v1/player/<account_id>', methods=['PUT'])
@app.route('/v1/players/<account_id>', methods=['PUT'])
@check_admin
def update_player_profile_v2(account_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "JSON body required"}), 400

        success = bombsquad_service.update_player_profile(account_id, data)
        if not success:
            return jsonify({"message": "Player profile not found"}), 404
        return jsonify({"message": "Player profile updated successfully"}), 200
    except Exception as e:
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


# from flask_asgi import FlaskASGI
# asgi_app = FlaskASGI(app)


# class FlaskApplication(BaseApplication):
#     def __init__(self, app, options=None):
#         self.options = options or {}
#         self.application = app
#         super(FlaskApplication, self).__init__()

#     def load_config(self):
#         config = {key: value for key, value in self.options.items(
#         ) if key in self.cfg.settings and value is not None}
#         for key, value in config.items():
#             self.cfg.set(key.lower(), value)

#     def load(self):
#         return self.application


# def start_uvicorn():
#     uvicorn.run("main:app", host='0.0.0.0', port=5000,
#                 reload=False, log_level="debug", workers=3, use_colors=True, no_signal=True)
# --- V2 Economy Admin Endpoints ---

@app.route('/v2/economy/tickets', methods=['POST'])
@check_admin
def admin_manage_tickets_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        amount = data.get("amount")
        action = data.get("action")

        if not account_id or amount is None or not action:
            return jsonify({"message": "Missing required fields: account_id, amount, action"}), 400

        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"message": "amount must be an integer"}), 400

        import shop
        if action == "add":
            new_bal = shop.add_tickets(account_id, amount)
        elif action == "remove":
            new_bal = shop.add_tickets(account_id, -amount)
        elif action == "set":
            new_bal = shop.set_tickets(account_id, amount)
        else:
            return jsonify({"message": "Invalid action. Supported: add, remove, set"}), 400

        return jsonify({"account_id": account_id, "new_balance": new_bal}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/transactions', methods=['GET'])
@check_admin
def admin_get_transactions_v2():
    try:
        account_id = request.args.get("account_id")
        page = request.args.get("page", 1)
        per_page = request.args.get("per_page", 50)

        import shop
        res = shop.get_transactions(
            account_id=account_id, page=page, per_page=per_page)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/purchases/<account_id>', methods=['GET'])
@check_admin
def admin_get_purchases_v2(account_id):
    try:
        import shop
        purchases = shop.get_player_purchases(account_id)
        tickets = shop.get_tickets(account_id)
        return jsonify({"account_id": account_id, "tickets": tickets, "purchases": purchases}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/purchases', methods=['POST'])
@check_admin
def admin_grant_purchase_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        item_type = data.get("item_type")
        item_id = data.get("item_id")
        usages_left = data.get("usages_left")

        if not account_id or not item_type or not item_id:
            return jsonify({"message": "Missing required fields: account_id, item_type, item_id"}), 400

        if usages_left is not None:
            try:
                usages_left = int(usages_left)
            except ValueError:
                return jsonify({"message": "usages_left must be an integer"}), 400

        import shop
        success = shop.add_purchase_admin(
            account_id, item_type, item_id, usages_left)
        if success:
            return jsonify({"message": "Successfully granted item to player"}), 200
        return jsonify({"message": "Failed to grant item"}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/purchases', methods=['DELETE'])
@check_admin
def admin_revoke_purchase_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        item_type = data.get("item_type")
        item_id = data.get("item_id")

        if not account_id or not item_type or not item_id:
            return jsonify({"message": "Missing required fields: account_id, item_type, item_id"}), 400

        import shop
        success = shop.remove_purchase_admin(account_id, item_type, item_id)
        if success:
            return jsonify({"message": "Successfully revoked item from player"}), 200
        return jsonify({"message": "Failed to revoke item"}), 400
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/purchases', methods=['PUT'])
@check_admin
def admin_update_usages_v2():
    try:
        data = request.get_json() or {}
        account_id = data.get("account_id")
        item_id = data.get("item_id")
        usages_left = data.get("usages_left")

        if not account_id or not item_id or usages_left is None:
            return jsonify({"message": "Missing required fields: account_id, item_id, usages_left"}), 400

        try:
            usages_left = int(usages_left)
        except ValueError:
            return jsonify({"message": "usages_left must be an integer"}), 400

        import shop
        success = shop.update_purchase_usages(account_id, item_id, usages_left)
        if success:
            return jsonify({"message": "Successfully updated remaining usages"}), 200
        return jsonify({"message": "Failed to update usages (verify purchase exists)"}), 404
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/leaderboard', methods=['GET'])
@check_admin
def admin_get_leaderboard_v2():
    try:
        limit = request.args.get("limit", 10)
        import shop
        res = shop.get_economy_leaderboard(limit=limit)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


@app.route('/v2/economy/purchasers', methods=['GET'])
@check_admin
def admin_get_purchasers_v2():
    try:
        page = request.args.get("page", 1)
        per_page = request.args.get("per_page", 50)
        import shop
        res = shop.get_purchasers_paginated(page=page, per_page=per_page)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500


def run_server():
    from waitress import serve
    serve(app, host="0.0.0.0", port=_bascenev1.get_game_port())


def enable(password):
    global SECRET_KEY
    SECRET_KEY = password
    t = Thread(target=run_server)
    t.start()
    # uvicorn_thread = threading.Thread(target=start_uvicorn)
    # uvicorn_thread.start()
    # options = {
    #     'bind': '0.0.0.0:8000',
    #     'workers': 4,
    #     'worker_class': 'gevent'
    # }

    # flask_app = FlaskApplication(app, options)
    # gevent_worker.GeventWorker(app.wsgi_app).init_process()
    # flask_app.run()
