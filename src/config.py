import yaml
from pathlib import Path

class Config():
    def __init__(self):
        self.config_path = Path('config.yaml')
        self.cached_config = None

    def get_config(self) -> dict:
        """ Get the configuration file and return a dictionary """
        if self.cached_config is not None:
            return self.cached_config

        # Read config file
        with open(self.config_path) as f:
            config = yaml.load(stream=f, Loader=yaml.Loader)

        self.cached_config = config

        return config

# Testing configuration information:
if __name__ == '__main__':
    config = Config().get_config()
    from pprint import pprint
    pprint(config)