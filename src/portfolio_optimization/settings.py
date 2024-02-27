"""Project settings. There is no need to edit this file unless you want to change values
from the Kedro defaults. For further information, including these default values, see
https://kedro.readthedocs.io/en/stable/kedro_project_setup/settings.html."""



# Instantiated project hooks.
# from portfolio_optimization.hooks import ProjectHooks
# HOOKS = (ProjectHooks(),)

# Installed plugins for which to disable hook auto-registration.
# DISABLE_HOOKS_FOR_PLUGINS = ("kedro-viz",)

# Class that manages storing KedroSession data.
# from kedro.framework.session.shelvestore import ShelveStore
# SESSION_STORE_CLASS = ShelveStore
# Keyword arguments to pass to the `SESSION_STORE_CLASS` constructor.
# SESSION_STORE_ARGS = {
#     "path": "./sessions"
# }

# Class that manages Kedro's library components.
# from kedro.framework.context import KedroContext
# CONTEXT_CLASS = KedroContext

# Directory that holds configuration.
# CONF_SOURCE = "conf"

# Class that manages how configuration is loaded.
# CONFIG_LOADER_CLASS = ConfigLoader

from kedro.config import TemplatedConfigLoader
from portfolio_optimization.consts import DATE_FORMAT
from portfolio_optimization.utils.config_utils import read_params
from portfolio_optimization.utils.date_utils import format_date, get_end_date
import warnings

# (0) Suppress future and deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# (1) Establish Global Params
params = read_params()
CONFIG_LOADER_CLASS = TemplatedConfigLoader
CONFIG_LOADER_ARGS = {
      "globals_dict": {
          "symbols": params["data"]["stocks"]["symbols"],
          "start_date": format_date(params["data"]["stocks"]["start_date"], format=DATE_FORMAT),
          "end_date": get_end_date(params["data"]["stocks"].get("end_date"), format=DATE_FORMAT),
          "n_iters": params["optimize"].get("monte_carlo_n_iters", 20000),
          "scipy_solver": params["optimize"].get("scipy_solver", "SLSQP"),
      }
}

# Class that manages the Data Catalog.
# from kedro.io import DataCatalog
# DATA_CATALOG_CLASS = DataCatalog
