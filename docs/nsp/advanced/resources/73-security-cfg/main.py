# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import json
import os
import time
import urllib.parse
from base64 import b64decode, b64encode

import requests
from dotenv import find_dotenv, load_dotenv
from requests.auth import HTTPProxyAuth

def getBasicAuthentication(user, pw):
    return b64encode(bytes(user + ':' + pw,'utf-8')).decode('utf-8')


def getToken(nsp_server, basicAuth, proxies):
    url = 'https://'+ nsp_server + '/rest-gateway/rest/api/v1/auth/token'
    body = json.dumps({"grant_type": "client_credentials"})
    token = requests.post(url, headers = basicAuth, data = body, verify = False, proxies=proxies)
    # could do something with refresh_token and expires_in values if it's a longer-running process but in this case that is unnecessary
    return token.json()['access_token']


def revokeToken(nsp_server, token, basicAuth, proxies):
    # revoke token after task is done for sanity reasons
    # nsp has max amount of auth clients allowed
    # makes sense to revoke afterwards

    url = 'https://' + nsp_server + '/rest-gateway/rest/api/v1/auth/revocation'
    body = 'token=' + token + '&token_type_hint=token'
    basicAuth["Content-Type"] = "application/x-www-form-urlencoded"
    revToken = requests.post(url, headers = basicAuth, data = body, verify = False, proxies=proxies)

    if revToken.status_code == 200:
        print("Successfully revoked token.")
    else:
        print(revToken.text)
        print("Error after token revocation attempt.")


def findBasicConfigIntents(nsp_server, version, bearerAuth, proxies, method = requests.post, addendum = ""):
    payload = json.dumps({ "ibn:input": {
        "filter":{
            "config-required":False,
            "intent-type-list": [{
                "intent-type":"basicconfig" + version,
                "intent-type-version":"1"
            }]
        },
        "page-number":0,
        "page-size":100
    }})
    url = 'https://' + nsp_server + '/restconf/operations/ibn:search-intents'
    create_result = method(url, headers = bearerAuth, data = payload, verify = False, proxies=proxies)
    print(
        create_result.status_code,
        create_result.text
    )


def sendBasicConfigIntent(nsp_server, version, bearerAuth, proxies, target, method = requests.post, addendum = ""):
    payload = json.dumps({
        "ibn:intent": {
            "target": target,
            "intent-type": "basicconfig"+version,
            "intent-type-version": 1,
            "required-network-state": "active",
            "ibn:intent-specific-data": {}
        }
    })
    url = 'https://' + nsp_server + '/restconf/data/ibn:ibn'
    create_result = method(url, headers = bearerAuth, data = payload, verify = False, proxies=proxies)
    print(
        create_result.status_code,
        create_result.text
    )


def auditBasicConfigIntent(nsp_server, version, target, bearerAuth, proxies, method = requests.post, addendum = ""):
    url = f"https://{nsp_server}/restconf/data/ibn:ibn/intent={target},basicconfig{version}/audit"
    create_result = method(url, headers = bearerAuth, verify = False, proxies=proxies)
    print(
        create_result.status_code,
        create_result.text
    )


def synchronizeBasicConfigIntent(nsp_server, version, target, bearerAuth, proxies, method = requests.post, addendum = ""):
    url = f"https://{nsp_server}/restconf/data/ibn:ibn/intent={target},basicconfig{version}/synchronize"
    create_result = method(url, headers = bearerAuth, verify = False, proxies=proxies)
    print(
        create_result.status_code,
        create_result.text
    )


def main():
    # Silence annoying warnings
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest="delete", action="store_true")
    parser.add_argument('--curl', dest="curl_only", action="store_true")
    parser.add_argument('--server', dest="nsp_server", required=False, default="")
    parser.add_argument('--user', dest="nsp_user", required=False, default="")
    parser.add_argument('--pass', dest="nsp_pass", required=False, default="")
    parser.add_argument('--inst', dest="inst_id", required=False, default="")
    args = parser.parse_args()

    load_dotenv(find_dotenv())  # Load the .env file.

    # Fetch variables from the .env file or use args.
    nsp_server          = args.nsp_server if args.nsp_server else os.getenv("NSP_SERVER")
    nsp_username        = args.nsp_user if args.nsp_user else os.getenv("NSP_USERNAME")
    nsp_password        = args.nsp_pass if args.nsp_pass else os.getenv("NSP_PASSWORD")
    INSTANCE_ID         = args.inst_id if args.inst_id else os.getenv("INSTANCE_ID")

    basicAuth = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {getBasicAuthentication(nsp_username, nsp_password)}"
    }

    proxies = { }

    token = getToken(nsp_server, basicAuth, proxies)
    bearerAuth = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    # findBasicConfigIntents(nsp_server, "", bearerAuth, proxies)
    # sendBasicConfigIntent(nsp_server, "", bearerAuth, proxies)

    # findBasicConfigIntents(nsp_server, f"-inst{INSTANCE_ID}", bearerAuth, proxies)

    # sendBasicConfigIntent(nsp_server, f"-inst{INSTANCE_ID}", bearerAuth, proxies, f"fd00:fde8::{INSTANCE_ID}:13")

    # auditBasicConfigIntent(nsp_server, f"-inst{INSTANCE_ID}", urllib.parse.quote_plus(f"fd00:fde8::{INSTANCE_ID}:12"), bearerAuth, proxies)
    # synchronizeBasicConfigIntent(nsp_server, f"-inst{INSTANCE_ID}", urllib.parse.quote_plus(f"fd00:fde8::{INSTANCE_ID}:12"), bearerAuth, proxies)

    revokeToken(nsp_server, token, basicAuth, proxies)


if __name__ == "__main__":
    main()
