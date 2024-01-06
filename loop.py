import time

import pygame
import pygame.camera
from optionbox import OptionBox


from scrabblecam import get_from_scrabblecam
from clock import ScrabbleClockAndScores, draw_clocks_and_scores
from cgp import scrabblecam_to_fen
from camera import CameraManager


scrabble_clock = ScrabbleClockAndScores(25 * 60)  # Initialize with 25 minutes

# initializing the camera
pygame.camera.init()

# make the list of all available cameras
camlist = pygame.camera.list_cameras()

pygame.init()
window_width, window_height = 800, 500
size = (window_width, window_height)
cam_res = (1280, 720)
window = pygame.display.set_mode(size)

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
    40,
    40,
    260,
    40,
    (150, 150, 150),
    (100, 200, 255),
    font,
    camlist,
)

cam_manager = None

last_time = time.time()
last_blitted_snapshot = None

clock = pygame.time.Clock()

PROCESS_SNAPSHOT_EVENT = pygame.USEREVENT + 1

# Game loop
# keep game running till running is true
while running:
    clock.tick(10)
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
            if event.key == pygame.K_RSHIFT:
                if not cam_manager:
                    print("select a camera first")
                    continue
                # Start the left player's timer
                scrabble_clock.switch_to_left()
                # Left player is always the bot (for now I guess)
                pygame.event.post(pygame.event.Event(PROCESS_SNAPSHOT_EVENT))

            if event.key == pygame.K_LSHIFT:
                if not cam_manager:
                    print("select a camera first")
                    continue
                # Start the right player's timer
                scrabble_clock.switch_to_right()

        if event.type == PROCESS_SNAPSHOT_EVENT:
            img = cam_manager.process_snapshot()
            res_json = get_from_scrabblecam("board", img)
            print("res_json", res_json)
            if res_json and res_json.get("board"):
                fen = scrabblecam_to_fen(res_json["board"])
                print(fen)
            else:
                print("Got unexpected response", res_json)

    scrabble_clock.update()

    selected_option = list1.update(event_list)
    if selected_option >= 0:
        # snapshot = pygame.surface.Surface(cam_res, 0, window)
        cam_manager = CameraManager(cam_res, camlist[selected_option])
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

    pygame.display.flip()
