include: "../helpers/common.smk"

rule workspace:
    input: "{workspace}{datacard}.txt"
    output:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Generate the map options for the othersignal(s)
        othersignal_maps = lambda wildcards: (
            " ".join([f"--PO 'map=.*/{sig}:r{sig}[1,-10,10]'" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    log:
        "{workspace}logs/workspace_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting workspace rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            text2workspace.py {wildcards.datacard}.txt \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose \
            --PO 'map=.*/{params.signallabel}:r{params.signallabel}[1,-10,10]' \
            {params.othersignal_maps} \
            -o {wildcards.datacard}__{wildcards.signallabel}.root" 2>&1 | tee -a {log}
        echo "[$(date)] Completed workspace rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """

rule limits:
    input:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Freeze and set parameters string handling both single value and list
        freeze_set_params = lambda wildcards: (
            " ".join([f"--setParameters r{sig}=0 --freezeParameters r{sig}" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    output:
        txt="{workspace}limits_{datacard}__{signallabel}.txt",
        json="{workspace}limits_{datacard}__{signallabel}.json"
    log:
        "{workspace}logs/limits_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting limits rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        
        echo "[$(date)] Running AsymptoticLimits" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M AsymptoticLimits {wildcards.datacard}__{params.signallabel}.root \
            --redefineSignalPOIs r{params.signallabel} \
            -n _{params.signallabel} \
            {params.freeze_set_params}" \
            2>&1 | tee -a {log} {output.txt}
            
        echo "[$(date)] Running CollectLimits" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combineTool.py -M CollectLimits \
            higgsCombine_{params.signallabel}.AsymptoticLimits.mH120.root \
            -o limits_{wildcards.datacard}__{params.signallabel}.json" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed limits rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """

rule significance:
    input:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Freeze and set parameters string handling both single value and list
        freeze_set_params = lambda wildcards: (
            " ".join([f"--setParameters r{sig}=0 --freezeParameters r{sig}" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    output:
        observed="{workspace}significance_observed_{datacard}__{signallabel}.txt",
        expected="{workspace}significance_expected_{datacard}__{signallabel}.txt"
    log:
        "{workspace}logs/significance_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting significance rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        
        echo "[$(date)] Running observed significance" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M Significance {wildcards.datacard}__{params.signallabel}.root \
            --redefineSignalPOIs r{params.signallabel} \
            -n _{params.signallabel} \
            {params.freeze_set_params}" \
            2>&1 | tee -a {log} {output.observed}
            
        echo "[$(date)] Running expected significance" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M Significance {wildcards.datacard}__{params.signallabel}.root \
            --redefineSignalPOIs r{params.signallabel} \
            -n _{params.signallabel} \
            -t -1 --expectSignal=1 \
            {params.freeze_set_params}" \
            2>&1 | tee -a {log} {output.expected}
            
        echo "[$(date)] Completed significance rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """

rule likelihood_scan:
    input:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Freeze and set parameters string handling both single value and list
        freeze_set_params = lambda wildcards: (
            " ".join([f"--setParameters r{sig}=0 --freezeParameters r{sig}" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    output:
        "{workspace}likelihood_scan_{datacard}__{signallabel}.pdf"
    log:
        "{workspace}logs/likelihood_scan_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting likelihood_scan rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        
        echo "|---- Running initial fit"
        echo "[$(date)] Running initial fit" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M MultiDimFit -d {wildcards.datacard}__{params.signallabel}.root \
            -n _{wildcards.datacard}_{params.signallabel} \
            --saveWorkspace --robustFit 1 \
            {params.freeze_set_params}" 2>&1 | tee -a {log}
            
        echo "|---- Running MultiDimFit"
        echo "[$(date)] Running MultiDimFit" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M MultiDimFit \
            -d higgsCombine_{wildcards.datacard}_{params.signallabel}.MultiDimFit.mH120.root \
            -n _{wildcards.datacard}_{params.signallabel}_final \
            -P r{params.signallabel} \
            --snapshotName MultiDimFit --rMin -10 --rMax 10 --algo grid --points 50 --alignEdges 1 \
            {params.freeze_set_params}" 2>&1 | tee -a {log}
            
        echo "|---- Plotting likelihood scan"
        echo "[$(date)] Plotting likelihood scan" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            plot1DScan.py higgsCombine_{wildcards.datacard}_{params.signallabel}_final.MultiDimFit.mH120.root \
            --POI r{params.signallabel} -o likelihood_scan_{wildcards.datacard}__{params.signallabel}" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed likelihood_scan rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """

rule impacts:
    input:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Parameter range string conditionally handling both single value and list
        param_range = lambda wildcards: (
            f"r{get_case_param(wildcards, 'signallabel')}=-10,10" + 
            (":" + ":".join([f"r{sig}=0,0" for sig in get_case_param(wildcards, "othersignal").split(",")]) 
             if get_case_param(wildcards, "othersignal") else "")
        ),
        # Freeze and set parameters string handling both single value and list
        freeze_set_params = lambda wildcards: (
            " ".join([f"--setParameters r{sig}=0 --freezeParameters r{sig}" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    output:
        "{workspace}impacts_combine_{datacard}__{signallabel}_observed.pdf"
    log:
        "{workspace}logs/impacts_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting impacts rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        
        echo "|---- Running initial fit"
        echo "[$(date)] Running initial fit" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combineTool.py -M Impacts -d {wildcards.datacard}__{params.signallabel}.root \
            --doInitialFit --robustFit 1 -m 125 \
            -n {wildcards.datacard}_{params.signallabel} \
            --setParameterRanges {params.param_range} \
            {params.freeze_set_params}" 2>&1 | tee -a {log}
            
        echo "|---- Running fits per systematic"
        echo "[$(date)] Running fits per systematic" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combineTool.py -M Impacts -d {wildcards.datacard}__{params.signallabel}.root \
            --doFits --robustFit 1 -m 125 --parallel 4 \
            -n {wildcards.datacard}_{params.signallabel} \
            --setParameterRanges {params.param_range} \
            {params.freeze_set_params}" 2>&1 | tee -a {log}
            
        echo "|---- Running merging results"
        echo "[$(date)] Running merging results" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combineTool.py -M Impacts \
            -m 125 -n {wildcards.datacard}_{params.signallabel} \
            -d {wildcards.datacard}__{params.signallabel}.root \
            -o impacts_combine_{wildcards.datacard}_{params.signallabel}_exp.json" 2>&1 | tee -a {log}
            
        echo "|---- Running creating pdf"
        echo "[$(date)] Running creating pdf" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            plotImpacts.py -i impacts_combine_{wildcards.datacard}_{params.signallabel}_exp.json \
            -o impacts_combine_{wildcards.datacard}__{params.signallabel}_observed \
            --POI r{params.signallabel} \
            --per-page 20 --left-margin 0.3 --height 400 --label-size 0.04" 2>&1 | tee -a {log}
            
        echo "[$(date)] Cleaning up temporary files" >> {log}
        rm {wildcards.workspace}/higgsCombine_*Fit* 2>&1 | tee -a {log}
        
        echo "[$(date)] Completed impacts rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """

rule gof:
    input:
        "{workspace}{datacard}__{signallabel}.root"
    params:
        signallabel = lambda wildcards: get_case_param(wildcards, "signallabel"),
        othersignal = lambda wildcards: get_case_param(wildcards, "othersignal"),
        # Freeze and set parameters string handling both single value and list
        set_params = lambda wildcards: (
            " ".join([f"--setParameters r{sig}=0" for sig in get_case_param(wildcards, "othersignal").split(",")])
            if get_case_param(wildcards, "othersignal") else ""
        )
    output:
        "{workspace}gof_{datacard}__{signallabel}.pdf"
    log:
        "{workspace}logs/gof_{datacard}__{signallabel}.log"
    shell:
        """
        mkdir -p $(dirname {log})
        echo "[$(date)] Starting gof rule for {wildcards.datacard} with signal {params.signallabel}" > {log}
        
        echo "|---- Running Goodness of Fit tests data"
        echo "[$(date)] Running Goodness of Fit tests data" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M GoodnessOfFit {wildcards.datacard}__{params.signallabel}.root \
            --algo saturated \
            -n _{wildcards.datacard}_{params.signallabel}_gof_data \
            {params.set_params}" 2>&1 | tee -a {log} {wildcards.workspace}/gof_data_{wildcards.datacard}_{params.signallabel}.txt
            
        echo "|---- Running Goodness of Fit tests toys"
        echo "[$(date)] Running Goodness of Fit tests toys" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combine -M GoodnessOfFit {wildcards.datacard}__{params.signallabel}.root \
            --toysFrequentist -t 500 --algo saturated  \
            -n _{wildcards.datacard}_{params.signallabel}_gof_toys \
            {params.set_params}" 2>&1 | tee -a {log} {wildcards.workspace}/gof_toys_{wildcards.datacard}_{params.signallabel}.txt
            
        echo "|---- Collecting Goodness of Fit results"
        echo "[$(date)] Collecting Goodness of Fit results" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            combineTool.py -M CollectGoodnessOfFit \
            --input higgsCombine_{wildcards.datacard}_{params.signallabel}_gof_data.GoodnessOfFit.mH120.root \
            higgsCombine_{wildcards.datacard}_{params.signallabel}_gof_toys.GoodnessOfFit.mH120.123456.root" \
            -o gof_{wildcards.datacard}_{params.signallabel}.json 2>&1 | tee -a {log}
            
        echo "|---- Plotting Goodness of Fit results"
        echo "[$(date)] Plotting Goodness of Fit results" >> {log}
        ./run_container combine "cd {wildcards.workspace} &&\
            plotGof.py gof_{wildcards.datacard}_{params.signallabel}.json \
            --statistic staturated --mass 120.0 \
            --output gof_{wildcards.datacard}__{params.signallabel}" 2>&1 | tee -a {log}
            
        echo "[$(date)] Completed gof rule for {wildcards.datacard} with signal {params.signallabel}" >> {log}
        """
