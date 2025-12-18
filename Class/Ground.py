import pygame

from Config import *

class Ground:
    def __init__(self):
        self.y = HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = WIDTH

    def update(self, dt, current_speed):
        dx = current_speed * dt
        self.x1 -= dx
        self.x2 -= dx
        if self.x1 + WIDTH <= 0: self.x1 = self.x2 + WIDTH
        if self.x2 + WIDTH <= 0: self.x2 = self.x1 + WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, (0, self.y, WIDTH, GROUND_HEIGHT))
        offset1 = int(self.x1 % 40)
        offset2 = int(self.x2 % 40)
        for i in range(0, WIDTH, 40):
            pygame.draw.circle(surface, BROWN_DARK, (i + offset1, self.y + 30), 4)
            pygame.draw.circle(surface, BROWN_DARK, (i + offset2, self.y + 60), 6)
        pygame.draw.rect(surface, GREEN_PIPE, (0, self.y, WIDTH, 15))
        pygame.draw.line(surface, GREEN_LIGHT, (0, self.y), (WIDTH, self.y), 3)