# This sample will allow you to connect to a room, and send/recieve messages.
# Args: host:port username password room
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.

import sys
import samples.samples_common as samples_common  # Common bits used between samples
import logging
import spotipy
import spotipy.util as util
from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema


# Called when a message is recieved.
def on_message(room, event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            print("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            msg = event['content']['body']
            sender = event['sender']
            print("{0}: {1}".format(sender, msg))

            if msg[0] == '!':
                room.send_text("You've got my attentions.")
                scope = 'playlist-modify-public'
                token = util.prompt_for_user_token("thetanbull",scope,client_id='7c7434125032486dba2b8b85ae1ea570',client_secret='9a8f70aef58b4f3faeb44fe435bb6843',redirect_uri='http://localhost/')

                if token:
                    sp = spotipy.Spotify(auth=token)
                    results = sp.search(msg[1:], type='track')
                    print(results['tracks']['items'][0]['album']['artists'][0]['name']) #artist
                    print(results['tracks']['items'][0]['album']['name']) #album
                    print(results['tracks']['items'][0]['name']) #track name
                    print(results['tracks']['items'][0]['uri']) #uri
                    print(results['tracks']['items'][0]['id']) #id
                    track_ids = []
                    track_ids.append(results['tracks']['items'][0]['id'])
                    # for item in results['tracks']['items']:
                    #     print(f"{item['album']['artists'][0]['name']} - {item['name']}")
                    tracks_added = sp.user_playlist_add_tracks("thetanbull", "7oea8xWOYjef0LIN4sHQuy", track_ids)
                    room.send_text(f"{results['tracks']['items'][0]['name']} added to the playlist!")
                else:
                    print ("Can't get token for", username)










    else:
        print(event['type'])



def main(host, username, password, room_id_alias):
    client = MatrixClient(host)

    try:
        client.login_with_password(username, password)
    except MatrixRequestError as e:
        print(e)
        if e.code == 403:
            print("Bad username or password.")
            sys.exit(4)
        else:
            print("Check your server details are correct.")
            sys.exit(2)
    except MissingSchema as e:
        print("Bad URL format.")
        print(e)
        sys.exit(3)

    try:
        room = client.join_room(room_id_alias)
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
    client.start_listener_thread()

    while True:
        msg = samples_common.get_input()
        if msg == "/quit":
            break
        else:
            room.send_text(msg)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    host, username, password = samples_common.get_user_details(sys.argv)

    if len(sys.argv) > 4:
        room_id_alias = sys.argv[4]
    else:
        room_id_alias = samples_common.get_input("Room ID/Alias: ")

    main(host, username, password, room_id_alias)