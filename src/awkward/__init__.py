# Backward compatibility shim - DEPRECATED  
# Please use: from src.data_formats.awkward import *

import warnings
warnings.warn(
    "base_class.awkward is deprecated. Use base_class.data_formats.awkward instead.",
    DeprecationWarning,
    stacklevel=2
)

from ..data_formats.awkward import *  # noqa: F401, F403
