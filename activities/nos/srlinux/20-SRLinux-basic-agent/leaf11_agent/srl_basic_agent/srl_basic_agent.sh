#!/bin/bash
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


_term (){
    echo "Caught signal SIGTERM !! "
    # When SIGTERM is caught: kill the child process
    kill -TERM "$child" 2>/dev/null
}

function main()
{
    # Associate a handler with signal SIGTERM
    trap _term SIGTERM

	# Set local variables
    local virtual_env="/opt/srlinux/python/virtual-env/bin/activate"
    local main_module="/etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent.py"

    # activate virtual env
    if [ -f "$virtual_env" ]; then
        source "$virtual_env"
    else
        echo "[WARN] Virtualenv not found in $virtual_env — running on default system python environment"
    fi

    # update PYTHONPATH variable with the agent directories and ndk bindings
	export PYTHONPATH="$PYTHONPATH:/usr/lib/python3.11/dist-packages/sdk_protos/:/etc/opt/srlinux/appmgr/srl_basic_agent"

	# start the agent in the background (as a child process)
    python ${main_module} &
	# save its process id
    child=$! 
	# wait for the child process to finish
    wait "$child"

}

# Exec main function
main "$@"
