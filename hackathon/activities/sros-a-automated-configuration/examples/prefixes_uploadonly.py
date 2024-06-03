# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Example implementation for the first leg of the automated-configuration
usecase for the Hackathon in SReXperts EMEA 2024.

Calls out to Maxmind API and uploads the found prefixes to the router using
SSH. This version of the file runs remotely and requires a secondary component
deployed on the router.

Tested on: SR OS 24.3.R2-1
"""

# import geoip2.webservice
import json
import os
from io import BytesIO
from zipfile import ZipFile

import paramiko
import requests
from dotenv import find_dotenv, load_dotenv


def getPrefixesFromMaxmind(country):
    """Function that takes a country as input, and queries the example
    database made available by Maxmind for related prefix data. As this
    example database is limited in size, the resulting list of prefixes is
    limited in size as well.

    Returns a list of IP Prefixes associated with the input country.
    """
    url = "https://dev.maxmind.com/static/GeoIP2-Country-CSV_Example.zip"
    resp = requests.get(url, verify=False, proxies={})

    geoip_csv_zipped = ZipFile(BytesIO(resp.content))
    geo_id = 000
    resulting_prefixes = []
    for line in geoip_csv_zipped.open(
        "GeoIP2-Country-CSV_Example/GeoIP2-Country-Locations-en.csv"
    ).readlines():
        if country in line:
            geo_id = line.decode("utf-8").split(",", 1)[0]
    for line in geoip_csv_zipped.open(
        "GeoIP2-Country-CSV_Example/GeoIP2-Country-Blocks-IPv4.csv"
    ).readlines():
        prefix_line = line.decode("utf-8")
        if geo_id in prefix_line:
            resulting_prefixes.append(prefix_line.split(",", 1)[0])
    return resulting_prefixes


def writeFile(filename, prefixes, username, password):
    """For the step the remote script only uploads the file, a separate
    connection is required for the actual upload.

    This function implements that functionality using paramiko. A SFTP
    session is built using the input username and password. A file is
    created on the remote host `clab-srexperts-pe1` containing the input
    prefixes, containing a list of IP prefixes as a json dump.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("clab-srexperts-pe1", username=username, password=password)
    sftp = ssh.open_sftp()
    sros_sftp_session = sftp.open("cf3:/" + filename, "w+")
    sros_sftp_session.write(json.dumps(prefixes))
    sros_sftp_session.close()
    ssh.close()


def main():
    """The main procedure. The execution starts here."""
    load_dotenv(find_dotenv())  # Load the .env file.

    # Fetch variables from the .env file.
    username_var = os.getenv("ACCOUNT_USERNAME")
    password_var = os.getenv("ACCOUNT_PASSWORD")

    # prefixes = getPrefixesFromMaxmind(b"United Kingdom")
    prefixes = getPrefixesFromMaxmind(b"Sweden")
    # with open("prefixes.txt", "w+") as prefixes_file:
    #    prefixes_file.write(str(json.dumps(prefixes)))
    writeFile("prefixes.txt", prefixes, username_var, password_var)


if __name__ == "__main__":
    main()
