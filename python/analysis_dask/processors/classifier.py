from base_class.dask.hist import Collection


def basic(events):  # TODO
    hists = Collection(
        nTags=[4, 3],
    )
    fill = hists.add("canjet.pt", (100, 0, 2000, ("CanJet_pt", "Candidate Jet $p_T$")))
    events["nTags"] = (
        4 * events["HCR_input"]["fourTag"] + 3 * events["HCR_input"]["threeTag"]
    )
    events["CanJet_pt"] = events["HCR_input"]["CanJet_pt"]
    events["weight"] = events["HCR_input"]["weight"]
    fill(events)
    return {"hists": hists.to_dict(True), "raw": events.weight}
