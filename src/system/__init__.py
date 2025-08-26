# Backward compatibility for system package
import warnings
warnings.warn(
    "base_class.system is deprecated. Use base_class.storage instead.",
    DeprecationWarning,
    stacklevel=2
)
