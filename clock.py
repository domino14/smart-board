import time
import math
import os


import pygame


class ScrabbleClockAndScores:
    def __init__(self, initial_time, p1, p2):  # p1 is left, p2 is right
        self.initial_time = initial_time
        self.left_time = initial_time
        self.right_time = initial_time
        self.left_active = False
        self.right_active = False
        self.last_update_time = time.time()
        self.left_score = 0
        self.right_score = 0
        self.p1 = p1
        self.p2 = p2

    def update(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time

        if self.left_active:
            self.left_time -= elapsed_time
        if self.right_active:
            self.right_time -= elapsed_time

    def switch_to_left(self):
        switched = True
        if self.left_active:
            switched = False

        self.right_active = False
        self.left_active = True
        return switched

    def switch_to_right(self):
        switched = True
        if self.right_active:
            switched = False

        self.left_active = False
        self.right_active = True
        return switched

    def stop_both_clocks(self):
        self.left_active = False
        self.right_active = False

    def get_times(self):
        return self.left_time, self.right_time

    def update_scores(self, l, r):
        self.left_score = l
        self.right_score = r

    def on_turn(self):
        if self.left_active:
            return self.p1
        if self.right_active:
            return self.p2


def draw_red_circle(surface, position):
    pygame.draw.circle(surface, (255, 0, 0), position, 20)  # (255, 0, 0) is red


def format_time(t):
    # Determine the sign and work with the absolute value
    sign = "-" if t < 0 else ""
    abs_t = abs(t)

    # Calculate minutes and seconds
    minutes = abs_t // 60
    seconds = abs_t % 60

    if t < 0:
        seconds = math.ceil(seconds)

    return f"{sign}{int(minutes)}:{int(seconds):02}"


def draw_clocks_and_scores(
    scrabble_clock: ScrabbleClockAndScores,
    timer_font,
    score_font,
    window_height,
    window_width,
    window,
):
    left_time, right_time = scrabble_clock.get_times()
    left_timer_surface = timer_font.render(format_time(left_time), True, (0, 0, 0))
    right_timer_surface = timer_font.render(format_time(right_time), True, (0, 0, 0))

    # Calculate positions for the timers and labels
    left_timer_pos = (50, window_height - 50)
    right_timer_pos = (
        window_width - right_timer_surface.get_width() - 125,
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
        right_timer_pos[0],
        right_timer_pos[1] + right_timer_surface.get_height(),
    )
    stop_label_pos = (
        (left_timer_pos[0] + right_timer_pos[0]) / 2,
        left_timer_pos[1] + left_timer_surface.get_height(),
    )

    left_score_pos = (
        left_timer_pos[0] + 200,
        left_timer_pos[1] - left_timer_surface.get_height() - 40,
    )

    right_score_pos = (
        right_timer_pos[0] - 90,
        right_timer_pos[1] - right_timer_surface.get_height() - 40,
    )

    # Render the label surfaces
    left_label_surface = timer_font.render("(L Shift - BOT)", True, (0, 0, 0))
    right_label_surface = timer_font.render("(R Shift - YOU)", True, (0, 0, 0))
    stop_clock_label_surface = timer_font.render("(B - STOP CLOCK)", True, (0, 0, 0))

    # Render the score surfaces
    left_score_surface = score_font.render(
        f"{scrabble_clock.left_score}    -    ", True, (0, 0, 0)
    )
    right_score_surface = score_font.render(
        f"{scrabble_clock.right_score}", True, (0, 0, 0)
    )

    window.blit(left_timer_surface, left_timer_pos)
    window.blit(right_timer_surface, right_timer_pos)
    window.blit(left_label_surface, left_label_pos)
    window.blit(right_label_surface, right_label_pos)
    window.blit(left_score_surface, left_score_pos)
    window.blit(right_score_surface, right_score_pos)
    window.blit(stop_clock_label_surface, stop_label_pos)

    if scrabble_clock.left_active:
        draw_red_circle(window, left_circle_pos)
    elif scrabble_clock.right_active:
        draw_red_circle(window, right_circle_pos)
