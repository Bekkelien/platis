import itertools

import pygame

from pathlib import Path

# Internals
from src.config import Config
from src.screen import ScreenResolution

config = Config().get_config()

# Move to config file for testing now
#PLAYER_COLOR = (255, 0, 0)
#BACKGROUND_COLOR = (255, 255, 255)

# Move out of main
pygame.init()
pygame.display.set_caption("Platis")
gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))
 
class AssetSprite():
    def __init__(self, asset_path: str, asset_folder: str, direction: bool = False):
        self.direction: bool = direction
        self.all_sprites: dict = {}
        self.image_paths: list = list(Path(asset_path + asset_folder).glob("*.png"))

    def _flip(self, sprites): # TODO: type hint, is sprite a pygame surface??
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

    def _get_image(self, image_path: Path) -> dict:
        
        sprite_sheet_image = pygame.image.load(image_path).convert_alpha()
        
        height = sprite_sheet_image.get_height()
        width = sprite_sheet_image.get_width() 
        image_blocks = int(width/height)

        sprites = []
        for i in range(image_blocks):
            surface = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha() # TODO: #32
            surface.blit(sprite_sheet_image, (0, 0), (height*i,0,height,height))
            # TODO :: 2x character size?
            sprites.append(surface)

        # Add sprites to the dictionary
        if self.direction:
            self.all_sprites[str(image_path.stem) + "_right"] = sprites
            self.all_sprites[str(image_path.stem) + "_left"] = self._flip(sprites)

        else:
            self.all_sprites[str(image_path.stem)] = sprites


    def load_sheets(self) -> dict: 
        """Loads the sprites sheets into a dictionary of sprites and returns the dictionary"""
        for image_path in self.image_paths:
            self._get_image(image_path)
        return self.all_sprites

class Background:
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

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity_x = 0
        self.velocity_y = 0
        self.fall_counter = 0
        self.jump_counter = 0
        self.hit = False
        self.animation_counter = 0
        self.hit_counter = 0
        self.direction = "left"
        self.sprites = AssetSprite(config['character']['path'], config['character']['folder'], direction=True).load_sheets()
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, velocity):
        self.velocity_x = -velocity
        if self.direction != "left": # If direction is not left and the player is moving left change direction
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.velocity_x = velocity
        if self.direction!= "right": # If direction is not right and the player is moving right change direction
            self.direction = "right"
            self.animation_count = 0

    def gravity(self):
        self.velocity_y += min(1, (self.fall_counter / config['game_settings']['fps']) * config['character']['gravity']) # Minimum gravity is 1 (NOTE: Should be pixel variable?)
        self.fall_counter += 1
        # missing gravity reset

    def loop(self):
        #self.gravity() # Adding gravity to the player
        self.move(self.velocity_x, self.velocity_y) # Move the player x,y direction
        self.update_sprite()
        self.update() # remove the background box from the character
    
    def update_sprite(self):
        sprite_state = "idle" # Idle sprite state every time we update
        if not self.velocity_x:
            sprite_state = "run"

        sprite_state = sprite_state + "_" + self.direction
        sprite_current = self.sprites[sprite_state]
        sprite_index = (self.animation_counter // config['character']['animation_delay']) % len(sprite_current)
        self.current_sprite = sprite_current[sprite_index]

        animation_counter_limit = len(sprite_current*config['character']['animation_delay'])
        if self.animation_counter < animation_counter_limit:
            self.animation_counter += 1
        else:
            self.animation_counter = 0 # Reset animation counter

        #print(self.animation_counter)
        
    def update(self):
        self.rect = self.current_sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.current_sprite)

    def draw(self, gui):
        gui.blit(self.current_sprite, self.rect)
        #pygame.draw.rect(gui, PLAYER_COLOR, self.rect)
        ##pygame.display.update()

# TODO: I dont like to have functions when everything is classes  
def move_player(player):
    keys = pygame.key.get_pressed()
    
    player.loop() # Move the player every frame
    player.velocity_x = 0 # Reset velocity when not pressing a button

    if keys[pygame.K_LEFT]:
        player.move_left(config['character']['velocity'])
    if keys[pygame.K_RIGHT]:
        player.move_right(config['character']['velocity'])

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
        clock.tick(config['game_settings']['fps'])

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