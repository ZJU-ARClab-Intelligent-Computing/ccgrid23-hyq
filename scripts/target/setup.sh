#!/bin/bash

if [ ! $# -eq 2 ]; then
    echo "usage: $0 <branch> <offload>"
    exit -1
fi

NUM_P2P_QUEUES_PER_DEV=32
MODULEDIR=${HOME}/nvme-target
SCRIPTDIR=$(dirname $(readlink -f "$0"))

if [ ! -d ${MODULEDIR} ]; then
    cd ${HOME}
    git clone https://github.com/nickyc975/nvme-target.git
    cd nvme-target
    ./configure --with-core-mod \
                --with-ipoib-mod \
                --with-ipoib-cm \
                --with-ipoib-allmulti \
                --with-srp-mod \
                --with-rxe-mod \
                --with-user_mad-mod \
                --with-user_access-mod \
                --with-addr_trans-mod \
                --with-mlx5-mod \
                --with-mlxfw-mod \
                --with-iser-mod \
                --with-isert-mod \
                --with-nfsrdma-mod \
                --with-nvmf_host-mod \
                --with-nvmf_target-mod \
                -j40
    make -j40
    sudo -S make install -j40
fi

if [ ! -f ${SCRIPTDIR}/addr ]; then
    echo "Please fill target address in file ${SCRIPTDIR}/addr"
    exit -1
fi
NVME_TARGET_ADDR=$(cat ${SCRIPTDIR}/addr)

# Disable hyper-thread
echo off | sudo tee /sys/devices/system/cpu/smt/control

# Set CPUs to max performance
for cpu_id in $(cat /sys/devices/system/cpu/online | tr "-" " " | xargs seq); do
    echo performance | sudo tee /sys/devices/system/cpu/cpu$cpu_id/cpufreq/scaling_governor
done

# Count number of possible CPUs
# NUM_POSSIBLE_CPUS=1
# NUM_POSSIBLE_CPUS=$(cat /sys/devices/system/cpu/possible | tr "-" " " | xargs seq | wc -w)

if [ $(/usr/sbin/lsmod | grep -w nvmet_rdma | wc -l) -eq 0 ]; then
    sudo -S /usr/sbin/rmmod nvmet nvme nvme-core
    sudo -S /usr/sbin/modprobe nvme num_p2p_queues=$NUM_P2P_QUEUES_PER_DEV
    sudo -S /usr/sbin/modprobe nvmet-rdma
fi

sudo -S ${SCRIPTDIR}/config_subsystems.sh stop
sudo -S /usr/sbin/rmmod nvmet-rdma

cd ${MODULEDIR} && git checkout $1
cd ${MODULEDIR} && make -j40 && sudo -S make install -j40

sudo -S ${SCRIPTDIR}/config_subsystems.sh start $2 ${NVME_TARGET_ADDR} 4420 $NUM_P2P_QUEUES_PER_DEV
