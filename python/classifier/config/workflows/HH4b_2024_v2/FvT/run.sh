# change these vars #
export LPCUSER="chuyuanl"
export CERNUSER="c/chuyuan"
export BASE="root://cmseos.fnal.gov//store/user/${LPCUSER}/HH4b_2024_v2"
export MODEL="${BASE}/classifier/FvT/"
export FvT="${BASE}/friend/FvT/"
export PLOT="root://eosuser.cern.ch//eos/user/${CERNUSER}/www/HH4b/classifier/HH4b_2024_v2/"
#####################

export WFS="classifier/config/workflows/HH4b_2024_v2/FvT"

# the first argument can be a port
if [ -z "$1" ]; then
    port=10200
else
    port=$1
fi

# train with train.yml and common.yml configs
./pyml.py \
    template "model: ${MODEL}" $WFS/train.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}" \
    -flag debug # use debug flag

# plot the AUC and ROC
./pyml.py analyze \
    --results ${MODEL}/result.json \
    -analysis HCR.LossROC \
    -setting IO "output: ${PLOT}" \
    -setting IO "report: FvT" \
    -setting Monitor "address: :${port}"

# evaluate with evaluate.yml and common.yml configs
./pyml.py \
    template "{model: ${MODEL}, FvT: ${FvT}}" $WFS/evaluate.yml \
    -from $WFS/../common.yml \
    -setting Monitor "address: :${port}"
