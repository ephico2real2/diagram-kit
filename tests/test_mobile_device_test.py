# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tests of the /mobile-device-test scripts, with fake device tools on PATH, so no device is needed."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import shutil
import stat
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "mobile-device-test" / "scripts"

spec = importlib.util.spec_from_file_location("strip_first_launch", SCRIPTS / "strip_first_launch.py")
strip_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strip_module)

FLOW_RESUME = """appId: com.example.app
# A flow that goes on in the running app.
---
- launchApp:
    stopApp: false
- assertVisible:
    id: "home.title"
"""

FLOW_CLEAR = """appId: com.example.app
---
- launchApp:
    clearState: true
- tapOn:
    id: "welcome.start"
"""


def tool(folder: pathlib.Path, name: str, body: str) -> None:
    path = folder / name
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run(script: str, args: list[str], env: dict[str, str], tmp: pathlib.Path) -> subprocess.CompletedProcess:
    full = {"PATH": f"{tmp / 'bin'}:/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(tmp), "CALLS": str(tmp / "calls"), **env}
    return subprocess.run(["bash", str(SCRIPTS / script), *args], capture_output=True, text=True, env=full, timeout=60)


def calls(tmp: pathlib.Path) -> list[str]:
    path = tmp / "calls"
    return path.read_text().splitlines() if path.exists() else []


# strip_first_launch.py


def test_the_copy_drops_a_leading_launch_that_resumes_the_app():
    text, result = strip_module.strip(FLOW_RESUME)
    assert result == "removed"
    assert "launchApp" not in text and text.startswith("appId: com.example.app\n# A flow")
    assert '- assertVisible:\n    id: "home.title"\n' in text


def test_the_copy_keeps_a_launch_that_clears_the_app():
    assert strip_module.strip(FLOW_CLEAR) == (FLOW_CLEAR, "kept")


def test_the_copy_keeps_a_later_resume_and_names_its_line():
    flow = FLOW_CLEAR + "- launchApp:\n    stopApp: false\n- assertVisible: \"Locked\"\n"
    text, result = strip_module.strip(flow)
    assert text == flow
    assert result == "kept warn:7"


def test_the_copy_reads_the_inline_form_and_a_comment_before_the_first_command():
    flow = "appId: x\n---\n# Resume.\n- launchApp: {stopApp: false}\n- back\n"
    text, result = strip_module.strip(flow)
    assert result == "removed" and text == "appId: x\n---\n# Resume.\n- back\n"


def test_the_copy_keeps_the_other_files_and_refuses_a_missing_flow(tmp_path):
    source = tmp_path / "flows"
    source.mkdir()
    (source / "resume.yaml").write_text(FLOW_RESUME)
    (source / "pin.yaml").write_text("appId: x\n---\n- tapOn: \"1\"\n")
    out = tmp_path / "copy"
    script = str(SCRIPTS / "strip_first_launch.py")
    ok = subprocess.run(["python3", "-I", script, str(source), str(out), "resume.yaml"], capture_output=True, text=True)
    assert ok.returncode == 0 and ok.stdout == "resume.yaml: removed\n"
    assert (out / "pin.yaml").read_text() == (source / "pin.yaml").read_text()
    assert (source / "resume.yaml").read_text() == FLOW_RESUME
    bad = subprocess.run(["python3", "-I", script, str(source), str(out), "gone.yaml"], capture_output=True, text=True)
    assert bad.returncode == 2 and "gone.yaml" in bad.stderr
    usage = subprocess.run(["python3", "-I", script], capture_output=True, text=True)
    assert usage.returncode == 2 and usage.stderr.startswith("Usage: strip_first_launch.py <flow folder>")


# ios-device.sh


@pytest.fixture
def ios(tmp_path):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    flows = tmp_path / "flows"
    flows.mkdir()
    (flows / "resume.yaml").write_text(FLOW_RESUME)
    tool(bin_, "xcrun", """echo "xcrun $*" >> "$CALLS"
case "$*" in
  *lockState*) if [ "$FAKE_LOCKED" = 1 ]; then echo '• passcodeRequired: true'; else echo '• passcodeRequired: false'; fi ;;
esac
""")
    tool(bin_, "maestro-runner", """case "$*" in
  --version) echo "maestro-runner $FAKE_VERSION"; echo "  Commit:  0" ;;
  *hierarchy*) echo "  Button  id=$FAKE_SCREEN_ID  text=\\"Start\\"" ;;
  *) echo "maestro-runner $* telemetry=$MAESTRO_RUNNER_NO_TELEMETRY agent=$DEVICELAB_IOS_AGENT_BUNDLE_ID" >> "$CALLS"; exit "${FAKE_RC:-0}" ;;
esac
""")
    tool(bin_, "xcodebuild", 'echo "xcodebuild $*" >> "$CALLS"; echo "Executed 3 tests, with 0 failures"; exit "${FAKE_RC:-0}"\n')
    tool(bin_, "sleep", "exit 0\n")
    return tmp_path


def ios_flows(tmp: pathlib.Path, **env: str) -> subprocess.CompletedProcess:
    args = ["flows", "--device", "UDID-1", "--bundle", "com.example.app", "--team-id", "TEAM1", "--require-id",
            "welcome.start", "--out", str(tmp / "out"), "--flows-dir", str(tmp / "flows"), "--agent-bundle-id",
            "com.example.agent", "-e", "NAME=iPad", "resume.yaml"]
    return run("ios-device.sh", args, {"FAKE_VERSION": "1.1.29", "FAKE_SCREEN_ID": "welcome.start", **env}, tmp)


def test_a_locked_ios_device_runs_nothing(ios):
    result = ios_flows(ios, FAKE_LOCKED="1")
    assert result.returncode == 3, result.stderr
    assert not [c for c in calls(ios) if c.startswith("maestro-runner")]


@pytest.mark.parametrize("screen", ["home.title", "welcome.startX", "welcomeXstart"])
def test_the_ios_gate_refuses_a_first_screen_without_the_element(ios, screen):
    result = ios_flows(ios, FAKE_SCREEN_ID=screen)
    assert result.returncode == 4, result.stdout + result.stderr
    assert "Nothing ran" in result.stderr
    assert not [c for c in calls(ios) if c.startswith("maestro-runner")]


def test_an_old_runner_gets_the_copy_and_a_new_runner_the_flows(ios):
    old = ios_flows(ios)
    assert old.returncode == 0, old.stdout + old.stderr
    run_call = [c for c in calls(ios) if c.startswith("maestro-runner")][-1]
    assert f"{ios}/out/flows-copy/resume.yaml" in run_call
    assert "launchApp" not in (ios / "out" / "flows-copy" / "resume.yaml").read_text()
    assert "telemetry=1 agent=com.example.agent" in run_call and "-e NAME=iPad" in run_call
    assert "--team-id TEAM1" in run_call and "--device UDID-1" in run_call
    new = ios_flows(ios, FAKE_VERSION="1.1.31")
    assert new.returncode == 0
    assert f"{ios}/flows/resume.yaml" in [c for c in calls(ios) if c.startswith("maestro-runner")][-1]


def test_a_failed_flow_exits_1_and_skipping_the_gate_needs_its_flag(ios):
    assert ios_flows(ios, FAKE_RC="5").returncode == 1
    args = ["xctest", "--device", "UDID-1", "--bundle", "b", "--team-id", "T", "--require-id", "welcome.start",
            "--out", str(ios / "x"), "--project", "A.xcodeproj", "--scheme", "A", "--only-testing", "AUITests",
            "--data-may-be-lost"]
    result = run("ios-device.sh", args, {"FAKE_VERSION": "1.1.29", "FAKE_SCREEN_ID": "home.title"}, ios)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "gate skipped" in result.stdout
    build = [c for c in calls(ios) if c.startswith("xcodebuild")][-1]
    assert "-destination id=UDID-1" in build and "-only-testing:AUITests" in build and "DEVELOPMENT_TEAM=T" in build


# android-device.sh


@pytest.fixture
def android(tmp_path):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (tmp_path / "flows").mkdir()
    (tmp_path / "flows" / "start.yaml").write_text(FLOW_CLEAR)
    tool(bin_, "adb", """shift 2
echo "adb $*" >> "$CALLS"
case "$*" in
  get-state) echo device ;;
  "shell getprop ro.kernel.qemu") echo "$FAKE_QEMU" ;;
  "shell dumpsys power") echo "  mWakefulness=$FAKE_POWER" ;;
  "shell dumpsys window") echo "  isKeyguardShowing=$FAKE_KEYGUARD" ;;
  "exec-out uiautomator dump /dev/tty") echo "<node resource-id=\\"$FAKE_SCREEN_ID\\" />" ;;
esac
""")
    for name in ("maestro", "maestro-runner"):
        tool(bin_, name, f'echo "{name} $* telemetry=$MAESTRO_RUNNER_NO_TELEMETRY" >> "$CALLS"; exit "${{FAKE_RC:-0}}"\n')
    tool(bin_, "sleep", "exit 0\n")
    return tmp_path


def android_flows(tmp: pathlib.Path, *extra: str, **env: str) -> subprocess.CompletedProcess:
    args = ["flows", "--serial", "S1", "--package", "com.example.app", "--require-id", "welcome.start",
            "--out", str(tmp / "out"), "--flows-dir", str(tmp / "flows"), "-e", "NAME=phone", *extra, "start.yaml"]
    base = {"FAKE_QEMU": "1", "FAKE_POWER": "Awake", "FAKE_KEYGUARD": "false", "FAKE_SCREEN_ID": "welcome.start"}
    return run("android-device.sh", args, {**base, **env}, tmp)


@pytest.mark.parametrize("power,keyguard", [("Dozing", "false"), ("Awake", "true")])
def test_a_real_phone_that_sleeps_or_is_locked_runs_nothing(android, power, keyguard):
    result = android_flows(android, FAKE_QEMU="0", FAKE_POWER=power, FAKE_KEYGUARD=keyguard)
    assert result.returncode == 3
    assert not [c for c in calls(android) if c.startswith("maestro")]
    assert not [c for c in calls(android) if "keyevent" in c or "input" in c]


def test_the_android_gate_and_each_tool(android):
    refused = android_flows(android, FAKE_SCREEN_ID="home.title")
    assert refused.returncode == 4 and not [c for c in calls(android) if c.startswith("maestro")]
    assert android_flows(android).returncode == 0
    assert calls(android)[-1] == f"maestro --device S1 test -e NAME=phone {android}/flows/start.yaml telemetry=1"
    assert android_flows(android, "--tool", "maestro-runner").returncode == 0
    assert calls(android)[-1].startswith("maestro-runner --platform android --device S1 --no-ansi test -e NAME=phone")
    assert android_flows(android, FAKE_RC="1").returncode == 1


# android-avd.sh


@pytest.fixture
def avd(tmp_path):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    tool(bin_, "emulator", """if [ "$1" = -list-avds ]; then printf 'phone-36\\ntablet-36\\n'; exit 0; fi
echo "emulator $*" >> "$CALLS"; touch "$HOME/booted"
""")
    tool(bin_, "adb", """if [ "$1" = devices ]; then
  echo "List of devices attached"
  [ -n "$FAKE_BUSY" ] && printf 'emulator-5580\\tdevice\\n'
  [ -f "$HOME/booted" ] && printf 'emulator-5580\\tdevice\\n'
  exit 0
fi
shift 2
echo "adb $*" >> "$CALLS"
case "$*" in
  "shell getprop sys.boot_completed") [ -f "$HOME/booted" ] && echo 1 ;;
  "emu avd name") echo "${FAKE_NAME:-phone-36}"; echo OK ;;
  "emu kill") rm -f "$HOME/booted" ;;
esac
""")
    tool(bin_, "sleep", "exit 0\n")
    return tmp_path


def avd_run(tmp: pathlib.Path, *command: str, **env: str) -> subprocess.CompletedProcess:
    args = ["--avd", "phone-36", "--port", "5580", "--lock", str(tmp / "lock"), "--log", str(tmp / "logs"), "--", *command]
    return run("android-avd.sh", args, env, tmp)


def test_the_emulator_runs_the_command_and_stops_after(avd):
    result = avd_run(avd, "sh", "-c", 'echo "serial=$ANDROID_SERIAL" >> "$CALLS"; exit 7')
    assert result.returncode == 7, result.stdout + result.stderr
    assert "serial=emulator-5580" in calls(avd)
    assert calls(avd)[-1] == "adb emu kill"
    assert not (avd / "lock").exists() and not (avd / "booted").exists()


def test_the_emulator_refuses_a_busy_port_a_wrong_avd_and_an_unknown_avd(avd):
    busy = avd_run(avd, "true", FAKE_BUSY="1")
    assert busy.returncode == 2 and "already in use" in busy.stderr
    assert not [c for c in calls(avd) if c.startswith("emulator")]
    wrong = avd_run(avd, "sh", "-c", 'echo ran >> "$CALLS"', FAKE_NAME="other")
    assert wrong.returncode == 2 and "not phone-36" in wrong.stderr
    assert "ran" not in calls(avd) and calls(avd)[-1] == "adb emu kill" and not (avd / "lock").exists()
    unknown = run("android-avd.sh", ["--avd", "nope", "--port", "5580", "--", "true"], {}, avd)
    assert unknown.returncode == 2 and "no AVD named nope" in unknown.stderr


# ios-sim.sh


@pytest.fixture
def sim(tmp_path):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    (tmp_path / "sims.json").write_text(json.dumps({"devices": {"rt": [{"name": "Taken", "udid": "U-OLD"}]}}))
    tool(bin_, "xcrun", """echo "xcrun $*" >> "$CALLS"
case "$*" in
  "simctl list devices -j") cat "$HOME/sims.json" ;;
  simctl\\ create*) echo U-NEW ;;
esac
""")
    return tmp_path


def test_a_simulator_of_another_job_is_never_erased(sim):
    result = run("ios-sim.sh", ["--name", "Taken", "--", "true"], {}, sim)
    assert result.returncode == 2 and "--reuse" in result.stderr
    assert not [c for c in calls(sim) if "erase" in c or "boot" in c]


def test_a_new_simulator_runs_the_command_and_is_deleted(sim):
    args = ["--name", "Job-iPad", "--type", "iPad Air", "--runtime", "rt", "--", "sh", "-c", 'echo "udid=$SIMULATOR_UDID" >> "$CALLS"']
    result = run("ios-sim.sh", args, {}, sim)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "udid=U-NEW" in calls(sim)
    assert calls(sim)[-1] == "xcrun simctl delete U-NEW"
    kept = run("ios-sim.sh", args[:-4] + ["--keep", "--", "true"], {}, sim)
    assert kept.returncode == 0 and not calls(sim)[-1].startswith("xcrun simctl delete")
    reused = run("ios-sim.sh", ["--name", "Taken", "--reuse", "--", "true"], {}, sim)
    assert reused.returncode == 0 and "xcrun simctl erase U-OLD" in calls(sim)
    assert "xcrun simctl delete U-OLD" not in calls(sim)


def test_every_script_passes_shellcheck_and_names_no_private_value():
    for path in sorted(p for p in SCRIPTS.iterdir() if p.is_file()):
        text = path.read_text()
        # No home folder and no hardware UDID of a real device (8 hex digits, a dash, 16 hex digits).
        assert "/Users/" not in text and not re.search(r"\b[0-9A-F]{8}-[0-9A-F]{16}\b", text), path
    if not shutil.which("shellcheck"):
        pytest.skip("shellcheck is not installed")
    result = subprocess.run(["shellcheck", "-S", "warning", *map(str, sorted(SCRIPTS.glob("*.sh")))], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout

