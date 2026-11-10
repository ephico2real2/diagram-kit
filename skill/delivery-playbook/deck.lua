-- Pandoc filter for the deck page. A figure written as figures/<name>.light.png becomes two images, light and dark,
-- and the page CSS shows the one that matches the reader's theme. The .pptx build does not use this filter.

-- The alt text comes from the Markdown, so it is escaped before it goes into an attribute.
local function attr(text)
  return (text:gsub("&", "&amp;"):gsub('"', "&quot;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

local function themed(src, alt)
  local dark = src:gsub("%.light%.png$", ".dark.png")
  alt = attr(alt)
  src = attr(src)
  dark = attr(dark)
  return pandoc.RawInline("html",
    '<img class="fig fig-light" src="' .. src .. '" alt="' .. alt .. '">' ..
    '<img class="fig fig-dark" src="' .. dark .. '" alt="' .. alt .. '">')
end

function Image(img)
  if not img.src:match("%.light%.png$") then
    return nil
  end
  return themed(img.src, pandoc.utils.stringify(img.caption))
end

-- A wide table scrolls inside its own box, so the page never scrolls sideways on a phone.
function Table(tbl)
  return { pandoc.RawBlock("html", '<div class="table-wrap">'), tbl, pandoc.RawBlock("html", "</div>") }
end
