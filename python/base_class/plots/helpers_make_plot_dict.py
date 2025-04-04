"""
Helper functions for creating plot dictionaries from histogram data.

This module provides functions to:
- Extract histogram data from input files
- Create plot configurations for different types of plots (1D, 2D, ratios)
- Handle stacked and unstacked histograms
- Manage plot metadata and styling
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import copy
import base_class.plots.helpers as plot_helpers
import hist
import numpy as np


def print_list_debug_info(process, tag, cut, region):
    print(f" hist process={process}, "
          f"tag={tag}, _cut={cut}"
          f"_reg={region}")


#
#  Get hist values
#
def get_hist_data(*, process: str, cfg: Any, config: Dict, var: str, region: str, cut: str, rebin: int, year: str, do2d: bool = False, file_index: Optional[int] = None, debug: bool = False) -> hist.Hist:
    """
    Extract histogram data for a given process and configuration.
    
    Args:
        process: Name of the process to extract
        cfg: Configuration object containing histogram data
        config: Dictionary of plot configuration options
        var: Variable to plot
        region: Analysis region
        cut: Selection cut to apply
        rebin: Rebinning factor
        year: Data taking year
        do2d: Whether to extract 2D histogram data
        file_index: Index of input file to use (if multiple files)
        debug: Enable debug output
        
    Returns:
        hist.Hist: Extracted histogram data
        
    Raises:
        ValueError: If histogram data cannot be found
    """

    if year in  ["RunII", "Run2", "Run3", "RunIII"]:
        year     = sum

    if debug:
        print(f" hist process={process}, "
              f"tag={config.get('tag', None)}, year={year}, var={var}")

    hist_opts = {"process": process,
                 "year":  year,
                 "tag":   config.get("tag", None),
                 "region": region
                 }

    if region == "sum":
        hist_opts["region"] = sum

    cut_dict = plot_helpers.get_cut_dict(cut, cfg.cutList)

    hist_opts = hist_opts | cut_dict

    hist_obj = None
    if len(cfg.hists) > 1 and not cfg.combine_input_files:
        if file_index is None:
            print("ERROR must give file_index if running with more than one input file without using the  --combine_input_files option")

        common, unique_to_dict = plot_helpers.compare_dict_keys_with_list(hist_opts, cfg.hists[file_index]['categories'])

        if len(unique_to_dict) > 0:
            for _key in unique_to_dict:
                hist_opts.pop(_key)

        hist_obj = cfg.hists[file_index]['hists'][var]

        if "variation" in cfg.hists[file_index]["categories"]:
            hist_opts = hist_opts | {"variation" : "nominal"}

    else:
        for _input_data in cfg.hists:

            common, unique_to_dict = plot_helpers.compare_dict_keys_with_list(hist_opts, _input_data['categories'])

            if len(unique_to_dict) > 0:
                for _key in unique_to_dict:
                    hist_opts.pop(_key)

            if var in _input_data['hists'] and process in _input_data['hists'][var].axes["process"]:

                if "variation" in _input_data["categories"]:
                    hist_opts = hist_opts | {"variation" : "nominal"}

                hist_obj = _input_data['hists'][var]

    if hist_obj is None:
        raise ValueError(f"ERROR did not find var {var} with process {process} in inputs")

    ## for backwards compatibility
    for axis in hist_obj.axes:
        if (axis.name == "tag") and isinstance(axis, hist.axis.IntCategory):
            hist_opts['tag'] = hist.loc(cfg.plotConfig["codes"]["tag"][config["tag"]])
        if (axis.name == "region") and isinstance(axis, hist.axis.IntCategory):
            if isinstance(hist_opts['region'], list):
                hist_opts['region'] = [ hist.loc(cfg.plotConfig["codes"]["region"][i]) for i in hist_dict['region'] ]
            elif region != "sum":
                hist_opts['region'] = hist.loc(cfg.plotConfig["codes"]["region"][region])

    #
    #  Add rebin Options
    #
    varName = hist_obj.axes[-1].name
    if not do2d:
        var_dict = {varName: hist.rebin(rebin)}
        hist_opts = hist_opts | var_dict

    #
    #  Do the hist selection/binngin
    #
    selected_hist = hist_obj[hist_opts]

    #
    # Catch list vs hist
    #  Shape give (nregion, nBins)
    #
    if do2d:
        if len(selected_hist.shape) == 3:  # for 2D plots
            selected_hist = selected_hist[sum, :, :]
    else:
        if len(selected_hist.shape) == 2:
            selected_hist = selected_hist[sum, :]

    #
    # Apply Scale factor
    #
    selected_hist *= config.get("scalefactor", 1.0)

    return selected_hist



#
def get_hist_data_list(*, proc_list: List[str], cfg: Any, config: Dict, var: str, region: str, cut: str, rebin: int, year: str, do2d: bool, file_index: Optional[int], debug: bool) -> hist.Hist:
    """
    Extract and combine histogram data for a list of processes.
    
    Args:
        proc_list: List of process names to combine
        cfg: Configuration object containing histogram data
        config: Dictionary of plot configuration options
        var: Variable to plot
        region: Analysis region
        cut: Selection cut to apply
        rebin: Rebinning factor
        year: Data taking year
        do2d: Whether to extract 2D histogram data
        file_index: Index of input file to use (if multiple files)
        debug: Enable debug output
        
    Returns:
        hist.Hist: Combined histogram data
    """

    selected_hist = None
    for _proc in proc_list:

        if type(_proc) is list:
            _selected_hist =  get_hist_data_list(proc_list=_proc, cfg=cfg, config=config, var=var, region=region,
                                                 cut=cut, rebin=rebin, year=year, do2d=do2d, file_index=file_index, debug=debug)
        else:
            _selected_hist = get_hist_data(process=_proc, cfg=cfg, config=config, var=var, region=region,
                                           cut=cut, rebin=rebin, year=year, do2d=do2d, file_index=file_index, debug=debug)

        if selected_hist is None:
            selected_hist = _selected_hist
        else:
            selected_hist += _selected_hist

    return selected_hist


#
#  Get hist from input file(s)
#
def add_hist_data(*, cfg, config, var, region, cut, rebin, year, do2d=False, file_index=None, debug=False):

    if debug:
        print(f"In add_hist_data {config['process']} \n")

    proc_list = config['process'] if type(config['process']) is list else [config['process']]

    selected_hist = get_hist_data_list(proc_list=proc_list, cfg=cfg, config=config, var=var, region=region,
                                       cut=cut, rebin=rebin, year=year, do2d=do2d, file_index=file_index, debug=debug)

    if do2d:

        # Extract counts and variances
        try:
            config["values"]    = selected_hist.view(flow=False)["value"].tolist()  # Bin counts (array)
            config["variances"] = selected_hist.view(flow=False)["variance"].tolist()  # Bin variances (array)
        except IndexError:
            config["values"]    = selected_hist.values()  # Bin counts (array)
            config["variances"] = selected_hist.variances()  # Bin variances (array)
        if config["variances"] is None:
            config["variances"] = np.zeros_like(config["values"])

        config["x_edges"]   = selected_hist.axes[0].edges.tolist()  # X-axis edges
        config["y_edges"]   = selected_hist.axes[1].edges.tolist()  # Y-axis edges
        config["x_label"]   = selected_hist.axes[0].label  # X-axis label
        config["y_label"]   = selected_hist.axes[1].label  # Y-axis label

    else:
        config["values"]     = selected_hist.values().tolist()
        config["variances"]  = selected_hist.variances().tolist()
        config["centers"]    = selected_hist.axes[0].centers.tolist()
        config["edges"]      = selected_hist.axes[0].edges.tolist()
        config["x_label"]    = selected_hist.axes[0].label
        config["under_flow"] = float(selected_hist.view(flow=True)["value"][0])
        config["over_flow"]  = float(selected_hist.view(flow=True)["value"][-1])

    return



def _create_base_plot_dict(var: str, cut: str, region: str, process: Any, **kwargs) -> Dict:
    """Create the base plot dictionary structure."""
    plot_data = {
        "hists": {},
        "stack": {},
        "ratio": {},
        "var": var,
        "cut": cut,
        "region": region,
        "kwargs": kwargs,
        "process": process
    }
    return plot_data

def _handle_cut_list(plot_data: Dict, process_config: Dict, cfg: Any, var_to_plot: str, 
                    region: str, cut_list: List[str], rebin: int, year: str, do2d: bool, 
                    label_override: Optional[List[str]] = None, debug: bool = False) -> None:
    """Handle plotting multiple cuts."""
    for ic, _cut in enumerate(cut_list):
        if debug:
            print_list_debug_info(process_config["process"], process_config.get("tag"), _cut, region)

        _process_config = copy.deepcopy(process_config)
        _process_config["fillcolor"] = plot_helpers.colors[ic]
        _process_config["label"] = plot_helpers.get_label(f"{process_config['label']} {_cut}", label_override, ic)
        _process_config["histtype"] = "errorbar"

        add_hist_data(cfg=cfg, config=_process_config,
                     var=var_to_plot, region=region, cut=_cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)

        proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]
        plot_data["hists"][f"{proc_id}{_cut}{ic}"] = _process_config

def _handle_region_list(plot_data: Dict, process_config: Dict, cfg: Any, var_to_plot: str,
                       cut: str, region_list: List[str], rebin: int, year: str, do2d: bool,
                       label_override: Optional[List[str]] = None, debug: bool = False) -> None:
    """Handle plotting multiple regions."""
    for ir, _reg in enumerate(region_list):
        if debug:
            print_list_debug_info(process_config["process"], process_config.get("tag"), cut, _reg)

        _process_config = copy.deepcopy(process_config)
        _process_config["fillcolor"] = plot_helpers.colors[ir]
        _process_config["label"] = plot_helpers.get_label(f"{process_config['label']} {_reg}", label_override, ir)
        _process_config["histtype"] = "errorbar"

        add_hist_data(cfg=cfg, config=_process_config,
                     var=var_to_plot, region=_reg, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)

        proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]
        plot_data["hists"][f"{proc_id}{_reg}{ir}"] = _process_config

def _add_ratio_plots(plot_data: Dict, **kwargs) -> None:
    """
    Add ratio plots to the plot configuration.
    
    Args:
        plot_data: Plot data dictionary
        **kwargs: Additional plotting options including do2d
    """
    do2d = kwargs.get("do2d", False)
    if do2d:
        _add_2d_ratio_plots(plot_data, **kwargs)
    else:
        _add_1d_ratio_plots(plot_data, **kwargs)

def get_plot_dict_from_list(*, cfg: Any, var: str, cut: str, region: str, process: Any, **kwargs) -> Dict:
    """
    Create a plot dictionary from lists of processes, cuts, regions, etc.
    
    Args:
        cfg: Configuration object
        var: Variable to plot
        cut: Selection cut
        region: Analysis region
        process: Process or list of processes
        **kwargs: Additional plotting options
        
    Returns:
        Dict: Plot configuration dictionary
    """
    debug = kwargs.get("debug", False)
    if debug:
        print(f"in _makeHistFromList hist process={process}, cut={cut}")

    rebin = kwargs.get("rebin", 1)
    do2d = kwargs.get("do2d", False)
    var_over_ride = kwargs.get("var_over_ride", {})
    label_override = kwargs.get("labels", None)
    year = kwargs.get("year", "RunII")
    file_labels = kwargs.get("fileLabels", [])

    plot_data = _create_base_plot_dict(var, cut, region, process, **kwargs)

    # Parse process configuration
    if isinstance(process, list):
        process_config = [plot_helpers.get_value_nested_dict(cfg.plotConfig, p) for p in process]
    else:
        try:
            process_config = plot_helpers.get_value_nested_dict(cfg.plotConfig, process)
            proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]
        except ValueError:
            raise ValueError(f"\t ERROR process = {process} not in plotConfig! \n")
        var_to_plot = var_over_ride.get(process, var)

    # Handle different types of lists
    if isinstance(cut, list):
        _handle_cut_list(plot_data, process_config, cfg, var_to_plot, region, cut, rebin, year, do2d, label_override, debug)
    elif isinstance(region, list):
        _handle_region_list(plot_data, process_config, cfg, var_to_plot, cut, region, rebin, year, do2d, label_override, debug)
    elif len(cfg.hists) > 1 and not cfg.combine_input_files:
        _handle_input_files(plot_data, process_config, cfg, var_to_plot, region, cut, rebin, year, do2d, label_override, debug, file_labels)
    elif isinstance(process, list):
        _handle_process_list(plot_data, process_config, cfg, var, region, cut, rebin, year, do2d, var_over_ride, debug)
    elif isinstance(var, list):
        _handle_var_list(plot_data, process_config, cfg, var, region, cut, rebin, year, do2d, label_override, debug)
    elif isinstance(year, list):
        _handle_year_list(plot_data, process_config, cfg, var, region, cut, rebin, year, do2d, label_override, debug)
    else:
        raise ValueError("Error: At least one parameter must be a list!")

    # Handle ratio plots if requested
    if kwargs.get("doRatio", kwargs.get("doratio", False)):
        _add_ratio_plots(plot_data, **kwargs)

    return plot_data


def load_stack_config(*, cfg: Any, stack_config: Dict, var: str, cut: str, region: str, **kwargs) -> Dict:
    """
    Load and process stack configuration for plotting.
    
    Args:
        cfg: Configuration object
        stack_config: Dictionary of stack configuration options
        var: Variable to plot
        cut: Selection cut
        region: Analysis region
        **kwargs: Additional plotting options
        
    Returns:
        Dict: Processed stack configuration
    """
    stack_dict = {}
    var_over_ride = kwargs.get("var_over_ride", {})
    rebin = kwargs.get("rebin", 1)
    year = kwargs.get("year", "RunII")
    debug = kwargs.get("debug", False)
    do2d = kwargs.get("do2d", False)

    for _proc_name, _proc_config in stack_config.items():
        proc_config = copy.deepcopy(_proc_config)
        var_to_plot = var_over_ride.get(_proc_name, var)

        if debug:
            print(f"stack_process is {_proc_name} var is {var_to_plot}")

        if proc_config.get("process", None):
            add_hist_data(cfg=cfg, config=proc_config,
                         var=var_to_plot, region=region, cut=cut, rebin=rebin, year=year,
                         do2d=do2d, debug=debug)
            stack_dict[_proc_name] = proc_config
        elif proc_config.get("sum", None):
            _handle_stack_sum(proc_config, cfg, var_to_plot, region, cut, rebin, year, do2d, debug, var_over_ride)
            stack_dict[_proc_name] = proc_config
        else:
            raise ValueError("Error: Stack component must have either 'process' or 'sum' configuration")

    return stack_dict

def _handle_stack_sum(proc_config: Dict, cfg: Any, var_to_plot: str, region: str, 
                     cut: str, rebin: int, year: str, do2d: bool, debug: bool,
                     var_over_ride: Dict) -> None:
    """Handle stack components that are sums of processes."""
    for sum_proc_name, sum_proc_config in proc_config["sum"].items():
        sum_proc_config["year"] = proc_config["year"]
        var_to_plot = var_over_ride.get(sum_proc_name, var_to_plot)

        add_hist_data(cfg=cfg, config=sum_proc_config,
                     var=var_to_plot, region=region, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)

    # Combine values and variances
    stack_values = [v["values"] for _, v in proc_config["sum"].items()]
    proc_config["values"] = np.sum(stack_values, axis=0).tolist()

    stack_variances = [v["variances"] for _, v in proc_config["sum"].items()]
    proc_config["variances"] = np.sum(stack_variances, axis=0).tolist()

    # Copy metadata from first sum component
    first_sum_entry = next(iter(proc_config["sum"].values()))
    proc_config["centers"] = first_sum_entry["centers"]
    proc_config["edges"] = first_sum_entry["edges"]
    proc_config["x_label"] = first_sum_entry["x_label"]

    # Combine under/overflow
    stack_under_flow = [v["under_flow"] for _, v in proc_config["sum"].items()]
    proc_config["under_flow"] = float(np.sum(stack_under_flow, axis=0).tolist())

    stack_over_flow = [v["over_flow"] for _, v in proc_config["sum"].items()]
    proc_config["over_flow"] = float(np.sum(stack_over_flow, axis=0))

def get_values_variances_centers_from_dict(hist_config: Dict, plot_data: Dict) -> Tuple[np.ndarray, np.ndarray, List[float]]:
    """
    Extract values, variances and centers from histogram configuration.
    
    Args:
        hist_config: Histogram configuration dictionary
        plot_data: Plot data dictionary
        
    Returns:
        Tuple containing values, variances and centers arrays
        
    Raises:
        ValueError: If histogram type is invalid
    """
    if hist_config["type"] == "hists":
        num_data = plot_data["hists"][hist_config["key"]]
        return np.array(num_data["values"]), np.array(num_data["variances"]), num_data["centers"]

    if hist_config["type"] == "stack":
        return_values = [v["values"] for _, v in plot_data["stack"].items()]
        return_values = np.sum(return_values, axis=0)

        return_variances = [v["variances"] for _, v in plot_data["stack"].items()]
        return_variances = np.sum(return_variances, axis=0)

        centers = next(iter(plot_data["stack"].values()))["centers"]
        return return_values, return_variances, centers

    raise ValueError("ERROR: ratio needs to be of type 'hists' or 'stack'")

def add_ratio_plots(ratio_config: Dict, plot_data: Dict, **kwargs) -> None:
    """
    Add ratio plots to the plot configuration.
    
    Args:
        ratio_config: Ratio plot configuration
        plot_data: Plot data dictionary
        **kwargs: Additional plotting options
    """
    for r_name, _r_config in ratio_config.items():
        r_config = copy.deepcopy(_r_config)

        num_values, num_vars, num_centers = get_values_variances_centers_from_dict(r_config.get("numerator"), plot_data)
        den_values, den_vars, _ = get_values_variances_centers_from_dict(r_config.get("denominator"), plot_data)

        if kwargs.get("norm", False):
            r_config["norm"] = True

        # Add ratio plot
        ratios, ratio_uncert = plot_helpers.makeRatio(num_values, num_vars, den_values, den_vars, **r_config)
        r_config["ratio"] = ratios.tolist()
        r_config["error"] = ratio_uncert.tolist()
        r_config["centers"] = num_centers
        plot_data["ratio"][f"ratio_{r_name}"] = r_config

        # Add background error band
        default_band_config = {"color": "k", "type": "band", "hatch": "\\\\\\"}
        _band_config = r_config.get("bkg_err_band", default_band_config)

        if _band_config:
            band_config = copy.deepcopy(_band_config)
            band_config["ratio"] = np.ones(len(num_centers)).tolist()
            den_values[den_values == 0] = plot_helpers.epsilon
            band_config["error"] = np.sqrt(den_vars * np.power(den_values, -2.0)).tolist()
            band_config["centers"] = list(num_centers)
            plot_data["ratio"][f"band_{r_name}"] = band_config

def get_plot_dict_from_config(*, cfg: Any, var: str = 'selJets.pt',
                            cut: str = "passPreSel", region: str = "SR", **kwargs) -> Dict:
    """
    Create a plot dictionary from configuration.
    
    Args:
        cfg: Configuration object
        var: Variable to plot
        cut: Selection cut
        region: Analysis region
        **kwargs: Additional plotting options
        
    Returns:
        Dict: Plot configuration dictionary
        
    Raises:
        AttributeError: If cut is not in cutList
    """
    process = kwargs.get("process", None)
    year = kwargs.get("year", "RunII")
    rebin = kwargs.get("rebin", 1)
    do2d = kwargs.get("do2d", False)
    debug = kwargs.get("debug", False)

    # Make process a list if it exists and isn't one already
    if process is not None and not isinstance(process, list):
        process = [process]

    var_over_ride = kwargs.get("var_over_ride", {})

    if cut and cut not in cfg.cutList:
        raise AttributeError(f"{cut} not in cutList {cfg.cutList}")

    # Initialize plot data structure
    plot_data = {
        "hists": {},
        "stack": {},
        "ratio": {},
        "var": var,
        "cut": cut,
        "region": region,
        "kwargs": kwargs
    }
    if do2d:
        plot_data["process"] = process[0]
        plot_data["is_2d_hist"] = True

    # Get histogram configuration
    hist_config = cfg.plotConfig["hists"]
    if process is not None:
        hist_config = {key: hist_config[key] for key in process if key in hist_config}

    # Process each histogram
    for _proc_name, _proc_config in hist_config.items():
        proc_config = copy.deepcopy(_proc_config)
        proc_config["name"] = _proc_name
        var_to_plot = var_over_ride.get(_proc_name, var)

        add_hist_data(cfg=cfg, config=proc_config,
                     var=var_to_plot, region=region, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)
        plot_data["hists"][_proc_name] = proc_config

    # Process stack configuration
    stack_config = cfg.plotConfig.get("stack", {})
    if process is not None:
        stack_config = {key: stack_config[key] for key in process if key in stack_config}

    plot_data["stack"] = load_stack_config(cfg=cfg, stack_config=stack_config, 
                                         var=var, cut=cut, region=region, **kwargs)

    # Add ratio plots if requested
    if kwargs.get("doRatio", kwargs.get("doratio", False)) and not do2d:
        ratio_config = cfg.plotConfig["ratios"]
        add_ratio_plots(ratio_config, plot_data, **kwargs)

    return plot_data

def _handle_input_files(plot_data: Dict, process_config: Dict, cfg: Any, var_to_plot: str,
                       region: str, cut: str, rebin: int, year: str, do2d: bool,
                       label_override: Optional[List[str]] = None, debug: bool = False,
                       file_labels: Optional[List[str]] = None) -> None:
    """Handle plotting from multiple input files."""
    if debug:
        print_list_debug_info(process_config["process"], process_config.get("tag"), cut, region)

    file_labels = file_labels or []
    proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]

    for iF, _input_file in enumerate(cfg.hists):
        _process_config = copy.deepcopy(process_config)
        _process_config["fillcolor"] = plot_helpers.colors[iF]

        if label_override:
            _process_config["label"] = label_override[iF]
        elif iF < len(file_labels):
            _process_config["label"] = f"{_process_config['label']} {file_labels[iF]}"
        else:
            _process_config["label"] = f"{_process_config['label']} file{iF + 1}"

        _process_config["histtype"] = "errorbar"

        add_hist_data(cfg=cfg, config=_process_config,
                     var=var_to_plot, region=region, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, file_index=iF, debug=debug)

        plot_data["hists"][f"{proc_id}file{iF}"] = _process_config

def _handle_process_list(plot_data: Dict, process_config: List[Dict], cfg: Any, var: str,
                        region: str, cut: str, rebin: int, year: str, do2d: bool,
                        var_over_ride: Dict, debug: bool = False) -> None:
    """Handle plotting multiple processes."""
    for iP, _proc_conf in enumerate(process_config):
        if debug:
            print_list_debug_info(_proc_conf["process"], _proc_conf.get("tag"), cut, region)

        _process_config = copy.deepcopy(_proc_conf)
        _process_config["fillcolor"] = _proc_conf.get("fillcolor", None)
        _process_config["histtype"] = "errorbar"

        _proc_id = _proc_conf["label"] if isinstance(_proc_conf["process"], list) else _proc_conf["process"]
        var_to_plot = var_over_ride.get(_proc_id, var)

        add_hist_data(cfg=cfg, config=_process_config,
                     var=var_to_plot, region=region, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)

        plot_data["hists"][f"{_proc_id}{iP}"] = _process_config

def _handle_var_list(plot_data: Dict, process_config: Dict, cfg: Any, var_list: List[str],
                    region: str, cut: str, rebin: int, year: str, do2d: bool,
                    label_override: Optional[List[str]] = None, debug: bool = False) -> None:
    """Handle plotting multiple variables."""
    proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]

    for iv, _var in enumerate(var_list):
        if debug:
            print_list_debug_info(process_config["process"], process_config.get("tag"), cut, region)

        _process_config = copy.deepcopy(process_config)
        _process_config["fillcolor"] = plot_helpers.colors[iv]
        _process_config["label"] = plot_helpers.get_label(f"{process_config['label']} {_var}", label_override, iv)
        _process_config["histtype"] = "errorbar"

        add_hist_data(cfg=cfg, config=_process_config,
                     var=_var, region=region, cut=cut, rebin=rebin, year=year,
                     do2d=do2d, debug=debug)

        plot_data["hists"][f"{proc_id}{_var}{iv}"] = _process_config

def _handle_year_list(plot_data: Dict, process_config: Dict, cfg: Any, var: str,
                     region: str, cut: str, rebin: int, year_list: List[str], do2d: bool,
                     label_override: Optional[List[str]] = None, debug: bool = False) -> None:
    """Handle plotting multiple years."""
    proc_id = process_config["label"] if isinstance(process_config["process"], list) else process_config["process"]

    for iy, _year in enumerate(year_list):
        if debug:
            print_list_debug_info(process_config["process"], process_config.get("tag"), cut, region)

        _process_config = copy.copy(process_config)
        _process_config["fillcolor"] = plot_helpers.colors[iy]
        _process_config["label"] = plot_helpers.get_label(f"{process_config['label']} {_year}", label_override, iy)
        _process_config["histtype"] = "errorbar"

        add_hist_data(cfg=cfg, config=_process_config,
                     var=var, region=region, cut=cut, rebin=rebin, year=_year,
                     do2d=do2d, debug=debug)

        plot_data["hists"][f"{proc_id}{_year}{iy}"] = _process_config

def _add_2d_ratio_plots(plot_data: Dict, **kwargs) -> None:
    """Add 2D ratio plots."""
    hist_keys = list(plot_data["hists"].keys())
    den_key = hist_keys.pop(0)

    den_values = np.array(plot_data["hists"][den_key]["values"])
    den_vars = plot_data["hists"][den_key]["variances"]
    den_values[den_values == 0] = plot_helpers.epsilon

    num_key = hist_keys.pop(0)
    num_values = np.array(plot_data["hists"][num_key]["values"])
    num_vars = plot_data["hists"][num_key]["variances"]

    ratio_config = {}
    ratios, ratio_uncert = plot_helpers.makeRatio(num_values, num_vars, den_values, den_vars, **kwargs)
    ratio_config["ratio"] = ratios.tolist()
    ratio_config["error"] = ratio_uncert.tolist()
    plot_data["ratio"][f"ratio_{num_key}_to_{den_key}"] = ratio_config

def _add_1d_ratio_plots(plot_data: Dict, **kwargs) -> None:
    """Add 1D ratio plots."""
    hist_keys = list(plot_data["hists"].keys())
    den_key = hist_keys.pop(0)

    den_values = np.array(plot_data["hists"][den_key]["values"])
    den_vars = plot_data["hists"][den_key]["variances"]
    den_centers = plot_data["hists"][den_key]["centers"]

    den_values[den_values == 0] = plot_helpers.epsilon

    # Add background error band
    band_ratios = np.ones(len(den_centers))
    band_uncert = np.sqrt(den_vars * np.power(den_values, -2.0))
    band_config = {
        "color": "k",
        "type": "band",
        "hatch": "\\\\",
        "ratio": band_ratios.tolist(),
        "error": band_uncert.tolist(),
        "centers": list(den_centers)
    }
    plot_data["ratio"]["bkg_band"] = band_config

    # Add ratio plots for each histogram
    for iH, _num_key in enumerate(hist_keys):
        num_values = np.array(plot_data["hists"][_num_key]["values"])
        num_vars = plot_data["hists"][_num_key]["variances"]

        ratio_config = {
            "color": plot_helpers.colors[iH],
            "marker": "o"
        }
        ratios, ratio_uncert = plot_helpers.makeRatio(num_values, num_vars, den_values, den_vars, **kwargs)
        ratio_config["ratio"] = ratios.tolist()
        ratio_config["error"] = ratio_uncert.tolist()
        ratio_config["centers"] = den_centers
        plot_data["ratio"][f"ratio_{_num_key}_to_{den_key}_{iH}"] = ratio_config
