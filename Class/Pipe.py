import pygame
import random

from Config import *
from Class.PowerUp import PowerUp
from Class.Collectible import Collectible

class Pipe:
    def __init__(self, x, gap_size, multiplier):
        self.x = x
        self.width = PIPE_WIDTH
        self.passed = False
        self.gap = gap_size
        margin = 80
        self.gap_mid = random.randint(margin + self.gap//2, HEIGHT - GROUND_HEIGHT - margin - self.gap//2)
        self.top_y = self.gap_mid - self.gap//2
        self.bottom_y = self.gap_mid + self.gap//2
        self.collectibles = []
        self.powerups = []
        self.moving = False
        self.move_speed = 0
        self.move_dir = 1
        
        if multiplier >= 3 and random.random() < 0.6: 
            self.moving = True
            self.move_speed = random.randint(40, 120)
            self.move_dir = random.choice([-1, 1])

        cx = self.x + self.width / 2
        chance = random.random()
        
        if random.random() < 0.12 and not self.moving:
            self.powerups.append(PowerUp(cx, self.gap_mid, 0))
        else:
            if chance < 0.10: 
                item_type = "manga"
                offset = (self.gap // 2) - 30 
                direction = random.choice([-1, 1])
                self.collectibles.append(Collectible(item_type, cx, self.gap_mid, offset * direction))
            elif chance < 0.35:
                item_type = "aguape"
                offset = random.choice([-30, 30, 0])
                self.collectibles.append(Collectible(item_type, cx, self.gap_mid, offset))
            elif chance < 0.85:
                item_type = "folha"
                for i in [-1, 0, 1]:
                    offset = i * 30
                    self.collectibles.append(Collectible(item_type, cx, self.gap_mid, offset))

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
