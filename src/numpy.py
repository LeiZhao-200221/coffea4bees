# Deprecated: use base_class.data_formats.numpy instead
import warnings
warnings.warn(
    "base_class.numpy is deprecated. Use base_class.data_formats.numpy instead.",
    DeprecationWarning,
    stacklevel=2
)

from .data_formats.numpy import *  # noqa: F403,F401
