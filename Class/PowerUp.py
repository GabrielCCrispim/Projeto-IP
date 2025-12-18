import pygame
import random
import math

from Config import *

class PowerUp:
    def __init__(self, x, pipe_gap_mid, relative_y):
        self.type = random.choice(["shield", "clock"])
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
    def update(self, dt, speed):
        self.x -= speed * dt
        if self.moving:
            self.gap_mid += self.move_speed * self.move_dir * dt
            if random.random() < 0.02: self.move_speed = random.randint(40, 150)
            margin = 80
            top_limit = margin + self.gap//2
            bot_limit = HEIGHT - GROUND_HEIGHT - margin - self.gap//2
            if self.gap_mid < top_limit:
                self.gap_mid = top_limit
                self.move_dir = 1
                self.move_speed = random.randint(50, 100)
            elif self.gap_mid > bot_limit:
                self.gap_mid = bot_limit
                self.move_dir = -1
                self.move_speed = random.randint(50, 100)
            self.top_y = self.gap_mid - self.gap//2
            self.bottom_y = self.gap_mid + self.gap//2

        cx = self.x + self.width / 2
        for c in self.collectibles:
            if not c.collected: c.update_position(cx, self.gap_mid)
        for p in self.powerups:
            if not p.collected: p.update(dt, speed, self.gap_mid)

    def off_screen(self): return self.x + self.width < -50
    def collides_with(self, rect):
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top_y))
        bottom_rect = pygame.Rect(int(self.x), int(self.bottom_y), self.width,
                                 int(HEIGHT - self.bottom_y - GROUND_HEIGHT))
        return rect.colliderect(top_rect) or rect.colliderect(bottom_rect)

    def draw(self, surface):
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top_y))
        pygame.draw.rect(surface, GREEN_PIPE, top_rect)
        pygame.draw.rect(surface, GREEN_DARK, top_rect, 4)
        pygame.draw.rect(surface, GREEN_LIGHT, (self.x + 10, 0, 10, self.top_y))
        
        cap_height = 25
        top_cap = pygame.Rect(self.x - 5, self.top_y - cap_height, self.width + 10, cap_height)
        pygame.draw.rect(surface, GREEN_PIPE, top_cap)
        pygame.draw.rect(surface, GREEN_DARK, top_cap, 4)

        bottom_rect = pygame.Rect(int(self.x), int(self.bottom_y), self.width,
                                 int(HEIGHT - self.bottom_y - GROUND_HEIGHT))
        pygame.draw.rect(surface, GREEN_PIPE, bottom_rect)
        pygame.draw.rect(surface, GREEN_DARK, bottom_rect, 4)
        pygame.draw.rect(surface, GREEN_LIGHT, (self.x + 10, self.bottom_y, 10, HEIGHT))
        
        bot_cap = pygame.Rect(self.x - 5, self.bottom_y, self.width + 10, cap_height)
        pygame.draw.rect(surface, GREEN_PIPE, bot_cap)
        pygame.draw.rect(surface, GREEN_DARK, bot_cap, 4)

        for c in self.collectibles: c.draw(surface)
        for p in self.powerups: p.draw(surface)