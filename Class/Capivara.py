import pygame

from Config import *

class Capivara:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.vel = 0

        # física / estado
        self.radius = 25
        self.rotation = 0
        self.alive = True

        # escudo / imunidade
        self.has_shield = False
        self.immunity_timer = 0.0

        # sprites
        self.frame_parado = pygame.image.load(
            "imagens/capivaravoadoraparada.png"
        ).convert_alpha()

        self.frame_voando = pygame.image.load(
            "imagens/capivaravoando.png"
        ).convert_alpha()

        self.frame_parado = pygame.transform.scale(self.frame_parado, (64, 48))
        self.frame_voando = pygame.transform.scale(self.frame_voando, (64, 48))

        self.frames = [self.frame_parado, self.frame_voando]
        self.frame_index = 0
        self.anim_timer = 0
        self.image = self.frames[0]

    def jump(self):
        self.vel = JUMP_VELOCITY

    def dive(self):
        self.vel = DIVE_VELOCITY

    def update(self, dt):
        # gravidade e movimento
        self.vel += GRAVITY * dt
        if self.vel > MAX_DROP_SPEED:
            self.vel = MAX_DROP_SPEED
        self.y += self.vel * dt

        # rotação baseada na velocidade (visual)
        self.rotation = max(-30, min(30, -self.vel * 0.05))

        # imunidade temporária
        if self.immunity_timer > 0:
            self.immunity_timer -= dt
            if self.immunity_timer < 0:
                self.immunity_timer = 0

        # animação
        self.anim_timer += dt
        if self.anim_timer > 0.12:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def get_rect(self):
        hitbox_radius = self.radius - 6
        return pygame.Rect(
            int(self.x - hitbox_radius),
            int(self.y - hitbox_radius),
            hitbox_radius * 2,
            hitbox_radius * 2
        )

    def draw(self, surface):
        rot_image = pygame.transform.rotate(self.image, self.rotation)
        rect = rot_image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rot_image, rect)
        # escudo visual
        if self.has_shield:
            pygame.draw.circle(surface, (0, 255, 255, 100), (int(self.x), int(self.y)), self.radius + 12, 3)