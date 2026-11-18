#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Runs a command against an iOS simulator of this job's own, made new or erased first, and removes it after.
#
# Usage: ios-sim.sh --name <name> --type <device type> --runtime <runtime id> [--app <.app>] [--reuse] [--keep]
#                   -- <command>...
#   --reuse  a simulator with this name exists already and belongs to this job: erase it instead of making one
#   --keep   keep the simulator after the command (shut down, not deleted)
# The command runs with SIMULATOR_UDID set. The exit status is the command's, or 2 for a setup failure.
#
# A job never uses a simulator by a name that another job or a person uses: the script refuses a name that exists,
# unless --reuse says that it is this job's. Example of the values:
#   --type "iPad Air 11-inch (M4)" --runtime com.apple.CoreSimulator.SimRuntime.iOS-26-5
# `xcrun simctl list devicetypes` and `xcrun simctl list runtimes` print the values of this Mac.
set -euo pipefail

die() { printf '%s ios-sim: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit 2; }
log() { printf '%s ios-sim: %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }

name='' type='' runtime='' app='' reuse=0 keep=0
while (($#)); do
  case "$1" in
    --name) name=$2; shift 2 ;;
    --type) type=$2; shift 2 ;;
    --runtime) runtime=$2; shift 2 ;;
    --app) app=$2; shift 2 ;;
    --reuse) reuse=1; shift ;;
    --keep) keep=1; shift ;;
    --) shift; break ;;
    *) die "unknown option $1" ;;
  esac
done
(($#)) || die "usage: ios-sim.sh --name <name> --type <type> --runtime <id> [options] -- <command>..."
[[ -n "$name" ]] || die "--name is required"
command -v xcrun >/dev/null || die "xcrun not found: this needs macOS with Xcode"

# The UDIDs of the simulators with exactly this name.
udids=$(xcrun simctl list devices -j | python3 -I -c '
import json, sys
name = sys.argv[1]
for runtime, devices in json.load(sys.stdin)["devices"].items():
    for device in devices:
        if device["name"] == name:
            print(device["udid"])' "$name")
count=$(grep -c . <<<"$udids" || true)
created=0
if ((count > 1)); then
  die "$count simulators are named $name: remove the extra ones by hand"
elif ((count == 1)); then
  ((reuse)) || die "a simulator named $name exists: give --reuse if it is this job's, or choose another name"
  udid=$udids
  xcrun simctl shutdown "$udid" 2>/dev/null || true
  xcrun simctl erase "$udid" || die "cannot erase $name"
  log "erased $name ($udid)"
else
  [[ -n "$type" && -n "$runtime" ]] || die "--type and --runtime are required to make $name"
  udid=$(xcrun simctl create "$name" "$type" "$runtime") || die "cannot make $name"
  created=1
  log "made $name ($udid)"
fi

cleanup() {
  xcrun simctl shutdown "$udid" 2>/dev/null || true
  if ((created && !keep)); then xcrun simctl delete "$udid" && log "deleted $name"; fi
}
trap cleanup EXIT

xcrun simctl boot "$udid" || die "cannot boot $name"
xcrun simctl bootstatus "$udid" -b > /dev/null || die "$name did not finish its boot"
if [[ -n "$app" ]]; then
  [[ -d "$app" ]] || die "no app at $app"
  xcrun simctl install "$udid" "$app" || die "the install failed on $name"
  log "installed $app"
fi

rc=0
SIMULATOR_UDID=$udid "$@" || rc=$?
log "command exit=$rc on $name"
exit "$rc"
