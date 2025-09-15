# Task System

The task system is designed to make both the python code and the command-line interface modularized and extensible. A task is a python class that follows one of the task protocol and has a `argparser` attribute.

## Task Protocols

There are basically two types of tasks: main tasks and other tasks. Each run accepts only one main task and arbitrary number of other tasks.

### Main task

A main task is a `.py` file in `config/main/` containing a class named `Main` which has a `run()` method specifiying how other tasks will be used. For example, the `train` task defined in `config/main/train.py` will load and merge the dateset tasks and pass them to the model tasks for training.

### Other tasks

Other tasks will be used by the main task or automatically handled by the internal system. The following protocols are available:

- `dataset`:
    - protocol: `Dataset` in `task/dataset.py`
    - implementations: `config/dataset/`
    - load a training/evaluation dataset
- `model`:
    - protocol: `Model` in `task/model.py`
    - implementations: `config/model/`
    - initialize or load a model
- `setting`:
    - protocol: `GlobalSetting` in `task/state.py`
    - implementations: `config/setting/`
    - register a global setting shared by all processes.
    - (handled by the system)
- `analysis`:
    - protocol: `Analysis` in `task/analysis.py`
    - implementations: `config/analysis/`
    - run analyses on the result of the main task (e.g. plotting, summary)
    - (handled by the system)

## Argparser

The `argparser` attribute is an instance of`ArgParser` defined in `task/task.py` which is basically the same as python's built-in `argparse.ArgumentParser` with the following new features:

- optimized for extensibility.
- allow to remove argument by using `remove_argument()`.
- `add_argument()` accepts a `condition` keyword to enable/disable the argument based on a flag defined in the task.

The `defaults` attribute can be used set the default values for the removed arguments.

The argparsers will be stacked through the inheritance of the task classes following the method resolution order (MRO).

The parsed arguments are available as `self.opts` before the `self.__init__()` is called.

The example below illustrates how the argparser works:

```python
class Base(Task):
    argparser = ArgParser()
    argparser.add_argument("--base-arg")
    argparser.add_argument("--optional-arg", condition="enable_optional")
    # enable `--optional-arg`
    enable_optional = True 

    def __init__(self):
        print(self.opts)

class DerivedA(Base):
    argparser = ArgParser()
    argparser.add_argument("--derived-arg")
    # disable `--optional-arg`
    enable_optional = False 

class DerivedB(Base):
    argparser = ArgParser()
    # remove `--base-arg`
    argparser.remove_argument("--base-arg")
    defaults = {"base_arg": "base_arg for DerivedB"}
    # enable `--optional-arg`
    enable_optional = True 
```

The `init` called on each task will print the following:

```python
# Base
Namespace(base_arg=None, optional_arg=None)
# DerivedA
Namespace(base_arg=None, derived_arg=None)
# DerivedB
Namespace(optional_arg=None, base_arg='base_arg for DerivedB')
```

## Command-line Interface

The command-line has the following format:

```bash
./pyml.py \
    <main-task> [--<main-args> ...] \
    -<other-task> module.class [--other-args ...] \
    -<other-task> module.class [--other-args ...] \
    ...
```

which consists of:

- one main task:
    - `<main-task>`: the name of a file in `config/main/` (without `.py`)
    - special main tasks: `from`, `template`
    - `[--<main-args> ...]`: the arguments passed to the main task
- arbitrary number of other tasks, each has
    - `-<other-task>`: a task protocol `-dataset`, `-model`, `-setting`, `-analysis`
    - special other tasks: `-from`, `-template`, `-flag`
    - `module.class`: an import path relative to `config/` and the class name.
    - `[--other-args ...]`: the arguments passed to the other task

For example,

```bash
./pyml.py \
    train --device cuda \
    -dataset HCR.SvB.Background --metadata datasets_HH4b --norm 3 \
    -dataset HCR.SvB.Signal --metadata datasets_HH4b \
    -model HCR.SvB.ggF.baseline.Train \
    -setting IO "output: ./output-{timestamp}/" \
    -flag debug
```

The detailed usage can be viewed by:

```bash
./pyml.py help
```

## Workflow File (Recommended)

The commands can be structured into a yaml workflow file which can be loaded by the `from` or `template` main task. The workflow is a dictionary where the keys are the task protocols and the values are lists of tasks. Each task is a dictionary with two keys: the `module` is the import path, and the `option` is a list of arguments. Multiple workflow files can be combined by the argument `-from` or `-template`.

The example command above is equivalent to the following workflow file:

```yaml
main:
  module: train
  option:
    - --device cuda
flag:
  - debug
dataset:
  - module: HCR.SvB.Background
    option:
      - --metadata datasets_HH4b
      - --norm 3
  - module: HCR.SvB.Signal
    option:
      - --metadata datasets_HH4b
model:
  - module: HCR.SvB.ggF.baseline.Train
setting:
  - module: IO
    option:
      - output: ./output-{timestamp}/
```

where the `setting` and the arguments labeled with `[embed]` in the help accept inplace dictionaries as options. `expand` and `workflow` main task can be used to convert back-and-forth between command-line and workflow file.

## Tips

- Do NOT import any large modules or code that depend on those modules (e.g. `torch`, `numpy`, `pandas`, `base_class.root`, `classifier.ml`, etc) at the top-level in any files located under `classifier/config/`. Instead, import them inside the scope that use them. Otherwise, the `autocomplete`, `help` functions will be dramatically slowed down.
