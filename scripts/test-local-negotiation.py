#!/usr/bin/env python3
"""
test-local-negotiation.py

Simulates local HTTP requests against docs/ following vercel.json rewrite & header rules:
- Verifies Accept: text/markdown content negotiation and Vary: Accept headers.
- Verifies 404 behavior and recovery markdown links.
- Verifies trust anchor endpoints /about, /contact, /privacy.
"""

import sys
import re
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import urllib.request
import urllib.error

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"

class VercelSimHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS_DIR), **kwargs)

    def do_GET(self):
        accept_header = self.headers.get("Accept", "")
        accept_markdown = "text/markdown" in accept_header

        url_path = self.path.split("?")[0].rstrip("/")
        if url_path == "":
            url_path = "/"

        # Rewrites simulation
        if accept_markdown:
            rewrite_map = {
                "/": "index.md",
                "/setup": "setup.md",
                "/about": "about.md",
                "/contact": "contact.md",
                "/privacy": "privacy.md",
                "/agent-instructions": "agent-instructions.md",
                "/404": "404.md"
            }
            if url_path in rewrite_map:
                target_file = DOCS_DIR / rewrite_map[url_path]
                if target_file.exists():
                    data = target_file.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                    self.send_header("Vary", "Accept, Accept-Encoding")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return

        # Static cleanUrls simulation
        clean_url_map = {
            "/": "index.html",
            "/setup": "setup.html",
            "/about": "about.html",
            "/contact": "contact.html",
            "/privacy": "privacy.html",
        }
        if url_path in clean_url_map:
            target_file = DOCS_DIR / clean_url_map[url_path]
            if target_file.exists():
                data = target_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Vary", "Accept, Accept-Encoding")
                self.send_header("Link", f"</{clean_url_map[url_path].replace('.html', '.md')}>; rel=\"alternate\"; type=\"text/markdown\"")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        # 404 simulation
        fpath = DOCS_DIR / url_path.lstrip("/")
        if not fpath.exists():
            h404 = DOCS_DIR / "404.html"
            data = h404.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Vary", "Accept, Accept-Encoding")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        super().do_GET()

def run_tests():
    server = HTTPServer(("127.0.0.1", 8765), VercelSimHandler)
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()

    base = "http://127.0.0.1:8765"
    errors = 0

    print("Testing Simulated Vercel Content Negotiation & Headers:")

    # 1. Accept: text/markdown on /
    req = urllib.request.Request(base + "/", headers={"Accept": "text/markdown"})
    with urllib.request.urlopen(req) as resp:
        ctype = resp.headers.get("Content-Type")
        vary = resp.headers.get("Vary")
        body = resp.read().decode("utf-8")
        if "text/markdown" in ctype and "Accept" in vary and "# tdlib-android" in body:
            print("  [PASS] GET / with Accept: text/markdown -> 200 text/markdown, Vary: Accept")
        else:
            print(f"  [FAIL] GET / with Accept: text/markdown -> ctype={ctype}, vary={vary}")
            errors += 1

    # 2. Browser request on /
    req_html = urllib.request.Request(base + "/", headers={"Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req_html) as resp:
        ctype = resp.headers.get("Content-Type")
        vary = resp.headers.get("Vary")
        body = resp.read().decode("utf-8")
        if "text/html" in ctype and "Accept" in vary and "<!doctype html>" in body:
            print("  [PASS] GET / with Accept: text/html -> 200 text/html, Vary: Accept")
        else:
            print(f"  [FAIL] GET / with Accept: text/html -> ctype={ctype}")
            errors += 1

    # 3. 404 status and recovery body
    try:
        urllib.request.urlopen(base + "/some-nonexistent-path-for-test")
        print("  [FAIL] 404 test did not raise HTTPError")
        errors += 1
    except urllib.error.HTTPError as e:
        if e.code == 404:
            body = e.read().decode("utf-8")
            if "sitemap.xml" in body and "llms.txt" in body:
                print("  [PASS] GET /nonexistent -> HTTP 404 with markdown recovery index")
            else:
                print("  [FAIL] 404 body missing recovery links")
                errors += 1
        else:
            print(f"  [FAIL] Expected 404 got {e.code}")
            errors += 1

    # 4. Trust anchor pages /about, /contact, /privacy
    for ep in ["/about", "/contact", "/privacy"]:
        req_ta = urllib.request.Request(base + ep, headers={"Accept": "text/html"})
        with urllib.request.urlopen(req_ta) as resp:
            body = resp.read().decode("utf-8")
            if resp.status == 200 and len(body) >= 500:
                print(f"  [PASS] GET {ep} -> 200 OK ({len(body)} bytes)")
            else:
                print(f"  [FAIL] GET {ep} -> status={resp.status}, length={len(body)}")
                errors += 1

    server.shutdown()
    if errors == 0:
        print(">>> ALL SIMULATED LOCAL NEGOTIATION TESTS PASSED! <<<")
        return 0
    else:
        print(f">>> {errors} SIMULATION TESTS FAILED! <<<")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
