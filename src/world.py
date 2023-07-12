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
    def _load_block(self, size, color):
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
    


# 1 Terrain, 9 Kiwi

class Map():
    def __init__(self):
        self.world_matrix = [ [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
                              [0,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,9,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0],
                              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                              [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]


# TODO Map all asset types
#class Assets(Map):
class Assets(Map):
    def __init__(self):
        super().__init__()
        self.map = self.world_matrix # meh HOW does this inheritance work 
        self.block_size = 48
        self.terrain = []
        self.items = []
        
        for index, horizontal_line in enumerate(self.map):
            y = self.block_size * index
            for index, asset_type in enumerate(horizontal_line):
                x = self.block_size * index
                if asset_type == 1:
                    self.terrain.append(Block(x,y,self.block_size))

                elif asset_type == 9:
                    self.items.append(Items(x,y,32))

    def draw(self, gui):
        for asset in self.terrain:
            asset.draw(gui)

        for asset in self.items:
            asset.draw(gui)
