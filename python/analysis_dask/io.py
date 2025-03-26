from datetime import datetime
from os import fspath
from pathlib import PurePosixPath
from typing import Any, Callable, Literal, Optional
from urllib.parse import urlparse
from uuid import uuid1

import fsspec
import fsspec.utils
from base_class.config import Configurable, config
from base_class.typetools import borrow_typehints
from dask import delayed


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
            case ".pkl" | ".coffea":
                import pickle

                return pickle.dumps
            case _:
                raise NotImplementedError(f"Unknown file format: {path}")

    def infer_compression(self, path: str, mode: str):
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
    def __call__(
        self,
        obj,
        path: str,
        absolute: bool = False,
        serializer: Callable[[Any], str | bytes] = ...,
        mode: Literal["t", "b"] = ...,
        compression: Optional[str] = ...,
        **kwargs,
    ):
        path = self.resolve_path(path, absolute)
        if serializer is ...:
            serializer = self.infer_serializer(path)
        data = serializer(obj, **kwargs)
        if mode is ...:
            mode = self.infer_mode(data)
        if compression is ...:
            compression = self.infer_compression(path, mode)
        with fsspec.open(path, f"w{mode}", compression=compression) as f:
            f.write(data)
        return path

    @classmethod
    @borrow_typehints(__call__)
    def dumps(cls, *args, **kwargs):
        return cls()(*args, **kwargs)
