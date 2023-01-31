#!/bin/bash

if [ ! $# -eq 3 ]; then
    echo "usage: $0 <branch> <addr> <offload>"
    exit -1
fi

NUM_P2P_QUEUES_PER_DEV=32
SCRIPTDIR=$(dirname $(readlink -f "$0"))
MODULEDIR=${SCRIPTDIR}/../../drivers/target

if [ ! -e "${MODULEDIR}/configure.mk.kernel" ]; then
    cd ${MODULEDIR} && \
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
                -j40 && \
    make -j40 && \
    sudo make install -j40
fi

if [ $(/usr/sbin/lsmod | grep -w nvmet_rdma | wc -l) -eq 0 ]; then
    sudo /usr/sbin/rmmod nvmet nvme nvme-core
    sudo /usr/sbin/modprobe nvme num_p2p_queues=$NUM_P2P_QUEUES_PER_DEV
    sudo /usr/sbin/modprobe nvmet-rdma
fi

sudo ${SCRIPTDIR}/config_subsystems.sh stop
sudo /usr/sbin/rmmod nvmet-rdma

cd ${MODULEDIR} && git checkout $1
cd ${MODULEDIR} && make -j40 && sudo make install -j40

sudo /usr/sbin/modprobe nvmet-rdma

sudo ${SCRIPTDIR}/config_subsystems.sh start $3 $2 4420 $NUM_P2P_QUEUES_PER_DEV
