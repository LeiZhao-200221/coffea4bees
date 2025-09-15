from __future__ import annotations

from typing import TYPE_CHECKING

from coffea4bees.classifier.config.setting.HCR import Input
from coffea4bees.classifier.config.state.label import MultiClass
from coffea4bees.classifier.task import ArgParser

from . import _remove_sig

if TYPE_CHECKING:
    from coffea4bees.classifier.ml import BatchType


class _keep_ZX:
    def __call__(self, batch: BatchType):
        import torch

        label = batch[Input.label]
        return torch.isin(
            label,
            label.new_tensor(MultiClass.indices("ZZ", "ZH", "multijet", "ttbar")),
        )


class Train(_remove_sig.Train):
    model = "SvB_ggF-ZX-only"
    argparser = ArgParser(description="Train SvB only with ZZ and ZH.")

    def remover(self):
        return _keep_ZX()
