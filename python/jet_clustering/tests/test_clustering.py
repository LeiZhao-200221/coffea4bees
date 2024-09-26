import unittest
#import argparse
from coffea.util import load
import yaml
#from parser import wrapper
import sys

import numpy as np
import awkward as ak
from coffea.nanoevents.methods import vector
import time
from copy import copy
import os

sys.path.insert(0, os.getcwd())
from jet_clustering.clustering   import kt_clustering, cluster_bs, cluster_bs_fast, cluster_bs_numba
from jet_clustering.declustering import compute_decluster_variables, decluster_combined_jets, make_synthetic_event, get_list_of_splitting_types, clean_ISR, get_list_of_ISR_splittings, children_jet_flavors, get_list_of_all_sub_splittings, get_list_of_combined_jet_types, get_splitting_summary, get_splitting_name

#import vector
#vector.register_awkward()
from coffea.nanoevents.methods.vector import ThreeVector
import fastjet




class clusteringTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        #
        #  Read in the pdfs
        #
        #  Make with ../.ci-workflows/synthetic-dataset-plot-job.sh
        # input_pdf_file_name = "analysis/plots_synthetic_datasets/clustering_pdfs.yml"
        input_pdf_file_name = "jet_clustering/jet-splitting-PDFs-00-07-00/clustering_pdfs_vs_pT.yml"
        #input_pdf_file_name = "jet_clustering/clustering_PDFs/clustering_pdfs_vs_pT.yml"
        with open(input_pdf_file_name, 'r') as input_file:
            self.input_pdfs = yaml.safe_load(input_file)

        #        self.inputFile = wrapper.args["inputFile"]

        #
        # From 4jet events
        #   (from analysis.helpers.topCandReconstruction import dumpTopCandidateTestVectors
        #
        self.input_jet_pt_4  = [[150.25, 127.8125, 60.875, 46.34375], [169.5, 105.3125, 82.375, 63.0], [174.625, 116.5625, 98.875, 58.96875], [297.75, 152.125, 108.3125, 49.875], [232.0, 176.5, 79.4375, 61.84375], [113.5625, 60.78125, 58.84375, 54.40625], [154.875, 137.75, 102.4375, 64.125], [229.75, 156.875, 109.75, 53.21875], [117.125, 94.75, 57.0, 56.1875], [149.875, 116.8125, 97.75, 42.5]]
        self.input_jet_eta_4 = [[0.708740234375, 2.24365234375, -0.37176513671875, -0.5455322265625], [-0.632080078125, 0.4456787109375, -0.27459716796875, -0.04097747802734375], [-2.03564453125, -0.10174560546875, -0.553466796875, -1.352783203125], [-0.26214599609375, -0.5142822265625, 0.6898193359375, 0.8153076171875], [1.438232421875, -0.66015625, 1.7353515625, 2.0283203125], [0.5064697265625, -1.33837890625, 1.122314453125, 0.31939697265625], [1.6240234375, 0.073394775390625, -2.119140625, -2.2568359375], [2.0361328125, 1.675048828125, 0.95849609375, 0.54150390625], [0.14300537109375, 0.9183349609375, -1.08251953125, 1.379150390625], [0.500244140625, -0.0623931884765625, -0.701416015625, -0.88671875]]
        self.input_jet_phi_4 = [[2.4931640625, -0.48309326171875, 2.66259765625, -1.79443359375], [-0.2913818359375, 2.51220703125, -2.73876953125, 0.58349609375], [-2.220703125, 0.6153564453125, 1.251708984375, -1.930908203125], [-1.36962890625, 1.342041015625, 1.99609375, 2.5849609375], [-0.1124420166015625, 2.6875, -2.44775390625, 0.168304443359375], [2.546875, 1.327392578125, -0.794189453125, -0.979248046875], [2.95556640625, 0.7203369140625, -1.276611328125, -0.4969482421875], [1.421630859375, -1.33935546875, -1.302978515625, -3.140625], [-2.45751953125, 0.27557373046875, 1.65087890625, -0.6121826171875], [-3.08984375, -0.14752197265625, 0.2174072265625, -2.95947265625]]
        self.input_jet_mass_4 = [[16.8125, 24.96875, 9.5390625, 6.18359375], [18.859375, 15.296875, 13.5, 7.7421875], [20.5, 16.96875, 11.7265625, 10.7421875], [20.421875, 16.921875, 16.46875, 9.1875], [32.3125, 18.015625, 10.4140625, 13.40625], [14.046875, 9.625, 12.3984375, 8.3515625], [19.3125, 22.875, 13.671875, 12.0234375], [32.15625, 11.8125, 17.25, 11.3828125], [17.0, 14.953125, 9.046875, 11.5], [15.65625, 16.890625, 17.640625, 7.9921875]]

        self.input_jet_flavor_4 = [["b"] * 4] * len(self.input_jet_pt_4)

        self.input_jets_4 = ak.zip(
            {
                "pt": self.input_jet_pt_4,
                "eta": self.input_jet_eta_4,
                "phi": self.input_jet_phi_4,
                "mass": self.input_jet_mass_4,
                "jet_flavor": self.input_jet_flavor_4,
                "btagDeepFlavB": self.input_jet_pt_4, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )

        self.input_jet_pt_5  = [[256.330078125, 133.5384521484375, 120.5, 56.39178466796875, 29.992462158203125], [134.58294677734375, 84.63372802734375, 69.49273681640625, 68.5399169921875, 52.375], [235.428466796875, 190.12060546875, 71.2095947265625, 65.34912109375, 60.4375], [205.2244873046875, 107.375, 94.7037353515625, 93.92022705078125, 92.0400390625], [178.065185546875, 120.625, 94.33807373046875, 84.4742431640625, 72.0380859375], [128.86138916015625, 126.4375, 119.819580078125, 60.375732421875, 47.94287109375], [161.7626953125, 74.89837646484375, 71.490478515625, 56.180023193359375, 50.375], [230.293212890625, 136.250244140625, 62.6171875, 58.7060546875, 49.34375], [228.0, 173.1611328125, 96.181640625, 79.3907470703125, 76.552734375], [128.54522705078125, 106.4375, 84.93209838867188, 64.737548828125, 49.700469970703125]]
        self.input_jet_eta_5  = [[0.8936767578125, 0.121337890625, 1.5341796875, -1.989501953125, -0.7362060546875], [0.29376220703125, 0.9923095703125, 1.52783203125, -0.06246185302734375, -1.863525390625], [2.14892578125, -0.574951171875, -1.082763671875, -0.26849365234375, 0.566650390625], [0.25811767578125, -1.43603515625, 1.063720703125, 1.9384765625, 0.408935546875], [0.46978759765625, 1.232666015625, -1.802734375, -1.022705078125, -1.654052734375], [1.38623046875, 0.6514892578125, 1.039794921875, -0.588623046875, 0.49981689453125], [1.182861328125, 0.174346923828125, -0.564208984375, 1.013671875, -1.2578125], [0.45703125, -0.30816650390625, -0.528564453125, 2.0302734375, -0.859375], [-2.0966796875, -0.52490234375, 0.931640625, 0.096832275390625, -0.21209716796875], [0.046417236328125, -0.7169189453125, 1.510986328125, 0.0444183349609375, 0.19891357421875]]
        self.input_jet_phi_5  = [[2.06884765625, 5.5608954429626465, -1.4248046875, 3.7079901695251465, 1.1357421875], [3.7953925132751465, 0.8619384765625, 0.7774658203125, 6.2029852867126465, 3.04150390625], [1.671142578125, 4.9018378257751465, 5.0817694664001465, 5.3899970054626465, 2.7255859375], [5.0261054039001465, 2.37890625, 2.68701171875, 0.7398681640625, 6.0952277183532715], [1.554931640625, -3.13134765625, 5.6200995445251465, 0.2047119140625, 4.4792304039001465], [2.47021484375, 1.626953125, 4.9301581382751465, 6.0857672691345215, 4.9946112632751465], [1.499267578125, 4.5829901695251465, 4.7106757164001465, 5.0483222007751465, -2.0654296875], [4.3429999351501465, 1.481689453125, 0.78515625, 0.6368408203125, 1.269775390625], [-2.8740234375, 1.008544921875, 4.2407050132751465, 5.5678534507751465, 0.562255859375], [1.16943359375, -2.26611328125, 4.9030585289001465, 5.8507513999938965, 1.7421875]]
        self.input_jet_mass_5  = [[18.3929443359375, 16.167137145996094, 20.8125, 9.837577819824219, 7.376430511474609], [18.627456665039062, 14.282325744628906, 10.098735809326172, 10.676605224609375, 12.8828125], [20.226531982421875, 35.16229248046875, 9.027721405029297, 14.4912109375, 9.1015625], [22.6912841796875, 19.15625, 15.039527893066406, 5.409450531005859, 13.238250732421875], [25.096435546875, 14.2734375, 11.000885009765625, 9.951026916503906, 10.315155029296875], [14.715652465820312, 11.21875, 14.8203125, 8.70376968383789, 8.22491455078125], [20.9124755859375, 10.833625793457031, 11.0955810546875, 10.830390930175781, 9.59375], [23.3994140625, 16.117172241210938, 10.51025390625, 10.590438842773438, 7.5078125], [23.140625, 24.85760498046875, 14.499320983886719, 12.903610229492188, 10.6402587890625], [25.775680541992188, 16.75, 12.032047271728516, 13.135284423828125, 6.7713165283203125]]
        self.input_jet_flavor_5  = [['b', 'b', 'j', 'b', 'b'], ['b', 'b', 'b', 'b', 'j'], ['b', 'b', 'b', 'b', 'j'], ['b', 'j', 'b', 'b', 'b'], ['b', 'j', 'b', 'b', 'b'], ['b', 'j', 'b', 'b', 'b'], ['b', 'b', 'b', 'b', 'j'], ['b', 'b', 'b', 'b', 'j'], ['j', 'b', 'b', 'b', 'b'], ['b', 'j', 'b', 'b', 'b']]
        self.input_btagDeepFlavB_5 = [[1.0] * 5] * len(self.input_jet_pt_5)# Dummy
        self.input_jets_5 = ak.zip(
            {
                "pt": self.input_jet_pt_5,
                "eta": self.input_jet_eta_5,
                "phi": self.input_jet_phi_5,
                "mass": self.input_jet_mass_5,
                "jet_flavor": self.input_jet_flavor_5,
                "btagDeepFlavB": self.input_jet_pt_5, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )

        self.input_jet_pt_bbj      = [[117.45941162109375, 88.99154663085938, 87.4119873046875, 63.419677734375, 29.453125], [100.06103515625, 73.87075805664062, 72.33502197265625, 51.287139892578125, 26.546875, 24.296875, 23.6875, 20.859375], [148.125, 102.0538330078125, 96.02734375, 93.0419921875, 77.5543212890625, 22.859375, 21.453125, 20.53125], [124.9375, 101.248291015625, 76.32794189453125, 60.34375, 59.03125, 58.67919921875, 58.44525146484375, 53.625, 44.71875], [168.7708740234375, 148.8355712890625, 131.60723876953125, 114.9873046875, 80.5625], [91.44287109375, 89.8497314453125, 53.0625, 52.611968994140625, 48.58992004394531, 32.6875], [134.1876220703125, 121.9676513671875, 60.878997802734375, 54.352783203125, 26.671875], [163.75, 107.653076171875, 94.9375, 83.68048095703125, 61.7420654296875, 61.53125, 38.12939453125], [188.375, 125.0625, 72.54299926757812, 66.5625, 54.622802734375, 45.521728515625], [164.951171875, 157.87939453125, 55.455963134765625, 46.22991943359375, 35.25]]
        self.input_jet_eta_bbj     = [[-0.263671875, -1.06103515625, 1.791748046875, -1.46337890625, 0.48992919921875], [0.0419769287109375, 0.03650665283203125, 0.6004638671875, 1.003173828125, 1.796630859375, 0.5921630859375, 1.13720703125, -1.43896484375], [1.4248046875, -1.441650390625, -0.1580810546875, -0.7156982421875, 0.596435546875, 2.03515625, -1.815673828125, -0.40679931640625], [-1.83349609375, 0.1121673583984375, -1.817138671875, 2.80419921875, 1.635986328125, -2.02490234375, -0.073455810546875, 1.0244140625, 2.3955078125], [-0.777099609375, -0.77099609375, -0.6082763671875, -0.45166015625, 0.1188201904296875], [1.110107421875, 0.9132080078125, -2.33447265625, 0.099578857421875, 0.908203125, 1.23974609375], [-0.576171875, -0.599853515625, 0.39227294921875, -1.322998046875, -0.13153076171875], [1.8603515625, 1.890625, 2.15087890625, 2.18603515625, -0.0839996337890625, -1.876220703125, 0.963134765625], [1.002685546875, -2.38916015625, 1.567138671875, 1.3095703125, 0.3037109375, -0.247314453125], [1.417236328125, -0.8421630859375, -0.582275390625, -0.359375, 1.044677734375]]
        self.input_jet_phi_bbj     = [[4.0922675132751465, 1.0703125, 2.73046875, 6.0312933921813965, 1.9189453125], [5.7095770835876465, 2.32275390625, 4.8061347007751465, 0.6533203125, 1.4697265625, 2.7373046875, -2.72607421875, -2.72998046875], [-0.99755859375, 5.2536444664001465, 1.982666015625, 1.7958984375, 1.978515625, 2.22998046875, 2.13671875, -0.29730224609375], [1.755126953125, 4.5390448570251465, 5.9088568687438965, -2.71533203125, -0.13885498046875, 0.717041015625, 2.740234375, 3.1171875, 0.6268310546875], [0.9737548828125, 1.568359375, 3.8549628257751465, 5.0243964195251465, -2.03857421875], [2.9033203125, 0.33795166015625, 2.482421875, 3.8188300132751465, 5.6412177085876465, -2.03515625], [0.179901123046875, 3.2392401695251465, 4.2534003257751465, 0.40570068359375, 2.36376953125], [1.628662109375, 6.1421942710876465, -1.920654296875, 4.8249335289001465, 3.6943182945251465, 2.06005859375, 1.7275390625], [1.259033203125, -1.13525390625, 3.6044745445251465, 3.001953125, 1.02880859375, 3.4296698570251465], [6.259438991546631, 3.1162109375, 4.0478339195251465, 0.44512939453125, 0.34515380859375]]
        self.input_jet_mass_bbj    = [[12.212333679199219, 14.547855377197266, 9.032913208007812, 9.729896545410156, 6.92578125], [11.015647888183594, 10.075767517089844, 6.872474670410156, 14.377754211425781, 3.806640625, 5.9140625, 6.015625, 5.59375], [23.625, 16.457977294921875, 12.192626953125, 13.806991577148438, 17.174148559570312, 3.09765625, 4.0625, 3.818359375], [12.921875, 16.77130126953125, 10.018440246582031, 7.0859375, 11.75, 9.24835205078125, 12.180450439453125, 7.7734375, 5.41015625], [16.266693115234375, 22.96240234375, 16.617996215820312, 18.90380859375, 16.65625], [18.78204345703125, 14.315475463867188, 8.96875, 12.370376586914062, 9.120094299316406, 8.21875], [21.4207763671875, 21.424346923828125, 10.804283142089844, 9.389877319335938, 6.20703125], [23.234375, 12.78912353515625, 12.5703125, 9.838478088378906, 10.14642333984375, 9.2890625, 8.95928955078125], [16.96875, 9.6640625, 10.244514465332031, 11.4453125, 11.19537353515625, 7.90191650390625], [16.4176025390625, 26.8564453125, 10.197921752929688, 8.037918090820312, 5.1953125]]
        self.input_jet_flavor_bbj  = [['b', 'b', 'b', 'b', 'j'], ['b', 'b', 'b', 'b', 'j', 'j', 'j', 'j'], ['j', 'b', 'b', 'b', 'b', 'j', 'j', 'j'], ['j', 'b', 'b', 'j', 'j', 'b', 'b', 'j', 'j'], ['b', 'b', 'b', 'b', 'j'], ['b', 'b', 'j', 'b', 'b', 'j'], ['b', 'b', 'b', 'b', 'j'], ['j', 'b', 'j', 'b', 'b', 'j', 'b'], ['b', 'j', 'b', 'j', 'b', 'b'], ['b', 'b', 'b', 'b', 'j']]
        self.input_btagDeepFlavB_bbj  = [[0.99462890625, 0.99951171875, 0.99951171875, 0.99951171875, 0.10302734375], [0.67919921875, 0.921875, 0.9990234375, 0.9951171875, 0.007720947265625, 0.0224456787109375, 0.0220947265625, 0.03350830078125], [0.0191192626953125, 0.71484375, 0.99951171875, 0.89892578125, 0.8134765625, 0.0198974609375, 0.0120849609375, 0.0225067138671875], [0.246337890625, 0.94140625, 0.65380859375, 0.025604248046875, 0.005462646484375, 0.9697265625, 0.998046875, 0.0233154296875, 0.03375244140625], [0.9990234375, 0.63818359375, 0.99951171875, 0.99853515625, 0.00926971435546875], [0.98828125, 0.99951171875, 0.007465362548828125, 0.99560546875, 0.99951171875, 0.0260772705078125], [0.99462890625, 0.99755859375, 0.99755859375, 0.99169921875, 0.006397247314453125], [0.0150604248046875, 0.72705078125, 0.0114593505859375, 0.62255859375, 0.640625, 0.006443023681640625, 0.97216796875], [0.94677734375, 0.0214080810546875, 0.7763671875, 0.1513671875, 0.99951171875, 0.943359375], [0.8017578125, 0.62353515625, 0.99365234375, 0.94482421875, 0.00836944580078125]]


        self.input_jets_bbj = ak.zip(
            {
                "pt": self.input_jet_pt_bbj,
                "eta": self.input_jet_eta_bbj,
                "phi": self.input_jet_phi_bbj,
                "mass": self.input_jet_mass_bbj,
                "jet_flavor": self.input_jet_flavor_bbj,
                "btagDeepFlavB": self.input_btagDeepFlavB_bbj,
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )


        self.input_jet_pt_6  = [[234.91912841796875, 228.775634765625, 64.3125, 61.700439453125, 58.14398193359375, 48.59375], [246.812744140625, 168.35546875, 131.75, 131.6524658203125, 77.25, 56.489501953125], [456.72607421875, 352.0, 149.59912109375, 86.875, 63.031005859375, 43.9178466796875], [279.784423828125, 250.7904052734375, 101.01605224609375, 60.875, 52.53875732421875, 50.4375], [205.3228759765625, 133.94091796875, 101.066650390625, 92.125, 87.998291015625, 73.75], [188.9853515625, 170.12255859375, 107.0625, 89.625, 72.04833984375, 51.375], [131.75, 106.16046142578125, 83.59130859375, 83.375, 80.9718017578125, 52.386932373046875], [188.0804443359375, 92.1796875, 85.25, 76.4375, 63.67181396484375, 47.8173828125], [223.25, 137.75, 112.379150390625, 81.25457763671875, 78.2041015625, 74.050048828125], [153.71630859375, 137.92950439453125, 72.625, 65.625, 48.224700927734375, 43.3271484375]]
        self.input_jet_eta_6  = [[-0.5133056640625, -1.543701171875, 0.831787109375, 0.9537353515625, -0.7618408203125, -1.153564453125], [0.34356689453125, 0.094818115234375, 0.9638671875, -0.02260589599609375, -0.31683349609375, -1.843505859375], [-1.39208984375, -1.231689453125, -0.9793701171875, -0.11669921875, 0.168609619140625, -0.13671875], [-1.185546875, 1.681396484375, 0.44091796875, 0.45770263671875, -0.3785400390625, -0.6993408203125], [0.06719970703125, -0.7655029296875, -0.005198478698730469, 1.295166015625, 0.669677734375, 2.1767578125], [0.03668975830078125, -0.8272705078125, 1.010009765625, -1.881591796875, 0.592041015625, -1.369384765625], [-0.1100006103515625, -1.47216796875, -0.756591796875, -1.90283203125, -0.605224609375, -0.5802001953125], [0.6260986328125, 1.0166015625, -1.91943359375, -2.1875, 0.588134765625, 0.03516387939453125], [2.29443359375, -2.3876953125, 0.200958251953125, -0.6177978515625, 0.5872802734375, 0.36236572265625], [0.56787109375, -0.610595703125, -2.2841796875, -0.0773773193359375, 0.9136962890625, 0.5615234375]]
        self.input_jet_phi_6  = [[0.49713134765625, 3.7636542320251465, -2.18408203125, 1.37109375, 3.01513671875, 0.0600128173828125], [5.3735175132751465, 2.31298828125, 2.5029296875, 5.6054511070251465, -1.099365234375, 2.41845703125], [1.5263671875, -1.49658203125, 4.2846503257751465, -2.72265625, 0.5770263671875, 0.21160888671875], [1.529296875, 4.7824530601501465, 5.1801581382751465, -2.49658203125, 1.103515625, 2.10205078125], [4.9992499351501465, 1.5009765625, 4.4350409507751465, 2.3486328125, 1.9658203125, 1.104248046875], [5.7166571617126465, 2.6904296875, -0.45654296875, 2.40087890625, 5.1591620445251465, 1.868896484375], [-2.20703125, 1.962158203125, 0.53076171875, -0.107879638671875, 2.99072265625, 6.280444622039795], [3.6713690757751465, 2.3046875, 0.2967529296875, -0.5640869140625, 0.604248046875, 6.1497015953063965], [-1.74560546875, 2.49755859375, 1.0810546875, 1.872802734375, 1.3837890625, 5.2116522789001465], [0.30316162109375, 3.1650214195251465, -2.75439453125, 0.294921875, 5.3921942710876465, 4.9733710289001465]]
        self.input_jet_mass_6  = [[30.531005859375, 29.481903076171875, 9.0234375, 11.388397216796875, 9.933212280273438, 9.6328125], [24.9578857421875, 25.6658935546875, 25.484375, 11.848068237304688, 9.796875, 8.627471923828125], [67.39971923828125, 32.09375, 25.495628356933594, 12.6328125, 9.835433959960938, 8.893363952636719], [37.81341552734375, 27.132110595703125, 21.957839965820312, 11.3828125, 7.413169860839844, 10.8203125], [20.790863037109375, 16.518096923828125, 16.962127685546875, 15.4921875, 12.61669921875, 13.7578125], [29.63092041015625, 26.920989990234375, 17.078125, 21.515625, 10.68695068359375, 10.27667236328125], [21.046875, 15.8487548828125, 11.893730163574219, 17.375, 16.7896728515625, 9.014328002929688], [18.280426025390625, 9.745559692382812, 13.5078125, 22.375, 11.146934509277344, 7.6776123046875], [13.953125, 14.125, 18.94012451171875, 14.496162414550781, 11.415924072265625, 9.816543579101562], [26.37384033203125, 13.808853149414062, 10.6328125, 11.40625, 8.66156005859375, 8.05224609375]]
        self.input_jet_flavor_6  = [['b', 'b', 'j', 'b', 'b', 'j'], ['b', 'b', 'j', 'b', 'j', 'b'], ['b', 'j', 'b', 'j', 'b', 'b'], ['b', 'b', 'b', 'j', 'b', 'j'], ['b', 'b', 'b', 'j', 'b', 'j'], ['b', 'b', 'j', 'j', 'b', 'b'], ['j', 'b', 'b', 'j', 'b', 'b'], ['b', 'b', 'j', 'j', 'b', 'b'], ['j', 'j', 'b', 'b', 'b', 'b'], ['b', 'b', 'j', 'j', 'b', 'b']]


        self.input_jets_6 = ak.zip(
            {
                "pt": self.input_jet_pt_6,
                "eta": self.input_jet_eta_6,
                "phi": self.input_jet_phi_6,
                "mass": self.input_jet_mass_6,
                "jet_flavor": self.input_jet_flavor_6,
                "btagDeepFlavB": self.input_jet_pt_6, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )


        self.input_jet_pt_5b  = [[847.06787109375, 575.1123046875, 393.391845703125, 132.3695068359375, 101.75, 46.1875], [147.25, 144.20068359375, 89.9044189453125, 86.82928466796875, 77.19970703125, 46.03125], [187.54718017578125, 111.3125, 109.57470703125, 96.76171875, 89.548828125, 53.4375], [205.770263671875, 91.76766967773438, 80.0137939453125, 72.25, 72.0625, 58.360931396484375], [257.81396484375, 199.16796875, 176.09033203125, 168.09375, 45.78125, 45.59375], [358.4278564453125, 158.643310546875, 141.4593505859375, 56.093170166015625, 52.625, 48.28125], [360.7578125, 157.62237548828125, 149.375, 72.39990234375, 71.32080078125, 48.5625], [232.29541015625, 107.25, 98.73687744140625, 93.718505859375, 68.5625, 62.34161376953125], [130.875, 85.73077392578125, 78.266357421875, 66.3837890625, 64.326171875, 45.125], [163.8134765625, 124.72186279296875, 116.5625, 56.59375, 52.27362060546875, 50.5859375]]
        self.input_jet_eta_5b  = [[-0.45623779296875, -0.146209716796875, -0.6796875, -1.140380859375, -1.597412109375, 1.530517578125], [-0.511962890625, 0.4573974609375, 0.03043365478515625, -0.8470458984375, -0.8199462890625, 0.6304931640625], [1.843994140625, -0.8642578125, 1.0400390625, -1.63427734375, 0.56298828125, -2.0244140625], [-0.6571044921875, 1.706787109375, 0.44293212890625, 0.40264892578125, 0.54150390625, 0.805419921875], [2.2060546875, -1.774169921875, 0.4654541015625, 1.042724609375, -0.0927581787109375, 1.240966796875], [-1.69287109375, 0.3299560546875, -0.47491455078125, -0.015758514404296875, 1.12255859375, 0.1666259765625], [-1.627685546875, -0.41790771484375, -1.678466796875, -1.666015625, -0.793701171875, 0.33197021484375], [0.4727783203125, -0.0710601806640625, 0.866455078125, -0.4940185546875, -0.011898040771484375, 0.607177734375], [0.901611328125, -1.986083984375, -1.075439453125, 0.713623046875, -0.517333984375, -1.24560546875], [-1.4072265625, -0.5345458984375, -1.128173828125, -1.193359375, -0.8819580078125, -0.673095703125]]
        self.input_jet_phi_5b  = [[0.7490234375, 3.5683417320251465, 2.86474609375, 4.8049139976501465, -1.607177734375, -1.41748046875], [-0.8682861328125, 2.0068359375, 4.2328925132751465, 3.4609198570251465, 0.798583984375, -2.06005859375], [4.7670722007751465, 2.68115234375, 0.95166015625, 5.9013495445251465, 2.50341796875, -0.0863189697265625], [1.468505859375, 5.1887030601501465, 3.1508612632751465, -1.85498046875, 0.2962646484375, 4.9518866539001465], [1.825927734375, 3.5492987632751465, 5.8480658531188965, 5.5837225914001465, -0.880859375, 1.49755859375], [0.51123046875, 3.2905097007751465, 3.7035956382751465, 5.5689520835876465, -1.193115234375, -1.93310546875], [1.469970703125, 3.5317206382751465, -1.829345703125, 5.3429999351501465, 4.3251776695251465, -1.745361328125], [1.477783203125, -2.37109375, 5.6043524742126465, 5.0405097007751465, 2.52294921875, 4.3627753257751465], [2.61083984375, 4.4965643882751465, 0.7987060546875, 4.7101874351501465, 5.7914862632751465, 1.236328125], [5.1718573570251465, 1.2177734375, 1.914306640625, -1.98681640625, 3.4330878257751465, 4.0219550132751465]]
        self.input_jet_mass_5b  = [[49.44325256347656, 84.58648681640625, 51.7620849609375, 15.502212524414062, 15.359375, 9.75], [18.140625, 18.935760498046875, 22.168212890625, 14.885765075683594, 11.135177612304688, 8.875], [31.703811645507812, 23.640625, 13.62493896484375, 14.672607421875, 9.512954711914062, 9.4375], [35.9139404296875, 14.719371795654297, 12.301963806152344, 15.1953125, 11.59375, 10.432571411132812], [40.98614501953125, 21.42822265625, 19.395263671875, 14.83355712890625, 10.734375, 7.0234375], [40.57731628417969, 32.29435729980469, 17.542205810546875, 9.165962219238281, 11.90625, 9.7578125], [36.6953125, 19.475631713867188, 20.125, 11.5631103515625, 12.649574279785156, 9.3671875], [23.001861572265625, 11.828125, 18.114395141601562, 18.237213134765625, 8.953125, 12.131118774414062], [18.859375, 10.186088562011719, 18.271240234375, 13.1004638671875, 11.26220703125, 9.5078125], [20.97808837890625, 21.042236328125, 18.296875, 10.4375, 9.928436279296875, 9.153881072998047]]
        self.input_jet_flavor_5b  = [['b', 'b', 'b', 'b', 'j', 'j'], ['j', 'b', 'b', 'b', 'b', 'j'], ['b', 'j', 'b', 'b', 'b', 'j'], ['b', 'b', 'b', 'j', 'j', 'b'], ['b', 'b', 'b', 'b', 'j', 'j'], ['b', 'b', 'b', 'b', 'j', 'j'], ['b', 'b', 'j', 'b', 'b', 'j'], ['b', 'j', 'b', 'b', 'j', 'b'], ['j', 'b', 'b', 'b', 'b', 'j'], ['b', 'b', 'j', 'j', 'b', 'b']]


        self.input_jets_5b = ak.zip(
            {
                "pt": self.input_jet_pt_5b,
                "eta": self.input_jet_eta_5b,
                "phi": self.input_jet_phi_5b,
                "mass": self.input_jet_mass_5b,
                "jet_flavor": self.input_jet_flavor_5b,
                "btagDeepFlavB": self.input_jet_pt_5b, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )



        #
        # ERrors in HH signal
        #
        self.input_jet_pt_HH_3b  = [[262.848876953125, 190.92445373535156, 118.01837921142578, 85.73815155029297, 84.77513885498047, 81.45384216308594, 56.21860122680664, 54.88019561767578, 53.123104095458984, 40.82435989379883]]
        self.input_jet_eta_HH_3b  = [[-0.5233154296875, -0.108184814453125, 1.060302734375, -1.105712890625, 1.79638671875, 2.23681640625, 0.953369140625, 0.212158203125, 1.939208984375, 1.075439453125]]
        self.input_jet_phi_HH_3b  = [[3.4057440757751465, 0.60888671875, 0.807861328125, 3.9755682945251465, 2.97900390625, -0.3990478515625, -0.474609375, 5.6286444664001465, 1.234130859375, 1.5517578125]]
        self.input_jet_mass_HH_3b  = [[19.766611099243164, 15.895012855529785, 20.83321762084961, 11.490931510925293, 14.269634246826172, 8.53515338897705, 9.325471878051758, 8.153546333312988, 11.367645263671875, 8.33912181854248]]
        self.input_jet_flavor_HH_3b  = [['b', 'b', 'j', 'b', 'j', 'j', 'j', 'b', 'j', 'j']]

        self.input_jets_HH_3b = ak.zip(
            {
                "pt": self.input_jet_pt_HH_3b + self.input_jet_pt_HH_3b,
                "eta": self.input_jet_eta_HH_3b + self.input_jet_eta_HH_3b,
                "phi": self.input_jet_phi_HH_3b + self.input_jet_phi_HH_3b,
                "mass": self.input_jet_mass_HH_3b + self.input_jet_mass_HH_3b,
                "jet_flavor": self.input_jet_flavor_HH_3b + self.input_jet_flavor_HH_3b,
                "btagDeepFlavB": self.input_jet_pt_HH_3b + self.input_jet_pt_HH_3b, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )

        #
        #   `(bj)((jj)b)` splittins
        #
        self.input_jet_pt_bad_split      = [[411.75, 347.75, 193.948974609375, 97.8897705078125, 74.1673583984375, 64.99481201171875, 64.4375, 45.6875], [257.868896484375, 252.375, 182.0518798828125, 163.2843017578125, 112.82763671875, 98.5625, 75.9375, 63.4375, 50.75, 40.625]]
        self.input_jet_eta_bad_split     = [[0.708251953125, -0.1527099609375, 1.647705078125, 0.0011379718780517578, 0.7615966796875, -1.027587890625, -0.0990142822265625, -0.5068359375], [-0.2508544921875, 0.6533203125, -0.8846435546875, -0.1190643310546875, -1.188232421875, 2.072265625, -1.62890625, -1.823486328125, -1.2900390625, -0.403564453125]]
        self.input_jet_phi_bad_split     = [[0.6732177734375, 3.1025390625, 5.0475897789001465, 2.546875, 5.5264716148376465, 4.5519843101501465, -1.86865234375, -2.2685546875], [0.37841796875, -2.87353515625, 0.8896484375, 3.4594550132751465, 4.4452948570251465, 1.46337890625, -1.463134765625, 0.43634033203125, 0.46148681640625, -2.2685546875]]
        self.input_jet_mass_bad_split    = [[44.78125, 34.3125, 22.199172973632812, 12.091888427734375, 16.046722412109375, 12.618278503417969, 11.578125, 6.93359375], [27.153228759765625, 21.859375, 20.270751953125, 22.866058349609375, 20.2275390625, 12.640625, 7.80078125, 9.8828125, 8.4609375, 7.046875]]
        self.input_jet_flavor_bad_split  = [['j', 'j', 'b', 'b', 'b', 'b', 'j', 'j'], ['b', 'j', 'b', 'b', 'b', 'j', 'j', 'j', 'j', 'j']]

        self.input_jets_bad_split = ak.zip(
            {
                "pt": self.input_jet_pt_bad_split,
                "eta": self.input_jet_eta_bad_split,
                "phi": self.input_jet_phi_bad_split,
                "mass": self.input_jet_mass_bad_split,
                "jet_flavor": self.input_jet_flavor_bad_split,
                "btagDeepFlavB": self.input_jet_pt_bad_split, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )




        self.input_jets_all = ak.zip(
            {
                "pt":  self.input_jet_pt_4 + self.input_jet_pt_5 + self.input_jet_pt_bbj + self.input_jet_pt_6 + self.input_jet_pt_5b,
                "eta": self.input_jet_eta_4 + self.input_jet_eta_5 + self.input_jet_eta_bbj + self.input_jet_eta_6 + self.input_jet_eta_5b,
                "phi": self.input_jet_phi_4 + self.input_jet_phi_5 + self.input_jet_phi_bbj + self.input_jet_phi_6 + self.input_jet_phi_5b,
                "mass": self.input_jet_mass_4 + self.input_jet_mass_5 + self.input_jet_mass_bbj + self.input_jet_mass_6 + self.input_jet_mass_5b,
                "jet_flavor": self.input_jet_flavor_4 + self.input_jet_flavor_5 + self.input_jet_flavor_bbj + self.input_jet_flavor_6 + self.input_jet_flavor_5b,
                "btagDeepFlavB": self.input_jet_pt_4 + self.input_jet_pt_5 + self.input_jet_pt_bbj + self.input_jet_pt_6 + self.input_jet_pt_5b, ## Hack
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )




        self.debug = False


    def test_kt_clustering_4jets(self):

        R = np.pi  # Jet size parameter
        clustered_jets = kt_clustering(self.input_jets_4, R)


        jetdefAll = fastjet.JetDefinition(fastjet.kt_algorithm, R)
        clusterAll = fastjet.ClusterSequence(self.input_jets_4, jetdefAll)

        for iEvent, jets in enumerate(clustered_jets):
            if self.debug: print(f"Event {iEvent}")
            for i, jet in enumerate(jets):

                hasFJMatch = False
                if self.debug: print(f"Jet {i+1}: px = {jet.px:.2f}, py = {jet.py:.2f}, pz = {jet.pz:.2f}, E = {jet.E:.2f}, type = {jet.jet_flavor}")
                for i_fj, jet_fj in enumerate(clusterAll.inclusive_jets()[iEvent]):
                    if np.allclose( (jet.px, jet.py, jet.pz, jet.E),(jet_fj.px, jet_fj.py, jet_fj.pz, jet_fj.E), atol=1e-3 ):
                        if self.debug: print("Has match!")
                        hasFJMatch =True

                self.assertTrue(hasFJMatch, " Not all jets have a fastjet match")

            if self.debug:
                for i_fj, jet_fj in enumerate(clusterAll.inclusive_jets()[iEvent]):
                    print(f"FJ  {i_fj+1}: px = {jet_fj.px:.2f}, py = {jet_fj.py:.2f}, pz = {jet_fj.pz:.2f}, E = {jet_fj.E:.2f}")


    def _declustering_test(self, input_jets, debug=False):

        clustered_jets, clustered_splittings = cluster_bs(input_jets, debug=False)
        compute_decluster_variables(clustered_splittings)

        split_name_flat = [get_splitting_name(i) for i in ak.flatten(clustered_splittings.jet_flavor)]
        split_name = ak.unflatten(split_name_flat, ak.num(clustered_splittings))
        clustered_splittings["splitting_name"] = split_name

        if self.debug:
            for iEvent, jets in enumerate(clustered_jets):
                print(f"Event {iEvent}")
                for i, jet in enumerate(jets):
                    print(f"Jet {i+1}: px = {jet.px:.2f}, py = {jet.py:.2f}, pz = {jet.pz:.2f}, E = {jet.E:.2f}, type = {jet.jet_flavor}")
                print("...Splittings")

                for i, splitting in enumerate(clustered_splittings[iEvent]):
                    print(f"Split {i+1}: px = {splitting.px:.2f}, py = {splitting.py:.2f}, pz = {splitting.pz:.2f}, E = {splitting.E:.2f}, type = {splitting.jet_flavor}")
                    print(f"\tPart_A {splitting.part_A}")
                    print(f"\tPart_B {splitting.part_B}")


        #
        # Declustering
        #

        # Eventually will
        #   Lookup thetaA, Z, mA, and mB
        #   radom draw phi  (np.random.uniform(-np.pi, np.pi, len()) ? )
        #
        #  For now use known inputs
        #   (should get exact jets back!)
        clustered_splittings["decluster_mask"] = True
        pA, pB = decluster_combined_jets(clustered_splittings)


        #
        # Check Pts
        #
        pt_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.pt, (pA + pB).pt)]
        if not all(pt_check):
            [print(i) for i in clustered_splittings.pt - (pA + pB).pt]
            [print(i, j) for i, j in zip(clustered_splittings.pt, (pA + pB).pt)]
        self.assertTrue(all(pt_check), "All pt should be the same")

        #
        # Check Eta
        #
        eta_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.eta, (pA + pB).eta)]
        if not all(eta_check):
            [print(i) for i in clustered_splittings.eta - (pA + pB).eta]
            [print(i, j) for i, j in zip(clustered_splittings.eta, (pA + pB).eta)]
        self.assertTrue(all(eta_check), "All eta should be the same")



        #
        # Check Masses
        #
        mass_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.mass, (pA + pB).mass)]
        if not all(mass_check):
            [print(i) for i in clustered_splittings.mass - (pA + pB).mass]
            [print(i, j) for i, j in zip(clustered_splittings.mass, (pA + pB).mass)]
        self.assertTrue(all(mass_check), "All Masses should be the same")

        #
        # Check Phis
        #
        phi_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.phi, (pA + pB).phi)]
        if not all(phi_check):
            [print(i) for i in clustered_splittings.phi - (pA + pB).phi]
            [print(i, j) for i, j in zip(clustered_splittings.phi, (pA + pB).phi)]
        self.assertTrue(all(phi_check), "All phis should be the same")


    def test_declustering_4jets(self):
        self._declustering_test(self.input_jets_4)

    def test_declustering_5jets(self):
        self._declustering_test(self.input_jets_5, debug=False)

    def test_declustering_bbjjets(self):
        self._declustering_test(self.input_jets_bbj, debug=False)

    def test_declustering_6jets(self):
        self._declustering_test(self.input_jets_6, debug=False)

    def test_declustering_Njets(self):
        self._declustering_test(self.input_jets_bad_split, debug=False)


    def test_cluster_bs_speed_test(self):

        start = time.perf_counter()
        clustered_jets_fast, clustered_splittings_fast = cluster_bs_fast(self.input_jets_all , debug=False)
        end = time.perf_counter()
        elapsed_time_matrix_python = (end - start)
        print(f"\nElapsed time fast Python = {elapsed_time_matrix_python}s")

        start = time.perf_counter()
        clustered_jets, clustered_splittings = cluster_bs(self.input_jets_all, debug=False)
        end = time.perf_counter()
        elapsed_time_loops_python = (end - start)
        print(f"\nElapsed time loops Python = {elapsed_time_loops_python}s")


        start = time.perf_counter()
        _, _ = cluster_bs_numba(self.input_jets_all, debug=False)
        end = time.perf_counter()
        elapsed_time_numba = (end - start)
        print(f"\nElapsed time numba1  = {elapsed_time_numba}s")

        start = time.perf_counter()
        clustered_jets_numba, clustered_splittings_numba = cluster_bs_numba(self.input_jets_all, debug=False)
        end = time.perf_counter()
        elapsed_time_numba = (end - start)
        print(f"\nElapsed time numba2  = {elapsed_time_numba}s")



        #
        # Sanity checks
        #

        #
        # Check Masses
        #
        self.assertTrue(np.sum(ak.num(clustered_splittings.mass)) == np.sum(ak.num(clustered_splittings_numba.mass)),
                        f"Should get the same number of splittings! {np.sum(ak.num(clustered_splittings.mass))} vs {np.sum(ak.num(clustered_splittings_numba.mass))}")


        mass_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.mass, clustered_splittings_numba.mass)]
        self.assertTrue(all(mass_check), "All Masses should be the same")
        pt_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.pt, clustered_splittings_numba.pt)]
        self.assertTrue(all(pt_check), "All Masses should be the same")


        #
        # Check Masses
        #
        mass_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.mass, clustered_splittings_fast.mass)]
        if not all(mass_check):
            print("deltas")
            [print(i) for i in clustered_splittings.mass - clustered_splittings_fast.mass]
            print("values")
            [print(i, j) for i, j in zip(clustered_splittings.mass, clustered_splittings_fast.mass)]
        self.assertTrue(all(mass_check), "All Masses should be the same")


        #
        # Check Pts
        #
        pt_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.pt, clustered_splittings_fast.pt)]
        if not all(pt_check):
            print("deltas")
            [print(i) for i in clustered_splittings.pt - clustered_splittings_fast.pt]
            print("values")
            [print(i, j) for i, j in zip(clustered_splittings.pt, clustered_splittings_fast.pt)]
        self.assertTrue(all(pt_check), "All Masses should be the same")


        #
        # Check phis
        #
        phi_check = [np.allclose(i, j, 1e-4) for i, j in zip(clustered_splittings.phi, clustered_splittings_fast.phi)]
        if not all(phi_check):
            print("deltas")
            [print(i) for i in clustered_splittings.phi - clustered_splittings_fast.phi]
            print("values")
            [print(i, j) for i, j in zip(clustered_splittings.phi, clustered_splittings_fast.phi)]
        self.assertTrue(all(phi_check), "All phis should be the same")


#    def profile_clustering(self):
#
#        from cProfile import Profile
#
#        test = lambda: cluster_bs(self.input_jets_all , debug=False)
#
#        profiler = Profile()
#        profiler.runcall(test)
#
#        from pstats import Stats
#        stats = Stats(profiler)
#        stats.strip_dirs()
#        stats.sort_stats("cumulative")
#        stats.print_stats()



    def _check_jet_flavors(self, part_A_jet_flavor, part_B_jet_flavor, debug=False):

        #
        # Check particle orderings of splittings
        #
        part_A_flat = ak.flatten(part_A_jet_flavor)
        part_B_flat = ak.flatten(part_B_jet_flavor)

        if debug:
            print(f"part_A_flat {part_A_flat}")
            print(f"part_B_flat {part_B_flat}")

        #
        #  A should always be the more complex
        #
        part_A_len = np.array([len(i) for i in part_A_flat])
        part_B_len = np.array([len(i) for i in part_B_flat])
        self.assertTrue(all(a >= b for a, b in zip(part_A_len, part_B_len)), "Part A should be the more complex of the pair")


        #
        #  More bs in A when lengths are the same
        #
        part_A_countbs = np.array([i.count("b") for i in part_A_flat])
        part_B_countbs = np.array([i.count("b") for i in part_B_flat])

        more_bs_in_partA = part_A_countbs >= part_B_countbs
        equal_len_mask = part_A_len == part_B_len
        more_bs_in_partA[~equal_len_mask] = True

        self.assertTrue(np.all(more_bs_in_partA), "Part A should alwasy have more bs")


    def _synthetic_datasets_test(self, input_jets, n_jets_expected, debug=False):

        clustered_jets, _clustered_splittings = cluster_bs(input_jets, debug=debug)

        self._check_jet_flavors(_clustered_splittings.part_A.jet_flavor,
                                _clustered_splittings.part_B.jet_flavor,
                                debug=debug)

        if debug:
            print(f"input_jets.pt             {input_jets.pt}")
            print(f"input_jets.jet_flavor     {input_jets.jet_flavor}")
            print(f"input_jets.btag_string    {input_jets.btag_string}")

        if debug:
            print(f"clustered_jets_wISR.pt             {clustered_jets.pt}")
            print(f"clustered_jets_wISR.jet_flavor     {clustered_jets.jet_flavor}")
            print(f"clustered_jets_wISR.btag_string    {clustered_jets.btag_string}")


        #
        #  Decluster the splitting that are 0b + >1 bs
        #
        if debug:
            print("Jet flavour Before ISR cleaning")
            [print(i) for i in clustered_jets.jet_flavor]

        clustered_jets = clean_ISR(clustered_jets, _clustered_splittings, debug=debug)

        if debug:
            print(f"clustered_jets.pt             {clustered_jets.pt}")
            print(f"clustered_jets.jet_flavor     {clustered_jets.jet_flavor}")
            print(f"clustered_jets.btag_string    {clustered_jets.btag_string}")

        #mask_b_jet = clean_ISR
        mask_unclustered_jet = (clustered_jets.jet_flavor == "b") | (clustered_jets.jet_flavor == "j")
        ak.num(clustered_jets[~mask_unclustered_jet])

        if debug:
            print("Jet flavour after ISR cleaning")
            [print(i) for i in clustered_jets.jet_flavor]

        #
        # Testing the splitting cleaning
        #
        all_split_types = get_list_of_splitting_types(_clustered_splittings)
        cleaned_combined_types = get_list_of_combined_jet_types(clustered_jets)
        cleaned_split_types = []
        for _s in cleaned_combined_types:
            cleaned_split_types += get_list_of_all_sub_splittings(_s)

        if debug:
            print(f"all_split_types {all_split_types}")
            print(f"cleaned_combined_types {cleaned_combined_types}")
            print(f"cleaned_split_types {cleaned_split_types}")


        #
        # Declustering
        #
        declustered_jets = make_synthetic_event(clustered_jets, self.input_pdfs, debug=debug)

        if debug:
            print(f"declustered_jets.pt             {declustered_jets.pt}")
            print(f"declustered_jets.jet_flavor     {declustered_jets.jet_flavor}")
            print(f"declustered_jets.btagDeepFlavB  {declustered_jets.btagDeepFlavB}")

        #
        # Sanity checks
        #

        match_n_jets = ak.num(declustered_jets) == n_jets_expected
        if not all(match_n_jets) or debug:
            print("ERROR number of declustered_jets")
            print(f"ak.num(declustered_jets)        {ak.num(declustered_jets)}")
            print(f"clustered_jets.jet_flavor     {clustered_jets.jet_flavor}")
            print(f"clustered_jets.pt             {clustered_jets.pt}")
            #print(f"pA.pt                         {pA.pt}")
            #print(f"pB.pt                         {pB.pt}")

            print(f"declustered_jets.pt             {declustered_jets.pt}")
            print(f"ak.num(declustered_jets)        {ak.num(declustered_jets)}")
            print(f"clustered_jets.phi             {clustered_jets.phi}")


        self.assertTrue(all(match_n_jets), f"Should always get {n_jets_expected} jets")

        #
        #  Do reclustering
        #
        is_b_mask = declustered_jets.jet_flavor == "b"

        canJet = declustered_jets[is_b_mask]
        notCanJet_sel = declustered_jets[~is_b_mask]
        jets_for_clustering = ak.concatenate([canJet, notCanJet_sel], axis=1)
        jets_for_clustering = jets_for_clustering[ak.argsort(jets_for_clustering.pt, axis=1, ascending=False)]
        clustered_jets_reclustered, clustered_splittings_reclustered = cluster_bs(jets_for_clustering, debug=False)
        compute_decluster_variables(clustered_splittings_reclustered)

        self._check_jet_flavors(clustered_splittings_reclustered.part_A.jet_flavor,
                                clustered_splittings_reclustered.part_B.jet_flavor)


    def test_synthetic_datasets_4jets(self):
        self._synthetic_datasets_test(self.input_jets_4, n_jets_expected = 4)

    def test_synthetic_datasets_5jets(self):
        self._synthetic_datasets_test(self.input_jets_5, n_jets_expected = 5, debug=False)

    def test_synthetic_datasets_bbjjets(self):
        self._synthetic_datasets_test(self.input_jets_bbj, n_jets_expected = ak.num(self.input_jet_pt_bbj))

    def test_synthetic_datasets_6jets(self):
        self._synthetic_datasets_test(self.input_jets_6, n_jets_expected = 6, debug = False)

    def test_synthetic_datasets_5bjets(self):
        self._synthetic_datasets_test(self.input_jets_5b, n_jets_expected = 6, debug = False)

    def test_synthetic_datasets_HH_3bjets(self):
        self._synthetic_datasets_test(self.input_jets_HH_3b, n_jets_expected = 10, debug = False)

    def test_synthetic_datasets_bad_split(self):
        self._synthetic_datasets_test(self.input_jets_bad_split, n_jets_expected = [8, 10], debug = False)


#    def profile_synthetic_datasets(self):
#
#        from cProfile import Profile
#
#        test = lambda: self._synthetic_datasets_test(self.input_jets_6 , n_jets_expected=6,debug=False)
#
#        profiler = Profile()
#        profiler.runcall(test)
#
#        from pstats import Stats
#        stats = Stats(profiler)
#        stats.strip_dirs()
#        stats.sort_stats("cumulative")
#        stats.print_stats()



    def test_children_jet_flavors(self):
        splitting_types = [ ('bb', ('b','b')), ('bj',('b','j')), ('jb',('j','b')), ('jj',('j','j')),
                            ("j(bb)", ('bb', 'j')), ("b(bj)", ('bj', 'b')), ("j(bj)", ('bj', 'j')), ("(bj)b", ('bj', 'b')),
                            ("(j(bj))b", ('j(bj)', 'b')), ("(bb)(jj)", ('bb', 'jj')), ("(jj)(bb)", ('jj', 'bb')), ("j(j(bj))", ('j(bj)','j')),
                            ('((((jj)j)j)((bj)j))b', ('(((jj)j)j)((bj)j)','b')),
                           ]

        for _s in splitting_types:

            _children = children_jet_flavors(_s[0])
            #print(_s[0],":",_children,"vs",_s[1])
            self.assertTrue(_children == _s[1], f"Miss match for type {_s[0]}: got {_children}, expected {_s[1]}")

    def test_get_list_of_ISR_splittings(self):

        splitting_types = [("b",False), ("j",False),
                           ("bb",False), ("bj",True), ("jj",True),
                           ("j(bb)",True), ("b(bj)",False), ("j(bj)",True),('(bj)b',False),
                           ("b(j(bj))",False), ('(bb)(jj)',True), ('(jj)(bb)',True) ,("j(j(bj))",True), ("j(b(bj))",True)
                           ]


        test_splitting_types = []
        expected_ISR_splittings = []

        for _s in splitting_types:
            test_splitting_types.append(_s[0])
            if _s[1]:
                expected_ISR_splittings.append(_s[0])

        expected_ISR_splittings.sort()
        ISR_splittings = get_list_of_ISR_splittings(test_splitting_types)

        self.assertListEqual(ISR_splittings, expected_ISR_splittings)


    def test_get_list_of_all_sub_splittings(self):
        splitting_types = [("b",[]),
                           ("bb",["bb"]),
                           ('j(bj)', ['j(bj)','bj']),
                           ("(bb)(jj)", ["(bb)(jj)",'bb', 'jj']),
                           ("j(j(bj))", ["j(j(bj))",'j(bj)','bj']),
                           ("(j(bj))b", ["(j(bj))b","j(bj)","bj"] ),
                           ("((((jj)j)j)((bj)j))b", ["((((jj)j)j)((bj)j))b", "(((jj)j)j)((bj)j)", "((jj)j)j",  "(jj)j", "jj", "(bj)j", "bj"]),
                           ]


        for _s in splitting_types:

            sub_splitting = get_list_of_all_sub_splittings(_s[0])
            expected = _s[1]
            #print(f"{_s[0]} -> {sub_splitting}")
            self.assertListEqual(expected, sub_splitting)

    def test_get_splitting_summary(self):
        splitting_types = [ ('bb',                   ( (1, 0), (1,0))),
                            ("(bb)j",                ( (2, 0), (0,1))),
                            ("(j(bj))b",             ( (1, 2), (1,0))),
                            ('((((jj)j)j)((bj)j))b', ( (1 ,6), (1,0))),
                             ]
        for _s in splitting_types:

            njets, nbs = get_splitting_summary(_s[0])
            expected_njets = _s[1][0]
            expected_nbs   = _s[1][1]
            print(f"{_s[0]} -> {njets}  {nbs}")
            self.assertEqual(expected_njets, njets, "ERROR in njets")
            self.assertEqual(expected_nbs,   nbs,   "ERROR in nbs")




if __name__ == '__main__':
    # wrapper.parse_args()
    # unittest.main(argv=sys.argv)
    unittest.main()
