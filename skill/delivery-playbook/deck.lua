-- Pandoc filter for the deck page. A figure written as figures/<name>.light.png becomes one image of class "fig", the
-- light render, which the page shows in every theme: the figures are light only. The .pptx build does not use this
-- filter.

-- The alt text comes from the Markdown, so it is escaped before it goes into an attribute.
local function attr(text)
  return (text:gsub("&", "&amp;"):gsub('"', "&quot;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

function Image(img)
  if not img.src:match("%.light%.png$") then
    return nil
  end
  local alt = attr(pandoc.utils.stringify(img.caption))
  return pandoc.RawInline("html", '<img class="fig" src="' .. attr(img.src) .. '" alt="' .. alt .. '">')
end

-- A wide table scrolls inside its own box, so the page never scrolls sideways on a phone.
function Table(tbl)
  return { pandoc.RawBlock("html", '<div class="table-wrap">'), tbl, pandoc.RawBlock("html", "</div>") }
end
