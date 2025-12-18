import pygame
import random

from Config import *

class Bird:
    def __init__(self):
        self.direction = random.choice([-1, 1])
        if self.direction == 1: self.x = -50
        else: self.x = WIDTH + 50
        self.y = random.randint(30, HEIGHT // 3)
        self.speed = random.randint(70, 140)
        self.size = random.randint(10, 20)
        self.flap_timer = 0
        self.wing_state = 0 

    def update(self, dt):
        self.x += self.speed * self.direction * dt
        self.flap_timer += dt
        if self.flap_timer > 0.2:
            self.flap_timer = 0
            self.wing_state = 1 - self.wing_state

    def draw(self, surface):
        cx, cy = self.x, self.y
        wing_span = self.size
        if self.wing_state == 0:
            points = [(cx - wing_span, cy - 5), (cx, cy + 2), (cx + wing_span, cy - 5)]
        else:
            points = [(cx - wing_span, cy - 2), (cx, cy + 4), (cx + wing_span, cy - 2)]
        pygame.draw.lines(surface, BIRD_COLOR, False, points, 3)