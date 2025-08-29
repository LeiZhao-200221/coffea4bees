#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent / "python")

from classifier.patch import patch_awkward_pandas
from classifier.task import EntryPoint

if __name__ == "__main__":
    # install patch
    patch_awkward_pandas()
    # run main
    main = EntryPoint()
    try:
        main.run()
    except KeyboardInterrupt:
        from classifier.sysutils import recursive_interrupt

        recursive_interrupt()
