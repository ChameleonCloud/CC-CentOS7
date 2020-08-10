#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root."
  exit 1
fi

### OS-specific installs
function centos_reqs() {
  DNF='dnf'
  if [[ $VERSION_ID = '8' ]]; then
    dnf install -y python3-pip
  else
    yum install -y python-pip
    DNF='yum'
  fi
  $DNF install -y epel-release
  $DNF install -y qemu-img kpartx
}

function ubuntu_reqs() {
  apt-get -qq install -y qemu-utils python-pip kpartx
}

source /etc/os-release
if [[ $ID = 'ubuntu' ]]; then
  ubuntu_reqs
else
  if [[ $ID = 'centos' ]]; then
    centos_reqs
  else
    echo 'Unknown distribution (not CentOS or Ubuntu?), aborting.'
    exit 1
  fi
fi

### Generic installs

# pip install --upgrade pip
# this is a bit dirty, you should probably use a virtualenv
pip install networkx==2.2
pip install diskimage-builder
