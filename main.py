import pygame
import itertools

from pathlib import Path

# Internals
from src.config import Config
from src.screen import ScreenResolution

config = Config().get_config()

# Move out of main
pygame.init()
pygame.display.set_caption(config['game_settings']['name'])
gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))
 
class AssetSprite():
    def __init__(self, asset_path: str, asset_folder: str, direction: bool = False):
        self.direction: bool = direction
        self.all_sprites: dict = {}
        self.image_paths: list = list(Path(asset_path + asset_folder).glob("*.png"))

    def _flip(self, sprites): # TODO: type hint, is sprite a pygame surface??
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

    def _get_image(self, image_path: Path) -> dict:
        print("Loading asset sprite:", image_path)
        sprite_sheet_image = pygame.image.load(image_path).convert_alpha()
        
        height = sprite_sheet_image.get_height()
        width = sprite_sheet_image.get_width() 
        image_blocks = int(width/height)

        sprites = []
        for i in range(image_blocks):
            surface = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha() # TODO: #32
            surface.blit(sprite_sheet_image, (0, 0), (height*i,0,height,height))
            if 'character' in str(image_path): # TODO :: Make generic if folder name is changed
                for _ in range(1,config['character']['scale']):
                    surface = pygame.transform.scale2x(surface)
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


class Object(pygame.sprite.Sprite):
    """Base class for all assets"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height

    def draw(self, gui):
        gui.blit(self.image, (self.rect.x, self.rect.y))


# This should be in block class or something like that
def load_block(size): # TODO: Map all terrain blocks, add name to loading a block
    path = Path(config['background']['path']) / Path(config['background']['folder']) / Path(config['background']['terrain'])
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 128, size, size)
    surface.blit(image, (0,0) ,rect)

    # Scaling
    for _ in range(1, config['background']['scale']):
        surface = pygame.transform.scale2x(surface)

    return surface

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity_x = 0
        self.velocity_y = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.animation_count = 0
        self.hit_count = 0
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
        self.velocity_y += min(1, (self.fall_count / config['game_settings']['fps']) * config['character']['gravity']) # Minimum gravity is 1 (NOTE: Should be pixel variable?)
        self.fall_count += 1
        # missing gravity reset

    def jump(self):
        self.velocity_y = - (config['character']['gravity'] * config['character']['jump_velocity'])
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
        self.fall_count = 0
        self.velocity_y = 0
        self.jump_count = 0
                
    def hit_head(self):
        self.count = 0
        self.velocity_y *= -1

    def loop(self):
        self.gravity() # Adding gravity to the player
        self.move(self.velocity_x, self.velocity_y) # Move the player x,y direction
        self.update_sprite()
        self.update() # remove the background box from the character
    
    def update_sprite(self):
        sprite_state = "idle" # Idle sprite state every time we update
        if self.velocity_y < 0: # We are jumping
            if self.jump_count == 1:
                sprite_state = "jump"
            elif self.jump_count == 2:
                sprite_state = "double_jump"
        elif self.velocity_y > config['character']['gravity']: # NOTE: HAX We are falling if we are moving faster then gravity
            sprite_state = "fall"

        elif self.velocity_x > 0: # elif as we are not running when jumping
            sprite_state = "run"

        sprite_state = sprite_state + "_" + self.direction
        sprite_current = self.sprites[sprite_state]
        sprite_index = (self.animation_count // config['character']['animation_delay']) % len(sprite_current)
        self.current_sprite = sprite_current[sprite_index]

        animation_counter_limit = len(sprite_current*config['character']['animation_delay'])
        if self.animation_count < animation_counter_limit:
            self.animation_count += 1
        else:
            self.animation_count = 0 # Reset animation counter

        #print(self.animation_counter)
        
    def update(self):
        """ Mask the character to get rid of the background box """
        self.rect = self.current_sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.current_sprite)

    def draw(self, gui):
        gui.blit(self.current_sprite, self.rect)

class Collision():
    def __init__(self) -> None:
        pass

    def vertical(self, player, objects: list):
        # NOTE: Check non vertical moving for performance
        collision = []
        for object in objects:
            if pygame.sprite.collide_mask(player, object): # NOTE: Object need rect from Asset from pygame.sprite.Sprite collide_mask
                if player.velocity_y > 0: # Moving down
                    player.rect.bottom = object.rect.top # move player to top
                    player.landed()
                if player.velocity_y < 0: # Moving up
                    player.rect.top = object.rect.bottom # move player to bottom
                    player.hit_head()

            collision.append(object) # All objects that are colliding with the player

        return collision # TODO :: Not used ATM
    


class Asset():
    def __init__(self, block_size=48*config['background']['scale']):
        self.floors = [Block(i, ScreenResolution.height - block_size, block_size) for i in range(0, ScreenResolution.width, block_size)]
        self.objects =  [Block(128, ScreenResolution.height - block_size*2, block_size),
                         Block(128*2, ScreenResolution.height - block_size*4, block_size),
                         Block(128*4, ScreenResolution.height - block_size*6, block_size)
                         ]
        
        self.assets = self.floors + self.objects

    def draw(self, gui):
        for asset in self.assets:
            asset.draw(gui)
        
        
class Movement():
    # player changes so needs to be passed as a parameter every time
    def __init__(self) -> None:
        self.keys = None
    
    def move(self, player):
        keys = pygame.key.get_pressed()
        player.loop() # Move the player every frame
        player.velocity_x = 0 # Reset velocity when not pressing a button

        if keys[pygame.K_LEFT]:
            player.move_left(config['character']['velocity'])
        if keys[pygame.K_RIGHT]:
            player.move_right(config['character']['velocity'])

    def jump(self, player, event):
        if event.key == pygame.K_SPACE and player.jump_count < config['character']['jump_limit']:
            player.jump()

class Scroll(): # TODO:
    def __init__(self) -> None:
        pass

def main(gui):
    #print(ScreenResolution.width)
    clock = pygame.time.Clock()

    # Invoke
    background = Background()
    player = Player(50,50,50,50)
    movement = Movement()
    asset = Asset()
    collision = Collision()

    # All assets 
    objects = asset.assets

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
            
            # Check for key presses
            if event.type == pygame.KEYDOWN:
                movement.jump(player, event) 

            # TODO add for "key down"

        # Check for movement before doing anything else
        movement.move(player) 
        collision.vertical(player, objects)
        
        ## NOTE:: draw in every function creates order of operations to be important
        background.draw(gui) # This is a bit confusing naming convention / fill and draw the background a bit messy
        asset.draw(gui)
        player.draw(gui)

        # Update screen
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(gui)