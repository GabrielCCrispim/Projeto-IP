import pygame

# Configurações Gerais
WIDTH, HEIGHT = 1280, 720
FPS = 60
SCORE_FILE = "scores.txt"

# Cores
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (80, 200, 120)
GREEN_PIPE = (80, 200, 120)
GREEN_DARK = (30, 100, 30)
GREEN_LIGHT = (120, 230, 150)
BROWN = (120, 85, 60)
BROWN_DARK = (80, 50, 30)
YELLOW = (255, 210, 50)
BLUE = (70, 150, 200)
ORANGE = (255, 160, 40)
RED_UI = (220, 50, 50)

#Cores de Objetos Especificos
BUTTON_COLOR = (200, 60, 60)
BUTTON_HOVER = (230, 90, 90)
SHIELD_COLOR = (0, 255, 255)
CLOCK_COLOR = (70, 20, 130)
GREY_TEXT = (100, 100, 100)
GOLD_TEXT = (255, 215, 0)
SILVER_TEXT = (160, 160, 160)
BRONZE_TEXT = (205, 127, 50)
BIRD_COLOR = (50, 50, 65)
SKY_DAY = (120, 200, 255)
SKY_SUNSET = (255, 120, 80)
SKY_NIGHT = (10, 10, 35)
MOUNTAIN_FAR = (160, 180, 210)  # Azul claro acinzentado (pra de longe)
MOUNTAIN_NEAR = (110, 125, 155) # Azul mais escuro (pra de perto)
CLOUD_MAIN_COLOR = (240, 248, 255) 
CLOUD_SHADOW_COLOR = (200, 220, 240)

# Padrões de Nuvem
CLOUD_PATTERNS = [
    ["  WW   ", " WWWW  ", "BBBBBB ", "BBBBBB "],
    ["   WW    ", "  WWWW   ", " BBBBBB  ", "BBBBBBBB ", " BBBBBB  "],
    [" W   W ", "WWW WWW", "BBBBBBB", " BBBBB "]
]

# Configurações de Jogo
CAPY_X = 180
CAPY_RADIUS = 24 
PIPE_WIDTH = 80
GROUND_HEIGHT = 100

# Física
GRAVITY = 1500.0
JUMP_VELOCITY = -420.0
DIVE_VELOCITY = 700.0
MAX_DROP_SPEED = 1000.0

# Dificuldade
PIPE_GAP_DEFAULT = 220
SPAWN_DISTANCE_START = 500
INITIAL_SPEED = 300
MAX_SPEED = 900.0

# Valores Base de Pontuação
VALOR_FOLHA = 5
VALOR_AGUAPE = 50
VALOR_MANGA = 500

# Música principal
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('Soundtrack/fight_looped.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Outros sons
moeda1 = pygame.mixer.Sound('Soundtrack/Coin01.mp3')
moeda2 = pygame.mixer.Sound('Soundtrack/Coin02.mp3')
moeda3 = pygame.mixer.Sound('Soundtrack/Coin03.mp3')
moeda1.play()
shield = pygame.mixer.Sound('Soundtrack/shield.mp3')
clock = pygame.mixer.Sound('Soundtrack/Clock.mp3')
colidiu = pygame.mixer.Sound('Soundtrack/colidiu.mp3')
victory = pygame.mixer.Sound('Soundtrack/Victory.mp3')
game_over = pygame.mixer.Sound('Soundtrack/Game over.mp3')