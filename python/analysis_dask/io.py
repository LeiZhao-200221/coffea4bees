from datetime import datetime
from functools import wraps
from os import fspath
from pathlib import PurePosixPath
from typing import Any, Callable, Concatenate, Literal, Optional, ParamSpec, Protocol
from urllib.parse import urlparse
from uuid import uuid1

import fsspec
import fsspec.utils
from base_class.config import Configurable, config
from dask import delayed

P = ParamSpec("P")


def timestamp(format: Optional[str] = None):
    now = datetime.now()
    if format is None:
        return now.isoformat()
    else:
        return now.strftime(format)


def uuid():
    return uuid1().hex


def joinurl(base: str, /, *parts: str):
    url = urlparse(base)
    return url._replace(path=fspath(PurePosixPath(url.path).joinpath(*parts))).geturl()


class Dumper(Configurable, namespace="analysis.io.dump"):
    compression = config("lz4")
    path_base = config[str]()
    path_kwargs = config[dict[str, str]]({})

    def __init__(
        self,
        path: str,
        absolute: bool = False,
        serializer: Callable[[Any], str | bytes] = ...,
        mode: Literal["t", "b"] = ...,
        compression: Optional[str] = ...,
        **kwargs,
    ):
        self.path = self.resolve_path(path, absolute)
        if serializer is ...:
            serializer = self.infer_serializer(path)
        self.serializer = serializer
        self.mode = mode
        self.compression = compression
        self.kwargs = kwargs

    def resolve_path(self, path: str, absolute: bool):
        path = path.format(**self.path_kwargs)
        if absolute:
            return path
        parsed = urlparse(self.path_base.format(**self.path_kwargs))
        return parsed._replace(path=fspath(PurePosixPath(parsed.path) / path)).geturl()

    def infer_serializer(self, path: str):
        match PurePosixPath(path).suffixes[0]:
            case ".json":
                import json

                return json.dumps
            case ".yaml" | ".yml":
                import yaml

                return yaml.safe_dump
            case ".pkl":
                import pickle

                return pickle.dumps
            case ".coffea":  # backward compatibility
                import cloudpickle

                return cloudpickle.dumps
            case _:
                raise NotImplementedError(f"Unknown file format: {path}")

    def infer_compression(self, path: str, mode: str):
        if PurePosixPath(path).suffix == ".coffea":
            return "lz4"  # backward compatibility
        compression = fsspec.utils.infer_compression(path)
        if compression is None and mode == "b":
            compression = self.compression
        return compression

    def infer_mode(self, data):
        match data:
            case str():
                return "t"
            case bytes():
                return "b"
            case _:
                raise ValueError(f"Unknown output type: {type(data)}")

    @delayed()
    def __call__(self, obj):
        data = self.serializer(obj, **self.kwargs)
        if (mode := self.mode) is ...:
            mode = self.infer_mode(data)
        if (compression := self.compression) is ...:
            compression = self.infer_compression(self.path, mode)
        with fsspec.open(self.path, f"w{mode}", compression=compression) as f:
            f.write(data)
        return self.path


class _DumpClassmethod(Protocol[P]):
    def __call__(self, obj: Any, *args: P.args, **kwargs: P.kwargs) -> str: ...


def _dump_classmethod(
    method: Callable[Concatenate[Any, P], Any],
) -> Callable[[Callable], _DumpClassmethod[P]]:
    return wraps(method)


@_dump_classmethod(Dumper.__init__)
def dumps(obj, *args, **kwargs):
    return Dumper(*args, **kwargs)(obj)
