import pygame
from Player import *
from settings import *
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uhybani")
running = True
clock = pygame.time.Clock()

hrac = Player(WIDTH // 2, HEIGHT)
hrac_group = pygame.sprite.Group()
hrac_group.add(hrac)
block = Block(WIDTH // 2, 0)
hrac_group.add(block)
while running:
    screen.fill((255, 0, 0))
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
             running = False
    hrac_group.update()
    hrac_group.draw(screen)
    clock.tick(60)
    pygame.display.update()
pygame.quit()