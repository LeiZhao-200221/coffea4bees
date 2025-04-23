import numpy as np
import awkward as ak
from coffea.lumi_tools import LumiMask
from analysis.helpers.common import mask_event_decision, drClean
from analysis.helpers.selection_basic_4b import (
    lepton_selection,
    jet_selection
)

def apply_event_selection(
    event: ak.Array, 
    corrections_metadata: dict, 
    cut_on_lumimask: bool = True
) -> ak.Array:
    """
    Applies basic event selection criteria for a 4b analysis.

    Parameters:
    -----------
    event : awkward.Array
        The event data containing fields such as `run`, `luminosityBlock`, `HLT`, and `Flag`.
    corrections_metadata : dict
        Metadata containing corrections and configuration information, such as:
        - `goldenJSON`: Path to the golden JSON file for luminosity masking.
        - `NoiseFilter`: List of noise filters to apply.
    cut_on_lumimask : bool, optional
        Whether to apply the luminosity mask cut. Defaults to True.

    Returns:
    --------
    event : awkward.Array
        The input event data with additional fields:
        - `lumimask`: Boolean mask indicating events passing the luminosity mask.
        - `passHLT`: Boolean mask indicating events passing the HLT trigger.
        - `passNoiseFilter`: Boolean mask indicating events passing noise filters.
    """
    # Apply luminosity mask
    if 'goldenJSON' not in corrections_metadata:
        raise KeyError("Missing 'goldenJSON' in corrections_metadata.")
    lumimask = LumiMask(corrections_metadata['goldenJSON'])
    event['lumimask'] = (
        np.array(lumimask(event.run, event.luminosityBlock))
        if cut_on_lumimask else np.full(len(event), True)
    )

    # Apply HLT trigger mask
    event['passHLT'] = (
        np.full(len(event), True)
        if 'HLT' not in event.fields else mask_event_decision(
            event, decision="OR", branch="HLT", list_to_mask=event.metadata.get('trigger', [])
        )
    )

    # Apply noise filter mask
    noise_filters = corrections_metadata.get('NoiseFilter', [])
    event['passNoiseFilter'] = (
        np.full(len(event), True)
        if 'Flag' not in event.fields else mask_event_decision(
            event, decision="AND", branch="Flag", list_to_mask=noise_filters,
            list_to_skip=['BadPFMuonDzFilter', 'hfNoisyHitsFilter']
        )
    )

    return event

def apply_dilep_ttbar_selection(event: ak.Array, isRun3: bool = False) -> ak.Array:
    """
    Applies dilepton ttbar selection criteria to the event data.

    Parameters:
    -----------
    event : ak.Array
        The event data containing fields such as `Muon`, `Electron`, and `MET`.
    isRun3 : bool, optional
        Whether to apply Run 3-specific selection criteria. Defaults to False.

    Returns:
    --------
    ak.Array
        A boolean mask indicating events passing the dilepton ttbar selection criteria.
    """
    # Select muons and electrons
    muons = event.selMuon
    n_muons = ak.sum(muons.pt, axis=1)

    electrons = event.selElec 
    if 'selElec' in event.fields:
        electrons = event.selElec
        n_electrons = ak.sum(electrons.pt, axis=1) 
        # Require exactly two leptons (muons + electrons)
        dilepton_mask = (n_muons + n_electrons) == 2
    else:
        dilepton_mask = n_muons == 2

    # Require opposite-sign leptons
    if hasattr(muons, 'charge'):
        os_muons = ak.any(muons.charge[:, None] + muons.charge == 0, axis=1)
        opposite_sign_mask = os_muons         
    elif hasattr(electrons, 'charge'):
        os_electrons = ak.any(electrons.charge[:, None] + electrons.charge == 0, axis=1)
        os_muon_electron = ak.any(muons.charge[:, None] + electrons.charge == 0, axis=1)
        opposite_sign_mask = os_muons | os_electrons | os_muon_electron
    else:
        opposite_sign_mask = np.full(len(event), False)

    # Require MET > 40 GeV
    met_mask = event.MET.pt > 40

    # Combine all selection criteria
    selection_mask = dilepton_mask & opposite_sign_mask & met_mask

    return selection_mask

def apply_boosted_4b_selection(event: ak.Array) -> ak.Array:
    """
    Applies boosted object selection criteria for 4b analysis.

    Parameters:
    -----------
    event : ak.Array
        The event data containing fields such as `FatJet` and `bdt`.

    Returns:
    --------
    ak.Array
        The input event data with additional fields:
        - `passBoostedKin`: Boolean mask for events passing boosted kinematic selection.
        - `passBoostedSel`: Boolean mask for events passing boosted selection criteria.
    """
    # Sort FatJets by particleNetMD_Xbb in descending order
    event['FatJet'] = event.FatJet[ak.argsort(event.FatJet.particleNetMD_Xbb, axis=1, ascending=False)]

    # Apply kinematic selection to FatJets
    FatJet_selected = (event.FatJet.pt > 300) & (np.abs(event.FatJet.eta) < 2.4)
    nFatJet_selected = ak.sum(FatJet_selected, axis=1)

    # Check if events pass boosted kinematic selection
    event['passBoostedKin'] = nFatJet_selected >= 2

    # Apply additional selection criteria to candidate jets
    tmp_selev = event[event.passBoostedKin]
    candJet1 = (tmp_selev.FatJet[:, 0].msoftdrop > 50) & (tmp_selev.FatJet[:, 0].particleNetMD_Xbb > 0.8)
    candJet2 = (tmp_selev.FatJet[:, 1].particleNet_mass > 50)

    # Apply BDT-based selection if available
    if 'bdt' in tmp_selev.fields:
        passBDT = (tmp_selev.FatJet[:, 1].particleNetMD_Xbb > 0.950) & (tmp_selev.bdt['score'] > 0.03)  ### bdt_score only in picoAOD.chunk.withBDT.root files
        # passBDT = (tmp_selev.FatJet[:, 1].particleNetMD_Xbb > 0.980) & (tmp_selev.bdt['score'] > 0.43)  ### bdt_score only in picoAOD.chunk.withBDT.root files
    else:
        passBDT = np.full(len(tmp_selev), True)

    # Combine all selection criteria
    passBoostedSel = np.full(len(event), False)
    passBoostedSel[event.passBoostedKin] = candJet1 & candJet2 & passBDT
    event['passBoostedSel'] = passBoostedSel

    return event

def apply_4b_selection(event, corrections_metadata, *,
                                dataset: str = '',
                                doLeptonRemoval: bool = True,
                                loosePtForSkim: bool = False,
                                override_selected_with_flavor_bit: bool = False,
                                do_jet_veto_maps: bool = False,
                                isRun3: bool = False,
                                isMC: bool = False,  ### temporary for Run3
                                isSyntheticData: bool = False,
                                isSyntheticMC: bool = False,
                            ):
    """
    Applies object selection criteria for 4b analysis.

    Parameters:
    -----------
    event : ak.Array
        The event data containing fields such as `Jet` and `Lepton`.
    corrections_metadata : dict
        Metadata containing corrections and configuration information.
    dataset : str, optional
        The dataset name. Defaults to an empty string.
    doLeptonRemoval : bool, optional
        Whether to perform lepton removal. Defaults to True.
    loosePtForSkim : bool, optional
        Whether to use loose pT cuts for skimming. Defaults to False.
    override_selected_with_flavor_bit : bool, optional
        Whether to override selected jets with flavor bit. Defaults to False.
    do_jet_veto_maps : bool, optional
        Whether to apply jet veto maps. Defaults to False.
    isRun3 : bool, optional
        Whether to apply Run 3-specific selection criteria. Defaults to False.
    isMC : bool, optional
        Whether the data is Monte Carlo simulation. Defaults to False.
    isSyntheticData : bool, optional
        Whether the data is synthetic. Defaults to False.
    isSyntheticMC : bool, optional
        Whether the Monte Carlo data is synthetic. Defaults to False.

    Returns:
    --------
    ak.Array
        The input event data with additional fields for object selection.
    """
    # Combined RunII and 3 selection
    event = lepton_selection(event, isRun3)
    
    event = jet_selection(event, corrections_metadata, isRun3, isMC, isSyntheticData, isSyntheticMC, dataset, doLeptonRemoval, do_jet_veto_maps, override_selected_with_flavor_bit)

    event['passJetMult'] = event['nJet_selected'] >= 4

    event['fourTag'] = (event['nJet_tagged'] >= 4)
    event['threeTag'] = (event['nJet_tagged_loose'] == 3) & (event['nJet_selected'] >= 4)
    event['twoTag'] = (event['nJet_tagged_loose'] == 2) & (event['nJet_selected'] >= 4)

    if isSyntheticData or isSyntheticMC:
        event['threeTag'] = False
        event['twoTag'] = False

    if isRun3:
        event['passPreSel'] = event.twoTag | event.threeTag | event.fourTag
    else:
        event['passPreSel'] = event.threeTag | event.fourTag

    event['tag'] = ak.zip({
        "twoTag": event.twoTag,
        "threeTag": event.threeTag,
        "fourTag": event.fourTag,
    })

    # For trigger emulation
    event['Jet', 'muon_cleaned'] = drClean(event.Jet, event.selMuon)[1]
    event['Jet', 'ht_selected'] = (event.Jet.pt >= 30) & (np.abs(event.Jet.eta) < 2.4) & event.Jet.muon_cleaned
    #  Calculate hT
    event["hT"] = ak.sum(event.Jet[event.Jet.selected_loose].pt, axis=1)
    event["hT_selected"] = ak.sum(event.Jet[event.Jet.selected].pt, axis=1)
    event["hT_trigger"] = ak.sum(event.Jet[event.Jet.ht_selected].pt, axis=1)

    # Only need 30 GeV jets for signal systematics
    if loosePtForSkim:
        mask_jet_lowpt_forskim = (event.Jet.pt >= 15) & (np.abs(event.Jet.eta) <= 2.4) & ~event.Jet.pileup & (event.Jet.jetId >= 2) & event.Jet.lepton_cleaned
        nJet_selected_lowpt_forskim = ak.sum(mask_jet_lowpt_forskim, axis=1)
        mask_tagjet_lowpt_forskim = mask_jet_lowpt_forskim & (event.Jet.btagScore >= corrections_metadata['btagWP']['M'])
        event['passJetMult_lowpt_forskim'] = nJet_selected_lowpt_forskim >= 4
        nJet_tagged_lowpt_forskim = ak.num(event.Jet[mask_tagjet_lowpt_forskim])
        event["fourTag_lowpt_forskim"] = (nJet_tagged_lowpt_forskim >= 4)
        event['passPreSel_lowpt_forskim'] = event.threeTag | event.fourTag_lowpt_forskim

    return event