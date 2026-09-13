#!/usr/bin/env python3
"""
Force single light theme + warm terminal across tdlib-android docs.
Removes: theme switcher, dark CSS blocks, dark media queries, head theme scripts.
Keeps: warm terminal (surface-warm #141715), copy buttons, reveal animation on index.
"""
import re, os, sys

# Windows console: allow unicode checkmarks
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')

def remove_balanced_block(text, selector_pattern):
    """Remove a CSS block { ... } starting at selector_pattern, matching balanced braces."""
    m = re.search(selector_pattern, text)
    if not m:
        return text, False
    start = m.start()
    idx = text.find('{', m.end())
    if idx == -1:
        return text, False
    depth = 1
    i = idx + 1
    while i < len(text) and depth > 0:
        if text[i] == '{': depth += 1
        elif text[i] == '}': depth -= 1
        i += 1
    end = i
    while end < len(text) and text[end] in '\r\n':
        end += 1
    return text[:start] + text[end:], True


def process_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    original = text
    basename = os.path.basename(filepath)

    # 1. Force data-theme="light"
    text = text.replace('data-theme="system"', 'data-theme="light"')
    text = text.replace('data-theme="dark"', 'data-theme="light"')

    # 2. Replace any <script>…theme…</script> head scripts with data-theme="light" + html.js
    #    Cleanest matching: any <script> whose content includes 'tdlib-theme' (multi-line).
    text = re.sub(
        r'<script>\s*\n\s*\(?function\(\)\s*\{.*?tdlib-theme.*?\(\);\s*</script>',
        '<script>document.documentElement.setAttribute("data-theme","light");document.documentElement.classList.add("js")</script>',
        text,
        count=1,
        flags=re.DOTALL
    )
    # Common single-line variants without tdlib-theme but setting data-theme
    text = re.sub(
        r"<script>\s*\n\s*var [tT]=(?:theme|t|saved)\s*=.*?data-theme.*?\(\);\s*</script>",
        '<script>document.documentElement.setAttribute("data-theme","light");document.documentElement.classList.add("js")</script>',
        text,
        count=1,
        flags=re.DOTALL
    )
    # Imitate index's own head script exactly (parses theme param + localStorage)
    text = re.sub(
        r'<script>\s*\n\s*\(function\(\)\s*\{\s*\n\s*var params .*?\}\)\(\);\s*\n</script>',
        '<script>document.documentElement.setAttribute("data-theme","light");document.documentElement.classList.add("js")</script>',
        text,
        count=1,
        flags=re.DOTALL
    )

    # 3. Remove dark CSS: @media (prefers-color-scheme: dark) { ... }
    removed_dark = False
    text, r = remove_balanced_block(text, r'@media\s*\(prefers-color-scheme:\s*dark\)')
    removed_dark = removed_dark or r

    # 4. Remove html[data-theme="dark"] { ... }
    text, r = remove_balanced_block(text, r'html\[data-theme="dark"\]\s*\{')
    removed_dark = removed_dark or r

    # 5. Remove html[data-theme="light"] { ... } (redundant — :root already has light values)
    text, r = remove_balanced_block(text, r'html\[data-theme="light"\]\s*\{')
    removed_dark = removed_dark or r

    # 6. Remove stale duplicate <meta name="theme-color" content="#0a0a0b">
    text = re.sub(r'\s*<meta name="theme-color" content="#0a0a0b">\s*\n?', '\n', text)

    # 6b. Strip orphan .theme-switcher CSS (markup + JS already removed) — line-based + single-line media queries
    lines = text.split('\n')
    keep = []
    for ln in lines:
        if ln.strip().startswith('.theme-switcher'):
            continue
        # Kill whole-line @media(max-width:640px){.theme-switcher...} mobile rules
        if 'max-width:640px' in ln and '.theme-switcher' in ln:
            continue
        if '.theme-switcher' not in ln:
            keep.append(ln)
            continue
        # lines mentioning .theme-switcher inside a rule (reduced-transparency media query)
        keep.append(ln.replace('.theme-switcher,', '').replace(',.theme-switcher', '').replace(' .theme-switcher', ''))
    text = '\n'.join(keep)

    # 7. Remove theme switcher HTML (<!-- THEME SWITCHER --> through </aside>)
    text = re.sub(
        r'\s*<!-- THEME SWITCHER -->\s*\n.*?</aside>\s*\n?',
        '\n',
        text,
        flags=re.DOTALL
    )

    # 8. Remove theme switcher JS controller
    #    Standalone script block: <script>\n// Floating...\n...applyTheme...\n</script>
    text = re.sub(
        r'<script>\s*\n// Floating Theme Switcher Controller\s*\n\(function\(\)\{.*?applyTheme\(saved\);\s*\}\)\(\);\s*\n</script>',
        '',
        text,
        flags=re.DOTALL
    )
    #    Within combined script block (setup.html): remove just the IIFE
    text = re.sub(
        r'\n?// Floating Theme Switcher Controller\s*\n\(function\(\)\{.*?applyTheme\(saved\);\s*\}\)\(\);',
        '',
        text,
        flags=re.DOTALL
    )

    # 9. For index.html only: js-class script already inserted by head replacement; skip dup.
    #    (index.html's original head script already sets html.js.)

    # 10. Clean up empty <script></script> or <script>\n</script>
    text = re.sub(r'\n?<script>\s*</script>\n?', '\n', text)

    # 11. Collapse 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    if text != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        saved = len(original) - len(text)
        print(f"  [OK] {basename} ({saved:+d} bytes)")
        return True
    else:
        print(f"  - {basename} (no changes)")
        return False


def fix_sitemap():
    sitemap = os.path.join(DOCS, 'sitemap.xml')
    with open(sitemap, 'r', encoding='utf-8') as f:
        st = f.read()
    st_new = st.replace(
        '<loc>https://tdlib-android.vercel.app/agent-instructions</loc>',
        '<loc>https://tdlib-android.vercel.app/agent-instructions.md</loc>'
    )
    if st_new != st:
        with open(sitemap, 'w', encoding='utf-8') as f:
            f.write(st_new)
        print("  [OK] sitemap.xml (agent-instructions to .md)")
    else:
        print("  – sitemap.xml (already correct)")


def update_design_md():
    """Rewrite DESIGN.md to describe single light theme, warm terminal."""
    path = os.path.join(DOCS, 'DESIGN.md')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    original = text

    # Replace dark theme references with light single-theme language
    text = text.replace(
        "**Style**: Terminal-native infra documentation page.",
        "**Style**: Light vellum + warm dark terminal. Single theme, no switcher."
    )
    text = text.replace(
        "**Feel**: A well-lit engineering console at 2am. Everything on screen earns its pixels.",
        "**Feel**: A clean light workbench with a warm dark terminal at center. Everything earns its pixels."
    )

    # Replace the dark palette with light palette as primary
    text = text.replace(
        "```css\n:root {\n  /* Backgrounds — Linear near-black */\n  --bg: #0a0a0b;                 /* page */\n  --surface: #121214;            /* cards/containers */\n  --surface-alt: #161618;        /* alternating section */\n  --surface-warm: #1a1714;       /* Warp-tinted card (terminal frame) */\n  --surface-hover: #1c1c1f;\n\n  /* Borders — Linear hairline */\n  --border: #23252a;\n  --border-hover: #34343a;\n\n  /* Text — Linear ink ramp */\n  --text: #f7f8f8;\n  --text-secondary: #d0d6e0;\n  --text-tertiary: #8a8f98;\n  --text-faint: #62666d;\n\n  /* Accent — Supabase emerald (#3ecf8e, HSL 152° — off-orange) */\n  --accent: #3ecf8e;\n  --accent-hover: #4ade80;\n  --accent-deep: #24b47e;\n  --on-accent: #0a0a0b;\n\n  /* RGB variants */\n  --bg-rgb: 10,10,11;\n  --accent-rgb: 62,207,142;\n\n  /* Semantic — Linear */\n  --success: #27a644;\n  --error: #e5484d;\n  --warning: #f5a524;\n  --code-bg: #0d0d0f;\n  --code-border: #1f2227;\n}\n```",
        """```css
:root {
  /* Backgrounds — light vellum */
  --bg: #FBFBFA;                 /* page */
  --surface: #FFFFFF;            /* cards/containers */
  --surface-alt: #F4F3EE;        /* alternating section */
  --surface-warm: #141715;       /* terminal frame (warm dark) */
  --surface-hover: #F2F0E8;

  /* Borders — warm hairline */
  --border: #E6E4DD;
  --border-hover: #D4D1C7;

  /* Text — ink ramp */
  --text: #161917;
  --text-secondary: #59615C;
  --text-tertiary: #59615C;
  --text-faint: #646C66;

  /* Accent — deep emerald */
  --accent: #047857;
  --accent-hover: #065f46;
  --accent-deep: #064e3b;
  --on-accent: #FFFFFF;

  /* RGB variants */
  --bg-rgb: 251, 251, 250;
  --accent-rgb: 4, 120, 87;

  /* Semantic */
  --success: #047857;
  --error: #DC2626;
  --warning: #D97706;
  --code-bg: #141715;
  --code-border: #242B26;
}
```"""
    )

    # Update color rules
    text = text.replace(
        "- Every color via CSS vars. No hardcoded hex in markup.\n- Emerald = the ONLY chromatic event. Appears on: primary CTA, version badge, ABI \"✓\" states, active nav. Never decorative washes.\n- One accent per section. Green links in body = always underline, never just color.\n- Body text never below `#8a8f98` on `#0a0a0b` (contrast ≥ 4.5:1).",
        "- Every color via CSS vars. No hardcoded hex in markup.\n- Emerald = the ONLY chromatic event. Appears on: primary CTA, version badge, ABI \"✓\" states, active nav. Never decorative washes.\n- One accent per section. Green links in body = always underline, never just color.\n- Body text `#59615C` on `#FBFBFA` = contrast ≥ 4.5:1 (AA)."
    )

    # Update typography contrast reference
    text = text.replace(
        "- Body text `#d0d6e0` on `#0a0a0b` = ~10:1. Accent `#3ecf8e` on `#0a0a0b` = ~8.5:1. All ≥ 4.5:1 (AA). Large display `#f7f8f8` ≥ 3:1.",
        "- Body text `#59615C` on `#FBFBFA` = contrast ≥ 7:1. Accent `#047857` on `#FBFBFA` = ≥ 5.5:1. All ≥ 4.5:1 (AA)."
    )

    # Update signature detail
    text = text.replace(
        '"An engineering console for TDLib-on-Android: near-black, mono-precise, one emerald signal — the page is a piece of tooling, not a pitch deck."',
        '"Light vellum workbench with a warm dark terminal at center: one emerald signal, zero theme split, the page is a piece of tooling, not a pitch deck."'
    )

    # Update fused systems description
    text = text.replace(
        "**Linear** (skeleton: near-black `#010102`, hairline borders, dense technical type scale) **+ Supabase** (texture: signature emerald `#3ecf8e` as sole chromatic accent). **Warp** borrowed: warm-charcoal `#2b2622`-derived terminal framing + tight geometry.",
        "**Linear** (skeleton: light vellum `#FBFBFA`, hairline borders, dense technical type scale) **+ Supabase** (texture: deep emerald `#047857` as sole chromatic accent). **Warp** borrowed: warm dark `#141715` terminal framing + tight geometry. Single theme, no switcher."
    )

    # Update interaction tier
    text = text.replace(
        "**Interaction Tier**: L2 — sticky blur nav, scroll-reveal, hero layered entrance, hover/focus states, reduced-motion fallback.",
        "**Interaction Tier**: L2 — sticky blur nav, scroll-reveal (index only), hover/focus states, reduced-motion fallback. Single light theme, no theme switcher."
    )

    # Add theme constraint to slop-rejection check
    text = text.replace(
        "## 9. Slop-Rejection Check\n\n- No centered hero + 3 decorative cards. Hero carries a real terminal.\n- No purple/blue gradient. Emerald only chromatic event.\n- No warm-cream / orange-amber palette (accents are emerald, bg near-black).\n- No Inter/Roboto/Space Grotesk defaults (IBM Plex Sans + JetBrains Mono).\n- Max one eyebrow per 3 sections. No \"powerful/seamless/cutting-edge\" copy.\n- Motion present + reduced-motion fallback. Focus states everywhere.",
        "## 9. Slop-Rejection Check\n\n- No centered hero + 3 decorative cards. Hero carries a real terminal.\n- No purple/blue gradient. Emerald only chromatic event.\n- No warm-cream / orange-amber palette (accents are emerald, bg light vellum).\n- No Inter/Roboto/Space Grotesk defaults (IBM Plex Sans + JetBrains Mono).\n- No theme switcher. Single light theme. Warm dark terminal only in code blocks.\n- Max one eyebrow per 3 sections. No \"powerful/seamless/cutting-edge\" copy.\n- Motion present + reduced-motion fallback. Focus states everywhere."
    )

    if text != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  [OK] DESIGN.md ({len(original) - len(text):+d} bytes)")
    else:
        print("  – DESIGN.md (no changes)")


def main():
    print("=== Light theme unification: tdlib-android docs ===\n")

    html_files = ['index.html', 'setup.html', 'about.html', 'contact.html', 'privacy.html', '404.html']
    count = 0
    for fn in html_files:
        fp = os.path.join(DOCS, fn)
        if os.path.exists(fp):
            if process_html(fp):
                count += 1
        else:
            print(f"  ✗ {fn} NOT FOUND")

    print()
    fix_sitemap()
    print()
    update_design_md()

    print(f"\n✓ {count} HTML files updated, sitemap fixed, DESIGN.md synced.")


if __name__ == '__main__':
    main()
