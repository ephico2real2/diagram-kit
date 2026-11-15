#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Starts one Android emulator by its AVD name, runs a command against it, and stops it again.
#
# Usage: android-avd.sh --avd <name> --port <even port> [--apk <.apk>] [--lock <dir>] [--log <dir>]
#                       [--boot-timeout <s>] -- <command>...
# The command runs with ANDROID_SERIAL=emulator-<port>. The exit status is the command's, or 2 for a setup failure.
#
# Why each rule:
# - The AVD name, not a serial: serials follow the order of boot, so emulator-5554 can be another job's device.
#   The script makes sure that the emulator on the port runs the AVD that was asked for.
# - A port that no device uses: the script refuses a port whose serial is already connected.
# - A lock folder: Maestro and adb tests on one Mac step on each other. mkdir is atomic, so the folder is the lock.
# - It never runs `adb kill-server` or `adb start-server`: other jobs use the same adb server.
set -euo pipefail

die() { printf '%s android-avd: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit 2; }
log() { printf '%s android-avd: %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }

avd='' port='' apk='' lock='' logs=. boot=300
while (($#)); do
  case "$1" in
    --avd) avd=$2; shift 2 ;;
    --port) port=$2; shift 2 ;;
    --apk) apk=$2; shift 2 ;;
    --lock) lock=$2; shift 2 ;;
    --log) logs=$2; shift 2 ;;
    --boot-timeout) boot=$2; shift 2 ;;
    --) shift; break ;;
    *) die "unknown option $1" ;;
  esac
done
(($#)) || die "usage: android-avd.sh --avd <name> --port <even port> [options] -- <command>..."
[[ -n "$avd" ]] || die "--avd is required"
[[ "$port" =~ ^[0-9]+$ ]] && ((port % 2 == 0 && port >= 5554 && port <= 5682)) || die "--port is an even number from 5554 to 5682"
if [[ -n "${ANDROID_HOME:-}" ]]; then export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"; fi
command -v adb >/dev/null && command -v emulator >/dev/null || die "adb or emulator not found: set ANDROID_HOME"
emulator -list-avds | grep -qx "$avd" || die "no AVD named $avd"

serial=emulator-$port
adb devices | grep -q "^${serial}[[:space:]]" && die "$serial is already in use: choose another port"
mkdir -p "$logs"

if [[ -n "$lock" ]]; then
  until mkdir "$lock" 2>/dev/null; do log "waiting for the lock $lock"; sleep 30; done
fi
started=0
cleanup() {
  if ((started)); then
    adb -s "$serial" emu kill >/dev/null 2>&1 || true
    local n=0
    while adb devices | grep -q "^${serial}[[:space:]]" && ((n++ < 60)); do sleep 2; done
  fi
  [[ -z "$lock" ]] || rmdir "$lock" 2>/dev/null || true
}
trap cleanup EXIT

emulator -avd "$avd" -port "$port" -no-window -no-audio -no-snapshot-save > "$logs/emulator-$avd.log" 2>&1 &
started=1
deadline=$((SECONDS + boot))
until [[ "$(adb -s "$serial" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == 1 ]]; do
  ((SECONDS < deadline)) || die "$avd did not boot in $boot s (log: $logs/emulator-$avd.log)"
  sleep 3
done
name=$(adb -s "$serial" emu avd name | head -1 | tr -d '\r')
[[ "$name" == "$avd" ]] || die "$serial runs $name, not $avd"
log "$avd booted on $serial"

if [[ -n "$apk" ]]; then
  adb -s "$serial" install -r -t "$apk" > "$logs/install-$avd.log" 2>&1 || die "the install failed on $avd"
  log "installed $apk"
fi

rc=0
ANDROID_SERIAL=$serial "$@" || rc=$?
log "command exit=$rc on $avd"
exit "$rc"
