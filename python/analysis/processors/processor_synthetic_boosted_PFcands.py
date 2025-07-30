import time
import awkward as ak
import numpy as np
import yaml
import warnings

from coffea.nanoevents import NanoAODSchema
from coffea import processor
from coffea.analysis_tools import PackedSelection
import hist

from analysis.helpers.event_selection import apply_event_selection
from base_class.hist import Collection, Fill
from jet_clustering.clustering_hist_templates import ClusterHistsBoosted
from base_class.physics.object import Jet, PFCand

from jet_clustering.declustering import compute_decluster_variables

import logging
import vector

#
# Setup
#
NanoAODSchema.warn_missing_crossrefs = False
warnings.filterwarnings("ignore")


class analysis(processor.ProcessorABC):
    def __init__(
            self,
            *,
            corrections_metadata="analysis/metadata/corrections.yml",
            **kwargs
    ):

        logging.debug("\nInitialize Analysis Processor")
        self.corrections_metadata = yaml.safe_load(open(corrections_metadata, "r"))

    def process(self, event):

        ### Some useful variables
        tstart = time.time()
        fname   = event.metadata['filename']
        year    = event.metadata['year']
        dataset = event.metadata['dataset']
        processName = event.metadata['processName']
        isMC    = True if event.run[0] == 1 else False
        nEvent = len(event)

        logging.info(fname)
        logging.info(f'Process {nEvent} Events')

        #
        # Event selection
        #
        event = apply_event_selection( event,
                                        self.corrections_metadata[year],
                                        cut_on_lumimask=True
                                        )



        selFatJet = event.FatJet[event.FatJet.pt > 300]
        #selFatJet = selFatJet[selFatJet.particleNetMD_Xbb > 0.8]
        selFatJet = selFatJet[selFatJet.subJetIdx1 >= 0]
        selFatJet = selFatJet[selFatJet.subJetIdx2 >= 0]

        selFatJet = selFatJet[(selFatJet.subjets [:, :, 0] + selFatJet.subjets [:, :, 1]).mass > 50]
        #selFatJet = selFatJet[ak.num(selFatJet.subjets, axis=2) > 1]



        #print(f" fields FatJets: {selFatJet.fields}")
        #print(f" fields nSubJets: {selFatJet.subjets.fields}")
        #print(f" nSubJets: {ak.num(selFatJet.subjets, axis=1)}")

        #selFatJet = selFatJet[ak.num(selFatJet.subjets) > 1]
        event["selFatJet"] = selFatJet


        #  Cehck How often do we have >=2 Fat Jets?
        event["passNFatJets"]  = (ak.num(event.selFatJet) == 2)








        # Apply object selection (function does not remove events, adds content to objects)

        selections = PackedSelection()
        selections.add( "lumimask", event.lumimask)
        selections.add( "passNoiseFilter", event.passNoiseFilter)
        selections.add( "passHLT", ( np.full(len(event), True) if isMC else event.passHLT ) )
        selections.add( "passNFatJets",  event.passNFatJets )
        ### add more selections, this can be useful


        #list_of_cuts = [ "lumimask", "passNoiseFilter", "passHLT", "passNFatJets" ]
        list_of_cuts = [ "passNFatJets" ]
        analysis_selections = selections.all(*list_of_cuts)
        selev = event[analysis_selections]

        #
        # Event selection
        #
        print(f"Number of FatJet PFCands: {ak.num(selev.FatJetPFCands)}\n")
        print(f"   event fields: {selev.fields}\n")
        print(f"   FatJet PFCands pt 0: {selev.FatJetPFCands.pt[0].tolist()}\n")
        print(f"   FatJet PFCands pfCandIdx 0: {selev.FatJetPFCands.pFCandsIdx[0].tolist()}\n")
        print(f"   FatJet PFCands jetIdx 0: {selev.FatJetPFCands.jetIdx[0].tolist()}\n")
        print(f"FatJet PFCands fields: {selev.FatJetPFCands.fields}\n")
        print(f"FatJet Fat Jet fields: {selev.FatJet.fields}\n")
        print(f"FatJet FatJet dir: {dir(selev.FatJet)}\n")
        print(f"PFCand fields: {selev.PFCands.fields}\n")

        print(f"FatJet index {ak.local_index(selev.FatJet, axis=1)}\n")
        print(f"FatJet index0 {ak.local_index(selev.FatJet, axis=1)[:,0]}\n")
        print(f"FatJet index1 {ak.local_index(selev.FatJet, axis=1)[:,1]}\n")

        PFCandFatJet0_mask = selev.FatJetPFCands.jetIdx == ak.local_index(selev.FatJet, axis=1)[:,0]
        PFCandFatJet1_mask = selev.FatJetPFCands.jetIdx == ak.local_index(selev.FatJet, axis=1)[:,1]

        PFCandIndex_FatJet0 = selev.FatJetPFCands[PFCandFatJet0_mask].pFCandsIdx
        PFCandIndex_FatJet1 = selev.FatJetPFCands[PFCandFatJet1_mask].pFCandsIdx

        print(f" nPFCands for FatJet0 {ak.num(PFCandIndex_FatJet0)}\n")


        print(f" PFCands for FatJet0 {selev.PFCands[PFCandIndex_FatJet0].pdgId.tolist()}\n")
        #print(f" PFCands for FatJet1 {selev.FatJetPFCands[PFCandFatJet1_mask].pFCandsIdx.tolist()}\n")

        print(type(selev.selFatJet),"\n")
        selev["selFatJet_PFCand0"] = selev.PFCands[PFCandIndex_FatJet0]
        selev["selFatJet_PFCand1"] = selev.PFCands[PFCandIndex_FatJet1]

        #print(f" PFCands for FatJet1 {selev.FatJetPFCands[PFCandFatJet1_mask].pFCandsIdx.tolist()}\n")
        #print(f"   FatJet PFCands jetIdx 0: {selev.FatJetPFCands.jetIdx[0].tolist()}\n")

        #print(f"Number of selected Fat Jets: {ak.num(selev.selFatJet)}")
        #print(f" Any passNFatJets: {ak.any(selev.passNFatJets)}")
        #print(f" Any passHLT: {ak.any(selev.passHLT)}")
        #print(f" FatJet pt: {selev.selFatJet.pt}")
        #
        #print(f" nSubJets: {ak.num(selev.selFatJet.subjets, axis=2)}")
        #print(f" subjet pt: {selev.selFatJet.pt[0:10]}")


        # Hacking the tag variable
        selev["fourTag"] = True
        selev['tag'] = ak.zip({
            "fourTag": selev.fourTag,
        })


        # Hack the region varable
        selev["SR"] = True
        selev["region"] = ak.zip({
            "SR": selev.SR,
        })

        selev["weight"] = 1.0



        fill = Fill(process=processName, year=year, weight="weight")
        histCuts = ["passNFatJets"]

        hist = Collection( process=[processName],
                           year=[year],
                           tag=["fourTag"],  # 3 / 4/ Other
                           region=['SR'],  # SR / SB / Other
                           **dict((s, ...) for s in histCuts)
                           )


        #
        # Jets
        #
        selev["selFatJet", "btagScore"] = selev.selFatJet.particleNet_XbbVsQCD
        fill += Jet.plot(("fatJets", "Selected Fat Jets"),        "selFatJet",           skip=["deepjet_c"], bins={"pt": (50, 0, 1000)})

        #trkPt
        #print("fields",selev["selFatJet_PFCand0"].fields,"\n")
        fill += PFCand.plot(("PFCand0", "PFCands in Selected Fat Jet0"),        "selFatJet_PFCand0",           skip=[],
                            bins={"pt":   (50, 0, 10), "mass": (50, 0, 0.2)}
                            )

        #fill += hist.add( "PFCand0.pt_l",  (100, 0, 100, ("selFatJet_PFCand0.trkPt",   'trk pt')))
        #fill += hist.add( "PFCand0.pt",    (100, 0, 10,  ("selFatJet_PFCand0.trkPt",   'trk pt')))

#        for _s_type in cleaned_splitting_name:

        #
        # fill histograms
        #
        fill(selev, hist)

        processOutput = {}

        output = hist.output | processOutput

        return output

    def postprocess(self, accumulator):
        return accumulator
