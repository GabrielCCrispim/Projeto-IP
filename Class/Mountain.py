import pygame
import random

from Config import *

class Mountain:
    def __init__(self, x, layer_type):
        self.type = layer_type
        self.x = x
        
        if self.type == 'far':
            self.color = MOUNTAIN_FAR
            self.width = random.randint(300, 600)
            self.height = random.randint(250, 450)
            self.scroll_factor = 0.05 # 5% da velocidade (muito lento)
            self.y_base = HEIGHT - GROUND_HEIGHT + 20 
            # Picos mais irregulares
            self.peak_offset = random.randint(-50, 50)
        else: # near
            self.color = MOUNTAIN_NEAR
            self.width = random.randint(200, 400)
            self.height = random.randint(100, 250)
            self.scroll_factor = 0.15 # 15% da velocidade
            self.y_base = HEIGHT - GROUND_HEIGHT + 10
            self.peak_offset = 0

    def update(self, dt, game_speed):
        self.x -= game_speed * self.scroll_factor * dt

    def draw(self, surface):
        # Desenha um triângulo (montanha)
        points = [
            (self.x, self.y_base),  # Canto esquerdo
            (self.x + self.width // 2 + self.peak_offset, self.y_base - self.height), # Pico
            (self.x + self.width, self.y_base) # Canto direito
        ]
        pygame.draw.polygon(surface, self.color, points)
