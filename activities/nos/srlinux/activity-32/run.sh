#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


set -o errexit
set -o pipefail

# abs path to the directory that hosts the run.sh script
BASE_DIR=$(dirname "$(readlink -f "$0")")
APPNAME=inventory
GOPKGNAME=${APPNAME}
BIN_DIR=${BASE_DIR}/build
BINARY=${BASE_DIR}/build/${APPNAME}

GOLANGCI_CMD="sudo docker run -t --rm -v $(pwd):/app -w /app golangci/golangci-lint:v1.60.3 golangci-lint"
GOLANGCI_FLAGS="run -v ./..."

GOIMPORTS_CMD="sudo docker run --rm -it -v $(pwd):/work -w /work ghcr.io/hellt/goimports:v0.25.0"
GOIMPORTS_FLAGS="-w ."

#################################
# Build and lint functions
#################################

function lint-yaml {
	echo "Linting YAML files"
	docker run --rm -v ${BASE_DIR}/${APPNAME}.yml:/data/${APPNAME}.yml cytopia/yamllint -d relaxed .
}

function lint {
	lint-yaml
}

GOFUMPT_CMD="docker run --rm -it -e GOFUMPT_SPLIT_LONG_LINES=on -v ${BASE_DIR}:/work ghcr.io/hellt/gofumpt:v0.7.0"
GOFUMPT_FLAGS="-l -w ."

GODOT_CMD="docker run --rm -it -v ${BASE_DIR}:/work ghcr.io/hellt/godot:1.4.11"
GODOT_FLAGS="-w ."

function gofumpt {
	${GOFUMPT_CMD} ${GOFUMPT_FLAGS}
}

function godot {
	${GODOT_CMD} ${GODOT_FLAGS}
}

function goimports {
	${GOIMPORTS_CMD} ${GOIMPORTS_FLAGS}
}

function format {
	goimports
	gofumpt
	godot
}

function copy-app {
	echo "Copying application to nodes"
	for host in leaf21 spine21; do
		ssh -q admin@clab-srexperts-${host} "bash mkdir -p /home/admin/inventory" || true
		docker cp ./build/inventory clab-srexperts-${host}:/home/admin/inventory/inventory
		docker cp ./yang clab-srexperts-${host}:/home/admin/inventory/yang
		docker cp ./inventory.yml clab-srexperts-${host}:/etc/opt/srlinux/appmgr/inventory.yml
		docker cp ./plugin/show_location.py clab-srexperts-${host}:/etc/opt/srlinux/cli/plugins/show_location.py
	done
}

function reload-app_mgr {
	echo "Reloading application manager"
	for host in leaf21 spine21; do
		ssh -q -o StrictHostKeyChecking=no admin@clab-srexperts-${host} "tools system app-management application app_mgr reload"
	done
}

function start-app {
	echo "Starting NDK application"
	for host in leaf21 spine21; do
		ssh -q -o StrictHostKeyChecking=no admin@clab-srexperts-${host} "tools system app-management application ${APPNAME} start" 1>/dev/null || true
	done
}

function stop-app {
	echo "Stopping NDK application"
	for host in leaf21 spine21; do
		ssh -q -o StrictHostKeyChecking=no admin@clab-srexperts-${host} "tools system app-management application ${APPNAME} stop" 1>/dev/null || true
	done
}

#################################
# App functions
#################################

function build-app {
	lint
	format
	echo "Building application"
	mkdir -p ${BIN_DIR}
	go mod tidy

	if [[ -n "${NDK_DEBUG}" ]]; then
		go build -race -o ${BINARY} -ldflags="${LDFLAGS}" -gcflags="${GCFLAGS}" .
	else
		go build -o ${BINARY} -ldflags="${LDFLAGS}" -gcflags="${GCFLAGS}" .
	fi
}

function deploy-app {
	build-app
	stop-app
    copy-app
	reload-app_mgr
	echo "Waiting for a moment to reload the YANG..."
	sleep 5
	start-app
}

_run_sh_autocomplete() {
	local current_word
	COMPREPLY=()
	current_word="${COMP_WORDS[COMP_CWORD]}"

	# Get list of function names in run.sh
	local functions=$(declare -F -p | cut -d " " -f 3 | grep -v "^_" | grep -v "nvm_")

	# Generate autocompletions based on the current word
	COMPREPLY=($(compgen -W "${functions}" -- ${current_word}))
}

# Specify _run_sh_autocomplete as the source of autocompletions for run.sh
complete -F _run_sh_autocomplete ./run.sh

function help {
	printf "%s <task> [args]\n\nTasks:\n" "${0}"

	compgen -A function | grep -v "^_" | grep -v "nvm_" | cat -n

	printf "\nExtended help:\n  Each task has comments for general usage\n"
}

# This idea is heavily inspired by: https://github.com/adriancooney/Taskfile
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:-help}"
