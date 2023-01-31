#!/bin/bash

function print_usage_exit() {
    echo "usage: $0 start <offload_ratio> <addrs> <base_port> <num_p2p_queues>"
    echo "          stop"
    exit 1
}

case "$1" in
    "stop")
        rm -f /sys/kernel/config/nvmet/ports/*/subsystems/*
        rmdir /sys/kernel/config/nvmet/ports/*
        rmdir /sys/kernel/config/nvmet/subsystems/*/namespaces/*
        rmdir /sys/kernel/config/nvmet/subsystems/*/
        exit 0
    ;;
    "start")
        if [ -z $2 ] || [ -z $3 ] || [ -z $4 ] || [ -z $5 ]; then
            print_usage_exit
        fi
    ;;
    *)
        print_usage_exit
    ;;
esac

OFFLOAD_RATIO=$2
ADDRS=($(echo $3 | tr "," " "))
BASE_PORT=$4
NUM_P2P_QUEUES_PER_DEV=$5

# increasing aio-max-nr to allow large iodepth with many jobs and NAMEs
echo 1048576 > /proc/sys/fs/aio-max-nr

I=0
NVME_DEVS=$(ls /dev/ | grep "nvme[0-9]\+n1")
NR_OFFLOAD_DEVS=$(echo "$(echo $NVME_DEVS | wc -w) * $OFFLOAD_RATIO" | bc | awk '{printf "%d", $0}')
for NVME_DEV in $NVME_DEVS; do
    ADDRIDX=$((I / 4))
    SUBSYS="testsubsystem$I"
    SUBSYS_PORT=$(($BASE_PORT+$I))
    SHOULD_OFFLOAD=$([ $I -lt $NR_OFFLOAD_DEVS ] && echo 1 || echo 0)
    echo "Creating $SUBSYS on $NVME_DEV with port $SUBSYS_PORT, offload: $SHOULD_OFFLOAD"

    mkdir /sys/kernel/config/nvmet/subsystems/${SUBSYS}
    echo 1 > /sys/kernel/config/nvmet/subsystems/${SUBSYS}/attr_allow_any_host
    mkdir /sys/kernel/config/nvmet/subsystems/${SUBSYS}/namespaces/1
    echo -n "/dev/${NVME_DEV}" > /sys/kernel/config/nvmet/subsystems/${SUBSYS}/namespaces/1/device_path
    echo $SHOULD_OFFLOAD > /sys/kernel/config/nvmet/subsystems/${SUBSYS}/attr_offload
    echo 1 > /sys/kernel/config/nvmet/subsystems/${SUBSYS}/namespaces/1/enable

    mkdir /sys/kernel/config/nvmet/ports/$((I+1))
    echo $SUBSYS_PORT > /sys/kernel/config/nvmet/ports/$((I+1))/addr_trsvcid
    echo ${ADDRS[$ADDRIDX]} > /sys/kernel/config/nvmet/ports/$((I+1))/addr_traddr
    echo "rdma" > /sys/kernel/config/nvmet/ports/$((I+1))/addr_trtype
    echo "ipv4" > /sys/kernel/config/nvmet/ports/$((I+1))/addr_adrfam
    echo $NUM_P2P_QUEUES_PER_DEV > /sys/kernel/config/nvmet/ports/$((I+1))/param_offload_queues

    ln -s /sys/kernel/config/nvmet/subsystems/${SUBSYS}/ /sys/kernel/config/nvmet/ports/$((I+1))/subsystems/${SUBSYS}

    I=$((I+1))
done

exit
