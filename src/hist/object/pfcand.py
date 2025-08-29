from ...hist import H
from .vector import  _PlotLorentzVector


class _PlotCommon:
    ...


class _PlotPFCand(_PlotCommon, _PlotLorentzVector):

    # fields ['trkHighPurity', 'charge', 'lostInnerHits', 'lostOuterHits', 'pdgId', 'pvAssocQuality', 'trkAlgo', 'trkQuality', 'd0', 'd0Err', 'dz', 'dzErr',  'trkChi2', 'trkEta', 'trkP', 'trkPhi', 'trkPt', 'vtxChi2']

    pdgId = H((50, -250, 250, ('pdgId', 'pdgId')))
    nHits = H((40, -0.5, 39.5, ('numberOfHits', 'number of Hits')))
    nPix  = H((10, -0.5,  9.5, ('numberOfPixelHits', 'number of Pixel Hits')))
    puppiWeight  = H((50, 0,  1.0, ('puppiWeight', 'puppiWeight')))
    puppiWeightNoLep  = H((50, 0,  1.0, ('puppiWeightNoLep', 'puppiWeightNoLep')))
    #deepjet_c = H((50, 0, 1, ('btagDeepFlavCvL', 'DeepJet $c$ vs $uds+g$')),
    #              (50, 0, 1, ('btagDeepFlavCvB', 'DeepJet $c$ vs $b$')))
    #id_pileup = H(([0b000, 0b100, 0b110, 0b111], ('puId', 'Pileup ID')))
    #id_jet = H(([0b000, 0b010, 0b110], ('jetId', 'Jet ID')))




class PFCand:
    plot = _PlotPFCand
