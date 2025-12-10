"""
Capivara Voadora - versão completa pronta para rodar
Rodar:
    pip install pygame
    python capivara_fly.py
"""

import pygame
import sys
import random
import math

# ---------- Configurações ----------
WIDTH, HEIGHT = 1280, 720
FPS = 60

# Capivara
CAPY_X = 180
CAPY_RADIUS = 22

# Tubos
PIPE_WIDTH = 80
PIPE_GAP = 220
PIPE_INTERVAL_MS = 1200  # milissegundos entre tubos

# Chão
GROUND_HEIGHT = 100

# Física (valores em pixels e segundos)
GRAVITY = 1500.0         # px / s^2
JUMP_VELOCITY = -420.0   # px / s
MAX_DROP_SPEED = 1000.0  # px / s

# Cores
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
SKY = (120, 200, 255)
GREEN = (80, 200, 120)
BROWN = (120, 85, 60)
YELLOW = (255, 210, 50)

# ---------- Classes ----------

class Capivara:
    """Jogador principal: posição, física, desenho e colisão"""
    def __init__(self, x=CAPY_X, y=HEIGHT//2):
        self.x = x
        self.y = y
        self.radius = CAPY_RADIUS
        self.vel = 0.0
        self.alive = True
        self.rotation = 0  # estética

    def jump(self):
        self.vel = JUMP_VELOCITY

    def update(self, dt):
        # dt em segundos
        self.vel += GRAVITY * dt
        if self.vel > MAX_DROP_SPEED:
            self.vel = MAX_DROP_SPEED
        self.y += self.vel * dt

        # limitar ao topo
        if self.y < self.radius:
            self.y = self.radius
            self.vel = 0

        # rotação estética baseada na velocidade
        self.rotation = max(-25, min(25, -self.vel * 0.05))

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           int(self.radius*2), int(self.radius*2))

    def draw(self, surface):
        # Sombra: desenhar em Surface com alpha e depois blit
        shadow_w = self.radius*2 + 8
        shadow_h = self.radius//1 + 8
        shadow_surf = pygame.Surface((shadow_w, int(shadow_h)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, shadow_w, shadow_h))
        shadow_pos = (int(self.x - shadow_w//2 + 8), int(self.y + 12))
        surface.blit(shadow_surf, shadow_pos)

        # corpo (círculo)
        pygame.draw.circle(surface, BROWN, (int(self.x), int(self.y)), self.radius)
        # olho
        pygame.draw.circle(surface, WHITE, (int(self.x+6), int(self.y-6)), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x+7), int(self.y-6)), 2)
        # sorriso (arco)
        arc_rect = pygame.Rect(int(self.x-6), int(self.y-2), 12, 8)
        pygame.draw.arc(surface, BLACK, arc_rect, 3.5, 6.0, 2)


class Pipe:
    """Tubo (par): uma parte superior e uma inferior com espaço entre elas"""
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        margin = 60
        gap_mid = random.randint(margin + PIPE_GAP//2, HEIGHT - GROUND_HEIGHT - margin - PIPE_GAP//2)
        self.top_y = gap_mid - PIPE_GAP//2
        self.bottom_y = gap_mid + PIPE_GAP//2
        self.passed = False

    def update(self, dt, speed):
        # speed em px/segundo
        self.x -= speed * dt

    def off_screen(self):
        return self.x + self.width < -50

    def collides_with(self, rect):
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top_y))
        bottom_rect = pygame.Rect(int(self.x), int(self.bottom_y), self.width,
                                  int(HEIGHT - self.bottom_y - GROUND_HEIGHT))
        return rect.colliderect(top_rect) or rect.colliderect(bottom_rect)

    def draw(self, surface):
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top_y))
        bottom_rect = pygame.Rect(int(self.x), int(self.bottom_y), self.width,
                                  int(HEIGHT - self.bottom_y - GROUND_HEIGHT))
        pygame.draw.rect(surface, GREEN, top_rect)
        pygame.draw.rect(surface, GREEN, bottom_rect)
        pygame.draw.rect(surface, (30,100,30), top_rect, 4)
        pygame.draw.rect(surface, (30,100,30), bottom_rect, 4)


class Ground:
    """Chão que se move (parallax simples)"""
    def __init__(self):
        self.y = HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = WIDTH
        self.speed = 120  # px/segundo

    def update(self, dt):
        dx = self.speed * dt
        self.x1 -= dx
        self.x2 -= dx
        if self.x1 + WIDTH <= 0:
            self.x1 = self.x2 + WIDTH
        if self.x2 + WIDTH <= 0:
            self.x2 = self.x1 + WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, (90,60,30), (0, self.y, WIDTH, GROUND_HEIGHT))
        # marcas de madeira (simples)
        offset1 = int(self.x1 % 40)
        offset2 = int(self.x2 % 40)
        for i in range(0, WIDTH, 40):
            pygame.draw.rect(surface, (70,50,25), (i + offset1, self.y + 5, 20, 8))
            pygame.draw.rect(surface, (70,50,25), (i + offset2, self.y + 5, 20, 8))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Capivara Voadora")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # fonte: None para fallback cross-platform
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 22)

        self.reset()

        # evento custom para gerar tubos
        self.PIPE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.PIPE_EVENT, PIPE_INTERVAL_MS)

    def reset(self):
        self.capy = Capivara()
        self.ground = Ground()
        self.pipes = []
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.started = False
        self.pipe_speed = 300  # px por segundo
        self.time = 0.0

    def spawn_pipe(self):
        new_pipe = Pipe(WIDTH + 20)
        self.pipes.append(new_pipe)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if not self.started:
                        self.started = True
                        self.capy.jump()
                    elif self.game_over:
                        self.reset()
                    else:
                        self.capy.jump()
                elif e.key == pygame.K_r and self.game_over:
                    self.reset()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not self.started:
                    self.started = True
                    self.capy.jump()
                elif self.game_over:
                    self.reset()
                else:
                    self.capy.jump()
            elif e.type == self.PIPE_EVENT and self.started and not self.game_over:
                self.spawn_pipe()

    def update(self, dt):
        # dt em segundos
        if not self.started or self.game_over:
            # anima o chão mesmo sem começar
            self.ground.update(dt)
            return

        self.time += dt
        self.capy.update(dt)
        self.ground.update(dt)

        # atualiza pipes e verifica colisões/pontuação
        for pipe in list(self.pipes):
            pipe.update(dt, self.pipe_speed)

            # marcar ponto quando a capivara passa do pipe (centro do pipe)
            if not pipe.passed and pipe.x + pipe.width < self.capy.x:
                pipe.passed = True
                self.score += 1

            if pipe.collides_with(self.capy.get_rect()):
                self.game_over = True
                self.capy.alive = False

            if pipe.off_screen():
                self.pipes.remove(pipe)

        # colisão com o chão
        if self.capy.y + self.capy.radius >= HEIGHT - GROUND_HEIGHT:
            self.capy.y = HEIGHT - GROUND_HEIGHT - self.capy.radius
            self.game_over = True
            self.capy.alive = False

    def draw_start(self):
        self.screen.fill(SKY)
        self.ground.draw(self.screen)
        title = self.font.render("Capivara Voadora", True, BLACK)
        hint = self.small_font.render("Pressione SPACE ou clique para começar", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//3 + 40)))
        # desenhar capivara estática como demo
        # posicionar levemente acima do chão para parecer pendurada
        self.capy.y = HEIGHT//2
        self.capy.draw(self.screen)

    def draw_game(self):
        self.screen.fill(SKY)

        # Sol
        sun_radius = 60
        sun_pos = (WIDTH - 150, 150)
        pygame.draw.circle(self.screen, YELLOW, sun_pos, sun_radius)
        # Raios (simples)
        for angle in range(0, 360, 30):
            ray_x = sun_pos[0] + int(sun_radius * 1.5 * math.cos(math.radians(angle)))
            ray_y = sun_pos[1] + int(sun_radius * 1.5 * math.sin(math.radians(angle)))
            pygame.draw.line(self.screen, YELLOW, sun_pos, (ray_x, ray_y), 3)

        # Tubos
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Capivara
        self.capy.draw(self.screen)

        # Chão
        self.ground.draw(self.screen)

        # Pontuação
        score_surf = self.font.render(str(self.score), True, BLACK)
        self.screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 30))

    def draw_game_over(self):
        # desenha o jogo por baixo
        self.draw_game()
        # overlay de painel
        overlay = pygame.Surface((WIDTH - 40, 140), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        self.screen.blit(overlay, (20, HEIGHT//2 - 70))
        go_text = self.font.render("Game Over", True, BLACK)
        score_text = self.small_font.render(f"Score: {self.score}", True, BLACK)
        high = max(self.high_score, self.score)
        high_text = self.small_font.render(f"Highscore: {high}", True, BLACK)
        hint = self.small_font.render("Press SPACE / click to restart", True, BLACK)
        self.screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 5))
        self.screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, HEIGHT//2 + 35))
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 65))
        if self.score > self.high_score:
            self.high_score = self.score

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0  # dt em segundos
            self.handle_events()
            self.update(dt)

            if not self.started:
                self.draw_start()
            elif self.game_over:
                self.draw_game_over()
            else:
                self.draw_game()

            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()