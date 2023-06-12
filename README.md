# SReXperts EMEA Rome 2023 Hackathon

## WiFi

```
Connect to SSID : NokiaSReXpertsEMEA2023

Password : Noki@23!
```

## Terminal / SSH Client
### Windows

* [WSL environment](https://learn.microsoft.com/en-us/windows/wsl/install)
* [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)
* [MobaXterm](https://mobaxterm.mobatek.net/download.html)
* [PuTTY Installer](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.78-installer.msi)
* [PuTTY Binary](https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe)


### MacOS


* [iTerm2](https://iterm2.com/downloads/stable/iTerm2-3_4_19.zip)
* [Warp](https://app.warp.dev/get_warp)
* [Hyper](https://hyper.is/)
* [Terminal](https://support.apple.com/en-gb/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac)

### Linux
* [Gnome Console](https://apps.gnome.org/en/app/org.gnome.Console/)
* [Gnome Terminal](https://help.gnome.org/users/gnome-terminal/stable/)

## IDEs
* [VS Code](https://code.visualstudio.com/Download)
* [VS Code Web](https://vscode.dev/)
* [Sublime Text](https://www.sublimetext.com/download)
* [IntelliJ IDEA](https://www.jetbrains.com/idea/download/)
* [Eclipse](https://www.eclipse.org/downloads/)
* [PyCharm](https://www.jetbrains.com/pycharm/download)

Note: VS code is installed on the instance, to access it you can use SSH with X11 forwarding:
```
user@laptop$ cat ~/.ssh/config 
Host *
	StrictHostKeyChecking no
	UserKnownHostsFile /dev/null
	# for SR OS R19
	HostKeyAlgorithms=+ssh-dss

Host hackathon-vm
	Hostname 1.2.3.4
	User hackathon
	ForwardX11 yes
```
Then ```ssh hackathon-vm``` will enable X11 forwarding, and ```code``` starts a VS Code session on your laptop.

## Credentials

### SSH-Config

username: ``` refer to the slide presented ```

password: ``` refer to the slide presented ```

To enable passwordless access to an instance, use ```ssh-keygen -h``` to generate a public/private key pair and then ```ssh-copy-id``` to copy it over.

### Instances

| hostname | group ID |
| --- | --- |
| h1.containerlab.dev | 1 |
| h2.containerlab.dev | 2 |
| ... | ... |
| h**X**.containerlab.dev | X |

### TCP/UDP port schema

Containerlab exposes port mappings per lab, per node using the following mapping logic:

4<span style="color:red">**L**</span><span style="color:blue">**X**</span><span style="color:purple">**NN**</span>

Where <span style="color:red">**L**</span> is a lab ID as per the table below

| L | lab name |
| --- | --- |
| 1 | [SR OS Stateful show](./sros-stateful-show/) |


5<span style="color:red">**L**</span><span style="color:blue">**X**</span><span style="color:purple">**NN**</span>

Where <span style="color:red">**L**</span> is a lab ID as per the table below

| L | lab name |
| --- | --- |
| 0 | [Standard SR OS](./sros-generic-lab/) |
| 1 | [Standard SR Linux](./srl-generic-lab/) |
| 2 | [Secure BGP Peering in IXPs](./ix-rpki-lab/) | 
| 3 | [Ansible](./srl-ansible-lab/) | 
| 4 | [SR OS command customization](./sros-command-customization/) | 
| 5 | [Streaming Telemetry SR Linux](./srl-telemetry-lab/) | 
| 6 | [Certificate Management](./sros-gnoi-cert-mgmt-lab/) | 
| 7 | [SR OS pySROS device correlation](./sros-pysros-device-correlation/) | 
| 8 | [SR OS pySROS enhanced login](./sros-pysros-device-correlation/) | 
| 9 | [SR OS event handler](./sros-event-handling) |

Where <span style="color:blue">**X**</span> is representing a particular service type

| ID | Protocol | 
| --- | --- |
| 0 | SSH |
| 1 | HTTP |
| 2 | HTTPS | 
| 3 | gNMI |
| 4 | Netconf |

Where <span style="color:purple">**NN**</span> is matching the last octet of the management IP address.

For custom created (container)labs, ports 40000 - 60000 are openend on each public IP/VM

## clone this repo
```
git clone git@github.com:nokia/SReXperts.git
```

## Links to the individual labs
* [Standard SR OS](./sros-generic-lab/)
* [Standard SR Linux](./srl-generic-lab/)
* [Secure BGP Peering in IXPs](./ix-rpki-lab/)
* [Streaming Telemetry SR OS](./sros-telemetry-lab/)
* [Streaming Telemetry SR Linux](./srl-telemetry-lab/)
* [Ansible](./srl-ansible-lab/)
* [Config Management with gNMI](./srl-sros-gnmi-config-lab/)
* [Certificate Management](./sros-gnoi-cert-mgmt-lab/)
* [SR OS command customization](./sros-command-customization/)
* [SR OS pySROS device correlation](./sros-pysros-device-correlation/)
* [SR OS pySROS enhanced login](./sros-pysros-device-correlation/)
* [SR OS Python scripts for BNG customization](./sros-bng/README.md)

## Useful links

* [Network Developer Portal](https://network.developer.nokia.com/)
* [containerlab](https://containerlab.dev/)
* [gNMIc](https://gnmic.openconfig.net/)

### SR Linux
* [Learn SR Linux](https://learn.srlinux.dev/)
* [YANG Browser](https://yang.srlinux.dev/)
* [gNxI Browser](https://gnxi.srlinux.dev/)

### SR OS
* [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)
