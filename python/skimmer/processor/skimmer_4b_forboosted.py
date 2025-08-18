import yaml
import logging
import awkward as ak
import numpy as np
from coffea.util import load
from src.skimmer.picoaod import PicoAOD #, fetch_metadata, resize
from src.physics.event_selection import apply_event_selection



class Skimmer(PicoAOD):
    def __init__(self, file_wEvents="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_wEvents = load(file_wEvents)
        self.corrections_metadata = yaml.safe_load(open('src/physics/corrections.yml', 'r'))

    def select(self, events):

        isMC    = True if events.run[0] == 1 else False
        year    = events.metadata['year']
        dataset = events.metadata['dataset']

        resolved_events = self.file_wEvents['event'][f"{dataset}"]
        resolved_selection_SR = np.isin( events.event.to_numpy(), resolved_events )

        return resolved_selection_SR
