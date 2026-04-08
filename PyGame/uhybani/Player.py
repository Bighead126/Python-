import pygame
import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):   # 🔥 teď bere x, y
        super().__init__()

        self.image = pygame.image.load(settings.PLAYER_IMAGE_PATH).convert_alpha()
        self.width, self.height = self.image.get_size()

        self.image = pygame.transform.scale(
            self.image,
            (self.width * settings.PLAYER_SCALE, self.height * settings.PLAYER_SCALE)
        )

        self.rect = self.image.get_rect(center=(x, y))  # 🔥 použije x, y

        self.speed = settings.PLAYER_SPEED

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed

        if keys[pygame.K_RIGHT] and self.rect.right < settings.SCREEN_WIDTH:
            self.rect.x += self.speed


if __name__ == "__main__":
    import main