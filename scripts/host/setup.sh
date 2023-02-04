#!/bin/bash

if [ ! $# -eq 3 ]; then
    echo "usage: $0 <branch> <target_addr> <numdisks>"
    exit -1
fi

SCRIPTDIR=$(dirname $(readlink -f "$0"))
MODULEDIR=${SCRIPTDIR}/../../drivers/host

$SCRIPTDIR/../config_cpu.sh

sudo rmmod basic 2>&1 || true
sudo rmmod qd-rw-based 2>&1 || true
sudo rmmod nvme-rdma 2>&1 || true

cd ${MODULEDIR} && git checkout $1
cd ${MODULEDIR} && make clean && make && sudo make install

sudo modprobe nvme-rdma
sudo modprobe qd-rw-based 2>&1 || true
sudo modprobe basic 2>&1 || true

for ((i=0; i<$3; i++)); do
    sudo nvme connect -a $2 -s 442$i -t rdma -n testsubsystem$i
    ret=$?
    if [ ! $ret -eq 0 ]; then
        echo "Failed to connect to target!"
        exit $ret
    fi
done
