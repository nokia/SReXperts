# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.ehs import get_event
from pysros.management import connect


def main():

    connection = connect(
        host="local connection only - unused",
        username="local connection only - unused",
    )

    print(">>>You are connected to device: pe4")

    trigger_event = get_event()
    if trigger_event.eventid in [2009, 2010]:
        data1 = connection.running.get(
            "/nokia-state:state/users/session",
            filter={
                "user": {},
                "connection-type": "sshv2",
                "connection-ip": {},
            },
        )

        number_of_sessions = len(list(data1.keys()))
        print("Number of active sessions:", number_of_sessions)

        new_system_name = "pe4_active_sessions=" + str(number_of_sessions)
        print("Node's system name changed to: ", new_system_name)

        name_path = "/nokia-conf:configure/system"
        name_payload = {"name": new_system_name}

        connection.candidate.set(name_path, name_payload)


if __name__ == "__main__":
    main()
