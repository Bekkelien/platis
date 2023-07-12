import pygame
import itertools
import random
import time 

from pathlib import Path
from typing import List, Optional
# Internals
from src.config import Config
from src.screen import ScreenResolution

config = Config().get_config()

# Move out of main
pygame.init()
pygame.display.set_caption(config['game_settings']['name'])
gui = pygame.display.set_mode((ScreenResolution.width, ScreenResolution.height))
 
class AssetSprite:
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
            surface = pygame.Surface((height,height), pygame.SRCALPHA).convert_alpha() 
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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.sprites = AssetSprite(config['character']['path'], config['character']['folder'], direction=True).load_sheets()

        self.hit: bool = False
        self.points: int = 0
        self.fall_count:int = 0 # Used to increment gravity "speed"
        self.jump_count:int = 0
        self.hit_count: int = 0
        self.current_velocity_x: int = 0 # NOTE: A bit messy to have float in y and int in x
        self.current_velocity_y: float = config['character']['gravity'] # Important to start with some gravity
        self.animation_count: int = 0

        self.direction: str = "left" # NOTE: Easy to understand when string but not optimal
        self.player_state: str = "fall"
    
    def move(self):
        self.rect.x += self.current_velocity_x # Current x position of the player
        self.rect.y += self.current_velocity_y # Current y position of the player

    def move_left(self, velocity):
        self.current_velocity_x = -velocity
        if self.direction != "left": # If direction is not left and the player is moving left we are moving left
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.current_velocity_x = velocity
        if self.direction!= "right": # If direction is not right and the player is moving right we are moving left
            self.direction = "right"
            self.animation_count = 0

    def gravity(self): # NOTE: This is a bit of a hack but it works
        self.current_velocity_y += min(config['character']['gravity'], (self.fall_count / config['game_settings']['fps']) * config['character']['gravity']) 
        self.fall_count += 1

    def jump(self):
        self.current_velocity_y = - (config['character']['gravity'] * config['character']['jump_velocity'])
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
        self.fall_count = 0
        self.jump_count = 0
        self.current_velocity_y = 0
                
    def hit_head(self):
        self.count = 0
        self.current_velocity_y *= -1 # Change direction of the velocity if we hit the head

    def loop(self):
        # print(self.player_state)
        self.gravity() # Adding gravity to the player
        self.move() # Move the player x,y direction
        self.update_player_state()
        self.update_sprite()
        self.update() # remove the background box from the character
    
    def update_player_state(self):
        self.player_state = "idle"
        if self.current_velocity_y < 0:
            if self.jump_count == 1:
                self.player_state = "jump"
            elif self.jump_count == 2:
                self.player_state = "double_jump"
        elif self.current_velocity_y >= config['character']['gravity'] * 2: # NOTE: TODO: Better gravity solution HAX We are falling if we are moving 2x faster then gravity
            self.player_state = "fall"
        elif self.current_velocity_x != 0: # elif as we are not running when jumping
            self.player_state = "run"
            
    def update_sprite(self):
        sprite_state = self.player_state + "_" + self.direction
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

    def horizontal(self, player, objects: list): # BUG we are colliding with the floor on objects due to gravity anybody's FUCKING GUESS
        # BUG sometimes we can jump on top of the item even if we are colliding horizontally and not jumping
        if player.current_velocity_x != 0:
            for object in objects:
                if pygame.sprite.collide_mask(player, object): 
                    print("X collision")
                    player.rect.x = player.rect.x - player.current_velocity_x 
                    return 

    def vertical(self, player, objects: list):
        # NOTE: Check non vertical moving for performance (since we almost always have gravity this doesn't matter FIXME)
        for object in objects:
            if pygame.sprite.collide_mask(player, object): # NOTE: Object need rect from Asset from pygame.sprite.Sprite collide_mask
                if player.current_velocity_y > 0: # Moving down
                    player.rect.bottom = object.rect.top # move player to top
                    player.landed()
                if player.current_velocity_y < 0: # Moving up
                    player.rect.top = object.rect.bottom # move player to bottom
                    player.hit_head()
    
    def check(self, player, objects: list):
        self.horizontal(player, objects)
        self.vertical(player, objects)

# FIXME
class GamePlay():
    def __init__(self):
        self.timer = time.time()

    def check(self, player, objects: list):
        for object in objects:
            if pygame.sprite.collide_mask(player, object): 
                player.points += 1
                self.timer = time.time()
                objects.remove(object)
                
                # TODO: MAP Safe places to add items on the screen
                x = random.randint(32, ScreenResolution.width)
                y = random.randint(48*4, ScreenResolution.height/2)
                print(ScreenResolution.height + y)
                objects.append(Items(x, ScreenResolution.height - y, 32))

        if time.time() - self.timer > 5:
            print(f"Dead, you got: {player.points} points")
            return True 
        
        return False 

class Hud():
    def __init__(self):
        self.font = pygame.font.SysFont("ArialBold", int(60/config['graphics']['screen_reduction']))

    def _points(self, player):
        text_surface = self.font.render(f"Points: {player.points}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10) 

        return text_surface, text_rect

    def draw(self, player, gui):
        text_surface, text_rect = self._points(player)
        gui.blit(text_surface, text_rect)

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

class Block(Object):
    def __init__(self, x, y, size, color='pink'): # NOTE: Only support square size blocks ATM
        super().__init__(x, y, size, size)
        block = self._load_block(size, color) # NOTE: Back-loading the function how to do this cleaner and better
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) 

    # TODO Improvements TODO
    def _load_block(self, size,color):
        path = Path(config['background']['path']) / Path(config['background']['folder']) / Path(config['background']['terrain'])
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        if color == 'green':
            color_placement = 0 # Green
        if color == 'orange':
            color_placement = 64 # Orange
        if color == 'pink':
            color_placement = 128 # Pink
        rect = pygame.Rect(96, color_placement, size, size)  
        surface.blit(image, (0,0) ,rect)

        # Scaling
        for _ in range(1, config['background']['scale']):
            surface = pygame.transform.scale2x(surface)

        return surface        
 

# FIXME
# JUST FOR TESTING
# NOTE: Masking is implemented for every item this is bad ignoring for now making for this item TODO
class Items(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = self._load_kiwi(size) # NOTE: Back-loading the function how to do this cleaner and better
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) 

    # TODO Improvements TODO
    def _load_kiwi(self, size):
        path = Path(config['items']['path']) / Path("kiwi.png") # HARDCODING FIXME
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, size, size)  # Loading static not the sprite NOTE:
        surface.blit(image, (0,0) ,rect)

        # Scaling
        for _ in range(1, config['background']['scale']):
            surface = pygame.transform.scale2x(surface)

        return surface
    
class Asset():
    def __init__(self):
        block_size_floor = 48 * config['background']['scale']

        self.floors = [Block(i, ScreenResolution.height - block_size_floor, block_size_floor) for i in range(0, ScreenResolution.width, block_size_floor)]
        self.objects =  [
                         Block(128*2, ScreenResolution.height - block_size_floor*4, block_size_floor),
                         Block(128*4, ScreenResolution.height - block_size_floor*4, block_size_floor),
                         Block(128*5, ScreenResolution.height - block_size_floor*4, block_size_floor),
                         Block(128*7, ScreenResolution.height - block_size_floor*4, block_size_floor),
                         Block(128*9, ScreenResolution.height - block_size_floor*4, block_size_floor),
                         ]
        
        self.assets = self.floors + self.objects

        self.items = [Items(128*2, ScreenResolution.height - 32*4, 32)]


    def draw(self, gui):
        for asset in self.assets:
            asset.draw(gui)

        for asset in self.items:
            asset.draw(gui)


class Movement():
    # player changes so needs to be passed as a parameter every time
    def __init__(self) -> None:
        self.keys = None
    
    def move(self, player):
        keys = pygame.key.get_pressed()
        player.loop() # Move the player every frame
        player.current_velocity_x = 0 # Reset velocity when not pressing a button
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
    gameplay = GamePlay()
    hud = Hud()

    # Preloading
    background.fill()

    alive = True # Not implemented
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

        # Order of operations is important
        movement.move(player) 

        # FIXME
        game_over_hax = gameplay.check(player, asset.items)
        if game_over_hax:
            break

        collision.check(player, asset.assets)

        ## NOTE:: draw in every function creates order of operations to be important
        background.draw(gui) # This is a bit confusing naming convention / fill and draw the background a bit messy
        asset.draw(gui)
        player.draw(gui)

        hud.draw(player, gui)
        # Update screen
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(gui)