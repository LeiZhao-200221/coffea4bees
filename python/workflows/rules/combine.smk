import os

include: "../helpers/common.smk"

rule workspace:
    input: "{path}.txt"
    output: "{path}.root"
    params:
        signallabel = "",
        othersignal_maps = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/workspace_{path}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting workspace rule with signal {params.signallabel}" > {log}
        {params.container_wrapper} cd $(dirname {input}) &&\
            text2workspace.py $(basename {input}) \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose \
            --PO 'map=.*/{params.signallabel}:r{params.signallabel}[1,-10,10]' \
            {params.othersignal_maps} \
            -o $(basename {output}) 2>&1 | tee -a {log}
        echo "[$(date)] Completed workspace rule with signal {params.signallabel}" >> {log}
        """

rule limits:
    input: "{path}__{signallabel}.root"
    output: 
        txt="{path}_limits__{signallabel}.txt",
        json="{path}_limits__{signallabel}.json"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        freeze_parameters = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/limits_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting limits rule with signal {params.signallabel}" > {log}
        
        echo "[$(date)] Running AsymptoticLimits" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M AsymptoticLimits $(basename {input}) \
            --redefineSignalPOIs r{params.signallabel} \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            -n _{params.signallabel}" \
            2>&1 | tee -a {log} $(basename {output.txt})
            
        echo "[$(date)] Running CollectLimits" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combineTool.py -M CollectLimits \
            higgsCombine_{params.signallabel}.AsymptoticLimits.mH120.root \
            -o $(basename {output.json})" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed limits rule with signal {params.signallabel}" >> {log}
        """

rule significance:
    input: "{path}__{signallabel}.root"
    output:
        observed="{path}_significance_observed__{signallabel}.txt",
        expected="{path}_significance_expected__{signallabel}.txt"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        freeze_parameters = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/significance_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting significance rule with signal {params.signallabel}" > {log}

        echo "[$(date)] Running observed significance" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M Significance $(basename {input}) \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            --redefineSignalPOIs r{params.signallabel} \
            -n _{params.signallabel}" \
            2>&1 | tee -a {log} $(basename {output.observed})
            
        echo "[$(date)] Running expected significance" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M Significance $(basename {input}) \
            --redefineSignalPOIs r{params.signallabel} \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            -n _{params.signallabel} \
            -t -1 --expectSignal=1" \
            2>&1 | tee -a {log} $(basename {output.expected})

        echo "[$(date)] Completed significance rule with signal {params.signallabel}" >> {log}
        """

rule likelihood_scan:
    input: "{path}__{signallabel}.root"
    output: "{path}_likelihood_scan__{signallabel}.pdf"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        freeze_parameters = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/likelihood_scan_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting likelihood_scan rule with signal {params.signallabel}" > {log}
        
        echo "|---- Running initial fit"
        echo "[$(date)] Running initial fit" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M MultiDimFit -d $(basename {input}) \
            -n _$(basename {input} .root)_{params.signallabel} \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            --saveWorkspace --robustFit 1" 2>&1 | tee -a {log}
            
        echo "|---- Running MultiDimFit"
        echo "[$(date)] Running MultiDimFit" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M MultiDimFit \
            -d higgsCombine_$(basename {input} .root)_{params.signallabel}.MultiDimFit.mH120.root \
            -n _$(basename {input} .root)_{params.signallabel}_final \
            -P r{params.signallabel} \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            --snapshotName MultiDimFit --rMin -10 --rMax 10 --algo grid --points 50 --alignEdges 1" 2>&1 | tee -a {log}
            
        echo "|---- Plotting likelihood scan"
        echo "[$(date)] Plotting likelihood scan" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            plot1DScan.py higgsCombine_$(basename {input} .root)_{params.signallabel}_final.MultiDimFit.mH120.root \
            --POI r{params.signallabel} -o $(basename {output} .pdf)" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed likelihood_scan rule with signal {params.signallabel}" >> {log}
        """

rule impacts:
    input: "{path}__{signallabel}.root"
    output: "{path}_impacts__{signallabel}.pdf"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        set_parameters_ranges = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/impacts_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting impacts rule with signal {params.signallabel}" > {log}
        
        echo "|---- Running initial fit"
        echo "[$(date)] Running initial fit" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combineTool.py -M Impacts -d $(basename {input}) \
            --doInitialFit --robustFit 1 -m 125 \
            --setParametersRanges r{params.signallabel}=-10,10{params.set_parameters_ranges} \
            {params.set_parameters_zero} \
            -n $(basename {input} .root)_{params.signallabel}" 2>&1 | tee -a {log}
            
        echo "|---- Running fits per systematic"
        echo "[$(date)] Running fits per systematic" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combineTool.py -M Impacts -d $(basename {input}) \
            --doFits --robustFit 1 -m 125 --parallel 4 \
            --setParametersRanges r{params.signallabel}=-10,10{params.set_parameters_ranges} \
            {params.set_parameters_zero} \
            -n $(basename {input} .root)_{params.signallabel}" 2>&1 | tee -a {log}
            
        echo "|---- Running merging results"
        echo "[$(date)] Running merging results" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combineTool.py -M Impacts \
            -m 125 -n $(basename {input} .root)_{params.signallabel} \
            -d $(basename {input}) \
            -o impacts_combine_$(basename {input} .root)_{params.signallabel}_exp.json" 2>&1 | tee -a {log}
            
        echo "|---- Running creating pdf"
        echo "[$(date)] Running creating pdf" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            plotImpacts.py -i impacts_combine_$(basename {input} .root)_{params.signallabel}_exp.json \
            -o $(basename {output} .pdf) \
            --POI r{params.signallabel} \
            --per-page 20 --left-margin 0.3 --height 400 --label-size 0.04" 2>&1 | tee -a {log}
            
        echo "[$(date)] Cleaning up temporary files" >> {log}
        rm $(dirname {input})/higgsCombine_*Fit* 2>&1 | tee -a {log}
        
        echo "[$(date)] Completed impacts rule with signal {params.signallabel}" >> {log}
        """

rule gof:
    input: "{path}__{signallabel}.root"
    output: "{path}_gof__{signallabel}.pdf"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/gof_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting gof rule with signal {params.signallabel}" > {log}
        
        echo "|---- Running Goodness of Fit tests data"
        echo "[$(date)] Running Goodness of Fit tests data" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M GoodnessOfFit $(basename {input}) \
            --algo saturated \
            {params.set_parameters_zero} \
            -n _$(basename {input} .root)_{params.signallabel}_gof_data" \
            2>&1 | tee -a {log} gof_data_$(basename {input} .root)_{params.signallabel}.txt
            
        echo "|---- Running Goodness of Fit tests toys"
        echo "[$(date)] Running Goodness of Fit tests toys" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M GoodnessOfFit $(basename {input}) \
            --toysFrequentist -t 500 --algo saturated  \
            -n _$(basename {input} .root)_{params.signallabel}_gof_toys" \
            2>&1 | tee -a {log} gof_toys_$(basename {input} .root)_{params.signallabel}.txt
            
        echo "|---- Collecting Goodness of Fit results"
        echo "[$(date)] Collecting Goodness of Fit results" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combineTool.py -M CollectGoodnessOfFit \
            --input higgsCombine_$(basename {input} .root)_{params.signallabel}_gof_data.GoodnessOfFit.mH120.root \
            higgsCombine_$(basename {input} .root)_{params.signallabel}_gof_toys.GoodnessOfFit.mH120.123456.root" \
            -o gof_$(basename {input} .root)_{params.signallabel}.json 2>&1 | tee -a {log}
            
        echo "|---- Plotting Goodness of Fit results"
        echo "[$(date)] Plotting Goodness of Fit results" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            plotGof.py gof_$(basename {input} .root)_{params.signallabel}.json \
            --statistic staturated --mass 120.0 \
            --output $(basename {output} .pdf)" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed gof rule with signal {params.signallabel}" >> {log}
        """

rule postfit:
    input: "{path}__{signallabel}.root"
    output: "{path}_postfit__{signallabel}.pdf"
    params:
        signallabel = "{signallabel}",
        set_parameters_zero = "",
        freeze_parameters = "",
        container_wrapper = config.get("container_wrapper", "./run_container combine")
    log: "output/logs/postfit_{path}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting postfit rule with signal {params.signallabel}" > {log}
        
        echo "[$(date)] Running postfit b-only" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M FitDiagnostics $(basename {input}) \
            --redefineSignalPOIs r{params.signallabel} \
            {params.set_parameters_zero} \
            --setParameters r{params.signallabel}=0 \
            {params.freeze_parameters} \
            -n _$(basename {input} .root)_prefit_bonly \
            --saveShapes --saveWithUncertainties --plots" 2>&1 | tee -a {log}
        
        echo "[$(date)] Running diffNuisances for b-only" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            python /home/cmsusr/CMSSW_11_3_4/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
            -p r{params.signallabel} \
            -a fitDiagnostics_$(basename {input} .root)_prefit_bonly.root \
            -g diffNuisances_$(basename {input} .root)_prefit_bonly.root" 2>&1 | tee -a {log}

        echo "[$(date)] Running postfit s+b" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            combine -M FitDiagnostics $(basename {input}) \
            --redefineSignalPOIs r{params.signallabel} \
            {params.set_parameters_zero} \
            {params.freeze_parameters} \
            -n _$(basename {input} .root)_prefit_sb \
            --saveShapes --saveWithUncertainties --plots" 2>&1 | tee -a {log}

        mkdir -p $(dirname {input})/fitDiagnostics_sb/
        mv $(dirname {input})/*th1x* $(dirname {input})/fitDiagnostics_sb/ 2>/dev/null || true
        mv $(dirname {input})/covariance* $(dirname {input})/fitDiagnostics_sb/ 2>/dev/null || true

        echo "[$(date)] Running diffNuisances for s+b" >> {log}
        {params.container_wrapper} "cd $(dirname {input}) &&\
            python /home/cmsusr/CMSSW_11_3_4/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
            -p r{params.signallabel} \
            -a fitDiagnostics_$(basename {input} .root)_prefit_sb.root \
            -g diffNuisances_$(basename {input} .root)_prefit_sb.root" 2>&1 | tee -a {log}
        
        echo "[$(date)] Running postfit plots for b-only" >> {log}
        pwd -LP

        {params.container_wrapper} "cd $(dirname {input}) &&\
            python3 plots/make_postfit_plot.py \
            -i fitDiagnostics_$(basename {input} .root)_prefit_sb.root \
            -o $(basename {input} .root)/plots/ -t prefit

        {params.container_wrapper} "cd $(dirname {input}) &&\
            python3 plots/make_postfit_plot.py \
            -i fitDiagnostics_$(basename {input} .root)_prefit_sb.root \
            -o $(basename {input} .root)/plots/ -t fit_b

        {params.container_wrapper} "cd $(dirname {input}) &&\
            python3 plots/make_postfit_plot.py \
            -i fitDiagnostics_$(basename {input} .root)_prefit_sb.root \
            -o $(basename {input} .root)/plots/ -t fit_s

        echo "[$(date)] Completed postfit rule with signal {params.signallabel}" >> {log}
        """