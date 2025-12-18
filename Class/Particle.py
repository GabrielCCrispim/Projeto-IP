import pygame
import math
import random

from Config import *

class Particle:
    def __init__(self, x, y, color=WHITE, explosive=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 6)
        self.life = 255
        self.decay = random.randint(10, 20)
        
        if explosive:
            speed = random.randint(100, 300)
            angle = random.uniform(0, 6.28)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.decay = random.randint(5, 10)
        else:
            self.vx = -random.randint(50, 150)
            self.vy = random.randint(-50, 50)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay
        if self.life < 0: self.life = 0

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            rgba = self.color + (self.life,)
            pygame.draw.circle(s, rgba, (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))