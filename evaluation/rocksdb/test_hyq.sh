#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

# Apply configurations.
source $SCRIPTDIR/../config.sh

# Setup test env.
sudo nvme disconnect-all && \
ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/setup.sh hyq ${TARGET_NVMF_ADDR} 1 && \
$SCRIPTDIR/../../scripts/host/setup.sh hyq ${TARGET_NVMF_ADDR} 2
$SCRIPTDIR/../../scripts/host/use_sched.sh qd_rw_based

scheme=hyq
cd $SCRIPTDIR/ && \
mkdir -p ./rocksdb_res/$scheme ./rocksdb_cpu/$scheme ./rocksdb_tgt_cpu/$scheme

cycle_cnt=1
runtime=300
benchmarks="readrandom overwrite readwhilewriting mergerandom"

for ((i = 0; i < $cycle_cnt; i++)); do
    for benchmark in $benchmarks; do
        if [ $benchmark == "readrandom" ]; then
            echo 0 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
            echo 32,32 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds
        else
            echo 1 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
            echo 16,16 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds
        fi

        jobpids=""

        mkdir -p $SCRIPTDIR/rocksdb_res/$scheme/${benchmark}_$i
        $SCRIPTDIR/db_bench.sh $DEVICES $benchmark $SCRIPTDIR/rocksdb_res/$scheme/${benchmark}_$i &
        jobpids="$jobpids $!"

        top -d 2 -b -n ${runtime} | grep %Cpu > $SCRIPTDIR/rocksdb_cpu/$scheme/${benchmark}_$i.log &
        jobpids="$jobpids $!"

        ssh root@${TARGET_SSH_ADDR} top -d 2 -b -n ${runtime} | grep %Cpu > $SCRIPTDIR/rocksdb_tgt_cpu/$scheme/${benchmark}_$i.log &
        jobpids="$jobpids $!"

        wait $jobpids
    done
done
