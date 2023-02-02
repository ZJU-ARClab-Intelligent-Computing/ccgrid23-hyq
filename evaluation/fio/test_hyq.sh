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
scheme=hyq

warmup() {
    $SCRIPTDIR/../../scripts/host/use_sched.sh none

    local filenames=""

    for device in $DEVICES; do
        filenames="$filenames --name=$(basename $device) --filename=$device"
    done

    fio --name=global \
        --bs=4k --numjobs=8 --iodepth=64 --rw=randwrite --runtime=1800 \
        --direct=1 --group_reporting --ioengine=libaio --time_based=1 \
        $filenames

    $SCRIPTDIR/../../scripts/host/use_sched.sh qd_rw_based
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

# Setup test env.
sudo nvme disconnect-all && \
ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/setup.sh hyq ${TARGET_NVMF_ADDR} 1 && \
$SCRIPTDIR/../../scripts/host/setup.sh hyq ${TARGET_NVMF_ADDR} 2

for ((i = 0; i < $cycle_cnt; i++)); do
    echo "Warm up first..." 
    warmup

    echo 0 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
    echo 32,32 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds

    benchmark randread_0_4k_4k_8_64_12500_2_48 $i

    benchmark randread_0_4k_4k_8_64_37500_2_48 $i

    benchmark randread_0_4k_4k_8_64_45000_2_48 $i

    benchmark randread_0_4k_4k_8_64_62500_2_48 $i

    benchmark randread_0_4k_4k_8_64_87500_2_48 $i

    benchmark randread_0_4k_4k_8_64_112500_2_48 $i

    echo 0 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
    echo 32,32 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds

    benchmark randrw_0_128k_128k_8_64_2147483647_2_48 $i
    warmup

    benchmark randrw_30_128k_128k_8_64_2147483647_2_48 $i
    warmup

    benchmark randrw_50_128k_128k_8_64_2147483647_2_48 $i
    warmup

    echo 1 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
    echo 16,16 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds

    benchmark randrw_70_128k_128k_8_64_2147483647_2_48 $i
    warmup

    echo 1 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
    echo 64,64 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds

    benchmark randrw_100_128k_128k_8_64_2147483647_2_48 $i
    warmup

    benchmark randread_0_128k_4k_8_64_2147483647_2_48 $i

    benchmark randread_0_128k_128k_8_64_2147483647_2_48 $i

    benchmark randread_0_128k_4k_1_1_2147483647_1_48 $i

    benchmark randread_0_128k_128k_1_1_2147483647_1_48 $i

    $SCRIPTDIR/../../scripts/host/use_sched.sh qd_rw_based
    echo 0 | sudo tee /sys/module/qd_rw_based/parameters/offload_op
    echo 32,32 | sudo tee /sys/module/qd_rw_based/parameters/offload_qds

    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/limit_cpu.sh 2
    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/set_irq_affinity.sh $TARGET_SNIC_NAME
    benchmark randread_0_4k_4k_8_64_2147483647_2_2 $i

    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/limit_cpu.sh 4
    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/set_irq_affinity.sh $TARGET_SNIC_NAME
    benchmark randread_0_4k_4k_8_64_2147483647_2_4 $i

    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/limit_cpu.sh 6
    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/set_irq_affinity.sh $TARGET_SNIC_NAME
    benchmark randread_0_4k_4k_8_64_2147483647_2_6 $i

    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/limit_cpu.sh 8
    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/set_irq_affinity.sh $TARGET_SNIC_NAME
    benchmark randread_0_4k_4k_8_64_2147483647_2_8 $i

    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/limit_cpu.sh 48
    ssh ssh root@${TARGET_SSH_ADDR} $SCRIPTDIR/../../scripts/target/set_irq_affinity.sh $TARGET_SNIC_NAME
done
