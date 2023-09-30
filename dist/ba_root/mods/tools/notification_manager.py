import time
import shutil
import random
import string
from pywebpush import webpush
import json
import base64
import ecdsa
import os
import _ba
from datetime import datetime
date_format = '%Y-%m-%d %H:%M:%S'
vapidkeys = {}
subscriptions = {}
subscribed_players = {}
PLAYERS_DATA_PATH = os.path.join(
    _ba.env()["python_directory_user"], "playersData" + os.sep
)


def get_vapid_keys():
    global vapidkeys
    if vapidkeys != {}:
        return vapidkeys
    try:
        f = open(".keys", "r")
        vapidkeys = json.load(f)
        f.close()
        return vapidkeys
    except:
        pk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        vk = pk.get_verifying_key()
        vapidkeys = {
            'private_key': base64.urlsafe_b64encode(pk.to_string()).rstrip(b'=').decode('utf-8'),
            'public_key': base64.urlsafe_b64encode(b'\x04' + vk.to_string()).rstrip(b'=').decode('utf-8')
        }
        f = open(".keys", "w")
        json.dump(vapidkeys, f)
        f.close()
        return vapidkeys


def send_push_notification(subscription, payload):
    # try:
    # Send the push notification using the subscription and payload
    print(subscription)
    print(payload)
    print(get_vapid_keys()["private_key"])

    webpush(subscription_info=subscription, data=json.dumps(payload),
            vapid_private_key=get_vapid_keys()["private_key"], vapid_claims={
                'sub': 'mailto:{}'.format("test@ballistica.net"),
    })
    print("Push notification sent successfully")
    # except Exception as e:
    # print("Error sending push notification:", str(e))


# if we already have that browser subscription saved get id or generate new one
def get_subscriber_id(sub):
    subscriber_id = None

    for key, value in subscriptions.items():
        if value["endpoint"] == sub["endpoint"]:
            subscriber_id = key
            break

    if not subscriber_id:
        subscriber_id = generate_random_string(6)
        subscriptions[subscriber_id] = sub
    return subscriber_id


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def subscribe(sub, account_id, name):

    id = get_subscriber_id(sub)
    if account_id in subscribed_players:
        if id not in subscribed_players[account_id]["subscribers"]:
            subscribed_players[account_id]["subscribers"].append(id)
            subscribed_players[account_id]["name"] = name
    else:
        subscribed_players[account_id] = {"subscribers": [id], "name": name}
    send_push_notification(sub, {"notification": {
                           "title": "Notification working !", "body": f'subscribed {name}'}})


def player_joined(pb_id):
    now = datetime.now()
    if pb_id in subscribed_players:
        if "last_notification" in subscribed_players[pb_id] and (now - datetime.strptime(subscribed_players[pb_id]["last_notification"], date_format)).seconds < 15 * 60:
            pass
        else:
            subscribed_players[pb_id]["last_notification"] = now.strftime(date_format)
            subscribes = subscribed_players[pb_id]["subscribers"]
            for subscriber_id in subscribes:
                sub = subscriptions[subscriber_id]
                send_push_notification(
                    sub, {
                        "notification": {
                            "title": f'{subscribed_players[pb_id]["name"] } is playing now',
                            "body": f'Join {_ba.app.server._config.party_name} server {subscribed_players[pb_id]["name"]} is waiting for you ',
                            "icon": "assets/icons/icon-96x96.png",
                            "vibrate": [100, 50, 100],
                            "requireInteraction": True,
                            "data": {"dateOfArrival": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                            "actions": [{"action": "nothing", "title": "Launch Bombsquad"}],
                        }
                    })


def loadCache():
    global subscriptions
    global subscribed_players
    try:
        f = open(PLAYERS_DATA_PATH+"subscriptions.json", "r")
        subscriptions = json.load(f)
        f.close()
    except:
        f = open(PLAYERS_DATA_PATH+"subscriptions.json.backup", "r")
        subscriptions = json.load(f)
        f.close()
    try:
        f = open(PLAYERS_DATA_PATH+"subscribed_players.json", "r")
        subscribed_players = json.load(f)
        f.close()
    except:
        f = open(PLAYERS_DATA_PATH+"subscribed_players.json.backup", "r")
        subscribed_players = json.load(f)
        f.close()


def dump_cache():
    if subscriptions != {}:
        shutil.copyfile(PLAYERS_DATA_PATH + "subscriptions.json",
                        PLAYERS_DATA_PATH + "subscriptions.json.backup")

        with open(PLAYERS_DATA_PATH + "subscriptions.json", "w") as f:
            json.dump(subscriptions, f, indent=4)
    if subscribed_players != {}:
        shutil.copyfile(PLAYERS_DATA_PATH + "subscribed_players.json",
                        PLAYERS_DATA_PATH + "subscribed_players.json.backup")

        with open(PLAYERS_DATA_PATH + "subscribed_players.json", "w") as f:
            json.dump(subscribed_players, f, indent=4)

    time.sleep(60)
    dump_cache()


loadCache()
