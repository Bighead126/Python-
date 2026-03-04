import pygame
import random
from settings import *

x = random.randint(0, WIDTH - BLOCK_WIDTH)
print(x)

class Block(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load(BLOCK_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.rect = self.image.get_rect(bottom=y, centerx=x) # center = (x,y)¨
        self.speed = BLOCK_SPEED
        
    def update(self):
        self.rect.x = x
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.kill()
