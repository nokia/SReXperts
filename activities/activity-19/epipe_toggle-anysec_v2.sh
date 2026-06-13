#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


# --------------------------------------------------
# Toggle ANYsec on EPipe spoke-SDP (Nokia SR OS)
#
# The script performs:
#   - IF ANYsec is configured on the EPipe spoke-SDP:
#       -> remove it
#   - ELSE:
#       -> configure it with the provided encryption-group
#
# Usage:
#   ./epipe_toggle-anysec_v2.sh \
#     -t clab-srexperts-pe2,clab-srexperts-pe3 \
#     -s Svc-A_Epipe \
#     -e EG_A
#
# Assumptions:
#   - One spoke-SDP per EPipe service
#   - gnmic and jq are installed
# --------------------------------------------------

set -euo pipefail

# ---------- Defaults ----------
USERNAME="admin"
#PASSWORD="NokiaSros1!"
PASSWORD=${EVENT_PASSWORD}

# ---------- Arguments ----------
TARGETS=""
SERVICE_NAME=""
ENCRYPTION_GROUP=""

usage() {
  echo "Usage:"
  echo "  $0 -t <target1,target2,...> -s <service-name> -e <encryption-group>"
  echo
  echo "Options:"
  echo "  -t   Comma-separated list of gNMI targets (e.g.: pe2,pe3)"
  echo "  -s   EPipe service-name (e.g.: Svc-A_Epipe)"
  echo "  -e   ANYsec encryption-group name (e.g.: EG_A or EG_B)"
  exit 1
}

while getopts "t:s:e:h" opt; do
  case "$opt" in
    t) TARGETS="$OPTARG" ;;
    s) SERVICE_NAME="$OPTARG" ;;
    e) ENCRYPTION_GROUP="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

if [[ -z "$TARGETS" || -z "$SERVICE_NAME" || -z "$ENCRYPTION_GROUP" ]]; then
  usage
fi

IFS=',' read -ra TARGET_LIST <<< "$TARGETS"

# ---------- Main loop ----------
for TARGET in "${TARGET_LIST[@]}"; do
  echo "=================================================="
  echo "Target        : $TARGET"
  echo "Service       : $SERVICE_NAME"
  echo "EncryptionGrp : $ENCRYPTION_GROUP"
  echo "--------------------------------------------------"

  # Base gnmic command for this target
  GNMIC_BASE=(
    gnmic
    -a "$TARGET"
    -u "$USERNAME"
    -p "$PASSWORD"
    --insecure
  )

  # --------------------------------------------------
  # Check if ANYsec is currently configured
  # --------------------------------------------------
  if "${GNMIC_BASE[@]}" get \
      --path "/configure/service/epipe[service-name=${SERVICE_NAME}]/spoke-sdp[sdp-bind-id=*]/anysec-encryption-group" \
    | jq -e '
        .[0].updates?
        | map(.values["configure/service/epipe/spoke-sdp/anysec-encryption-group"])
        | any(. != null)
      ' >/dev/null
  then
    # ------------------------------------------------
    # ANYsec is present -> remove it
    # ------------------------------------------------
    echo "-> Original status: ANYsec WAS configured"

    "${GNMIC_BASE[@]}" getset \
      --get "/configure/service/epipe[service-name=${SERVICE_NAME}]/spoke-sdp[sdp-bind-id=*]/anysec-encryption-group" \
      --condition '
        .[0].updates[0].values["configure/service/epipe/spoke-sdp/anysec-encryption-group"] != null
      ' \
      --delete "\"/configure/service/epipe[service-name=${SERVICE_NAME}]/spoke-sdp[sdp-bind-id=*]/anysec-encryption-group\"" \
    && echo "-> New status: ANYsec REMOVED"

  else
    # ------------------------------------------------
    # ANYsec is not present -> configure it
    # ------------------------------------------------
    echo "-> Original status: ANYsec was NOT configured"

    "${GNMIC_BASE[@]}" getset \
      --get "/configure/service/epipe[service-name=${SERVICE_NAME}]/spoke-sdp[sdp-bind-id=*]" \
      --condition '
        .[0].updates[0].values["configure/service/epipe/spoke-sdp/anysec-encryption-group"] == null
      ' \
      --update '
        .[0].updates[0].Path + "/anysec-encryption-group"
      ' \
      --value "\"${ENCRYPTION_GROUP}\"" \
    && echo "-> New status: ANYsec CONFIGURED"
  fi

  echo "Done for $TARGET"
  echo "=================================================="
done

echo "Toggle ANYsec completed for all targets"
