---
name: mobile-app-designer
description: Design the screens of a mobile app for iOS and Android after Apple's Human Interface Guidelines. Read the guidelines first and measure Apple's system colors on the simulator. A script makes every color token and tests each contrast pair in light, dark and increased contrast. Category colors come from measured separation. The mockup follows /build-mockup, every screen is rendered and looked at, and an interactive review page goes to the owner. Use when the user types /mobile-app-designer, or asks for the design, the colors, the theme, the look or the mockup of a mobile app.
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

1. The look on Android. Apple design on both platforms keeps one design. Some behavior stays native on each
   platform: the system back gesture, the share sheet and the biometric prompt.
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
- A switch that is on uses the good state color. A destructive action uses the stop color and opens a confirmation.
- A sheet or an alert sits on a `position: fixed` overlay. An overlay tied to the page height leaves the sheet below
  the first screen.
- Every screen of a mockup with sample data shows a banner that says so.
- No claim that the product cannot prove yet: no word such as "encrypted" or "secure", and no tick mark on a shield
  icon, which reads as "protected".
- A proposed feature gets a dashed outline, a "Proposed" label and a note. Show it in the state that keeps the screen's
  other text true. For example, a proposed password switch on an export sheet stays off while the sheet warns that the
  copy has no protection.
- Draw simple outline icons of your own, as paths. The app uses the platform symbols.

## 7. Render, test and look

1. Render with Inkcast's `scripts/mockups/render.js` and test with its `check.py`, run in place from a clone of
   Inkcast. They carry the PolyForm Shield license, so never copy them into another repository.
   `render.js` does not expand `<dc-import>`, so the phone and tablet frames work only on the canvas. `check.py` opens
   every variant at 390, 820 and 1440 px, which covers the same widths.
2. Take a PNG of each screen at 390 x 844 and 820 x 1180, at device scale 2, in light and dark.
3. Look at every PNG before you send one. After a fix, render every screen again before you send pictures, so that
   no picture shows the state before the fix.
4. Search the source for each claim word, and accept a hit only in the sample banner.

## 8. Publish a review page

Load the `artifact-design` skill, then build one page from the rendered screens:

- Each rendered screen goes into an `iframe` through `srcdoc`, chosen by switches for screen, appearance, contrast and
  size.
- Each button of the mockup carries `data-go="<screen>"`. A small script in each rendered page posts the screen name to
  the review page, so a tap inside the phone moves to the next screen.
- A short list gives the points for the owner's decision, each with its measured number.
- A table shows each category and state color in the four appearances.

Publish it as a private Artifact. Put its link in the issue, never in the repository.

## 9. Deliver into the repository

- The source canvas (`Main.dc.html`, `Colors.dc.html`, the frames and `canvas.json`), the new token file beside the old
  one, the probe and its output, and the two scripts.
- The exports: one HTML page and the PNGs of each screen, and a PNG of the tokens sheet.
- A design note with the target table, the owner's decisions with their words, the method and results of section 5,
  the points for review, the Android note, the sources with quotes, and the commands that make every file again.
- A progress comment in the issue, with the commit and the link. The issue stays In-Progress until the owner approves
  each screen in writing.

## Anti-patterns

| Do not | Do |
|---|---|
| Pick hex values from memory or from a search result | Measure them on the simulator, or read them from a page you cite |
| Take a dashboard palette for app categories | Take the platform's system colors and rank the sets by measured separation |
| Lighten a color until it passes, on a tint made from itself | Tint from the published color, and move only the foreground |
| Leave a translucent label untested | Composite it over each ground before the ratio |
| Draw a proposed feature as built | Dashed outline, a "Proposed" label, and the off state |
| Send pictures from before the last fix | Render every screen again, then look, then send |
