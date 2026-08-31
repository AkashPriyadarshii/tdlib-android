# DESIGN.md — tdlib-android

> Developer infrastructure that drops into your `build.gradle.kts`. No source compile, no `.so` wrangling, no NDK. The page reads like a piece of tooling: dense, precise, quietly demanding trust.

## 1. Visual Theme & Atmosphere

**Style**: Terminal-native infra documentation page.
**Keywords**: precise, dense, hardware, CLI, dark-ops, single-signal, tabular, code-first.
**Tone**: Technical and unhurried — NOT startup-boilerplate hype.
**Feel**: A well-lit engineering console at 2am. Everything on screen earns its pixels.

**Interaction Tier**: L2 — sticky blur nav, scroll-reveal, hero layered entrance, hover/focus states, reduced-motion fallback.
**Dependencies**: CSS-only (no framework). Vanilla JS `IntersectionObserver` for reveal.

## 2. Color Palette & Roles

Fused from **Telegram Protocol Blue** (`#0088CC`, `#229ED9`, Hue: 199.0°) on Dark Navy `#08111A`.

```css
:root {
  /* Backgrounds — Telegram dark navy */
  --bg: #08111a;                 /* page */
  --surface: #0e1a26;            /* cards/containers */
  --surface-alt: #122130;        /* alternating section */
  --surface-warm: #0d1824;       /* tinted card (terminal frame) */
  --surface-hover: #16283b;

  /* Borders — hairline navy slate */
  --border: #1a2f45;
  --border-hover: #264360;

  /* Text — clean ink ramp */
  --text: #f7f8f8;
  --text-secondary: #d0d6e0;
  --text-tertiary: #8a8f98;
  --text-faint: #62666d;

  /* Accent — Telegram Native Blue (#229ED9 / #0088CC, HSL 199° — protocol blue) */
  --accent: #229ed9;
  --accent-hover: #2bb3f4;
  --accent-deep: #0088cc;
  --on-accent: #ffffff;

  /* RGB variants */
  --bg-rgb: 8,17,26;
  --accent-rgb: 34,158,217;

  /* Semantic */
  --success: #27a644;
  --error: #e5484d;
  --warning: #229ed9;
  --code-bg: #060d14;
  --code-border: #16283b;
}
```

**Color Rules:**
- Every color via CSS vars. No hardcoded hex in markup.
- Telegram Blue = the primary chromatic signal. Appears on: primary CTA, version badge, ABI "✓" states, active nav, terminal dot.
- One accent per section. Blue links in body = always underline, never just color.
- Body text never below `#8a8f98` on `#08111a` (contrast ≥ 4.5:1).

## 3. Typography

**Faces:**
- **Geist Sans** (sans) — display + body. Modern, geometric, precise technical grain.
- **JetBrains Mono** (mono) — all code blocks, terminal mockups, version strings, table ABI labels. Tabular, hardware-precise.
- Fallbacks: `'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` / `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`.

Weight logic: display 600, body 400, labels 500 mono. No serif anywhere — this is tooling, not editorial.

Scale:
```
--text-hero:    clamp(2.5rem, 6vw, 4rem)    / 1.05  weight 600  ls -0.03em
--text-h2:      2rem                        / 1.15  weight 600  ls -0.02em
--text-h3:      1.25rem                     / 1.25  weight 600  ls -0.01em
--text-body:    1.0625rem (17px)            / 1.6   weight 400
--text-sm:      0.9375rem (15px)            / 1.5
--text-mono:    0.875rem (14px)             / 1.6   mono
--text-label:   0.78125rem (12.5px)         / 1.2   mono cap  uppercase ls 0.08em
```
All headings `text-wrap: balance`; body `text-wrap: pretty`.

## 4. Spacing & Layout

Container: `min(1200px, 92vw)` centered. Section spacing `clamp(4rem, 10vh, 7rem)`.

Grid: 12-col free-mix (not rigid 3-card rows). Hero = 8/4 split (copy + terminal frame). ABIs = 4-col table. Pipeline = vertical mono flow.

**Layout archetype (reject centered-hero-3-cards):**
1. **Hero** — full-width. Left: display headline + sub + 2 CTAs (primary `Add to build.gradle.kts` / ghost `See the releases`). Right: a real **terminal window** (dark surface-warm, mono, fake prompt output showing Gradle dependency resolve) — the product IS the code.
2. **Proof strip** — one line mono: `TDLib 1.8.64 · 4 ABIs · Realme GT 7 ✓`.
3. **ABI matrix** — honest 4-col table (mono, tabular-nums, emerald/blue ✓), not fluffy badges.
4. **Why-this-exists** — dense editorial block, the "every other option is dead" argument. Copy carries it.
5. **Pipeline** — vertical flow (mono steps, `→` connectors) showing the automated CI loop. Signature detail home.
6. **Card rail** — 3 utility cards, but not feature-cliché: each is a *receipt* (a concrete number/mechanic, not "powerful/fast").
7. **CTA band** — minimal, single line.
8. **Footer** — license split (BSL-1.0 core / Apache-2.0 ktx), credits, socials.

## 5. Component Patterns & Micro-Polish

- **Radius**: concentric — base 12px; nested card 10px (`12 - 2`); terminal header 8px. Never all-equal.
- **Hit targets**: ≥ 40px on every interactive.
- **Cards**: surface + 1px `--border` hairline + 1px image/terminal outline (never vanish on dark). Hover: `border-hover` + lift 2px, `transition: transform .2s, border-color .2s` (NO `transition: all`).
- **Primary CTA**: telegram blue bg, `--on-accent` text, hover `--accent-hover`, focus-visible 2px `--accent` ring offset 2px. Label ≤ 3 words, never wraps on wide breakpoint.
- **Buttons/labels**: mono uppercase for chip labels (`ABI`, `LICENSE`, `VERSION`) — max ONE eyebrow per 3 sections.
- **Terminal frame**: `--surface-warm` bg, `--code-border`, 3-dot mac-ish header (`#ff5f57 #229ed9 #28c840`), body = JetBrains Mono. A `$` prompt + syntax-colored output. Version badge pinned in the header right.
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

- Body text `#d0d6e0` on `#08111a` = ~12:1. Accent `#229ed9` on `#08111a` = ~6.8:1. All ≥ 4.5:1 (AA). Large display `#f7f8f8` ≥ 3:1.
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

**The auto-update pipeline as a live vertical flow.** Below the fold, a mono terminal-style sequence renders the automated TDLib pipeline — `check-upstream → build matrix (4 ABIs) → human-review PR → publish → smoke-verify` — as connected steps with `→` glyphs. Each step is a terse mono line (`[cron 6h] poll tdlib/td VERSION`), framed like build logs, with the final step lit telegram blue. It makes the product's biggest differentiator (self-updating, zero-touch) visible as the page's structural spine — not a bullet list.

## 9. Slop-Rejection Check

- No centered hero + 3 decorative cards. Hero carries a real terminal.
- No warm-cream / orange-amber palette (`#febc2e`, `#f5a524` replaced with Telegram Protocol Blue `#229ed9` / `#0088cc`).
- No Inter/Roboto/Space Grotesk defaults (Geist Sans + JetBrains Mono).
- Max one eyebrow per 3 sections. No "powerful/seamless/cutting-edge" copy.
- Motion present + reduced-motion fallback. Focus states everywhere.

---

### Fused systems
**Telegram Native Blue** (`#0088cc` / `#229ed9`, Hue: 199.0°) on **Dark Navy Console** (`#08111a`, hairline borders `#1a2f45`, dense technical type scale with Geist Sans + JetBrains Mono).

### Signature detail
The live auto-update pipeline as a vertical mono flow, protocol-blue-lit at the publish/verify step.

### One-line pitch
"An engineering console for TDLib-on-Android: dark navy, mono-precise, Telegram protocol blue signal — the page is a piece of tooling, not a pitch deck."

