from __future__ import annotations

import gc
import logging
import re
from abc import abstractmethod
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import chain
from typing import Iterable

import awkward as ak
import numpy as np
import numpy.typing as npt
import uproot
from analysis.helpers.cutflow import cutFlow
from base_class.awkward.zip import NanoAOD
from base_class.root import Chunk, TreeReader, TreeWriter, merge
from base_class.system.eos import EOS, PathLike
from base_class.utils.wrapper import retry
from coffea.processor import ProcessorABC

_PICOAOD = "picoAOD"
_ROOT = ".root"


class SkimmingError(Exception):
    __module__ = Exception.__module__


def _log_exception(e, *_):
    logging.error(f"The following exception occurred during skimming:", exc_info=e)
    return {}


def _clear_cache(events: ak.Array):
    # try to clear cached branches
    for cache in events.caches:
        cache.clear()
    gc.collect()


def _branch_filter(collections: Iterable[str], branches: Iterable[str]):
    branches = chain(
        map("({}_.*)".format, collections or ()),
        map("(n{})".format, collections or ()),
        map("({})".format, branches or ()),
    )
    return rf'^(?!({"|".join(branches)})$).*$'


class PicoAOD(ProcessorABC):
    def __init__(
        self,
        base_path: PathLike,
        step: int,
        skip_collections: Iterable[str] = None,
        skip_branches: Iterable[str] = None,
    ):
        self._base = EOS(base_path)
        self._step = step
        self._branch_filter = re.compile(
            _branch_filter(skip_collections, skip_branches)
        )
        self._transform = NanoAOD(regular=False, jagged=True)
        self.cutFlowCuts = []

    def _filter(self, branches: set[str]):
        return {*filter(self._branch_filter.match, branches)}

    @abstractmethod
    def select(
        self, events: ak.Array
    ) -> (
        npt.NDArray[np.bool_]
        | tuple[npt.NDArray[np.bool_], ak.Array]
        | tuple[npt.NDArray[np.bool_], ak.Array | None, dict]
    ):
        pass

    # no retry, return empty dict if any exception
    @retry(1, handler=_log_exception, skip=(SkimmingError,))
    def process(self, events: ak.Array):
        EOS.set_retry(3, 10)  # 3 retries with 10 seconds interval
        self._cutFlow = cutFlow(self.cutFlowCuts)
        selected = self.select(events)
        added, result = None, {}
        if isinstance(selected, tuple):
            if len(selected) >= 2:
                added = selected[1]
            if len(selected) >= 3:
                result = selected[2] or result
            selected = selected[0]
        chunk = Chunk.from_coffea_events(events)
        dataset = events.metadata["dataset"]

        # construct output
        result = {
            dataset: {
                "total_events": len(events),
                "saved_events": int(ak.sum(selected)),
                "files": [],
                "source": {str(chunk.path): [(chunk.entry_start, chunk.entry_stop)]},
            }
            | result
        }
        lumi = events.metadata.get("lumi", 1.0)
        xs = events.metadata.get("xs", 1.0)
        kFactor = events.metadata.get("kFactor", 1.0)
        self._cutFlow.addOutputSkim(result, dataset, lumi=lumi, xs=xs, kFactor=kFactor)

        # sanity check
        if (
            added is not None
            and (size := len(added)) != result[dataset]["saved_events"]
        ):
            raise SkimmingError(f"Length of additional branches ({size}) does not match the number of selected events ({result[dataset]['saved_events']})")
        # clear cache
        _clear_cache(events)
        # save selected events
        if result[dataset]["saved_events"] > 0:
            filename = f"{dataset}/{_PICOAOD}_{chunk.uuid}_{chunk.entry_start}_{chunk.entry_stop}{_ROOT}"
            path = self._base / filename
            reader = TreeReader(self._filter)
            saved = 0
            with TreeWriter()(path) as writer:
                for i, chunks in enumerate(
                    Chunk.partition(self._step, chunk, common_branches=True)
                ):
                    _selected = selected[i * self._step : (i + 1) * self._step]
                    _range = np.arange(len(_selected))[_selected]
                    if len(_range) == 0:
                        continue
                    _start, _stop = _range[0], _range[-1] + 1
                    _chunk = chunks[0].slice(_start, _stop)
                    _selected = _selected[_start:_stop]
                    data = reader.arrays(_chunk)[_selected]
                    if added is not None:
                        _saved = saved + ak.sum(_selected)
                        _added = added[saved:_saved]
                        for k in added.fields:
                            data[k] = _added[k]
                        saved = _saved
                    data = self._transform(data)
                    writer.extend(data)
            if writer.tree is not None:
                result[dataset]["files"].append(writer.tree)
        return result

    def postprocess(self, accumulator):
        pass


def _fetch_metadata(dataset: str, path: PathLike, dask: bool = False):
    try:
        with uproot.open(path) as f:
            if "genEventCount" in f["Runs"].keys():
                data = f["Runs"].arrays(
                    ["genEventCount", "genEventSumw", "genEventSumw2"]
                )
                return {
                    dataset: {
                        "count": float(ak.sum(data["genEventCount"])),
                        "sumw": float(ak.sum(data["genEventSumw"])),
                        "sumw2": float(ak.sum(data["genEventSumw2"])),
                    }
                }
            else:
                data = f["Events"].arrays(["event"])
                return {dataset: {"count": float(ak.num(data["event"], axis=0))}}
    except:
        return {dataset: {"bad_files": [str(EOS(path))]}}


def fetch_metadata(
    fileset: dict[str, dict[str, list[str]]], n_process: int = None, dask: bool = True
) -> list[dict[str, dict[str]]]:
    if not dask:
        with ProcessPoolExecutor(max_workers=n_process) as executor:
            tasks: list[Future] = []
            for dataset, files in fileset.items():
                for file in files["files"]:
                    tasks.append(
                        executor.submit(_fetch_metadata, dataset, file, dask=dask)
                    )
            results = [task.result() for task in tasks]
    else:
        from dask import delayed
        func = delayed(_fetch_metadata)
        results = []
        for dataset, files in fileset.items():
            for file in files["files"]:
                results.append(func(dataset, file, dask=dask))
    return results


def integrity_check(
    fileset: dict[str, dict[str, list[str]]],
    output: dict[str, dict[str, dict[str, list[tuple[int, int]]]]],
    num_entries: dict[str, dict[str, int]] = None,
):
    logging.info("Checking integrity of the picoAOD...")
    diff = set(fileset) - set(output)
    miss_dict = {}
    if diff:
        logging.error(f"The whole dataset is missing: {diff}")
        miss_dict["dataset_missing"] = "Run again :P"
    for dataset in fileset:
        if len(output[dataset]["files"]) == 0:
            logging.warning(f'No file is saved for "{dataset}"')
        inputs = map(EOS, fileset[dataset]["files"])
        outputs = {EOS(k): v for k, v in output[dataset]["source"].items()}
        ns = (
            None
            if num_entries is None
            else {EOS(k): v for k, v in num_entries[dataset].items()}
        )
        file_missing = []
        chunk_missing = []
        for file in inputs:
            if file not in outputs:
                logging.error(f'The whole file is missing: "{file}"')
                file_missing.append(str(file))
            else:
                chunks = sorted(outputs[file], key=lambda x: x[0])
                if ns is not None:
                    chunks.append((ns[file], ns[file]))
                merged = []
                start, stop = 0, 0
                for _start, _stop in chunks:
                    if _start != stop:
                        if start != stop:
                            merged.append([str(start), str(stop)])
                        start = _start
                        logging.error(f'Missing chunk: [{stop}, {_start}) in "{file}"')
                        chunk_missing.append(f'[{stop}, {_start}) in "{file}"')
                    stop = _stop
                if start != stop:
                    merged.append([start, stop])
        if file_missing:
            miss_dict["file_missing"] = file_missing
        if chunk_missing:
            miss_dict["chunk_missing"] = chunk_missing
    output[dataset].pop("source")
    output[dataset]["missing"] = miss_dict
    return output


def resize(
    base_path: PathLike,
    output: dict[str, dict[str, list[Chunk]]],
    step: int,
    chunk_size: int,
    dask: bool = True
):
    base = EOS(base_path)
    transform = NanoAOD(regular=False, jagged=True)
    for dataset, chunks in output.items():
        if len(chunks["files"]) > 0:
            output[dataset]["files"] = merge.resize(
                base / dataset / f"{_PICOAOD}{_ROOT}",
                *chunks["files"],
                step=step,
                chunk_size=chunk_size,
                reader_options={"transform": transform},
                dask=dask,
            )
    return output
