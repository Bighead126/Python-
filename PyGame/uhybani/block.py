import pygame
from settings import *
class Block(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("obrazky/diamant.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center = (x,y))
        self.speed = BLOCK_SPEED
    def update(self):
        