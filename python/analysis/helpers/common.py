import sys
import logging
import pickle
import warnings

import awkward as ak
import numpy as np
import correctionlib
from coffea.nanoevents import NanoAODSchema
from coffea.nanoevents.methods import vector

NanoAODSchema.warn_missing_crossrefs = False
warnings.filterwarnings("ignore")
ak.behavior.update(vector.behavior)


def mask_event_decision(event, decision='OR', branch='HLT', list_to_mask=[''], list_to_skip=['']):
    '''
    Takes event.branch and passes an boolean array mask with the decisions of all the list_to_mask
    '''

    tmp_list = []
    if branch in event.fields:
        for i in list_to_mask:
            if i in event[branch].fields:
                tmp_list.append( event[branch][i] )
            elif i in list_to_skip: continue
            else: logging.warning(f'\n{i} branch not in {branch} for event.')
    else: logging.warning(f'\n{branch} branch not in event.')
    if not tmp_list:
        print(f'tmp_list {tmp_list}\n\n')
        sys.exit(0)
    #     tmp_list = [np.zeros(len(event), dtype=bool)]
    #     logging.warning(f'No {list_to_mask} branches found in event. Returning empty mask.')

    tmp_array = np.array( tmp_list )

    if decision.lower().startswith('or'): decision_array = np.any( tmp_array, axis=0 )
    else: decision_array = np.all( tmp_array, axis=0 )

    return decision_array

def apply_btag_sf( jets,
                    correction_file='data/JEC/BTagSF2016/btagging_legacy16_deepJet_itFit.json.gz',
                    correction_type="deepJet_shape",
                    sys_value = 'central',
                    btag_uncertainties = None,
                    dataset = '',
                    btagSF_norm_file='ZZ4b/nTupleAnalysis/weights/btagSF_norm.pkl',
                    ):
    '''
    Can be replace with coffea.btag_tools when btag_tools accept jsonpog files
    '''

    btagSF = correctionlib.CorrectionSet.from_file(correction_file)[correction_type]

    weights = {}
    j, nj = ak.flatten(jets), ak.num(jets)
    hf, eta, pt, tag = ak.to_numpy(j.hadronFlavour), ak.to_numpy(abs(j.eta)), ak.to_numpy(j.pt), ak.to_numpy(j.btagScore)

    cj_bl = jets[jets.hadronFlavour!=4]
    nj_bl = ak.num(cj_bl)
    cj_bl = ak.flatten(cj_bl)
    hf_bl, eta_bl, pt_bl, tag_bl = ak.to_numpy(cj_bl.hadronFlavour), ak.to_numpy(abs(cj_bl.eta)), ak.to_numpy(cj_bl.pt), ak.to_numpy(cj_bl.btagScore)
    SF_bl= btagSF.evaluate(sys_value, hf_bl, eta_bl, pt_bl, tag_bl)
    SF_bl = ak.unflatten(SF_bl, nj_bl)
    SF_bl = np.prod(SF_bl, axis=1)

    cj_c = jets[jets.hadronFlavour==4]
    nj_c = ak.num(cj_c)
    cj_c = ak.flatten(cj_c)
    hf_c, eta_c, pt_c, tag_c = ak.to_numpy(cj_c.hadronFlavour), ak.to_numpy(abs(cj_c.eta)), ak.to_numpy(cj_c.pt), ak.to_numpy(cj_c.btagScore)
    SF_c= btagSF.evaluate(sys_value, hf_c, eta_c, pt_c, tag_c)
    SF_c = ak.unflatten(SF_c, nj_c)
    SF_c = np.prod(SF_c, axis=1)

    ### btag norm
    try:
        with open(btagSF_norm_file, 'rb') as f:
            btagSF_norm = pickle.load(f)[dataset]
            logging.info(f'btagSF_norm {btagSF_norm}')
    except FileNotFoundError:
        btagSF_norm = 1.0

    btag_var = [ sys_value ]
    if btag_uncertainties:
        btag_var += [ f'{updown}_{btagvar}' for updown in ['up', 'down',] for btagvar in btag_uncertainties ]
    for sf in btag_var:
        if sf == 'central':
            SF = btagSF.evaluate('central', hf, eta, pt, tag)
            SF = ak.unflatten(SF, nj)
            # hf = ak.unflatten(hf, nj)
            # pt = ak.unflatten(pt, nj)
            # eta = ak.unflatten(eta, nj)
            # tag = ak.unflatten(tag, nj)
            # for i in range(len(selev)):
            #     for j in range(nj[i]):
            #         print(f'jetPt/jetEta/jetTagScore/jetHadronFlavour/SF = {pt[i][j]}/{eta[i][j]}/{tag[i][j]}/{hf[i][j]}/{SF[i][j]}')
            #     print(np.prod(SF[i]))
            SF = np.prod(SF, axis=1)
        if '_cf' in sf:
            SF = btagSF.evaluate(sf, hf_c, eta_c, pt_c, tag_c)
            SF = ak.unflatten(SF, nj_c)
            SF = SF_bl * np.prod(SF, axis=1) # use central value for b,l jets
        if '_hf' in sf or '_lf' in sf or '_jes' in sf:
            SF = btagSF.evaluate(sf, hf_bl, eta_bl, pt_bl, tag_bl)
            SF = ak.unflatten(SF, nj_bl)
            SF = SF_c * np.prod(SF, axis=1) # use central value for charm jets

        weights[f'btagSF_{sf}'] = SF * btagSF_norm

    logging.debug(weights)
    return weights


def drClean(coll1,coll2,cone=0.4):

    from coffea.nanoevents.methods import vector
    j_eta = coll1.eta
    j_phi = coll1.phi
    l_eta = coll2.eta
    l_phi = coll2.phi

    j_eta, l_eta = ak.unzip(ak.cartesian([j_eta, l_eta], nested=True))
    j_phi, l_phi = ak.unzip(ak.cartesian([j_phi, l_phi], nested=True))
    delta_eta = j_eta - l_eta
    delta_phi = vector._deltaphi_kernel(j_phi,l_phi)
    dr = np.hypot(delta_eta, delta_phi)
    nolepton_mask = ~ak.any(dr < cone, axis=2)
    jets_noleptons = coll1[nolepton_mask]
    return [jets_noleptons, nolepton_mask]

def update_events(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items():
        out = ak.with_field(out, value, name)
    return out

def compute_puid( jet, dataset ):
    """Compute the PUId for the given jet collection based on correctionlib. To be used in UL"""

    puid_WP_table = correctionlib.CorrectionSet.from_file('data/puId/puid_tightWP.json')['PUID']

    n, j = ak.num(jet), ak.flatten(jet)
    puid_WP = puid_WP_table.evaluate( j.pt, abs(j.eta), f"UL{dataset.split('UL')[1][:2]}" )

    logging.debug(f"puid_WP: {puid_WP[:10]}")
    logging.debug(f"puIdDisc: {j.puIdDisc[:10]}")
    logging.debug(f"eta: {j.eta[:10]}")
    logging.debug(f"pt: {j.pt[:10]}")
    logging.debug(f"puId: {j.puId[:10]}")
    j['is_pujet'] = ak.where( j.puIdDisc < puid_WP, True, False )
    logging.debug(f"is_pujet: {j['is_pujet'][:10]}\n\n")
    jet = ak.unflatten(j, n)

    return jet["is_pujet"]
