# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# discovering toolbox pod
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
echo "== Discovering toolbox pod =="
TOOLBOX=$(kubectl get pods -n eda-system -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep toolbox | head -1)
echo "Toolbox pod name: '$TOOLBOX'"

SDK_EXERCISE_DIR="${HOME}/eda-sdk-exercise"
mkdir -p "$SDK_EXERCISE_DIR"

# generating SDK (write under /tmp so kubectl cp path is known)
echo "== Generating SDK (this takes a minute) =="
GEN_RESULT=$(kubectl -n eda-system exec "$TOOLBOX" -- sh -c 'cd /tmp && edactl sdk generate --grpc --lazy-imports --language python')
echo "$GEN_RESULT"
SDK_ARCHIVE=$(echo "$GEN_RESULT" | sed -n 's/^Generated python SDK into file //p')
echo "$SDK_ARCHIVE"

if [[ -z "$SDK_ARCHIVE" ]]; then
  echo "Could not parse SDK archive name from generator output." >&2
  exit 1
fi

if [[ "$SDK_ARCHIVE" = /* ]]; then
  REMOTE_ARCHIVE="$SDK_ARCHIVE"
else
  REMOTE_ARCHIVE="/tmp/$(basename "$SDK_ARCHIVE")"
fi

LOCAL_ARCHIVE="${SDK_EXERCISE_DIR}/$(basename "$SDK_ARCHIVE")"

echo "== Copying archive from toolbox pod =="
kubectl cp -n eda-system "${TOOLBOX}:${REMOTE_ARCHIVE}" "$LOCAL_ARCHIVE"

echo "== Removing any previous eda-python-sdk extract =="
find "$SDK_EXERCISE_DIR" -maxdepth 1 -type d -name 'eda-python-sdk*' -exec rm -rf {} + 2>/dev/null || true

echo "== Extracting SDK into ${SDK_EXERCISE_DIR} =="
tar -xzf "$LOCAL_ARCHIVE" -C "$SDK_EXERCISE_DIR"
SDK_TOP=$(tar -tzf "$LOCAL_ARCHIVE" | head -1 | sed 's|^\./||' | cut -d/ -f1)
echo "SDK location: ${SDK_EXERCISE_DIR}/${SDK_TOP}"

rm -f "$LOCAL_ARCHIVE"

# patch the SDK
echo "== Patching SDK =="
"$SCRIPT_DIR/patch_sdk.sh" "$SDK_EXERCISE_DIR/$SDK_TOP"