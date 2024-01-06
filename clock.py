import time


class ScrabbleClock:
    def __init__(self, initial_time):
        self.initial_time = initial_time
        self.left_time = initial_time
        self.right_time = initial_time
        self.left_active = False
        self.right_active = False
        self.last_update_time = time.time()

    def update(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time

        if self.left_active:
            self.left_time -= elapsed_time
        if self.right_active:
            self.right_time -= elapsed_time

    def switch_to_left(self):
        self.right_active = False
        self.left_active = True

    def switch_to_right(self):
        self.left_active = False
        self.right_active = True

    def get_times(self):
        return self.left_time, self.right_time
