import pygame

# Internals
from src.screen import ScreenResolution

pygame.init()
pygame.display.set_caption("Platis")


FPS = 60
PLAYER_SPEED = 5
BACKGROUND_COLOR = (255, 255, 255)

gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))

def main(gui):
    clock = pygame.time.Clock()

    alive = True
    while alive:
        clock.tick(FPS)

        for event in pygame.event.get():
            # Exit if the player dies
            if event.type == pygame.QUIT:
                alive = False
                break

    
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(gui)