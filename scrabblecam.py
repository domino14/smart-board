import requests


def get_from_scrabblecam(board_or_rack, imgbuffer):
    files = {"file": ("image.jpg", imgbuffer, "image/jpeg")}
    url = "https://scrabblecam.com/process"
    if board_or_rack == "rack":
        url += "_rack"

    response = requests.post(url, files=files)
    print("status_code", response.status_code)
    print("response body", response.text)
    return response.json()
