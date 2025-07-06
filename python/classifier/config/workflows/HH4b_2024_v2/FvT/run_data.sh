export LPCUSER="chuyuanl"
export CERNUSER="c/chuyuan"
export WFS="classifier/config/workflows/HH4b_2024_v2/FvT"
export BASE="root://cmseos.fnal.gov//store/user/${LPCUSER}/HH4b_2024_v2"
export MODEL="${BASE}/classifier/FvT/"
export WEB="root://eosuser.cern.ch//eos/user/${CERNUSER}/www/HH4b/classifier/HH4b_2024_v2/FvT/"
export GMAIL=~/gmail.yml

# check port
if [ -z "$1" ]; then
    port=10200
else
    port=$1
fi

# train
./pyml.py \
    template "user: ${LPCUSER}" $WFS/train_data.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}" -flag debug

# plot
./pyml.py analyze \
    --results ${MODEL}/data/result.json \
    -analysis HCR.LossROC \
    -setting IO "output: ${WEB}" \
    -setting IO "report: data" \
    -setting Monitor "address: :${port}"

# evaluate
./pyml.py \
    template "user: ${LPCUSER}" $WFS/evaluate_data.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}"

if [ -e "$GMAIL" ]; then
    ./pyml.py analyze \
        -analysis notify.Gmail \
        --title "FvT done" \
        --body "All jobs done at $(date)" \
        --labels HH4b AN_v4 \
        -from $GMAIL \
        -setting Monitor "address: :${port}"
fi