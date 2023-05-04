import yaml
from typing import Dict
from yaml import Loader


def load(content: str) -> Dict:
    try:
        return yaml.load(content, Loader)
    except yaml.YAMLError as exception:
        raise exception