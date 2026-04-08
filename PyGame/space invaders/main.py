import pygame
import settings
from player import *

pygame.init()

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

running = True
clock = pygame.time.Clock()

player = None

countdown_start = 0
COUNTDOWN_TIME = 3000

def vypis_menu():
    screen.fill((0, 0, 127))
    screen.blit(settings.title_text, settings.title_rect)
    screen.blit(settings.play_text, settings.play_rect)
    screen.blit(settings.settings_text, settings.settings_rect)
    screen.blit(settings.quit_text, settings.quit_rect)

def vypis_settings():
    screen.fill((0, 0, 127))
    screen.blit(settings.res800_text, settings.res800_rect)
    screen.blit(settings.res1024_text, settings.res1024_rect)
    screen.blit(settings.res1280_text, settings.res1280_rect)
    screen.blit(settings.back_text, settings.back_rect)

state = "MENU"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "MENU":
                if settings.play_rect.collidepoint(event.pos):
                    state = "COUNTDOWN"
                    countdown_start = pygame.time.get_ticks()

                elif settings.settings_rect.collidepoint(event.pos):
                    state = "SETTINGS"

                elif settings.quit_rect.collidepoint(event.pos):
                    running = False

            elif state == "SETTINGS":
                if settings.res800_rect.collidepoint(event.pos):
                    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = 800, 600
                    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

                elif settings.res1024_rect.collidepoint(event.pos):
                    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = 1024, 768
                    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

                elif settings.res1280_rect.collidepoint(event.pos):
                    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = 1280, 960
                    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

                elif settings.back_rect.collidepoint(event.pos):
                    state = "MENU"

    # ===== STATES =====
    if state == "MENU":
        vypis_menu()

    elif state == "SETTINGS":
        vypis_settings()

    elif state == "COUNTDOWN":
        screen.fill((0, 0, 0))

        current_time = pygame.time.get_ticks()
        elapsed = current_time - countdown_start

        remaining = 3 - (elapsed // 1000)

        if remaining > 0:
            text = settings.menu_font.render(str(remaining), True, (255, 255, 255))
            rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
            screen.blit(text, rect)
        else:
            # 🔥 vytvoření hráče uprostřed dole
            player = Player(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 50)
            state = "PLAYING"

    elif state == "PLAYING":
        screen.fill((0, 0, 0))

        player.update()
        screen.blit(player.image, player.rect)

    pygame.display.flip()
    clock.tick(settings.FPS)

pygame.quit()