# Install Your Own EDA

|                       |                                                                             |
| --------------------- | --------------------------------------------------------------------------- |
| **Short Description** | The full power of EDA with a simulated network topology. All on your laptop |
| **Difficulty**        | Intermediate                                                                |
| **Topology Nodes**    | N/A                                                                         |
| **Tools used**        | make, KinD, macOS/Linux/Windows                                             |

In the modern cloud-native world of infrastructure automation it is common to offer an open source/freemium version for people to get familiar with the platform/software and try things out before they invest in the enterprise offering.

With Nokia EDA we give you a way to install the platform with all its features and without:

- asking for a license
- forcing you to register
- limiting you with a time-based trial

We are happy to offer this flexibility and openness of the platform to everyone who wants to try EDA.

## Objective

By completing this exercise you will get familiar with EDA's installation process, hardware requirements and packaging **for non-production/lab environments**. We will solely focus on setting up EDA for lab and demo purposes where the whole system is brought up in a development Kubernetes cluster with a small virtual network topology to try out the platform.

## Technology Explanation

EDA is a cloud-native platform for infrastructure automation. It is deployed on top of a Kubernetes cluster and consists of a set of microservices responsible for various tasks such as:

- configuration provisioning
- state synchronization and reconciliation
- node bootstrap
- workflow orchestration
- artifact management
- and so on...

If microservices and Kubernetes concepts are new to you, fear not, you don't have to be a PhD in cloud-native to install EDA in the lab environment, let alone to use it.
We call the process of installing a lab instance of EDA - **Try EDA** - and it is [documented on docs.eda.dev](https://docs.eda.dev/getting-started/try-eda/).

The Try EDA installation installs the **EDA Playground** - a lab environment that consists of a [KinD](https://kind.sigs.k8s.io/) k8s cluster with EDA platform and a small virtual network topology with SR Linux nodes running on top of it.

-{{ diagram(url='srexperts/hackathon-diagrams/main/eda.drawio', title='', page=3, zoom=1.5) }}-

By leveraging EDA's deployment model that uses Kubernetes, we can install EDA Playground on any compute that runs Kubernetes or KinD:

<div class="grid cards" markdown>

- :simple-linux:{ .middle } **Linux**

    ---

    Of course, you can install EDA on any compute powered by Linux. Just use the [Try EDA](https://docs.eda.dev/getting-started/try-eda/) installation guide to get started.

    [:octicons-arrow-right-24: Try EDA on Linux](https://docs.eda.dev/getting-started/try-eda/)

- :fontawesome-brands-windows:{ .middle } **Windows**

    ---

    You can install EDA on Windows as well! Leveraging the Windows Subsystem for Linux (WSL) you can install EDA on top of it. Check out our guide.

    [:octicons-arrow-right-24: Try EDA on Windows](https://docs.eda.dev/software-install/non-production/wsl/)

- :simple-apple:{ .middle } **MacOS**

    ---

    Ever wanted to make your expensive MacBook actually do something useful? Install EDA on it!

    By setting up Docker on your Mac you can install EDA on top of it. Check out our guide.

    [:octicons-arrow-right-24: Try EDA on macOS](https://docs.eda.dev/software-install/non-production/macos/)

- :simple-kubernetes:{ .middle } **Existing Kubernetes cluster**

    ---

    If you happen to have access to an existing Kubernetes cluster, you can install EDA on it as well. You will have dive into the installation bits we packaged in the [Makefile](https://github.com/nokia-eda/playground/blob/main/Makefile) of the EDA Playground to understand what sub-targets to call and in what order.

    This is a more advanced path, as you will need to understand basic Kubernetes concepts and EDA installation process to get it running.

    [:octicons-arrow-right-24: Playground on an existing Kubernetes cluster](https://docs.eda.dev/software-install/non-production/on-prem-cluster/)

</div>

/// note | Did you know that
Everyone can install EDA whenever they like. EDA software components are distributed as a set of container images that can be pulled by anyone, whenever they like.

You can create an infinite number of virtual SR Linux nodes in the free version of EDA. The only time you need a license is when you want to manage hardware devices.
///

## Tasks

As you may have guessed, we invite you to Try EDA on your own compute - be it your laptop, or a server in your lab.

/// warning | System requirements
Regardless of the platform you choose, you will have to ensure that the following system requirements are met:

- 10 CPU cores
- 16 GB RAM
- 30 GB disk space

This is the amount of resources that your kubernetes cluster implemented by the KinD should have available. Or simply put, your VM that you use to run the playground should be provisioned with these amount of resources.
///

Choose your deployment option and equip yourself with the following documentation articles to help you get going:

- [Try EDA process explained](https://docs.eda.dev/getting-started/try-eda/) - to install EDA on a Linux server.
- [macOS install instructions](https://docs.eda.dev/software-install/non-production/macos/) - to install EDA Playground on a macOS.
- [Windows install instructions](https://docs.eda.dev/software-install/non-production/wsl/) - to install EDA Playground on a Windows machine.
- [`Makefile`](https://github.com/nokia-eda/playground/blob/main/Makefile) from the EDA Playground repository - to see what actually being installed and how when you run `make try-eda` command.
- [Installation process explained](https://docs.eda.dev/getting-started/installation-process/) - to have a deeper dive on how EDA is installed on a Linux server.

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
