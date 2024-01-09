import requests

from cgp import scrabblecam_to_fen


def get_from_scrabblecam(board_or_rack, imgbuffer):
    files = {"file": ("image.jpg", imgbuffer, "image/jpeg")}
    url = "https://scrabblecam.com/process"
    if board_or_rack == "rack":
        url += "_rack"
    try:
        response = requests.post(url, files=files)
    except Exception as e:
        print(e)
    else:
        print("status_code", response.status_code)
    return response.json()


def get_board_and_rack_from_images(board_img: bytes, rack_img: bytes):
    board_json = get_from_scrabblecam("board", board_img)
    fen = ""
    if board_json and board_json.get("board"):
        fen = scrabblecam_to_fen(board_json["board"])
        print(fen)
    else:
        print("Got unexpected response", board_json)
    rack_letters = ""
    if len(rack_img) > 0:
        rack_json = get_from_scrabblecam("rack", rack_img)
        if rack_json and rack_json.get("rack"):
            rack_letters = "".join(rack_json.get("rack").split(","))
            print("Rack is", rack_letters)

    return fen, rack_letters
