---
name: delivery-playbook
description: "Make the Delivery Playbook for a client. The playbook is the standard method of review, design, build, test and delivery. It holds the principles, the services, the lifecycle, the review loop and the pipelines for web, API and mobile. It ends with the standard legend. A client copy states what operates today and what is proposed. Markdown first, then a page, a PDF and a .pptx deck. Use when the user types /delivery-playbook. Also use it for a playbook, a methodology or a delivery standard. Use it for the legend and pipeline figures of a new client."
---

# /delivery-playbook: one method for every client, with the facts of each client

`/delivery-playbook <client>` makes a client copy of the Delivery Playbook. The standard text, figures and legend are
in this folder. They hold no firm name and no client data, because this repository is public.

## 1. What is in this folder

| File | What it is |
|---|---|
| `PLAYBOOK.md` | The standard text: 14 sections, from the principles to the legend. Names in angle brackets are placeholders |
| `DECK.md` | The same method as slides, for pandoc to make a `.pptx` |
| `figures/source.html` | The five figures: lifecycle, review loop, local first, web pipeline and mobile pipeline |
| `figures/*.light.png`, `figures/*.dark.png` | The figures, rendered by `diagram-render` |
| `page-head.html` | The style of the page, in the kit palette, with light and dark themes |
| `deck-template.html`, `deck.lua` | The template and the pandoc filter that make the deck page: one card for each slide |

## 2. Make a client copy

1. Copy `PLAYBOOK.md`, `DECK.md`, `page-head.html` and the `figures` PNGs into the client repository, for example
   into `docs/playbook/`.
2. Replace each placeholder in the metadata block: `[Author]`, `[Role]`, `[Firm]`, `[version]` and `[date]`. The firm name goes only into
   the client copy, never back into this folder.
3. Add a last section, "Applied to `<client>`". For each standard row, state what operates today, what is proposed,
   and the source: a file and line, a workflow job, a command, or an issue. A proposal stays a proposal until a test
   proves it.
4. Keep the legend of section 14 unchanged. It equals `skill/agile/LEGEND.md`. A client report opens with the same legend.
5. If a client pipeline differs from figure 4 or 5, draw the client pipeline with `/visual`. Mark each proposed stage
   with a dashed box. Do not change the standard figures.

## 3. Build the page, the PDF and the deck

The Markdown is the source. Each other form is made from it and is never edited by hand.

```sh
# The page: pandoc with the kit style. The figures folder sits beside the page.
# The metadata block at the top gives the title, the subtitle, the byline and the date.
pandoc PLAYBOOK.md --standalone --toc --toc-depth=2 -H page-head.html -o playbook.html
# The deck: one slide for each level-2 heading of DECK.md.
pandoc DECK.md --slide-level=2 -o playbook.pptx
# The deck as a page: one card for each slide, light and dark figures, keyboard arrows. The figures folder sits beside it.
pandoc DECK.md -t html5 --section-divs --lua-filter deck.lua --template deck-template.html \
  -M hint="Use the arrow keys, or scroll. Each card is one slide." -o deck.html
# Look at each slide before it goes out, as the kit README says (LibreOffice and pdftoppm).
soffice -env:UserInstallation=file://$PWD/.lo --headless --convert-to pdf playbook.pptx
pdftoppm -r 50 -png playbook.pdf slide
```

To share the page, publish `playbook.html` with its `figures` folder. A reader saves a PDF from the browser. Check
the page at 375 px, 820 px and 1280 px in both themes before you publish it.

## 4. Rules

- The standard holds no firm name, no client name, no client number and no private host.
- Each statement in a client copy has a source. "Operates" needs a test or a workflow run. Anything else is
  "proposed" or "not built".
- A figure shows the standard. The client copy states which stages operate today.
- The playbook and the client report use the same legend, the same status words and the same verdict words.
- After a change to the standard, render the figures again and update each client copy that the firm still keeps.
