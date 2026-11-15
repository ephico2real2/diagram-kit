#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Tests an app on a real iPhone or iPad: Maestro flows through maestro-runner and its XCTest agent, or the app's
# XCTest UI tests through xcodebuild. Maestro itself refuses a real iOS device (Maestro 2.11.0 changelog).
#
# Usage: ios-device.sh <command> --device <UDID> [options]
#   state    exit 0 if the device is unlocked, 3 if it is locked or cannot be reached
#   screen   --bundle <app id> --out <dir>: open the app, save its element tree, print the element ids
#   flows    --bundle <id> --team-id <team> --require-id <element id> --out <dir> --flows-dir <dir>
#            [--app <.app>] [--agent-bundle-id <id>] [-e KEY=VALUE]... <flow file>...
#   xctest   --bundle <id> --team-id <team> --require-id <element id> --out <dir> --project <.xcodeproj>
#            --scheme <scheme> [--test-plan <name>] [--only-testing <target>]... [--app <.app>]
#   Option   --data-may-be-lost: run with no gate. Use it only when the owner said in chat that the app's data
#            on this device may be lost.
# Exit: 0 pass, 1 a test failed, 2 a wrong call or a missing tool, 3 the device is locked, 4 the gate refused.
#
# The gate: flows with `clearState` and UI tests that make a new vault, account or profile change the app's data.
# On a person's device that data can be theirs. So before a run, the script opens the app and reads its first
# screen, and runs only if the element of --require-id is there (for example the button of a first launch).
set -euo pipefail

die() { local code=$1; shift; printf '%s ios-device: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit "$code"; }
log() { printf '%s ios-device: %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }
here=$(cd "$(dirname "$0")" && pwd)

command=${1:-}; [[ -n "$command" ]] || die 2 "usage: ios-device.sh state|screen|flows|xctest --device <UDID> ..."
shift
device='' bundle='' team='' require='' out='' flows_dir='' app='' agent='' project='' scheme='' plan='' unsafe=0
envs=() only=() flows=()
while (($#)); do
  case "$1" in
    --device) device=$2; shift 2 ;;
    --bundle) bundle=$2; shift 2 ;;
    --team-id) team=$2; shift 2 ;;
    --require-id) require=$2; shift 2 ;;
    --out) out=$2; shift 2 ;;
    --flows-dir) flows_dir=$2; shift 2 ;;
    --app) app=$2; shift 2 ;;
    --agent-bundle-id) agent=$2; shift 2 ;;
    --project) project=$2; shift 2 ;;
    --scheme) scheme=$2; shift 2 ;;
    --test-plan) plan=$2; shift 2 ;;
    --only-testing) only+=("-only-testing:$2"); shift 2 ;;
    -e) envs+=(-e "$2"); shift 2 ;;
    --data-may-be-lost) unsafe=1; shift ;;
    -*) die 2 "unknown option $1" ;;
    *) flows+=("$1"); shift ;;
  esac
done
[[ -n "$device" ]] || die 2 "--device is required"
command -v xcrun >/dev/null || die 2 "xcrun not found: this needs macOS with Xcode"

# maestro-runner sends usage data unless this is set.
export MAESTRO_RUNNER_NO_TELEMETRY=1
[[ -z "$agent" ]] || export DEVICELAB_IOS_AGENT_BUNDLE_ID="$agent"
runner=${MAESTRO_RUNNER:-maestro-runner}

device_state() {
  local info
  info=$(xcrun devicectl device info lockState --device "$device" 2>&1) || { log "$info"; return 3; }
  grep -q 'passcodeRequired: false' <<<"$info" || { log "the device is locked: $(grep -o 'passcodeRequired: [a-z]*' <<<"$info")"; return 3; }
}

need() { for name in "$@"; do [[ -n "${!name}" ]] || die 2 "--${name//_/-} is required for $command"; done; }

# Opens the app (a cold launch when it is not running) and saves the element tree that maestro-runner reads.
read_screen() {
  mkdir -p "$out"
  command -v "$runner" >/dev/null || die 2 "maestro-runner not found: set MAESTRO_RUNNER or put it on PATH"
  xcrun devicectl device process launch --device "$device" "$bundle" > "$out/launch.log" 2>&1 \
    || die 2 "cannot open $bundle on the device: $(tail -1 "$out/launch.log")"
  sleep 3
  "$runner" --platform ios --device "$device" ${team:+--team-id "$team"} --no-ansi hierarchy --compact \
    > "$out/screen.txt" 2>&1 || die 2 "cannot read the screen: $(tail -1 "$out/screen.txt")"
}

gate() {
  if ((unsafe)); then log "gate skipped: --data-may-be-lost"; return; fi
  read_screen
  # One whole word, so a dot in the id is not a regex wildcard and a longer id does not match.
  awk -v want="id=$require" '{ for (i = 1; i <= NF; i++) if ($i == want) found = 1 } END { exit !found }' \
    "$out/screen.txt" || die 4 "the first screen has no element $require, so the app can hold data. Nothing ran. Saved: $out/screen.txt"
  log "gate passed: the first screen shows $require"
}

install_app() {
  [[ -z "$app" ]] && return
  [[ -d "$app" ]] || die 2 "no app at $app"
  xcrun devicectl device install app --device "$device" "$app" > "$out/install.log" 2>&1 \
    || die 2 "the install failed: $(tail -3 "$out/install.log")"
  log "installed $app"
}

# maestro-runner before 1.1.30 restarts a running app at `launchApp` with `stopApp: false` on a real device.
needs_copy() {
  local version
  version=$("$runner" --version 2>&1 | awk '/^maestro-runner /{print $2; exit}')
  [[ -n "$version" ]] || die 2 "cannot read the maestro-runner version"
  log "maestro-runner $version"
  [[ "$(printf '%s\n1.1.30\n' "$version" | sort -V | head -1)" != 1.1.30 ]]
}

case "$command" in
  state)
    device_state || exit 3
    log "unlocked" ;;
  screen)
    need bundle out
    device_state || exit 3
    read_screen
    # The header of the tree names the device as id=<UDID>; only the elements are listed.
    grep -o 'id=[A-Za-z0-9._-]*' "$out/screen.txt" | grep -vx "id=$device" | sort -u ;;
  flows)
    need bundle team require out flows_dir
    ((${#flows[@]})) || die 2 "name at least one flow file of --flows-dir"
    mkdir -p "$out"
    device_state || exit 3
    install_app
    gate
    run_dir=$flows_dir
    if needs_copy; then
      run_dir="$out/flows-copy"
      python3 -I "$here/strip_first_launch.py" "$flows_dir" "$run_dir" "${flows[@]}" | tee "$out/flows-copy.txt"
    fi
    paths=(); for flow in "${flows[@]}"; do paths+=("$run_dir/$flow"); done
    rc=0
    "$runner" --platform ios --device "$device" --team-id "$team" --no-ansi ${envs[@]+"${envs[@]}"} \
      test --test-output-dir "$out/run" "${paths[@]}" > "$out/flows.log" 2>&1 || rc=$?
    log "flows exit=$rc, log $out/flows.log"
    exit $((rc ? 1 : 0)) ;;
  xctest)
    need bundle team require out project scheme
    mkdir -p "$out"
    device_state || exit 3
    install_app
    gate
    rm -rf "$out/tests.xcresult"
    rc=0
    xcodebuild test -project "$project" -scheme "$scheme" ${plan:+-testPlan "$plan"} \
      -destination "id=$device" -derivedDataPath "$out/derived" -allowProvisioningUpdates DEVELOPMENT_TEAM="$team" \
      -resultBundlePath "$out/tests.xcresult" ${only[@]+"${only[@]}"} > "$out/xctest.log" 2>&1 || rc=$?
    grep -E 'Executed [0-9]+ tests|\*\* TEST' "$out/xctest.log" | tail -2 || true
    log "xctest exit=$rc, log $out/xctest.log"
    exit $((rc ? 1 : 0)) ;;
  *) die 2 "unknown command $command" ;;
esac
