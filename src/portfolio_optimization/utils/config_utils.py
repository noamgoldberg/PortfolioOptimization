from typing import Optional
import yaml


def read_yaml(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)
    
def write_yaml(config: dict, filepath: str, indent: Optional[int] = None) -> None:
    with open(filepath, 'w') as file:
        yaml.dump(
            config,
            file,
            indent=indent,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )
