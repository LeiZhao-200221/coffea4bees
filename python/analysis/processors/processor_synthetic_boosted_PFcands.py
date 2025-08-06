import time
import awkward as ak
import numpy as np
import yaml
import warnings
from collections import OrderedDict
from base_class.hist import Template

from coffea.nanoevents import NanoAODSchema
from coffea import processor
from coffea.analysis_tools import PackedSelection
import hist
from analysis.helpers.cutflow import cutFlow

from analysis.helpers.event_selection import apply_event_selection
from base_class.hist import Collection, Fill
from jet_clustering.clustering_hist_templates import ClusterHistsBoosted
from base_class.physics.object import LorentzVector, Jet, PFCand

from jet_clustering.declustering import compute_decluster_variables
from jet_clustering.clustering import comb_jet_flavor

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


        selFatJet = event.FatJet
        #selFatJet = selFatJet[selFatJet.particleNetMD_Xbb > 0.8]
        selFatJet = selFatJet[selFatJet.subJetIdx1 >= 0]
        selFatJet = selFatJet[selFatJet.subJetIdx2 >= 0]

        selFatJet = event.FatJet[event.FatJet.pt > 300]

        selFatJet = selFatJet[(selFatJet.subjets [:, :, 0] + selFatJet.subjets [:, :, 1]).pt   > 300]
        selFatJet = selFatJet[(selFatJet.subjets [:, :, 0] + selFatJet.subjets [:, :, 1]).mass > 50]

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

        event["weight"] = 1.0


        #
        # Do the cutflow
        #
        sel_dict = OrderedDict({
            'all'               : selections.require(lumimask=True),
            'passNoiseFilter'   : selections.require(lumimask=True, passNoiseFilter=True),
            'passHLT'           : selections.require(lumimask=True, passNoiseFilter=True, passHLT=True),
            'passNFatJets'      : selections.require(lumimask=True, passNoiseFilter=True, passHLT=True, passNFatJets=True),
        })
        #sel_dict['passJetMult'] = selections.all(*allcuts)

        self.cutFlow = cutFlow()
        for cut, sel in sel_dict.items():
            self.cutFlow.fill( cut, event[sel], allTag=True )


        list_of_cuts = [ "lumimask", "passNoiseFilter", "passHLT", "passNFatJets" ]
        #list_of_cuts = [ "passNFatJets" ]
        analysis_selections = selections.all(*list_of_cuts)
        selev = event[analysis_selections]


        #
        #  Create the subjets
        #
        sorted_sub_jets = selev.selFatJet.subjets
        sorted_sub_jets = sorted_sub_jets[ak.argsort(sorted_sub_jets.pt, axis=2, ascending=False)]

        if "tau1" not in sorted_sub_jets.fields:
            # If the subjets do not have tau1, tau2, tau3, we need to add them
            sorted_sub_jets = ak.with_field(sorted_sub_jets, sorted_sub_jets.pt, "tau1")
            sorted_sub_jets = ak.with_field(sorted_sub_jets, sorted_sub_jets.pt, "tau2")
            sorted_sub_jets = ak.with_field(sorted_sub_jets, sorted_sub_jets.pt, "tau3")


        subjets = ak.zip({"p"  : sorted_sub_jets[:, :, 0] + sorted_sub_jets[:, :, 1],
                          "i0" : sorted_sub_jets[:, :, 0],
                          "i1" : sorted_sub_jets[:, :, 1],
                          } )

        # Calculate di-jet variables
        subjets["p", "st"]   = subjets.i0.pt + subjets.i1.pt
        subjets["p", "dr"]   = subjets.i0.delta_r(subjets.i1)
        subjets["p", "dphi"] = subjets.i0.delta_phi(subjets.i1)


        # Define the tau21 variable for each subjet
        subjets["i0", "tau21"] = subjets.i0.tau2 / (subjets.i0.tau1 + 0.001)
        subjets["i1", "tau21"] = subjets.i1.tau2 / (subjets.i1.tau1 + 0.001)

        subjets["i0", "tau32"] = subjets.i0.tau3 / (subjets.i0.tau2 + 0.001)
        subjets["i1", "tau32"] = subjets.i1.tau3 / (subjets.i1.tau2 + 0.001)

        # Dummy
        subjets["i0", "btag_string"] = "0.001"
        subjets["i1", "btag_string"] = "0.001"


        # Define the jet flavor for each subjet
        subjets["i0", "jet_flavor"] = ak.where(subjets.i0.tau21 > 0.5, "b", "bj")
        subjets["i1", "jet_flavor"] = ak.where(subjets.i1.tau21 > 0.5, "b", "bj")

        # Swap if i1 more complex than i0
        i1_more_complex = (subjets.i1.jet_flavor == "bj") & (subjets.i0.jet_flavor == "b")

        subjets["iA"] = ak.where(i1_more_complex, subjets.i1, subjets.i0)
        subjets["iB"] = ak.where(i1_more_complex, subjets.i0, subjets.i1)

        # print(f"Subjets: {subjets.fields}")
        # print(f"  iA flavor: {subjets.iA.jet_flavor[0:10]}")
        # print(f"  iB flavor: {subjets.iA.jet_flavor[0:10]}")

        #
        #  Set the jet flavor for the combined fat jet
        #
        C = [comb_jet_flavor(a, b) for a, b in zip(ak.flatten(subjets.iA.jet_flavor), ak.flatten(subjets.iB.jet_flavor))]
        fatjet_flavor_flat = np.array(C)
        selev["selFatJet", "jet_flavor"] = ak.unflatten(fatjet_flavor_flat, ak.num(selev.selFatJet))



        #
        #  Printouts to understand the structure of the PFCands
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
        print(f" nPFCands for FatJet1 {ak.num(PFCandIndex_FatJet1)}\n")

        print(f" PFCands for FatJet0 {selev.PFCands[PFCandIndex_FatJet0].pdgId.tolist()}\n")
        print(f" PFCands for FatJet1 {selev.PFCands[PFCandIndex_FatJet1].pdgId.tolist()}\n")
        #print(f" PFCands for FatJet1 {selev.FatJetPFCands[PFCandFatJet1_mask].pFCandsIdx.tolist()}\n")

        print(type(selev.selFatJet),"\n")
        #subjets["PFCand0"] = selev.PFCands[PFCandIndex_FatJet0]
        #subjets["PFCand1"] = selev.PFCands[PFCandIndex_FatJet1]
        selev["selFatJet_PFCand0"] = selev.PFCands[PFCandIndex_FatJet0]

###        #
###        # Probably a better way to do this....
###        #   (Testing the following)
###        # Add the PF Cands for each FatJet
###        PFCands_test1 = ak.concatenate([selev.PFCands[PFCandIndex_FatJet0], selev.PFCands[PFCandIndex_FatJet1]], axis=1)
###        print(f" nPFCands1  {ak.num(PFCands_test1)}\n")
###        print(f" nPFCands1  {PFCands_test1.pdgId.tolist()}\n")
###
###        PFCands_test0 = ak.concatenate([selev.PFCands[PFCandIndex_FatJet0], selev.PFCands[PFCandIndex_FatJet1]], axis=0)
###        print(f" nPFCands0  {ak.num(PFCands_test0)}\n")
###        print(f" nPFCands0 {PFCands_test0.pdgId.tolist()}\n")
###
###        PFCands_testZ = ak.unflatten(ak.concatenate([selev.PFCands[PFCandIndex_FatJet0], selev.PFCands[PFCandIndex_FatJet1]]), 2)
###
###        print(f" nPFCandsZ  {ak.num(PFCands_testZ)}\n")
###        print(f" nPFCandsZ {PFCands_testZ.pdgId.tolist()}\n")


        #
        #  Add the subjets to the event
        #
        selev["subjets"] = subjets


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



        #
        #  Class to plot the Fat Jets
        #
        class FatJetHists(Template):

            p  = LorentzVector.plot_pair(('...', R'Fat Jet'), 'p',  skip=['n'], bins={"mass": (100, 40, 300),
                                                                                      "pt": (60, 250, 1000),
                                                                                      "dr": (50, 0, 1.2),
                                                                                      "dphi": (50, -1.5, 1.5)
                                                                                      })

            i0 = Jet.plot(('...', R'subjet 0'), 'i0',     skip=['deepjet_c','n'], bins={"mass": (100, 0, 200), "pt": (50, 100, 1000)})
            i1 = Jet.plot(('...', R'subjet 1'), 'i1',     skip=['deepjet_c','n'], bins={"mass": (50, 0, 100)})


        fill += PFCand.plot(("PFCand0", "PFCands in Selected Fat Jet0"),        "selFatJet_PFCand0",           skip=[],
                            bins={"pt":   (50, 0, 10), "mass": (50, 0, 0.2)}
                            )


        fill += FatJetHists(('fatJets', R''), 'subjets')
        #trkPt
        #print("fields",selev["selFatJet_PFCand0"].fields,"\n")

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
