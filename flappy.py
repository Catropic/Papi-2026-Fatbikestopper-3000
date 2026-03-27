#===========================================================================
#                      simpele flappybird game
#===========================================================================

import pygame
import random
import sys

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Flappy Bird - Fatbike Beloning")

SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()

clock = pygame.time.Clock()

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 180, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)

#=================settings===============
GRAVITY = 0.55
FLAP_STRENGTH = -11
PIPE_SPEED = -4.5
PIPE_GAP = 340
PIPE_WIDTH = 90
PIPE_FREQUENCY = 1350

BIRD_X = SCREEN_WIDTH // 6
BIRD_SIZE = 65

# ======================global variables======================
bird_y = 0
bird_velocity = 0
pipes = []
score = 0
last_pipe_time = 0
game_over = False


# ======================functions======================

def reset_game():
    """restart the entire game"""
    global bird_y, bird_velocity, pipes, score, last_pipe_time, game_over
    bird_y = SCREEN_HEIGHT // 3
    bird_velocity = 0
    pipes = []
    score = 0
    last_pipe_time = pygame.time.get_ticks()
    game_over = False


def draw_bird():
    pygame.draw.rect(screen, YELLOW, (BIRD_X, int(bird_y), BIRD_SIZE, BIRD_SIZE))


def draw_pipes():
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']))
        bottom_y = pipe['top_height'] + PIPE_GAP
        pygame.draw.rect(screen, GREEN, (pipe['x'], bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y))


def check_collision():
    bird_rect = pygame.Rect(BIRD_X, int(bird_y), BIRD_SIZE, BIRD_SIZE)
   
    if bird_y < 0 or bird_y + BIRD_SIZE > SCREEN_HEIGHT:
        return True
   
    for pipe in pipes:
        top_pipe = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top_height'])
        bottom_pipe = pygame.Rect(pipe['x'], pipe['top_height'] + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT)
        if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
            return True
    return False


# ====================== main game ======================
def run_flappy_bird():
    global bird_y, bird_velocity, pipes, score, last_pipe_time, game_over
   
    reset_game()        # start het spel
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        # events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_over:
                    bird_velocity = FLAP_STRENGTH
                else:
                    reset_game()

        # game logic
        if not game_over:
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            # pipe generation
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                top_height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 200)
                pipes.append({'x': SCREEN_WIDTH + 50, 'top_height': top_height})
                last_pipe_time = current_time

            # pipes move
            for pipe in pipes[:]:
                pipe['x'] += PIPE_SPEED
                if pipe['x'] < -PIPE_WIDTH:
                    pipes.remove(pipe)

            # score
            for pipe in pipes:
                if pipe['x'] + PIPE_WIDTH < BIRD_X and not pipe.get('scored', False):
                    score += 1
                    pipe['scored'] = True

            # collision
            if check_collision():
                game_over = True

        # drawing the assets
        screen.fill(BLACK)
        draw_pipes()
        draw_bird()

        # score text
        try:
            font_big = pygame.font.Font("digital_font.ttf", 80)
        except:
            font_big = pygame.font.SysFont("arial", 80)
       
        score_text = font_big.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 180, 40))

        # game Over
        if game_over:
            try:
                font_big = pygame.font.Font("digital_font.ttf", 100)
                font_small = pygame.font.Font("digital_font.ttf", 40)
            except:
                font_big = pygame.font.SysFont("arial", 100)
                font_small = pygame.font.SysFont("arial", 40)

            go_text = font_big.render("GAME OVER", True, RED)
            restart_text = font_small.render("Druk SPATIE om opnieuw te spelen", True, WHITE)
           
            screen.blit(go_text, (SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 - 120))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(60)

    return score

# ====================== start ======================
if __name__ == "__main__":
    final_score = run_flappy_bird()
    print(f"Spel afgelopen! Score: {final_score}")

__all__ = ['run_flappy_bird']
