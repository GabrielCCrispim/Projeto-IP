import pygame

from Config import *

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 0
        self.max_time = 60 
        self.font = pygame.font.SysFont(None, 32, bold=True)

    def update(self):
        self.y -= 1.5 
        self.timer += 1

    def draw(self, surface):
        if self.timer < self.max_time:
            alpha = 255 - int((self.timer / self.max_time) * 255)
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            shadow_surf = self.font.render(self.text, True, BLACK)
            shadow_surf.set_alpha(alpha)
            surface.blit(shadow_surf, (self.x + 2, self.y + 2))
            surface.blit(text_surf, (self.x, self.y))