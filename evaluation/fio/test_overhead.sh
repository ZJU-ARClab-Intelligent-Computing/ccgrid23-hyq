#!/bin/bash

SCRIPTDIR=$(dirname $(readlink -f "$0"))

# Apply configurations.
source $SCRIPTDIR/../config.sh

# Output dirs.
fio_res="$SCRIPTDIR/fio_res"
cpu_res="$SCRIPTDIR/cpu_res"
tgt_cpu_res="$SCRIPTDIR/tgt_cpu_res"

# Test parameters.
cycle_cnt=1
runtime=100
sleeptime=1

warmup() {
    local filenames=""

    for device in $DEVICES; do
        filenames="$filenames --name=$(basename $device) --filename=$device"
    done

    fio --name=global \
        --bs=4k --numjobs=8 --iodepth=64 --rw=randwrite --runtime=1800 \
        --direct=1 --group_reporting --ioengine=libaio --time_based=1 \
        $filenames
}

# $1 = jobname
# $2 = cycle
benchmark() {
    local jobpid=""
    local jobname=$1; local cycle=$2
    local resname=${scheme}_${jobname}_${cycle}

    fio $SCRIPTDIR/fio-job/$jobname --output-format=json --output=$fio_res/$resname.json &
    jobpid="$jobpid $!"

    # Wait for fio starting up. 
    sleep $sleeptime

    top -d 2 -b -n $runtime | grep %Cpu > $cpu_res/$resname.log &
    ssh root@${TARGET_SSH_ADDR} top -d 2 -b -n $runtime | grep %Cpu > $tgt_cpu_res/$resname.log

    wait $jobpid

    # Let the hardwares have a rest.
    sleep 60
}

# echo "Warm up first..." 
# warmup

for ((i = 0; i < $cycle_cnt; i++)); do
    # Setup test env.
    sudo nvme disconnect-all && \
    ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/setup.sh main ${TARGET_NVMF_ADDR} 0 && \
    $SCRIPTDIR/../../scripts/host/setup.sh main ${TARGET_NVMF_ADDR} 2
    scheme=non-offloading

    benchmark randread_0_4k_4k_8_64_2147483647_2_48 $i

    benchmark randread_0_4k_4k_1_1_2147483647_1_48 $i

    # Setup test env.
    sudo nvme disconnect-all && \
    ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/setup.sh hyq ${TARGET_NVMF_ADDR} 1 && \
    $SCRIPTDIR/../../scripts/host/setup.sh hyq ${TARGET_NVMF_ADDR} 2
    $SCRIPTDIR/../../scripts/host/use_sched.sh basic
    scheme=hyq

    benchmark randread_0_4k_4k_8_64_2147483647_2_48 $i

    benchmark randread_0_4k_4k_1_1_2147483647_1_48 $i
done
