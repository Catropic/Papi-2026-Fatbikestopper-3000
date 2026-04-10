import pygame
import sys
from gpiozero import LED
from gpiozero import PWMOutputDevice
from gpiozero import DigitalInputDevice
from time import sleep
import RPi.GPIO as GPIO
import time

# ================== GPIO setup ==================
try:
    GPIO.setmode(GPIO.BOARD)
#     GPIO.setwarnings(False)     
   
    PIN_GAME = 24
    PIN_ESC = 35                                                                                                                                                                                                                                                                                                           
                                             
    GPIO.setup(38, GPIO.OUT)
    servo=GPIO.PWM(38, 50)
#     buzzer = PWMOutputDevice(16)
    sensor = DigitalInputDevice(12)
    
    GPIO.setup(PIN_GAME, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_ESC, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(f"GPIO knoppen succesvol ingesteld (Pin {PIN_GAME} en {PIN_ESC})")
    gpio_available = True
except ImportError:
    print("GPIO niet beschikbaar (normaal op laptop). We gebruiken muis/toetsenbord.")
    gpio_available = False

pygame.init()
screen = pygame.display.set_mode((800,480))
pygame.display.set_caption("fatbike interface")

clock = pygame.time.Clock()

font_speed = pygame.font.Font("digital_font.ttf", 80)
font_small = pygame.font.Font("digital_font.ttf", 40)

SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()

# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 480

# ================== variables ==================
game_state = "menu"
playtime_credits = 0.0
MIN_CREDITS_TO_PLAY = 60
CREDITS_PER_GAME = 60

HIGHSCORE_FILE = "highscore.txt"
warning_start = None

grootteWiel = 100.5
start = time.perf_counter()
eindeMeting=0
counter=0
metingen=[]
kmMax=25
totaal=0
laatsteLoop=0

# ================== speed test ==================
speed_value = 0
speed_direction = 0.1

servo.start(0)
servo.ChangeDutyCycle(3) # left -90 deg position
sleep(1)
servo.stop()


def illegal():
    global counter
    
    counter += 1
    if counter >= 3:
        servo.start(0)
        servo.ChangeDutyCycle(10) # left -90 deg position
        sleep(1)
        servo.stop()
        print(f"ILLEGAAL!!! je gaat te hard")
        pygame.quit()
        sys.exit()
        quit


def get_speed():
    global eindeMeting
    global start
    global grootteWiel
    global metingen
    global kmMax
    global playtime_credits
    global totaal
    global laatsteLoop
    print("hoi")
    
    laatsteLoop=0
    eindeMeting = time.perf_counter()
    totaal = 0
    tijd=eindeMeting-start
    start=time.perf_counter()
    cmSec=grootteWiel/tijd
    snelheidMeting=cmSec*0.036
    metingen.append(snelheidMeting)
    
    if len(metingen)>5:
        metingen.pop(0)
    
    for ding in metingen:
        totaal=totaal+ding
        
        
    print(f"je gaat gemiddeld{int(totaal)}")
    
    if int(totaal)>kmMax:
        illegal()
    sleep(0.3)
    return totaal

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(new_score):
    current_high = load_highscore()
    if new_score > current_high:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(new_score))
        return new_score
    return current_high

highscore = load_highscore()
button_rect = pygame.Rect(250, 300, 450, 80) #mark is ech heel raar en bart ook en vincent ook en jurre ook en tom ook en gabriel niet

# ================== main loop ==================
while True:
    mouse_clicked = False
    
    #GPIO input
    if gpio_available:
        if GPIO.input(PIN_GAME) != GPIO.LOW:
            game_button_pressed = True
        else:
            game_button_pressed = False
        if GPIO.input(PIN_ESC) != GPIO.LOW:
            esc_button_pressed = True
        else:
            esc_button_pressed = False
    else:
        game_button_pressed = False
        esc_button_pressed = False
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "menu":
            if button_rect.collidepoint(event.pos):
                mouse_clicked = True
                
    if game_button_pressed:
        mouse_clicked=True
    

    screen.fill((0, 0, 0))
    
    sensor.when_activated = get_speed
    # credits opbouwen
    playtime_credits=playtime_credits+0.03
    
    if laatsteLoop>360:
        laatsteLoop=0
        totaal=0
    laatsteLoop=laatsteLoop+1
    
    # ================== MENU ==================
    if game_state == "menu":
        warning_start = None  # reset timer

        if playtime_credits >= MIN_CREDITS_TO_PLAY:
            button_color = (0, 0, 255)
            button_text_str = "druk knop om te spelen"
        else:
            button_color = (100, 100, 100)
            button_text_str = f"nog {int(MIN_CREDITS_TO_PLAY - playtime_credits)} credits"

        pygame.draw.rect(screen, button_color, button_rect)
        button_text = font_small.render(button_text_str, True, (255, 255, 255))
        screen.blit(button_text, (button_rect.x + 50, button_rect.y + 25))

        speed_text = font_speed.render(f"{int(totaal)} km/u", True, (255, 255, 255))
        screen.blit(speed_text, (200, 200))

        credits_text = font_small.render(f"credits {int(playtime_credits)}", True, (0, 255, 0))
        screen.blit(credits_text, (50, 50))

        hs_text = font_small.render(f"Highscore: {highscore}", True, (255, 255, 100))
        screen.blit(hs_text, (50, 100))

        if mouse_clicked and playtime_credits >= 1:
            print("mark houdt van mannen")
            game_state = "game"
    
    # ================== GAME ==================
    if game_state == "game":
        if totaal > 3:
            warning = font_small.render("Je moet stilstaan om te spelen!", True, (255, 0, 0))
            screen.blit(warning, (150, 250))

            # start timer
            if warning_start is None:
                warning_start = time.time()

            # na 5 sec terug
            elif time.time() - warning_start > 5:
                game_state = "menu"
                warning_start = None

        else:
            warning_start = None

            try:
                from flappy import run_flappy_bird
                final_score = run_flappy_bird()

                playtime_credits -= CREDITS_PER_GAME
                if playtime_credits < 0:
                    playtime_credits = 0

                highscore = save_highscore(final_score)
                game_state = "menu"

            except Exception:
                error_text = font_small.render("Error loading game...", True, (255, 0, 0))
                screen.blit(error_text, (200, 200))
                pygame.time.wait(1500)
                game_state = "menu"
    
    # ================== esc ==================
    if esc_button_pressed:
        print("hoi???")
        if game_state == "game":
            game_state = "menu"
        elif game_state == "menu":
            pygame.quit()
            sys.exit()
        time.sleep(0.3)

    pygame.display.flip()
    clock.tick(60)
