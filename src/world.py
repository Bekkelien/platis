import pygame

from pathlib import Path

from src.screen import ScreenResolution
from src.config import Config

config = Config().get_config()

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

        return surface
    
class Assets():
    def __init__(self):
        block_size_floor = 48

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
