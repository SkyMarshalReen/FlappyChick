import math
import random
from pathlib import Path

import pygame


pygame.init()
pygame.mixer.init()

WIDTH = 480
HEIGHT = 640
GROUND_HEIGHT = 90
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

FONT_BIG = pygame.font.Font(None, 64)
FONT_MEDIUM = pygame.font.Font(None, 40)
FONT_SMALL = pygame.font.Font(None, 28)

HIGH_SCORE_FILE = Path("highscore.txt")
SOUND_DIR = Path("sounds")

SKY = (135, 206, 235)
CLOUD = (245, 245, 245)
PIPE_GREEN = (45, 180, 55)
PIPE_DARK = (25, 120, 35)
GROUND = (222, 196, 120)
GROUND_GRASS = (120, 190, 70)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)

BIRD_X = 110
BIRD_START_Y = 290

GRAVITY = 0.45
JUMP_STRENGTH = -8.5

PIPE_WIDTH = 72
PIPE_GAP = 175
PIPE_DISTANCE = 230
START_PIPE_SPEED = 3.5
MAX_PIPE_SPEED = 6.5


def load_high_score():
    if not HIGH_SCORE_FILE.exists():
        return 0

    try:
        return int(HIGH_SCORE_FILE.read_text().strip())
    except ValueError:
        return 0


def save_high_score(value):
    HIGH_SCORE_FILE.write_text(str(value))


def load_sound(filename):
    path = SOUND_DIR / filename

    if not path.exists():
        return None

    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None


jump_sound = load_sound("jump.wav")
score_sound = load_sound("score.wav")
hit_sound = load_sound("hit.wav")


def play_sound(sound):
    if sound is not None:
        sound.play()


def create_pipe(x):
    top_height = random.randint(90, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 90)

    return {
        "x": float(x),
        "top_height": top_height,
        "scored": False,
    }


def reset_game():
    pipes = [
        create_pipe(WIDTH + 100),
        create_pipe(WIDTH + 100 + PIPE_DISTANCE),
        create_pipe(WIDTH + 100 + PIPE_DISTANCE * 2),
    ]

    return {
        "bird_y": float(BIRD_START_Y),
        "bird_velocity": 0.0,
        "pipes": pipes,
        "score": 0,
        "game_over": False,
    }


def draw_cloud(x, y, scale=1.0):
    radius = int(18 * scale)

    pygame.draw.circle(screen, CLOUD, (int(x), int(y)), radius)
    pygame.draw.circle(
        screen,
        CLOUD,
        (int(x + 18 * scale), int(y - 8 * scale)),
        int(radius * 1.15),
    )
    pygame.draw.circle(
        screen,
        CLOUD,
        (int(x + 38 * scale), int(y)),
        radius,
    )

    pygame.draw.rect(
        screen,
        CLOUD,
        (
            int(x),
            int(y),
            int(38 * scale),
            int(18 * scale),
        ),
    )


def draw_background(ticks):
    screen.fill(SKY)

    cloud_offset = (ticks * 0.015) % (WIDTH + 150)

    draw_cloud(WIDTH - cloud_offset, 110, 1.1)
    draw_cloud((WIDTH + 210 - cloud_offset * 0.65) % (WIDTH + 220) - 70, 210, 0.8)

    pygame.draw.rect(
        screen,
        GROUND_GRASS,
        (0, HEIGHT - GROUND_HEIGHT, WIDTH, 18),
    )

    pygame.draw.rect(
        screen,
        GROUND,
        (0, HEIGHT - GROUND_HEIGHT + 18, WIDTH, GROUND_HEIGHT - 18),
    )


def draw_pipe(pipe):
    x = int(pipe["x"])
    top_height = pipe["top_height"]
    bottom_y = top_height + PIPE_GAP

    top_rect = pygame.Rect(
        x,
        0,
        PIPE_WIDTH,
        top_height,
    )

    bottom_rect = pygame.Rect(
        x,
        bottom_y,
        PIPE_WIDTH,
        HEIGHT - GROUND_HEIGHT - bottom_y,
    )

    pygame.draw.rect(screen, PIPE_GREEN, top_rect)
    pygame.draw.rect(screen, PIPE_GREEN, bottom_rect)

    pygame.draw.rect(
        screen,
        PIPE_DARK,
        (x + PIPE_WIDTH - 10, 0, 10, top_height),
    )

    pygame.draw.rect(
        screen,
        PIPE_DARK,
        (
            x + PIPE_WIDTH - 10,
            bottom_y,
            10,
            HEIGHT - GROUND_HEIGHT - bottom_y,
        ),
    )

    cap_height = 28
    cap_overhang = 6

    pygame.draw.rect(
        screen,
        PIPE_GREEN,
        (
            x - cap_overhang,
            top_height - cap_height,
            PIPE_WIDTH + cap_overhang * 2,
            cap_height,
        ),
    )

    pygame.draw.rect(
        screen,
        PIPE_GREEN,
        (
            x - cap_overhang,
            bottom_y,
            PIPE_WIDTH + cap_overhang * 2,
            cap_height,
        ),
    )

    pygame.draw.rect(
        screen,
        PIPE_DARK,
        (
            x + PIPE_WIDTH - 10 + cap_overhang,
            top_height - cap_height,
            10,
            cap_height,
        ),
    )

    pygame.draw.rect(
        screen,
        PIPE_DARK,
        (
            x + PIPE_WIDTH - 10 + cap_overhang,
            bottom_y,
            10,
            cap_height,
        ),
    )

    return top_rect, bottom_rect


def create_bird_surface(wing_offset):
    surface = pygame.Surface((80, 70), pygame.SRCALPHA)

    pygame.draw.circle(
        surface,
        (255, 220, 0),
        (34, 35),
        21,
    )

    pygame.draw.ellipse(
        surface,
        (240, 185, 0),
        (16, 31 + wing_offset, 24, 17),
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (43, 27),
        6,
    )

    pygame.draw.circle(
        surface,
        BLACK,
        (45, 27),
        2,
    )

    pygame.draw.polygon(
        surface,
        (255, 145, 0),
        [
            (52, 34),
            (70, 29),
            (70, 39),
        ],
    )

    return surface


def draw_bird(y, velocity, ticks):
    wing_offset = int(math.sin(ticks * 0.02) * 3)

    bird_surface = create_bird_surface(wing_offset)

    angle = max(-65, min(30, -velocity * 3.2))

    rotated = pygame.transform.rotate(
        bird_surface,
        angle,
    )

    rect = rotated.get_rect(
        center=(BIRD_X, int(y))
    )

    screen.blit(rotated, rect)

    hitbox = pygame.Rect(
        BIRD_X - 16,
        int(y) - 15,
        32,
        30,
    )

    return hitbox


def draw_score(score, high_score):
    score_surface = FONT_MEDIUM.render(
        f"Score: {score}",
        True,
        BLACK,
    )

    high_surface = FONT_SMALL.render(
        f"High: {high_score}",
        True,
        BLACK,
    )

    screen.blit(score_surface, (18, 18))
    screen.blit(high_surface, (20, 58))


def draw_start_screen():
    title = FONT_BIG.render(
        "Flappy Bird",
        True,
        BLACK,
    )

    subtitle = FONT_SMALL.render(
        "SPACE to start",
        True,
        BLACK,
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 240)),
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(center=(WIDTH // 2, 305)),
    )


def draw_game_over(score, high_score):
    title = FONT_BIG.render(
        "Game Over",
        True,
        BLACK,
    )

    score_text = FONT_MEDIUM.render(
        f"Score: {score}",
        True,
        BLACK,
    )

    high_text = FONT_SMALL.render(
        f"High score: {high_score}",
        True,
        BLACK,
    )

    restart = FONT_SMALL.render(
        "SPACE to restart",
        True,
        BLACK,
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 230)),
    )

    screen.blit(
        score_text,
        score_text.get_rect(center=(WIDTH // 2, 295)),
    )

    screen.blit(
        high_text,
        high_text.get_rect(center=(WIDTH // 2, 335)),
    )

    screen.blit(
        restart,
        restart.get_rect(center=(WIDTH // 2, 390)),
    )


high_score = load_high_score()
game = reset_game()

started = False
running = True

while running:
    ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                if not started:
                    started = True
                    game["bird_velocity"] = JUMP_STRENGTH
                    play_sound(jump_sound)

                elif game["game_over"]:
                    game = reset_game()
                    game["bird_velocity"] = JUMP_STRENGTH
                    play_sound(jump_sound)

                else:
                    game["bird_velocity"] = JUMP_STRENGTH
                    play_sound(jump_sound)

    if started and not game["game_over"]:
        game["bird_velocity"] += GRAVITY
        game["bird_y"] += game["bird_velocity"]

        pipe_speed = min(
            MAX_PIPE_SPEED,
            START_PIPE_SPEED + game["score"] * 0.12,
        )

        for pipe in game["pipes"]:
            pipe["x"] -= pipe_speed

            if (
                not pipe["scored"]
                and pipe["x"] + PIPE_WIDTH < BIRD_X
            ):
                pipe["scored"] = True
                game["score"] += 1

                play_sound(score_sound)

                if game["score"] > high_score:
                    high_score = game["score"]
                    save_high_score(high_score)

        leftmost_pipe = min(
            game["pipes"],
            key=lambda pipe: pipe["x"],
        )

        if leftmost_pipe["x"] < -PIPE_WIDTH - 20:
            rightmost_x = max(
                pipe["x"] for pipe in game["pipes"]
            )

            leftmost_pipe["x"] = rightmost_x + PIPE_DISTANCE
            leftmost_pipe["top_height"] = random.randint(
                90,
                HEIGHT - GROUND_HEIGHT - PIPE_GAP - 90,
            )
            leftmost_pipe["scored"] = False

    draw_background(ticks)

    pipe_rects = []

    for pipe in game["pipes"]:
        pipe_rects.extend(draw_pipe(pipe))

    bird_rect = draw_bird(
        game["bird_y"],
        game["bird_velocity"],
        ticks,
    )

    if started and not game["game_over"]:
        collided = any(
            bird_rect.colliderect(pipe_rect)
            for pipe_rect in pipe_rects
        )

        hit_ceiling = bird_rect.top <= 0
        hit_ground = bird_rect.bottom >= HEIGHT - GROUND_HEIGHT

        if collided or hit_ceiling or hit_ground:
            game["game_over"] = True
            play_sound(hit_sound)

    draw_score(
        game["score"],
        high_score,
    )

    if not started:
        draw_start_screen()

    elif game["game_over"]:
        draw_game_over(
            game["score"],
            high_score,
        )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
