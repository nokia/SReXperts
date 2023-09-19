FROM ubuntu:latest

ENV http_proxy=http://135.245.192.7:8000
ENV https_proxy=http://135.245.192.7:8000

COPY requirements.txt requirements.txt

# install some useful tools
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3 python-is-python3 python3-pip 
RUN apt-get install -y net-tools inetutils-ping ssh-client sshpass vim telnet bash-completion curl jq
RUN pip install --no-input --trusted-host pypi.org certifi wheel build pip ansible ansible-pylibssh jxmlease
RUN pip install --no-input --trusted-host pypi.org -r requirements.txt
RUN ansible-galaxy collection install nokia.sros ansible.netcommon --force-with-deps

ENTRYPOINT ["bash"]
