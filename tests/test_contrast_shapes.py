# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Run the production JavaScript with controlled DOM inputs.

The Playwright package supplies Node. These tests cover shape selection, paint
order and contrast arithmetic. Browser layout remains in test_render_browser.py.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest
from playwright._impl._driver import compute_driver_executable

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contrast_renderer", ROOT / "diagram_kit/render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

HARNESS = r"""
const fs = require('node:fs');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const shapeBox = {left: 0, top: 0, right: 200, bottom: 100};
const textBox = data.outside ? {left: 210, top: 20, right: 260, bottom: 40}
                             : {left: 20, top: 20, right: 80, bottom: 40};
const shape = (tag, fill) => ({tagName: tag, textContent: '', style: {fill},
                              getBoundingClientRect: () => shapeBox});
const text = {tagName: 'text', textContent: 'Label', style: {fill: data.ink},
              getBoundingClientRect: () => textBox};
let elements = [shape(data.tag, data.fill)];
if (data.topFill) elements.push(shape(data.tag, data.topFill));
if (data.after) elements.unshift(text); else elements.push(text);
const figure = {style: {backgroundColor: data.ground},
                querySelectorAll: selector => elements.filter(el => selector.split(/,\s*/).includes(el.tagName))};
global.document = {body: {style: {backgroundColor: data.ground}}, querySelectorAll: () => [figure]};
global.getComputedStyle = el => el.style;
const result = (eval('(' + data.script + ')'))();
process.stdout.write(JSON.stringify(result));
"""


def evaluate(tag, fill="rgb(255, 255, 255)", ink="rgb(255, 255, 255)",
             ground="rgb(0, 0, 0)", **extra):
    node = str(compute_driver_executable()[0])
    data = dict(script=renderer.LOW_CONTRAST, tag=tag, fill=fill, ink=ink, ground=ground, **extra)
    result = subprocess.run([node, "-e", HARNESS], input=json.dumps(data), text=True,
                            capture_output=True, check=True, timeout=10)
    return json.loads(result.stdout)


@pytest.mark.parametrize("gray, expected", [
    (118, []),
    (119, ['figure 1: "Label" at 4.48:1']),
])
def test_the_contrast_limit_stays_between_nearby_gray_backgrounds(gray, expected):
    assert evaluate("rect", fill=f"rgb({gray}, {gray}, {gray})") == expected
