#!/usr/bin/env python3
"""
Generates an SVG chart for tdlib-android release downloads & Maven Central telemetry.
Stdlib-only: zero external dependencies.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

REPO = "AkashPriyadarshii/tdlib-android"
SCARF_OWNER = "Tdlib-android"
OUTPUT_SVG = "docs/downloads-chart.svg"
OUTPUT_BANNER_SVG = "docs/banner.svg"

def fetch_release_stats():
    releases = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "tdlib-android-metrics-generator"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                page_releases = json.loads(res.read().decode("utf-8"))
        except Exception as e:
            print(f"Warning: Failed to fetch releases from GitHub (page {page}): {e}")
            if page == 1:
                return []
            break
        if not page_releases:
            break
        releases.extend(page_releases)
        if len(page_releases) < 100:
            break
        page += 1

    stats = []
    for r in releases:
        tag = r.get("tag_name", "unknown")
        created = r.get("published_at", "")[:10]
        core_dl = 0
        ktx_dl = 0
        checksum_dl = 0
        for asset in r.get("assets", []):
            name = asset.get("name", "")
            dl = asset.get("download_count", 0)
            if "core-release" in name:
                core_dl += dl
            elif "ktx-release" in name:
                ktx_dl += dl
            elif "checksums" in name:
                checksum_dl += dl

        total = core_dl + ktx_dl + checksum_dl
        stats.append({
            "tag": tag,
            "date": created,
            "core": core_dl,
            "ktx": ktx_dl,
            "checksums": checksum_dl,
            "total": total
        })
    return stats

def fetch_scarf_stats():
    """
    Fetches aggregate telemetry from Scarf v3 insights API.
    Returns zeroed stats if token is missing or API fails.
    """
    token = os.environ.get("SCARF_API_TOKEN")
    default_stats = {
        "downloads": 0,
        "unique_sources": 0,
        "core": 0,
        "ktx": 0,
    }
    if not token:
        print("Note: SCARF_API_TOKEN not set, using zeroed Scarf stats.")
        return default_stats

    url = f"https://api.scarf.sh/v3/insights/{SCARF_OWNER}/aggregations/export?breakdown=by-total&rollup=daily"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "tdlib-android-metrics-generator"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            lines = res.read().decode("utf-8").strip().split("\n")
            total_dl = 0
            core_dl = 0
            ktx_dl = 0
            for line in lines:
                if not line:
                    continue
                data = json.loads(line)
                tot = data.get("total", 0)
                art = data.get("artifact_name", "")
                total_dl += tot
                if "core" in art:
                    core_dl += tot
                elif "ktx" in art:
                    ktx_dl += tot

            unique_sources = 0
            try:
                origin_url = f"https://api.scarf.sh/v3/insights/{SCARF_OWNER}/aggregations/export?breakdown=by-origin&rollup=yearly"
                origin_req = urllib.request.Request(
                    origin_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "tdlib-android-metrics-generator"
                    }
                )
                with urllib.request.urlopen(origin_req, timeout=10) as origin_res:
                    origin_lines = origin_res.read().decode("utf-8").strip().split("\n")
                    origins = {
                        json.loads(l).get("origin_id")
                        for l in origin_lines
                        if l and json.loads(l).get("origin_id")
                    }
                    if origins:
                        unique_sources = len(origins)
            except Exception as e:
                print(f"Note: Could not fetch distinct origin count: {e}")

            return {
                "downloads": total_dl,
                "unique_sources": unique_sources,
                "core": core_dl,
                "ktx": ktx_dl,
            }
    except Exception as e:
        print(f"Warning: Failed to fetch stats from Scarf: {e}")
        return default_stats

def render_svg(stats, scarf_stats):
    gh_downloads = sum(s["total"] for s in stats)
    total_core = sum(s["core"] for s in stats)
    total_ktx = sum(s["ktx"] for s in stats)
    # Telemetry from Scarf (Maven Central publisher insights)
    maven_core = scarf_stats.get("core", 0)
    maven_ktx = scarf_stats.get("ktx", 0)
    maven_downloads = scarf_stats.get("downloads", 0)
    maven_unique_sources = scarf_stats.get("unique_sources", 0)
    total_downloads = gh_downloads + maven_downloads
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Global max across all bars for proportional scaling
    max_count = max([maven_core, maven_ktx] + [s["total"] for s in stats] + [1])
    bar_area_width = 440
    bar_x = 150
    view_width = 820
    row_height = 52

    # Section 1: Maven Central Packages (Scarf Telemetry)
    sec1_y = 166
    sec1_items = [
        {"name": ":core (AAR)", "meta": "Maven Central", "total": maven_core, "detail": "4 ABIs embedded", "color": "#0F7B45"},
        {"name": ":ktx (Flow)", "meta": "Maven Central", "total": maven_ktx, "detail": "coroutines wrapper", "color": "#0B6136"}
    ]
    sec1_svg = []
    for i, item in enumerate(sec1_items):
        y = sec1_y + 28 + (i * row_height)
        ratio = item["total"] / max_count
        bar_w = max(int(ratio * bar_area_width), 8)
        sec1_svg.append(f"""
        <g class="row" transform="translate(0, {y})">
            <text x="32" y="18" class="tag">{item['name']}</text>
            <text x="32" y="34" class="meta">{item['meta']}</text>
            <rect x="{bar_x}" y="8" width="{bar_area_width}" height="24" rx="5" fill="#EFEBDF" stroke="#DCD7C6" stroke-width="1" />
            <rect x="{bar_x}" y="8" width="{bar_w}" height="24" rx="5" fill="{item['color']}" />
            <text x="{bar_x + bar_w + 14}" y="25" class="bar-val">{item['total']:,} dl</text>
            <text x="690" y="24" class="breakdown">{item['detail']}</text>
        </g>
        """)

    # Section 2: GitHub Releases (Direct AAR Downloads)
    sec2_y = sec1_y + 28 + (len(sec1_items) * row_height) + 18
    sec2_svg = []
    for i, item in enumerate(stats):
        y = sec2_y + 28 + (i * row_height)
        ratio = item["total"] / max_count
        bar_w = max(int(ratio * bar_area_width), 8)
        core_ratio = item["core"] / item["total"] if item["total"] > 0 else 0
        core_w = int(bar_w * core_ratio)
        ktx_w = max(bar_w - core_w, 0)

        sec2_svg.append(f"""
        <g class="row" transform="translate(0, {y})">
            <text x="32" y="18" class="tag">{item['tag']}</text>
            <text x="32" y="34" class="meta">{item['date']}</text>
            <rect x="{bar_x}" y="8" width="{bar_area_width}" height="24" rx="5" fill="#EFEBDF" stroke="#DCD7C6" stroke-width="1" />
            <rect x="{bar_x}" y="8" width="{core_w}" height="24" rx="5" fill="#0F7B45" />
            <rect x="{bar_x + core_w}" y="8" width="{ktx_w}" height="24" rx="2" fill="#454A3D" />
            <text x="{bar_x + bar_w + 14}" y="25" class="bar-val">{item['total']:,} dl</text>
            <text x="690" y="24" class="breakdown">core: {item['core']} | ktx: {item['ktx']}</text>
        </g>
        """)

    chart_height = sec2_y + 28 + (len(stats) * row_height) + 56

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {chart_height}" width="100%" height="100%">
    <style>
        .bg {{ fill: #F7F4EC; }}
        .band {{ fill: #EFEBDF; }}
        .panel {{ fill: #FCFAF4; stroke: #DCD7C6; stroke-width: 1; }}
        .border {{ stroke: #C8C3AE; stroke-width: 1; fill: none; }}
        .rule {{ stroke: #DCD7C6; stroke-width: 1; }}
        .header-title {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 16px; font-weight: 700; fill: #191C15; }}
        .header-sub {{ font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12.5px; fill: #454A3D; }}
        .section-title {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11.5px; font-weight: 600; fill: #454A3D; }}
        .stat-label {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11px; font-weight: 500; fill: #6E7263; }}
        .stat-val-ac {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 22px; font-weight: 700; fill: #0F7B45; }}
        .stat-val {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 22px; font-weight: 700; fill: #191C15; }}
        .stat-sub {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 10.5px; fill: #6E7263; }}
        .tag {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 600; fill: #191C15; }}
        .meta {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11px; fill: #6E7263; }}
        .bar-val {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; font-weight: 600; fill: #191C15; }}
        .breakdown {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11px; fill: #454A3D; }}
        .footer-note {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 10.5px; fill: #6E7263; }}
    </style>

    <rect width="{view_width}" height="{chart_height}" rx="14" class="bg" />
    <rect x="0" y="{chart_height - 40}" width="{view_width}" height="40" rx="14" class="band" />
    <rect x="0" y="{chart_height - 40}" width="{view_width}" height="14" class="band" />
    <rect width="{view_width}" height="{chart_height}" rx="14" class="border" />

    <!-- Header Section -->
    <text x="32" y="38" class="header-title">tdlib-android / distribution telemetry</text>
    <text x="32" y="58" class="header-sub">Combined downloads across Maven Central via Scarf ({maven_downloads:,}) and GitHub Releases ({gh_downloads:,})</text>

    <!-- Metrics Cards Row -->
    <g transform="translate(32, 76)">
        <!-- Card 1: Total Merged Downloads -->
        <rect x="0" y="0" width="236" height="68" rx="8" class="panel" />
        <text x="16" y="23" class="stat-label">Total downloads (merged)</text>
        <text x="16" y="50" class="stat-val-ac">{total_downloads:,}</text>
        <text x="112" y="50" class="stat-sub">MC {maven_downloads:,} + GH {gh_downloads:,}</text>

        <!-- Card 2: Maven Central (Scarf Verified) -->
        <rect x="256" y="0" width="244" height="68" rx="8" class="panel" />
        <text x="272" y="23" class="stat-label">Maven Central (Scarf)</text>
        <text x="272" y="50" class="stat-val">{maven_downloads:,}</text>
        <text x="372" y="50" class="stat-sub">{maven_unique_sources} sources</text>

        <!-- Card 3: GitHub Releases AARs -->
        <rect x="520" y="0" width="236" height="68" rx="8" class="panel" />
        <text x="536" y="23" class="stat-label">GitHub direct AARs</text>
        <text x="536" y="50" class="stat-val">{gh_downloads:,}</text>
        <text x="614" y="50" class="stat-sub">4 ABIs · {total_core} core</text>
    </g>

    <!-- Section 1: Maven Central Packages -->
    <g>
        <text x="32" y="{sec1_y + 12}" class="section-title">Maven Central packages (Scarf)</text>
        <line x1="32" y1="{sec1_y + 20}" x2="{view_width - 32}" y2="{sec1_y + 20}" class="rule" />
        {''.join(sec1_svg)}
    </g>

    <!-- Section 2: GitHub Releases -->
    <g>
        <text x="32" y="{sec2_y + 12}" class="section-title">GitHub Releases (standalone AARs)</text>
        <line x1="32" y1="{sec2_y + 20}" x2="{view_width - 32}" y2="{sec2_y + 20}" class="rule" />
        {''.join(sec2_svg)}
    </g>

    <!-- Footer -->
    <line x1="0" y1="{chart_height - 40}" x2="{view_width}" y2="{chart_height - 40}" class="rule" />
    <text x="32" y="{chart_height - 16}" class="footer-note">Sources: Maven Central (io.github.tdlib-android via Scarf) + GitHub Releases  ·  Updated {now_utc}</text>
</svg>
"""
    return svg_content

def render_banner_svg(version):
    """
    Renders an SVG banner for the repository matching the tdlib-android engineering-datasheet design system.
    Updates the precompiled version tag and Gradle coordinates dynamically.
    """
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 350" width="100%" height="100%">
    <defs>
        <pattern id="paper-grid" width="44" height="44" patternUnits="userSpaceOnUse">
            <path d="M 44 0 L 0 0 0 44" fill="none" stroke="#DCD7C6" stroke-width="1" opacity="0.45" />
        </pattern>
        <clipPath id="banner-clip">
            <rect width="850" height="350" rx="14" />
        </clipPath>
    </defs>
    <style>
        .bg {{ fill: #F7F4EC; }}
        .band {{ fill: #EFEBDF; }}
        .border {{ stroke: #C8C3AE; stroke-width: 1; fill: none; }}
        .rule {{ stroke: #DCD7C6; stroke-width: 1; }}
        .pill-bg {{ fill: #EFEBDF; stroke: #0F7B45; stroke-width: 1; }}
        .pill-text {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11.5px; font-weight: 600; fill: #0F7B45; }}
        .title {{ font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 30px; font-weight: 700; fill: #191C15; letter-spacing: -0.02em; }}
        .subtitle {{ font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14.5px; fill: #454A3D; }}
        .specs {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; fill: #6E7263; }}
        .term-box {{ fill: #141714; stroke: #2B2F28; stroke-width: 1; }}
        .term-head {{ fill: #1B1F1A; }}
        .term-rule {{ stroke: #2B2F28; stroke-width: 1; }}
        .term-file {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11.5px; fill: #A3AE9F; }}
        .term-comment {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; fill: #A3AE9F; }}
        .term-fn {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; fill: #8ECBE0; }}
        .term-str {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; fill: #56D68B; }}
        .term-punct {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; fill: #D9E1D5; }}
        .meta-text {{ font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 11.5px; fill: #454A3D; }}
    </style>

    <g clip-path="url(#banner-clip)">
        <rect width="850" height="350" class="bg" />
        <rect width="850" height="350" fill="url(#paper-grid)" />
        <rect x="0" y="306" width="850" height="44" class="band" />
        <line x1="0" y1="306" x2="850" y2="306" class="rule" />
    </g>
    <rect width="850" height="350" rx="14" class="border" />

    <!-- Version & Spec Tag (untracked sentence-case mono per DESIGN.md) -->
    <rect x="40" y="28" width="338" height="26" rx="5" class="pill-bg" />
    <text x="52" y="45" class="pill-text">v{version}  ·  prebuilt AAR  ·  4 ABIs  ·  zero NDK</text>

    <!-- Main Title & Specs -->
    <text x="40" y="90" class="title">Precompiled TDLib for Android</text>
    <text x="40" y="116" class="subtitle">Signed Maven Central AARs with Kotlin Coroutines and Flow. Zero local NDK.</text>
    <text x="40" y="140" class="specs">arm64-v8a  ✳  armeabi-v7a  ✳  x86_64  ✳  x86  ✳  Android 15 16KB page aligned</text>

    <!-- Dark Terminal Instrument (plain filename bar, no OS dots per DESIGN.md) -->
    <rect x="40" y="164" width="770" height="120" rx="8" class="term-box" />
    <rect x="41" y="165" width="768" height="30" rx="7" class="term-head" />
    <line x1="40" y1="195" x2="810" y2="195" class="term-rule" />
    <text x="794" y="184" text-anchor="end" class="term-file">app/build.gradle.kts</text>
    <text x="60" y="218" class="term-comment">// Drop-in dependencies — no CMake or NDK setup</text>
    <text x="60" y="244">
        <tspan class="term-fn">implementation</tspan><tspan class="term-punct">(</tspan><tspan class="term-str">"io.github.tdlib-android:core:{version}"</tspan><tspan class="term-punct">)</tspan>
    </text>
    <text x="60" y="268">
        <tspan class="term-fn">implementation</tspan><tspan class="term-punct">(</tspan><tspan class="term-str">"io.github.tdlib-android:ktx:{version}"</tspan><tspan class="term-punct">)</tspan>
    </text>

    <!-- Footer Band -->
    <text x="40" y="332" class="meta-text">Maven Central + GitHub Releases  ·  BSL-1.0 / Apache-2.0</text>
    <text x="810" y="332" text-anchor="end" class="meta-text">tdlib-android.vercel.app</text>
</svg>"""
    return svg

def main():
    stats = fetch_release_stats()
    if not stats:
        # Fallback cache if rate limited
        stats = [
            {"tag": "v0.1.1", "date": "2026-09-13", "core": 51, "ktx": 24, "checksums": 6, "total": 81},
            {"tag": "v0.1.0", "date": "2026-06-17", "core": 536, "ktx": 133, "checksums": 34, "total": 703},
        ]
    scarf_stats = fetch_scarf_stats()
    svg = render_svg(stats, scarf_stats)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Rendered {OUTPUT_SVG} with {len(stats)} releases.")

    # Write dynamic badge JSON endpoint for Shields.io (Total Merged: GitHub Releases + Maven Central/Scarf)
    gh_downloads = sum(s["total"] for s in stats)
    total_downloads = gh_downloads + scarf_stats.get("downloads", 0)
    badge_data = {
        "schemaVersion": 1,
        "label": "downloads",
        "message": f"{total_downloads:,}+",
        "color": "27a644"
    }
    with open("docs/downloads-badge.json", "w", encoding="utf-8") as f:
        json.dump(badge_data, f, indent=2)
    print(f"Rendered docs/downloads-badge.json with {gh_downloads:,}+ GitHub downloads.")

    # Determine latest version for banner
    latest_version = "0.1.1"
    if stats and stats[0].get("tag") and stats[0]["tag"] != "unknown":
        latest_version = stats[0]["tag"].lstrip("v")
    else:
        try:
            with open("VERSION", "r", encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    latest_version = v
        except Exception:
            pass

    # Render dynamic banner SVG
    banner_svg = render_banner_svg(latest_version)
    with open(OUTPUT_BANNER_SVG, "w", encoding="utf-8") as f:
        f.write(banner_svg)
    print(f"Rendered {OUTPUT_BANNER_SVG} for version v{latest_version}.")

if __name__ == "__main__":
    main()
