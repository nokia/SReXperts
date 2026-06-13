#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# Patches a fresh copy of the eda-python-sdk so that Authenticator.login()
# succeeds against an EDA server that requires an HTTP Referer header on
# requests to /auth/config.
#
# Usage: ./patch-sdk.sh [path/to/eda-python-sdk]
#   Defaults to ./eda-python-sdk relative to this script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK_DIR="${1:-${SCRIPT_DIR}/eda-python-sdk}"
TARGET="${SDK_DIR}/edasdk/api_client.py"

if [[ ! -f "${TARGET}" ]]; then
    echo "error: cannot find ${TARGET}" >&2
    exit 1
fi

OLD='cfg_resp = self._rest.request("GET", url)'
NEW='cfg_resp = self._rest.request("GET", url, headers={"Referer": base})'

if grep -qF "${NEW}" "${TARGET}"; then
    echo "patch already applied to ${TARGET}"
    exit 0
fi

if ! grep -qF "${OLD}" "${TARGET}"; then
    echo "error: expected line not found in ${TARGET}; SDK may have changed" >&2
    exit 1
fi

python3 - "${TARGET}" "${OLD}" "${NEW}" <<'PY'
import sys, pathlib
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(path)
text = p.read_text()
count = text.count(old)
if count != 1:
    sys.exit(f"error: expected exactly 1 occurrence in {path}, found {count}")
p.write_text(text.replace(old, new))
PY

echo "patched ${TARGET}"
