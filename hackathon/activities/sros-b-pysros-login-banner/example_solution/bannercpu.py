# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.exceptions import ModelProcessingError
from pysros.management import connect


def main():
    try:
        connection_object = connect(
            host="clab-srexperts-pe3",
            username="admin",
            password="password",
            hostkey_verify=False,
        )
    except RuntimeError as runtime_error:
        raise SystemExit(runtime_error)
    except ModelProcessingError as model_proc_error:
        raise SystemExit(model_proc_error)
    except Exception as generic_error:
        raise SystemExit(generic_error)

    data1 = connection_object.running.get(
        "/nokia-state:state/system/oper-name"
    )
    data2 = connection_object.running.get(
        '/nokia-state:state/system/cpu[sample-period="1"]/summary/usage'
    )
    data3 = connection_object.running.get("/nokia-state:state/system/version")
    print(">>>You are connected to device:", data1)
    print(">>>Current cpu-usage = ", data2["cpu-usage"], "%")
    print(">>>System Version = ", data3["version-number"])


if __name__ == "__main__":
    main()
