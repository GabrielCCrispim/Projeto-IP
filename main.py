
import pygame
import sys
import random
import math

# --- Configurações ---
WIDTH, HEIGHT = 1920, 1080
FPS = 60

CAPY_X = 220
CAPY_RADIUS = 30

PIPE_WIDTH = 80
GROUND_HEIGHT = 140

GRAVITY = 1800.0
JUMP_VELOCITY = -520.0
MAX_DROP_SPEED = 1400.0

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
SKY = (120, 200, 255)
GREEN = (80, 200, 120)
BROWN = (120, 85, 60)
YELLOW = (255, 210, 50)
BLUE = (70, 150, 200)
ORANGE = (255, 160, 40)

PROB_FOLHA = 60
PROB_AGUAPE = 30
PROB_MANGA = 10

GAP_BY_TYPE = {
    "folha": 300,
    "aguape": 200,
    "manga": 150
}
POINTS_BY_TYPE = {
    "folha": 1,
    "aguape": 3,
    "manga": 10  # Agora vale 10 pontos
}
DEFAULT_SPAWN_DISTANCE = 650

# --- Classes ---
class Collectible:
    def __init__(self, item_type, x, y):
        self.type = item_type
        self.x = x
        self.y = y
        if self.type == "folha":
            self.radius = 16
        elif self.type == "aguape":
            self.radius = 20
        else:
            self.radius = 26
        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                               int(self.radius*2), int(self.radius*2))
        self.collected = False

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def get_rect(self):
        return self.rect

    def draw(self, surface):
        if self.collected:
            return
        if self.type == "folha":
            pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.radius)
            pygame.draw.line(surface, (40,90,50), (int(self.x-6), int(self.y)), (int(self.x+6), int(self.y)), 2)
        elif self.type == "aguape":
            rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius//1.5),
                              int(self.radius*2), int(self.radius*1.3))
            pygame.draw.ellipse(surface, BLUE, rect)
            pygame.draw.ellipse(surface, (30,90,120), rect, 2)
        else:
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, (220,130,30), (int(self.x+6), int(self.y-6)), 6)

class Capivara:
    def __init__(self, x=CAPY_X, y=HEIGHT//2):
        self.x = x
        self.y = y
        self.radius = CAPY_RADIUS
        self.vel = 0.0
        self.alive = True
        self.rotation = 0

    def jump(self):
        self.vel = JUMP_VELOCITY

    def update(self, dt):
        self.vel += GRAVITY * dt
        if self.vel > MAX_DROP_SPEED:
            self.vel = MAX_DROP_SPEED
        self.y += self.vel * dt
        if self.y < self.radius:
            self.y = self.radius
            self.vel = 0
        self.rotation = max(-25, min(25, -self.vel * 0.05))

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           int(self.radius*2), int(self.radius*2))

    def draw(self, surface):
        shadow_w = self.radius*2 + 12
        shadow_h = max(12, self.radius//1 + 10)
        shadow_surf = pygame.Surface((shadow_w, int(shadow_h)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, shadow_w, shadow_h))
        shadow_pos = (int(self.x - shadow_w//2 + 10), int(self.y + 18))
        surface.blit(shadow_surf, shadow_pos)
        pygame.draw.circle(surface, BROWN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x+8), int(self.y-8)), 6)
        pygame.draw.circle(surface, BLACK, (int(self.x+9), int(self.y-8)), 3)
        arc_rect = pygame.Rect(int(self.x-8), int(self.y-3), 16, 10)
        pygame.draw.arc(surface, BLACK, arc_rect, 3.5, 6.0, 2)


class Pipe:
    def __init__(self, x, gap, collected_item_type=None):
        self.x = x
        self.width = PIPE_WIDTH
        self.passed = False
        self.gap = gap
        margin = 80
        gap_mid = random.randint(margin + self.gap//2, HEIGHT - GROUND_HEIGHT - margin - self.gap//2)
        self.top_y = gap_mid - self.gap//2
        self.bottom_y = gap_mid + self.gap//2

        self.collectibles = []
        if collected_item_type:
            cx = self.x + self.width / 2
            if collected_item_type == "folha":
                # 3 folhas em 1/4, 2/4, 3/4 do gap
                for i in range(1, 4):
                    frac = i / 4
                    cy = self.top_y + frac * self.gap
                    self.collectibles.append(Collectible("folha", cx, cy))
            elif collected_item_type == "aguape":
                # 2 aguapés em 1/4 e 3/4 do gap (exclui o meio)
                for i in [1, 3]:
                    frac = i / 4
                    cy = self.top_y + frac * self.gap
                    self.collectibles.append(Collectible("aguape", cx, cy))
            else:
                # Manga única no centro do gap
                cy = self.top_y + 0.5 * self.gap
                self.collectibles.append(Collectible("manga", cx, cy))

    def update(self, dt, speed):
        self.x -= speed * dt
        for c in self.collectibles:
            if not c.collected:
                cx = self.x + self.width / 2
                # Mantém o offset vertical original
                c.update_position(cx, c.y)

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
        pygame.draw.rect(surface, (30,100,30), top_rect, 6)
        pygame.draw.rect(surface, (30,100,30), bottom_rect, 6)
        for c in self.collectibles:
            if not c.collected:
                c.draw(surface)

class Ground:
    def __init__(self):
        self.y = HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = WIDTH
        self.speed = 180

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
        offset1 = int(self.x1 % 40)
        offset2 = int(self.x2 % 40)
        for i in range(0, WIDTH, 40):
            pygame.draw.rect(surface, (70,50,25), (i + offset1, self.y + 6, 24, 10))
            pygame.draw.rect(surface, (70,50,25), (i + offset2, self.y + 6, 24, 10))

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Capivara Voadora")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 56)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.capy = Capivara()
        self.ground = Ground()
        self.pipes = []
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.started = False
        self.pipe_speed = 380
        self.time = 0.0
        self.counts = {"folha": 0, "aguape": 0, "manga": 0}
        self.spawn_distance = DEFAULT_SPAWN_DISTANCE
        first_type = self._choose_item_type()
        first_gap = GAP_BY_TYPE[first_type]
        first_pipe = Pipe(WIDTH + 40, first_gap, collected_item_type=first_type)
        self.pipes.append(first_pipe)

    def _choose_item_type(self):
        r = random.uniform(0, 100)
        if r < PROB_FOLHA:
            return "folha"
        r -= PROB_FOLHA
        if r < PROB_AGUAPE:
            return "aguape"
        return "manga"

    def spawn_pipe(self):
        item_type = self._choose_item_type()
        gap = GAP_BY_TYPE[item_type]
        new_pipe = Pipe(WIDTH + 40, gap, collected_item_type=item_type)
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

    def update(self, dt):
        if not self.started or self.game_over:
            self.ground.update(dt)
            return
        self.time += dt
        self.capy.update(dt)
        self.ground.update(dt)
        if not self.pipes:
            self.spawn_pipe()
        else:
            last_pipe = self.pipes[-1]
            if last_pipe.x < WIDTH - self.spawn_distance:
                self.spawn_pipe()
        for pipe in list(self.pipes):
            pipe.update(dt, self.pipe_speed)
            if not pipe.passed and pipe.x + pipe.width < self.capy.x:
                pipe.passed = True
            if pipe.collides_with(self.capy.get_rect()):
                self.game_over = True
                self.capy.alive = False
            for c in pipe.collectibles:
                if not c.collected and c.get_rect().colliderect(self.capy.get_rect()):
                    item = c.type
                    pts = POINTS_BY_TYPE.get(item, 0)
                    self.score += pts
                    self.counts[item] += 1
                    c.collected = True
            if pipe.off_screen():
                self.pipes.remove(pipe)
        ground_level = HEIGHT - GROUND_HEIGHT - self.capy.radius
        if self.capy.y >= ground_level:
            self.capy.y = ground_level
            self.capy.vel = 0

    def draw_collectible_counts(self):
        # Placar no canto superior esquerdo
        x = 30
        y = 18
        panel_w = 340
        panel_h = 70
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((255,255,255,200))
        self.screen.blit(panel, (x, y))

        espacamento = 100
        base_x = x + 20
        base_y = y + 18

        # Folha
        folha_x = base_x
        folha_y = base_y + 16
        pygame.draw.circle(self.screen, GREEN, (folha_x, folha_y), 16)
        pygame.draw.line(self.screen, (40,90,50), (folha_x-6, folha_y), (folha_x+6, folha_y), 2)
        txt_folha = self.small_font.render(str(self.counts['folha']), True, BLACK)
        self.screen.blit(txt_folha, (folha_x + 28, folha_y - 14))

        # Aguapé
        aguape_x = base_x + espacamento
        aguape_y = base_y + 16
        pygame.draw.ellipse(self.screen, BLUE, (aguape_x - 18, aguape_y - 12, 36, 24))
        pygame.draw.ellipse(self.screen, (30,90,120), (aguape_x - 18, aguape_y - 12, 36, 24), 2)
        txt_aguape = self.small_font.render(str(self.counts['aguape']), True, BLACK)
        self.screen.blit(txt_aguape, (aguape_x + 28, aguape_y - 14))

        # Manga
        manga_x = base_x + 2 * espacamento
        manga_y = base_y + 16
        pygame.draw.circle(self.screen, ORANGE, (manga_x, manga_y), 14)
        pygame.draw.circle(self.screen, (220,130,30), (manga_x+6, manga_y-6), 6)
        txt_manga = self.small_font.render(str(self.counts['manga']), True, BLACK)
        self.screen.blit(txt_manga, (manga_x + 26, manga_y - 14))

        # Título do placar
        titulo = self.small_font.render("Itens coletados", True, BLACK)
        self.screen.blit(titulo, (x + 10, y - 8))

    def draw_start(self):
        self.screen.fill(SKY)
        self.ground.draw(self.screen)
        title = self.font.render("Capivara Voadora", True, BLACK)
        hint = self.small_font.render("Pressione SPACE ou clique para começar", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//3 + 50)))
        self.capy.y = HEIGHT//2
        self.capy.draw(self.screen)
        self.draw_collectible_counts()

    def draw_game(self):
        self.screen.fill(SKY)
        sun_radius = 90
        sun_pos = (WIDTH - 220, 180)
        pygame.draw.circle(self.screen, YELLOW, sun_pos, sun_radius)
        for angle in range(0, 360, 24):
            ray_x = sun_pos[0] + int(sun_radius * 1.6 * math.cos(math.radians(angle)))
            ray_y = sun_pos[1] + int(sun_radius * 1.6 * math.sin(math.radians(angle)))
            pygame.draw.line(self.screen, YELLOW, sun_pos, (ray_x, ray_y), 4)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self.capy.draw(self.screen)
        self.ground.draw(self.screen)
        score_surf = self.font.render(str(self.score), True, BLACK)
        self.screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 40))
        self.draw_collectible_counts()

    def draw_game_over(self):
        self.draw_game()
        overlay = pygame.Surface((WIDTH - 240, 180), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        self.screen.blit(overlay, (120, HEIGHT//2 - 90))
        go_text = self.font.render("Game Over", True, BLACK)
        score_text = self.small_font.render(f"Score: {self.score}", True, BLACK)
        high = max(self.high_score, self.score)
        high_text = self.small_font.render(f"Highscore: {high}", True, BLACK)
        hint = self.small_font.render("Press SPACE / clique para reiniciar", True, BLACK)
        self.screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 40))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
        self.screen.blit(high_text, (WIDTH//2 - high_text.get_width()//2, HEIGHT//2 + 50))
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 90))
        if self.score > self.high_score:
            self.high_score = self.score

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
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