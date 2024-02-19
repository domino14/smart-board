from cgp import scrabblecam_to_fen


def test_scrabblecam_to_fen():
    scrabblecam_out = {
        "status": "OK",
        "board": ",,,,,,,,,,,Y,O,O,P|,,,,,,,,,G,,A,,X,|,,,,,,,,,L,,G,,E,|,,,,,,,,,O,,E,,N,|,,,,,,,V,I,Z,O,R,,,|,J,A,M,,,,,,E,,,,U,R|B,,S,I,A,?,A,N,G,S,,,,N,E|E,,,L,,,Y,O,U,,W,,,P,I|R,I,,D,,L,E,N,T,,H,,Q,I,|A,W,,E,,,,,,F,A,,I,C,E|T,R,I,S,T,A,T,E,,O,M,,,K,|E,E,,T,,,,F,A,R,S,I,D,P,|,N,U,,,D,A,T,E,,,,,D,|,C,,O,B,I,,,,,,,,,|R,H,I,N,O,,,,,,,,,,",
        "corners": [[217, 198], [1274, 202], [1326, 1387], [114, 1358]],
    }
    cgp = scrabblecam_to_fen(scrabblecam_out["board"])
    # Not actually valid FEN because of the unknown blank but we'll figure that out later.
    assert (
        cgp
        == "11YOOP/9G1A1X1/9L1G1E1/9O1E1N1/7VIZOR3/1JAM5E3UR/B1SIA?ANGS3NE/E2L2YOU1W2PI/RI1D1LENT1H1QI1/AW1E5FA1ICE/TRISTATE1OM2K1/EE1T3FARSIDP1/1NU2DATE4D1/1C1OBI9/RHINO10"
    )


def test_something_else():
    print("i am testing something else")
    assert "Foo"


def test_longrunning():
    import time
    time.sleep(2)
    assert "I am a banana"
