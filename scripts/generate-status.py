#!/usr/bin/env python3
"""Generate a live server-status SVG for the Ashu4463 profile README.

Checks 3 sites (HTTP status + DNS + response time) and writes
assets/server-status.svg. Run by .github/workflows/server-status.yml
every 15 minutes. No third-party dependencies — stdlib only.
"""
import socket
import time
import urllib.request
from datetime import datetime, timezone

SITES = [
    ("mydnsreport.com", "https://mydnsreport.com"),
    ("toolsbudy.com", "https://toolsbudy.com"),
    ("github.com", "https://github.com"),
]

OUT = "assets/server-status.svg"


def check(name, url):
    host = url.split("://", 1)[1].split("/", 1)[0]
    dns_ms = None
    try:
        t0 = time.monotonic()
        socket.getaddrinfo(host, 443)
        dns_ms = (time.monotonic() - t0) * 1000
    except Exception:
        pass
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Ashu4463-status-check/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 0
    total_ms = (time.monotonic() - t0) * 1000
    if 200 <= code < 400:
        status, color = f"ONLINE · {code}", "#3fb950"
    elif code:
        status, color = f"ERROR · {code}", "#d29922"
    else:
        status, color = "DOWN", "#f85149"
    ms = f"{total_ms:.0f} ms" + (f" · DNS {dns_ms:.0f} ms" if dns_ms is not None else "")
    return {"name": name, "url": url, "status": status, "color": color, "ms": ms}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    results = [check(n, u) for n, u in SITES]
    updated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    row_h, top = 38, 62
    height = top + len(results) * row_h + 34
    rows = []
    for i, r in enumerate(results):
        y = top + i * row_h
        rows.append(
            f'  <circle cx="28" cy="{y + 9}" r="6" fill="{r["color"]}"/>'
            f'<text x="46" y="{y + 13}" font-family="monospace" font-size="15" fill="#e6edf3">{esc(r["name"])}</text>'
            f'<text x="46" y="{y + 28}" font-family="monospace" font-size="11" fill="#7d8590">{esc(r["url"])}</text>'
            f'<text x="560" y="{y + 13}" font-family="monospace" font-size="13" font-weight="bold" fill="{r["color"]}" text-anchor="end">{esc(r["status"])}</text>'
            f'<text x="560" y="{y + 28}" font-family="monospace" font-size="11" fill="#7d8590" text-anchor="end">{esc(r["ms"])}</text>'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="%d" viewBox="0 0 600 %d">'
        '<rect x="1" y="1" width="598" height="%d" rx="10" fill="#0d1117" stroke="#30363d"/>'
        '<text x="20" y="32" font-family="monospace" font-size="15" font-weight="bold" fill="#3fb950">\u25cf LIVE</text>'
        '<text x="86" y="32" font-family="monospace" font-size="15" font-weight="bold" fill="#e6edf3">SERVER STATUS</text>'
        '<text x="580" y="32" font-family="monospace" font-size="11" fill="#7d8590" text-anchor="end">auto-refresh · 15 min</text>'
        '%s'
        '<text x="20" y="%d" font-family="monospace" font-size="11" fill="#7d8590">Updated %s · github.com/Ashu4463</text>'
        '</svg>'
        % (height, height, height - 2, "".join(rows), height - 12, updated)
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({len(results)} sites, updated {updated})")


if __name__ == "__main__":
    main()
