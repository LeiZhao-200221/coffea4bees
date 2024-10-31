from ...typetools import dict_proxy
from ...utils import import_
from ._dict import mapping


def instance(opt: list[str], pkg: str, /, **kwargs):
    if len(opt) < 1:
        return None
    parts = f"{pkg}.{opt[0]}".split(".")
    _, cls = import_(".".join(parts[:-1]), parts[-1])
    if cls is None:
        return None
    if len(opt) > 1:
        dict_proxy(kwargs).update(*map(mapping, opt[1:]))
    return cls(**kwargs)
