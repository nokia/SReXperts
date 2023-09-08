#!/usr/bin/env python3
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

 
from pysros.management import connect
from pysros.exceptions import ModelProcessingError


def main():
    try:
        connection_object = connect(
            host="172.20.20.20",
            username="enter_username_here",
            password="enter_password_here",
            hostkey_verify=False,
        )
    except RuntimeError as runtime_error:
        raise SystemExit(runtime_error)
    except ModelProcessingError as model_proc_error:
        raise SystemExit(model_proc_error)
    except Exception as generic_error:
        raise SystemExit(generic_error)
    data = connection_object.running.get("/nokia-state:state/system/oper-name")
    print("You are connected to device:", data)


if __name__ == "__main__":
    main()
