---
name: mobile-app-designer
description: Design the screens of a mobile app for iOS and Android after Apple's Human Interface Guidelines. iOS comes first, and Android gives the same experience, with a mockup view of each screen that differs. Read the guidelines first and measure Apple's system colors on the simulator. A script makes every color token and tests each contrast pair in light, dark and increased contrast. Category colors come from measured separation. Sample content is made from real files with a license check, and files open in viewers inside the app. The mockup follows /build-mockup, every screen is rendered and looked at, a second model reviews it, and an interactive review page goes to the owner. Use when the user types /mobile-app-designer, or asks for the design, the colors, the theme, the look or the mockup of a mobile app.
---

# /mobile-app-designer: screens that look native and pass every contrast test

`/mobile-app-designer <the app, the screens>` designs the screens of a mobile app. The look follows Apple's Human
Interface Guidelines on iOS and on Android. Every color comes from a measured source or a script, never from memory.
The mockup itself follows `/build-mockup`, so this skill adds what a native app needs on top of that standard.

The method comes from one app mockup of 2026-11-10, with eight screens, four appearances and two widths. Each rule below
exists because breaking it produced a defect in that work.

## 1. Read the guidelines before you choose anything

Apple's pages load their text with a script, so a plain fetch of the page returns no guideline text. Read the JSON
form of each page instead:

```text
https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json
```

Read these pages in full: `color`, `dark-mode`, `accessibility`, `typography` and `materials`. Also read the page of
each component that you draw, for example `tab-bars`, `sheets`, `alerts`, `toggles` and `lists-and-tables`. Save each JSON file with its
SHA-256 and the date read. Cite a rule only with its URL, the date and a verbatim quote. These quotes were read on
2026-11-10 and set the rules of this skill:

- dark-mode: "Prefer the system background colors." "At a minimum, make sure the contrast ratio between colors is
  no lower than 4.5:1." "For custom foreground and background colors, strive for a contrast ratio of 7:1, especially
  in small text."
- color: "make sure to supply light and dark variants, and an increased contrast option for each variant". "Avoid
  using the same color to mean different things." "prefer a monochromatic appearance for toolbars and tab bars".
- accessibility: the minimum control size on iOS is "44x44 pt". "Convey information with more than color alone."
- typography: "SF Pro is the system font in iOS and iPadOS." "don't embed system fonts".
- materials: Liquid Glass is for "controls and navigation elements". "Don't use Liquid Glass in the content layer."

For a rule of Android, read the Android developer page that states it before you cite a number.

## 2. Settle the decisions with the owner

Ask only what the code and the guidelines cannot decide. Record each answer with its date and the owner's words.

1. iOS first, the same experience on Android. This is the owner's standing rule: "Anything we do for ios is going to
   benefit our Android as well. The same user experience". Design each screen and control from the iOS system
   behavior and Apple's guidelines. Then give Android the same experience. Some behavior stays native on each
   platform, for example the system back gesture, the share sheet and the biometric prompt. Section 7 shows each
   such difference.
2. Brand screens and working screens. A brand color fills the welcome and lock screens and the wordmark. The working
   screens use the system backgrounds.
3. The accent. A brand accent needs a darker variant for light mode and an increased-contrast variant for each mode.
4. The categories and their meaning. A category color never doubles as a state color.

## 3. Measure Apple's system colors

Apple does not publish the hex values of its system colors. Resolve them with UIKit on the simulator.
`ios-color-probe.swift` beside this file prints each color for six cases: `light`, `dark`, `dark-elevated`, and the
same three with increased contrast.

```sh
xcrun --sdk iphonesimulator swiftc -target arm64-apple-ios26.0-simulator ios-color-probe.swift -o probe
xcrun simctl boot <device id>
xcrun simctl spawn <device id> "$PWD/probe" > ios-<version>-system-colors.txt
xcrun simctl shutdown <device id>
```

Set the `-target` to the iOS version of the simulator, and name the output file for that version. Run the probe
twice and compare the files. Commit the probe and its output in the app repository, so that the token script reads
only files of the repository.

## 4. Make the tokens with a script

Write one script in the app repository. It reads the probe output and the brand colors, and it writes the token
file. It has three modes:

- `write` computes the tokens and tests every pair. If a pair fails, it writes nothing.
- `check` computes the tokens again. If a pair fails, or if the token file or a token table in the mockup differs from
  the computation, it exits with status 1.
- `select` ranks the sets of category hues (section 5).

The rules of the script:

1. Use the token names of `/build-mockup`, and map the system colors to them. `bg` comes from
   `systemGroupedBackground`, and `surface` from `secondarySystemGroupedBackground`. `raised` and `sheet` come from the
   `dark-elevated` case. `control` comes from `tertiarySystemFill`, `border` from `separator` and `track` from
   `systemFill`. `text` comes from `label`, and `muted` from `secondaryLabel`.
2. Text needs 4.5:1, and 7:1 with increased contrast. A mark (an icon, a dot) needs 3:1. With increased contrast, 4.5:1
   for a mark is a choice of the project. Write it down as one.
3. Composite a translucent color over its ground before you compute a ratio. `secondaryLabel` is translucent, and in
   that mockup it reached 4.5:1 on white only with its opacity raised from 0.60 to 0.76. Raise the opacity only as far
   as the rule needs.
4. If a color fails, move it in OKLCH lightness only, with its hue kept, and cut chroma only as far as the sRGB gamut
   needs. Keep a color that passes as published.
5. Make each tint (an icon tile, a state badge) from the system color as published, 12% over `surface` in light and 16%
   in dark. A tint made from the adjusted color drifts toward pastel. In one test, warning orange and stop red came to
   0.048 apart in OKLab that way, in dark mode with increased contrast. With the tint from the published color, they
   came to 0.071.
6. Give the brand screens their own set, with an increased-contrast variant. In that mockup, gold on the navy card
   measured 5.93:1, under the 7:1 rule.

## 5. Choose the category colors by measurement

1. Take the candidates from the measured system colors. Leave out every hue next to the accent. Also leave out the
   state hues: green, orange and red. If gray marks information, leave it out too.
2. For every set of the needed size, compute the smallest OKLab distance between a category and any other category,
   the accent or a state, in all four appearances. Count only pairs that hold a category, because a pair of two states
   is the same in every set and ranks nothing.
3. Take the set with the largest smallest distance. Write the result and the runner-up into the design note. In that
   mockup, the chosen Apple set measured 0.074. A set with pink measured 0.049, because pink sits next to stop red.
   The Tableau 10 set measured 0.022, because its yellow sits next to a gold accent.
4. Map categories to colors by meaning. The mapping changes no distance.
5. Every tile carries its icon and its word, so color is never the only signal.

The token names of `/build-mockup` can lack a name for a chosen hue. Then add the name to the standard in a pull
request to the kit, and change `/build-mockup` and `/mockup-to-page` together.

## 6. Build the mockup

Follow `/build-mockup`. A native app adds these rules:

- `$target` names the platform choice, for example `native, pending <the decision record>`. `/mockup-to-page` targets
  web frameworks only, so the mockup is the contract, and the translation into Color Sets or a Compose theme follows
  the platform choice.
- The screen state is named `tab`, because the export of the Inkcast tools reads that key.
- The system font stack, `-apple-system, system-ui`. Never embed SF Pro. A brand serif is only for the wordmark.
- Large titles of 34 pt, inset grouped lists, controls of at least 44 pt (or the project's own larger size), and a
  monochromatic tab bar on a translucent surface. The current tab takes the accent.
- A switch that is on uses the good state color. A destructive action uses the stop color, and an alert asks the person before it acts.
- A sheet or an alert sits on a `position: fixed` overlay. An overlay tied to the page height leaves the sheet below
  the first screen.
- Every screen of a mockup with sample data shows a banner that says so.
- No claim that the product cannot prove yet: no word such as "encrypted" or "secure", and no tick mark on a shield
  icon, which reads as "protected".
- A proposed feature gets a dashed outline, a "Proposed" label and a note. Show it in the state that keeps the screen's
  other text true. For example, a proposed password switch on an export sheet stays off while the sheet warns that the
  copy has no protection.
- Draw simple outline icons of your own, as paths. The app uses the platform symbols.

## 7. Show each platform where it differs

1. The artboard has a `platform` switch: `ios` by default, and `android`. It changes only the parts that differ.
2. The export adds `<screen>-android-light.png` and `<screen>-android-dark.png`, only for the screens that differ.
3. The design note has a table with three columns: the screen, what differs, and the source that forces it. A
   source is a platform rule or component that you read, with its URL and a quote. A difference with no source is a
   defect: draw the iOS behavior on both.
4. Typical differences: the biometric prompt, the share sheet, the system back gesture, the volume slider of the
   video player (section 9), and the formatter of file sizes ("KB" on iOS, "kB" on Android).
5. If no source says what a control does, test it on a real device. Of the volume abilities, Apple's MPVolumeView
   page says: "These abilities only work on a device."

## 8. Make the sample content real

1. Each sample item is one real file that a script makes: pictures and video drawn in code, documents and text
   written in code. The file holds no photo of a person and no personal data, and it says that it is a sample.
2. Check the license of every tool that makes content that ships. For example, the macOS license allows the system
   voices only "to create your own original content and projects for your personal, non-commercial use". So a voice
   for a commercial app comes from a voice whose model and training data allow commercial use, or from the owner.
3. Counts and sizes come from the files. A build task records the size of each file, and a test compares it with the
   sample data. CI compares each file in the built app with its source, byte for byte.
4. Some encoders write the time into the file, for example the MP4 header. Then the committed file is the source,
   and the note says so.
5. The mockup shows copies of the real files, made by a script with its commands in the note. It never shows gray
   lines in place of a document.

## 9. Open every file inside the app

Read the guideline page of each viewer first. These quotes were read on 2026-11-10:

- playing-video: "Use the system video player to give people a familiar and convenient experience." "Always display
  video content at its original aspect ratio."
- gestures (the iOS table): double tap, "Zoom in" and "zoom out if already zoomed in". Swipe, "Reveal actions and
  controls", "dismiss views" and "scroll".
- file-management: Quick Look lets people "view them within your app and in some cases interact with them".

The rules:

1. A file opens in a viewer of its kind, inside the app. The app does not hand a file to another app to show it.
2. A picture fits the screen. A pinch zooms, a double tap zooms in and out, and a drag moves a zoomed picture.
3. A video plays in the system player at its original aspect ratio, and starts paused. The volume control is the
   one of the system player on each platform:
   - iOS: the player has a mute button and a slider. The slider shows the system volume. Apple's MPVolumeView page
     says that the slider "moves to reflect the new volume" at a press of the volume buttons. A test on an iPad in
     2026 showed the same. The app draws no slider of its own.
   - Android: the player has the same mute button. The side buttons change the media volume through the system
     panel. Call `setVolumeControlStream(AudioManager.STREAM_MUSIC)` in `onResume()`.
   - Android has no slider in the player. A slider like the iOS one sets the device volume. Android's page on audio
     output says of those methods: "Avoid using them". This is a forced difference of section 7.
4. A PDF shows its real pages in one scroll, with a label that names the page at the top.
5. Text shows in full. Select and copy stay off until the project has a rule for plaintext on the clipboard.
6. A swipe opens the next or the previous file of the list that the viewer came from, in that list's order. Arrows do
   the same for people who cannot swipe, and they name the position, for example "2 of 4 in Travel".
7. The details go to an Info sheet. The app switcher shows a cover, never the file.
8. In the mockup, the viewer screen is exactly as high as the phone, and each viewer scrolls inside itself. A page
   that grows with its content pushes the action bar and the arrows off the screen.
9. Measure the contrast of controls that sit on media over the real frames. Blend the control's ground over the
   brightest pixel under each control, then compute the ratio.

## 10. Render, test and look

1. Render with Inkcast's `scripts/mockups/render.js` and test with its `check.py`, run in place from a clone of
   Inkcast. They carry the PolyForm Shield license, so never copy them into another repository.
   `render.js` does not expand `<dc-import>`, so the phone and tablet frames work only on the canvas. `check.py` opens
   every variant at 390, 820 and 1440 px, which covers the same widths.
2. Take a PNG of each screen at 390 x 844 and 820 x 1180, at device scale 2, in light and dark.
3. Look at every PNG before you send one. After a fix, render every screen again before you send pictures, so that
   no picture shows the state before the fix.
4. Search the source for each claim word, and accept a hit only in the sample banner.

## 11. Publish a review page

Load the `artifact-design` skill, then build one page from the rendered screens:

- Each rendered screen goes into an `iframe` through `srcdoc`, chosen by switches for screen, appearance, contrast and
  size.
- Each button of the mockup carries `data-go="<screen>"`. A small script in each rendered page posts the screen name to
  the review page, so a tap inside the phone moves to the next screen.
- A short list gives the points for the owner's decision, each with its measured number.
- A table shows each category and state color in the four appearances.

Publish it as a private Artifact. Put its link in the issue, never in the repository.

Before the owner approves, a model of another family reviews the mockup, for example Codex at the effort that the owner
names. The brief carries the whole agent report standard (`/agent-report`). It lists each claim to test with its file
and lines, and asks for a fix and a test for each defect. The arbiter rules on each finding. A review by a second
model is not an independent audit, and the record never calls it one.

## 12. Deliver into the repository

- The source canvas (`Main.dc.html`, `Colors.dc.html`, the frames and `canvas.json`), the new token file beside the old
  one, the probe and its output, and the two scripts.
- The exports: one HTML page and the PNGs of each screen, and a PNG of the tokens sheet.
- A design note with the target table, the owner's decisions with their words, the method and results of section 5,
  the points for review, the Android note, the sources with quotes, and the commands that make every file again.
- A progress comment in the issue, with the commit and the link. The issue stays In-Progress until the owner approves
  each screen in writing.

## 13. Write the as-built design document after each approval

The design note of each version is its history, so it stays as it was approved. One more document shows the whole
design as it is now approved: `design/as-built/README.md`. The owner asked for it on 2026-11-10.

1. Update it only after the owner approves a version. It never shows a version that waits for approval.
2. Open it with the approval record: the version, the date, the owner's words and the link to the issue comment.
3. Embed every screen of the approved version, in light and in dark, with the Android picture beside the iOS one where
   they differ. The export script writes this catalogue from the screen list, so it cannot drift from the PNGs.
4. Add the flows as a `/visual` diagram, each component with its states, the tokens, the platform differences with
   their sources, and every decision with the version that made it.
5. Link each version's design note for its history and its sources. Do not edit an approved version's note.
6. Make the files again from the commands of section 12, and look at every embedded picture before the commit.

## Anti-patterns

| Do not | Do |
|---|---|
| Pick hex values from memory or from a search result | Measure them on the simulator, or read them from a page you cite |
| Take a dashboard palette for app categories | Take the platform's system colors and rank the sets by measured separation |
| Lighten a color until it passes, on a tint made from itself | Tint from the published color, and move only the foreground |
| Leave a translucent label untested | Composite it over each ground before the ratio |
| Draw a proposed feature as built | Dashed outline, a "Proposed" label, and the off state |
| Send pictures from before the last fix | Render every screen again, then look, then send |
| Draw only iOS and call it both | Show each platform where it differs, with the source |
| Fill a document with gray lines | Show copies of the real sample files |
| Leave the approved screens only in a review page | Embed every approved screen in the as-built document |
| Ship content from a tool with a personal-use license | Read the license, and use content that allows commercial use |
