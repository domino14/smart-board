from scrabblecam import get_from_scrabblecam
from cgp import scrabblecam_to_fen, fen_change_to_event
from woogles_api import set_racks, send_game_event, string_to_machine_letters


class WooglesGameManager:
    def __init__(self, players, bot_position):
        self.players = players
        self.bot_position = bot_position

    def set_player_on_turn(self, player_on_turn):
        self.player_on_turn = player_on_turn

    def set_game_id(self, game_id):
        self.game_id = game_id

    def process_board_and_rack(self, board_img, rack_img):
        board_json = get_from_scrabblecam("board", board_img)
        fen = ""
        if board_json and board_json.get("board"):
            fen = scrabblecam_to_fen(board_json["board"])
            print(fen)
        else:
            print("Got unexpected response", board_json)
        rack_json = get_from_scrabblecam("rack", rack_img)
        rack_letters = ""
        if rack_json and rack_json.get("rack"):
            rack_letters = "".join(rack_json.get("rack").split(","))
            print("Rack is", rack_letters)
        if fen != "":
            # if not (fen != "" and rack_letters != ""):
            # We could not read either the board or the rack. Can't
            # work properly.
            print("Unable to read board. Adjust camera and press 0 to try again")
            return
        if (
            rack_letters == ""
            and self.bot_position is not None
            and self.player_on_turn[1] == self.bot_position
        ):
            print("Unable to read rack for bot. Adjust camera and press 0 to try again")
            return

        # ok. we have a fen.
        # we need to:
        # 1) Figure out what changed from the last turn, and send new
        #   move to Woogles. If nothing changed and player on turn changed,
        #   it was a pass or exchange.
        # 2) Query woogles for game document, and update scores on interface
        # 3) determine whose turn it is.
        #    a) if it is the bot's turn, create a CGP with rack and updated score,
        #       send to lambda/bestbot/etc. Wait for response. Speak response.
        #    b) if it is the human's turn, do nothing i think
        if fen == last_fen:
            # Nothing changed. Send a pass or whatever.
            # XXX: interface should maybe allow user to input an exchange
            # explicitly. for now, just send a pass.
            evt = {"type": "PASS", "game_id": self.game_id}
        else:
            try:
                evt = fen_change_to_event(last_fen, fen)
            except Exception as e:
                print("error", e)
                return
            last_fen = fen

        rack_mls = None
        if rack_letters == "":
            # It has to be a player's turn. We don't know their rack. Set it
            # to be at least the tiles that were played in evt.
            if evt["type"] == "TILE_PLACEMENT":
                rack_mls = evt["machine_letters"]
        else:
            rack_mls = string_to_machine_letters(rack_letters)

        racks_to_set = [bytearray(), bytearray()]
        if self.player_on_turn[1] == "LEFT":
            racks_to_set[0] = rack_mls
        elif self.player_on_turn[1] == "RIGHT":
            racks_to_set[1] = rack_mls
        set_racks(self.game_id, racks_to_set)

        send_game_event(evt)
