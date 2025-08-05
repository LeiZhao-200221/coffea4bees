import time
import awkward as ak
import numpy as np
import yaml
import warnings
from collections import OrderedDict

from coffea.nanoevents import NanoAODSchema
from coffea import processor
from coffea.analysis_tools import PackedSelection
import hist
from analysis.helpers.cutflow import cutFlow

from analysis.helpers.event_selection import apply_event_selection
from base_class.hist import Collection, Fill
from jet_clustering.clustering_hist_templates import ClusterHistsBoosted, ClusterHistsDetailedBoosted
from base_class.physics.object import Jet

from jet_clustering.declustering import compute_decluster_variables, get_splitting_name, get_list_of_combined_jet_types, get_list_of_all_sub_splittings
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
        estart  = event.metadata['entrystart']
        estop   = event.metadata['entrystop']
        chunk   = f'{dataset}::{estart:6d}:{estop:6d} >>> '
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
                                        cut_on_lumimask=(not isMC),
                                        )

        selFatJet = event.FatJet
        selFatJet = selFatJet[selFatJet.particleNetMD_Xbb > 0.8]
        selFatJet = selFatJet[selFatJet.subJetIdx1 >= 0]
        selFatJet = selFatJet[selFatJet.subJetIdx2 >= 0]



        # Hack for synthetic data
        selFatJet = selFatJet[selFatJet.subJetIdx1 < 4]
        selFatJet = selFatJet[selFatJet.subJetIdx2 < 4]

        selFatJet = selFatJet[(selFatJet.subjets [:, :, 0] + selFatJet.subjets [:, :, 1]).pt > 300]
        selFatJet = selFatJet[(selFatJet.subjets [:, :, 0] + selFatJet.subjets [:, :, 1]).mass > 50]


        #print(f" fields nSubJets: {ak.num(selFatJet.subjets)},\n")

        #selFatJet = selFatJet[ak.num(selFatJet.subjets) > 1]
        event["selFatJet"] = selFatJet


        #  Check How often do we have >=2 Fat Jets?
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
        analysis_selections = selections.all(*list_of_cuts)
        selev = event[analysis_selections]

        #
        # Event selection
        #
        #

        #
        #  Compute Soft drop
        #
        selev["selFatJet","subjetmass"] = (selev.selFatJet.subjets[:,:,0] + selev.selFatJet.subjets[:,:,1]).mass

        selev["selFatJet","subjetdr"]    = (selev.selFatJet.subjets[:,:,0].delta_r(selev.selFatJet.subjets[:,:,1]))
        selev["selFatJet","subjetpt0"]   = (selev.selFatJet.subjets[:,:,0].pt)
        selev["selFatJet","subjetpt1"]   = (selev.selFatJet.subjets[:,:,1].pt)


        # print( "softdrop mass",selev[0:5].selFatJet.msoftdrop.tolist(),"\n")
        # print( "subjet mass",selev[0:5].selFatJet.subjetmass.tolist(),"\n")
        #print( "subjet pt0",selev[0:5].selFatJet.subjets[:,:,0].pt.tolist(),"\n")
        #print( "subjet pt1",selev[0:5].selFatJet.subjets[:,:,1].pt.tolist(),"\n")

        #
        # Adding btag and jet flavor to fat jets
        #
        particleNet_HbbvsQCD_flat = ak.flatten(selev.selFatJet.particleNet_HbbvsQCD)
        particleNet_HbbvsQCD_flat_str = [ str(round(v,3)) for v in particleNet_HbbvsQCD_flat ]
        #selev["selFatJet", "btag_string"] = ak.unflatten(particleNet_HbbvsQCD_flat_str, ak.num(selev.selFatJet))


        indices = []
        indices_str = []
        for arr in selev.selFatJet.pt:
            indices_str.append( [f"({i},{i})" for i in range(len(arr))] )
            indices.append(list(range(len(arr))))

        selev["selFatJet", "btag_string"] = indices_str
        selev["selFatJet", "btagScore"] = selev.selFatJet.particleNetMD_Xbb

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


        subjets = ak.zip({"i0" : sorted_sub_jets[:, :, 0],
                          "i1" : sorted_sub_jets[:, :, 1],
                          } )

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

        # print(f" Combined:{selev.selFatJet.jet_flavor[0:10]}")
        # print(f" \tpartA:{subjets.iA.jet_flavor[0:10]}")
        # print(f" \tpartB:{subjets.iB.jet_flavor[0:10]}")

        #
        # Create the splittings
        #
        fat_jet_splittings_events = ak.zip(
            {
                "pt":   (subjets.iA + subjets.iB).pt  ,
                "eta":  (subjets.iA + subjets.iB).eta ,
                "phi":  (subjets.iA + subjets.iB).phi ,
                "mass": (subjets.iA + subjets.iB).mass,
                "jet_flavor": selev.selFatJet.jet_flavor,
                "btag_string": selev.selFatJet.btag_string,

                "part_A": ak.zip(
                    {
                        "pt":          subjets.iA.pt,
                        "eta":         subjets.iA.eta,
                        "phi":         subjets.iA.phi,
                        "mass":        subjets.iA.mass,
                        "jet_flavor":  subjets.iA.jet_flavor,
                        "btag_string": subjets.iA.btag_string,
                        "tau21":       subjets.iA.tau21,
                        "tau32":       subjets.iA.tau32,
                    },
                    with_name="PtEtaPhiMLorentzVector",
                    behavior=vector.backends.awkward.behavior
                ),

                "part_B": ak.zip(
                    {
                        "pt":          subjets.iB.pt,
                        "eta":         subjets.iB.eta,
                        "phi":         subjets.iB.phi,
                        "mass":        subjets.iB.mass,
                        "jet_flavor":  subjets.iB.jet_flavor,
                        "btag_string": subjets.iB.btag_string,
                        "tau21":       subjets.iB.tau21,
                        "tau32":       subjets.iB.tau32,
                    },
                    with_name="PtEtaPhiMLorentzVector",
                    behavior=vector.backends.awkward.behavior
                ),
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.backends.awkward.behavior
        )

        #
        # Compute the declustering variables
        #
        compute_decluster_variables(fat_jet_splittings_events)

        #
        # Assign the splitting names
        #
        split_name_flat = [get_splitting_name(str(i)) for i in ak.flatten(fat_jet_splittings_events.jet_flavor)]
        split_name = ak.unflatten(split_name_flat, ak.num(fat_jet_splittings_events))
        fat_jet_splittings_events["splitting_name"] = split_name

        #
        # Get list of all the splitting types
        #
        cleaned_combined_jet_flavors = get_list_of_combined_jet_types(fat_jet_splittings_events)
        cleaned_split_jet_flavors = []
        for _s in cleaned_combined_jet_flavors:
            cleaned_split_jet_flavors += get_list_of_all_sub_splittings(_s)

        cleaned_splitting_name = [get_splitting_name(i) for i in cleaned_split_jet_flavors]
        cleaned_splitting_name = set(cleaned_splitting_name)
        # will not split 1b0j/0b1j

        if "1b0j/0b1j" in cleaned_splitting_name:
            cleaned_splitting_name.remove("1b0j/0b1j")

        # print(f"cleaned splitting types: {cleaned_splitting_name}")

        #
        # Sort clusterings by type
        #
        for _s_type in cleaned_splitting_name:
            selev[f"splitting_{_s_type}"]   = fat_jet_splittings_events[fat_jet_splittings_events.splitting_name == _s_type]



        fat_jet_splittings_events_low_mass = fat_jet_splittings_events[fat_jet_splittings_events.mass_AB < 75.0]
        selev["splitting_1b0j/1b0j_lowMass"]   = fat_jet_splittings_events_low_mass

        fat_jet_splittings_events_mid_mass = fat_jet_splittings_events[(fat_jet_splittings_events.mass_AB > 75.0) & (fat_jet_splittings_events.mass_AB < 200.0)]
        selev["splitting_1b0j/1b0j_midMass"]   = fat_jet_splittings_events_mid_mass

        fat_jet_splittings_events_high_mass = fat_jet_splittings_events[fat_jet_splittings_events.mass_AB > 200.0]
        selev["splitting_1b0j/1b0j_highMass"]   = fat_jet_splittings_events_high_mass


        dr_partA = selev["splitting_1b0j/1b0j"].delta_r(selev["splitting_1b0j/1b0j"].part_A)
        bad_match_A = ak.any(dr_partA > 1.0, axis=1)

        dr_partB = selev["splitting_1b0j/1b0j"].delta_r(selev["splitting_1b0j/1b0j"].part_B)
        bad_match_B = ak.any(dr_partB > 1.0, axis=1)

        bad_match_flag = bad_match_A | bad_match_B


        if ak.sum(bad_match_flag) > 0:

            print(f"Found {ak.sum(bad_match_flag)} bad matches in {len(selev['splitting_1b0j/1b0j'])} events")

            bad_splitting = selev["splitting_1b0j/1b0j"][bad_match_flag]
            badFatJet  = selev.selFatJet[bad_match_flag]
            dr_partA = dr_partA[bad_match_flag]
            dr_partB = dr_partB[bad_match_flag]

            print("zA",bad_splitting.zA.tolist()[0:10],"\n")
            #print("zA_num",selev["splitting_1b0j/1b0j"].zA_num.tolist(),"\n")
            print("fatJets\n\t  pt",badFatJet.pt,"\n\t subjetIdx1",badFatJet.subJetIdx1, "\n\t subjetIdx1",badFatJet.subJetIdx2,"\n")
            print("comb\n\t     pt:",bad_splitting.pt[0:10],        "\n\t eta:", bad_splitting.eta[0:10], "\n\t phi:", bad_splitting.phi[0:10],"\n")
            print("\tpart A\n\t pt:",bad_splitting.part_A.pt[0:10], "\n\t eta:", bad_splitting.part_A.eta[0:10], "\n\t phi:", bad_splitting.part_A.phi[0:10],"\n\t dr:", dr_partA.tolist()[0:10],"\n")
            print("\tpart B\n\t pt:",bad_splitting.part_B.pt[0:10], "\n\t eta:", bad_splitting.part_B.eta[0:10], "\n\t phi:", bad_splitting.part_B.phi[0:10],"\n\t dr:", dr_partB.tolist()[0:10],"\n")



        #
        # Better Hists
        #

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

        #selev.sel



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
        fill += Jet.plot(("fatJets", "Selected Fat Jets"),        "selFatJet",           skip=["deepjet_c"], bins={"pt": (50, 0, 1000)})

        #                 "Histogram Name", (nBins, min, max, (variable (selev.variable), title) )
        fill += hist.add( "msoftdrop",  (100, 40, 400, ("selFatJet.msoftdrop",   'Soft Drop Mass')))

        fill += hist.add( "msubjet",    (100, 40, 400, ("selFatJet.subjetmass",  'Sub Jet Mass')))
        fill += hist.add( "subjetdr",   (100, 0, 1.0, ("selFatJet.subjetdr",    'Sub Jet Delta R')))

        fill += hist.add( "subjet0.pt",  (100, 0, 400, ("selFatJet.subjetpt0",   'Sub Jet0 Pt')))
        fill += hist.add( "subjet1.pt",  (100, 0, 400, ("selFatJet.subjetpt1",   'Sub Jet1 Pt')))

        #fill += hist.add( "subjet0.tau21",  (100, 0, 400, ("selFatJet.subjetpt0",   'Sub Jet0 Pt')))
        #fill += hist.add( "subjet1.tau21",  (100, 0, 400, ("selFatJet.subjetpt1",   'Sub Jet1 Pt')))


        for _s_type in cleaned_splitting_name:
            fill += ClusterHistsBoosted( (f"splitting_{_s_type}", f"{_s_type} Splitting"), f"splitting_{_s_type}" )
            fill += ClusterHistsDetailedBoosted( (f"detail_splitting_{_s_type}", f"{_s_type} Splitting"), f"splitting_{_s_type}")


        #
        #  By Mass
        #
        fill += ClusterHistsBoosted( ("splitting_1b0j/1b0j_lowMass", "1b0j/1b0j Splitting (low Mass"), "splitting_1b0j/1b0j_lowMass" )
        fill += ClusterHistsDetailedBoosted( ("detail_splitting_1b0j/1b0j_lowMass", "1b0j/1b0j Splitting (low Mass)"), "splitting_1b0j/1b0j_lowMass")

        fill += ClusterHistsBoosted( ("splitting_1b0j/1b0j_midMass", "1b0j/1b0j Splitting (mid Mass"), "splitting_1b0j/1b0j_midMass" )
        fill += ClusterHistsDetailedBoosted( ("detail_splitting_1b0j/1b0j_midMass", "1b0j/1b0j Splitting (mid Mass)"), "splitting_1b0j/1b0j_midMass")

        fill += ClusterHistsBoosted( ("splitting_1b0j/1b0j_highMass", "1b0j/1b0j Splitting (high Mass"), "splitting_1b0j/1b0j_highMass" )
        fill += ClusterHistsDetailedBoosted( ("detail_splitting_1b0j/1b0j_highMass", "1b0j/1b0j Splitting (high Mass)"), "splitting_1b0j/1b0j_highMass")

        #
        # fill histograms
        #
        fill(selev, hist)

        processOutput = {}
        self.cutFlow.addOutput(processOutput, event.metadata["dataset"])

        output = hist.output | processOutput

        return output

    def postprocess(self, accumulator):
        return accumulator
