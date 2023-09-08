#!/usr/bin/env python
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# coding=utf-8

import grpc
import datetime
import time
import sys
import logging
import os
import json
import signal
import traceback
import re

# sys.path.append('/usr/lib/python3.6/site-packages/sdk_protos')
from sdk_protos import sdk_service_pb2, sdk_service_pb2_grpc, config_service_pb2

# import sdk_common_pb2

# To report state back
import telemetry_service_pb2, telemetry_service_pb2_grpc

from pygnmi.client import gNMIclient, telemetryParser

from logging.handlers import RotatingFileHandler

# from rtr_client import rtr_client as run_rtr_client
from rtr_client.rtr_client import RTRClient

ADMIN_PASSWORD = "NokiaSrl1!"

############################################################
## Agent will start with this name
############################################################
agent_name = "srl_rpki_agent"

############################################################
## Open a GRPC channel to connect to sdk_mgr on the dut
## sdk_mgr will be listening on 50053
############################################################
# channel = grpc.insecure_channel('unix:///opt/srlinux/var/run/sr_sdk_service_manager:50053')
channel = grpc.insecure_channel("127.0.0.1:50053")
metadata = [("agent_name", agent_name)]
stub = sdk_service_pb2_grpc.SdkMgrServiceStub(channel)

# Global gNMI channel, used by multiple threads
gnmi_options = [("username", "admin"), ("password", ADMIN_PASSWORD)]
gnmi_channel = grpc.insecure_channel(
    "unix:///opt/srlinux/var/run/sr_gnmi_server", options=gnmi_options
)
# Postpone connect
# grpc.channel_ready_future(gnmi_channel).result(timeout=5)


############################################################
## Subscribe to required event
## This proc handles subscription of: Interface, LLDP,
##                      Route, Network Instance, Config
############################################################
def Subscribe(stream_id, option):
    # XXX Does not pass pylint
    op = sdk_service_pb2.NotificationRegisterRequest.AddSubscription
    if option == "cfg":
        entry = config_service_pb2.ConfigSubscriptionRequest()
        # entry.key.js_path = '.' + agent_name
        request = sdk_service_pb2.NotificationRegisterRequest(
            op=op, stream_id=stream_id, config=entry
        )

    subscription_response = stub.NotificationRegister(
        request=request, metadata=metadata
    )
    print(
        "Status of subscription response for {}:: {}".format(
            option, subscription_response.status
        )
    )


############################################################
## Subscribe to all the events that Agent needs
############################################################
def Subscribe_Notifications(stream_id):
    """
    Agent will receive notifications to what is subscribed here.
    """
    if not stream_id:
        logging.info("Stream ID not sent.")
        return False

    # Subscribe to config changes, first
    Subscribe(stream_id, "cfg")
    # Subscribe(stream_id, 'nexthop_group')


############################################################
## Function to populate state of agent config
## using telemetry -- add/update info from state
############################################################
def Add_Telemetry(js_path, js_data):
    telemetry_stub = telemetry_service_pb2_grpc.SdkMgrTelemetryServiceStub(channel)
    telemetry_update_request = telemetry_service_pb2.TelemetryUpdateRequest()
    telemetry_info = telemetry_update_request.state.add()
    telemetry_info.key.js_path = js_path
    telemetry_info.data.json_content = json.dumps(js_data)
    logging.info(f"Telemetry_Update_Request :: {telemetry_update_request}")
    telemetry_response = telemetry_stub.TelemetryAddOrUpdate(
        request=telemetry_update_request, metadata=metadata
    )
    return telemetry_response


#
# Uses gNMI to get /platform/chassis/mac-address and format as hhhh.hhhh.hhhh
#
def GetSystemMAC():
    path = "/platform/chassis/mac-address"
    with gNMIclient(
        target=("unix:///opt/srlinux/var/run/sr_gnmi_server", 57400),
        username="admin",
        password=ADMIN_PASSWORD,
        insecure=True,
        debug=False,
    ) as gnmi:
        result = gnmi.get(encoding="json_ietf", path=[path])
        for e in result["notification"]:
            if "update" in e:
                logging.info(f"GetSystemMAC GOT Update :: {e['update']}")
                m = e["update"][0]["val"]  # aa:bb:cc:dd:ee:ff
                return f"{m[0]}{m[1]}.{m[2]}{m[3]}.{m[4]}{m[5]}"

    return "0000.0000.0000"


#
# Runs as a separate thread
#
from threading import Thread, Event


class RPKIThread(Thread):
    def __init__(self, state, net_inst):
        Thread.__init__(self)
        self.daemon = True  # Mark thread as a daemon thread
        self.state = state
        self.event = Event()
        self.net_inst = net_inst

        # Wait for gNMI to connect
        # while True:
        #   try:
        #     grpc.channel_ready_future(gnmi_channel).result(timeout=5)
        #     logging.info( "gRPC unix socket connected" )
        #     break
        #   except grpc.FutureTimeoutError:
        #     logging.warning( "gRPC timeout, continue waiting 5s..." )

    def run(self):
        logging.info(f"RPKIThread run(): {self.net_inst}")
        ni = self.state.network_instances[self.net_inst]
        try:
            cfg = ni["config"]

            # Create per-thread gNMI stub, using a global channel
            # self.gnmi_stub = gNMIStub( gnmi_channel )

            netns_name = f"srbase-{cfg['rpki_ni']}"
            while not os.path.exists(f"/var/run/netns/{netns_name}"):
                logging.info(f"Waiting for {netns_name} netns to be created...")
                time.sleep(2)  # 1 second is not enough
            # with netns.NetNS(nsname=netns_name):
            self.rtr_client = RTRClient(dump=False, debug=0)

            # Does not return
            logging.info(
                f"Connecting to RTR server {cfg['rpki_server']}:{cfg['rpki_port']} in netns {netns_name}"
            )
            self.rtr_client.connect(
                host=cfg["rpki_server"], port=cfg["rpki_port"], namespace=netns_name
            )
            logging.info(f"RPKIThread connected to RTR server")

            # while True: # Keep waiting for route events
            #   self.event.wait(timeout=10.0)
            #   logging.info( f"MonitoringThread received event or 10s timeout expired" )
            #   self.event.clear() # Reset for next iteration

        except Exception as e:
            traceback_str = "".join(traceback.format_tb(e.__traceback__))
            logging.error(f"RPKIThread error: {e} trace={traceback_str}")

        logging.info(f"RPKIThread exit: {self.net_inst}")
        del ni["rpki_thread"]

    def lookup_prefix(self, cidr):
        return self.rtr_client.get_session().lookup_prefix(cidr)


# Upon changes in route counts, check for RPKI changes
class RouteMonitoringThread(Thread):
    def __init__(self, rpki_thread):
        Thread.__init__(self)
        self.rpki_thread = rpki_thread

    def add_rpki_prefix(self, prefix, maxlen, asn, gnmi):
        """Adds the given prefix to a list representing validated RPKI prefixes"""
        # Note: 'maxlen' not yet used
        gnmi.set(
            encoding="json_ietf",
            update=[
                (
                    f"/routing-policy/prefix-set[name=rpki-validated-{asn}]",
                    {"prefix": [{"ip-prefix": prefix, "mask-length-range": "exact"}]},
                )
            ],
        )

    def process_prefix(self, ip_version, prefix, gnmi):
        """Logic to process gNMI on_change event for a given prefix"""

        (maxlen, aslist) = self.rpki_thread.lookup_prefix(prefix)
        logging.info(f"IP prefix: {prefix} maxlen={maxlen} AS list={aslist}")

        # Lookup BGP attr ID for AS path
        p = f"/network-instance[name=default]/bgp-rib/afi-safi[afi-safi-name=ipv{ip_version}-unicast]/ipv{ip_version}-unicast/local-rib/routes[prefix={prefix}]"
        data = gnmi.get(path=[p], encoding="json_ietf")

        # Assume this is a single return value
        base = data["notification"][0]["update"][0]["val"]["routes"][0]
        logging.info(
            f"BGP attr id: {base['attr-id']} neighbor AS {base['neighbor-as']} neighbor {base['neighbor']}"
        )

        # TODO use attr-id to lookup /network-instance default bgp-rib attr-sets attr-set {attr-id} for full as-path

        # If AS is a valid origin according to RPKI, add prefix to list of validated prefixes
        if base["neighbor-as"] in aslist:
            logging.info("Neighbor AS origin validated by RPKI, adding prefix...")
            self.add_rpki_prefix(prefix, maxlen, base["neighbor-as"], gnmi)

            # TODO apply policy to target neighbor based on the rpki-validated-{asn} prefix list

    def run(self):
        logging.info(
            "RouteMonitoringThread run(), wait 30 secs for RPKI to finish sync..."
        )

        time.sleep(30.0)

        # Subscribe to changes in 'active' state for IPv4/v6 prefixes
        regex = re.compile(r".*\[ipv(4|6)-prefix=([^\]]+)\].*")

        subscribe = {
            "subscription": [
                {
                    # Cannot do 'path': f'/network-instance[name=default]/bgp-rib/afi-safi[afi-safi-name={v}-unicast]/{v}-unicast/rib-in-out/rib-in-pre',
                    "path": f"/network-instance[name=default]/route-table/{v}-unicast/route[route-owner=bgp_mgr]/active",
                    # 'path': f'/network-instance[name=default]/bgp-rib/afi-safi[afi-safi-name={v}-unicast]/{v}-unicast/local-rib/routes',
                    "mode": "on_change",
                }
                for v in ["ipv4", "ipv6"]
            ],
            "use_aliases": False,
            # 'updates_only': True, # Optional
            "mode": "stream",
            "encoding": "json",
        }
        with gNMIclient(
            target=("unix:///opt/srlinux/var/run/sr_gnmi_server", 57400),
            username="admin",
            password="NokiaSrl1!",
            insecure=True,
            debug=False,
        ) as c:
            telemetry_stream = c.subscribe(subscribe=subscribe)
            try:
                for m in telemetry_stream:
                    if m.HasField("update"):  # both update and delete events
                        # Filter out only toplevel events
                        parsed = telemetryParser(m)
                        logging.info(
                            f"RouteMonitoringThread gNMI change event :: {parsed}"
                        )
                        update = parsed["update"]
                        if update["update"]:
                            logging.info(f"RouteMonitoringThread: {update['update']}")
                            # Assume routes changed, get attributes.
                            for u in update["update"]:
                                if bool(u["val"]):  # Route active?
                                    path = u["path"]
                                    m = regex.match(path)
                                    if m:
                                        self.process_prefix(m[1], m[2], c)

            except Exception as ex:
                logging.error(ex)
            logging.info("Leaving gNMI subscribe loop - closing gNMI connection")


##################################################################
## Updates configuration state based on 'config' notifications
## May calls vtysh to update an interface
##
## Return: network instance that was updated
##################################################################
def Handle_Notification(obj, state):
    if obj.HasField("config"):
        logging.info(f"GOT CONFIG :: {obj.config.key.js_path}")

        # Tested on main thread
        # ConfigurePeerIPMAC( "e1-1.0", "1.2.3.4", "00:11:22:33:44:55" )

        net_inst = obj.config.key.keys[0]  # e.g. "default"
        if net_inst == "mgmt":
            return None

        def get_data_as_json():
            if obj.config.op == 2:  # Skip deletes, TODO process them?
                return {}
            json_acceptable_string = obj.config.data.json.replace("'", '"')
            return json.loads(json_acceptable_string)

        ni = (
            state.network_instances[net_inst]
            if net_inst in state.network_instances
            else {"config": {}}
        )

        base_path = ".network_instance.protocols.rpki"
        if obj.config.key.js_path == base_path:
            logging.info(
                f"Got config for agent, now will handle it :: \n{obj.config}\
                            Operation :: {obj.config.op}\nData :: {obj.config.data.json}"
            )
            # Could define NETNS here: "NETNS" : f'srbase-{net_inst}'
            params = {"network_instance": net_inst}
            if obj.config.op == 2:
                logging.info(f"Delete config scenario")
                # TODO if this is the last namespace, unregister?
                # response=stub.AgentUnRegister(request=sdk_service_pb2.AgentRegistrationRequest(), metadata=metadata)
                # logging.info( f'Handle_Config: Unregister response:: {response}' )
                # state = State() # Reset state, works?
                # state.network_instances.pop( net_inst, None )
            else:
                data = get_data_as_json()
                if "admin_state" in data:
                    params["admin_state"] = data["admin_state"][12:]
                if "rpki_server" in data:
                    params["rpki_server"] = data["rpki_server"]["value"]
                if "port" in data:
                    params["rpki_port"] = data["port"]["value"]
                if "network_instance" in data:
                    params["rpki_ni"] = data["network_instance"]["value"]

            if "config" in ni:
                ni["config"].update(**params)
            else:
                ni["config"] = params

        # elif obj.config.key.js_path == base_path + ".group":
        #    group_name = obj.config.key.keys[1]
        #    update_conf( 'groups', group_name, get_data_as_json()['group'], True )
        # elif obj.config.key.js_path == base_path + ".neighbor":
        #    neighbor_ip = obj.config.key.keys[1]
        #    update_conf( 'neighbors', neighbor_ip, get_data_as_json()['neighbor'], True )
        else:
            logging.warning(f"Ignoring: {obj.config.key.js_path}")

        logging.info(f"Updated config for {net_inst}: {ni}")
        state.network_instances[net_inst] = ni
        return net_inst
    else:
        logging.info(f"Unexpected notification : {obj}")

    # No network namespaces modified
    logging.info("No network instances modified...")
    return None


class State(object):
    def __init__(self):
        self.network_instances = {}  # Indexed by name
        # TODO more properties

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


def UpdateDaemons(state, modified_netinstances):
    for n in modified_netinstances:
        ni = state.network_instances[n]
        # Shouldn't run more than one thread
        if "config" in ni:
            if "rpki_thread" not in ni:
                rpki_thread = ni["rpki_thread"] = RPKIThread(state, n)
                rpki_thread.start()

                RouteMonitoringThread(rpki_thread).start()  # gRPC monitoring
            else:
                logging.info(f"RPKIThread already running, poke it?")
                # ni['monitor_thread'].CheckForUpdatedInterfaces()
        else:
            logging.warning("Incomplete config, not starting RPKIThread")


##################################################################################################
## This is the main proc where all processing for FRR agent starts.
## Agent registration, notification registration, Subscrition to notifications.
## Waits on the subscribed Notifications and once any config is received, handles that config
## If there are critical errors, unregisters the agent gracefully.
##################################################################################################
def Run():
    sub_stub = sdk_service_pb2_grpc.SdkNotificationServiceStub(channel)

    # optional agent_liveliness=<seconds> to have system kill unresponsive agents
    response = stub.AgentRegister(
        request=sdk_service_pb2.AgentRegistrationRequest(), metadata=metadata
    )
    logging.info(f"Registration response : {response.status}")

    request = sdk_service_pb2.NotificationRegisterRequest(
        op=sdk_service_pb2.NotificationRegisterRequest.Create
    )
    create_subscription_response = stub.NotificationRegister(
        request=request, metadata=metadata
    )
    stream_id = create_subscription_response.stream_id
    logging.info(f"Create subscription response received. stream_id : {stream_id}")

    Subscribe_Notifications(stream_id)

    stream_request = sdk_service_pb2.NotificationStreamRequest(stream_id=stream_id)
    stream_response = sub_stub.NotificationStream(stream_request, metadata=metadata)

    state = State()
    count = 1
    modified = {}  # Dict of modified network instances, no duplicates
    try:
        for r in stream_response:
            logging.info(f"Count :: {count}  NOTIFICATION:: \n{r.notification}")
            count += 1
            for obj in r.notification:
                if obj.HasField("config") and obj.config.key.js_path == ".commit.end":
                    logging.info(
                        f"Processing commit.end, updating daemons...{modified}"
                    )
                    UpdateDaemons(state, modified)
                    modified = {}  # Restart dict
                else:
                    netns = Handle_Notification(obj, state)
                    logging.info(f"Updated state after {netns}: {state}")
                    if (
                        netns in state.network_instances
                    ):  # filter mgmt and other irrelevant ones
                        modified[netns] = True

    except grpc._channel._Rendezvous as err:
        logging.error(f"_Rendezvous error: {err}")

    except Exception as e:
        logging.error("General exception in Run -> exitting")
        logging.exception(e)
        # if file_name != None:
        #    Update_Result(file_name, action='delete')
    # for n in state.ipdbs:
    #   state.ipdbs[n].release()
    Exit_Gracefully(0, 0)


############################################################
## Gracefully handle SIGTERM signal
## When called, will unregister Agent and gracefully exit
############################################################
def Exit_Gracefully(signum, frame):
    logging.info("Caught signal :: {}\n will unregister frr_agent".format(signum))
    try:
        response = stub.AgentUnRegister(
            request=sdk_service_pb2.AgentRegistrationRequest(), metadata=metadata
        )
        logging.error("try: Unregister response:: {}".format(response))
    except grpc._channel._Rendezvous as err:
        logging.error("GOING TO EXIT NOW: {}".format(err))
    finally:
        sys.exit(signum)


##################################################################################################
## Main from where the Agent starts
## Log file is written to: /var/log/srlinux/stdout/<dutName>_fibagent.log
## Signals handled for graceful exit: SIGTERM
##################################################################################################
if __name__ == "__main__":
    # hostname = socket.gethostname()
    stdout_dir = "/var/log/srlinux/stdout"  # PyTEnv.SRL_STDOUT_DIR
    signal.signal(signal.SIGTERM, Exit_Gracefully)
    if not os.path.exists(stdout_dir):
        os.makedirs(stdout_dir, exist_ok=True)
    log_filename = f"{stdout_dir}/{agent_name}.log"
    logging.basicConfig(
        handlers=[RotatingFileHandler(log_filename, maxBytes=3000000, backupCount=5)],
        format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )
    logging.info("START TIME :: {}".format(datetime.datetime.now()))
    Run()
