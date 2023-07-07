import itertools

import pygame

from pathlib import Path

# Internals
from src.config import Config
from src.screen import ScreenResolution

config = Config().get_config()

pygame.init()
pygame.display.set_caption("Platis")


FPS = 60
PLAYER_SPEED = 5
BACKGROUND_COLOR = (255, 255, 255)

gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))

class Background: # TODO fix implementation of background hardcoded
    def __init__(self):
        background = "pink.png"
        self.image = pygame.image.load(Path(config['art']['background'])  / Path(background))
        _, _, self.width, self.height = self.image.get_rect()

    def fill(self):
        # X and Y upper left corner coordinate for each tile in the background image to fill the screen
        block_coordinate_x = [i for i in range(0, ScreenResolution.width, self.width)]
        block_coordinate_y = [i for i in range(0, ScreenResolution.height, self.height)]
        self.tiles = list(itertools.product(block_coordinate_x, block_coordinate_y))

    def draw(self):
        for tile in self.tiles:
            gui.blit(self.image, tile)
        pygame.display.update()


def main(gui):
    print(ScreenResolution.width)
    clock = pygame.time.Clock()

    # Invoke background
    background = Background()
    background.fill()

    alive = True
    while alive:
        clock.tick(FPS)

        for event in pygame.event.get():
            # Exit if the player dies
            if event.type == pygame.QUIT:
                alive = False
                break
        
        # Gaming 
        background.draw()
    
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(gui)