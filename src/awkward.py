# Deprecated: use base_class.data_formats.awkward instead
import warnings
warnings.warn(
    "base_class.awkward is deprecated. Use base_class.data_formats.awkward instead.",
    DeprecationWarning,
    stacklevel=2
)

from .data_formats.awkward import *  # noqa: F403,F401
