from analysis.helpers.hist_templates import (
    FvTHists,
    QuadJetHistsSelected,
    QuadJetHistsMinDr,
    QuadJetHistsSRSingle,
    SvBHists,
    TopCandHists,
    WCandHists,
    # m4jVsPt4j, m4jVsHt, m4jVsNSelJets, pt4jVsNSelJets, hTVsPt4j, hTVsNSelJets, m4jVsJetPt, m4jVsJetsDr, ptVsJetsDr, m4jVsSvB, svbVsJetsDr
)
from base_class.hist import Collection, Fill
from base_class.physics.object import Elec, Jet, LorentzVector, Muon
import logging
from memory_profiler import profile

# @profile
def filling_nominal_histograms(selev, JCM,
                               processName: str = None,
                               year: str = 'UL18',
                               isMC: bool = False,
                               histCuts: list = [],
                               apply_FvT: bool = False,
                               run_SvB: bool = False,
                               top_reconstruction: bool = False,
                               isDataForMixed: bool = False,
                               tag_list: list = ["threeTag", "fourTag"],
                               run_dilep_ttbar_crosscheck: bool = False,
                               event_metadata: dict = {},
                               ):

    fill = Fill(process=processName, year=year, weight="weight")
    
    hist = Collection( process=[processName],
                        year=[year],
                        tag=tag_list,
                        region=['SR', "SB"],
                        **dict((s, ...) for s in histCuts)
                        )

    fill += hist.add( "trigWeight", (40, 0, 2, ("trigWeight", 'Trigger weight')), weight='no_weight' )

    fill += hist.add( "nPVs", (101, -0.5, 100.5, ("PV.npvs", "Number of Primary Vertices")) )
    fill += hist.add( "nPVsGood", (101, -0.5, 100.5, ("PV.npvsGood", "Number of Good Primary Vertices")), )

    fill += hist.add( "hT", (50, 0, 1500, ("hT", "h_{T} [GeV]")) )
    fill += hist.add( "hT_selected", (50, 0, 1500, ("hT_selected", "h_{T} [GeV]")), )

    #
    # Jets
    #
    skip_jet_list = ['energy', 'deepjet_c']
    fill += Jet.plot(("selJets", "Selected Jets"),        "selJet",           skip=skip_jet_list, bins={"mass": (50, 0, 100)})
    fill += Jet.plot(("canJets", "Higgs Candidate Jets"), "canJet",           skip=skip_jet_list, bins={"mass": (50, 0, 100)})
    fill += Jet.plot(("othJets", "Other Jets"),           "notCanJet_coffea", skip=skip_jet_list, bins={"mass": (50, 0, 100)})
    fill += Jet.plot(("tagJets", "Tag Jets"),             "tagJet",           skip=skip_jet_list, bins={"mass": (50, 0, 100)})
    
    if any('lowpt' in tag for tag in tag_list):
        fill += hist.add('lowpt_categories', (21, -0.5, 20.5, ('lowpt_categories', 'lowpt_categories')))
        fill += Jet.plot(("selJets_lowpt", "Selected lowpt Jets"), "selJet_lowpt", skip=skip_jet_list, bins={"mass": (50, 0, 100)})
        fill += Jet.plot(("tagJets_lowpt", "Selected lowpt tagged Jets"), "tagJet_lowpt", skip=skip_jet_list, bins={"mass": (50, 0, 100)})


    #
    #  Make quad jet hists
    #
    fill += LorentzVector.plot_pair( ("v4j", R"$HH_{4b}$"), "v4j", skip=["n", "dr", "dphi", "st"], bins={"mass": (120, 0, 1200)}, )
    fill += QuadJetHistsSelected( ("quadJet_selected", "Selected Quad Jet"), "quadJet_selected" )
    fill += QuadJetHistsMinDr( ("quadJet_min_dr", "Min dR Quad Jet"), "quadJet_min_dr" )
    
    fill += hist.add( "m4j",    (200, 0, 2000, ("m4j"     , "m4j [GeV]"     )) )
    fill += hist.add( "m4j_hh", (200, 0, 2000, ("m4j_HHSR", "m4j HHSR [GeV]")) )
    fill += hist.add( "m4j_zh", (200, 0, 2000, ("m4j_ZHSR", "m4j ZHSR [GeV]")) )
    fill += hist.add( "m4j_zz", (200, 0, 2000, ("m4j_ZZSR", "m4j ZZSR [GeV]")) )
    fill += hist.add( "m4j_hh_passHH", (200, 0, 2000, ("m4j_HHSR_passHH", "m4j HHSR passHH [GeV]")) )
    fill += hist.add( "m4j_zh_passZH", (200, 0, 2000, ("m4j_ZHSR_passZH", "m4j ZHSR passZH [GeV]")) )
    fill += hist.add( "m4j_zz_passZZ", (200, 0, 2000, ("m4j_ZZSR_passZZ", "m4j ZZSR passZZ [GeV]")) )

    fill += QuadJetHistsSRSingle( ("dijet_HHSR", "DiJet Mass HHSR") ,"dijet_HHSR"  )
    fill += QuadJetHistsSRSingle( ("dijet_ZHSR", "DiJet Mass ZHSR") ,"dijet_ZHSR"  )
    fill += QuadJetHistsSRSingle( ("dijet_ZZSR", "DiJet Mass ZZSR") ,"dijet_ZZSR"  )
    
    # fill += m4jVsPt4j(("v4j_mass_vs_v4j_pt", "") , "v4j_mass_vs_v4j_pt")
    # fill += m4jVsHt(("v4j_mass_vs_hT", "m4j vs hT") , "v4j_mass_vs_hT") 
    # fill += m4jVsHt(("v4j_mass_vs_hT_trigger", "m4j vs hT_trig") , "v4j_mass_vs_hT_trigger") 
    # fill += m4jVsHt(("v4j_mass_vs_hT_selected", "m4j vs hT_sel") , "v4j_mass_vs_hT_selected") 
    # fill += m4jVsNSelJets(("v4j_mass_vs_nJetSel", "m4j vs nJetSel"), "v4j_mass_vs_nJetSel")
    # fill += pt4jVsNSelJets(("v4j_pt_vs_nJetSel", "pt4j vs nJetSel"), "v4j_pt_vs_nJetSel")
    # fill += hTVsNSelJets(("hT_sel_vs_nJetSel", "hT_sel vs nJetSel"), "hT_sel_vs_nJetSel")
    # fill += hTVsPt4j(("hT_sel_vs_v4j_pt", "hT_sel vs pt4j"), "hT_sel_vs_v4j_pt")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_l",  "v4j_mass vs pt_l"),  "v4j_mass_vs_pt_l")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_s",  "v4j_mass vs pt_s"),  "v4j_mass_vs_pt_s")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_ll", "v4j_mass vs pt_ll"), "v4j_mass_vs_pt_ll")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_ls", "v4j_mass vs pt_ls"), "v4j_mass_vs_pt_ls")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_sl", "v4j_mass vs pt_sl"), "v4j_mass_vs_pt_sl")
    # fill += m4jVsJetPt(("v4j_mass_vs_pt_ss", "v4j_mass vs pt_ss"), "v4j_mass_vs_pt_ss")
    # fill += ptVsJetsDr(("v4j_pt_vs_dr_l_s",  "v4j_pt_vs_dr_l_s"),  "v4j_pt_vs_dr_l_s")
    # fill += ptVsJetsDr(("l_pt_vs_dr_l_s",  "l_pt_vs_dr_l_s"),  "l_pt_vs_dr_l_s")
    # fill += ptVsJetsDr(("s_pt_vs_dr_l_s",  "s_pt_vs_dr_l_s"),  "s_pt_vs_dr_l_s")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_0_1",  "v4j_mass_vs_SvB_0_1"),  "v4j_mass_vs_SvB_0_1")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_0_p2",  "v4j_mass_vs_SvB_0_p2"),  "v4j_mass_vs_SvB_0_p2")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_p2_p8",  "v4j_mass_vs_SvB_p2_p8"),  "v4j_mass_vs_SvB_p2_p8")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_p4_p8",  "v4j_mass_vs_SvB_p4_p8"),  "v4j_mass_vs_SvB_p4_p8")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_p6_p8",  "v4j_mass_vs_SvB_p6_p8"),  "v4j_mass_vs_SvB_p6_p8")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_p2_1",  "v4j_mass_vs_SvB_p2_1"),  "v4j_mass_vs_SvB_p2_1")
    # fill += m4jVsSvB(("v4j_mass_vs_SvB_p8_1",  "v4j_mass_vs_SvB_p8_1"),  "v4j_mass_vs_SvB_p8_1")
    # fill += svbVsJetsDr(("svb_vs_dr_l_s",  "svb_vs_dr_l_s"),  "svb_vs_dr_l_s")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_l_s",  "v4j_mass_vs_dr_l_s"),  "v4j_mass_vs_dr_l_s")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_ll_ls","v4j_mass_vs_dr_ll_ls"),"v4j_mass_vs_dr_ll_ls")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_ll_sl","v4j_mass_vs_dr_ll_sl"),"v4j_mass_vs_dr_ll_sl")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_ll_ss","v4j_mass_vs_dr_ll_ss"),"v4j_mass_vs_dr_ll_ss")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_ls_sl","v4j_mass_vs_dr_ls_sl"),"v4j_mass_vs_dr_ls_sl")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_ls_ss","v4j_mass_vs_dr_ls_ss"),"v4j_mass_vs_dr_ls_ss")
    # fill += m4jVsJetsDr(("v4j_mass_vs_dr_sl_ss","v4j_mass_vs_dr_sl_ss"),"v4j_mass_vs_dr_sl_ss")

    

    #
    #  Make classifier hists
    #
    if apply_FvT:
        FvT_skip = []
        if "pt" not in selev.FvT.fields:
            FvT_skip = ["pt", "pm3", "pm4"]

        fill += FvTHists(("FvT", "FvT Classifier"), "FvT", skip=FvT_skip)

        fill += hist.add("quadJet_selected.FvT_score", (100, 0, 1, ("quadJet_selected.FvT_q_score", "Selected Quad Jet Diboson FvT q score") ) )
        fill += hist.add("quadJet_min_dr.FvT_score",      (100, 0, 1, ("quadJet_min_dr.FvT_q_score",   "Min dR Quad Jet Diboson FvT q score"  ) ) )

        if JCM:
            fill += hist.add("FvT_noFvT", (100, 0, 5, ("FvT.FvT", "FvT reweight")), weight="weight_noFvT")

    skip_all_but_n = ["deepjet_b", "energy", "eta", "id_jet", "id_pileup", "mass", "phi", "pt", "pz", "deepjet_c", ]

    fill += Jet.plot( ("selJets_noJCM", "Selected Jets"),        "selJet",       weight="weight_noJCM_noFvT", skip=skip_all_but_n, )
    fill += Jet.plot( ("tagJets_noJCM", "Tag Jets"),             "tagJet",       weight="weight_noJCM_noFvT", skip=skip_all_but_n, )
    fill += Jet.plot( ("tagJets_loose_noJCM", "Loose Tag Jets"), "tagJet_loose", weight="weight_noJCM_noFvT", skip=skip_all_but_n, )
    if JCM:
        fill += hist.add( "nPSJets",             (20, -0.5, 19.5, ("nJet_pseudotagged", "nPseudoTag Jets")) )
        fill += hist.add( "nPSplusTagJets",      (20, -0.5, 19.5, ("nJet_ps_and_tag", "nPseudoTag + nTag Jets")) )

    for iJ in range(4):
        fill += Jet.plot( (f"canJet{iJ}", f"Higgs Candidate Jets {iJ}"), f"canJet{iJ}", skip=["n", "deepjet_c"], bins={"mass": (50, 0, 100)} )

    #
    #  Leptons
    #
    skip_muons = ["charge"] + Muon.skip_detailed_plots
    if not isMC:
        skip_muons += ["genPartFlav"]
    fill += Muon.plot( ("selMuons", "Selected Muons"), "selMuon", skip=skip_muons )

    if "Elec" in selev.fields:
        skip_elecs = ["charge"] + Elec.skip_detailed_plots
        if not isMC:
            skip_elecs += ["genPartFlav"]
        fill += Elec.plot( ("selElecs", "Selected Elecs"), "selElec", skip=skip_elecs )

    #
    # Top Candidates
    #
    if top_reconstruction in ["slow","fast"]:
        fill += TopCandHists(("top_cand", "Top Candidate"), "top_cand")
        fill += hist.add("xW",  (100, -12, 12, ("xW", "xW")))
        fill += hist.add("xbW", (100, -15, 15, ("xbW", "xbW")))

    if run_SvB:

        fill += SvBHists(("SvB",    "SvB Classifier"),    "SvB")
        fill += SvBHists(("SvB_MA", "SvB MA Classifier"), "SvB_MA")
        fill += SvBHists(("SvB_noFvT",    "SvB Classifier"),    "SvB",   weight="weight_noFvT")
        fill += SvBHists(("SvB_MA_noFvT", "SvB MA Classifier"), "SvB_MA",weight="weight_noFvT")
        fill += hist.add( "quadJet_selected.SvB_q_score", ( 100, 0, 1, ( "quadJet_selected.SvB_q_score",  "Selected Quad Jet Diboson SvB q score") ) )
        fill += hist.add( "quadJet_min_dr.SvB_MA_q_score",   ( 100, 0, 1, ( "quadJet_min_dr.SvB_MA_q_score", "Min dR Quad Jet Diboson SvB MA q score") ) )
        if isDataForMixed:
            for _FvT_name in event_metadata["FvT_names"]:
                # logging.info(_FvT_name)
                fill += SvBHists( (f"SvB_{_FvT_name}",    "SvB Classifier"),    "SvB",    weight=f"weight_{_FvT_name}", )
                fill += SvBHists( (f"SvB_MA_{_FvT_name}", "SvB MA Classifier"), "SvB_MA", weight=f"weight_{_FvT_name}", )
            for _FvT_name in event_metadata["FvT_names"]:
                fill += hist.add( f"m4j_{_FvT_name}"   , (200, 0, 2000, ("m4j"     , "m4j [GeV]")),      weight=f"weight_{_FvT_name}", )
                fill += hist.add( f"m4j_hh_{_FvT_name}", (200, 0, 2000, ("m4j_HHSR", "m4j HHSR [GeV]")), weight=f"weight_{_FvT_name}", )
                fill += hist.add( f"m4j_zh_{_FvT_name}", (200, 0, 2000, ("m4j_ZHSR", "m4j ZHSR [GeV]")), weight=f"weight_{_FvT_name}", )
                fill += hist.add( f"m4j_zz_{_FvT_name}", (200, 0, 2000, ("m4j_ZZSR", "m4j ZZSR [GeV]")), weight=f"weight_{_FvT_name}", )
                fill += hist.add( f"m4j_zz_passZZ_{_FvT_name}", (200, 0, 2000, ("m4j_ZZSR_passZZ", "m4j ZZSR passZZ [GeV]")) , weight=f"weight_{_FvT_name}",)
                fill += hist.add( f"m4j_zh_passZH_{_FvT_name}", (200, 0, 2000, ("m4j_ZHSR_passZH", "m4j ZHSR passZH [GeV]")) , weight=f"weight_{_FvT_name}",)
                fill += hist.add( f"m4j_hh_passHH_{_FvT_name}", (200, 0, 2000, ("m4j_HHSR_passHH", "m4j HHSR passHH [GeV]")) , weight=f"weight_{_FvT_name}",)

    #
    #  MC Truth
    #
    if "truth_v4b" in selev.fields:
        fill += LorentzVector.plot_pair( ("truth_v4b", R"$HH_{4b}$"), "truth_v4b", skip=["n", "dr", "dphi", "st"], bins={"mass": (120, 0, 1200)}, )

    #
    # fill histograms
    #

    # fill.cache(selev)
    fill(selev, hist)

    if run_dilep_ttbar_crosscheck:

        fill_ttbar = Fill(process=processName, year=year, weight="weight_noJCM_noFvT")
        hist_ttbar = Collection( process=[processName],
                            year=[year],
                            **dict((s, ...) for s in ['passDilepTtbar'])
                            )

        fill_ttbar += Jet.plot(("tagJets_dilepttbar", "Tag Jets dilep ttbar"), "tagJet", skip=skip_jet_list)
        fill_ttbar(selev, hist_ttbar)
    
        return hist.to_dict(nonempty=True)|{"hists_ttbar":hist_ttbar.to_dict(nonempty=True)["hists"]}
    
    else:
        return hist.to_dict(nonempty=True)


def filling_syst_histograms(selev, weights, analysis_selections,
                            shift_name: str = 'nominal',
                            processName: str = None,
                            year: str = 'UL18',
                            histCuts: list = []
                            ):

    shift_name = "nominal" if not shift_name else shift_name 
    hist_SvB = Collection( process=[processName],
                            year=[year],
                            variation=[shift_name],
                            tag=["threeTag", "fourTag"],
                            region=['SR', "SB"],
                            **dict((s, ...) for s in histCuts),
                            )

    fill_SvB = Fill( process=processName, year=year)
    fill_SvB += SvBHists(("SvB",    "SvB Classifier"),    "SvB",    skip=["ps", "ptt"])
    fill_SvB += SvBHists(("SvB_MA", "SvB MA Classifier"), "SvB_MA", skip=["ps", "ptt"])

    fill_SvB(selev, hist_SvB, variation=shift_name, weight="weight")

    if "nominal" in shift_name:
        logging.info(f"Weight variations {weights.variations}")

        for ivar in list(weights.variations):
            selev[f"weight_{ivar}"] = weights.weight(modifier=ivar)[ analysis_selections ]
            logging.debug(f"{ivar} {selev['weight']}")
            fill_SvB(selev, hist_SvB, variation=ivar, weight=f"weight_{ivar}")

    return hist_SvB.to_dict(nonempty=True)
