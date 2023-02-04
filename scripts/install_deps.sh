#!/bin/bash

# Install kernel-5.8.15-301.fc33.x86_64 and the corresponding development files.
mkdir .tmp_pkgs && cd .tmp_pkgs

wget https://kojipkgs.fedoraproject.org/packages/kernel/5.8.15/301.fc33/x86_64/kernel-5.8.15-301.fc33.x86_64.rpm
wget https://kojipkgs.fedoraproject.org/packages/kernel/5.8.15/301.fc33/x86_64/kernel-core-5.8.15-301.fc33.x86_64.rpm
wget https://kojipkgs.fedoraproject.org/packages/kernel/5.8.15/301.fc33/x86_64/kernel-devel-5.8.15-301.fc33.x86_64.rpm
wget https://kojipkgs.fedoraproject.org/packages/kernel/5.8.15/301.fc33/x86_64/kernel-modules-5.8.15-301.fc33.x86_64.rpm

sudo yum install -y kernel-5.8.15-301.fc33.x86_64.rpm --allowerasing

cd ../ && rm -rf .tmp_pkgs

# Generate a certificate for signing modules.
openssl req -new -nodes -utf8 -sha512 -days 36500 -batch -x509 -config x509.genkey.fedora -outform DER -out signing_key.x509 -keyout signing_key.pem
mv signing_key.x509 /lib/modules/5.8.15-301.fc33.x86_64/build/certs/
mv signing_key.pem /lib/modules/5.8.15-301.fc33.x86_64/build/certs/

# Change the default kernel to 5.8.15-301.fc33.x86_64.
sudo grubby --set-default=/boot/vmlinuz-5.8.15-301.fc33.x86_64

# Install build tools.
sudo yum install -y vim git make gcc g++

# Install RockdDB build dependencies.
sudo yum install -y zstd libzstd libzstd-devel
sudo yum install -y gflags gflags-devel

# Install nvme-cli tool.
sudo yum install -y nvme-cli

# Use tuna to tune target irqs.
sudo yum install -y tuna

# Install fio.
sudo yum install -y fio

# Install python tools.
sudo yum install -y python3 python3-pip
pip3 install matplotlib numpy

# Install fonts for figures.
sudo yum install -y rpm-build cabextract ttmkfdir fontconfig
wget http://corefonts.sourceforge.net/msttcorefonts-2.5-1.spec
rpmbuild -bb msttcorefonts-2.5-1.spec
sudo rpm -ivh $HOME/rpmbuild/RPMS/noarch/msttcorefonts-2.5-1.noarch.rpm
rm -f msttcorefonts-2.5-1.spec
sudo fc-cache -f -v

# Turn off the firewall.
sudo systemctl stop firewalld
sudo systemctl disable firewalld
