# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import re
import sys

import uos
from pysros.management import connect  # type: ignore


def simpleString(inputstring):
    if type(inputstring) == str:
        return inputstring
    else:
        return inputstring.__repr__()


ARGS_MAP = {
    "-s": ("ehs", simpleString),
}


def poor_argparse(connection):
    # Funtion used to parse provided args as argparse is not available
    # NB : Return error = False in the dict if arg parsing fails
    arg_list = sys.argv
    # cause the if to short-circuit before second member of 'or' is evaluated to prevent IndexError
    # https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not
    if len(arg_list) == 0:
        return {}
    elif len(arg_list) == 1 or arg_list[1] == "-h":
        cfg_path = "/nokia-conf:configure/system/script-control"
        print_output = [
            policy_name[0]
            for policy_name in connection.running.get(cfg_path)[
                "script-policy"
            ]
        ]
        print(
            """Requires the name of an EHS as input. Valid options are """
            + str(print_output)
        )
        sys.exit()
    else:
        args = {}
        for index, value in enumerate(arg_list):
            if index % 2 == 1 and len(arg_list) != 2:
                assert "-" in value, "This is not a valid CLI flag/option."
                args[ARGS_MAP[value][0]] = ARGS_MAP[value][1](
                    arg_list[index + 1]
                )  # this may throw a IndexError if there is no ind+1
            elif len(arg_list) == 2:
                args["ehs"] = arg_list[1]
        return args


def get_script_results_location(connection, ehs):
    # cfg_path = '/nokia-conf:configure/system/script-control/script-policy[policy-name="%s"][owner="admin"]'%ehs
    # ehs_config = connection.running.get(cfg_path)
    cfg_path = "/nokia-conf:configure/system/script-control"
    all_ehs_cfg = connection.running.get(cfg_path)["script-policy"]
    for policy_name, policy in all_ehs_cfg.items():
        if (
            policy_name[0] == ehs
            or (
                "*" in ehs
                and re.match(
                    ehs.replace(".*", "*").replace("*", ".*"), policy_name[0]
                )
            )
            and policy_name[1] == "admin"
        ):
            return policy["results"].data
    return {}


def main():
    conn = connect(
        host="127.0.0.1", username="admin", port="830", password="admin"
    )
    args = poor_argparse(conn)
    path_to_results = get_script_results_location(conn, args["ehs"])
    # ehs_result_files = uos.listdir(path_to_results)
    # ehs_result_files = c.cli("/file list %s" % path_to_results )
    # individual_files = [('_' + x.split('\n')[0]) for x in ehs_result_files.split(' _')[1:]]
    individual_files = uos.listdir(path_to_results)
    print()  # create some space
    if individual_files:
        print()
        with open(
            path_to_results + individual_files[-1], "r"
        ) as latest_ehs_file:
            print(latest_ehs_file.read())
    conn.disconnect()


if __name__ == "__main__":
    main()
