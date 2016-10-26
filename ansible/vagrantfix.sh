#!/bin/bash
#
#  Script to add a public network and an VM's name to a basic Vagrant file.
#  and our public key the VM's authorized_keys file.
#

if [[ -z $1 ]] ||  [[ -z $2 ]] ; then 
    echo 'Name argument and ip-addr argument required !!! '
    exit 1
fi

if [[ $2 = "default" ]] ; then
    addr=$(awk '$0 ~ /^  # config.vm.network "private_network", ip:/ { gsub(/"/,"", $5); print $5 }' Vagrantfile)
else
    addr=$2
fi

if [[ -z $addr ]] ; then
    echo "Can't get IP address from either command argument or Vagrant file"
    exit 1
fi

sudo arp -d $addr

sed '/^  # config.vm.network "private_network", ip:/d' Vagrantfile > Vagrantfile.tmp 
awk '$0 ~ /^end$/ { 
        print "  config.vm.network \"private_network\", ip: \"'$addr'\""
        print "  config.vm.provider :virtualbox do |vb|\n    vb.name = \"'$1'\"\n  end" 
        print "  ssh_pub_key = File.readlines(\"#{Dir.home}/.ssh/id_rsa.pub\").first.strip"
        print "  config.vm.provision '"'"'shell'"'"', inline: \"echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys\", privileged: false"
    }
    { print }
' Vagrantfile > Vagrantfile.tmp
mv Vagrantfile.tmp Vagrantfile
