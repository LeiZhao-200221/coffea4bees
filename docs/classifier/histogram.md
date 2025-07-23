# Histogram

A processor for creating histograms of SvB distributions and FvT reweighted kinematic variables is implemented for the `coffea` with `dask-awkward`. This processor can be directly run within the same environment as for the classifier training.

## Dask Analysis

A framework for generic dask analysis is implemented as follows:

- `analysis_dask/`: main package for dask analysis
    - `config/`: yaml configuration files
    - `processors/`: `coffea` processors
    - `weight/`: tools to generate different weights
    - `__init__.py`: commonly used functions to assemble the analysis tasks
- `dask_run.py`: run dask processors. The usage is given as below:

```bash
python dask_run.py [-h] \
    [--log-level {INFO,DEBUG,WARNING,ERROR}] \
    [--diagnostics DIAGNOSTICS] \
    configs [configs ...]
```

where the

- `--log-level` set the log level, default to `INFO`.
- `--diagnostics` can be used to provide a path to store the diagnostic reports for debugging. If not provided, the diagnostic steps will be skipped. The diagnostics includes figures for both the original and optimized task graph and a summary of the necessary ROOT file branches to read. The visualization and optimization will take some time for large datasets, and the large figures are usually hard to read, so it's only recommended to enable the diagnostics for small test datasets.
- `configs` are a list of paths to the `yaml` config files. An extended syntax is supported. See [this guide](https://chuyuanliu.github.io/heptools/guide/optional/config_parser.html) for more details.

To utilize the flexibility of dask tasks and for better reproducibility, the use of command line arguments is limited. The workflows and other arguments are completely described by different levels of the python code and yaml files.

The following keys in the config files will be used:

- `client`: a dask client to run all tasks
- `tasks`: a list of dask tasks
- `post-tasks`: a list of callables that will run locally in sequence after all dask tasks are finished.

The function `apply()` is available in `analysis_dask` as an combination of `coffea.dataset_tools.preprocess` and `coffea.dataset_tools.apply_to_fileset` with additional friend tree and preprocessing cache support.

## Classifier Plot Processor

A basic plot processor is implemented in `processors/classifier.py` as `BasicPlot`. This processor will read the selections and reconstructed objects from the friend tree for classifier input and plot the SvB distributions and other kinematic variables after JCM and FvT reweighting. The friend trees are passed through a dictionary with the keys following the conventions:

- The keys of FvT friend trees are required to match the pattern `FvT{suffix}`. Then, the hist collection will be structured as follows:

    - all data without any reweighting will be stored as `process=data`
    - the 3b data with only JCM reweight will be stored as `process=Multijet_JCM, tag=fourTag`
    - the 3b data with both JCM and FvT reweight will be stored as `process=Multijet{suffix}, tag=fourTag` per each suffix.

- The keys of SvB friend trees are required to match the pattern `SvB{suffix}`. Then, the hist collection will be structured as follows:

    - if at least one SvB is provided, the processor will repeat the following for each SvB: set `SvB_category=ggF/ZZ/ZH/failed` for each event based on the highest score; plot everything in the `BasicHists` template with prefix `SvB{suffix}.`
    - if no SvB is provided, all events will get `SvB_category=uncategorized` and the prefix for all plots will be `all.`

`0-1` JCM, `0-n` FvT, `0-n` SvB are acceptable.

For example, if `FvT_v1`, `FvT_v2`, `SvB_vA` and `SvB_vB` are provided, the hist collection will have a structure like:

```yaml
categories:
    process: [data, Multijet_JCM, Multijet_v1, Multijet_v2, ...]
    year: [UL18, UL17, UL16_preVFP, UL16_postVFP]
    tag: [fourTag, threeTag]
    region: [SR, SB]
    SvB_category: [ggF, ZZ, ZH, failed]
hists:
  - SvB_vA.score
  - SvB_vA.canjets.pt
  - SvB_vA.othjets.pt
  - ...
  - SvB_vB.score
  - SvB_vB.canjets.pt
  - SvB_vB.othjets.pt
  - ...
```

where the combinations `data,fourTag,SR` (blind), `Multijet_JCM,threeTag`, `Multijet_v1,threeTag` and `Multijet_v2,threeTag` will be empty.

!!! note

    In general, new object reconstructions need to be added to the `BasicPlot.__call__`, while new hists need to be added to the `BasicHists` template.

## Classifier Plot Configurations

The configurations are defined in different levels:

- `config/classifier_plot.cfg.yml`: defines the workflow to plot all input datasets, merge hists and dump to a file. If you just want to run the workflow, you don't need to change anything in this file. For new plotting workflows, you can add a new key at the same level as `2024_v2`.
- `config/classifier_plot_vars.cfg.yml`: defines the variables required by the workflow above. You are supposed to make a copy of this file and specify the classifier output friend trees under `classifier_outputs<var>` and the dataset year combinations under `classifier_datasets<var>`.
- `config/cluster.cfg.yml`: contains commonly used predefined cluster configurations.
- `config/userdata.cfg.yml`: contains user data shared by all workflows. You should make a copy of this file and add your own data. Your personal data should be kept locally.

    - The `scratch_dir` should be on a shared file system that is accessible by all workers. For example, on LPC/LXPLUS with condor, you may want to use EOS area. On a single rogue node, you can use the same directory as `output_dir`.
    - The `output_dir` is where you want all results to be stored.
    - For the `scratch_dir` and `output_dir`, you only need to provide a base directory. The workflows will create their own workspace under it (usually with the name of the workflow and a timestamp).

!!! note

    For the configurations that you don't want to commit, name the file with suffix `.local.cfg.yml`.

For example, if you run the workflow for `datasets_HH4b_2024_v2` on rogue, you can use:

```bash
export BASE=classifier/config # optional
python dask_run.py \
    ${BASE}/userdata.local.cfg.yml \
    ${BASE}/cluster.cfg.yml#rogue_local_huge \ 
    ${BASE}/classifier_plot_vars.local.cfg.yml#2024_v2 \
    ${BASE}/classifier_plot.cfg.yml#2024_v2
```

## Tips

- If the `Operation Expired` errors from XRootD keep occurring, reduce the number of workers or swtich to other nodes may help.
