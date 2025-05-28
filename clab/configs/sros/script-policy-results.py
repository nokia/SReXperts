# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""
This module contains code designed to run in the on-board interpreter of a
model-driven SR OS node to quickly display text file contents related to
the latest execution of a script policy.

This iteration has some features built in to improve user friendliness.
"""
import sys
import uos
from pysros.management import connect
from pysros.pprint import Table


def summary_table(scripts):
    """Print a table that shows the options in case no choice was found."""
    rows = sorted(scripts.values(), key=lambda item: item[0])
    cols = [(25, "ID"), (62, "Policy Name")]
    width = sum((col[0] for col in cols))
    table = Table(
        "Available script policies",
        columns=cols,
        showCount="defined script policies",
        width=width,
    )
    return table, rows


def get_script_results_location(connection):
    """Get the existing script-policies and corresponding results location
    with a selection node filter."""
    cfg_path = "/nokia-conf:configure/system/script-control/script-policy"
    ehs_results = connection.running.get(cfg_path, filter={"results": {}})
    result = {}
    index = 0
    for k, v in ehs_results.items():
        if str(v["results"]) == "/null":
            continue
        path = str(v["results"]).rsplit("/", 1)[0] + "/"
        result[str(index)] = (index, k[0], path)
        index += 1
    return result


def main():
    """Main function, controlling flow of this script."""
    connection = connect()
    input_id = -1
    input_name = None
    try:
        input_id = str(int(sys.argv[1]))
    except IndexError as _:
        # no input specified, no problem.
        pass
    except ValueError as _:
        # might be a script policy name
        input_name = sys.argv[1]

    found_scripts = get_script_results_location(connection)
    if input_id == -1 and input_name is None:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input("Select the ID of the script to show its latest result: ")

    if input_id == -1:
        entry_found_by_name = [
            entry[0] for entry in found_scripts.values() if entry[1] == input_name
        ]
        if entry_found_by_name:
            input_id = str(entry_found_by_name[0])
        else:
            input_id = input_name

    while not input_id in found_scripts:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input(
            "The chosen ID '%s' was not found, please input an ID from the table above or 'quit': "
            % input_id
        )
        if input_id == "quit":
            return

    results_file_location = found_scripts[input_id][2]
    files = [""]
    try:
        files = uos.listdir(results_file_location)
        if not files:
            print("Directory %s contains no files." % results_file_location)
            return
        with open(results_file_location + files[-1], "r+") as f:
            print(
                ">>> Showing output for script policy %s from %s\n"
                % (found_scripts[input_id][1], results_file_location + files[-1])
            )
            print(f.read())
    except ValueError as _:
        print("Couldn't find the file at %s" % (results_file_location + files[-1]))

    except OSError as exc:
        print(exc)
        print("The directory %s may not exist." % results_file_location)


if __name__ == "__main__":
    main()
