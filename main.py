import itertools

import pygame

from pathlib import Path

# Internals
from src.config import Config
from src.screen import ScreenResolution

config = Config().get_config()

# Move to config file for testing now
FPS = 60
GRAVITY = 1
PLAYER_VELOCITY = 5
#PLAYER_COLOR = (255, 0, 0)
#BACKGROUND_COLOR = (255, 255, 255)

# Move out of main
pygame.init()
pygame.display.set_caption("Platis")
gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))
 

# TESTING SPRITES TODO ::
def get_image(image):
    sprites = []
    sprite_sheet_image = pygame.image.load(Path(config['character']['path']) / Path(image)).convert_alpha()
    height = sprite_sheet_image.get_height()
    width = sprite_sheet_image.get_width() 
    images = int(width/height)

    for i in range(images):
        image_segment = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha()
        image_segment.blit(sprite_sheet_image, (0, 0), (height*i,0,height,height))
        sprites.append(image_segment)
    
    print(sprites)
    return sprites

class Background: # TODO fix implementation of background hardcoded
    def __init__(self):
        self.image = pygame.image.load(Path(config['background']['path'])  / Path(config['background']['type']))
        _, _, self.width, self.height = self.image.get_rect()

    def fill(self):
        # X and Y upper left corner coordinate for each tile in the background image to fill the screen
        x = [i for i in range(0, ScreenResolution.width, self.width)]
        y = [i for i in range(0, ScreenResolution.height, self.height)]
        self.tiles = list(itertools.product(x, y))


    def draw(self, gui):
        for tile in self.tiles:
            gui.blit(self.image, tile)
        #pygame.display.update()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity_x = 0
        self.velocity_y = 0
        self.fall_counter = 0
        #self.mask = None
        # HAX FOR NOW::
        self.image = get_image("run.png")[3] #TODO: Fix this only loading one image
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, velocity):
        self.velocity_x = -velocity

    def move_right(self, velocity):
        self.velocity_x = velocity

    def gravity(self):
        self.velocity_y += min(1, (self.fall_counter / FPS) * GRAVITY) # Minimum gravity is 1 (NOTE: Should be pixel variable?)
        self.fall_counter += 1
        # missing gravity reset

    def loop(self):
        #self.gravity() # Adding gravity to the player
        self.move(self.velocity_x, self.velocity_y) # Move the player x,y direction
    
    def draw(self, gui):
        gui.blit(self.image, self.rect)
        #pygame.draw.rect(gui, PLAYER_COLOR, self.rect)
        ##pygame.display.update()

# TODO: I dont like to have functions when everything is classes  
def move_player(player):
    keys = pygame.key.get_pressed()
    
    player.loop() # Move the player every frame
    player.velocity_x = 0 # Reset velocity when not pressing a button

    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VELOCITY)

    player.draw(gui) # Cache the players new position


def main(gui):
    print(ScreenResolution.width)
    clock = pygame.time.Clock()

    # Invoke
    background = Background()
    player = Player(50,50,50,50)

    # Preloading
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
        background.draw(gui)
        move_player(player)
        
        # Update screen
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(gui)