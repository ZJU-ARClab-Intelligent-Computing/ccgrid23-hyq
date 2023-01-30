#!/bin/bash

if [ ! $# -eq 2 ]; then
    echo "usage: $0 <branch> <target_addr> <numdisks>"
    exit -1
fi

SCRIPTDIR=$(dirname $(readlink -f "$0"))
MODULEDIR=${SCRIPTDIR}/drivers/host

if [ ! -f ${SCRIPTDIR}/target_addr ]; then
    echo "Please fill target address in file ${SCRIPTDIR}/target_addr"
    exit -1
fi
NVME_TARGET_ADDRS=($(cat ${SCRIPTDIR}/target_addr | tr "," " "))

if [ ! -d ${MODULEDIR} ]; then
    cd ${HOME} && git clone https://github.com/nickyc975/nvme-host.git
fi

if [ $(/usr/sbin/lsmod | grep nvme_rdma | wc -l) -eq 0 ]; then
    sudo modprobe nvme-rdma
fi

sudo nvme disconnect-all
sudo rmmod qd-rw-based 2>&1 || true
sudo rmmod nvme-rdma

cd ${MODULEDIR} && git checkout $1
cd ${MODULEDIR} && make clean && make && sudo make install

sudo modprobe nvme-rdma

if [ -e "${MODULEDIR}/host/cx5.ko" ]; then
    sudo modprobe cx5
fi

for ((i=0; i<$2; i++)); do
    ADDRIDX=$((i / 4))
    sudo nvme connect -a ${NVME_TARGET_ADDRS[$ADDRIDX]} -s 442$i -t rdma -n testsubsystem$i
    ret=$?
    if [ ! $ret -eq 0 ]; then
        echo "Failed to connect to target!"
        exit $ret
    fi
done

# Disable hyper-thread
echo off | sudo tee /sys/devices/system/cpu/smt/control

# Set CPUs to max performance
for cpu_id in $(cat /sys/devices/system/cpu/online | tr "-" " " | xargs seq); do
    echo performance | sudo tee /sys/devices/system/cpu/cpu$cpu_id/cpufreq/scaling_governor
done
