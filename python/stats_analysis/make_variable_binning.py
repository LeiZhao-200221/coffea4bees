import argparse
import ROOT
import array
import numpy as np
from convert_json_to_root import create_root_file

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def compute_variable_binning(multijet_hist, signal_hist, threshold):
    """
       multijet_hist and signal_hist are ROOT TH1 histograms
    """

    # Sum the last elements of multijet bkg until the sum is greater than the threshold
    total_nbins = multijet_hist.GetNbinsX()
    multijet_bin = total_nbins
    for ibin in range(total_nbins-1, 0, -1):
        multijet_integral = multijet_hist.Integral(ibin, multijet_bin)
        # print(ibin, total_nbins, multijet_bin, multijet_integral)
        if multijet_integral > threshold:
            multijet_bin = ibin
            break
    print(f"Multijet bin: {multijet_bin}, lowedgebin: {multijet_hist.GetBinLowEdge(multijet_bin)}, integral: {multijet_integral}, threshold: {threshold}")
    
    ## Check the binning of the signal asuming multijet binning threshold
    signal_binning = signal_hist.Integral(multijet_bin, total_nbins)
    print(f"Signal integral: {signal_binning}")
    # signal_binning = signal_binning - (np.sqrt(signal_binning))
    signal_binning = signal_binning - (0.05*signal_binning)
    print(f"Signal integral threshold: {signal_binning}")
    variable_binning = [1, signal_hist.GetBinLowEdge(multijet_bin)]
    print(f"Variable binning initial: {variable_binning}")
    higher_bin = multijet_bin
    for ibin in range(multijet_bin-1, 0, -1):
        # print(higher_bin, ibin, signal_hist.GetBinLowEdge(ibin), signal_hist.GetBinLowEdge(higher_bin))
        tmp_signal_binning = signal_hist.Integral(ibin, higher_bin)
        # print(signal_binning, tmp_signal_binning)
        if tmp_signal_binning > signal_binning:
            variable_binning.append(signal_hist.GetBinLowEdge(ibin))
            higher_bin = ibin-1
            continue

    variable_binning.append(signal_hist.GetBinLowEdge(1))
    variable_binning = array.array('d', variable_binning[::-1])
    print(f"Variable binning: {variable_binning}")

    can = ROOT.TCanvas("can", "can", 800, 800)
    tmp_signal_hist = rebin_histogram( signal_hist.Clone("new"), variable_binning)
    tmp_signal_hist.Draw()
    can.SaveAs("signal_rebin.pdf")

    return variable_binning

def rebin_histogram(hist, variable_binning):
    """
       hist is a ROOT TH1 histogram
    """
    return hist.Rebin(len(variable_binning) - 1, hist.GetName()+'_rebin', array.array('d', variable_binning))

def make_variable_binning(input_file, hist_name, threshold, output_file):
    
    # Open the ROOT file
    file = ROOT.TFile.Open(input_file)
    if not file or file.IsZombie():
        print(f"It is not a ROOT file, creating a ROOT file '{input_file.replace('.json', '.root')}'")
        create_root_file(input_file, hist_name, '/'.join(input_file.split("/")[:-1]))
        file = ROOT.TFile.Open(input_file.replace(".json", ".root"))
        
    # Retrieve the histograms
    hist_name = hist_name.replace(".", "_")
    multijet_hist = file.Get(f"{hist_name}_data_UL16_preVFP_threeTag_SR")
    signal_hist = file.Get(f"{hist_name}_GluGluToHHTo4B_cHHH1_UL16_preVFP_fourTag_SR")
    for iy in [ 'UL16_postVFP', 'UL17', 'UL18']:
        multijet_hist.Add(file.Get(f"{hist_name}_data_{iy}_threeTag_SR"))
        signal_hist.Add(file.Get(f"{hist_name}_GluGluToHHTo4B_cHHH1_{iy}_fourTag_SR"))
    
    can = ROOT.TCanvas("can", "can", 800, 800)
    signal_hist.Draw()
    can.SaveAs("signal.pdf")

    variable_binning = compute_variable_binning(multijet_hist, signal_hist, threshold)

    if output_file:
        # Create a new ROOT file to save the rebinned histograms
        output = ROOT.TFile(output_file, "RECREATE")

        # Rebin all histograms in the file using variable_binning
        for key in file.GetListOfKeys():
            hist = key.ReadObj()
            if isinstance(hist, ROOT.TH1) and (hist_name in hist.GetName()):
                rebinned_hist = rebin_histogram( hist, variable_binning)
                rebinned_hist.Write()
                # print(f"Rebinned histogram '{hist.GetName()}'")

        # Close the ROOT file
        file.Close()
        output.Close()
        
    return variable_binning



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make variable binning study",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_file", default = "histsAll.root", type=str, help="Path to the input ROOT file")
    parser.add_argument("-o", "--output_file", default = "histAll_rebinned.root", type=str, help="Path to the output ROOT file")
    parser.add_argument("-n", "--hist_name", default = "SvB_MA.ps_hh_fine", type=str, help="Name of the histogram to rebin")
    parser.add_argument('-t', '--threshold', type=float, default=10.0, help='Threshold value')
    

    args = parser.parse_args()

    make_variable_binning(args.input_file, args.hist_name, args.threshold, args.output_file)