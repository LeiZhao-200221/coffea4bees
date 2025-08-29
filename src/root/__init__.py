# Backward compatibility shim - DEPRECATED
# Please use: from src.data_formats.root import *

import warnings  
warnings.warn(
    "base_class.root is deprecated. Use base_class.data_formats.root instead.",
    DeprecationWarning,
    stacklevel=2
)

from ..data_formats.root import *  # noqa: F401, F403
