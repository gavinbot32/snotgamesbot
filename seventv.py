'''
7tv Tracker Client
@author: Yespere

Useful links:
    Firehose for my emote sets
    https://events.7tv.io/v3@emote_set.update<object_id=645861cbd3b4256e12d82c67>

    Simple get for all mar emotes:
    https://7tv.io/v3/users/twitch/562314750

    (yespere Emotes for testing)
    https://7tv.io/v3/users/twitch/504754639

    (gavins emotes)
    https://7tv.io/v3/users/twitch/154649067
'''

import json
import requests
import websocket
import time
import threading


subscribe = '{"op": 35,"d": {"type": "emote_set.update","condition": {"object_id": "63c217602b6c46cb48bb423b"}}}'
# subscribe = '{"op": 35,"d": {"type": "emote_set.update","condition": {"object_id": "645861cbd3b4256e12d82c67"}}}'

# Define the WebSocket server URL
websocket_url = "wss://events.7tv.io/v3"


class EmoteClient():
    def __init__(self):
        self._emotes = set()
        self._emoteID = {}
        self._ws = None
        self._thread = None
        self._reconnect = True

    def connect(self):
        response = requests.get('https://7tv.io/v3/users/twitch/562314750')
        # response = requests.get('https://7tv.io/v3/users/twitch/154649067')
        data = json.loads(response.text)
        temp_emotes = set()
        temp_emoteID = {}
        for emote in data['emote_set']['emotes']:
            temp_emotes.add(emote['name'])
            temp_emoteID[emote['id']] = emote['name']
        self._emotes = temp_emotes
        self._emoteID = temp_emoteID
        self._ws = websocket.WebSocketApp(
            websocket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self._thread = threading.Thread(target=self._ws.run_forever)
        self._thread.daemon = True
        self._thread.start()

    def on_open(self, ws):
        print("WebSocket connection opened.", flush=True)
        ws.send(subscribe)

    def on_message(self, ws, message):
        data = json.loads(message)
        if (data['op'] == 0 and data['d']['type'] == 'emote_set.update'):
            if (data['d']['body'].get('pushed')):
                for each in data['d']['body']['pushed']:
                    new = each['value']['name']
                    print("Add:", new, flush=True)
                    self._emotes.add(new)
                    self._emoteID[each['value']['id']] = new
            elif (data['d']['body'].get('pulled')):
                for each in data['d']['body']['pulled']:
                    old = self._emoteID[each['old_value']['id']]
                    print("Remove:", old, flush=True)
                    self._emotes.remove(old)
            elif (data['d']['body'].get('updated')):
                for each in data['d']['body']['updated']:
                    old = each['old_value']['name']
                    print("Remove:", old, flush=True)
                    self._emotes.remove(old)
                    new = each['value']['name']
                    print("Add:", new, flush=True)
                    self._emotes.add(new)
                    self._emoteID[each['value']['id']] = new
            else:
                print('Unknown Emote Set Update')
                print("Received message: {}".format(message))
        elif (data['op'] == 2):
            # Heartbeat Ignore
            pass
        else:
            print("Received message: {}".format(message), flush=True)

    def on_error(self, ws, error):
        print("Error encountered: {}".format(error), flush=True)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed.", flush=True)
        time.sleep(5)
        if (self._reconnect):
            self.connect()

    def close(self):
        self._ws.close()
        self._reconnect = False

    def isEmote(self, emote):
        return emote in self._emotes