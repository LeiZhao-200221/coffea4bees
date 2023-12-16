from ...hist import H
from .vector import _PlotDiLorentzVector, _PlotLorentzVector


class _PlotCommon:
    ...


class _PlotJet(_PlotCommon, _PlotLorentzVector):
    deepjet_b = H((100, 0, 1, ('btagDeepFlavB', 'DeepJet $b$')))
    deepjet_c = H((100, 0, 1, ('btagDeepFlavCvL', 'DeepJet $c$ vs $uds+g$')),
                  (100, 0, 1, ('btagDeepFlavCvB', 'DeepJet $c$ vs $b$')))
    id_pileup = H(([0b000, 0b100, 0b110, 0b111], ('puId', 'Pileup ID')))
    id_jet = H(([0b000, 0b010, 0b110], ('jetId', 'Jet ID')))


class _PlotDiJet(_PlotCommon, _PlotDiLorentzVector):
    ...


class Jet:
    plot = _PlotJet
    plot_pair = _PlotDiJet
