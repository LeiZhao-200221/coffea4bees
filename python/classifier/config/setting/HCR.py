from enum import IntEnum

from classifier.task import Cascade


class InputBranch(Cascade):
    feature_CanJet: list[str] = ["pt", "eta", "phi", "mass"]
    feature_NotCanJet: list[str] = feature_CanJet + ["isSelJet"]
    feature_ancillary: list[str] = ["nSelJets", "year", "xbW", "xW"]
    n_CanJet: int = 4
    n_NotCanJet: int = 8

    @classmethod
    def get__feature_CanJet(cls, var: list[str]):
        return [f"CanJet_{f}" for f in var]

    @classmethod
    def get__feature_NotCanJet(cls, var: list[str]):
        return [f"NotCanJet_{f}" for f in var]

    @classmethod
    def get__feature_ancillary(cls, var: list[str]):
        return var.copy()


class Input(Cascade):
    label: str = "label"
    region: str = "region"
    weight: str = "weight"
    ancillary: str = "ancillary"
    CanJet: str = "CanJet"
    NotCanJet: str = "NotCanJet"


class Output(Cascade):
    class_raw: str = "class_raw"
    class_prob: str = "class_prob"
    quadjet_raw: str = "quadjet_raw"
    quadjet_prob: str = "quadjet_prob"


class MassRegion(IntEnum):
    SB = 0b10
    ZZSR = 0b0101
    ZHSR = 0b1001
    HHSR = 0b1101
    SR = 0b01


class NTag(IntEnum):
    fourTag = 0b10
    threeTag = 0b01
