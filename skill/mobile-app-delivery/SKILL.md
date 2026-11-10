---
name: mobile-app-delivery
description: Deliver a new mobile app end to end on the approved standards, with no interruption between the owner's gates. The work goes from one round of questions to research, decisions, diagrams, design, backlog, repositories, CI, tested builds and a build on the owner's phone. Each step uses a kit skill. Use when the user types /mobile-app-delivery, or asks to build or deliver a new mobile app end to end.
---

# /mobile-app-delivery: a new mobile app from the idea to the owner's phone

`/mobile-app-delivery <the app>` builds a new mobile app end to end. The owner asks once, and the work continues without
questions until a gate in section 1. Each step uses a skill of this kit, so the app follows the same standards as the
other work of the owner. The owner asked for this on 2026-11-10, so that the work goes on "without me getting in your
way".

## The first app sets the standard

The first app on this skill is a local-first app with no backend and no API service. Local-first means that the data
lives on the phone. That app uses only the platform ecosystem: the files, the key store, the media players and the
viewers of iOS and Android. The App Store and Google Play are its only outside services: they deliver the app and
sell it. Its Android build asks for no INTERNET permission. It went from research to a debug build on the owner's
phone on 2026-11-09 and 2026-11-10.

1. Each lesson of the first app comes back into this skill as a pull request to the kit.
2. Later apps can have full backend services. On 2026-11-10 the owner named Inkcast, an app of the owner with full
   backend services, as their model. Before you plan a backend, read the decision records and the delivery rules of
   Inkcast.
3. No mobile app with a backend used this skill yet, so the backend steps are a plan. Each one says so. The first
   mobile app with a backend proves them, and its lessons replace the plan.
4. Start each new app from the steps of the first app. If the app needs a service, add the backend steps.

## 1. Work on your own, except at the gates

Decide, record the decision with its reason, and continue. Stop and ask the owner only at these gates:

1. Money, or an account that costs money or holds the owner's identity: a store account, a paid service, a domain.
2. A credential, a secret, or a change of a permission, a policy or a ruleset on the owner's accounts.
3. A license for shipped code or content. A permissive license that you read in full needs no gate.
4. Security that protects real data: production cryptography, key storage, and any claim that the app is secure.
5. A change of a decision that the owner approved: a decision record, an approved mockup, or a gate.
6. A check that fails three times with three different fixes.

At intake the owner can keep more gates or give some away, for example the approval of the mockup. Record the list.

The owner approves the first mockup of the app by default. Later mockups follow the gate list.

A merge needs no question. Merge a pull request once local CI passed on a clean clone and every required GitHub check
passed. Then record it.

## 2. Intake: one round of questions

Ask these together, once, with `AskUserQuestion`. Give a recommended answer for each, so that the owner can accept
them all at once.

1. The purpose of the app, its users and the one job of its first version.
2. The brand: the name, the colors and the wordmark, or "choose for me".
3. The data that the app keeps, and where it lives: only on the phone, in a cloud service, or both.
4. The GitHub owner, and the name and visibility of each repository.
5. The phone for test builds, by its Tailscale device name.
6. The gate list of section 1, with any change.

Write the answers with the owner's words and the date into a charter document in the first repository. Then do not
ask again.

## 3. Research the stack as it is used now

1. Search the web, and add the current year to each query, for example "Kotlin Multiplatform vs Flutter 2026". Search
   also for what other developers do. Open and read each page before you cite it. A search summary is not a source.
2. Run the research as background agents. Each brief carries the whole report standard of `/agent-report`, names its
   findings folder under `/workbench`, and holds one topic group. Run heavy agents one at a time.
3. For every app, research the platform ecosystem:
   - The app platform: native screens on a shared Kotlin module, Flutter, or React Native.
   - Storage on the phone, and the key store of each system.
   - The system components that the app uses, for example the video player, the PDF view and the share sheet.
   - Accessibility, privacy rules of each store, and the size of the app.
   - The build tools and the CI runners for iOS and Android.
   - The store services: test tracks, the release steps, and the store billing if the app sells anything.
4. If the app needs a service, also research the backend topics. Start from the decisions of Inkcast:
   - A managed service or an own API, and its hosting and cost.
   - Sign-in, sync, offline use and push messages.
   - Monitoring, and privacy of the data on the server.
5. Compare the options in a table with a cited fact or a measured number in each cell. Put a proposal that no source
   supports in the recommendations, marked as such.
6. If two options stay close, build a small spike of each and measure it: build time, app size, a screen with a search
   field, and the native features that the app needs.
7. For each external API that the app calls, plan a stand-in with `/mock-app`.

## 4. Decide, and draw the decisions

1. Write one decision record for each choice: the platform, storage, the repository layout and CI. An app with a
   service adds the backend and sign-in. Each record names the options, the measured facts and the reason.
2. If the app has a service, review the backend with `/app-architect`.
3. If the app keeps personal data, write a threat model before any code that touches that data.
4. Draw with `/visual`: the system and its trust boundaries, the data flow, and the CI/CD pipeline. Embed each figure
   as its light PNG in the document that explains it.

## 5. Design the screens

Use `/mobile-app-designer`, on top of `/build-mockup`. iOS comes first, and Android gives the same experience. The
mockup shows each platform where the two differ, and every sample file is real. A model of another family reviews the
mockup before the owner sees it. The owner approves the mockup at the gate of section 1.

## 6. Plan the work

1. Make the milestone, the epic and the stories with `/agile`, `/epic` and `/issue`. Each acceptance criterion names
   the test that shows it: a unit test, a device flow or a screenshot.
2. Start the tracker with `/build-tracker` and the note with `/handover` on the first day. Update both after each step.
3. Give each issue its work tag, and move it with evidence.

## 7. Make the repositories and CI

1. Keep every clone and worktree under `/workbench`.
2. Create each repository with `gh repo create`, private unless the owner chose otherwise.
3. Protect `main` with a ruleset: a pull request, the required checks, no force push and no deletion.
4. Write the CI scripts in the repository, for example `ci/android.sh` and `ci/ios.sh`, and run them from the
   workflow. Pin each action to a commit SHA. Check the checksum of each downloaded tool.
5. The jobs: the Android build with its tests and lint, the iOS simulator build with its tests, a secret scan of the
   new commits, and a check that the generated files match their source.
6. Run the same jobs before each push, on a clean clone, with `ci/local.sh`. Jobs that run on Linux can also run under
   `/setup-local-ci`. A macOS job cannot run in a Linux container, so `ci/local.sh` runs it on the Mac itself.
7. If the app has a service, CI builds its image, pushes it with an immutable tag, and deploys it by its digest
   (`/registry-first`). No mobile app proved this step yet.

## 8. Build each story

1. One branch and one pull request for each story.
2. Write the test first. Show that it fails without the change and passes with it. A mutation that the tests do not
   catch is a gap in the tests.
3. Run the device flows on the Android emulator and the iOS simulator, and look at every screenshot against the
   mockup. A flow passes only after one full run with no failed and no skipped step.
4. Update the README where a reader looks for the change.
5. Handle each defect with `/fix-defect`. Give a change that touches security, money or data an adversarial review
   with `/adversarial-review` or `/codex-arbiter`.
6. Run local CI on a clean clone, push, and open the pull request with `/pull-request`. If every check passes, merge.
7. Close the story with its evidence: the merge, the CI run, the test counts and the screenshots.

## 9. Put the app on the owner's phone

1. Android: build the debug APK from `main`. Wait until `tailscale status` shows the phone, then send the file with
   `tailscale file cp <apk> <device>:`. Give the owner its SHA-256 and the install steps.
2. iOS: a build on an iPhone needs the owner's Apple developer account, which is a gate. Until then, the iOS app runs
   on the simulator.
3. Turn what the owner reports from the phone into issues. Each report is a fact about the app.

## 10. Keep the records true

1. The tracker and the note change with each step, so that a restart loses nothing (`/resume-work`).
2. A status page for others comes from `/delivery-page`, and a Word copy from `/document`.
3. Record each owner rule in the charter, with the date and the owner's words.

## 11. Done

The first version is done at the point that each item below holds:

- [ ] Every story of the first milestone is merged, with its tests and screenshots.
- [ ] The app runs on the owner's Android phone from a build of `main`, and on the iOS simulator.
- [ ] CI passes on `main`, and local CI passes on a clean clone.
- [ ] The decision records, the diagrams and the README describe what was built.
- [ ] The tracker shows each unit done with its evidence.
- [ ] Each lesson of the app is in a pull request to this kit.

## Anti-patterns

| Do not | Do |
|---|---|
| Ask the owner a question that the code, a source or a test can answer | Answer it, record it, and continue |
| Choose a stack from memory | Search with the current year, read the sources, and measure close options |
| Add a backend that the app does not need | Use the platform and the stores first, as the first app did |
| Push without local CI on a clean clone | Run `ci/local.sh` on a clean clone, then push |
| Call a pull request done with CI alone and no device flow | Run the flows on both platforms and look at the screenshots |
| Pass a gate of section 1 without the owner | Stop at the gate, ask once, and record the answer |
