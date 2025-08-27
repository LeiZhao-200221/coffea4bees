class cutflow:

    def addOutputLumisProcessed(self, o, dataset, runs, luminosityBlocks):
        o[dataset]["lumis_processed"] = {}
        run_list = set(runs)
        for r in run_list:
            run_mask = (runs == r)
            lbs_per_run = list(set(luminosityBlocks[run_mask]))
            o[dataset]["lumis_processed"][r] = list(lbs_per_run)

    def addOutputSkim(self, o, dataset):
        pass

