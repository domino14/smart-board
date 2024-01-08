from woogles_api import string_to_machine_letters


def scrabblecam_to_fen(board_str):
    rows = board_str.split("|")
    outstr = ""

    for idx, row in enumerate(rows):
        chars = row.split(",")
        emptyct = 0
        for c in chars:
            if c == "":
                emptyct += 1
            else:
                if emptyct != 0:
                    outstr += f"{emptyct}"
                    emptyct = 0
                outstr += c
        if emptyct != 0:
            outstr += f"{emptyct}"
        outstr += "/" if idx != len(rows) - 1 else ""

    return outstr


def fen_to_board(fen: str):
    board = []
    for row in fen.split("/"):
        cur_n = ""
        boardrow = []
        for ch in row:
            if ch >= "0" and ch <= "9":
                cur_n += ch
            else:
                if cur_n != "":
                    for _ in range(int(cur_n)):
                        boardrow.append(" ")
                    cur_n = ""
                boardrow.append(ch)
        if cur_n != "":
            for i in range(int(cur_n)):
                boardrow.append(" ")
        board.append(boardrow)
    return board


def fen_change_to_event(old_fen, new_fen, game_id):
    old_board = fen_to_board(old_fen)
    new_board = fen_to_board(new_fen)
    changes = []
    for ridx, row in enumerate(old_board):
        for chidx, ch in enumerate(row):
            if new_board[ridx][chidx] != ch:
                changes.append((ridx, chidx))

    crow = set()
    ccol = set()

    for change in changes:
        crow.add(change[0])
        ccol.add(change[1])

    if len(crow) > 1 and len(ccol) > 1:
        raise Exception("tiles not colinear")

    vertical = False
    if len(crow) == 1:
        # horizontal (or one-tile); all in same row
        ri, ci = 0, 1

    elif len(ccol) == 1:
        ri, ci = 1, 0
        # vertical (or one-tile)
        vertical = True

    # find starting tile. look backwards from first change.
    first_change = changes[0]
    firstr, firstc = first_change[0], first_change[1]
    r, c = firstr, firstc
    while r - ri >= 0 and c - ci >= 0:
        if new_board[r - ri][c - ci] == " ":
            break
        r -= ri
        c -= ci

    # starting square is (r, c). convert to coords.
    rcoord = r + 1
    ccoord = chr(c + ord("A"))
    coords = f"{rcoord}{ccoord}"
    if vertical:
        coords = f"{ccoord}{rcoord}"

    letters = ""

    while True:
        if old_board[r][c] != " ":
            letters += "."
        elif new_board[r][c] != " ":
            # XXX: This only works for the english distribution!!! It's a hack, fix me later.
            tile = new_board[r][c]
            letters += tile

        r += ri
        c += ci
        # Of course only for 15x15 boards:
        if r > 14 or c > 14:
            break

    return {
        "type": "TILE_PLACEMENT",
        "game_id": game_id,
        "position_coords": coords,
        "machine_letters": string_to_machine_letters(letters),
    }
