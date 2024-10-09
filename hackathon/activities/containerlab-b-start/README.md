# Deploying a Lab with ContainerLab

| Item | Details |
| --- | --- |
| Short Description | Deploy Containerlab with a SR Linux and a SR OS node |
| Skill Level | Beginner |
| Tools Used | Containerlab, Docker, vrnetlab, SR Linux, SR OS |

Containerlab provides a CLI for orchestrating and managing container-based networking labs. It starts  containers and builds virtual wiring between them to create lab topologies of the users choice and subsequently manages the labs lifecycle.

To learn about all the features of Containerlab, visit [containerlab.dev](https://containerlab.dev/).

If you prefer to listen, check out the [Youtube video](https://www.youtube.com/watch?v=xdi7rwdJgkg).

## SReXperts Hackathon

In this activity, you will use Containerlab to deploy a 2-node topology with both SR Linux and SR OS devices.

```
	SR Linux (port ethernet-1/1) <-------------------------------> SR OS (port 1/1/c1/1)
```

## Device Images for Containerlab use

As the name suggests, Containerlab runs the network devices as containers. For simplicity, let's imagine a container as a mini-virtual machine without an operating system (OS) layer and with only the application component.

In order to manage containers, we need management software. The most common software for managing containers is Docker.  Docker allows you build a container image and deploy it.

The software image for a container should be imported into the Docker image store in order for Docker to deploy it. This will be done in the subsequent steps.

### SR Linux Image

Nokia provides a free downloadable docker image with each release of SR Linux.  This can be directly pulled from the docker instance in your environment using:

```
sudo docker pull ghcr.io/nokia/srlinux
```

This command pulls the latest SR Linux docker image into your environment.  To pull a specific release, add `:<relese version>` after the image name, e.g. `ghcr.io/nokia/srlinux:24.7.1`.

```
docker pull ghcr.io/nokia/srlinux:24.3.3
```

Use the below command to verify the list of local docker images.

```
sudo docker image list
```
```
REPOSITORY                                 TAG         IMAGE ID       CREATED              SIZE
ghcr.io/nokia/srlinux                      latest     0fe55808e0bb   2 months ago         2.72GB
```

To see a list of all available SR Linux docker image versions, visit [Nokia GitHub repo](https://github.com/nokia/srlinux-container-image/pkgs/container/srlinux).

### SR OS Image

Nokia publishes a virtual simulator (vSIM) image (in qcow2 format) for very SR OS release. A Nokia account is required to download this image.

A valid license is required to deploy an SR OS node in Containerlab.  Please contact your Nokia Account team representative to obtain your license. For this hackathon activity, a license is already provided in your environment.

As mentioned above, we need a docker image for our Containerlab environment. We will look at the steps required to build a docker image from a SR OS vSIM image.

A vSIM qcow2 image for SR OS release 24.3.3 is present in your environemnt under the `/opt/srexperts/images` directory.

```
ls -lrt /opt/srexperts/images
```
```
total 464644
-rw-r--r-- 1 root root 475791360 Oct  8 08:12 sros-vsim.qcow2
```

We will use a software called [vrnetlab](https://github.com/hellt/vrnetlab/) to create a docker image from a vSIM image.

Let's go over the steps:

1. Clone the vrnetlab repo to your environment.

```
git clone https://github.com/hellt/vrnetlab.git
```

2. Copy the SR OS vSIM qcow2 (as root) to `vrnetlab/sros` directory and rename the file to include the release number. The release number will be used as a tag inside docker in order to differentiate between releases.

```
sudo cp /opt/srexperts/images/sros-vsim.qcow2 $HOME/vrnetlab/sros/sros-vm-24.3.R3.qcow2
```

3. Run `sudo make docker-image` (as root) from inside the `vrnetlab/sros` directory.

```
cd $HOME/vrnetlab/sros
sudo make docker-image 
```

At the end of the process, the docker image that is built by vrnetlab will be available in the `docker image list` output.

```
sudo docker image list
```
```
REPOSITORY                                 TAG         IMAGE ID       CREATED              SIZE
...
vrnetlab/nokia_vsr                         24.3.R3     1b8042dbbb41   11 seconds ago       767MB
...
```

Our SR OS docker image is now ready for use.

## Topology File

In Containerlab, a lab network is defined using a simple topology file written in YAML.

There are pre-defined keywords to be used to define the different components of the lab.  For more details and options, visit [Containerlab](https://containerlab.dev/manual/topo-def-file/).  Here are some of the common attributes that we will use for our lab:

- name: defines a name for the lab. If multiple labs are deployed in the same environment, each lab should be given a unique name. When deploying a lab, Containerlab creates a directory using the given name to store the lab configuration files.

- topology: contains the lab topology information.

- nodes: contains the information of nodes and node types. Each node in the lab can be defined using a node name.

- kind: defines the type of image. For examples - `nokia_srlinux`, `nokia_sros`, `ceos`, etc.

- image: defines the location of the docker image. This can be obtained from the output of `sudo docker image list`. The format is `repository:tag`. For example: `ghcr.io/nokia/srlinux:latest`. If no tag is specified, the image with the `latest` is used. If the image is not available in the local docker image repo in your environment, Containerlab will pull the image from the remote repo location. For SR OS, we will use the docker image we built in the previous step.

- links: provides the definition of the network connectivity link information

- endpoints: defines a point-to-point link between 2 nodes. The format is `nodename:interface`. SR Linux interface naming convention is: `ethernet-1/Y`, where `1` is the only available line card and `Y` is the port on the line card. For port `1/1` on SR Linux, it will be `e1-1`. SR OS interface naming convention is: `ethX`, where `X` is the port number.

- startup-config: defines configuration that should be loaded on node startup. The file can be local or remote.

- type: defines the chassis model we want to emulate. SR Linux default is 7220 IXR-D2L.

- license: SR OS nodes require a license from Nokia. Give the license file path here.

Let's create our lab topology using the above keywords.

```yaml
name: srx24

topology:
  nodes:
    srl:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux
    sros:
      kind: nokia_sros
      image: vrnetlab/vr-sros:24.3.R3
      type: sr-1
      license: /opt/srexperts/license-sros24.txt

  links:
    - endpoints: ["srl:e1-1", "sros:eth1"]
```

Save the above topology to a file called `lab.clab.yml`.

## Deploying the lab

The deployment step will spin up a network lab based on the topology defined in the .yaml topology file. 

The command to deploy a lab is:  
```
containerlab [global-flags] deploy [local-flags]
```
With the global `--topo` or `-t` flag a user sets the path to the topology definition file (.yaml) that will be used to spin up a lab.

Example:
```
sudo containerlab deploy -t srx24.yml
```
To display the deloyed network lab
```
sudo containerlab inspect -t srx24.yml
```
```
+---+-----------------------+--------------+--------------------------+---------------+---------+----------------+----------------------+
| # |         Name          | Container ID |          Image           |     Kind      |  State  |  IPv4 Address  |     IPv6 Address     |
+---+-----------------------+--------------+--------------------------+---------------+---------+----------------+----------------------+
| 1 | clab-srx24-srl        | 3a00f5e95e9c | ghcr.io/nokia/srlinux    | nokia_srlinux | running | 172.20.20.2/24 | 2001:172:20:20::2/64 |
| 2 | clab-srx24-sros       | 96c7c1f0db6f | vrnetlab/vr-sros:24.3.R3 | nokia_sros    | running | 172.20.20.3/24 | 2001:172:20:20::3/64 |
+---+-----------------------+--------------+--------------------------+---------------+---------+----------------+----------------------+
```
## Connecting to the lab
To access the network element via CLI you can SSH to it using the admin user.
```
ssh admin@clab-srx24-srl
```

## Exporting the lab

**This section is for your reference only. You are not required to do this section during the hackathon.**

We can share the configuration of our lab with others in many ways.  For sharing the topology only, the topology yaml file we created earlier `lab.clab.yml` can be used.

Before sharing, save the current state of the lab:

```
sudo containerlab save -t lab.clab.yml 
```
```
INFO[0000] Parsing & checking topology file: lab.clab.yml 
INFO[0000] saved sros running configuration to startup configuration file 
INFO[0001] saved SR Linux configuration from srl node. Output:
/system:
    Saved current running configuration as initial (startup) configuration '/etc/opt/srlinux/config.json'
```

Git is the preferred way for sharing a lab. You may use `git push` or manually upload the topology file `lab.clab.yml` and the directory created by Containerlab `clab-sr24` to your Git repo.

Containerlab supports deployment of labs that are stored in remote version control systems. By specifying a URL to a repository or a `.clab.yml` file in a repository, containerlab will automatically clone the repository in your current directory and deploy it. If the URL points to a `.clab.yml` file, containerlab will clone the repository and deploy the lab defined in the file.

Here's an example of deploying a lab stored in Git.

```
sudo clab deploy -t https://github.com/hellt/clab-test-repo/blob/main/lab1.clab.yml
```

In closed environments, it is useful to export the lab as a compressed file.  Create a tar file of the topology file and the directory created by Containerlab for our specific lab. This directory has all the components required for the lab.  You can do this as root (for this hackathon activity) by using the `sudo` command.

```
sudo tar cvf clab-export.tar lab.clab.yml clab-srx24/
```

In the new environemnt, extract the tar file.

```
sudo tar xvf clab-export.tar
```

Now we are able to deploy the lab using the steps in this guide and continue from where we left off.

## Destroying the lab

When we are finished with our testing, we can destroy the lab.

Destroying the lab without the `--cleanup` option retains the containerlab directory created for the lab which holds the information of the lab. This allows us to re-deploy the lab at a later time and start from where we left off.

```
sudo clab destroy -t lab.clab.yml 
```
```
INFO[0000] Parsing & checking topology file: lab.clab.yml 
INFO[0000] Destroying lab: srx24                    
INFO[0000] Removed container: clab-srx24-srl      
INFO[0000] Removed container: clab-srx24-sros     
INFO[0000] Removing containerlab host entries from /etc/hosts file 
INFO[0000] Removing ssh config for containerlab nodes   
```

Destroying the lab with the `--cleanup` option will also delete the directory with the lab information.

```
sudo clab destroy -t lab.clab.yml --cleanup
```
```
INFO[0000] Parsing & checking topology file: lab.clab.yml 
INFO[0000] Destroying lab: srx24                    
INFO[0000] Removed container: clab-srx24-srl      
INFO[0000] Removed container: clab-srx24-sros     
INFO[0000] Removing containerlab host entries from /etc/hosts file 
INFO[0000] Removing ssh config for containerlab nodes   
```

## Using a Startup config

When deploying a lab, we have the option to assign a startup config to our nodes. This is useful when we want our lab to come up with some basic config like interfaces.

By default, Containerlab will push some default configs like management IP, linecard turn up to both SR Linux and SR OS nodes.

When specifying a full config file as described below, Containerlab will use the contents of the file as the full router config and will not apply any of the default configs.

When specifying a partial config, the contents of the file will be applied on top of the default config pushed by Containerlab.

SR Linux startup configuration file can be provided in two formats:
- full SR Linux config in JSON format
- partial config in SR Linux CLI format

Let's a build a partial startup config for SR Linux in CLI format. Save this to a file called `srl-startup.partial.cfg'.

```
set / interface ethernet-1/1 description using-startup
set / interface ethernet-1/1 admin-state enable
set / interface ethernet-1/1 subinterface 0 ipv4 admin-state enable
set / interface ethernet-1/1 subinterface 0 ipv4 address 192.168.10.0/31
set / network-instance default type default
set / network-instance default admin-state enable
set / network-instance default interface ethernet-1/1.0
```

SR OS startup configuration file can be provided in two ways:
- partial config in SR OS CLI format. The file name should have `.partial` string in its name.
- full config in SR OS CLI format. The file name should not have `.partial` string in its name.

In this activity, we will create a partial startup config for SR OS. Save this to a file called `sros-startup.partial.cfg'.

```
/configure port 1/1/c1 admin-state enable
/configure port 1/1/c1 connector breakout c1-100g
/configure port 1/1/c1/1 admin-state enable
/configure port 1/1/c1/1 description "startup-test"
/configure router "Base" interface "To-SRLA" port 1/1/c1/1
/configure router "Base" interface "To-SRLA" ipv4 primary address 192.168.10.1
/configure router "Base" interface "To-SRLA" ipv4 primary prefix-length 31
```

Our goal with these startup configs is to have a L3 connection between the 2 devices. After we deploy the lab, we should be able to ping between the 2 devices using the addresses in the startup configuration files.

Let's modify our topology file to include the startup config files. We will use a different lab name for this purpose so that our existing lab is not impacted. Save the topology to a new file. Let's call it `startup-clab.yml'

```yaml
name: srx24-startup

topology:
  nodes:
    srl:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux
      startup-config: srl-startup.partial.cfg
    sros:
      kind: nokia_sros
      image: vrnetlab/vr-sros:24.3.R3
      type: sr-1
      license: /opt/srexperts/license-sros24.txt
      startup-config: sros-startup.partial.cfg

  links:
    - endpoints: ["srl:e1-1", "sros:eth1"]
```

Deploy the lab.

```
sudo clab deploy -t startup-clab.yml
```

After deployment is complete, login to the SR Linux node and try a ping to the remote SR OS node.

Note - When doing this immediately after deployment, wait for a few ping packets to be sent before getting a successful ping response.

```
ssh admin@clab-srx24-startup-srl
```
```
ping 192.168.10.1 network-instance default
```
```
Using network instance default
PING 192.168.10.1 (192.168.10.1) 56(84) bytes of data.
64 bytes from 192.168.10.1: icmp_seq=1 ttl=64 time=3.47 ms
64 bytes from 192.168.10.1: icmp_seq=2 ttl=64 time=3.04 ms
64 bytes from 192.168.10.1: icmp_seq=3 ttl=64 time=3.13 ms
```

The ping is successful because the interfaces are configured using the startup configs.

## Re-deploying a destroyed lab

A previously destroyed lab can be re-deployed with the `deploy` command.

```
sudo clab deploy -t lab.clab.yml 
```

## Clean up all deployed labs

As the last step, you may destroy and cleanup the deployed labs in your environment:

```
sudo clab destroy -t lab.clab.yml --cleanup
sudo clab destroy -t startup-clab.yml --cleanup
```


