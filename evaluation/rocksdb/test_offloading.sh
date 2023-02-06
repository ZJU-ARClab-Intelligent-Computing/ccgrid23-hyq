#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

# Apply configurations.
source $SCRIPTDIR/../config.sh

# We only need one device.
DEVICES=$(echo $DEVICES | awk '{print $1}')

# Setup test env.
sudo nvme disconnect-all && \
ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/setup.sh main ${TARGET_NVMF_ADDR} 1 && \
$SCRIPTDIR/../../scripts/host/setup.sh main ${TARGET_NVMF_ADDR} 2

scheme=offloading
cd $SCRIPTDIR/ && \
mkdir -p ./rocksdb_res/$scheme ./rocksdb_cpu/$scheme ./rocksdb_tgt_cpu/$scheme

cycle_cnt=1
runtime=300
benchmarks="readrandom overwrite readwhilewriting mergerandom"

for ((i = 0; i < $cycle_cnt; i++)); do
    for benchmark in $benchmarks; do
        jobpids=""

        mkdir -p $SCRIPTDIR/rocksdb_res/$scheme/${benchmark}_$i
        ./db_bench.sh $DEVICES $benchmark $SCRIPTDIR/rocksdb_res/$scheme/${benchmark}_$i &
        jobpids="$jobpids $!"

        top -d 2 -b -n ${runtime} | grep %Cpu > $SCRIPTDIR/rocksdb_cpu/$scheme/${benchmark}_$i.log &
        jobpids="$jobpids $!"

        ssh root@${TARGET_SSH_ADDR} top -d 2 -b -n ${runtime} | grep %Cpu > $SCRIPTDIR/rocksdb_tgt_cpu/$scheme/${benchmark}_$i.log &
        jobpids="$jobpids $!"

        wait $jobpids
    done
done
