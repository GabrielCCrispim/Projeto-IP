import pygame
import random
import math
import sys
import os


from Config import *
from Class.Button import Button
from Class.Ground import Ground
from Class.Cloud import Cloud
from Class.Capivara import Capivara
from Class.Pipe import Pipe
from Class.Mountain import Mountain
from Class.Particle import Particle
from Class.FloatingText import FloatingText
from Class.Bird import Bird

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappybara")
        self.entering_name = False
        self.player_name = ""
        self.saved_this_session = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 60)
        self.btn_exit_start = Button(WIDTH - 140, 20, 120, 50, "SAIR", self.font, BUTTON_COLOR, BUTTON_HOVER)
        self.btn_exit_over = Button(WIDTH // 2 - 70, HEIGHT // 2 + 150, 140, 50, "SAIR", self.font, BUTTON_COLOR, BUTTON_HOVER)
        self.top_scores = self.load_scores()
        self.reset()

    def load_scores(self):
        if not os.path.exists(SCORE_FILE):
            return []

        scores = []
        try:
            with open(SCORE_FILE, "r") as f:
                for line in f:
                    if "," in line:
                        user, score = line.strip().split(",")
                        scores.append({"user": user, "score": int(score)})
        except:
            pass
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

    def save_score(self, user, score):
        self.top_scores.append({"user": user, "score": score})
        self.top_scores = sorted(self.top_scores, key=lambda x: x["score"], reverse=True)[:10]

        try:
            with open(SCORE_FILE, "w") as f:
                for s in self.top_scores:
                    f.write(f"{s['user']},{s['score']}\n")
        except:
            pass

    def is_new_record(self, score):
        if len(self.top_scores) < 10:
            return True
        return score > self.top_scores[-1]["score"]

    def draw_blur_background(self):
        small = pygame.transform.smoothscale(self.screen, (WIDTH // 10, HEIGHT // 10))
        blur = pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
        self.screen.blit(blur, (0, 0))

    def draw_name_input(self):
        self.draw_game()
        self.draw_blur_background() 

        panel = pygame.Surface((500, 260), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 230))
        rect = panel.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(panel, rect)

        title = self.big_font.render("PARABÉNS!", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        score_txt = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_txt, score_txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))

        prompt = self.small_font.render("Digite seu User Cin:", True, GREY_TEXT)
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2)))

        name_box = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 20, 240, 40)
        pygame.draw.rect(self.screen, WHITE, name_box, border_radius=6)
        pygame.draw.rect(self.screen, BLACK, name_box, 2, border_radius=6)

        name_txt = self.font.render(self.player_name.upper(), True, BLACK)
        self.screen.blit(name_txt, name_txt.get_rect(center=name_box.center))

        hint = self.small_font.render("ENTER para confirmar", True, GREY_TEXT)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))


    def interpolate_color(self, start_color, end_color, factor):
        return (
            int(start_color[0] + (end_color[0] - start_color[0]) * factor),
            int(start_color[1] + (end_color[1] - start_color[1]) * factor),
            int(start_color[2] + (end_color[2] - start_color[2]) * factor),
        )

    def get_sky_color(self):
        if self.time < 30:
            factor = self.time / 30.0
            return self.interpolate_color(SKY_DAY, SKY_SUNSET, factor)
        elif self.time < 60:
            factor = (self.time - 30) / 30.0
            return self.interpolate_color(SKY_SUNSET, SKY_NIGHT, factor)
        else: return SKY_NIGHT

    def reset(self):
        self.capy = Capivara()
        self.ground = Ground()
        self.pipes = []
        self.particles = []
        self.floating_texts = [] 
        self.clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
        self.birds = [Bird() for _ in range(3)]
        self.entering_name = False
        self.player_name = ""
        self.saved_this_session = False
        
        # Gera Montanhas Iniciais (Fundo e Frente)
        self.mountains_far = []
        self.mountains_near = []
        
        # Preencher o fundo inicialmente
        current_x = -200
        while current_x < WIDTH + 200:
            m = Mountain(current_x, 'far')
            self.mountains_far.append(m)
            current_x += m.width - random.randint(50, 100) # Sobreposição
            
        current_x = -200
        while current_x < WIDTH + 200:
            m = Mountain(current_x, 'near')
            self.mountains_near.append(m)
            current_x += m.width - random.randint(30, 80) # Sobreposição
        
        self.score = 0
        self.counts = {"folha": 0, "aguape": 0, "manga": 0}
        self.game_over = False
        self.started = False
        self.saved_this_session = False
        self.time = 0.0
        self.shake_duration = 0 
        self.level_up_flash = 0 
        self.base_speed = 300
        self.current_speed = INITIAL_SPEED
        self.multiplier = 1
        first_pipe = Pipe(WIDTH + 50, PIPE_GAP_DEFAULT, self.multiplier)
        self.pipes.append(first_pipe)
        # relogio
        self.slow_timer = 0.0
        self.slow_duration = 10.0  # segundos
        self.slow_factor = 2/3     # 2/3 da velocidade normal
        # escudo
        self.shield_timer = 0.0
        self.shield_duration = 25.0

    def spawn_pipe(self):
        gap = max(160, PIPE_GAP_DEFAULT - (self.multiplier * 5))
        new_pipe = Pipe(WIDTH + 50, gap, self.multiplier)
        self.pipes.append(new_pipe)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        if not self.started:
            self.btn_exit_start.check_hover(mouse_pos)
        if self.game_over:
            self.btn_exit_over.check_hover(mouse_pos)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --------- INPUT DE NOME (TEM PRIORIDADE) ---------
            if self.entering_name:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN and self.player_name:
                        self.save_score(self.player_name.upper(), self.score)
                        self.saved_this_session = True
                        self.entering_name = False

                    elif e.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]

                    elif len(self.player_name) < 8:
                        if e.unicode.isalnum():
                            self.player_name += e.unicode
                continue  # ⬅️ MUITO IMPORTANTE: bloqueia resto do input

            # --------- BOTÕES ---------
            if not self.started and self.btn_exit_start.is_clicked(e):
                pygame.quit()
                sys.exit()

            if self.game_over and self.btn_exit_over.is_clicked(e):
                pygame.quit()   
                sys.exit()

            # --------- TECLADO ---------
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_UP):
                    if not self.started:
                        self.started = True
                        self.capy.jump()
                    elif self.game_over and not self.entering_name:
                        self.reset()
                    else:
                        self.capy.jump()
                        for _ in range(4):
                            self.particles.append(Particle(self.capy.x, self.capy.y + 10))

                elif e.key == pygame.K_r and self.game_over:
                    self.reset()

                elif e.key in (pygame.K_DOWN, pygame.K_s) and self.started and not self.game_over:
                    self.capy.dive()

            # --------- MOUSE ---------
            elif e.type == pygame.MOUSEBUTTONDOWN:
                clicked_ui = False
                if not self.started and self.btn_exit_start.rect.collidepoint(e.pos):
                    clicked_ui = True
                if self.game_over and self.btn_exit_over.rect.collidepoint(e.pos):
                    clicked_ui = True

                if not clicked_ui:
                    if not self.started:
                        self.started = True
                        self.capy.jump()
                    elif self.game_over:
                        self.reset()
                    else:
                        self.capy.jump()


        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not self.started and self.btn_exit_start.is_clicked(e):
                pygame.quit()
                sys.exit()
            if self.game_over and self.btn_exit_over.is_clicked(e):
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE or e.key == pygame.K_UP:
                    if not self.started:
                        self.started = True
                        self.capy.jump()
                    elif self.game_over: self.reset()
                    else:
                        self.capy.jump()
                        for _ in range(4): self.particles.append(Particle(self.capy.x, self.capy.y+10))
                elif e.key == pygame.K_r and self.game_over: self.reset()
                elif (e.key == pygame.K_DOWN or e.key == pygame.K_s) and self.started and not self.game_over:
                    self.capy.dive()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                clicked_ui = False
                if not self.started and self.btn_exit_start.rect.collidepoint(e.pos): 
                    clicked_ui = True
                if self.game_over and self.btn_exit_over.rect.collidepoint(e.pos): clicked_ui = True
                if not clicked_ui:
                    if not self.started:
                        self.started = True
                        self.capy.jump()
                    elif self.game_over: self.reset()
                    else: self.capy.jump()

    def update(self, dt):
        # Atualiza Fundo (Montanhas, Nuvens, Pássaros)
        
        # Montanhas (Longe)
        for m in self.mountains_far: m.update(dt, self.current_speed)
        # Remove se saiu da tela e adiciona nova no fim
        if self.mountains_far[0].x + self.mountains_far[0].width < -100:
            removed = self.mountains_far.pop(0)
            # Adiciona nova
            last_x = self.mountains_far[-1].x + self.mountains_far[-1].width
            new_m = Mountain(last_x - random.randint(50, 100), 'far')
            self.mountains_far.append(new_m)

        # Montanhas (Perto)
        for m in self.mountains_near: m.update(dt, self.current_speed)
        if self.mountains_near[0].x + self.mountains_near[0].width < -100:
            removed = self.mountains_near.pop(0)
            last_x = self.mountains_near[-1].x + self.mountains_near[-1].width
            new_m = Mountain(last_x - random.randint(30, 80), 'near')
            self.mountains_near.append(new_m)

        for c in self.clouds:
            c.update(dt)
            if c.x + c.width < 0:
                self.clouds.remove(c)
                self.clouds.append(Cloud())
        for b in self.birds:
            b.update(dt)
            if b.x < -100 or b.x > WIDTH + 100: self.birds.remove(b)
        if random.random() < 0.005 and len(self.birds) < 5: self.birds.append(Bird())

        if not self.started:
            self.ground.update(dt, self.current_speed)
            self.capy.y = HEIGHT//2 + math.sin(pygame.time.get_ticks() * 0.003) * 20
            return

        if (self.game_over and not self.saved_this_session and not self.entering_name and self.is_new_record(self.score)):
            self.entering_name = True
        if self.game_over:
            if self.shake_duration > 0:
                self.shake_duration -= 1
            return


        self.time += dt
        # efeito relogio
        speed_multiplier = 1.0
        if self.slow_timer > 0:
            self.slow_timer -= dt
            speed_multiplier = self.slow_factor
            if self.slow_timer < 0:
                self.slow_timer = 0
        # efeito escudo
        if self.shield_timer > 0:
            self.shield_timer -= dt
            # quando o tempo acabar, desativa o escudo
            if self.shield_timer <= 0:
                self.shield_timer = 0
                self.capy.has_shield = False
        if self.shake_duration > 0: self.shake_duration -= 1
        if self.level_up_flash > 0: self.level_up_flash -= 5
        if self.current_speed < MAX_SPEED: self.current_speed += 4 * dt
        new_multiplier = 1 + int(self.time // 10)
        if new_multiplier > self.multiplier:
            self.multiplier = new_multiplier
            self.level_up_flash = 255 
        
        self.capy.update(dt)
        self.ground.update(dt, self.current_speed)
        if random.random() < 0.3: self.particles.append(Particle(self.capy.x - 10, self.capy.y))
        for p in list(self.particles):
            p.update(dt)
            if p.life <= 0: self.particles.remove(p)
        for ft in list(self.floating_texts):
            ft.update()
            if ft.timer >= ft.max_time: self.floating_texts.remove(ft)

        if self.pipes:
            last_pipe = self.pipes[-1]
            dist = max(350, SPAWN_DISTANCE_START - (self.time * 3))
            if last_pipe.x < WIDTH - dist: self.spawn_pipe()

        for Pipe in list(self.pipes):
            effective_speed = self.current_speed * speed_multiplier
            if effective_speed > INITIAL_SPEED:
                effective_speed = INITIAL_SPEED
            Pipe.update(dt, effective_speed)
            if Pipe.collides_with(self.capy.get_rect()):
                if self.capy.immunity_timer <= 0:
                    if self.capy.has_shield:
                        self.capy.has_shield = False
                        self.capy.immunity_timer = 2.0
                        self.capy.y -= 10
                        self.shake_duration = 10 
                        for _ in range(10): self.particles.append(Particle(self.capy.x, self.capy.y, SHIELD_COLOR, True))
                    else:
                        self.game_over = True
                        self.capy.alive = False
            for p in Pipe.powerups:
                if not p.collected and p.rect.colliderect(self.capy.get_rect()):
                    p.collected = True
                    if p.type == "shield":
                        self.capy.has_shield = True
                        self.shield_timer = self.shield_duration # reinicia o tempo
                        self.floating_texts.append(FloatingText(self.capy.x, self.capy.y - 40, "ESCUDO!", SHIELD_COLOR))
                    elif p.type == "clock":
                        self.slow_timer = self.slow_duration
                        self.floating_texts.append(FloatingText(self.capy.x, self.capy.y - 40, "TEMPO LENTO!", CLOCK_COLOR))
            for c in Pipe.collectibles:
                if not c.collected and c.rect.colliderect(self.capy.get_rect()):
                    c.collected = True
                    points = c.base_value * self.multiplier
                    self.score += points
                    self.counts[c.type] += 1
                    color = WHITE
                    if c.type == "manga": 
                        color = GOLD_TEXT
                        moeda3.play()
                        for _ in range(15):
                            col = random.choice([RED_UI, YELLOW, ORANGE, WHITE])
                            self.particles.append(Particle(c.x, c.y, col, True))
                    elif c.type == "aguape": 
                        color = BLUE
                        moeda2.play()  
                    elif c.type == "folha": 
                        color = GREEN
                        moeda1.play()
                    self.floating_texts.append(FloatingText(self.capy.x, self.capy.y - 30, f"+{points}", color))
            if Pipe.off_screen(): self.pipes.remove(Pipe)

        if self.capy.y + self.capy.radius >= HEIGHT - GROUND_HEIGHT:
            game_over.play()
            self.capy.y = HEIGHT - GROUND_HEIGHT - self.capy.radius
            self.game_over = True
            self.capy.alive = False
            self.shake_duration = 20
        if (self.game_over and not self.saved_this_session and not self.entering_name and self.is_new_record(self.score)):
            victory.play()
            self.entering_name = True

    def draw_hud_ingame(self):
        hud_bg = pygame.Surface((200, 150), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, (255, 255, 255, 180), hud_bg.get_rect(), border_radius=10)
        self.screen.blit(hud_bg, (10, 10))
        score_surf = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_surf, (20, 20))
        mult_text = f"BONUS x{self.multiplier}"
        color = RED_UI if self.multiplier > 1 else (60, 60, 60)
        mult_surf = self.font.render(mult_text, True, color)
        self.screen.blit(mult_surf, (WIDTH - mult_surf.get_width() - 20, 20))
        spd_text = self.small_font.render(f"Velocidade: {int(self.current_speed)}", True, GREY_TEXT)
        self.screen.blit(spd_text, (WIDTH - spd_text.get_width() - 20, 55))
        panel_x = 20
        panel_y = 60
        pygame.draw.circle(self.screen, GREEN, (panel_x + 10, panel_y + 10), 10)
        txt_f = self.small_font.render(f"x {self.counts['folha']}", True, BLACK)
        self.screen.blit(txt_f, (panel_x + 30, panel_y + 2))
        pygame.draw.circle(self.screen, BLUE, (panel_x + 10, panel_y + 40), 10)
        txt_a = self.small_font.render(f"x {self.counts['aguape']}", True, BLACK)
        self.screen.blit(txt_a, (panel_x + 30, panel_y + 32))
        pygame.draw.circle(self.screen, ORANGE, (panel_x + 10, panel_y + 70), 10)
        txt_m = self.small_font.render(f"x {self.counts['manga']}", True, BLACK)
        self.screen.blit(txt_m, (panel_x + 30, panel_y + 62))
        # hud relogio
        if self.slow_timer > 0:
            txt = self.small_font.render(
                f"TEMPO LENTO: {int(self.slow_timer)}s",
                True,
                (70, 20, 130)
            )
            self.screen.blit(txt, (20, 170))
        # hud escudo
        if self.shield_timer > 0:
            txt = self.small_font.render(
                f"ESCUDO: {int(self.shield_timer)}s",
                True,
                SHIELD_COLOR
            )
            self.screen.blit(txt, (20, 195))


    def draw_start(self):
        self.screen.fill(SKY_DAY)
        # Desenha Fundo
        for m in self.mountains_far: m.draw(self.screen)
        for m in self.mountains_near: m.draw(self.screen)
        for c in self.clouds: c.draw(self.screen)
        for b in self.birds: b.draw(self.screen)
        self.ground.draw(self.screen)
        self.capy.draw(self.screen)
        
        title = self.big_font.render("Flappybara", True, BLACK)
        title_shadow = self.big_font.render("Flappybara", True, (200, 200, 200))
        center_x = WIDTH//2
        title_rect = title.get_rect(center=(center_x, HEIGHT//3))
        self.screen.blit(title_shadow, (title_rect.x+2, title_rect.y+2))
        self.screen.blit(title, title_rect)
        hint = self.font.render("Pressione SPACE", True, (50,50,50))
        self.screen.blit(hint, hint.get_rect(center=(center_x, HEIGHT//3 + 60)))
        hint2 = self.small_font.render("Seta BAIXO = Mergulhar", True, RED_UI)
        self.screen.blit(hint2, hint2.get_rect(center=(center_x, HEIGHT//3 + 90)))
        board_y = HEIGHT//2 + 50
        header = self.small_font.render("- TOP RECORDES -", True, BLACK)
        self.screen.blit(header, header.get_rect(center=(center_x, board_y - 30)))
        if not self.top_scores:
            txt = self.small_font.render("Sem recordes ainda...", True, GREY_TEXT)
            self.screen.blit(txt, txt.get_rect(center=(center_x, board_y)))
        else:
            left_x = center_x - 260
            right_x = center_x + 40
            start_y = board_y

            for i, entry in enumerate(self.top_scores):
                col_x = left_x if i < 5 else right_x
                y = start_y + (i % 5) * 26
                if i == 0:
                    color = GOLD_TEXT
                elif i == 1:
                    color = SILVER_TEXT
                elif i == 2:
                    color = BRONZE_TEXT
                else:
                    color = BLACK

                txt = self.small_font.render(
                    f"{i+1:>2}. {entry['user']:<8} {entry['score']}",
                    True,
                    color
                )
                self.screen.blit(txt, (col_x, y))



    def draw_game(self):
        self.screen.fill(self.get_sky_color())
        
        shake_x = 0
        shake_y = 0
        if self.shake_duration > 0:
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-4, 4)
        
        if self.time < 50:
            sun_y = 100 + int(self.time * 5)
            s = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 200, 50), (100, 100), 80)
            self.screen.blit(s, (WIDTH - 250 + shake_x, sun_y - 100 + shake_y))
            pygame.draw.circle(self.screen, YELLOW, (WIDTH - 150 + shake_x, sun_y + shake_y), 50)
        else:
            random.seed(int(self.time))
            for _ in range(20):
                pygame.draw.circle(self.screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT//2)), 2)
            random.seed()
            pygame.draw.circle(self.screen, (240, 240, 255), (WIDTH - 150, 100), 40)

        # Ordem de Desenho do Fundo
        for m in self.mountains_far: m.draw(self.screen)
        for m in self.mountains_near: m.draw(self.screen)
        for c in self.clouds: c.draw(self.screen)
        for b in self.birds: b.draw(self.screen)
        
        for Pipe in self.pipes: Pipe.draw(self.screen)
        for p in self.particles: p.draw(self.screen)
        for ft in self.floating_texts: ft.draw(self.screen)
        self.capy.draw(self.screen)
        self.ground.draw(self.screen)
        self.draw_hud_ingame()
        
        if self.level_up_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(self.level_up_flash)
            self.screen.blit(flash_surf, (0, 0))

    def draw_game_over(self):
        self.draw_game()
        overlay = pygame.Surface((WIDTH - 40, 360), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        panel_rect = overlay.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(overlay, panel_rect)
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        go_text = self.big_font.render("GAME OVER", True, BLACK)
        score_text = self.font.render(f"Score Final: {self.score}", True, BLACK)
        self.screen.blit(go_text, go_text.get_rect(center=(center_x, center_y - 120)))
        self.screen.blit(score_text, score_text.get_rect(center=(center_x, center_y - 60)))
        stats_y = center_y + 40
        gap_x = 120
        pygame.draw.circle(self.screen, GREEN, (center_x - gap_x, stats_y), 25)
        t1 = self.font.render(f"{self.counts['folha']}", True, BLACK)
        self.screen.blit(t1, t1.get_rect(center=(center_x - gap_x, stats_y + 40)))
        pygame.draw.circle(self.screen, BLUE, (center_x, stats_y), 25)
        t2 = self.font.render(f"{self.counts['aguape']}", True, BLACK)
        self.screen.blit(t2, t2.get_rect(center=(center_x, stats_y + 40)))
        pygame.draw.circle(self.screen, ORANGE, (center_x + gap_x, stats_y), 25)
        t3 = self.font.render(f"{self.counts['manga']}", True, BLACK)
        self.screen.blit(t3, t3.get_rect(center=(center_x + gap_x, stats_y + 40)))
        hint = self.small_font.render("Espaço para Reiniciar", True, (80,80,80))
        self.screen.blit(hint, hint.get_rect(center=(center_x, center_y + 110)))
        self.btn_exit_over.draw(self.screen)

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            self.handle_events()
            self.update(dt)
            if not self.started:
                self.draw_start()
            elif self.game_over and self.entering_name:
                self.draw_name_input()
            elif self.game_over:
                self.draw_game_over()
            else:
                self.draw_game()    
            pygame.display.flip()