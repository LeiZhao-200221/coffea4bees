# Deprecated: use base_class.plotting instead
import warnings
warnings.warn(
    "base_class.plots is deprecated. Use base_class.plotting instead.",
    DeprecationWarning,
    stacklevel=2
)

from .plotting import *  # noqa: F403,F401
