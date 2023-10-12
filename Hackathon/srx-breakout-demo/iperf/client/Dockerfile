FROM ubuntu:latest

RUN apt-get update && apt-get install -y iperf3 net-tools inetutils-ping vim

COPY trafficgen.sh /trafficgen.sh

ENTRYPOINT ["/trafficgen.sh"]
