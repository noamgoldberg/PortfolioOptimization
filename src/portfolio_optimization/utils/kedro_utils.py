from typing import Dict, Any
from kedro.config import ConfigLoader,TemplatedConfigLoader


def get_config_loader(conf: str = "conf", templated: bool = True):
   if templated:
      from portfolio_optimization.settings import CONFIG_LOADER_ARGS
      return TemplatedConfigLoader(
         conf, globals_dict=CONFIG_LOADER_ARGS["globals_dict"]
      )
   return ConfigLoader(conf)

def read_catalog(conf: str = "conf", templated: bool = True) -> Dict[str, Any]:
    return get_config_loader(conf=conf, templated=templated).get("catalog*")

def read_params(conf: str = "conf", templated: bool = True) -> Dict[str, Any]:
   return get_config_loader(conf=conf, templated=templated).get("parameters*")