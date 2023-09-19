.PHONY: all
all: netmgmt iperfclient iperfserver pysros_cache

.PHONY: netmgmt
netmgmt:
	docker build -t netmgmt ./netmgmt/

.PHONY: iperfclient
iperfclient:
	docker build -t iperfclient ./iperf/client/

.PHONY: iperfserver
iperfserver:
	docker build -t iperfserver ./iperf/server/

.PHONY: pysros_cache
pysros_cache:
	mkdir -p .pysros

.PHONY: clean
clean:
	docker image rm netmgmt:latest iperfclient:latest iperfserver:latest
