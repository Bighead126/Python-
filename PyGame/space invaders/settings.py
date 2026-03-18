import pygame
pygame.init()

menu_font = pygame.font.SysFont("Arial", 50)
title_text = menu_font.render("SPACE INVADERS", True, (255, 255, 255))
title_rect = title_text.get_rect(center=(400, 50))
play_text = menu_font.render("PLAY", True, (255, 255, 255))
play_rect = play_text.get_rect(center=(400, 200))
settings_text = menu_font.render("SETTINGS", True, (255, 255, 255))
settings_rect = settings_text.get_rect(center=(400, 300))
quit_text = menu_font.render("QUIT", True, (255, 255, 255))
quit_rect = quit_text.get_rect(center=(400, 400))
