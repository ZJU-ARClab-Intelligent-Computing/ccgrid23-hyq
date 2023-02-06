#!/bin/bash

# Target ip address for nvmf connection. 
TARGET_NVMF_ADDR=127.0.0.1

# Target ip address for ssh connection.
# It is recommanded to use a separate network interface for ssh connection,
# or ssh data transmissions may impact NVMe-oF storage performance.
TARGET_SSH_ADDR=127.0.0.1

# Artifact scripts' path on the target server.
# The evaluation scripts will leverage this by:
#   ssh root@${TARGET_SSH_ADDR} ${TARGET_SCRIPTS_ROOT}/scripts/target/xxx.sh
TARGET_SCRIPTS_ROOT=/path/to/ccgrid23-hyq

# Target Smart-NIC name.
# The evaluation scripts will tune the interrupt distribution of this device.
TARGET_SNIC_NAME=enp134s0f0

# NVMe-oF devices on the host server for evaluation.
#
# !!! ATTENTION: DO NOT STORE ANY DATA ON THESE DEVICES, !!!
# !!! OR YOU WILL LOSE THE DATA !!!
#
# These are the device entries created by the "nvme connect" command.
# Typically, if there isn't any NVMe or NVMe-oF devices on the host server
# originally, this should be DEVICES="/dev/nvme0n1 /dev/nvme1n1".
DEVICES=""
