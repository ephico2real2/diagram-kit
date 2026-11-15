#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# Checks a Mac for every tool that the device tests of /mobile-device-test need, and prints each one with its
# version and its state. Then it lists the real devices that the Mac can see. It changes nothing.
#
# Usage: check-mac.sh [--android-home <dir>]
# Environment: JAVA_HOME, ANDROID_HOME, MAESTRO_RUNNER (the binary, if it is not on PATH).
# Exit: 0 if every required tool is there, 1 if one is missing or too old.
#
# States: ok, old (works, with a known limit), missing (a required tool), absent (an optional tool).
set -uo pipefail

android_home=${ANDROID_HOME:-}
while (($#)); do
  case "$1" in
    --android-home) android_home=$2; shift 2 ;;
    *) echo "usage: check-mac.sh [--android-home <dir>]" >&2; exit 2 ;;
  esac
done
if [[ -z "$android_home" ]] && command -v brew >/dev/null; then
  android_home="$(brew --prefix 2>/dev/null)/share/android-commandlinetools"
fi

failed=0
row() {  # tool, version, state, note
  printf '%-22s %-34s %-8s %s\n' "$1" "${2:0:34}" "$3" "$4"
  [[ "$3" != missing ]] || failed=1
}
first() { "$@" 2>&1 | head -1; }
# The newer of two dotted versions is the larger; "sort -V" orders them on macOS and Linux.
at_least() { [[ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -1)" == "$2" ]]; }

printf '%-22s %-34s %-8s %s\n' TOOL VERSION STATE NOTE
row macOS "$(sw_vers -productVersion 2>/dev/null) $(uname -m)" ok ""

# Xcode, its command line tools and the simulators
if command -v xcodebuild >/dev/null && xcodebuild -version >/dev/null 2>&1; then
  row Xcode "$(xcodebuild -version | tr '\n' ' ')" ok "selected: $(xcode-select -p)"
  runtimes=$(xcrun simctl list runtimes 2>/dev/null | grep -c '^iOS ')
  if ((runtimes)); then
    # "iOS 26.5 (26.5 - 23F77) - com.apple..." becomes "26.5 (23F77)".
    row "iOS simulator runtime" "$(xcrun simctl list runtimes | sed -n 's/^iOS \([0-9.]*\) ([0-9.]* - \([A-Za-z0-9]*\)).*/\1 (\2)/p' | tr '\n' ' ')" ok ""
  else
    row "iOS simulator runtime" "" missing "xcodebuild -downloadPlatform iOS"
  fi
  row devicectl "$(first xcrun devicectl --version)" ok "real iPhone and iPad"
else
  row Xcode "" missing "install Xcode, then: xcodebuild -runFirstLaunch"
fi

# Java: Maestro needs 17 or later. /usr/bin/java is a stub that prints an error when no JDK is set.
java=${JAVA_HOME:+$JAVA_HOME/bin/java}
java=${java:-java}
jv=$("$java" -version 2>&1 | sed -n 's/.*version "\([0-9][0-9.]*\).*/\1/p' | head -1)
if [[ -z "$jv" ]]; then
  row Java "" missing "brew install openjdk@17; export JAVA_HOME=\$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
elif at_least "$jv" 17; then
  row Java "$jv" ok "${JAVA_HOME:-on PATH}"
else
  row Java "$jv" missing "Maestro needs Java 17 or later"
fi

# Android SDK
adb=$android_home/platform-tools/adb
emulator=$android_home/emulator/emulator
sdkmanager=$android_home/cmdline-tools/latest/bin/sdkmanager
if [[ -x "$adb" ]]; then row platform-tools "$("$adb" version | sed -n 's/^Version //p')" ok "$android_home"
else row platform-tools "" missing "brew install --cask android-commandlinetools; sdkmanager platform-tools"; fi
if [[ -x "$emulator" ]]; then row emulator "$(first "$emulator" -version | sed -n 's/.*version \([0-9.]*\).*/\1/p')" ok ""
else row emulator "" missing "sdkmanager emulator"; fi
if [[ -x "$sdkmanager" ]]; then
  row cmdline-tools "$(sed -n 's/^Pkg.Revision=//p' "$android_home/cmdline-tools/latest/source.properties" 2>/dev/null)" ok "sdkmanager, avdmanager"
  images=$(find "$android_home/system-images" -mindepth 3 -maxdepth 3 -type d 2>/dev/null | sed "s|$android_home/system-images/||" | tr '\n' ' ')
  if [[ -n "$images" ]]; then row "system images" "$(wc -w <<<"$images" | tr -d ' ')" ok "$images"
  else row "system images" "" missing "sdkmanager \"system-images;android-36;google_apis;arm64-v8a\""; fi
  avds=$("$emulator" -list-avds 2>/dev/null | tr '\n' ' ')
  if [[ -n "$avds" ]]; then row AVDs "$(wc -w <<<"$avds" | tr -d ' ')" ok "$avds"
  else row AVDs "" missing "avdmanager create avd -n <name> -k <system image> -d <device>"; fi
else
  row sdkmanager "" missing "brew install --cask android-commandlinetools"
fi

# The test tools
maestro=$(command -v maestro || { [[ -x "$HOME/.maestro/bin/maestro" ]] && echo "$HOME/.maestro/bin/maestro"; })
if [[ -n "$maestro" ]]; then
  if [[ -n "$jv" ]]; then
    row Maestro "$(JAVA_HOME=${JAVA_HOME:-} "$maestro" --version 2>/dev/null | tail -1)" ok "no real iPhone or iPad"
  else
    row Maestro "(needs Java to print it)" ok "no real iPhone or iPad"
  fi
else
  row Maestro "" missing "curl -fsSL \"https://get.maestro.mobile.dev\" | bash"
fi
runner=${MAESTRO_RUNNER:-$(command -v maestro-runner)}
if [[ -n "$runner" && -x "$runner" ]]; then
  rv=$(MAESTRO_RUNNER_NO_TELEMETRY=1 "$runner" --version 2>/dev/null | awk '/^maestro-runner /{print $2; exit}')
  if at_least "$rv" 1.1.30; then row maestro-runner "$rv" ok "real iPhone and iPad"
  else row maestro-runner "$rv" old "before 1.1.30: restarts the app at launchApp stopApp: false"; fi
else
  row maestro-runner "" missing "release from github.com/devicelab-dev/maestro-runner; set MAESTRO_RUNNER"
fi
row python3 "$(first python3 --version | sed 's/Python //')" "$(command -v python3 >/dev/null && echo ok || echo missing)" ""
for optional in xcodegen shellcheck; do
  # xcodegen prints "Version: 2.46.0", shellcheck prints "version: 0.11.0" on its second line.
  if command -v "$optional" >/dev/null; then row "$optional" "$("$optional" --version 2>&1 | sed -n 's/^[Vv]ersion: //p' | head -1)" ok "optional"
  else row "$optional" "" absent "optional: brew install $optional"; fi
done

# The real devices that this Mac can see. Emulators and simulators are not listed here.
echo
echo "Real devices:"
if command -v xcrun >/dev/null; then
  xcrun devicectl list devices 2>/dev/null | awk 'NR > 2 && NF { print "  iOS:     " $0 }'
fi
if [[ -x "$adb" ]]; then
  "$adb" devices -l 2>/dev/null | awk 'NR > 1 && NF && $1 !~ /^emulator-/ { print "  Android: " $0 }'
fi
exit "$failed"
