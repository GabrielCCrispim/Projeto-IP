"""
Capivara Voadora - versão inicial
Rodar: pip install pygame
       python capivara_fly.py

Estrutura: POO com classes Game, Capivara, Pipe, Ground
Mecânica: pulo com espaço/ clique, gravidade, tubos gerados aleatoriamente,
pontuação por passar entre os tubos, tela inicial e game over.
Comentários mostram onde adicionar sprites, sons, colecionáveis e variação de dificuldades.
"""

import pygame
import sys
import random
import math

# ---------- Constantes ----------
WIDTH, HEIGHT = 1920, 1080
FPS = 60

# Capivara
CAPY_X = 80
CAPY_RADIUS = 18

# Tubos
PIPE_WIDTH = 80
PIPE_GAP = 225
PIPE_INTERVAL_MS = 900  # tempo entre tubos (ajustar para dificuldade)

# Chão
GROUND_HEIGHT = 100

# Física
GRAVITY = 0.6
JUMP_VELOCITY = -11
MAX_DROP_SPEED = 12

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
        self.rotation = 0  # apenas estético

    def jump(self):
        self.vel = JUMP_VELOCITY

    def update(self, dt):
        # aplicar gravidade
        self.vel += GRAVITY * dt
        if self.vel > MAX_DROP_SPEED:
            self.vel = MAX_DROP_SPEED
        self.y += self.vel * dt

        # limitar ao topo
        if self.y < 0 + self.radius:
            self.y = self.radius
            self.vel = 0

        # rotação estética baseada na velocidade
        # (não necessário para colisão, só visual)
        self.rotation = max(-25, min(25, -self.vel * 2))

    def get_rect(self):
        # aproximação: retângulo central
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           int(self.radius*2), int(self.radius*2))

    def draw(self, surface):
        # desenha sombra
        shadow_pos = (int(self.x+8), int(self.y+12))
        pygame.draw.ellipse(surface, (0,0,0,40), (shadow_pos[0]-self.radius, shadow_pos[1]-self.radius//2, self.radius*2, self.radius))
        # desenha corpo (círculo)
        pygame.draw.circle(surface, BROWN, (int(self.x), int(self.y)), self.radius)
        # olho
        pygame.draw.circle(surface, WHITE, (int(self.x+6), int(self.y-6)), 5)
        pygame.draw.circle(surface, BLACK, (int(self.x+7), int(self.y-6)), 2)
        # sorriso (simples)
        pygame.draw.arc(surface, BLACK, (self.x-6, self.y-2, 12, 8), 3.5, 6.0, 2)

# class Nuvem:

class Pipe:
    """Tubo (pair): uma parte superior e uma inferior com espaço entre elas"""
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        # define posição do gap central (entre top e bottom)
        margin = 60
        gap_mid = random.randint(margin + PIPE_GAP//2, HEIGHT - GROUND_HEIGHT - margin - PIPE_GAP//2)
        self.top = gap_mid - PIPE_GAP//2 - HEIGHT  # desenhar começando acima da tela (uso para retângulo)
        self.bottom = gap_mid + PIPE_GAP//2
        self.passed = False  # para contabilizar pontos

    def update(self, dt, speed):
        self.x -= speed * dt

    def off_screen(self):
        return self.x + self.width < -50

    def collides_with(self, rect):
        # colisão simples por retângulos
        top_rect = pygame.Rect(self.x, 0, self.width, self.bottom - PIPE_GAP)
        bottom_rect = pygame.Rect(self.x, self.bottom, self.width, HEIGHT - self.bottom - GROUND_HEIGHT)
        return rect.colliderect(top_rect) or rect.colliderect(bottom_rect)

    def draw(self, surface):
        # desenha tubos como retângulos verdes com borda escura
        top_rect = pygame.Rect(int(self.x), 0, self.width, self.bottom - PIPE_GAP)
        bottom_rect = pygame.Rect(int(self.x), self.bottom, self.width, HEIGHT - self.bottom - GROUND_HEIGHT)
        # ficar seguro dos retângulos negativos
        pygame.draw.rect(surface, GREEN, top_rect)
        pygame.draw.rect(surface, GREEN, bottom_rect)
        # borda
        pygame.draw.rect(surface, (30,100,30), top_rect, 4)
        pygame.draw.rect(surface, (30,100,30), bottom_rect, 4)


class Ground:
    """Chão que se move (parallax simples)"""
    def __init__(self):
        self.y = HEIGHT - GROUND_HEIGHT
        # duas imagens virtuais para repetir
        self.x1 = 0
        self.x2 = WIDTH
        self.speed = 120

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
        # marcações de madeira
        for i in range(0, WIDTH, 40):
            pygame.draw.rect(surface, (70,50,25), (i + (self.x1%40), self.y + 5, 20, 8))
            pygame.draw.rect(surface, (70,50,25), (i + (self.x2%40), self.y + 5, 20, 8))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Capivara Voadora")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)

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
        self.pipe_speed = 10  # px per second; ajustar para dificuldades
        # tempo acumulado para dt está em segundos com base em clock.tick
        self.time = 0.0

    def spawn_pipe(self):
        # cria novo pipe vindo da direita
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
                        # reinicia
                        self.reset()
                    else:
                        self.capy.jump()
                elif e.key == pygame.K_r and self.game_over:
                    self.reset()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # clique para pular / iniciar
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
        if not self.started or self.game_over:
            # mesmo que parado, atualiza animação do chão para ficar agradável
            self.ground.update(dt)
            return

        self.time += dt
        self.capy.update(dt)
        self.ground.update(dt)

        # atualiza pipes e verifica colisões/pontuação
        for pipe in list(self.pipes):
            pipe.update(dt, self.pipe_speed)
            # marcar ponto quando a capivara passa do pipe
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
        self.capy.draw(self.screen)

    def draw_game(self):
        self.screen.fill(SKY)  # Fundo azul

        # Desenhando o sol (círculo amarelo)
        sun_radius = 60
        sun_pos = (WIDTH - 150, 150)  # posição do sol no canto superior direito
        pygame.draw.circle(self.screen, YELLOW, sun_pos, sun_radius)

        # Se você quiser adicionar raios ao redor do sol, pode desenhar linhas:
        ray_length = 100
        for angle in range(0, 360, 15):  # criando raios a cada 15º
            ray_x = sun_pos[0] + int(sun_radius * 1.5 * math.cos(math.radians(angle)))
            ray_y = sun_pos[1] + int(sun_radius * 1.5 * math.sin(math.radians(angle)))
            pygame.draw.line(self.screen, YELLOW, sun_pos, (ray_x, ray_y), 3)  # raios amarelos

        # Desenhar pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Desenhar a capivara
        self.capy.draw(self.screen)

        # Chão
        self.ground.draw(self.screen)

        # Pontuação
        score_surf = self.font.render(str(self.score), True, BLACK)
        self.screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 30))

    def draw_game_over(self):
        self.draw_game()
        # painel de game over
        overlay = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220))
        self.screen.blit(overlay, (20, HEIGHT//2 - 40))
        go_text = self.font.render("Game Over", True, BLACK)
        score_text = self.small_font.render(f"Score: {self.score}", True, BLACK)
        high = max(self.high_score, self.score)
        high_text = self.small_font.render(f"Highscore: {high}", True, BLACK)
        hint = self.small_font.render("Press SPACE / click to restart", True, BLACK)
        self.screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 30))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 5))
        self.screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, HEIGHT//2 + 30))
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 60))
        # atualizar highscore se necessário
        if self.score > self.high_score:
            self.high_score = self.score

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 16.6667  # normaliza dt para ficar consistente (aprox 60fps => dt=1)
            # alternativa: dt_seconds = dt_ms / 1000.0  (mas valores de velocidades devem ajustar)
            self.handle_events()
            self.update(dt)
            # desenhar
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