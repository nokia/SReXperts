# How to run this lab on your own environment?

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

once these variables are exposed, one can run this lab by executing:
(assuming this repo has been checked out in $HOME/SReXperts)

``` bash
CLAB_LABDIR_BASE=$HOME sudo -E clab deploy -t $HOME/SReXperts/clab/srx.clab.yml --reconfigure
```
