import os
import ROOT
import argparse
import logging
import json
ROOT.gROOT.SetBatch(True)


def json_to_TH1( coffea_hist, iname, rebin ):
    """docstring for hist_to_root"""

    edges     = coffea_hist['edges']
    centers   = coffea_hist['centers']
    values    = coffea_hist['values']
    variances = coffea_hist['variances']
    underflow_value      = coffea_hist['underflow_value']
    underflow_variance   = coffea_hist['underflow_variance']
    overflow_value       = coffea_hist['overflow_value']  
    overflow_variance    = coffea_hist['overflow_variance']

    rHist = ROOT.TH1F(iname, iname, len(centers), edges[0], edges[-1])
    rHist.Sumw2()

    rHist.SetBinContent(0, underflow_value)
    rHist.SetBinError(0, ROOT.TMath.Sqrt(underflow_variance))

    for ibin in range(1, len(centers)+1 ):
        rHist.SetBinContent(ibin, values[ibin-1])
        rHist.SetBinError(ibin, ROOT.TMath.Sqrt(variances[ibin-1]))

    rHist.SetBinContent( len(centers)+1, overflow_value)
    rHist.SetBinError( len(centers)+1, ROOT.TMath.Sqrt(overflow_variance))

    rHist.Rebin( rebin )

    return rHist

def create_root_file(file_to_convert, _, output_dir):
    logging.info( "in create_root_file")
    coffea_hists = json.load(open(file_to_convert, 'r'))
    logging.info( "leaded coffea_hists")

    root_hists = {}
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logging.info( "made dirs")
    output = output_dir + "/" + (file_to_convert.split("/")
                                 [-1].replace(".json", "")) + ".root"

    root_file = ROOT.TFile(output, 'recreate')

    for ih in coffea_hists.keys():
        for iprocess in coffea_hists[ih].keys():
            for iy in coffea_hists[ih][iprocess].keys():
                for itag in coffea_hists[ih][iprocess][iy].keys():
                    for iregion in coffea_hists[ih][iprocess][iy][itag].keys():
                        this_hist = json_to_TH1(
                            coffea_hists[ih][iprocess][iy][itag][iregion],
                            ih.replace(".", "_") + "_" + iprocess + "_" + iy + "_" + itag + "_" + iregion,
                            1)
                        print( 'Converting hist', ih, ih.replace(".", "_") + "_" + iprocess + "_" + iy + "_" + itag + "_" + iregion)
                        this_hist.Write()

    root_file.Close()
    logging.info("\n File " + output + " created.")


if __name__ == '__main__':

    #
    # input parameters
    #
    parser = argparse.ArgumentParser(
        description='Convert json hist to root TH1F', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-o', '--output_dir', dest="output_dir",
                        default="./datacards/", help='Output directory.')
    parser.add_argument('--histos', dest="histos", nargs="+",
                        default=[ ], help='List of histograms to convert')
    parser.add_argument('-f', '--file', dest='file_to_convert',
                        default="histos/histAll.json", help="File with coffea hists")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info("\nRunning with these parameters: ")
    logging.info(args)

    logging.info("Creating root files from json")
    create_root_file(args.file_to_convert, args.histos, args.output_dir)
