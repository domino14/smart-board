import os
import time
from enum import Enum

import pygame
import pygame.camera
from optionbox import OptionBox
from pygame.rect import Rect
import pygame_gui
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine

from clock import ScrabbleClockAndScores, draw_clocks_and_scores
from camera import CameraManager, MockCameraManager
from woogles_api import create_broadcast
from game import WooglesGameManager
from scrabblecam import get_board_and_rack_from_images


class PlayerPosition(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


players = [
    (os.getenv("SMARTBOARD_LEFT_NAME") or "left-player", PlayerPosition.LEFT),
    (os.getenv("SMARTBOARD_RIGHT_NAME") or "right-player", PlayerPosition.RIGHT),
]

bot_position = os.getenv("SMARTBOARD_BOT_POSITION") or PlayerPosition.LEFT
# camera_flip_for: flip the camera 180 degrees when it is this player's turn.
# can be LEFT, RIGHT, ALWAYS, NEVER
camera_flip_for = os.getenv("CAMERA_ORIENTATION") or "ALWAYS"

lexicon = os.getenv("LEXICON_NAME") or "NWL20"
letterdist = os.getenv("LETTER_DISTRIBUTION") or "English"
challenge_rule = os.getenv("CHALLENGE_RULE") or "ChallengeRule_DOUBLE"

# Initialize with 25 minutes
scrabble_clock = ScrabbleClockAndScores(25 * 60, players[0], players[1])

# initializing the camera
pygame.camera.init()

# make the list of all available cameras
camlist = pygame.camera.list_cameras()

pygame.init()
window_width, window_height = 800, 500
size = (window_width, window_height)
cam_res = (1280, 720)
window = pygame.display.set_mode(size)

manager = pygame_gui.UIManager((window_width, window_height))


# Setting name for window
pygame.display.set_caption(
    "Where did all these smart boards come from? "
    "I don't think that I can choose just one."
)

running = True

font_size = 30
font = pygame.font.SysFont(None, font_size)

score_font = pygame.font.SysFont("monospace", 48)

list1 = OptionBox(
    500,
    10,
    260,
    40,
    (150, 150, 150),
    (100, 200, 255),
    font,
    camlist,
)

fen_text_input = UITextEntryLine(
    relative_rect=Rect(10, 10, 480, 30), manager=manager, placeholder_text="fen..."
)
rack_text_input = UITextEntryLine(
    relative_rect=Rect(10, 40, 180, 30), manager=manager, placeholder_text="rack..."
)

cam_manager = None

last_time = time.time()
last_blitted_snapshot = None

clock = pygame.time.Clock()

PROCESS_SNAPSHOT_EVENT = pygame.USEREVENT + 1

game_started = False
woogles_game_id = None
last_turn_was = None
player_on_turn = None
last_fen = None

woogles_game_manager = None


def on_turn_is_bot():
    return player_on_turn[1] == bot_position


def start_game(players):
    broadcast_players = players
    if (
        player_on_turn[1] == PlayerPosition.RIGHT
    ):  # If the player on the right starts, then flip for API.
        broadcast_players[0], broadcast_players[1] = (
            broadcast_players[1],
            broadcast_players[0],
        )
    resp = create_broadcast(broadcast_players, lexicon, letterdist, challenge_rule)
    woogles_game_id = resp.get("game_id")
    woogles_game_manager = WooglesGameManager(broadcast_players, bot_position)
    return woogles_game_id, woogles_game_manager


entered_fen = ""
entered_rack = ""
# Game loop
# keep game running till running is true
while running:
    time_delta = clock.tick(10) / 1000.0
    # Check for event if user has pushed
    # any event in queue
    event_list = pygame.event.get()

    process_snapshot = False

    for event in event_list:
        # if event is of type quit then set
        # running bool to false
        if event.type == pygame.QUIT:
            running = False
            if cam_manager:
                cam_manager.stop_camera()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RSHIFT, pygame.K_LSHIFT):
                if not cam_manager:
                    print("select a camera first")
                    continue

                switched = False
                if event.key == pygame.K_RSHIFT:
                    switched = scrabble_clock.switch_to_left()
                if event.key == pygame.K_LSHIFT:
                    switched = scrabble_clock.switch_to_right()

                if switched:
                    pygame.event.post(pygame.event.Event(PROCESS_SNAPSHOT_EVENT))
                    last_turn_was = player_on_turn
                    player_on_turn = scrabble_clock.on_turn()
                    if not game_started:
                        game_started = True
                        woogles_game_id, woogles_game_manager = start_game(players)
                    woogles_game_manager.set_player_on_turn(player_on_turn)

                print("last turn", last_turn_was)
                print("on turn", player_on_turn)
                print("switched", switched)

            if event.key == pygame.K_b:
                if not cam_manager:
                    print("select a camera first")
                    continue
                scrabble_clock.stop_both_clocks()

            if event.key == pygame.K_0:
                pygame.event.post(pygame.event.Event(PROCESS_SNAPSHOT_EVENT))

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == fen_text_input:
                    entered_fen = event.text
                    print("fen", entered_fen)
                elif event.ui_element == rack_text_input:
                    entered_rack = event.text
                    print("rack", entered_rack)

        if event.type == PROCESS_SNAPSHOT_EVENT:
            # PROCESS_SNAPSHOT_EVENT can be triggered by the clocks or by pressing 0
            bot_on_turn = on_turn_is_bot()
            rotate = False
            contains_rack = False
            if bot_on_turn:
                print("Bot is on turn; assume contains_rack and rotate")
                rotate = True
                contains_rack = True
            if camera_flip_for == "ALWAYS":
                print("Always rotating camera")
                rotate = True
            elif camera_flip_for == player_on_turn[1]:
                print("Player on turn is", player_on_turn[1], "so flipping camera")
                rotate = True
            board_img, rack_img = cam_manager.process_snapshot(rotate, contains_rack)
            # fen, rack_letters = get_board_and_rack_from_images(board_img, rack_img)
            fen, rack_letters = entered_fen, entered_rack
            woogles_game_manager.process_board_and_rack(fen, rack_letters)

        manager.process_events(event)

    manager.update(time_delta)
    scrabble_clock.update()

    selected_option = list1.update(event_list)
    if selected_option >= 0:
        cam_manager = CameraManager(cam_res, camlist[selected_option])
        # cam_manager = MockCameraManager(cam_res, "./testdata/H6kV.jpg")
        cam_manager.start_camera()

    window.fill((255, 255, 255))
    list1.draw(window)

    # Draw the camera at only a few hz.
    if cam_manager and time.time() - last_time > 0.25:
        last_blitted_snapshot = cam_manager.capture_image()
        last_time = time.time()

    if last_blitted_snapshot:
        window.blit(last_blitted_snapshot, (144, 100))

    draw_clocks_and_scores(
        scrabble_clock, font, score_font, window_height, window_width, window
    )
    manager.draw_ui(window)

    pygame.display.flip()
