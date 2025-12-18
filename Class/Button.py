import pygame

from Config import *

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        try:
            pygame.draw.rect(surface, (50, 20, 20), shadow_rect, border_radius=12)
            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=12)
        except TypeError:
            pygame.draw.rect(surface, (50, 20, 20), shadow_rect)
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)