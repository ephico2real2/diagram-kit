-- Pandoc filter: every figure shows its light render, in both page themes. Use it for a page that people present
-- or print, where a figure must look the same on each screen. Name it after deck.lua, because it reads the HTML
-- that deck.lua writes. Without this filter, a page shows the render that matches the theme of the reader.

local DARK_SOURCE = '%s*<source media="%(prefers%-color%-scheme: dark%)"[^>]*>'
local DARK_IMAGE = '<img class="fig fig%-dark"[^>]*>'

local function light_only(el)
  if el.format ~= "html" then
    return nil
  end
  local text = el.text:gsub(DARK_SOURCE, ""):gsub(DARK_IMAGE, ""):gsub('class="fig fig%-light"', 'class="fig"')
  if text == el.text then
    return nil
  end
  el.text = text
  return el
end

RawInline = light_only
RawBlock = light_only
