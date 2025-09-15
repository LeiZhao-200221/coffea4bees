# Backward compatibility shim - DEPRECATED
# Please use: from src.storage.eos import EOS

import warnings
warnings.warn(
    "base_class.system.eos is deprecated. Use base_class.storage.eos instead.",
    DeprecationWarning,
    stacklevel=2
)

from ..storage.eos import *  # noqa: F401, F403
