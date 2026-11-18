---
name: mobile-device-test
description: Test a mobile app on emulators, simulators, real phones and real iPads. The tools are Maestro, maestro-runner, XCTest UI and the Android device tests. It says which tool runs on which device, and gives one script for each target. The scripts find an emulator by its AVD name. They make a simulator with a name of the job. They never type the PIN or passcode of a person's device. A test that can change the app's data runs only after the first screen shows that the app holds none. Use when the user types /mobile-device-test. Also use it to test an app on a device, or to set up Maestro or maestro-runner for devices.
---

# /mobile-device-test: an app on emulators, simulators and real devices

`/mobile-device-test <the app, the devices>` runs the app's UI tests on each device that is asked for, and reports
each result with its log. The scripts are in `scripts/` beside this file. Each script prints `--help`-style usage at
the top of its file, and exits with 2 for a wrong call or a missing tool.

## 1. Which tool runs on which device

| Device | Maestro | maestro-runner | XCTest UI (`xcodebuild test`) | Android device tests (Gradle) |
|---|---|---|---|---|
| Android emulator | Yes | Yes | No | Yes |
| Real Android phone | Yes | Yes | No | Yes |
| iOS simulator | Yes | Yes | Yes | No |
| Real iPhone or iPad | **No** | Yes, through its XCTest agent app | Yes | No |

Maestro refuses a real iOS device. Its changelog for 2.11.0 says: "iOS: stop listing physical iPhones as devices,
and fail attempted runs early with "Physical iOS devices are not yet supported"". The pull request for them
(mobile-dev-inc/Maestro #2856) closed unmerged on 2026-06-15. Maestro 2.12.1 (2026-11-02) lists simulators
only. Read the changelog again before you trust this table, because it changes.

maestro-runner (devicelab-dev/maestro-runner, Apache-2.0) runs the same flow files. On a real iPhone or iPad it
installs an XCTest agent app on the device and drives the app through it.

## 2. Set up the Mac

Run the check first. It changes nothing, prints each tool with its version and state, and lists the real devices
that the Mac can see. If a required tool is missing or too old, it exits with 1.

```sh
scripts/check-mac.sh            # JAVA_HOME, ANDROID_HOME and MAESTRO_RUNNER, if set, choose the tools
```

Install each tool that it marks `missing`. The last column is the version on the reference Mac (macOS 26.5.2,
Apple silicon, 2026-11-15). Each command comes from the vendor's page in the sources.

| Tool | Needed for | Install | Measured |
|---|---|---|---|
| Xcode | iOS builds, simulators, real iOS devices | The App Store or the Apple developer site, then `xcodebuild -runFirstLaunch` | 26.6 (17F113) |
| iOS simulator runtime | iOS simulators | `xcodebuild -downloadPlatform iOS` | iOS 26.5 (23F77) |
| `devicectl` | Real iPhone and iPad | Part of Xcode | 518.33 |
| JDK 17 or later | Maestro, Gradle | `brew install openjdk@17`, then set `JAVA_HOME` (below) | 17.0.21 |
| Android command line tools | `sdkmanager`, `avdmanager` | `brew install --cask android-commandlinetools` | 22.0 |
| Platform tools and emulator | `adb`, emulators | `sdkmanager "platform-tools" "emulator"` | 37.0.1, 37.2.13.0 |
| A system image | Emulators | `sdkmanager "system-images;android-36;google_apis;arm64-v8a"` | API 28, 32, 36 |
| Maestro | Flows on Android and on simulators | `curl -fsSL "https://get.maestro.mobile.dev" \| bash` | 2.12.1 |
| maestro-runner | Flows on every device, real iOS too | A release of devicelab-dev/maestro-runner (below) | 1.1.29 |
| Python 3 | The scripts of this skill | `brew install python` | 3.15.2 |

Then these steps:

1. Make the JDK the one that the tools use. If no JDK is set, the `/usr/bin/java` of macOS only prints "Unable to locate
   a Java Runtime":

   ```sh
   export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
   export ANDROID_HOME="$(brew --prefix)/share/android-commandlinetools"
   ```

2. Accept the Android SDK licenses once: `sdkmanager --licenses`. Google's page says that `sdkmanager` is
   deprecated and names `android sdk` instead. The reference Mac uses `sdkmanager`. Asked for its help, its `android`
   command started an unpack and showed a license text. Read its page before you use it.
3. Make an AVD for each device that the tests need, from an installed system image. The device ids come from
   `avdmanager list device -c`, for example `pixel_9_pro` for a phone and `pixel_tablet` for a tablet:

   ```sh
   avdmanager create avd -n <name> -k "system-images;android-36;google_apis;arm64-v8a" -d pixel_9_pro
   ```

4. Install maestro-runner. Its README gives `curl -fsSL https://open.devicelab.dev/install/maestro-runner | bash`.
   To check what runs, download the release file instead, compare its SHA-256 with the release, and check the
   signature with `codesign -dv` and `spctl -a -vv -t install`. If the binary is not on PATH, set
   `MAESTRO_RUNNER=<path>`. Its `doctor` command checks the Mac for a run.
5. Turn off usage reports of maestro-runner with `MAESTRO_RUNNER_NO_TELEMETRY=1`. Its README names this switch, and
   the scripts set it.
6. Run `scripts/check-mac.sh` again. Every required row must say `ok`. A maestro-runner before 1.1.30 says `old`:
   it works, with the limit of section 9.

## 3. Set up each device

### A real iPhone or iPad

The owner does these steps on the device. The job never does them, and never types the device passcode.

1. Connect the device to the Mac with a cable. If "Trust This Computer" appears on the device, tap Trust.
2. In Xcode, pair the device. Apple's current page says: choose Xcode > Open Developer Tool > Device Hub, select
   the device. If a Pair button appears, click it. The menu name can differ in another Xcode version.
3. Turn on Developer Mode. The switch appears only after the pairing starts, or for a device that was paired
   before. In Settings > Privacy & Security, turn on Developer Mode, and tap Restart in the alert. After the
   restart, swipe up, tap Enable, and enter the device passcode.
4. Turn on Settings > Developer > Enable UI Automation. No Apple page documents this switch. The Appium XCUITest
   driver's setup page names it for UI tests on a real device.
5. If the app does not open and the device names an untrusted developer, trust the developer in Settings >
   General > VPN & Device Management. Apple's support page gives this path for enterprise apps.
6. Run `scripts/ios-device.sh state --device <UDID>`. It must say `unlocked`. Keep the device unlocked and awake
   during the run.

To turn Developer Mode off after the tests, turn off its switch in Settings > Privacy & Security and restart the
device. Xcode then cannot run apps on it until it is on again.

### A real Android phone

The owner does these steps on the phone. macOS needs no USB driver.

1. Turn on Developer options: in Settings > About phone, tap Build number seven times, until "You are now a
   developer!" shows. Other makers put Build number in another place. Google's page lists them.
2. Turn on USB debugging. On Android 9 and later it is in Settings > System > Advanced > Developer options.
3. Connect the phone with a cable. When the phone asks whether to accept the RSA key of the Mac, accept it.
4. For a test over Wi-Fi (Android 11 and later), turn on Wireless debugging in Developer options, and pair the
   phone with a pairing code, as Google's page shows.
5. Run `scripts/android-device.sh state --serial <serial>`. `adb devices -l` names the serial. The phone must be
   awake with no lock screen.

### An emulator or a simulator

- An emulator needs only its AVD. If the app needs a screen lock, set a PIN of the emulator with
  `adb shell locksettings set-pin <PIN>`. That PIN is an emulator value, never a real one.
- A simulator needs only its runtime. Face ID and the passcode sheet are in section 8.

## 4. Rules for every device

1. Use only the devices that the owner gave to the job. Name each one in the report.
2. Find an Android emulator by its AVD name, never by its serial. Serials follow the order of boot, so
   `emulator-5554` can be another job's device. `android-avd.sh` makes sure that the port runs the AVD you asked for.
3. Make your own iOS simulator with a name of the job. Never erase a simulator that another job or a person uses.
   `ios-sim.sh` refuses a name that exists, unless `--reuse` says that it is the job's own.
4. Take a lock folder before a Maestro or adb run on a shared Mac (`--lock` of `android-avd.sh`). `mkdir` is atomic,
   so the folder is the lock. Two Maestro runs on one Mac step on each other.
5. Never run `adb kill-server`, `adb start-server` or `adb reconnect`. Every job uses the same adb server.
6. On a person's device, never type its PIN or passcode, never wake it with key events, and never change a setting.
   If it is locked or asleep, skip it, and report the state that the script printed (exit 3).
7. On a person's device, run nothing that can change the app's data until the gate passes (section 5).
8. When the job ends, stop each emulator that it started, and delete each simulator that it made. The scripts do
   this in their exit trap.
9. Turn off usage reports: `MAESTRO_RUNNER_NO_TELEMETRY=1`. The scripts set it.

## 5. The gate: no test changes a person's data

A flow with `clearState: true` erases the app's data. A UI test that makes a new account or vault replaces the old
one. On a person's device that data can be theirs. So before a run, `ios-device.sh` and `android-device.sh` open the
app and read its first screen. If the element that `--require-id` names is there, they run. An example is the
button of a first launch. Choose an element that only an app with no data shows.

- If the gate refuses (exit 4), nothing ran. The script saves the screen it read. Ask the owner whether the data
  can be lost, or let the owner remove the app.
- `--data-may-be-lost` skips the gate. If the owner said in chat that the app's data on that device can be lost,
  give it. Never give it for another reason.
- After a run, the tests leave their own data. The next run's gate refuses it, which is correct. A data set that a
  run made is test data. The job can remove the app and install it again, and must say so in the report.

## 6. Android emulator

```sh
scripts/android-avd.sh --avd <AVD name> --port 5580 --apk app-debug.apk --lock <shared dir>/locks/maestro-android \
  --log <out dir> -- scripts/android-device.sh flows --serial emulator-5580 --package <app id> \
  --require-id <first-launch id> --out <out dir> --flows-dir maestro -e DEVICE=phone first-run.yaml
```

- Boot one emulator at a time. A port is an even number from 5554 to 5682, and its serial is `emulator-<port>`.
- The emulator boots with `-no-window`, so a run needs no screen.
- An app that needs a screen lock (for a key in the Android Keystore) needs a PIN on the emulator. That PIN is an
  emulator value. Set it with `adb shell locksettings set-pin`, and never use a real PIN.
- For Android device tests in Gradle, run `ANDROID_SERIAL=emulator-<port> ./gradlew connectedAndroidTest` (or the
  project's device task) as the command of `android-avd.sh`.

## 7. Real Android phone

```sh
scripts/android-device.sh state --serial <serial>
scripts/android-device.sh flows --serial <serial> --package <app id> --require-id <first-launch id> --out <dir> \
  --flows-dir maestro --tool maestro first-run.yaml
```

- `state` passes for a real phone only with `mWakefulness=Awake` and `isKeyguardShowing=false`. Ask the owner to
  unlock the phone and keep it awake. Do not wait in a loop.
- `--tool maestro-runner` runs the same flows with maestro-runner.

## 8. iOS simulator

```sh
scripts/ios-sim.sh --name <job>-iPad --type "iPad Air 11-inch (M4)" --runtime com.apple.CoreSimulator.SimRuntime.iOS-26-5 \
  --app build/ios/Build/Products/Debug-iphonesimulator/App.app -- sh -c 'maestro --device "$SIMULATOR_UDID" test maestro/'
```

- A system sheet, for example "Enter iPhone Passcode", belongs to another process. Maestro reads only the app and
  SpringBoard, so `when visible` cannot see the sheet. Tap it at a point of the screen, then type.
- A simulator with no enrolled face shows the passcode sheet, and any code passes. A simulator with an enrolled face
  shows the Face ID sheet instead. Send a face with `xcrun simctl spawn <UDID> notifyutil -p
  com.apple.BiometricKit_Sim.fingerTouch.match` (or the face match) only after you enrolled it.
- A file that a flow picks through the system files picker must be in the Files app first. Its local storage is
  the app group `group.com.apple.FileProvider.LocalStorage` of `com.apple.DocumentsApp`
  (`xcrun simctl get_app_container <UDID> com.apple.DocumentsApp groups`).

## 9. Real iPhone or iPad

### Before the first run

Do sections 2 and 3. Then choose the team and the agent:

1. Use a development team that can sign apps: `--team-id <team>`.
2. If another team took the default agent bundle id, a free team cannot sign it. Then give the agent a bundle id
   of your own team: `--agent-bundle-id <your prefix>.testagent`.

### Run

```sh
scripts/ios-device.sh state  --device <UDID>
scripts/ios-device.sh screen --device <UDID> --bundle <app id> --team-id <team> --agent-bundle-id <id> --out <dir>
scripts/ios-device.sh flows  --device <UDID> --bundle <app id> --team-id <team> --agent-bundle-id <id> \
  --require-id <first-launch id> --out <dir> --flows-dir maestro --app <Debug-iphoneos .app> -e DEVICE=iPad first-run.yaml
scripts/ios-device.sh xctest --device <UDID> --bundle <app id> --team-id <team> --require-id <first-launch id> \
  --out <dir> --project App.xcodeproj --scheme App --only-testing AppUITests
```

`xcrun devicectl list devices` names the device. `devicectl` and maestro-runner both take its hardware UDID.

### Limits measured on a real iPad (iPadOS 26.5)

- maestro-runner 1.1.29 restarts a running app at `launchApp` with `stopApp: false`. An app that locks at each
  start then shows its lock screen. The fix is commit 1628fab, in release 1.1.30. With an older version,
  `ios-device.sh flows` runs a copy of the flows without that first command (`strip_first_launch.py`). It names
  each later `stopApp: false` that it kept.
- A share sheet on an iPad opens as a popover. Its own text is in a remote view that the runner's tree does not
  enter. Prove its contents with a screenshot, and close it with a tap outside the popover.
- `pressKey: home` did not move the app to the background in a measured relock test, while the person's own
  gesture did. Test a timed lock by hand.
- An XCTest screen recording on the device makes an app with a recording cover show that cover. Set the test plan's
  capture to screenshots.
- The system files picker on an iPad has a sidebar ("On My iPad"), not the tab bar of an iPhone. Nothing copies
  test files into the Files app of a real device, so a test that picks a file needs the file there first.
- Touch ID and Face ID need the person's finger or face. A test can wait for them, but cannot give them.

### Build for the device

The build for a real device is signed, so it needs the team: `xcodebuild build -destination 'id=<UDID>'
-allowProvisioningUpdates DEVELOPMENT_TEAM=<team>`. Xcode can reuse the build plan of a failed build. So if a
build failed on a missing dependency, delete `Build/Intermediates.noindex/XCBuildData` of its derived data folder
before the next build.

## 10. The report

For each device: its name, model, OS version and how it was chosen. Then the app build: its commit and its
build type, Debug or Release. Then the tool and its version, and the command. Then the start and end times in UTC, the counts of
passed, failed and skipped tests, and the log path. For each failure, its message and its cause, measured from the log or a screenshot, and the
issue filed for it. Say plainly what was not run and why: a locked device, a refused gate, a limit of section 9.

## Sources

- Maestro changelog, 2.11.0: https://github.com/mobile-dev-inc/Maestro/blob/main/CHANGELOG.md
- Maestro pull request #2856, "feat: Add iOS physical device support", closed unmerged:
  https://github.com/mobile-dev-inc/Maestro/pull/2856
- maestro-runner, its options (`maestro-runner --help`, version 1.1.29) and its releases:
  https://github.com/devicelab-dev/maestro-runner
- maestro-runner commit 1628fab, "launchApp with stopApp: false keeps a running app running", in v1.1.30.
- Apple, "Enabling Developer Mode on a device":
  https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device
- Apple, Managing your simulated and physical devices in Device Hub (pairing, Trust This Computer):
  https://developer.apple.com/documentation/xcode/managing-your-simulated-and-physical-devices-in-device-hub
- Apple, Downloading and installing additional Xcode components (`-downloadPlatform`, `-runFirstLaunch`):
  https://developer.apple.com/documentation/xcode/downloading-and-installing-additional-xcode-components
- Apple Support, Install custom enterprise apps (VPN & Device Management): https://support.apple.com/en-us/118254
- Appium XCUITest driver, device setup (Enable UI Automation):
  https://github.com/appium/appium-xcuitest-driver/blob/master/docs/getting-started/device-setup.md
- Android, Configure on-device developer options: https://developer.android.com/studio/debug/dev-options
- Android, Run apps on a hardware device (USB, Wi-Fi, macOS needs no driver): https://developer.android.com/studio/run/device
- Android, sdkmanager and avdmanager: https://developer.android.com/tools/sdkmanager,
  https://developer.android.com/tools/avdmanager
- Maestro README (Java 17 or higher, the install command): https://github.com/mobile-dev-inc/Maestro
- Apple's developer pages render with JavaScript. A plain fetch gets only the title. Their text is at the same
  path under `https://developer.apple.com/tutorials/data/` with `.json` at the end.
