import pygame.camera
from io import BytesIO


class CameraManager:
    def __init__(self, cam_res, selected_option):
        self.cam_res = cam_res
        self.cam = pygame.camera.Camera(selected_option, cam_res)
        self.snapshot = None

    def start_camera(self):
        self.cam.start()
        # Actual res.. is there a way to get this earlier?
        print("actual camera resolution is", self.cam.get_size())

    def capture_image(self):
        if self.cam.query_image():
            self.snapshot = self.cam.get_image(self.snapshot)
            return pygame.transform.scale(self.snapshot, (512, 288))
        return None

    def process_snapshot(self):
        buffer = BytesIO()
        pygame.image.save(self.snapshot, buffer, "JPEG")
        pygame.image.save(self.snapshot, "tmp.jpg")
        return buffer.getvalue()

    def stop_camera(self):
        self.cam.stop()
