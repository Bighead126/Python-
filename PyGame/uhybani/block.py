import pygame
import random
from settings import *

class Block(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        x = random.randrange(0 + (BLOCK_WIDTH // 2), WIDTH - (BLOCK_WIDTH // 2))
        y = 0

        self.image = pygame.image.load(BLOCK_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.rect = self.image.get_rect(bottom=y, centerx=x)

        self.speed = speed

    def update(self):
        self.rect.y += self.speed