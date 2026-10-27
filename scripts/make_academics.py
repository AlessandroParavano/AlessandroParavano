#!/usr/bin/env python3
"""Draws assets/academics.svg (an animated results card) from data/academics.json.

    python3 scripts/make_academics.py
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "academics.json").read_text(encoding="utf-8"))
rows = sorted(d["highlights"], key=lambda r: (-r["mark"], r["code"]))
top = rows[0]["mark"]

W, PAD = 600, 36
TRACK_X, TRACK_W = PAD, 440
Y0, PITCH = 330, 46
H = Y0 + (len(rows) - 1) * PITCH + 76
dist_x = TRACK_X + TRACK_W * d["distinction_from"] / 100

bars, labels, grid = [], [], []
for i, r in enumerate(rows):
    y = Y0 + i * PITCH
    w = TRACK_W * r["mark"] / 100
    best = r["mark"] == top
    delay = 0.25 + i * 0.09
    grid.append(f'<rect x="{TRACK_X}" y="{y+9}" width="{TRACK_W}" height="10" rx="5" fill="#8aa4ff" fill-opacity=".08"/>')
    bars.append(f'<rect class="bar" style="animation-delay:{delay:.2f}s" x="{TRACK_X}" y="{y+9}" width="{w:.1f}" height="10" rx="5" fill="url(#{"gold" if best else "acc"})"{" filter=\"url(#glowf)\"" if best else ""}/>')
    labels.append(f'<g class="fade" style="animation-delay:{delay:.2f}s">'
                  f'<text class="mono" x="{PAD}" y="{y}" font-size="14" font-weight="700" fill="{"#fbbf24" if best else "#7dd3fc"}">{escape(r["code"])}</text>'
                  f'<text class="sans" x="{PAD+68}" y="{y}" font-size="14.5" fill="#e5e7ff">{escape(r["name"])}</text>'
                  f'<text class="sans" x="{TRACK_X + w + 10:.1f}" y="{y+19}" font-size="15" font-weight="800" fill="{"#fde68a" if best else "#ffffff"}">{r["mark"]}</text>'
                  + '</g>')

# yearly weighted averages as small columns (third stat)
yrs = d["years"]
base_y, col_h = 196, 64
cols = []
for i, y in enumerate(yrs):
    h = col_h * y["average"] / 100
    x = 372 + i * 64
    cols.append(f'<rect class="col" style="animation-delay:{0.6+i*0.15:.2f}s" x="{x}" y="{base_y-h:.1f}" width="44" height="{h:.1f}" rx="6" fill="url(#acc)" fill-opacity="{".55" if y.get("partial") else ".95"}"/>'
                f'<text class="sans fade" style="animation-delay:{0.9+i*0.15:.2f}s" x="{x+22}" y="{base_y-h-8:.1f}" text-anchor="middle" font-size="15" font-weight="800" fill="#fff">{y["average"]:.0f}</text>'
                f'<text class="mono" x="{x+22}" y="{base_y+17}" text-anchor="middle" font-size="12" fill="#8b9bd8">{y["year"]}{"*" if y.get("partial") else ""}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Academic highlights: {d["distinctions"]} distinctions, top mark {top} percent in {escape(rows[0]["name"])}, cumulative average {d["cumulative_average"]:.1f} percent">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070a1f"/><stop offset=".55" stop-color="#15104a"/><stop offset="1" stop-color="#090c28"/></linearGradient>
  <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fbbf24"/><stop offset="1" stop-color="#fde68a"/></linearGradient>
  <linearGradient id="num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#a5b4fc"/></linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#6366f1" stop-opacity=".38"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#8aa4ff" fill-opacity=".07"/></pattern>
  <filter id="glowf" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  .sans{{font-family:Montserrat,"Segoe UI","Helvetica Neue",Arial,sans-serif}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}}
  .bar,.col{{transform-box:fill-box;animation:grow 1.1s cubic-bezier(.2,.8,.2,1) both}}
  .bar{{transform-origin:left center}} .col{{transform-origin:center bottom;animation-name:rise}}
  @keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
  @keyframes rise{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
  .fade{{animation:fade .7s ease both}}
  @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <ellipse cx="{W*0.7:.0f}" cy="170" rx="300" ry="200" fill="url(#glow)"/>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>

  <text class="sans" x="{PAD}" y="48" font-size="13" font-weight="600" letter-spacing="3" fill="#8b9bd8">ACADEMIC HIGHLIGHTS</text>
  <rect x="{PAD}" y="62" width="56" height="3" rx="1.5" fill="url(#acc)"/>
  <text class="sans" x="{PAD}" y="94" font-size="19" font-weight="800" fill="url(#num)">{escape(d["programme"])}</text>

  <g class="fade" style="animation-delay:.4s">
    <text class="sans" x="{PAD}" y="196" font-size="64" font-weight="800" fill="url(#num)">{d["distinctions"]}</text>
    <text class="sans" x="{PAD}" y="246" font-size="12" font-weight="700" letter-spacing="2" fill="#8b9bd8">DISTINCTIONS</text>
    <text class="sans" x="196" y="196" font-size="40" font-weight="800" fill="url(#num)">{d["cumulative_average"]:.1f}%</text>
    <text class="sans" x="196" y="246" font-size="12" font-weight="700" letter-spacing="2" fill="#8b9bd8">CUMULATIVE AVG</text>
    <text class="sans" x="372" y="246" font-size="12" font-weight="700" letter-spacing="2" fill="#8b9bd8">YEARLY AVERAGE</text>
  </g>
  {"".join(cols)}
  <line x1="{PAD}" y1="270" x2="{W-PAD}" y2="270" stroke="#8b7cf6" stroke-opacity=".25"/>

  <text class="sans" x="{PAD}" y="298" font-size="13" fill="#8b9bd8">Selected modules, marks out of 100</text>
  <g>{"".join(grid)}</g>
  <line x1="{dist_x:.1f}" y1="{Y0-16}" x2="{dist_x:.1f}" y2="{Y0+(len(rows)-1)*PITCH+24}" stroke="#a78bfa" stroke-opacity=".6" stroke-dasharray="3 5"/>
  <text class="sans" x="{dist_x:.1f}" y="{Y0-26}" text-anchor="middle" font-size="10.5" font-weight="700" letter-spacing="1.5" fill="#a78bfa">DISTINCTION {d["distinction_from"]}+</text>
  <g>{"".join(bars)}</g>
  {"".join(labels)}

  <text class="sans" x="{PAD}" y="{H-22}" font-size="11.5" fill="#6f7bb0">As at {d["updated"]}.  * 2026 so far (final year in progress).</text>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#8b7cf6" stroke-opacity=".28"/>
</svg>
'''
(ROOT / "assets" / "academics.svg").write_text(svg, encoding="utf-8")
print(f"assets/academics.svg: {len(rows)} modules, {d['distinctions']} distinctions, size {W}x{H}")
