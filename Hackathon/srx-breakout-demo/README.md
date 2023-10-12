# SReXperts 2023

## Introduction

This demostration creates an SR OS based network topology with the following open source tools included:

* gnmic
* prometheus
* grafana
* openbgpd
* iperf

## Instructions

To deploy the lab issue the following command:

```
make
containerlab deploy
```

The system will create the containers required for the lab automatically.  You will need to wait for the 
SR OS containers to boot.  You can watch them do so using the `docker logs -f` command.  For example:

```
docker logs -f clab-srx-demo-p2
```

Once the SR OS containers have booted you can configure the entire topology using the pySROS application 
provided in `./pysros/demo.py` by issuing the following command:

```
docker exec -ti clab-srx-demo-netmgmt /pysros/demo.py
```

The grafana portal will be available using a webbrowser on port `3000`.

If you would like to deploy a VPN between the PE devices to connect the CE devices over L3VPN over Segment Routing
then issue the following command:

```
docker exec -ti clab-srx-demo-netmgmt /ansible/demo.sh
```

When complete use the following commands to stop and cleanup the demonstration:

```
sudo containerlab destroy --cleanup
make clean
```
