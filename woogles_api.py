import base64
import os

import requests

woogles_api_key = os.getenv("WOOGLES_API_KEY")


def create_broadcast(players, lexicon: str, letterdist: str, challenge_rule: str):
    player_info = [
        {
            "user_id": "user1",
            "nickname": players[0][0],
            "full_name": players[0][0],
            "first": True,
        },
        {
            "user_id": "user2",
            "nickname": players[1][0],
            "full_name": players[1][0],
        },
    ]
    try:
        resp = requests.post(
            json={
                "players_info": player_info,
                "lexicon": lexicon,
                "rules": {
                    "board_layout_name": "CrosswordGame",
                    "letter_distribution_name": letterdist,
                    "variant_name": "classic",
                },
                "challenge_rule": challenge_rule,
            },
            headers={"X-Api-Key": woogles_api_key},
            url="https://woogles.io/twirp/omgwords_service.GameEventService/CreateBroadcastGame",
        )
    except Exception as e:
        print("could not post", e)
        return {}
    else:
        print("Got response", resp.json())

    return resp.json()


def set_racks(game_id: str, machine_letter_racks: list[bytearray]):
    print("Sending set_racks to woogles", machine_letter_racks)
    # protojson for some reason encodes bytearrays as base64 strings
    racks = map(lambda x: base64.b64encode(x), machine_letter_racks)
    try:
        resp = requests.post(
            json={
                "game_id": game_id,
                "racks": racks,
            },
            headers={"X-Api-Key": woogles_api_key},
            url="https://woogles.io/twirp/omgwords_service.GameEventService/SetRacks",
        )
    except Exception as e:
        print("could not post", e)
        return {}
    else:
        print("Got response", resp.json())


def send_game_event(game_event):
    print("Sending game event to woogles", game_event)
    if game_event["type"] == "TILE_PLACEMENT":
        # protojson-compatible:
        game_event["machine_letters"] = base64.b64encode(game_event["machine_letters"])
    try:
        resp = requests.post(
            json=game_event,
            headers={"X-Api-Key": woogles_api_key},
            url="https://woogles.io/twirp/omgwords_service.GameEventService/SendGameEvent",
        )
    except Exception as e:
        print("could not post", e)
        return {}
    else:
        print("Got response", resp.json())


def get_game_document(game_id):
    try:
        resp = requests.post(
            json={"game_id": game_id},
            headers={"X-Api-Key": woogles_api_key},
            url="https://woogles.io/twirp/omgwords_service.GameEventService/GetGameDocument",
        )
    except Exception as e:
        print("could not post", e)
        return {}
    return resp.json()


def string_to_machine_letters(s: str):
    """Only compatible with English/French right now!! Use full conversion later; see liwords."""
    mls = []
    for tile in s:
        blank = False
        if tile >= "A" and tile <= "Z":
            base_val = ord(tile) - ord("A") + 1
        elif tile >= "a" and tile <= "z":
            base_val = ord(tile) - ord("a") + 1
            blank = True
        elif tile == "." or tile == "?":
            base_val = 0
        if blank:
            base_val |= 0x80
        mls.append(base_val)
    return bytearray(mls)
