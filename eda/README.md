# EDA Onboard Notes

Note: these commands are for documentation purposes only, everything has been preempted on the cloud instances.

## Copy files

To copy the files from this repo to a remote system:

```shell
# RS_DEST=nokia@1.edadev.srexperts.net
# RS_REMOTE_DEST=/home/nokia/eda
RS_DEST=demo1.ohn81
RS_REMOTE_DEST=/root/eda
rsync -avz --delete eda/fabric ${RS_DEST}:${RS_REMOTE_DEST}
```

```shell
# RS_DEST=nokia@1.edadev.srexperts.net
# RS_REMOTE_DEST=/home/nokia/eda
RS_DEST=demo1.ohn81
RS_REMOTE_DEST=/root/eda
rsync -avz --delete eda/topo-onboard ${RS_DEST}:${RS_REMOTE_DEST}
```

will move the `fabric` dir to `/root/eda` on the remote system.

## Clone playground

The playground dir needs to be present on the target system

```shell
git clone https://github.com/nokia-eda/playground.git
```

## Ensure sysctls are raised

Sysctls needs to be raised to ensure EDA runs smoothly.

While in the playground dir call:

```shell
make configure-sysctl-params
```

## Download tools

while in the playground dir call:

```shell
make download-tools
make download-k9s
```

## Copy kubectl and k9s

Copy the kubectl and k9s tools from the playground/tools dir to `/usr/local/bin` so they are available to a user:

```shell
cp ./tools/kubectl* /usr/local/bin/kubectl
cp ./tools/k9s* /usr/local/bin/k9s
```

### kubectl completions

<small>from https://spacelift.io/blog/kubectl-auto-completion#how-to-set-up-kubectl-autocomplete-in-a-linux-bash-shell</small>

Run this once during the setup of the host (should run after bash-completion is installed):

```
kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
```

### kubectl alias

During the setup run:

```
echo 'alias k=kubectl' >>~/.bashrc
```

Also to enable completions on the alias, run once during setup:

```
echo 'complete -o default -F __start_kubectl k' >>~/.bashrc
```

## edactl

To allow users to use `edactl` from the lab host, we need to setup an alias that would use edactl from the EDA's toolbox pod.

This should go into the shell rc file

```
alias edactl='kubectl -n eda-system exec -it $(kubectl -n eda-system get pods \
-l eda.nokia.com/app=eda-toolbox -o jsonpath="{.items[0].metadata.name}") \
-- edactl'
```

## Deploy containerlab topo

The clab topo needs to be deployed without startup configs mounted to the DC1 nodes; this requirement will be lifted once the BGP fix is merged into SRL.

For now, we need to comment out the startup configs by running the following:

```bash
uv run clab/comment-startup.py
```

Note, that currently the client nodes require the bonding kernel to be loaded to support the bond interfaces:

```
sudo modprobe bonding mmiimon=100 mode=802.3ad lacp_rate=fast
```

## Deploy EDA

```shell
# EDA_DN=1.edadev.srexperts.net
EDA_DN=10.181.131.41
SIMULATE=false EXT_DOMAIN_NAME=${EDA_DN} make try-eda
```

## Add EDA License

Put the [EDA license](https://gitlabe2.ext.net.nokia.com/sr/eda/license/-/blob/main/eda-non-prod-license.yaml?ref_type=heads) in `/opt/srexperts`

Apply the license after EDA is deployed:

```
kubectl apply -f /opt/srexperts/eda-non-prod-license.yaml
```

## Store EDA last transaction hash

To enable users to revert to an initial state the EDA was deployed, we need to store the last transaction and its hash after we deployed EDA.

Execute `bash eda/record-init-tx.sh` script that will store the `TX_ID TX_HASH` pair in the `/opt/srexperts/eda-init-tx` file. This file then can be used to revert EDA to this transaction.

## Exposing EDA UI

EDA UI is automatically exposed when `make try-eda` finishes. But whenever there are issues with UI access we might need to restart the service:

```
make start-ui-port-forward
```

## Onboard SRX Topology

As the DC nodes run in clab next to the EDA deployment, we need to onboard them to the EDA cluster.

Start with substituting env vars in the the topo onboard files. Change into the `eda` directory in the root of the hackathon repo and run:

```shell
docker run --rm -e INSTANCE_ID=$(echo $INSTANCE_ID) -e EVENT_PASSWORD=$(echo $EVENT_PASSWORD) \
-u $(id -u):$(id -g) \
-v $(pwd)/topo-onboard/clab:/work \
ghcr.io/hellt/envsubst:0.1.0
```

Then apply the templated onboarding resources:

```shell
kubectl apply -f $(pwd)/topo-onboard/clab
```

## Deploy Fabric

Before we deploy the fabric, we need to remove some default allocation pools to keep the UI clean and let attendees create pools as they need them.

```shell
# assuming you are in the ./eda directory
bash cleanup-pools.sh
```

Then we need to apply the fabric resources so that the fabric is provisioned on the srl nodes, because when EDA onboards the nodes it takes control over the config and pushes the config as it is provided in the CRs.

Again, run the substitute env vars script over the fabric resources:

```shell
docker run --rm -e INSTANCE_ID=$(echo $INSTANCE_ID) -e EVENT_PASSWORD=$(echo $EVENT_PASSWORD) \
-u $(id -u):$(id -g) \
-v $(pwd)/fabric:/work \
ghcr.io/hellt/envsubst:0.1.0
```

and apply them:

```shell
kubectl apply -f $(pwd)/fabric
```

## Extract the kubeconfig

(TBD if we need it, since the kind cluster will originally have only 127.0.0.1 as the k8s API)

Extract the kubeconfig for the kind cluster running EDA:

```
mkdir ~/.kube
/home/nokia/eda/playground/tools/kind-v0.24.0 get kubeconfig --name eda-demo > ~/.kube/eda.kubeconfig
```

## Restore script

When users need to restore EDA to a well known state, they should run the following script:

```bash
bash /opt/srexperts/restore-eda.sh
```

This script restores the transaction recorded in `/opt/srexperts/eda-init-tx` by the lab provisioning script. The transaction stored in this file is the last transaction of the deployment/onboarding and represents the starting state of the platform.
