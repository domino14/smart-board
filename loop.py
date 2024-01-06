# Python program to capture a single image
# using pygame library

# importing the pygame library
import pygame
import pygame.camera
from optionbox import OptionBox
from io import BytesIO
from scrabblecam import get_from_scrabblecam
from clock import ScrabbleClock


scrabble_clock = ScrabbleClock(25 * 60)  # Initialize with 25 minutes

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
pygame.display.set_caption("Where did all these smart boards come from?")

running = True

clock = pygame.time.Clock()
font_size = 30
font = pygame.font.SysFont(None, font_size)

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


cam = None
snapshot = None


def draw_red_circle(surface, position):
    pygame.draw.circle(surface, (255, 0, 0), position, 20)  # (255, 0, 0) is red


# Game loop
# keep game running till running is true
while running:
    clock.tick(20)

    # Check for event if user has pushed
    # any event in queue
    event_list = pygame.event.get()

    process_snapshot = False

    for event in event_list:
        # if event is of type quit then set
        # running bool to false
        if event.type == pygame.QUIT:
            running = False
            if cam:
                cam.stop()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RSHIFT:
                if not cam:
                    print("select a camera first")
                    continue
                # Start the left player's timer
                scrabble_clock.switch_to_left()
                # Left player is always the bot (for now I guess)
                process_snapshot = True

            if event.key == pygame.K_LSHIFT:
                if not cam:
                    print("select a camera first")
                    continue
                # Start the right player's timer
                scrabble_clock.switch_to_right()

    scrabble_clock.update()

    selected_option = list1.update(event_list)
    if selected_option >= 0:
        snapshot = pygame.surface.Surface(cam_res, 0, window)
        cam = pygame.camera.Camera(selected_option, cam_res)
        cam.start()
        print(cam.get_size())  # Actual res.. is there a way to get this earlier?

    window.fill((255, 255, 255))
    list1.draw(window)

    if cam and cam.query_image():
        snapshot = cam.get_image(snapshot)
        scaled = pygame.transform.scale(snapshot, (512, 288))
        window.blit(scaled, (100, 100))
        if process_snapshot:
            buffer = BytesIO()
            pygame.image.save(snapshot, buffer, "JPEG")
            img = buffer.getvalue()
            res_json = get_from_scrabblecam("board", img)
            print(res_json)

    left_time, right_time = scrabble_clock.get_times()
    left_timer_surface = font.render(
        f"{int(left_time // 60)}:{int(left_time % 60):02}", True, (0, 0, 0)
    )
    right_timer_surface = font.render(
        f"{int(right_time // 60)}:{int(right_time % 60):02}", True, (0, 0, 0)
    )

    # Calculate positions for the timers and labels
    left_timer_pos = (50, window_height - 50)
    right_timer_pos = (
        window_width - right_timer_surface.get_width() - 50,
        window_height - 50,
    )

    left_circle_pos = (left_timer_pos[0], left_timer_pos[1] - 30)
    right_circle_pos = (
        right_timer_pos[0] + right_timer_surface.get_width(),
        right_timer_pos[1] - 30,
    )

    left_label_pos = (
        left_timer_pos[0],
        left_timer_pos[1] + left_timer_surface.get_height(),
    )
    right_label_pos = (
        right_timer_pos[0] - 50,
        right_timer_pos[1] + right_timer_surface.get_height(),
    )

    # Render the label surfaces
    left_label_surface = font.render("(L Shift - BOT)", True, (0, 0, 0))
    right_label_surface = font.render("(R Shift - YOU)", True, (0, 0, 0))

    window.blit(left_timer_surface, left_timer_pos)
    window.blit(right_timer_surface, right_timer_pos)
    window.blit(left_label_surface, left_label_pos)
    window.blit(right_label_surface, right_label_pos)

    if scrabble_clock.left_active:
        draw_red_circle(window, left_circle_pos)
    elif scrabble_clock.right_active:
        draw_red_circle(window, right_circle_pos)

    pygame.display.flip()
