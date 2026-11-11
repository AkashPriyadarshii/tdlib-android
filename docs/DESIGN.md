# DESIGN.md — tdlib-android

> Developer infrastructure that drops into your `build.gradle.kts`. No source compile, no `.so` wrangling, no NDK. The page reads like a piece of tooling: dense, precise, quietly demanding trust.

## 1. Visual Theme & Atmosphere

**Style**: Dark terminal-precision theme. Single theme, high contrast.
**Keywords**: precise, dense, hardware, CLI, dark-carbon, tabular, code-first.
**Tone**: Technical and unhurried — NOT startup-boilerplate hype.
**Feel**: An engineered terminal console. Dense information hierarchy where code and verified metrics earn every pixel.

**Interaction Tier**: L2 — sticky blur nav, responsive scrollable links on mobile, scroll-reveal (index only), visible focus rings, reduced-motion fallback. Single dark theme.
**Dependencies**: CSS-only (no framework). Vanilla JS `IntersectionObserver` for reveal.

## 2. Color Palette & Roles

Engineered for precision tooling with Telegram emerald + cyan accents on deep carbon.

```css
:root {
  /* Backgrounds */
  --bg: #070a09;                 /* page canvas */
  --bg2: #0c110f;                /* alternating sections / stat tiles */
  --panel: #101614;              /* cards, interactive containers */

  /* Borders */
  --line: #1c2622;               /* subtle borders */
  --line2: #263430;              /* interactive / hovered borders */

  /* Text — ink ramp (all >= 4.5:1 on their backgrounds) */
  --ink: #e6f0ea;                /* primary text (17.05:1 on --bg) */
  --dim: #9db3a8;                /* secondary text / leads (8.94:1 on --bg) */
  --mut: #769687;                /* muted labels, table headers (6.14:1 on --bg) */

  /* Accent — Telegram green + cyan */
  --ac: #2eea8b;                 /* primary accent green */
  --ac2: #35c9e8;                /* secondary cyan for links/highlights */
  --ac-soft: rgba(46,234,139,.11);/* pill backgrounds */

  /* Terminal frame */
  --code-bg: #0a100e;
  --code-border: #1c2622;
  --term-text: #c6d6cd;
  --term-muted: #769687;
  --term-accent: #2eea8b;
  --term-comment: #6c8c7d;       /* code comments (5.20:1 on #0a100e) */
}
```

**Color Rules:**
- Every color via CSS vars. No hardcoded hex in markup.
- Telegram emerald (`--ac`) = primary chromatic event: CTAs, version badges, ABI "✓" states, active nav indicators.
- Contrast verification: all normal text pairings exceed WCAG 2.1 AA (≥ 4.5:1).
- Interactive focus states: explicit `:focus-visible` outline in `--ac` with 3px offset.

## 3. Typography

**Faces:**
- **Sora** (sans) — display + body. Technical geometry, humanist legibility.
- **IBM Plex Mono** (mono) — all code blocks, terminal mockups, version strings, table ABI labels. Tabular, hardware-precise.
- Fallbacks: `'Sora', system-ui, sans-serif` / `'IBM Plex Mono', ui-monospace, monospace`.

Weight logic: display 700/800, body 400/600, labels 500 mono.

Scale:
```
--text-hero:    clamp(40px, 5.6vw, 64px)    / 1.04  weight 800  ls -0.03em
--text-h2:      clamp(28px, 3.4vw, 40px)    / 1.15  weight 700  ls -0.02em
--text-lead:    1.09375rem (17.5px)         / 1.6   weight 400
--text-body:    1rem (16px)                 / 1.65  weight 400
--text-mono:    0.8125rem (13px)            / 1.75  mono
--text-label:   0.71875rem (11.5px)         / 1.2   mono cap  uppercase ls 0.08em
```
All headings `text-wrap: balance`; body and lead paragraphs `text-wrap: pretty`. Tabular numbers enforced across all data cells.

## 4. Spacing & Layout

Container: `min(1200px, 92vw)` centered. Section spacing `clamp(4rem, 10vh, 7rem)`.

Grid: 12-col free-mix (not rigid 3-card rows). Hero = 8/4 split (copy + terminal frame). ABIs = 4-col table. Pipeline = vertical mono flow.

**Layout archetype (reject centered-hero-3-cards):**
1. **Hero** — full-width. Left: display headline + sub + 2 CTAs (primary `Add to build.gradle.kts` / ghost `See the releases`). Right: a real **terminal window** (dark surface-warm, mono, fake prompt output showing Gradle dependency resolve) — the product IS the code.
2. **Proof strip** — one line mono: `TDLib v0.1.1 · 4 ABIs · Realme GT 7 ✓`.
3. **ABI matrix** — honest 4-col table (mono, tabular-nums, emerald ✓), not fluffy badges.
4. **Why-this-exists** — dense editorial block, the "every other option is dead" argument. Copy carries it.
5. **Pipeline** — vertical flow (mono steps, `→` connectors) showing the automated CI loop. Signature detail home.
6. **Card rail** — 3 utility cards, but not feature-cliché: each is a *receipt* (a concrete number/mechanic, not "powerful/fast").
7. **CTA band** — minimal, single line.
8. **Footer** — license split (BSL-1.0 core / Apache-2.0 ktx), credits, socials.

## 5. Component Patterns & Micro-Polish

- **Radius**: concentric — base 12px; nested card 10px (`12 - 2`); terminal header 8px. Never all-equal.
- **Hit targets**: ≥ 40px on every interactive.
- **Cards**: surface + 1px `--border` hairline + 1px image/terminal outline (never vanish on dark). Hover: `border-hover` + lift 2px, `transition: transform .2s, border-color .2s` (NO `transition: all`).
- **Primary CTA**: emerald bg, `--on-accent` text, hover `--accent-hover`, focus-visible 2px `--accent` ring offset 2px. Label ≤ 3 words, never wraps on wide breakpoint.
- **Buttons/labels**: mono uppercase for chip labels (`ABI`, `LICENSE`, `VERSION`) — max ONE eyebrow per 3 sections.
- **Terminal frame**: `--surface-warm` bg, `--code-border`, 3-dot mac-ish header (`#ff5f57 #febc2e #28c840` muted at 40%), body = JetBrains Mono. A `$` prompt + syntax-colored output. Version badge pinned in the header right.
- Every numeric cell `font-variant-numeric: tabular-nums`.
- All interactive: `:focus-visible` ring. No hover-only interactivity.

## 6. Motion (L2, from interaction-patterns.md)

- Entrance: `.reveal` opacity 0 → 1 + 8px rise, `cubic-bezier(0.16,1,0.3,1)` `.6s`, observed once (IntersectionObserver, threshold 0.15).
- Hero layered: nav, then headline, then sub, then terminal — stagger `80ms`.
- Sticky nav: blur backdrop + hairline on scroll.
- Terminal "boot": on reveal, the mock output lines fade in sequentially (typewriter feel, `.04s` stagger) — the signature motion.
- Hover: CTA scale 1.02, cards lift 2px.
- Reduced motion: kill all (pattern below).

## 7. Accessibility Gate

- Body text `#3F463F` on `#FBFBFA` = contrast ≥ 9.4:1. Accent `#047857` on `#FBFBFA` = ≥ 5.5:1. All ≥ 4.5:1 (AA).
- Nav, CTAs, links, terminal all keyboard-reachable with visible `:focus-visible`.
- `prefers-reduced-motion: reduce` → animations/transitions collapsed to 0.01ms.
- Decorative terminal dots `aria-hidden`; meaningful badges have aria-labels; images alt.
- Links describe destination ("View the github releases" not "click here").

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## 8. Signature Detail

**The auto-update pipeline as a live vertical flow.** Below the fold, a mono terminal-style sequence renders the automated TDLib pipeline — `check-upstream → build matrix (4 ABIs) → human-review PR → publish → smoke-verify` — as connected steps with `→` glyphs. Each step is a terse mono line (`[cron 6h] poll tdlib/td VERSION`), framed like build logs, with the final step lit emerald. It makes the product's biggest differentiator (self-updating, zero-touch) visible as the page's structural spine — not a bullet list.

## 9. Slop-Rejection Check

- No centered hero + 3 decorative cards. Hero carries a real terminal.
- No purple/blue gradient. Emerald only chromatic event.
- No warm-cream / orange-amber palette (accents are emerald, bg light vellum).
- No Inter/Roboto/Space Grotesk defaults (IBM Plex Sans + JetBrains Mono).
- No theme switcher. Single light theme. Warm dark terminal only in code blocks.
- Max one eyebrow per 3 sections. No "powerful/seamless/cutting-edge" copy.
- Motion present + reduced-motion fallback. Focus states everywhere.

---

### Fused systems
**Linear** (skeleton: light vellum `#FBFBFA`, hairline borders, dense technical type scale) **+ Supabase** (texture: deep emerald `#047857` as sole chromatic accent). **Warp** borrowed: warm dark `#141715` terminal framing + tight geometry. Single theme, no switcher.

### Signature detail
The live auto-update pipeline as a vertical mono flow, emerald-lit at the publish/verify step.

### One-line pitch
"Light vellum workbench with a warm dark terminal at center: one emerald signal, zero theme split, the page is a piece of tooling, not a pitch deck."
