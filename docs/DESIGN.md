# DESIGN.md — tdlib-android

> Precompiled TDLib for Android, shipped as AARs. The site reads like an engineering datasheet: printed specification, ruled grids, one instrument on the desk. Built, measured, checked — not pitched.

## 1. Visual Theme & Atmosphere

**Style**: Light engineering-datasheet workbench. Warm paper ground, ink hairlines, one deep green signal, a single dark terminal instrument. Single light theme for pages; the code block is the only dark surface.
**Keywords**: printed spec, ruled, tabular, precise, ink-on-paper, measuring-instrument, quiet.
**Tone**: Tooling documentation that happens to be a website. Dense where it earns density, silent about everything else.
**Interaction Tier**: L2 — sticky blur nav, scrollable mobile nav, scroll-reveal on index only, terminal boot staggering, visible focus rings, reduced-motion fallback.
**Dependencies**: CSS-only. Vanilla `IntersectionObserver` for reveal. Google Fonts: IBM Plex Sans + IBM Plex Mono.

## 2. Color Palette & Roles

Every colour is a token. No literal hex past `:root` in any stylesheet or inline style.

```css
:root {
  /* paper */
  --bg:        #F7F4EC;   /* page canvas: warm bone paper */
  --bg2:       #EFEBDF;   /* alternating bands, footer, strip */
  --panel:     #FCFAF4;   /* cards, lifted containers */

  /* ink ramp */
  --ink:       #191C15;   /* headings, primary text — 14.9:1 on --bg */
  --dim:       #454A3D;   /* body copy — 8.2:1 on --bg */
  --mut:       #6E7263;   /* labels, muted — 5.0:1 on --bg */

  /* hairlines */
  --line:      #DCD7C6;   /* section rules */
  --line2:     #C8C3AE;   /* interactive borders, hover */

  /* the one signal */
  --ac:        #0F7B45;   /* engineering green: CTAs, ✓, version — 4.6:1 on --bg */
  --ac-hover:  #0B6136;
  --ac-soft:   rgba(15,123,69,.09);

  /* instrument: the dark terminal block */
  --term-bg:     #141714;
  --term-border: #2B2F28;
  --term-ink:    #D9E1D5;
  --term-dim:    #A3AE9F;
  --term-mut:    #7E897B;
  --term-ac:     #56D68B;

  /* misc */
  --on-ac:   #FBFAF5;
  --bmc:     #FFDD00;   /* vendor-fixed Buy Me a Coffee chip */
}
```

**Rules**
- Green is the sole chromatic event: primary CTA, ✓ cells, key-version figure, active nav.
- Links sit on `--ink` with underline; the blue cyan of the old theme is gone.
- Contrast: every ink ramp step ≥ 4.5:1 on its ground; green checked for text it carries.
- Focus: 2px `--ac` outline, 3px offset, everywhere.

## 3. Typography

**Faces**
- **IBM Plex Sans** — display and body. Print-tooling geometry.
- **IBM Plex Mono** — labels, values, code, tables, version figures. The measuring voice.

Scale:
```
--text-hero:  clamp(40px, 5.4vw, 62px) / 1.04  weight 700  ls -0.025em
--text-h2:    clamp(28px, 3.2vw, 38px) / 1.15  weight 700  ls -0.02em
--text-lead:  17.5px / 1.6   weight 400   --dim
--text-body:  16px   / 1.65
--text-mono:  13px   / 1.75  mono
```
- Headings `text-wrap: balance`, prose `text-wrap: pretty`, all numeric cells `tabular-nums`.
- Labels are mono, sentence case, **untracked** — no uppercase, no letter-spacing anywhere.

## 4. Spacing & Layout

Container `min(1180px, 92vw)`. Section rhythm `clamp(4rem, 10vh, 7rem)`. Grid tracks `minmax(0, 1fr)` wherever columns meet content; display heads carry `overflow-wrap: break-word; min-width: 0`. `html, body { overflow-x: clip }`. Container capped and centred: at 1920px the gutters grow, the measure does not.

Page archetypes (index):
1. **Hero** — 8/4 asymmetric split. Left: headline, one sentence, two actions. Right: the dark terminal instrument (plain filename bar, no mac dots — no hand-drawn OS windows).
2. **Datasheet strip** — mono facts separated by `✳`, marquee with hover-pause.
3. **Pipeline** — vertical ruled flow, mono keys left, the signature detail: four gates, publish row lit green.
4. **Contents** — asymmetric card grid (4/2 then 3/3), receipts not slogans.
5. **Comparison table** — datasheet table, mono lowercase heads, green ✓ against mut fallbacks.
6. **CTA band** + **footer** on `--bg2`, license split BSL-1.0 / Apache-2.0.

Subpages (setup, about, contact, privacy) share `article.css`: 860px measure, numbered steps, tip boxes, code blocks on the dark instrument, contact/bio cards.

## 5. Component Patterns

- **Radius**: 8px base, 14px panels — concentric down, never all-equal.
- **Cards**: `--panel` surface + 1px hairline; hover raises border to `--line2`, lift 2px. `transition: border-color .2s, transform .2s` — never `transition: all`.
- **Primary CTA**: `--ac` ground, `--on-ac` text, `--ac-hover` on hover, ≤ 3 words, never wraps at desktop.
- **Code block**: dark instrument only. Filename label top-right, copy button top-right on hero, comment/orange-green syntax kept from mono palette.
- **Hero paper texture**: a faint ruled grid (repeating-linear-gradient hairlines at 4% ink) behind the hero only — the datasheet surface, not decoration.
- Every interactive element ≥ 40px hit height with visible `:focus-visible`.

## 6. Motion (L2)

- `.reveal/.rv`: opacity 0→1 + 12px rise, `cubic-bezier(0.16,1,0.3,1)` .6s, IntersectionObserver threshold .15, observed once. Index only.
- Hero layers stagger 80ms: headline → lead → actions → terminal.
- Terminal boot: mock output lines fade in sequentially on reveal, 40ms stagger.
- Marquee: 30s linear loop, pauses on hover/focus-within.
- Hover: CTA translateY(-1px), cards lift 2px. Real properties only; no width/height/top/left animation.
- `prefers-reduced-motion: reduce` collapses everything to .01ms, marquee falls back to wrapped static list.

## 7. Accessibility Gate

- All ink ramp steps ≥ 4.5:1 (measured above); green CTA carries ≥ 4.5:1 against its `--on-ac` text.
- Skip link, `:focus-visible` on every interactive, keyboard-reachable nav/actions/table.
- `prefers-reduced-motion` + `prefers-reduced-transparency` fallbacks mandatory.
- Decorative marks `aria-hidden`; icons labelled; alt text on content images.

## 8. Slop-Rejection Check

- No dark-purple or dark-green dev-site default: the page is paper and ink.
- No hand-drawn browser/OS window chrome, no decorative status dots, no emoji icons.
- No tracked-caps eyebrows or mid-dot meta strings.
- No invented metrics: every figure on the page traces to the repo (VERSION file, workflow YAML, verify script).
- No card-inside-card, no purple-blue gradient. The hero grid texture is a hairline rule pattern, not a colour gradient.
- Max one eyebrow per three sections; copy carries itself.
- `sloplint --render` must pass before ship.

## 9. One-Line Pitch

"A printed engineering datasheet that keeps one dark instrument on the desk: warm ruled paper, IBM Plex everything, a single measured green — the opposite of another glowing dark dev page."
