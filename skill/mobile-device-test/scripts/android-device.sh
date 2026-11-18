#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Tests an app on one Android device, a real phone or an emulator, with Maestro or maestro-runner.
#
# Usage: android-device.sh <command> --serial <adb serial> [options]
#   state    exit 0 if the device can be used, 3 if not. An emulator can always be used. A real phone must be awake
#            with no lock screen: the script never wakes it and never types its PIN.
#   screen   --package <id> --out <dir>: open the app, save its element tree, print the resource ids
#   flows    --package <id> --require-id <element id> --out <dir> --flows-dir <dir> [--tool maestro|maestro-runner]
#            [--apk <.apk>] [-e KEY=VALUE]... <flow file>...
#   Option   --data-may-be-lost: run with no gate. Use it only when the owner said in chat that the app's data
#            on this device may be lost.
# Exit: 0 pass, 1 a flow failed, 2 a wrong call or a missing tool, 3 the device cannot be used, 4 the gate refused.
#
# The gate is the one of ios-device.sh: the run starts only if the app's first screen shows --require-id.
# Compose test tags are resource ids only when the app sets testTagsAsResourceId, as Maestro's `id:` needs too.
set -euo pipefail

die() { local code=$1; shift; printf '%s android-device: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit "$code"; }
log() { printf '%s android-device: %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }

command=${1:-}; [[ -n "$command" ]] || die 2 "usage: android-device.sh state|screen|flows --serial <serial> ..."
shift
serial='' package='' require='' out='' flows_dir='' apk='' tool=maestro unsafe=0
envs=() flows=()
while (($#)); do
  case "$1" in
    --serial) serial=$2; shift 2 ;;
    --package) package=$2; shift 2 ;;
    --require-id) require=$2; shift 2 ;;
    --out) out=$2; shift 2 ;;
    --flows-dir) flows_dir=$2; shift 2 ;;
    --apk) apk=$2; shift 2 ;;
    --tool) tool=$2; shift 2 ;;
    -e) envs+=(-e "$2"); shift 2 ;;
    --data-may-be-lost) unsafe=1; shift ;;
    -*) die 2 "unknown option $1" ;;
    *) flows+=("$1"); shift ;;
  esac
done
[[ -n "$serial" ]] || die 2 "--serial is required"
if ! command -v adb >/dev/null && [[ -n "${ANDROID_HOME:-}" ]]; then export PATH="$ANDROID_HOME/platform-tools:$PATH"; fi
command -v adb >/dev/null || die 2 "adb not found: set ANDROID_HOME or put platform-tools on PATH"
export MAESTRO_RUNNER_NO_TELEMETRY=1
a() { adb -s "$serial" "$@"; }
need() { for name in "$@"; do [[ -n "${!name}" ]] || die 2 "--${name//_/-} is required for $command"; done; }

device_state() {
  [[ "$(a get-state 2>/dev/null)" == device ]] || { log "$serial is not connected"; return 3; }
  if [[ "$(a shell getprop ro.kernel.qemu | tr -d '\r')" == 1 ]]; then log "$serial is an emulator"; return 0; fi
  local power keyguard
  power=$(a shell dumpsys power | grep -o 'mWakefulness=[A-Za-z]*' | head -1)
  keyguard=$(a shell dumpsys window | grep -o 'isKeyguardShowing=[a-z]*' | head -1)
  log "$serial is a real device: $power $keyguard"
  [[ "$power" == mWakefulness=Awake && "$keyguard" == isKeyguardShowing=false ]] || return 3
}

read_screen() {
  mkdir -p "$out"
  a shell monkey -p "$package" -c android.intent.category.LAUNCHER 1 > "$out/launch.log" 2>&1 \
    || die 2 "cannot open $package: $(tail -1 "$out/launch.log")"
  sleep 3
  a exec-out uiautomator dump /dev/tty > "$out/screen.xml" 2>/dev/null || die 2 "cannot read the screen of $serial"
}

gate() {
  if ((unsafe)); then log "gate skipped: --data-may-be-lost"; return; fi
  read_screen
  grep -qF "resource-id=\"$require\"" "$out/screen.xml" \
    || die 4 "the first screen has no element $require, so the app can hold data. Nothing ran. Saved: $out/screen.xml"
  log "gate passed: the first screen shows $require"
}

case "$command" in
  state)
    device_state || exit 3 ;;
  screen)
    need package out
    device_state || exit 3
    read_screen
    grep -o 'resource-id="[^"]*"' "$out/screen.xml" | sort -u ;;
  flows)
    need package require out flows_dir
    ((${#flows[@]})) || die 2 "name at least one flow file of --flows-dir"
    mkdir -p "$out"
    device_state || exit 3
    if [[ -n "$apk" ]]; then
      a install -r -t "$apk" > "$out/install.log" 2>&1 || die 2 "the install failed: $(tail -2 "$out/install.log")"
      log "installed $apk"
    fi
    gate
    paths=(); for flow in "${flows[@]}"; do paths+=("$flows_dir/$flow"); done
    rc=0
    case "$tool" in
      maestro)
        "${MAESTRO:-maestro}" --device "$serial" test ${envs[@]+"${envs[@]}"} "${paths[@]}" > "$out/flows.log" 2>&1 || rc=$? ;;
      maestro-runner)
        "${MAESTRO_RUNNER:-maestro-runner}" --platform android --device "$serial" --no-ansi \
          test ${envs[@]+"${envs[@]}"} --test-output-dir "$out/run" "${paths[@]}" > "$out/flows.log" 2>&1 || rc=$? ;;
      *) die 2 "--tool is maestro or maestro-runner, not $tool" ;;
    esac
    log "$tool exit=$rc, log $out/flows.log"
    exit $((rc ? 1 : 0)) ;;
  *) die 2 "unknown command $command" ;;
esac
