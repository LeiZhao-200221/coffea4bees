export LPCUSER="chuyuanl"
export CERNUSER="c/chuyuan"
export WFS="classifier/config/workflows/HH4b_2024_v2/SvB"
export BASE="root://cmseos.fnal.gov//store/user/${LPCUSER}/HH4b_2024_v2"
export MODEL="${BASE}/classifier/SvB/"
export WEB="root://eosuser.cern.ch//eos/user/${CERNUSER}/www/HH4b/classifier/HH4b_2024_v2/SvB/"
export GMAIL=~/gmail.yml

# check port
if [ -z "$1" ]; then
    port=10200
else
    port=$1
fi


# train and make plots
./pyml.py \
    template "user: ${LPCUSER}" $WFS/train.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}" -flag debug

./pyml.py analyze \
    --results ${MODEL}/ggF_baseline/result.json \
    -analysis HCR.LossROC \
    -setting IO "output: ${WEB}" \
    -setting IO "report: ggF_baseline" \
    -setting Monitor "address: :${port}"

# evaluate
./pyml.py \
    template "user: ${LPCUSER}" $WFS/evaluate.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}"

if [ -e "$GMAIL" ]; then
    ./pyml.py analyze \
        -analysis notify.Gmail \
        --title "SvB jobs done" \
        --body "All jobs done at $(date)" \
        --labels Classifier HH4b \
        -from $GMAIL \
        -setting Monitor "address: :${port}"
fi