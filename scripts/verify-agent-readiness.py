#!/usr/bin/env python3
"""
verify-agent-readiness.py

Automated verification suite for tdlib-android agent readiness:
1. Agent-friendly 404s (404.html, 404.md, recovery links)
2. Markdown content negotiation (vercel.json rewrites, Vary: Accept, Link rel="alternate", .md pairs)
3. Brand discoverability (Schema.org JSON-LD, aliases, NAP, meta tags, sitemap.xml)
4. Agent instructions (when-to-use, when-not-to-use, agent-instructions.md, llms.txt)
5. Trust anchor pages (about, contact, privacy >= 500 characters, mandatory footer columns)
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"

def pass_test(name):
    print(f"  [PASS] {name}")

def fail_test(name, err):
    print(f"  [FAIL] {name}: {err}")
    return 1

def main():
    print("=== Running tdlib-android Agent Readiness Verification Suite ===")
    failures = 0

    # 1. File Presence
    print("\n--- 1. File Presence Checks ---")
    required_files = [
        "index.html", "index.md",
        "setup.html", "setup.md",
        "about.html", "about.md",
        "contact.html", "contact.md",
        "privacy.html", "privacy.md",
        "404.html", "404.md",
        "agent-instructions.md",
        "llms.txt", "llms-full.txt",
        "sitemap.xml", "robots.txt"
    ]
    for rf in required_files:
        fp = DOCS_DIR / rf
        if not fp.exists():
            failures += fail_test(f"File {rf} exists", "File missing")
        else:
            pass_test(f"File {rf} exists ({fp.stat().st_size} bytes)")

    vjson_path = ROOT_DIR / "vercel.json"
    if not vjson_path.exists():
        failures += fail_test("vercel.json exists", "Missing at repo root")
    else:
        pass_test(f"vercel.json exists ({vjson_path.stat().st_size} bytes)")

    # 2. Trust Anchor Content Length (>= 500 characters each)
    print("\n--- 2. Trust Anchor Pages Checks (Requirement 5) ---")
    trust_anchors = ["about", "contact", "privacy"]
    for ta in trust_anchors:
        html_file = DOCS_DIR / f"{ta}.html"
        md_file = DOCS_DIR / f"{ta}.md"

        html_content = html_file.read_text(encoding="utf-8")
        md_content = md_file.read_text(encoding="utf-8")

        if len(html_content) < 500:
            failures += fail_test(f"{ta}.html content length", f"Too short ({len(html_content)} chars < 500)")
        else:
            pass_test(f"{ta}.html length is {len(html_content)} characters (>= 500)")

        if len(md_content) < 500:
            failures += fail_test(f"{ta}.md content length", f"Too short ({len(md_content)} chars < 500)")
        else:
            pass_test(f"{ta}.md length is {len(md_content)} characters (>= 500)")

    # 3. Mandatory Footer Columns Verification
    print("\n--- 3. Mandatory Website Footer Columns (Akash Identity Rule 12) ---")
    html_pages_to_check = ["index.html", "setup.html", "about.html", "contact.html", "privacy.html", "404.html"]
    for page in html_pages_to_check:
        content = (DOCS_DIR / page).read_text(encoding="utf-8")
        has_ecosystem = "design-genius" in content and "akash-design-engineering" in content and "kharcha" in content
        has_author = "Patna, Bihar, India" in content and "akashpriyadarshi.vercel.app" in content
        has_social = "@Akash__ydv001" in content or "Akash__ydv001" in content

        if not (has_ecosystem and has_author and has_social):
            failures += fail_test(f"{page} mandatory footer columns", "Missing one or more required columns (Ecosystem, Author, Social)")
        else:
            pass_test(f"{page} includes mandatory Ecosystem, Author, and Social columns")

    # 4. Agent Instructions & When-to-Use (Requirement 4)
    print("\n--- 4. Agent Instructions & When-To-Use (Requirement 4) ---")
    ai_content = (DOCS_DIR / "agent-instructions.md").read_text(encoding="utf-8")
    if "When to Use This" in ai_content and "When NOT to Use This" in ai_content:
        pass_test("agent-instructions.md defines explicit when-to-use and when-not-to-use criteria")
    else:
        failures += fail_test("agent-instructions.md when-to-use", "Missing explicit sections")

    if "io.github.tdlib-android:core" in ai_content and "System.loadLibrary" in ai_content:
        pass_test("agent-instructions.md includes exact Gradle dependencies and JNI usage")
    else:
        failures += fail_test("agent-instructions.md code samples", "Missing dependency or initialization guidance")

    llms_content = (DOCS_DIR / "llms.txt").read_text(encoding="utf-8")
    if "When to Use This (Agent Guidance)" in llms_content and "agent-instructions.md" in llms_content:
        pass_test("llms.txt contains When to Use This section and links to agent-instructions.md")
    else:
        failures += fail_test("llms.txt agent guidance", "Missing guidance section or link")

    llms_full_content = (DOCS_DIR / "llms-full.txt").read_text(encoding="utf-8")
    if "When to Use This (Agent Guidance)" in llms_full_content:
        pass_test("llms-full.txt contains When to Use This section")
    else:
        failures += fail_test("llms-full.txt agent guidance", "Missing guidance section")

    # 5. Agent-Friendly 404 Recovery (Requirement 1)
    print("\n--- 5. Agent-Friendly 404 Recovery (Requirement 1) ---")
    h404 = (DOCS_DIR / "404.html").read_text(encoding="utf-8")
    m404 = (DOCS_DIR / "404.md").read_text(encoding="utf-8")

    expected_404_links = ["/sitemap.xml", "/llms.txt", "/setup", "/about", "/contact", "/privacy"]
    missing_links = [l for l in expected_404_links if l not in h404 or l not in m404]
    if missing_links:
        failures += fail_test("404 recovery links", f"Missing links: {missing_links}")
    else:
        pass_test("404.html and 404.md contain complete recovery links (sitemap, llms.txt, setup, trust pages)")

    # 6. Content Negotiation & vercel.json (Requirement 2)
    print("\n--- 6. Markdown Content Negotiation & vercel.json (Requirement 2) ---")
    try:
        vcfg = json.loads(vjson_path.read_text(encoding="utf-8"))
        pass_test("vercel.json is valid JSON")
    except Exception as e:
        failures += fail_test("vercel.json JSON syntax", str(e))
        vcfg = {}

    rewrites = vcfg.get("rewrites", [])
    has_md_rewrite = False
    for r in rewrites:
        has_cond = r.get("has", [])
        for c in has_cond:
            if c.get("type") == "header" and c.get("key", "").lower() == "accept" and "text/markdown" in c.get("value", ""):
                has_md_rewrite = True
                break
    if has_md_rewrite:
        pass_test("vercel.json contains rewrites matching Accept: text/markdown")
    else:
        failures += fail_test("vercel.json rewrites", "Missing Accept: text/markdown conditional rewrite")

    headers = vcfg.get("headers", [])
    has_vary_all = False
    has_md_content_type = False
    for h in headers:
        src = h.get("source", "")
        hlist = {item["key"].lower(): item["value"] for item in h.get("headers", [])}
        if "vary" in hlist and "accept" in hlist["vary"].lower():
            if src == "/(.*)":
                has_vary_all = True
        if "content-type" in hlist and "text/markdown" in hlist["content-type"]:
            has_md_content_type = True

    if has_vary_all:
        pass_test("vercel.json sets Vary: Accept on all routes /(.*)")
    else:
        failures += fail_test("vercel.json Vary header", "Missing Vary: Accept on /(.*)")

    if has_md_content_type:
        pass_test("vercel.json sets Content-Type: text/markdown for .md files")
    else:
        failures += fail_test("vercel.json Content-Type", "Missing Content-Type text/markdown for .md files")

    # Check <link rel="alternate"> in HTML files
    for p in ["index.html", "setup.html", "about.html", "contact.html", "privacy.html"]:
        c = (DOCS_DIR / p).read_text(encoding="utf-8")
        if 'rel="alternate" type="text/markdown"' in c:
            pass_test(f"{p} contains <link rel=\"alternate\" type=\"text/markdown\"> tag")
        else:
            failures += fail_test(f"{p} link alternate", "Missing link alternate tag")

    # 7. Brand Discoverability & Schema.org (Requirement 3)
    print("\n--- 7. Brand Name Discoverability & Schema.org (Requirement 3) ---")
    index_html = (DOCS_DIR / "index.html").read_text(encoding="utf-8")
    if 'name="application-name" content="tdlib-android"' in index_html:
        pass_test("index.html contains application-name tdlib-android meta tag")
    else:
        failures += fail_test("index.html meta tag", "Missing application-name meta tag")

    if '"alternateName": ["TDLib Android", "tdlib android"' in index_html:
        pass_test("index.html Schema.org contains alternateName aliases for tdlib-android")
    else:
        failures += fail_test("index.html Schema.org alternateName", "Missing alternateName in JSON-LD")

    if '"SoftwareSourceCode"' in index_html and '"WebSite"' in index_html:
        pass_test("index.html Schema.org declares SoftwareSourceCode and WebSite types")
    else:
        failures += fail_test("index.html Schema.org types", "Missing SoftwareSourceCode type")

    # 8. Sitemap and Robots
    print("\n--- 8. Sitemap & Robots Completeness ---")
    sitemap_text = (DOCS_DIR / "sitemap.xml").read_text(encoding="utf-8")
    for ep in ["/", "/setup", "/about", "/contact", "/privacy", "/agent-instructions", "/llms.txt"]:
        if f"https://tdlib-android.vercel.app{ep}" in sitemap_text:
            pass_test(f"sitemap.xml contains {ep}")
        else:
            failures += fail_test(f"sitemap.xml {ep}", f"Missing endpoint {ep}")

    robots_text = (DOCS_DIR / "robots.txt").read_text(encoding="utf-8")
    if "GPTBot" in robots_text and "ClaudeBot" in robots_text and "Sitemap: https://tdlib-android.vercel.app/sitemap.xml" in robots_text:
        pass_test("robots.txt allows AI bots and points to sitemap.xml")
    else:
        failures += fail_test("robots.txt", "Missing bot permissions or sitemap reference")

    print("\n=================================================")
    if failures == 0:
        print(">>> ALL AGENT READINESS VERIFICATION CHECKS PASSED! <<<")
        return 0
    else:
        print(f">>> {failures} CHECKS FAILED! <<<")
        return 1

if __name__ == "__main__":
    sys.exit(main())
