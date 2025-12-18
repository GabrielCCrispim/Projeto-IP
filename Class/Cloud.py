import pygame
import random

from Config import *

class Cloud:
    def __init__(self, x=None):
        self.x = x if x is not None else random.randint(WIDTH, WIDTH + 400)
        self.y = random.randint(20, HEIGHT // 2)
        self.speed = random.randint(15, 40)
        self.pattern = random.choice(CLOUD_PATTERNS)
        self.pixel_size = random.randint(25, 45)
        self.width = len(self.pattern[0]) * self.pixel_size

    def update(self, dt):
        self.x -= self.speed * dt

    def draw(self, surface):
        for row_index, row in enumerate(self.pattern):
            for col_index, char in enumerate(row):
                rect_x = self.x + col_index * self.pixel_size
                rect_y = self.y + row_index * self.pixel_size
                rect = pygame.Rect(rect_x, rect_y, self.pixel_size, self.pixel_size)
                
                if char == 'W':
                    pygame.draw.rect(surface, CLOUD_MAIN_COLOR, rect)
                elif char == 'B':
                    pygame.draw.rect(surface, CLOUD_SHADOW_COLOR, rect)