from typing import Dict, Any
from kedro.config import TemplatedConfigLoader

from portfolio_optimization.settings import CONFIG_LOADER_ARGS


def read_catalog(conf: str = "conf") -> Dict[str, Any]:
    return TemplatedConfigLoader(
       conf, globals_dict=CONFIG_LOADER_ARGS["globals_dict"]
    ).get("catalog*")