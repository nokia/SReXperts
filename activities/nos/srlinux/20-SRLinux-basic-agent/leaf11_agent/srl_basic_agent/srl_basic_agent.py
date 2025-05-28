#!/usr/bin/env python
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# coding=utf-8

# Title: SRLinux Basic agent
# Author: Nokia SReXperts
# Date: 2025-03-03
# location /etc/opt/srl_basic_agent/srl_basic_agent.py

import grpc
import datetime
import sys
import logging
import socket
import os
import ipaddress
import signal
import time
import threading
import json
import subprocess
from time import sleep

import sdk_service_pb2
import sdk_service_pb2_grpc
import config_service_pb2
import telemetry_service_pb2
import telemetry_service_pb2_grpc
import route_service_pb2
import route_service_pb2_grpc
import nexthop_group_service_pb2
import nexthop_group_service_pb2_grpc
import sdk_common_pb2

import re

############################################################
## Agent will start with this name
############################################################
agent_name = 'srl_basic_agent'
metadata = [('agent_name', agent_name)]

############################################################
## Global parameters:
## Open a GRPC channel to connect to the SR Linux sdk_mgr
## sdk_mgr will be listening on 50053
## and create an SDK service client stub
## and create an SDK notification service stub
############################################################

channel = grpc.insecure_channel('127.0.0.1:50053')
stub = sdk_service_pb2_grpc.SdkMgrServiceStub(channel)
sdk_notification_service_client = sdk_service_pb2_grpc.SdkNotificationServiceStub(channel)

#dictionary to save state of each static-route. 
#key: (network-instance,route-prefix)
#value: {admin-status,next-hop-ip,cpe-check-admin-status,cpe-check-thread,cpe-check-is-alive}
ROUTES={}

## Verify that SIGTERM signal was received
sigterm_exit = False

## validate an IPv4 address
def validateIPv4Network(i):
   try:
       if ipaddress.IPv4Network(i):
           return True
   except ValueError as err:
       return False

#Class to hold individual static-route state
class StaticRoute():
    def __init__(self, data, route, network_instance):
        self.mutex = threading.Lock()
        self.admin_enabled = None
        self.cpe_check_enabled = None
        self.cpe_check_thread = None
        self.cpe_check_is_alive = None
        self.next_hop = None
        self.network_instance = network_instance
        self.route = route
        self.installed = False
        self.deleted = False
        self.update_config(data)
        self.evaluate()

    def update_config(self, data):
        logging.info(data)
        nh_changed = False

        self.mutex.acquire()

        if data['route']['admin_state'] == 'ADMIN_STATE_enable':
            self.admin_enabled = True
        else:
            self.admin_enabled = False

        if 'next_hop' in data['route']:
            new_nh = data['route']['next_hop']['value']
            if new_nh != self.next_hop:
                nh_changed = True
                self.next_hop = new_nh

        if data['route']['cpe_check']['admin_state']=='ADMIN_STATE_enable':
            self.cpe_check_enabled = True
            if not self.cpe_check_thread and self.admin_enabled:
                self.create_probe_thread()
            elif not self.admin_enabled:
                self.cpe_check_thread = None
        else:
            self.cpe_check_enabled = False
            self.cpe_check_thread = None

        self.mutex.release()

        if nh_changed:
            self.evaluate(nh_changed=True)
        else:
            self.evaluate()

        #update state datastore
        self.update_telemetry()

    def create_probe_thread(self):
        self.cpe_check_is_alive = True
        self.cpe_check_thread = threading.Thread(target=probe, args=(self, 1))
        self.cpe_check_thread.daemon = True
        self.cpe_check_thread.start()
        self.update_telemetry()

    def install(self, reprogram=False):
        nhg = f"{self.route}_sdk"
        if self.installed == False or reprogram == True:
            nhg_result = create_next_hop_group(nhg_name=nhg,nw_instance=self.network_instance,
                                resolve_to="DIRECT",
                                resolution_type="REGULAR",
                                next_hop_list=[self.next_hop])
            sr_result = create_static_route(nw_instance=self.network_instance,
                                ip_prefix=ipaddress.IPv4Network(self.route).network_address,
                                ip_prefix_length=ipaddress.IPv4Network(self.route).prefixlen,
                                nhg_name=nhg,
                                preference=10,
                                metric=10)
            if (not sr_result or not nhg_result):
                logging.error(f"Failed to install/reinstall route {self.route} with next-hop {self.next_hop} in {self.network_instance}")
                return False
            if self.installed == True:
                logging.info(f"reinstalled route {self.route} with next-hop {self.next_hop} in {self.network_instance}")
            else:
                logging.info(f"installed route {self.route} with next-hop {self.next_hop} in {self.network_instance}")
            self.installed=True
            return True
    def uninstall(self):
        if self.installed == True:
            del_sr = delete_static_route(nw_instance=self.network_instance,
                                ip_prefix=ipaddress.IPv4Network(self.route).network_address,
                                ip_prefix_length=ipaddress.IPv4Network(self.route).prefixlen)
            del_nhg = delete_next_hop_group(nhg_name=f"{self.route}_sdk", nw_instance=self.network_instance)
            
            if not del_sr or not del_nhg:
                logging.error(f"failed to uninstall route {self.route} in {self.network_instance}")
                return False

            self.installed=False
            logging.info(f"uninstalled route {self.route} in {self.network_instance}")
            return True

    def destroy(self):
        self.mutex.acquire()
        self.cpe_check_thread = None
        self.deleted = True
        self.mutex.release()

        uninstall_result = self.uninstall()
        if not uninstall_result:
            logging.error(f"Something went wrong while destroying route {self.route} in {self.network_instance}")
            return False
        logging.info(f"destroyed route {self.route} in {self.network_instance}")

        self.update_telemetry()

        return True

    def evaluate(self, nh_changed=False):
        self.mutex.acquire()

        if not self.admin_enabled or not self.next_hop or (self.cpe_check_enabled and not self.cpe_check_is_alive):
            self.uninstall()
        else:
            if nh_changed:
                self.install(reprogram=True)
            else:
                self.install()

        self.mutex.release()
    
    def update_telemetry(self):
        js_path = f'.network_instance{{.name=="{self.network_instance}"}}.static_routes_ndk.route{{.prefix=="{self.route}"}}'

        js_data = {
            "admin_state": 'ADMIN_STATE_enable' if self.admin_enabled else 'ADMIN_STATE_disable',
            "next_hop": self.next_hop,
            "cpe_check": {
                "admin_state": 'ADMIN_STATE_enable' if self.cpe_check_enabled else 'ADMIN_STATE_disable',
            }
        }

        if self.deleted:
            delete_state_datastore(js_path)
            return

        if self.cpe_check_thread:
            js_data['cpe_check']['is-alive'] =  self.cpe_check_is_alive

        update_state_datastore(js_path=js_path, js_data=json.dumps(js_data))
    
    def update_aliveness(self, alive):
        #if alive status changed, evaluate route and update telemetry
        if alive != self.cpe_check_is_alive:
            self.cpe_check_is_alive = alive
            self.evaluate()
            self.update_telemetry()


########################################################
## probe function
########################################################
def probe(staticroute, timeout):
    current_thread=staticroute.cpe_check_thread
    namespace = f'srbase-{staticroute.network_instance}'
    logging.info(f'probe thread started for {staticroute.route} in {staticroute.network_instance}')

    #run infinitely until gets decoupled from the StaticRoute object
    while current_thread == staticroute.cpe_check_thread:
        if staticroute.next_hop:
            command = ['ip','netns','exec',namespace,'ping','-c','1','-W',str(timeout),staticroute.next_hop]
            probe_result=subprocess.run(command, shell=False, check=False ,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE, universal_newlines=True)
            if probe_result.returncode == 0:
                staticroute.update_aliveness(True)
            else:
                staticroute.update_aliveness(False)
        sleep(1)
    logging.info(f'probe thread finished for {staticroute.route} in {staticroute.network_instance}')


########################################################
## Create a next-hop group
## In:
## - nhg_name: the name of the NHG
## - nw_instance: the network instance in which the route is created
## - resolve_to: resolve to type (LOCAL, DIRECT or INDIRECT)
## - resolution_type: resolution type (REGULAR or MPLS)
## - next_hop_list: a list of one or more netxh hops
#########################################################
def create_next_hop_group(nhg_name, nw_instance, resolve_to, resolution_type, next_hop_list):
    nhg_stub = nexthop_group_service_pb2_grpc.SdkMgrNextHopGroupServiceStub(channel)
    nhg_request = nexthop_group_service_pb2.NextHopGroupRequest()
    nhg_info = nhg_request.group_info.add()
    nhg_info.key.name = nhg_name
    nhg_info.key.network_instance_name = nw_instance
    for next_hop_ip in next_hop_list:
        nh = nhg_info.data.next_hop.add()
        nh.type = nexthop_group_service_pb2.NextHop.ResolutionType.Value(resolution_type)
        nh.resolve_to = nexthop_group_service_pb2.NextHop.ResolveToType.Value(resolve_to)
        nh.ip_nexthop.addr = ipaddress.ip_address(next_hop_ip).packed

    nhg_response = nhg_stub.NextHopGroupAddOrUpdate(request=nhg_request, metadata=metadata)
    if nhg_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"NHG addition failed for {nhg_name} with error {nhg_response.error_str}")
        return False
    return True
########################################################
## Delete a next-hop group
## In:
## - nhg_name: the name of the NHG
## - nw_instance: the network instance in which the route is created
#########################################################
def delete_next_hop_group(nhg_name, nw_instance):
    nhg_stub = nexthop_group_service_pb2_grpc.SdkMgrNextHopGroupServiceStub(channel)
    nhg_request = nexthop_group_service_pb2.NextHopGroupDeleteRequest()
    nhg_key = nhg_request.group_key.add()
    nhg_key.name = nhg_name
    nhg_key.network_instance_name = nw_instance

    nhg_response = nhg_stub.NextHopGroupDelete(request=nhg_request, metadata=metadata)
    if nhg_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"NHG deletion failed for {nhg_name} with error {nhg_response.error_str}")
        return False
    return True

########################################################
## Create a new static route to the routing table
## In:
## - nw_instance: the network instance in which the route is created
## - ip_prefix: the ip address of the static route w/o mask
## - ip_prefix_length: the mask length
## - nhg_name: the next group for this static IP
## - preference: the preference value of the static route
## - metric: the metric of the static route
#########################################################
def create_static_route(nw_instance, ip_prefix, ip_prefix_length, nhg_name,
                        preference=None, metric=None):
    route_stub = route_service_pb2_grpc.SdkMgrRouteServiceStub(channel)
    route_request = route_service_pb2.RouteAddRequest()
    route_info = route_request.routes.add()
    route_info.key.net_inst_name = nw_instance
    route_info.key.ip_prefix.ip_addr.addr = ipaddress.ip_address(ip_prefix).packed
    route_info.key.ip_prefix.prefix_length = ip_prefix_length
    
    route_info.data.nexthop_group_name = nhg_name

    if preference is not None:
        route_info.data.preference = preference
    if metric is not None:
        route_info.data.metric = metric
    route_response = route_stub.RouteAddOrUpdate(request=route_request, metadata=metadata)
    if route_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Route {ip_prefix}/{ip_prefix_length} addition failed with error {route_response.error_str}")
        return False
    return True
########################################################
## Delete a static-route
## In:
## - nw_instance: the network instance in which the route is created
## - ip_prefix: the ip address of the static route w/o mask
## - ip_prefix_length: the mask length
#########################################################
def delete_static_route(nw_instance, ip_prefix, ip_prefix_length):
    route_stub = route_service_pb2_grpc.SdkMgrRouteServiceStub(channel)
    route_request = route_service_pb2.RouteDeleteRequest()
    route_key = route_request.routes.add()
    route_key.net_inst_name = nw_instance
    route_key.ip_prefix.ip_addr.addr = ipaddress.ip_address(ip_prefix).packed
    route_key.ip_prefix.prefix_length = ip_prefix_length

    route_response = route_stub.RouteDelete(request=route_request, metadata=metadata)
    if route_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Route {ip_prefix}/{ip_prefix_length} deletion failed with error {route_response.error_str}")
        return False
    return True


############################################################
## update a object in the state datastore
## using the telemetry grpc service
## Input parameters:
## - js_path: JSON Path = the base YANG container
## - js_data: JSON attribute/value pair(s) based on the YANG model
############################################################
def update_state_datastore(js_path, js_data):
    pass

############################################################
## delete an object in the state datastore
## using the telemetry grpc service
## Input parameters:
## - js_path: JSON Path = the base YANG container
############################################################
def delete_state_datastore(js_path):

    # create gRPC client stub for the Telemetry Service
    telemetry_stub = telemetry_service_pb2_grpc.SdkMgrTelemetryServiceStub(channel)

    # Build an telemetry delete service request
    telemetry_delete_request = telemetry_service_pb2.TelemetryDeleteRequest()

    # Add the YANG Path and Attribute/Value pair to the request
    telemetry_key = telemetry_delete_request.key.add()
    telemetry_key.js_path = js_path

    # Log the request
    logging.info(f"Telemetry_Delete_Request ::\{telemetry_delete_request}")

    # Call the telemetry RPC
    telemetry_response = telemetry_stub.TelemetryDelete(
        request=telemetry_delete_request,
        metadata=metadata)

    return telemetry_response



############################################################
## Gracefully handle SIGTERM signal (SIGTERM number = 15)
## When called, will unregister Agent and gracefully exit
############################################################
def exit_gracefully(signum, frame):
    logging.info(f"SIGTERM Received: {signum}")
    logging.info("Caught signal :: {}\ will unregister srl_basic_agent agent".format(signum))
    try:
        global sigterm_exit
        sigterm_exit = True
        logging.info(f"Unregister Agent")

        # unregister agent
        unregister_request = sdk_service_pb2.AgentRegistrationRequest()
        unregister_response = stub.AgentUnRegister(request=unregister_request, metadata=metadata)
        logging.info(f"Unregister response:: {sdk_common_pb2.SdkMgrStatus.Name(unregister_response.status)}")
    except grpc._channel._Rendezvous as err:
        logging.error('GOING TO EXIT NOW: {}'.format(err))
        sys.exit()

## Keep Alive thread: send a keep every 10 seconds via gRPC call
def send_keep_alive():
    ## exit the thread when sigterm is received
    while not sigterm_exit:
        logging.info("Send Keep Alive")
        keepalive_request = sdk_service_pb2.KeepAliveRequest()
        keepalive_response = stub.KeepAlive(request=keepalive_request, metadata=metadata)
        if keepalive_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
            logging.error("Keep Alive failed")
        time.sleep(10)

#####################################
## Create an SDK notification stream
#####################################
def create_sdk_stream():

    # build Create request
    op = sdk_service_pb2.NotificationRegisterRequest.Create
    request=sdk_service_pb2.NotificationRegisterRequest(op=op)

    # call SDK RPC to create a new stream
    notification_response = stub.NotificationRegister(
        request=request,
        metadata=metadata)

    # process the response, return stream ID if successful
    if notification_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Notification Stream Create failed with error {notification_response.error_str}")
        return 0
    else:
        logging.info(f"Notification Stream successful. stream ID: {notification_response.stream_id}, sub ID: {notification_response.sub_id}")
        return notification_response.stream_id

#########################################################
## Use notification stream to subscribe to 'config events
#########################################################
def add_sdk_config_subscription(stream_id):

    # Build subscription request for config events
    subs_request=sdk_service_pb2.NotificationRegisterRequest(
        op=sdk_service_pb2.NotificationRegisterRequest.AddSubscription,
        stream_id=stream_id,
        config=config_service_pb2.ConfigSubscriptionRequest())

    # Call RPC
    subscription_response = stub.NotificationRegister(
        request=subs_request,
        metadata=metadata)


    # Process response
    if subscription_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error("Config Subscription failed")
    else:
        logging.info(f"Config Subscription successful. stream ID: {subscription_response.stream_id}, sub ID: {subscription_response.sub_id}")
    return


########################################################
## Start notification stream from SDK SR Linux
#########################################################
def start_notification_stream(stream_id):

    # Build request
    request=sdk_service_pb2.NotificationStreamRequest(stream_id=stream_id)

    # Call Server Streaming SDK service
    # SR Linux will start streamning requested notifications
    notification_stream = sdk_notification_service_client.NotificationStream(
        request=request,
        metadata=metadata)

    # return the stream
    return notification_stream


########################################################
## Process the received notification stream
## Only config events are expected
## Exit the loop if SIGTERM is received
#########################################################
def process_notification(notification):
    for obj in notification.notification:
        if obj.HasField("config"):
            ## Process config notification
            logging.info("--> Received config notification")
            process_config_notification(obj)
        else:
            logging.info("--> Received unexpected notification")
        if sigterm_exit:
            ## exit loop if agent has been stopped
            logging.info("Agent Stopped Time :: {}".format(datetime.datetime.now()))
            return


########################################################
## Process specifically a config notification
## Expects that 'name' from 'srl_basic_agent' branch has been configured
## Will set 'response' string as a response
#########################################################
def process_config_notification(obj):
    global ROUTES

    if obj.config.key.js_path != ".network_instance.static_routes_ndk.route":
        logging.info(f'ignore js_path={obj.config.key.js_path}')
        return
    netinst = obj.config.key.keys[0]
    route = obj.config.key.keys[1]

    if obj.config.op == 2:
        logging.info("Received a delete notification")
        if (netinst, route) in ROUTES:
            ROUTES[(netinst, route)].destroy()
            del ROUTES[(netinst, route)]
        return
    logging.info("Received a create/update notification")
    data = json.loads(obj.config.data.json)
    logging.info(f"DataJson :: {data}" )

    if (netinst, route) in ROUTES:
        ROUTES[(netinst, route)].update_config(data)
    else:
        ROUTES[(netinst, route)] = StaticRoute(data,network_instance=netinst, route=route)

## Main agent function
def run_agent():

    ## Register Agent
    register_request = sdk_service_pb2.AgentRegistrationRequest()
    register_request.agent_liveliness=30
    register_response = stub.AgentRegister(request=register_request, metadata=metadata)
    if register_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Agent Registration failed with error {register_response.error_str}")
    else:
        logging.info(f"Agent Registration successful. App ID: {register_response.app_id}")

    app_id = register_response.app_id

    ## Start separate thread to send keep alive every 10 seconds
    thread = threading.Thread(target=send_keep_alive)
    thread.start()

    ## Create a new SDK notification stream
    stream_id = create_sdk_stream()

    ## Subscribe to 'config' notifications
    ## Only configuration of srl_basic_agent YANG data models will be received
    ## And only once they are commit into the running configuration
    add_sdk_config_subscription(stream_id)

    ## Start listening for notifications from SR Linux
    notification_stream  = start_notification_stream(stream_id)

    ## process received notifications
    for notification in notification_stream:
        logging.info(f"Received Notification ::\{notification}")
        process_notification(notification)


if __name__ == '__main__':
    ## configure SIGTERM handler
    signal.signal(signal.SIGTERM, exit_gracefully)

    ## configure log file
    log_filename = '/var/log/srlinux/stdout/srl_basic_agent_python.log'
    logging.basicConfig(filename=log_filename, filemode='a',datefmt='%H:%M:%S', level=logging.INFO)
    logging.info("Agent Start Time :: {}".format(datetime.datetime.now()))

    ## Run agent function
    run_agent()
    sys.exit()
