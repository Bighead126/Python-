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

text = "Score: {}".format(score)
base_font = pygame.font.Font(None, 40)

hrac = Player(WIDTH // 2, HEIGHT)
hrac_group = pygame.sprite.Group()
hrac_group.add(hrac)
blok = Block()
blok_group = pygame.sprite.Group()
blok_group.add(blok)

BLOK_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(BLOK_SPAWN, 500)

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == BLOK_SPAWN:
            blok_group.add(Block())
            score += 1
            text = "Score: {}".format(score)
            score_text = base_font.render(text, True, (255, 255, 255))
    hrac_group.update()
    hrac_group.draw(screen)
    blok_group.update()
    blok_group.draw(screen)
    

    if pygame.sprite.spritecollide(hrac, blok_group, True, pygame.sprite.collide_mask):
        print("KOLIZE!")
        pygame.time.delay(1000)
        with open("score.txt", "w") as soubor:
            soubor.write(str(score))
        running = False

    score_text = base_font.render(text, True, (255, 255, 255))
    screen.blit(score_text, (10, 10))


    pygame.display.update()
    clock.tick(FPS)
pygame.quit()