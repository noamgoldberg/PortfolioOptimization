import yaml
from kedro.config import ConfigLoader


def read_yaml(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def read_params(env: str = "conf"):
    return ConfigLoader(env).get("parameters/**")