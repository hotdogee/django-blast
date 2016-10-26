#!/bin/bash 
#
#  Copy Ansible files to a dir.
#
if [[ -d $1 ]] ; then  
    cp setup.py setup.yml vm.yml vagrantfix.sh pg_hba.conf dotcp.sh $1
fi
