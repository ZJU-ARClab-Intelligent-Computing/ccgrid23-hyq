#!/bin/bash

# Target ip address for ssh connection.
TARGET_SSH_ADDR=127.0.0.1

# Target ip address for nvmf connection.
TARGET_NVMF_ADDR=127.0.0.1

# Target scripts path.
TARGET_SCRIPTS_ROOT=/path/to/ccgrid23-hyq

# Target Smart-NIC name.
TARGET_SNIC_NAME=enp134s0f0

# NVMe-oF devices for evaluation
DEVICES="/dev/nvme1n1 /dev/nvme2n1"
