# Deprecated: use base_class.storage instead
import warnings
warnings.warn(
    "base_class.system is deprecated. Use base_class.storage instead.",
    DeprecationWarning,
    stacklevel=2
)

from .storage import *  # noqa: F403,F401
