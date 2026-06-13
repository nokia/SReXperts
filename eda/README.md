# EDA Onboard Notes

Note: these commands are for documentation purposes only, everything has been preempted on the cloud instances.

## Clone playground

The playground dir needs to be present on the target system

```shell
git clone https://github.com/nokia-eda/playground.git
cd playground
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
```

## Make tools available in PATH

To make the tools available in PATH, run the following, prepend the path with the directory of the tools.

```shell
export PATH=$(realpath ./tools):$PATH
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

Note, that currently the client nodes require the bonding kernel to be loaded to support the bond interfaces:

```bash
sudo modprobe bonding mmiimon=100 mode=802.3ad lacp_rate=fast
```

The clab topology make use of the following env vars, make sure they are set in your env:

- INSTANCE_ID
- EVENT_PASSWORD
- NOKIA_UID
- NOKIA_GID
- SSH_PUBLIC_KEY (your public key that you want to use in your Node User)

SSH public key can be set to the available pub key in users home dir for local testing:

```bash
export SSH_PUBLIC_KEY=$(cat ~/.ssh/id_rsa.pub)
```

Then check the env vars:

```bash
echo "INSTANCE_ID: $INSTANCE_ID"
echo "EVENT_PASSWORD: $EVENT_PASSWORD"
echo "NOKIA_UID: $NOKIA_UID"
echo "NOKIA_GID: $NOKIA_GID"
echo "SSH_PUBLIC_KEY: $SSH_PUBLIC_KEY"
```

The topology also needs to linux bridges to be create, created them using ip link:

```bash
sudo ip link add pe1-p1 type bridge
sudo ip link add pe2-p1 type bridge
```

Proceed with deploying the topology:

```bash
containerlab deploy -c -t ./clab
```

## Deploy EDA

```shell
SIMULATE=false make try-eda
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

## Accessing EDA UI

EDA UI is automatically exposed when `make try-eda` finishes. No additional steps required to access the UI. It is exposed over HTTPS, port 9443.

## Onboard SRX Topology

As the DC nodes run in clab next to the EDA deployment, we need to onboard them to the EDA cluster.

Start with substituting env vars in the the topo onboard files and run:

```shell
docker run --rm -e \
INSTANCE_ID=$(echo -n $INSTANCE_ID) -e EVENT_PASSWORD="$(echo -n $EVENT_PASSWORD)" -e SSH_PUBLIC_KEY="$(echo -n $SSH_PUBLIC_KEY)" \
-u $(id -u):$(id -g) \
-v $(pwd)/eda/topo-onboard/clab:/work \
ghcr.io/hellt/envsubst:0.2.0
```

Then apply the templated onboarding resources:

```shell
kubectl apply -f $(pwd)/eda/topo-onboard/clab
```

## Deploy Fabric

Before we deploy the fabric, we need to remove some default allocation pools to keep the UI clean and let attendees create pools as they need them.

```shell
# assuming you are in the repo root
bash ./eda/cleanup-pools.sh
```

Then we need to apply the fabric resources so that the fabric is provisioned on the srl nodes, because when EDA onboards the nodes it takes control over the config and pushes the config as it is provided in the CRs.

Again, run the substitute env vars script over the fabric resources:

```shell
# INSTANCE_ID=1 EVENT_PASSWORD=SReXperts2026!
docker run --rm -e INSTANCE_ID=$(echo -n $INSTANCE_ID) -e EVENT_PASSWORD="$(echo -n $EVENT_PASSWORD)" \
-u $(id -u):$(id -g) \
-v $(pwd)/eda/fabric:/work \
ghcr.io/hellt/envsubst:0.2.0
```

and apply them:

```shell
kubectl apply -f $(pwd)/eda/fabric
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

## EDA and Ansible

To automate some provisioning tasks we use Ansible collections for EDA.

Install the collections to a local collections tree, execute from the repo root:

```bash
uv --directory eda run ansible-galaxy collection install -p ./.ansible/collections -r galaxy-requirements.yml
```

With the collections installed, you can now use `ansible-playbook` to run plays against the EDA cluster using the `inventory.yml` file that defines the connection parameters of the EDA cluster.

```bash
uv --directory eda run ansible-playbook -i inventory.yml ./playbooks/users.yaml
```

This will create 2 users (`admin2` and `admin3`) by default.

To create a different number of user:

```bash
uv --directory eda run ansible-playbook -i inventory.yml ./playbooks/users.yaml -e eda_extra_admin_user_count=20
```

## CX on EDA

To support activities around Digital Twin/CX on EDA we spin a single VM that is shared by all attendees. It is configured with many admin users (admin admin2 admin3 ... admin80) based on the max number of instances.

This system spins up EDA with `simulate=true` and uses containerized images for SR-SIM and SRL-SIM. Since the default node profile for SR OS comes without the containerImage in its spec, we need to set it by running kubectl patch on the node profile CR `sros-ghcr-26.3.r1`:

```bash
SRSIM_IMAGE=europe-west1-docker.pkg.dev/nhc-f4160d67/containerlab/nokia_srsim:26.3.R1
kubectl -n eda patch nodeprofile sros-ghcr-26.3.r1 --type=merge -p '{"spec":{"containerImage":"'${SRSIM_IMAGE}'"}}'
```

Then we need to also set the SR-SIM license in the already existing `sros-ghcr-26.3.r1-dummy-license` configmap by reading its content from disk `/opt/srexperts/sros.license`:

```bash
jq -n --rawfile lic /opt/srexperts/sros.license '{data:{"license.key": $lic}}' > /tmp/cm-patch.json
kubectl -n eda-system patch configmap sros-ghcr-26.3.r1-dummy-license --type=merge --patch-file=/tmp/cm-patch.json
```

Now we can use the SR-SIM and SRL-SIM images to spin up the CX topology.
