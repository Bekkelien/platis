import screeninfo
from dataclasses import dataclass


from src.config import Config


config = Config().get_config()

@dataclass
class ScreenResolution:
    screen = screeninfo.get_monitors()[0]
    width: int = int(screen.width / config['graphics']['screen_reduction'])
    height: int = int(screen.height / config['graphics']['screen_reduction'])



if __name__ == '__main__':
    print(ScreenResolution.screen)