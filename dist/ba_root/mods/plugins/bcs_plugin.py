# -*- coding: utf-8 -*-
# coding: utf-8

# ba_meta require api 7
# from gunicorn.app.base import BaseApplication
# from gunicorn.workers import ggevent as gevent_worker

import logging
from threading import Thread
from flask import Flask, request, jsonify
from functools import wraps
import os
import _ba
import _thread
# import uvicorn
from . import bombsquad_service

os.environ['FLASK_APP'] = 'bombsquadflaskapi.py'
os.environ['FLASK_ENV'] = 'development'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["DEBUG"] = False
SECRET_KEY = 'default'


@app.after_request
def add_cors_headers(response):
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    # Allow specific headers
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,Secret-Key'
    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    return response


def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "Secret-Key" not in request.headers or request.headers["Secret-Key"] != SECRET_KEY:
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
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


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
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


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
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


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
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 400


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
    # flask_run = _thread.start_new_thread(app.run, ("0.0.0.0", 5000, False))

def run_server():
    from waitress import serve
    serve(app, host="0.0.0.0", port=_ba.get_game_port())


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
