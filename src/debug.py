import pygame
import math

from src.screen import ScreenResolution

# Used for testing map creation, setting grid
class GridDebug:
    def __init__(self):
        self.block_size = 48
        self.color = (255, 255, 255)

    def _width(self, gui):
        for line in range(1,math.ceil(ScreenResolution.width / self.block_size)):
            pygame.draw.line(gui, self.color, (line*self.block_size, 0), (line*self.block_size, ScreenResolution.height)) # start: (x,y), stop (x,y)
    
    def _height(self, gui):
        for line in range(1,math.ceil(ScreenResolution.height / self.block_size)):
            pygame.draw.line(gui, self.color, (0, line*self.block_size), (ScreenResolution.width, line*self.block_size)) # start: (x,y), stop (x,y)
        
    def draw(self, gui):
        self._width(gui)
        self._height(gui)
        