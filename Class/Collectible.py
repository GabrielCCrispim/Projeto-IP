import pygame
import random
import math

from Config import *

class Collectible:
    def __init__(self, item_type, x, pipe_gap_mid, relative_y):
        self.type = item_type
        self.x = x
        self.rel_y = relative_y 
        self.y = pipe_gap_mid + self.rel_y
        self.collected = False
        self.pulse_timer = random.random() * 10
        
        if self.type == "folha":
            self.radius = 16
            self.base_value = VALOR_FOLHA
        elif self.type == "aguape":
            self.radius = 20
            self.base_value = VALOR_AGUAPE
        else:
            self.radius = 24
            self.base_value = VALOR_MANGA

        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                               int(self.radius*2), int(self.radius*2))

    def update_position(self, x, current_pipe_mid):
        self.x = x
        self.y = current_pipe_mid + self.rel_y
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def draw(self, surface):
        if self.collected: return
        self.pulse_timer += 0.1
        pulse = math.sin(self.pulse_timer) * 2
        draw_rad = self.radius + pulse
        cx, cy = int(self.x), int(self.y)

        if self.type == "folha":
            points = [(cx, cy - draw_rad), (cx + draw_rad, cy + draw_rad/2), (cx, cy + draw_rad), (cx - draw_rad, cy + draw_rad/2)]
            pygame.draw.polygon(surface, GREEN, points)
            pygame.draw.polygon(surface, WHITE, points, 1)
        elif self.type == "aguape":
            pygame.draw.circle(surface, BLUE, (cx, cy), draw_rad)
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), draw_rad-5)
            pygame.draw.circle(surface, YELLOW, (cx, cy), 4) 
        else: 
            rect_manga = pygame.Rect(cx - draw_rad*0.8, cy - draw_rad, draw_rad*1.6, draw_rad*2)
            pygame.draw.ellipse(surface, ORANGE, rect_manga)
            pygame.draw.ellipse(surface, (255, 200, 100), (cx - draw_rad*0.4, cy - draw_rad*0.6, draw_rad*0.5, draw_rad*0.8))
            pygame.draw.line(surface, BROWN, (cx, cy - draw_rad), (cx, cy - draw_rad - 5), 3)
