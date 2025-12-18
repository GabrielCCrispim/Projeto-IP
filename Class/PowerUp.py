import pygame
import random
import math

from Config import *

class PowerUp:
    def __init__(self, x, pipe_gap_mid, relative_y):
        self.type = random.choice(["clock","shield"])
        self.x = x
        self.rel_y = relative_y 
        self.y = pipe_gap_mid + self.rel_y
        self.radius = 18
        self.collected = False
        self.rect = pygame.Rect(x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        self.float_offset = 0
        self.pulse_timer = 0

    def update(self, dt, speed, current_pipe_mid):
        self.x -= speed * dt
        self.float_offset += 5 * dt
        self.pulse_timer += dt * 3
        base_y = current_pipe_mid + self.rel_y
        self.y = base_y + math.sin(self.float_offset) * 3
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def draw(self, surface):
        if self.collected: return
        pulse = 2 + math.sin(self.pulse_timer) * 2
        pygame.draw.circle(surface, SHIELD_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius + int(pulse), 1)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 4, 1)
        font = pygame.font.SysFont(None, 24)
        txt = font.render("S", True, BLACK)
        surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))
        if self.type == "clock":
            pygame.draw.circle(surface, (180, 180, 255), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

            # ponteiros
            pygame.draw.line(surface, BLACK,
                            (self.x, self.y),
                            (self.x, self.y - 8), 2)
            pygame.draw.line(surface, BLACK,
                            (self.x, self.y),
                            (self.x + 6, self.y), 2)