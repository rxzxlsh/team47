import pygame
import random
import sys

# Initialize pygame
pygame.init()


WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Frozen Split: Biathlon Challenge")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont('Arial', 24)
BIG_FONT = pygame.font.SysFont('Arial', 40)


# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Sounds
COLLISION_SOUND = pygame.mixer.Sound("crunch.wav.mp3")
BOX_SOUND = pygame.mixer.Sound("collect.wav.mp3")
HIT_SOUND = pygame.mixer.Sound("hit.wav.mp3")
MISS_SOUND = pygame.mixer.Sound("miss.wav.mp3")

# --- Skiing Mode Variables ---
player = pygame.Rect(100, 500, 50, 50)
y_velocity = 0
jumping = False
gravity = 0.8
obstacles = [pygame.Rect(random.randint(300, WIDTH), 500, 50, 50) for _ in range(5)]
boxes = [pygame.Rect(random.randint(300, WIDTH), 500, 30, 30) for _ in range(5)]
lives = 3
boxes_collected = 0
speed = 5

# --- Shooting Mode Variables ---
shooting_mode = False
targets = []
score = 0
shooting_lives = 3
fatigue = 0  # will scale with obstacles hit
shoot_timer = 60
last_spawn = 0

# Game state
mode = "skiing"

# --- Skiing Variables ---
player = pygame.Rect(100, 500, 50, 50)
y_velocity = 0
jumping = False
gravity = 0.8
obstacles = [pygame.Rect(random.randint(300, WIDTH), 500, 50, 50) for _ in range(5)]
boxes = [pygame.Rect(random.randint(300, WIDTH), 500, 30, 30) for _ in range(5)]
lives = 3
boxes_collected = 0
speed = 5

# --- Shooting Variables ---
targets = []
score = 0
shooting_lives = 3
fatigue = 0
shoot_timer = 60
last_spawn = 0

def draw_start_screen():
    WIN.fill(WHITE)
    title = BIG_FONT.render("Frozen Split: Biathlon Challenge", True, BLUE)
    start = FONT.render("Press ENTER to Start", True, BLACK)
    instr = FONT.render("Press I for Instructions", True, BLACK)

    WIN.blit(title, (WIDTH//2 - title.get_width()//2, 200))
    WIN.blit(start, (WIDTH//2 - start.get_width()//2, 280))
    WIN.blit(instr, (WIDTH//2 - instr.get_width()//2, 320))
    pygame.display.update()


def draw_instructions():
    WIN.fill(WHITE)
    lines = [
        "INSTRUCTIONS",
        "",
        "SKIING PHASE:",
        "- Press SPACE to jump",
        "- Avoid red obstacles",
        "- Collect 5 yellow boxes",
        "",
        "SHOOTING PHASE:",
        "- Click BLUE targets",
        "- Fatigue increases difficulty",
        "",
        "Press B to go back"
    ]

    for i, line in enumerate(lines):
        text = FONT.render(line, True, BLACK)
        WIN.blit(text, (100, 100 + i * 30))
    pygame.display.update()


def draw_skiing():
    WIN.fill(WHITE)
    pygame.draw.rect(WIN, BLUE, player)
    for obs in obstacles:
        pygame.draw.rect(WIN, RED, obs)
    for box in boxes:
        pygame.draw.rect(WIN, YELLOW, box)
    text = FONT.render(f"Lives: {lives}  Boxes: {boxes_collected}/5", True, BLACK)
    WIN.blit(text, (10, 10))
    pygame.display.update()

def draw_shooting():
    WIN.fill(WHITE)
    # Draw crosshair at mouse
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(WIN, BLACK, (mx, my), 10, 2)
    for t in targets:
        pygame.draw.rect(WIN, BLUE if t['type']=='correct' else RED, t['rect'])
    text = FONT.render(f"Score: {score}  Lives: {shooting_lives}  Time: {shoot_timer}", True, BLACK)
    WIN.blit(text, (10, 10))
    pygame.display.update()

def skiing_update():
    global y_velocity, jumping, lives, boxes_collected, mode, fatigue
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not jumping:
        y_velocity = -15
        jumping = True
    # Apply gravity
    y_velocity += gravity
    player.y += y_velocity
    if player.y >= 500:
        player.y = 500
        jumping = False

    # Move obstacles and boxes left to simulate forward movement
    for obs in obstacles:
        obs.x -= speed
        if obs.right < 0:
            obs.x = random.randint(WIDTH, WIDTH+400)
    for box in boxes:
        box.x -= speed
        if box.right < 0:
            box.x = random.randint(WIDTH, WIDTH+400)

    # Collision detection
    for obs in obstacles:
        if player.colliderect(obs):
            lives -= 1
            fatigue += 1
            COLLISION_SOUND.play()
            obs.x = random.randint(WIDTH, WIDTH+400)

    for box in boxes:
        if player.colliderect(box):
            boxes_collected += 1
            BOX_SOUND.play()
            box.x = random.randint(WIDTH, WIDTH+400)

    # End skiing mode
    if boxes_collected >= 5 or lives <= 0:
        return True
    return False

def shooting_update(dt):
    global targets, score, shooting_lives, shoot_timer, mode
    shoot_timer -= dt / 1000
    # Spawn targets
    global last_spawn
    if pygame.time.get_ticks() - last_spawn > 800:
        t_rect = pygame.Rect(random.randint(50, WIDTH-50), 0, 40, 40)
        t_type = 'correct' if random.random() < 0.7 else 'incorrect'
        targets.append({'rect': t_rect, 'type': t_type})
        last_spawn = pygame.time.get_ticks()

    # Move targets down
    for t in targets:
        t['rect'].y += 3 + fatigue * 0.5  # fatigue makes targets faster

    # Remove off-screen targets
    targets[:] = [t for t in targets if t['rect'].y < HEIGHT]

    # Check mouse clicks
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            hit = False
            for t in targets:
                if t['rect'].collidepoint((mx, my)):
                    if t['type'] == 'correct':
                        score += 10
                        HIT_SOUND.play()
                    else:
                        shooting_lives -= 1
                        MISS_SOUND.play()
                    targets.remove(t)
                    hit = True
                    break
            if not hit:
                shooting_lives -=1
                MISS_SOUND.play()

    # End shooting mode
    if shoot_timer <= 0 or shooting_lives <= 0:
        return True
    return False

def restart_game():
    global mode, lives, boxes_collected, fatigue, score, shooting_lives, shoot_timer, targets
    lives = 3
    boxes_collected = 0
    fatigue = 0
    score = 0
    shooting_lives = 3
    shoot_timer = 60
    targets = []
    mode = "start"

def main():
    global mode, fatigue
    running = True
    dt = 0
    while running:
        CLOCK.tick(60)
        dt = CLOCK.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if mode == "skiing":
            end = skiing_update()
            draw_skiing()
            if end:
                mode = "shooting"
        elif mode == "shooting":
            end = shooting_update(dt)
            draw_shooting()
            if end:
                running = False
    pygame.quit()
    print(f"Run Over! Fatigue: {fatigue}  Score: {score}")

if __name__ == "__main__":
    main()
