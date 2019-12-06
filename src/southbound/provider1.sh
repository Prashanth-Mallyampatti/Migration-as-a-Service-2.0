##############################################
# Script to create mainBR, a connectivity to 
# hypervisor and provider ns pns
##############################################

#!/bin/bash

#virsh net-undefine testBR
#virsh net-destroy testBR
#ip netns del pns

# Create mainBR network and bridge
sudo cp /root/networks/testBR1.xml /etc/libvirt/qemu/networks/
cd /etc/libvirt/qemu/networks
sudo virsh net-define testBR1.xml
sudo virsh net-start testBR1
sudo virsh net-autostart testBR1

# Create pns
sudo ip netns add pns1

# Create veth pair
sudo ip link add p11 type veth peer name br1
ip link set dev br1 up
brctl addif testBR1 br1

# Attach veth pair to pns
ip link set p11 netns pns1
ip netns exec pns1 ip link set dev p11 up

echo "DHCLIENT"
ip netns exec pns1 dhclient p11

echo "link up"
ip link set dev testBR1 up

echo "Rules"
# Rules to take care
rule_num_1=`sudo iptables -t filter -L FORWARD -nv --line-numbers | grep testBR | grep REJECT | awk -c '{print $1}' | awk 'NR==1'`
rule_num_2=`sudo iptables -t filter -L FORWARD -nv --line-numbers | grep testBR | grep REJECT | awk -c '{print $1}' | awk 'NR==2'`
#echo "$rule_num_1"
#echo "$rule_num_2"

sudo iptables -t filter -D FORWARD $rule_num_1
sudo iptables -t filter -D FORWARD $rule_num_1

sudo iptables -P FORWARD ACCEPT
