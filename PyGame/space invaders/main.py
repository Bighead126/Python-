import pygame
from settings import *
pygame.init()

def vypis_menu():
    screen.blit(title_text, title_rect)
    screen.blit(play_text, play_rect)
    screen.blit(settings_text, settings_rect)
    screen.blit(quit_text, quit_rect)
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Pygame")

clock = pygame.time.Clock()
FPS = 60

running = True
state = "MENU"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if state == "MENU":
                if play_rect.collidepoint(mouse_pos):
                    state = "PLAYING"
                elif settings_rect.collidepoint(mouse_pos):
                    state = "SETTINGS"
                elif quit_rect.collidepoint(mouse_pos):
                    running = False
    if state == "MENU":
        screen.fill((0, 0, 127))
        vypis_menu()

        
    elif state == "PLAYING":
        # herní logika
        pass
    elif state == "PAUSED":
        # zobrazení pauzy
        pass
    elif state == "GAME_OVER":
        # zobrazení skóre, restart
        pass




    pygame.display.update()
    clock.tick(FPS)
pygame.quit()