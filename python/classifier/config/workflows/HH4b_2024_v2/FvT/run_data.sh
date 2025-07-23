export LPCUSER="chuyuanl"
export CERNUSER="c/chuyuan"
export BASE="root://cmseos.fnal.gov//store/user/${LPCUSER}/HH4b_2024_v2"
export MODEL="${BASE}/classifier/FvT/"
export FvT="${BASE}/friend/FvT/"
export PLOT="root://eosuser.cern.ch//eos/user/${CERNUSER}/www/HH4b/classifier/HH4b_2024_v2/"

export WFS="classifier/config/workflows/HH4b_2024_v2/FvT"

# check port
if [ -z "$1" ]; then
    port=10200
else
    port=$1
fi

# train
./pyml.py \
    template "model: ${MODEL}" $WFS/train_data.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}" -flag debug

# plot
./pyml.py analyze \
    --results ${MODEL}/result.json \
    -analysis HCR.LossROC \
    -setting IO "output: ${PLOT}" \
    -setting IO "report: FvT" \
    -setting Monitor "address: :${port}"

# evaluate
./pyml.py \
    template "{model: ${MODEL}, FvT: ${FvT}}" $WFS/evaluate_data.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}"
