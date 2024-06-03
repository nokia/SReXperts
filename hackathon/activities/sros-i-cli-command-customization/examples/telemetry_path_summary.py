#!/usr/bin/env python3
# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import sys
from pysros.management import connect
from pysros.pprint import Table
from pysros.exceptions import *


def simple_boolean(_inputstring):
    """Simple function to return True after being called, used to augment
    the Argument classes below. it is meant to be used as a replacement
    for action=store_true in regular argparse
    """
    return True


def simple_string(inputstring):
    """Simple function to return string representation of the argument
    after being called, used to augment the Argument classes below

    :parameter inputstring: The argument passed via sys.argv to be converted
                            to string (if needed) and returned by this function
    :type inputstring: str
    :returns: inputstring as str type
    :rtype: :py:class:`str`
    """
    if isinstance(inputstring, str):
        return inputstring
    return repr(inputstring)


def simple_integer(inputstring):
    """Simple function to return the integer representation of the argument
    after being called, used to augment the Argument classes below

    :parameter inputstring: The argument passed via sys.argv to be converted
                            to an int object and returned by this function
    :type inputstring: str
    :returns: inputstring as int type
    :rtype: :py:class:`int`
    """
    return int(inputstring)


class Argument:
    """Class representing a single CLI argument passed via sys.argv

    :parameter name:    resulting key to be used in the args dictionary to
                        find the value passed for this argument.
    :type name: str
    :parameter parsing_function:    function to be run using the discovered
                                    parameters as input, result of which is
                                    assigned to the variable.
    :type parsing_function: Callable
    :parameter help_text:   Help text to be displayed when needed
    :type help_text: str
    :parameter parameter_modifier:  Number of values to retrieve from
                                    sys.argv to consume for this variable.
    :type parameter_modifier: int
    :parameter default_value:   value assigned by default to ensure args
                                dictionary is always populated.
    :type default_value: Any
    """

    def __init__(
        self,
        _name,
        _parsing_function,
        _help_text,
        _parameter_modifier,
        _default_value,
    ):
        self.name = _name
        self.parsing_function = _parsing_function
        self.help_text = _help_text
        self.parameter_modifier = _parameter_modifier
        self.default_value = _default_value
        self.value = _default_value

    def set_value(self, value):
        """Set the value of this Argument to the passed value parameter
        after it is passed through the object's parsing function.

        :parameter value: The argument passed assigned to the object value
        :type value: Any
        """
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        self.value = self.parsing_function(value)

    def __str__(self):
        return "%*s" % (20, self.help_text)


class ArgumentHelper:
    """Class acting as abstraction layer between sys.argv and a
    collection of Arguments to be returned as a key:value dictionary
    after parsing and processing.

    Intended to be similar to the ArgumentParser class in argparse.
    """

    def __init__(self):
        self.command_help = "watch help/-h"
        self.arg_list_pointer = 0
        self.args = {}

    def add_argument(self, key, arg):
        """Add an argument to the class' internal args dictionary by key
        with value equal to an Argument.

        :parameter key: CLI flag to be used to specifically address the
                        corresponding Argument object
        :type key: str
        :parameter arg: The Argument object being created and made available
        :type arg: :py:class:`Argument`
        """
        self.args[key] = arg

    def send_help(self):
        """Distill a help message similar to what is shown on Linux CLI
        to be shown on the SR OS CLI when an operator enters the command
        without arguments, or with "-h" or "help" as an argument

        :returns:   a printable help message to be displayed on the CLI, using
                    information found in each Argument contained in self.args
        :rtype: str
        """
        help_message = "\nExample: %-*s\nCommand options:\n" % (
            20,
            "watch.py <command to execute/monitor> %s" % (self.help_flags()),
        )
        for flag, arg in self.args.items():
            help_message += " %-*s%s\n" % (10 + len(flag), flag, arg)
        help_message += " %-*s%s" % (
            10 + len("-h"),
            "-h",
            "Display this message.",
        )
        return help_message

    def help_flags(self):
        """Add an argument to the class' internal args dictionary by key
        with value equal to an Argument.

        :returns:   a printable help message to be displayed on the CLI,
                    showing potentially usable flags in shorthand notation,
                    to be included with the result of send_help
        :rtype: str
        """
        flags = "|".join(
            k + (" #" if v.parameter_modifier > 0 else "")
            for k, v in self.args.items()
        )
        return flags

    def handle_argument(self, index, arg_list_skip_path):
        """Handle an argument specified on the CLI by finding the key, using
        the key to find the Argument object, determining how many parameters
        there should be on the CLI and passing those to the Argument's
        set_value call.

        :parameter index:   Current index in the list of CLI arguments being
                            looked at for parsing/processing
        :type key: int
        :parameter arg_list_skip_path: list of CLI arguments
        :type arg: list
        """
        argument_flag = arg_list_skip_path[index]
        self.arg_list_pointer += self.args[argument_flag].parameter_modifier
        self.args[argument_flag].set_value(
            arg_list_skip_path[index + 1: self.arg_list_pointer + 1]
        )
        self.arg_list_pointer += 1

    def parse_argv(self, _arg_list):
        """Add an argument to the class' args dictionary by key with value
        equal to an Argument.

        :parameter _arg_list:   the list of arguments, retrieved from sys.argv
                                by the caller and passed to this function.
        :type arg: list
        :returns:   a dictionary containing the specified Arguments either with
                    default or specific values, or a "helped" flag that
                    terminates the program.
        :rtype: str
        """
        arg_list = _arg_list
        if len(arg_list) == 0:
            return None

        if (len(arg_list) > 1 and (arg_list[1] == "-h" or arg_list[1] == "help")):
            print(self.send_help())
            return {"helped": True}

        result_args = {}
        # Skip the first element, as that is the path (in this case)
        if len(arg_list) > 1 and arg_list[1] == "/":
            # Elements such as
            #     watch /state/system/up-time
            #     watch /nokia-state:state/system/up-time
            # are passed to arg_list with the first '/' in its
            # own entry in the list: undo that.
            #
            # - this also applies to
            # -     /show system information
            # - that appears "/", "show system information"
            # - avoid, lighten the condition on the if-statement above
            arg_list[1] += arg_list[2]
            del arg_list[2]
        arg_list_skip_path = arg_list[1:]

        # ### ###
        # If this command needs a tools/show/state command to start
        # this section is needed. If not provided it can't run.
        # ### ###
        try:
            # parts of show commands that follow a space and start with '-'
            # may cause a problem in execution however no specific examples
            # of this are known
            self.arg_list_pointer = min(
                (
                    index
                    for index, value in enumerate(arg_list_skip_path)
                    if value.startswith("-")
                )
            )
        except ValueError:
            # ValueError: min() arg is an empty sequence
            self.arg_list_pointer = len(arg_list_skip_path)
        result_args["xpath"] = " ".join(
            arg_list_skip_path[: self.arg_list_pointer]
        )
        # ### ###
        # the arguments come after the show command
        # ### ###
        for index, value in enumerate(arg_list_skip_path):
            if self.arg_list_pointer == index:
                try:
                    self.handle_argument(index, arg_list_skip_path)
                except KeyError as error_cli_option:
                    print(
                        '"%s" is not a valid command option. See \n%s'
                        % (error_cli_option, self.send_help())
                    )
                    sys.exit(98)
            else:
                # this parameter or flag was already used - skip
                pass

        intermediary = {v.name: v.value for _, v in self.args.items()}
        intermediary.update(result_args)
        return intermediary


def get_connection(host,username,password):
    try:
        c = connect(
            host=host,
            username=username,
            password=password,
            hostkey_verify=False,
        )
    except Exception as e:
        print("Failed to connect:", e)
        sys.exit(-1)
    return c


# Fuction definition to output a SR OS style table to the screen
def print_grpc_subs_table(rows):

    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [
        (11, "Sub. Id", '^'),
        (68, "Path"),
    ]

    # Initalize the Table object with the heading and columns.
    table = Table("Overview of gRPC subscriptions and their associated paths", cols, showCount='Subscriptions')

    # Print the output passing the data for the rows as an argument to the function.
    table.print(rows)


def get_grpc_subscription_paths(conn):
    grpc_subs = conn.running.get('/nokia-state:state/system/telemetry/grpc/subscription')
    result = {}
    for subscription_identifier, subscription in grpc_subs.items():
        result[subscription_identifier] = list(subscription['path'].keys())
    return result


def main():
    """The main procedure.  The execution starts here."""
    args = ArgumentHelper()
    args.add_argument(
        "-u",
        Argument(
            "username",
            simple_string,
            "Username to authenticate to remote host (-a) with, when executed off-box",
            1,
            "",
        ),
    )
    args.add_argument(
        "-p",
        Argument(
            "password",
            simple_string,
            "Password to authenticate to remote host (-a) with, when executed off-box",
            1,
            "",
        ),
    )
    args.add_argument(
        "-a",
        Argument(
            "hostname",
            simple_string,
            "Remote host to target when running off-box",
            1,
            "",
        ),
    )
    node_handle = None
    if found_arguments := args.parse_argv(sys.argv):
        if "helped" in found_arguments.keys():
            return
        node_handle = get_connection(
            found_arguments["hostname"],
            found_arguments["username"],
            found_arguments["password"]
        )
    information = get_grpc_subscription_paths(node_handle)
    print_grpc_subs_table([ (sub_id,path) for sub_id,paths in information.items() for path in paths ])


if __name__ == "__main__":
    main()
