from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

import awkward as ak
import base_class.dask.awkward as dakext
import dask_awkward as dak
import numpy as np
from base_class.dask.hist import Collection, Fill, Template
from base_class.physics.object import Jet

from ._utils import selection_to_label


# NOTE: add plots here
class BasicHists(Template):
    canjets = Jet.plot(("canjets", "Boson Candidate Jets"), "CanJets")
    othjets = Jet.plot(("othjets", "Other Jets"), "NotCanJets")


@dataclass
class BasicPlot:
    tags: Iterable[str] = ("threeTag", "fourTag")
    regions: Iterable[str] = ("SR", "SB")
    cutflows: Iterable[str] = ()
    JCM: Callable[[dak.Array], dak.Array] = None
    signals: Iterable[str] = ("ggF", "ZZ", "ZH")
    unblind: bool = False

    def __call__(self, events: dak.Array):
        process = events.metadata["process"]
        year = events.metadata["year"]

        inputs = events.HCR_input
        selection = (inputs.SR | inputs.SB) & (inputs.threeTag | inputs.fourTag)
        if process == "data" and not self.unblind:
            selection = selection & (inputs.SB | inputs.threeTag)
        events = events[selection]
        events = self.rename(events, "HCR_input")

        hists = Collection(
            process=[process],
            year=[year],
            tag=list(self.tags),
            region=list(self.regions),
            category=[*self.signals, "failed"],
            **{cut: ... for cut in self.cutflows},
        )
        SvBs = [k for k in events.fields if k.startswith("SvB")]
        FvTs = [k for k in events.fields if k.startswith("FvT")]

        inputs = events.HCR_input  # need to reassign
        if process == "data":
            weights = self.reweight_FvT(
                inputs.weight,
                inputs.threeTag,
                None if self.JCM is None else self.JCM(inputs.nSelJets),
                **{f: events[f].FvT for f in FvTs},
            )
            events_3b = events[inputs.threeTag]
            weights_3b = weights[inputs.threeTag]
            multijets = {
                k: f"Multijet{k.removeprefix('FvT')}"
                for k in weights_3b.fields
                if k != "weight"
            }
        else:
            weights = dak.zip({"weight": inputs.weight})

        for SvB in SvBs:
            SvB_score = self.category_SvB(events[SvB])
            SvB_name = SvB.replace("_", " ")
            fill = Fill(year=year)
            fill += hists.add(f"{SvB}.score", (100, 0, 1, ("svb_score", SvB_name)))
            fill += BasicHists((SvB, f"Categorized by {SvB_name}, "), ())
            fill(
                events,
                process=process,
                category=SvB_score.category,
                svb_score=SvB_score.score,
                weight=weights.weight,
            )
            if process == "data":
                SvB_score_3b = SvB_score[inputs.threeTag]
                for multijet_field, multijet_process in multijets.items():
                    fill(
                        events_3b,
                        tag="fourTag",  # interpret reweighted 3b-data as 4b-multijet
                        process=multijet_process,
                        category=SvB_score_3b.category,
                        svb_score=SvB_score_3b.score,
                        weight=weights_3b[multijet_field],
                    )
        return {"hists": hists.to_dict(True)}

    @dakext.partition_mapping  # force a single node
    def rename(self, events: ak.Array, friend_tree: str):
        nevents = dakext.safe.len(events)
        stored = events[friend_tree]
        events["weight"] = stored.weight
        events["tag"] = selection_to_label(
            {tag: dakext.safe.to_numpy(stored[tag]) for tag in self.tags},
            nevents,
        )
        events["region"] = selection_to_label(
            {region: dakext.safe.to_numpy(stored[region]) for region in self.regions},
            nevents,
        )
        events["CanJets"] = ak.zip(
            {
                "pt": stored.CanJet_pt,
                "eta": stored.CanJet_eta,
                "phi": stored.CanJet_phi,
                "mass": stored.CanJet_mass,
            },
            with_name="PtEtaPhiMLorentzVector",
        )
        events["NotCanJets"] = ak.zip(
            {
                "pt": stored.NotCanJet_pt,
                "eta": stored.NotCanJet_eta,
                "phi": stored.NotCanJet_phi,
                "mass": stored.NotCanJet_mass,
            },
            with_name="PtEtaPhiMLorentzVector",
        )

        for cut in self.cutflows:
            events[cut] = stored[cut]

        return events

    @dakext.partition_mapping
    def reweight_FvT(
        self, weight: ak.Array, b3: ak.Array, jcm: Optional[ak.Array], **kwargs
    ):
        raw = weight.to_numpy()
        weights = {"weight": weight}
        if jcm is not None:  # apply JCM
            raw = raw.copy()
            raw[b3] *= jcm.to_numpy()[b3]
            weights["FvT_JCM"] = raw
        for k, v in kwargs.items():  # apply FvT
            reweight = raw.copy()
            reweight[b3] *= v.to_numpy()[b3]
            weights[k] = reweight
        return ak.zip(weights)

    @reweight_FvT.typetracer  # bypass numpy operations incompatible with typetracer
    def __reweight_FvT_typetracer(self, weight, b3, jcm, **kwargs):
        dakext.safe.to_numpy(b3)  # touch buffers
        weights = {"weight": weight, **kwargs}
        if jcm is not None:
            weights["FvT_JCM"] = jcm
        return ak.zip(weights)

    @dakext.partition_mapping
    def category_SvB(self, scores: ak.Array):
        stacked = np.stack(list(scores[f"p_{k}"].to_numpy() for k in self.signals))
        max_idx = np.argmax(stacked, axis=0)
        max_val = np.take_along_axis(stacked, max_idx[None, :], axis=0).squeeze()
        max_idx[max_val <= 0.01] = len(self.signals)
        category = np.array([*self.signals, "failed"])[max_idx]
        return ak.zip({"category": category, "score": scores.p_sig})

    @category_SvB.typetracer
    def __category_SvB_typetracer(self, scores):
        for k in (*(f"p_{k}" for k in self.signals), "p_sig"):
            dakext.safe.to_numpy(scores[k])  # touch buffers
        return ak.zip({"category": ["failed"], "score": [0.0]})
