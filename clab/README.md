# How to run this lab on your own environment?

## Node licenses

Node licenses are assumed to be placed in the following paths:  

* `/opt/srexperts/sros.license` (SR-SIM license, required for SR-OS nodes)  
* `/opt/srexperts/srl.license` (SR Linux license, required for node types that do not belong to the 7220 IXR family)

## Linux bridges

Some topology links are implemented using linux bridges. You must create them before you try to deploy the topology.
```bash
sudo ip link add pe1-p1 type bridge group_fwd_mask 0xFFF8
sudo ip link add pe2-p1 type bridge group_fwd_mask 0xFFF8
sudo ip link add pe1-p2 type bridge group_fwd_mask 0xFFF8
sudo ip link add pe2-p2 type bridge group_fwd_mask 0xFFF8
sudo ip link set pe1-p2 up
sudo ip link set pe2-p2 up
sudo ip link set pe1-p1 up
sudo ip link set pe2-p1 up
```

## Bonding kernel module
Client nodes require the bonding kernel module to be loaded in order to support bond interfaces. If your linux host doesn't have it loaded yet, you can load it using:

```bash
sudo modprobe bonding mmiimon=100 mode=802.3ad lacp_rate=fast
```

## Environment variables

This is a templated lab and relies on a number of environment variables to be exposed in your shell.

Assuming bash/zsh, export/append these variables to your rc files.

```bash
# any number between 1-99
export INSTANCE_ID=99
export CNSP_INSTANCE_ID=$(printf '%04d' ${INSTANCE_ID})
# Password you want to set when accessing the nodes in the topology
export EVENT_PASSWORD=iWantToRunThisLabOnMyOwn

# specifically to run the codeserver image, which is part of the topology
export NOKIA_UID=$(id -u)
export NOKIA_GID=$(getent group docker | cut -d: -f3)
```

Then check the env vars:

```bash
echo "INSTANCE_ID: $INSTANCE_ID"
echo "EVENT_PASSWORD: $EVENT_PASSWORD"
echo "NOKIA_UID: $NOKIA_UID"
echo "NOKIA_GID: $NOKIA_GID"
```

## Run

Once linux bridges and environment variables are created, you can run this lab by executing:   

``` bash
#Clab deploy (assuming this repo has been checked out in $HOME/SReXperts) 
sudo -E clab deploy -t $HOME/SReXperts/clab/srx.clab.yml --reconfigure
```
```bash
#Set Link Impairments for some linux bridge slave interfaces
sudo tc qdisc replace dev p1-1-1-c1-1 root netem delay 5ms
sudo tc qdisc replace dev pe1-1-1-c1-1 root netem delay 5ms
sudo tc qdisc replace dev p1-1-1-c2-1 root netem delay 5ms
sudo tc qdisc replace dev pe2-1-1-c1-1 root netem delay 5ms
sudo tc qdisc replace dev p2-1-1-c1-1 root netem delay 5ms
sudo tc qdisc replace dev pe1-1-1-c2-1 root netem delay 5ms
sudo tc qdisc replace dev p2-1-1-c2-1 root netem delay 5ms
sudo tc qdisc replace dev pe2-1-1-c2-1 root netem delay 5ms
```

