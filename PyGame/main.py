import pygame
from pygame.locals import *

pygame.init()

window = pygame.display.set_mode((600, 600))
window.fill((255, 255, 255))

triangle_positions = []

size = 120  
color = (0, 0, 255)

run = True

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        elif event.type == MOUSEBUTTONDOWN:
            position = event.pos
            triangle_positions.append(position)

    window.fill((255, 255, 255))

    for position in triangle_positions:
        x, y = position

        
        points = [
            (x, y - size // 2),               
            (x - size // 2, y + size // 2),    
            (x + size // 2, y + size // 2)     
        ]

        pygame.draw.polygon(window, color, points)

    pygame.display.update()

pygame.quit()
