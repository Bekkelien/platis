import screeninfo
from dataclasses import dataclass

# NOTE: Temp to reduce size of the window
FACTOR = 2

@dataclass
class ScreenResolution:
    screen = screeninfo.get_monitors()[0]
    width = screen.width / 2
    height = screen.height / 2



if __name__ == '__main__':
    print(ScreenResolution.screen)