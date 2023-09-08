# Welcome at the hackathon @ SReXperts!

This README is your starting point into the hackathon, it should get you familiar with the lab environment provided by Nokia, and provide an overview of the suggested sample labs.

During the afternoon you will work in groups (or alone if you prefer) on any project that you are inspired to tackle or on one of the pre-provided projects of varying difficulty.

As long as you have a laptop with the ability to SSH we have example projects and lab topologies to help you progress if you don’t have something specific already in mind.   

Need help, not a problem, pop your hand in the air and an eager expert will be there to guide you. 

## Lab Environment
If everything went according to plan, you should have received a physical piece of paper which contains:
- a group ID allocated to your group (or to yourself if you're working alone)
- SSH credentials to a public cloud instance dedicated to your group. 
- HTTP URL's towards this repo and access to a web based IDE in case you don't have one installed on your operating system.

> <p style="color:red">!!! Make sure to backup any code, config, ... <u> offline (e.g your laptop)</u>. 
> The public cloud instances will be destroyed once the hackathon is concluded.</p>

### Group ID

Please refer to the paper provided by the hackathon session leader. If nothing has been provided, not a problem, pop your hand in the air and an eager expert will be there to allocate one for you. 

| Group ID | hostname instance |
| --- | --- |
| 1 | 1.srexperts.net |
| 2 | 2.srexperts.net |
| ... | ... |
| **X** | **X**.srexperts.net |

### SSH

hostname: `refer to the paper provided `

username: `refer to the paper provided or the slide presented`

password: `refer to the paper provided or the slide presented`

To enable passwordless access to an instance, use `ssh-keygen -h` to generate a public/private key pair and then `ssh-copy-id` to copy it over.

### WiFi

Details provided in the session.

### Overview of pre-provided projects
During this hackathon you can work on any problem/project you are inspired to tackle or on one of the pre-provided projects of varying difficulty.
Below you can find a table with links towards those pre-provided project which you can use as a baseline for the problem/project you might want to tackle or perform the tasks we've set up for you.

If you have your own project in mind then we would suggest to use either the [Standard SR OS lab](./sros-generic-lab/) or the [Standard SR Linux lab](./srl-generic-lab/).

Each pre-provided project comes with a README of it's own, please click the pre-provided projects for more information.

| Link to pre-provided project | Difficulty |
| --- | --- |
| [Standard SR OS](./sros-generic-lab/) | # |
| [Standard SR Linux](./srl-generic-lab/) | # |
| [Secure BGP Peering in IXPs](./ix-rpki-lab/) | #### |
| [SR Linux Streaming Telemetry](./srl-telemetry-lab/) | ## |
| [SR Linux JSON-RPC with Ansible](./srl-ansible-lab/) | ## |
| [Config Management with gNMI](./srl-sros-gnmi-config-lab/) | ### |
| [Certificate Management](./sros-gnoi-cert-mgmt-lab/) | ###  |
| [SR OS command customization](./sros-command-customization/) | # |
| [SR OS pySROS device correlation](./sros-pysros-device-correlation/) | ## |
| [SR OS pySROS enhanced login](./sros-pysros-enhanced-login-banner/) | # |
| [SR OS Python scripts for BNG customization](./sros-bng/) | ### |
| [SR OS pySROS stateful show commands](./sros-stateful-show/) | # |
| [SR OS event handling](./sros-event-handling/) | #### |

### Deploying a project
When accessing your hackathon VM instance you'll see the following bootstrapped environment.
the SReXperts directory is a git clone of this repository.

``` 
~$ ls
SReXperts  go

~$ cd SReXperts/

~/SReXperts$ cd Hackathon/

~/SReXperts/Hackathon$ ls -1
README.md
ix-rpki-lab
pysros_primer
srl-ansible-lab
srl-generic-lab
srl-sros-gnmi-config-lab
srl-telemetry-lab
sros-bng
sros-command-customization
sros-event-handling
sros-generic-lab
sros-gnoi-cert-mgmt-lab
sros-pysros-device-correlation
sros-pysros-enhanced-login-banner
sros-stateful-show

~/SReXperts/Hackathon$
```

For explanatory purposes, suppose we want to deploy the sros-generic-lab:

Change directories
```
cd $HOME/SReXperts/Hackathon/sros-generic-lab
```
Execute the `containerlab deploy` command
```
sudo containerlab deploy --reconfigure
```

> As CPU cores and memory are a finite resource, please destroy the deployed labs once your objective has been concluded by executing the `containerlab destroy` command.
```
sudo containerlab destroy --cleanup
```

### Credentials & Access
#### Accessing the lab from within the VM
To access the lab nodes from within the VM, users should identify the names of the deployed nodes using the `sudo containerlab inspect` command:

```
sudo containerlab inspect
INFO[0000] Parsing & checking topology file: sros-generic-lab.clab.yml
+----+--------------------------------+--------------+------------------------------------+---------+---------+-----------------+-----------------------+
| #  |              Name              | Container ID |               Image                |  Kind   |  State  |  IPv4 Address   |     IPv6 Address      |
+----+--------------------------------+--------------+------------------------------------+---------+---------+-----------------+-----------------------+
|  1 | clab-sros-srx2023-ce1          | 6897dc97fcd4 | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.5/24  | 2001:172:20:20::5/64  |
|  2 | clab-sros-srx2023-ce2          | 413d88e63176 | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.16/24 | 2001:172:20:20::10/64 |
|  3 | clab-sros-srx2023-ce3          | c21eb08d85dc | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.4/24  | 2001:172:20:20::4/64  |
|  4 | clab-sros-srx2023-ce4          | 7e9e6c61403f | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.9/24  | 2001:172:20:20::9/64  |
|  5 | clab-sros-srx2023-consul-agent | 75e5ac0d733a | consul:1.15                        | linux   | running | 172.20.20.8/24  | 2001:172:20:20::8/64  |
|  6 | clab-sros-srx2023-gnmic        | 1bee5f2032e6 | ghcr.io/openconfig/gnmic           | linux   | running | 172.20.20.12/24 | 2001:172:20:20::c/64  |
|  7 | clab-sros-srx2023-grafana      | 51e63ca2aad7 | grafana/grafana:latest             | linux   | running | 172.20.20.14/24 | 2001:172:20:20::e/64  |
|  8 | clab-sros-srx2023-pe1          | 69903c0afb93 | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.6/24  | 2001:172:20:20::6/64  |
|  9 | clab-sros-srx2023-pe2          | 6a9878a43e6b | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.15/24 | 2001:172:20:20::f/64  |
| 10 | clab-sros-srx2023-pe3          | 46b0b66e2267 | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.10/24 | 2001:172:20:20::a/64  |
| 11 | clab-sros-srx2023-pe4          | 576306a09a26 | vr-sros:23.7.R1                    | vr-sros | running | 172.20.20.7/24  | 2001:172:20:20::7/64  |
| 12 | clab-sros-srx2023-prometheus   | f3d43e60670b | prom/prometheus:latest             | linux   | running | 172.20.20.11/24 | 2001:172:20:20::b/64  |
| 13 | clab-sros-srx2023-rs1          | c411b6a25593 | ghcr.io/srl-labs/network-multitool | linux   | running | 172.20.20.3/24  | 2001:172:20:20::3/64  |
| 14 | clab-sros-srx2023-tg1          | e91466614108 | ghcr.io/srl-labs/network-multitool | linux   | running | 172.20.20.2/24  | 2001:172:20:20::2/64  |
| 15 | clab-sros-srx2023-tg2          | c73b6adbada9 | ghcr.io/srl-labs/network-multitool | linux   | running | 172.20.20.13/24 | 2001:172:20:20::d/64  |
+----+--------------------------------+--------------+------------------------------------+---------+---------+-----------------+-----------------------+
```
Using the names from the above output, we can login to the a node using the following command:

For example to access node `clab-sros-srx2023-pe1` via ssh simply type:
```
ssh admin@clab-sros-srx2023-pe1
```

#### Accessing the lab via Internet

Each public cloud instance has a port-range (50000 - 51000) exposed towards the Internet, as lab nodes spin up, a public port is dynamically allocated by the docker daemon on the public cloud instance.
You can utilize those to access the lab services straight from your laptop via the Internet.

With the `show-ports` command executed on a VM you get a list of mappings between external and internal ports allocated for each node of a lab:

```
~$ show-ports
Name                            Forwarded Ports
clab-sros-srx2023-ce1           50095 -> 22, 50094 -> 830, 50093 -> 57400
clab-sros-srx2023-ce2           50088 -> 22, 50087 -> 830, 50086 -> 57400
clab-sros-srx2023-ce3           50098 -> 22, 50097 -> 830, 50096 -> 57400
clab-sros-srx2023-ce4           50091 -> 22, 50090 -> 830, 50089 -> 57400
clab-sros-srx2023-consul-agent  50092 -> 8500, 50003 -> 8600
clab-sros-srx2023-grafana       50082 -> 3000
clab-sros-srx2023-pe1           50085 -> 22, 50084 -> 830, 50083 -> 57400
clab-sros-srx2023-pe2           50107 -> 22, 50106 -> 830, 50105 -> 57400
clab-sros-srx2023-pe3           50101 -> 22, 50100 -> 830, 50099 -> 57400
clab-sros-srx2023-pe4           50104 -> 22, 50103 -> 830, 50102 -> 57400
clab-sros-srx2023-prometheus    50081 -> 9090
```

Each service exposed on a lab node gets a unique external port number as per the table above. 
In the given case, Grafana's web interface is available on port 50082 of the VM which is mapped to Grafana's node internal port of 3000.

The following table shows common container internal ports and is meant to help you find the correct exposed port for the services.

| Service    | Internal Port number |
| ---------- | -------------------- |
| SSH        | 22                   |
| Netconf    | 830                  |
| gNMI       | 57400                |
| HTTP/HTTPS | 80/443               |
| Grafana    | 3000                 |

Subsequently you can access the lab node on the external port for your given instance using the DNS name of the assigned VM.

| Group ID | hostname instance |
| --- | --- |
| **X** | **X**.srexperts.net |

In the example above, accessing PE1 would be possible by: 
```
ssh admin@X.srexperts.net -p 50085
```

In the example above, accessing grafana would be possible browsing towards **http://X.srexperts.net:50082** (where X is the group ID you've been allocated)

Optional:
> You can generate `ssh-config` using the `generate-ssh-config` command and store the output on your local laptop's SSH client, in order to connect directly to nodes.

## clone this repo
If you would like to work locally on your personal device you should clone this repository. This can be done using one of the following commands.

> HTTPS
```
git clone https://github.com/nokia/SReXperts.git
```
> SSH
```
git clone git@github.com:nokia/SReXperts.git
```
> GH CLI
```
gh repo clone nokia/SReXperts
```
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

### Misc Tools/Software
#### Windows

* [WSL environment](https://learn.microsoft.com/en-us/windows/wsl/install)
* [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)
* [MobaXterm](https://mobaxterm.mobatek.net/download.html)
* [PuTTY Installer](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.78-installer.msi)
* [PuTTY Binary](https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe)


#### MacOS

* [iTerm2](https://iterm2.com/downloads/stable/iTerm2-3_4_19.zip)
* [Warp](https://app.warp.dev/get_warp)
* [Hyper](https://hyper.is/)
* [Terminal](https://support.apple.com/en-gb/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac)

#### Linux

* [Gnome Console](https://apps.gnome.org/en/app/org.gnome.Console/)
* [Gnome Terminal](https://help.gnome.org/users/gnome-terminal/stable/)

#### IDEs

* [VS Code](https://code.visualstudio.com/Download)
* [VS Code Web](https://vscode.dev/)
* [Sublime Text](https://www.sublimetext.com/download)
* [IntelliJ IDEA](https://www.jetbrains.com/idea/download/)
* [Eclipse](https://www.eclipse.org/downloads/)
* [PyCharm](https://www.jetbrains.com/pycharm/download)



