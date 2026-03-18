import pygame
from Player import *
from Block import Block
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uhybani")
running = True
clock = pygame.time.Clock()

score = 0
game_speed = 5
base_font = pygame.font.Font(None, 40)


try:
    with open("score.txt", "r") as soubor:
        high_score = int(soubor.read())
except FileNotFoundError:
    high_score = 0

hrac = Player(WIDTH // 2, HEIGHT)
hrac_group = pygame.sprite.Group()
hrac_group.add(hrac)

blok_group = pygame.sprite.Group()

BLOK_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(BLOK_SPAWN, 500)

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == BLOK_SPAWN:
            blok_group.add(Block(game_speed)) 

    hrac_group.update()
    hrac_group.draw(screen)

    blok_group.update()

    for blok in blok_group:
        if blok.rect.top > HEIGHT:
            score += 1
            blok.kill()

           
            if score % 25 == 0:
                game_speed += 1
                print("Zrychlení:", game_speed)

    blok_group.draw(screen)

    
    if pygame.sprite.spritecollide(hrac, blok_group, True, pygame.sprite.collide_mask):
        print("KOLIZE!")
        pygame.time.delay(1000)

        if score > high_score:
            with open("score.txt", "w") as soubor:
                soubor.write(str(score))

        running = False

    score_text = base_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    high_score_text = base_font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (10, 50))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()