from coffea4bees.classifier.nn.schedule import Schedule
from coffea4bees.classifier.utils import NOOP, noop


class _SkimBS(NOOP):
    def __init__(self, dataset):
        from coffea4bees.classifier.nn.dataset import skim_loader

        self.dataloader = skim_loader(dataset, shuffle=False, drop_last=False)


class SkimStep(Schedule):
    epoch: int = 1

    def optimizer(cls, _, **__):
        return noop

    def lr_scheduler(self, _, **__):
        return noop

    def bs_scheduler(self, dataset, **__):
        return _SkimBS(dataset)


class BenchmarkStep(SkimStep):
    def bs_scheduler(self, _, **__):
        return noop
