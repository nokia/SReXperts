INSTANCE_ID ?= 1
CLAB_LABDIR_BASE ?= /home/nokia
EVENT_PASSWORD ?= SReXperts2024

config:
	envsubst < configs/sros/p1.partial.tmpl.cfg | tee configs/sros/p1.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/p2.partial.tmpl.cfg | tee configs/sros/p2.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/pe1.partial.tmpl.cfg | tee configs/sros/pe1.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/pe2.partial.tmpl.cfg | tee configs/sros/pe2.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/pe3.partial.tmpl.cfg | tee configs/sros/pe3.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/pe4.partial.tmpl.cfg | tee configs/sros/pe4.partial.cfg > /dev/null 2>&1
	envsubst < configs/sros/vRR.partial.tmpl.cfg | tee configs/sros/vRR.partial.cfg > /dev/null 2>&1
	envsubst < configs/srl/spine11.tmpl.cfg | tee configs/srl/spine11.cfg > /dev/null 2>&1
	envsubst < configs/srl/spine12.tmpl.cfg | tee configs/srl/spine12.cfg > /dev/null 2>&1
	envsubst < configs/srl/leaf11.tmpl.cfg | tee configs/srl/leaf11.cfg > /dev/null 2>&1
	envsubst < configs/srl/leaf12.tmpl.cfg | tee configs/srl/leaf12.cfg > /dev/null 2>&1
	envsubst < configs/srl/leaf13.tmpl.cfg | tee configs/srl/leaf13.cfg > /dev/null 2>&1
	envsubst < configs/srl/leaf21.tmpl.cfg | tee configs/srl/leaf21.cfg > /dev/null 2>&1
	envsubst < configs/srl/agg1.tmpl.cfg | tee configs/srl/agg1.cfg > /dev/null 2>&1
	envsubst < configs/srl/ixp1.tmpl.cfg | tee configs/srl/ixp1.cfg > /dev/null 2>&1
	envsubst < configs/srl/peering2.tmpl.cfg | tee configs/srl/peering2.cfg > /dev/null 2>&1
	envsubst < configs/radius/interfaces.tmpl | tee configs/radius/interfaces > /dev/null 2>&1
	envsubst < configs/radius/clients.tmpl.conf | tee configs/radius/clients.conf > /dev/null 2>&1
	envsubst < configs/transit/gobgp.tmpl.yml | tee configs/transit/gobgp.yml > /dev/null 2>&1
	envsubst < configs/dns/dnsmasq.tmpl.conf | tee configs/dns/dnsmasq.conf > /dev/null 2>&1
	envsubst < configs/sros/boot-good-exec.tmpl.cfg | tee configs/sros/boot-good-exec.cfg > /dev/null 2>&1


clean:
	rm configs/sros/*.partial.cfg
	rm configs/srl/spine11.cfg
	rm configs/srl/spine12.cfg
	rm configs/srl/leaf11.cfg
	rm configs/srl/leaf12.cfg
	rm configs/srl/leaf13.cfg
	rm configs/srl/leaf21.cfg
	rm configs/srl/agg1.cfg
	rm configs/srl/ixp1.cfg
	rm configs/srl/peering2.cfg
	rm configs/radius/interfaces
	rm configs/radius/clients.conf
	rm configs/transit/gobgp.yml
	rm configs/dns/dnsmasq.conf
	rm configs/sros/post-good-exec.cfg
	rm ../activities/sros-ansible-netconf/ansible-example/group_vars/sros_routers

deploy: config
	EVENT_PASSWORD=${EVENT_PASSWORD} CLAB_LABDIR_BASE=${CLAB_LABDIR_BASE} INSTANCE_ID=${INSTANCE_ID} sudo -E containerlab deploy -t srx.clab.yml --reconfigure

destroy:
	sudo -E containerlab destroy -t srx.clab.yml --cleanup
