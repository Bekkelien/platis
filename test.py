import pygame

import time
# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))

# Load the source image
source_image = pygame.image.load("./art/background/pink.png")

# Define the destination coordinates
dest_coords = [(100, 100), (200, 200), (300, 300)]

# Create the blit sequence
blit_sequence = [(source_image, coords) for coords in dest_coords]
print(blit_sequence)
# Call the blits() function to draw the images
rects_changed = screen.blits(blit_sequence, doreturn=True)
time.sleep(1)
# Update the display
pygame.display.update()

# Print the list of rects that were changed
print(rects_changed)

# Quit Pygame
#pygame.quit()