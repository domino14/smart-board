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
