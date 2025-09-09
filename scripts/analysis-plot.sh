source "src/scripts/common.sh"

# Parse output base argument
OUTPUT_BASE_DIR=$(parse_output_base_arg "output" "$@")
if [ $? -ne 0 ]; then
    echo "Error parsing output base argument. Use --output-base DIR to specify the output directory. Default DIR=output/"
    exit 1
fi

# Create output directory
INPUT_DIR="$OUTPUT_BASE_DIR/tools_merge_test"
JOB="analysis_plot"
OUTPUT_DIR=$OUTPUT_BASE_DIR/$JOB
create_output_directory "$OUTPUT_DIR"

display_section_header "Running plotting test"
run_command python coffea4bees/plots/makePlots.py \
    $INPUT_DIR/test.coffea \
    --doTest \
    -o $OUTPUT_DIR \
    -m coffea4bees/plots/metadata/plotsAll.yml

display_section_header "Checking if pdf files exist"
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zz.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zh.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_hh.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR_vs_SB/data/SvB_MA_ps.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR_vs_SB/HH4b/SvB_MA_ps.pdf
ls $OUTPUT_DIR/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/data/v4j_mass.pdf
ls $OUTPUT_DIR/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/HH4b/v4j_mass.pdf 
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/data/quadJet_min_dr_close_vs_other_m.pdf 
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/HH4b/quadJet_min_dr_close_vs_other_m.pdf
ls $OUTPUT_DIR/RunII/passPreSel/threeTag/SR/Multijet/quadJet_min_dr_close_vs_other_m.pdf 


display_section_header "check making the plots from yaml "
run_command python coffea4bees/plots/plot_from_yaml.py \
    --input_yaml $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zz.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zh.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/SvB_MA_ps_hh.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR_vs_SB/data/SvB_MA_ps.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR_vs_SB/HH4b/SvB_MA_ps.yaml \
        $OUTPUT_DIR/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/data/v4j_mass.yaml \
        $OUTPUT_DIR/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/HH4b/v4j_mass.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/data/quadJet_min_dr_close_vs_other_m.yaml \
        $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/HH4b/quadJet_min_dr_close_vs_other_m.yaml \
        $OUTPUT_DIR/RunII/passPreSel/threeTag/SR/Multijet/quadJet_min_dr_close_vs_other_m.yaml \
        --out $OUTPUT_DIR/test_plots_from_yaml 

display_section_header "Checking if pdf files exist"
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zz.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zh.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR/SvB_MA_ps_hh.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR_vs_SB/data/SvB_MA_ps.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR_vs_SB/HH4b/SvB_MA_ps.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/data/v4j_mass.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/HH4b/v4j_mass.pdf 
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR/data/quadJet_min_dr_close_vs_other_m.pdf 
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/fourTag/SR/HH4b/quadJet_min_dr_close_vs_other_m.pdf
ls $OUTPUT_DIR/test_plots_from_yaml/RunII/passPreSel/threeTag/SR/Multijet/quadJet_min_dr_close_vs_other_m.pdf 
