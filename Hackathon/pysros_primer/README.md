# pySROS primer

## Introduction

This notebook takes the reader on a walk though an introduction to pySROS from Nokia in an interactive format.

The notebook requires:

* A Nokia SR OS device with a valid license.  If you do not have these please contact your Nokia representative.
* The Nokia SR OS device to be in model-driven configuration-mode and using model-driven CLI (the default for all new devices from release 23.3.R1).
* NETCONF must be enabled with administrative permissions for the chosen user.

**You should not run this pySROS primer tutorial on a network element that is part of a live network.  Select
a lab node or a standalone simulator (vSIM).**

## Setup

Clone this repository to your local system.  This system (whether it is a personal workstation or a server) should have access to the SR OS node through any firewalls.

Within the local clone of the repository, edit the `.env` file in the root of the cloned repository to include the specifics for your environment.  The `.env` file looks like this:

```
DEMO_HOST=my_hostname
DEMO_USERNAME=my_username
DEMO_PASSWORD=my_password
DEMO_PORT=830
DEMO_SSH_PORT=22
```

All fields must be completed.

## Running the primer

The notebook can be loaded and run directly in any IDE that supports Jupyter notebooks or from a browser by running Jupyter inside a Docker container.

The run this primer inside a Docker container run `docker compose up -d` (or `docker-compose up -d` on older Docker installations) and then connect to port `8888` in your brower.

## Navigating the primer

This primer is provided as a [Jupyter notebook](https://jupyter.org/).  It should be followed from top to bottom, reading the text and executing the code in order (including the very first cell).  Each paragraph in the notebook is a cell.  Pressing the play button on the cell will run it.  

A `[ ]` icon to the left of the cell means it has not been executed.

A `[*]` icon to the left of the cell means it is currently running.  Do not move onto the next until this has completed.

A `[n]` icon (where `n` is a number) to the left of the cell means it has finished running.  Any output will be displayed immediately below the cell.

## Closing down the primer

The primer session can be concluded by executing `docker compose down -v`.
