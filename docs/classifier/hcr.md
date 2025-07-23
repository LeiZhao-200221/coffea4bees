# Hierarchical Combinatoric ResNet (HCR)

This tutorial will work through a complete example of training baseline FvT and SvB classifier for HH4b analysis using skim datasets_HH4b_2024_v2 on rogue.

## Setup environment

See [Overview](index.md#setup-environment) for details.
## Plotting

See [Histogram](histogram.md#classifier-plot-configurations) for details.

## Tips on Performance

- Training:
    - in main task `train`, consider increasing `--max-trainers` to parallel multiple models (CPU, GPU, memory bounded)
    - in `-dataset HCR.*`, consider increasing `--max-workers` (IO and CPU bounded, require extra memory)
    - in `-setting ml.DataLoader`
        - always set `optimize_sliceable_dataset` to `True` if the dataset fits in memory. This option enables a custom data loader that makes use of `torch`'s c++ based parallel slicing, which is significantly faster and more memory efficient than the default `torch.utils.data.DataLoader`.
        - if `optimize_sliceable_dataset` is disabled, consider increasing `num_workers` to speed up batch generation (mainly CPU bounded, require extra memory)
        - consider increasing `batch_eval` to speed up evaluation (mainly GPU memory bounded)
    - in `-setting torch.Training`, consider using `disable_benchmark` to skip all benchmark steps.
- Evaluation:
    - in main task `evaluate`, consider increasing `--max-evaluators` to parallel multiple models (CPU, GPU, memory bounded)
    - in `-setting torch.DataLoader`, consider increasing `num_workers` and `batch_eval`. (IO and CPU bounded, require extra memory)
- Merging k-folds:
    - in `-analysis kfold.Merge`,
        - consider increasing `--workers` (IO and CPU bounded, require extra memory)
        - consider using a finite `--step` to split root files into smaller chunks.
