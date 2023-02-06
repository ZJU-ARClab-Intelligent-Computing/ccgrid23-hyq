# Artifacts of HyQ

This repository provides the artifacts for reproducing the experiment results in paper __HyQ: Hybrid I/O Queue Architecture for NVMe over Fabrics to Enable High-Performance Hardware Offloading__.

## Overview

The repository consists of three components: the implementation of HyQ, the scripts for building, installing, and configuring HyQ, and the scripts and configurations for reproducing the results in the main paper.

### HyQ Implementation

Folder `drivers/` contains the implementation of HyQ.

* `drivers/host` includes the host side NVMe-oF drivers. The `main` branch of  `drivers/host` keeps the original drivers from Linux kernel 5.8.15. And the `hyq` branch of `drivers/host` implements HyQ based on the Linux drivers.

* `drivers/target` includes drivers from MLNX_OFED package. These drivers are essential for leveraging ConnectX SmartNICs' NVMe-oF target offloading feature. The `main` branch of `drivers/target` keeps the original drivers, and the `hyq` branch of `driver/target` keeps our slightly modified version for cooperating with HyQ.

Please refer to the corresponding repositories and commits for details.

### Building, Installing, and Configuring Scripts

Folder `scripts` contains scripts for building, installing, and Configuring HyQ.

* `scripts/install_deps.sh` installs the required dependencies for building and running HyQ, along with extra dependencies for running the evaluation.

* `scripts/config_cpu.sh` tunes server CPUs for the following evaluations. It is called by the setup scripts of host and target.

* `scripts/host/setup.sh` builds and installs HyQ on the host server, then tries to connect to NVMe-oF services provided by the target server.

* `scripts/host/use_sched.sh` sets the HyQ schedulers of all capable NVMe-oF devices to the given one. For example, `scripts/host/use_sched.sh none` sets the schedulers of the devices to `none`, i.e., not using any scheduler.

* `scripts/target/setup.sh` builds and installs the MLNX_OFED drivers on the target server, then tries to start NVMe-oF services.

* `scripts/target/config_subsystem.sh` is used by `scripts/target/setup.sh` to start NVMe-oF services.

* `scripts/target/limit_cpu.sh` and `scripts/target/set_irq_affinity.sh` are only used for evaluation. The former controls the number of online CPU cores of the target server. The latter updates the interrupt affinity of the given device.

### Evaluation Scripts

Folder `evaluation` contains scripts for reproducing the experiment results in the main paper. There are many scripts in the folder, but only three of them need your attention.

* `evaluation/config.sh` keeps the meta information that needs to be manually filled. Read the comments in the file for details.

* `evaluation/fio/run_tests.sh` is the entry of all fio related experiments. Executing the script generates Fig. 3-5 and Fig. 9-15 of the main paper.

* `evaluation/rocksdb/run_tests.sh` is the entry of all RocksDB experiments. Executing the script generates Fig. 16 and 17 of the main paper.

## Hardware and Software Configurations

### Hardware Configuration

Essential requirements:

* Server with at least 16 CPU cores, 16 GB memory, and 64 GB disk space * 2
* 2-TB Intel P4510 SSD * 2
* Mellanox ConnectX-5 100 Gbps Smart NIC * 1
* Arbitrary 100 Gbps RDMA NIC * 1

The arbitrary 100 Gbps RDMA NIC should be installed on the host server. The SSDs and the ConnectX-5 SmartNIC should be installed on the target server. The two 100 Gbps NICs should be connected with 100-Gbps capable cables.

### Software Configuration

Essential requirements:

* Fedora OS 33 on both host and target servers
* Connectivity with static IP address between the two 100 Gbps NICs
* Public-key-based SSH authentication from host server to target server

Follow the steps to initialize the software environments, __all operations should be performed on both host and target servers__:

* Clone the repository: `git clone https://github.com/ZJU-ARClab-Intelligent-Computing/ccgrid23-hyq.git`

* Update submodules: `cd /path/to/ccgrid23-hyq && git submodule update --init --recursive`

* Install dependencies: `cd /path/to/ccgrid23-hyq/scripts && ./install_deps.sh`

* Reboot the servers: `reboot`

* Edit `/path/to/ccgrid23-hyq/evaluation/config.sh` to fill in the required information

## Evaluate the Artifacts

__All of the following operations should only be performed on the host server.__

### Fio Experiments

* `cd /path/to/ccgrid23-hyq/evaluation/fio`
* `./gen_fio_jobs.sh`
* `./run_tests.sh` (need about 16 hours to finish)
* Figures can be found in `./plot/figures`

### RocksDB Experiments

* `cd /path/to/ccgrid23-hyq/evaluation/rocksdb`
* `./run_tests.sh` (need about 2 hours to finish)
* Figures can be found in `./plot/figures`

## Citation

Please cite our paper in your publications if the artifacts help your research.

```bibtex
@inproceedings{ccgrid2023hyq,
  author    = {Chen, Yiquan and Chen, Jinlong and Wang, Yijing and Chen, Yi and Jin, Zhen and Xu, Jiexiong and Fang, Guoju and Lin, Wenhai and Wei, Chengkun and Chen, Wenzhi},
  booktitle = {The 23rd International Symposium on Cluster, Cloud and Internet Computing},
  title     = {HyQ: Hybrid I/O Queue Architecture for NVMe over Fabrics to Enable High-Performance Hardware Offloading},
  year      = {2023},
  pages     = {},
  doi       = {}
}
```
