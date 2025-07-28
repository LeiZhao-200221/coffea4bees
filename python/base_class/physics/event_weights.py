import logging
from coffea.analysis_tools import Weights
import correctionlib
import awkward as ak
import numpy as np

def add_weights(event, do_MC_weights: bool = True,
                dataset: str = None,
                year_label: str = None,
                corrections_metadata: dict = None,
                apply_trigWeight: bool = True,
                friend_trigWeight: callable = None,
                isTTForMixed: bool = False,
                target: callable = None,
                ):
    """Add weights to the event.
    """

    weights = Weights(len(event), storeIndividual=True)
    list_weight_names = []

    if do_MC_weights:
        # genWeight
        lumi    = event.metadata.get('lumi',    1.0)
        xs      = event.metadata.get('xs',      1.0)
        kFactor = event.metadata.get('kFactor', 1.0)
        weights.add( "genweight", event.genWeight * (lumi * xs * kFactor / event.metadata["genEventSumw"]) )
        list_weight_names.append('genweight')
        logging.debug( f"genweight {weights.partial_weight(include=['genweight'])[:10]}\n" )
        logging.debug( f" = {event.genWeight} * ({lumi} * {xs} * {kFactor} / {event.metadata['genEventSumw']})\n")

        # trigger Weight (to be updated)
        if apply_trigWeight:
            trigWeight = event.trigWeight if "trigWeight" in event.fields else friend_trigWeight.arrays(target) if friend_trigWeight else logging.error(f"No friend tree for trigWeight found.")

            hlt = ak.where(event.passHLT, 1., 0.)
            weights.add( "CMS_bbbb_resolved_ggf_triggerEffSF",
                        trigWeight.Data, ##* ak.where(trigWeight.MC != 0, hlt / trigWeight.MC, 1) ### uncomment for new data.
                        trigWeight.MC,
                        hlt )
            list_weight_names.append('CMS_bbbb_resolved_ggf_triggerEffSF')
            logging.debug( f"trigWeight {weights.partial_weight(include=['CMS_bbbb_resolved_ggf_triggerEffSF'])[:10]}\n" )

        # puWeight (to be checked)
        if not isTTForMixed:
            puWeight = list( correctionlib.CorrectionSet.from_file( corrections_metadata["PU"] ).values() )[0]
            weights.add( f"CMS_pileup_{year_label}",
                            puWeight.evaluate(event.Pileup.nTrueInt, "nominal"),
                            puWeight.evaluate(event.Pileup.nTrueInt, "up"),
                            puWeight.evaluate(event.Pileup.nTrueInt, "down"), )
            list_weight_names.append(f"CMS_pileup_{year_label}")
            logging.debug( f"PU weight {weights.partial_weight(include=[f'CMS_pileup_{year_label}'])[:10]}\n" )

        # L1 prefiring weight
        if ( "L1PreFiringWeight" in event.fields ):  #### AGE: this should be temprorary (field exists in UL)
            weights.add( f"CMS_prefire_{year_label}",
                            event.L1PreFiringWeight.Nom,
                            event.L1PreFiringWeight.Up,
                            event.L1PreFiringWeight.Dn, )
            logging.debug( f"L1Prefire weight {weights.partial_weight(include=[f'CMS_prefire_{year_label}'])[:10]}\n" )
            list_weight_names.append(f"CMS_prefire_{year_label}")

        if ( "PSWeight" in event.fields ):  #### AGE: this should be temprorary (field exists in UL)
            nom      = np.ones(len(weights.weight()))
            up_isr   = np.ones(len(weights.weight()))
            down_isr = np.ones(len(weights.weight()))
            up_fsr   = np.ones(len(weights.weight()))
            down_fsr = np.ones(len(weights.weight()))

            if len(event.PSWeight[0]) == 4:
                up_isr   = event.PSWeight[:, 0]
                down_isr = event.PSWeight[:, 2]
                up_fsr   = event.PSWeight[:, 1]
                down_fsr = event.PSWeight[:, 3]

            else:
                logging.warning( f"PS weight vector has length {len(event.PSWeight[0])}" )

            weights.add("ps_isr", nom, up_isr, down_isr)
            weights.add("ps_fsr", nom, up_fsr, down_fsr)
            list_weight_names.append(f"ps_isr")
            list_weight_names.append(f"ps_fsr")

        # pdf_Higgs_ggHH, alpha_s, PDFaS weights are included in datacards through the inference tool. Kept this code for reference.
        # if "LHEPdfWeight" in event.fields:

        #     # https://github.com/nsmith-/boostedhiggs/blob/a33dca8464018936fbe27e86d52c700115343542/boostedhiggs/corrections.py#L53
        #     nom  = np.ones(len(weights.weight()))
        #     up   = np.ones(len(weights.weight()))
        #     down = np.ones(len(weights.weight()))

        #     # NNPDF31_nnlo_hessian_pdfas
        #     # https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_hessian_pdfas/NNPDF31_nnlo_hessian_pdfas.info
        #     if "306000 - 306102" in event.LHEPdfWeight.__doc__:
        #         # Hessian PDF weights
        #         # Eq. 21 of https://arxiv.org/pdf/1510.03865v1.pdf
        #         arg = event.LHEPdfWeight[:, 1:-2] - np.ones( (len(weights.weight()), 100) )

        #         summed = ak.sum(np.square(arg), axis=1)
        #         pdf_unc = np.sqrt((1.0 / 99.0) * summed)
        #         weights.add("pdf_Higgs_ggHH", nom, pdf_unc + nom)

        #         # alpha_S weights
        #         # Eq. 27 of same ref
        #         as_unc = 0.5 * ( event.LHEPdfWeight[:, 102] - event.LHEPdfWeight[:, 101] )

        #         weights.add("alpha_s", nom, as_unc + nom)

        #         # PDF + alpha_S weights
        #         # Eq. 28 of same ref
        #         pdfas_unc = np.sqrt(np.square(pdf_unc) + np.square(as_unc))
        #         weights.add("PDFaS", nom, pdfas_unc + nom)

        #     else:
        #         weights.add("alpha_s", nom, up, down)
        #         weights.add("pdf_Higgs_ggHH", nom, up, down)
        #         weights.add("PDFaS", nom, up, down)
        #     list_weight_names.append(f"alpha_s")
        #     list_weight_names.append(f"pdf_Higgs_ggHH")
        #     list_weight_names.append(f"PDFaS")
    else:
        weights.add("data", np.ones(len(event)))
        list_weight_names.append(f"data")

    logging.debug(f"weights event {weights.weight()[:10]}")
    logging.debug(f"Weight Statistics {weights.weightStatistics}")

    return weights, list_weight_names