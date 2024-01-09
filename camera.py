import pygame

import pygame.camera
from io import BytesIO


class CameraManager:
    def __init__(self, cam_res, selected_option):
        self.cam_res = cam_res
        self.cam = pygame.camera.Camera(selected_option, cam_res)
        self.snapshot = pygame.surface.Surface(cam_res, 0)

    def start_camera(self):
        self.cam.start()
        # Actual res.. is there a way to get this earlier?
        print("actual camera resolution is", self.cam.get_size())

    def capture_image(self):
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)
            return pygame.transform.scale(self.snapshot, (512, 288))
        return None

    def process_snapshot(self, rotate: bool, contains_rack: bool):
        return process_snapshot(self.snapshot, self.cam_res, rotate, contains_rack)

    def stop_camera(self):
        self.cam.stop()


class MockCameraManager:
    def __init__(self, cam_res, img_file):
        self.cam_res = cam_res
        self.img_file = img_file
        self.snapshot = pygame.surface.Surface(cam_res, 0)

    def start_camera(self):
        print("Started mock camera")

    def capture_image(self):
        self.snapshot = pygame.image.load(self.img_file)
        return pygame.transform.scale(self.snapshot, (512, 288))

    def process_snapshot(self, rotate: bool, contains_rack: bool):
        return process_snapshot(self.snapshot, self.cam_res, rotate, contains_rack)

    def stop_camera(self):
        print("Stop mock camera")


def process_snapshot(
    snapshot: pygame.Surface, cam_res: tuple, rotate: bool, contains_rack: bool
):
    board_buffer = BytesIO()
    # We are assuming that the board is facing the player, and
    # thus away from the bot. So we should rotate the snapshot so that
    # it's from the bot's perspective.
    if rotate:
        snapshot = pygame.transform.rotate(snapshot, 180)

    pygame.image.save(snapshot, board_buffer, "JPEG")
    pygame.image.save(snapshot, "board.jpg")

    rack_buffer = BytesIO()

    if contains_rack:
        # Figure out a rough position for the rack. This is very kludgy.
        source_x_size = cam_res[0] / 2
        source_y_size = cam_res[1] / 5
        source_x_top = cam_res[0] / 3
        source_y_top = 4 * cam_res[1] / 5

        cropped = pygame.Surface((source_x_size, source_y_size))
        cropped.blit(
            snapshot,
            (0, 0),
            (source_x_top, source_y_top, source_x_size, source_y_size),
        )
        pygame.image.save(cropped, rack_buffer, "JPEG")
        pygame.image.save(cropped, "rack.jpg")

    return board_buffer.getvalue(), rack_buffer.getvalue()
