#!/usr/bin/env python3
"""Draws the prerequisite graph of my degree from data/modules.json.

    python3 scripts/make_graph.py

Writes:
  assets/prerequisites.svg   animated picture for the README
  data/modules.cypher        the same graph as a Neo4j script
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "modules.json").read_text(encoding="utf-8"))
mods = {m["code"]: m for m in D["modules"]}
SANS = "font-family:Montserrat,'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# ------------------------------------------------------------------ layout
children = {c: [] for c in mods}
for m in mods.values():
    for p in m["prereqs"]:
        children[p].append(m["code"])

depth = {}
def level(c):
    if c not in depth:
        depth[c] = 0 if not mods[c]["prereqs"] else 1 + max(level(p) for p in mods[c]["prereqs"])
    return depth[c]
for c in mods:
    level(c)
NL = max(depth.values()) + 1
layers = [[c for c in mods if depth[c] == i] for i in range(NL)]

W, NW, NH, MX = 1000, 150, 44, 40
MINGAP = 62
GAP = (W - 2 * MX - NL * NW) / (NL - 1)
X = [MX + i * (NW + GAP) for i in range(NL)]

y = {c: m["y"] for c, m in mods.items() if "y" in m}                     # modules whose position is pinned in modules.json

def settle(codes, want):
    order = sorted(codes, key=lambda c: want[c])
    pos = {}
    for i, c in enumerate(order):
        pos[c] = max(want[c], pos[order[i - 1]] + MINGAP if i else -1e9)
    for _ in range(3):                                                    # keep the group centred on where its nodes want to be
        shift = (sum(want.values()) - sum(pos.values())) / len(pos)
        for c in pos:
            pos[c] += shift
        for i in range(1, len(order)):
            pos[order[i]] = max(pos[order[i]], pos[order[i - 1]] + MINGAP)
    return pos

def mean(vals):
    vals = list(vals)
    return sum(vals) / len(vals)

for i in range(NL - 1, -1, -1):                                           # un-pinned modules sit level with what they unlock...
    todo = [c for c in layers[i] if c not in y and any(k in y for k in children[c])]
    if todo:
        y.update(settle(todo, {c: mean(y[k] for k in children[c] if k in y) for c in todo}))
for i in range(NL):                                                       # ...or with their prerequisites
    todo = [c for c in layers[i] if c not in y]
    if todo:
        y.update(settle(todo, {c: mean(y[p] for p in mods[c]["prereqs"] if p in y) for c in todo}))

H = int(max(y.values()) + NH + 150)
node = {c: (X[depth[c]], y[c]) for c in mods}

def edge_path(a, b):
    xs, ys = node[a][0] + NW, node[a][1] + NH / 2
    xt, yt = node[b][0], node[b][1] + NH / 2
    dx = (xt - xs) * 0.5
    return xs, ys, xt, yt, f"M{xs:.1f} {ys:.1f} C{xs+dx:.1f} {ys:.1f} {xt-dx:.1f} {yt:.1f} {xt:.1f} {yt:.1f}"

def crossings():
    """edges that run through a node that is not one of their own ends"""
    bad = []
    for b, m in mods.items():
        for a in m["prereqs"]:
            xs, ys, xt, yt, _ = edge_path(a, b)
            dx = (xt - xs) * 0.5
            for k in range(1, 60):
                t = k / 60
                px = (1-t)**3*xs + 3*(1-t)**2*t*(xs+dx) + 3*(1-t)*t**2*(xt-dx) + t**3*xt
                py = (1-t)**3*ys + 3*(1-t)**2*t*ys + 3*(1-t)*t**2*yt + t**3*yt
                for c, (nx, ny) in node.items():
                    if c not in (a, b) and nx - 3 < px < nx + NW + 3 and ny - 3 < py < ny + NH + 3:
                        bad.append((a, b, c)); break
                else:
                    continue
                break
    return bad

# ------------------------------------------------------------------ the picture
STATUS = {
    "distinction": dict(stroke="url(#goldS)", code="#fbbf24", fill="#17144a", w=1.8, filt=' filter="url(#glow)"', dash=""),
    "passed":      dict(stroke="#6573c9", code="#9fb4ff", fill="#0e1138", w=1.2, filt="", dash=""),
    "in-progress": dict(stroke="#a78bfa", code="#c4b5fd", fill="#0e1138", w=1.4, filt="", dash=' stroke-dasharray="5 4"'),
}

def edge_svg(a, b):
    xs, ys, xt, yt, d = edge_path(a, b)
    hot = mods[b]["status"] == "distinction" and mods[a]["status"] == "distinction"
    return (f'<path class="edge" data-from="{a}" data-to="{b}" d="{d}" fill="none" stroke="url(#edge)" stroke-opacity="{.55 if hot else .3}" stroke-width="{1.6 if hot else 1.2}"/>'
            f'<path class="flow" data-from="{a}" data-to="{b}" style="animation-delay:{-(hash(a+b) % 26)/10:.1f}s" d="{d}" fill="none" stroke="url(#edge)" stroke-width="{2.1 if hot else 1.5}" stroke-linecap="round"/>'
            f'<path class="tip" d="M{xt-9:.1f} {yt-5:.1f} L{xt-1:.1f} {yt:.1f} L{xt-9:.1f} {yt+5:.1f}" fill="none" stroke="#a5b4fc" stroke-opacity=".7" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')

def node_svg(c, delay):
    m = mods[c]; x0, y0 = node[c]; s = STATUS[m["status"]]
    out = [f'<g class="node fade {m["status"]}" data-code="{c}" style="animation-delay:{delay:.2f}s">',
           f'<rect x="{x0}" y="{y0}" width="{NW}" height="{NH}" rx="10" fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="{s["w"]}"{s["dash"]}{s["filt"]}/>',
           f'<text style="{MONO}" x="{x0+12}" y="{y0+18}" font-size="13" font-weight="800" fill="{s["code"]}">{c}</text>',
           f'<text style="{SANS}" x="{x0+12}" y="{y0+34}" font-size="10.5" fill="#c7cdf0">{escape(m["name"])}</text>']
    if m["status"] == "distinction":
        top = m["mark"] == max(x.get("mark", 0) for x in mods.values())
        out.append(f'<circle cx="{x0+NW-1}" cy="{y0+1}" r="{15 if top else 13}" fill="url(#goldF)"{" filter=\"url(#glow)\"" if top else ""}/>'
                   f'<text style="{SANS}" x="{x0+NW-1}" y="{y0+6}" text-anchor="middle" font-size="{13 if top else 12}" font-weight="800" fill="#2a1b04">{m["mark"]}</text>')
    elif m["status"] == "in-progress":
        out.append(f'<text class="pulse" style="{SANS}" x="{x0+NW-10}" y="{y0+18}" text-anchor="end" font-size="8.5" font-weight="800" letter-spacing="1.2" fill="#c4b5fd">IN PROGRESS</text>')
    out.append("</g>")
    return "".join(out)

def build_svg(interactive=False):
    edges = "".join(edge_svg(a, b) for b, m in mods.items() for a in m["prereqs"])
    nodes = "".join(node_svg(c, 0.1 + depth[c] * 0.18 + (i % 4) * 0.03) for i, c in enumerate(sorted(mods, key=lambda c: (depth[c], y[c]))))
    ly = H - 52
    legend = (f'<g transform="translate(40 {ly})">'
              f'<rect x="0" y="0" width="34" height="20" rx="6" fill="#17144a" stroke="url(#goldS)" stroke-width="1.6"/><circle cx="34" cy="1" r="8" fill="url(#goldF)"/>'
              f'<text style="{SANS}" x="46" y="14" font-size="11" fill="#c7cdf0">Distinction (75 and above), with the mark</text>'
              f'<rect x="290" y="0" width="34" height="20" rx="6" fill="#0e1138" stroke="#6573c9" stroke-width="1.2"/>'
              f'<text style="{SANS}" x="336" y="14" font-size="11" fill="#c7cdf0">Passed</text>'
              f'<rect x="410" y="0" width="34" height="20" rx="6" fill="#0e1138" stroke="#a78bfa" stroke-width="1.4" stroke-dasharray="4 3"/>'
              f'<text style="{SANS}" x="456" y="14" font-size="11" fill="#c7cdf0">In progress</text>'
              f'<text style="{SANS}" x="{W-80}" y="14" text-anchor="end" font-size="11" fill="#8b9bd8">Read left to right: an arrow means needed before</text></g>'
              f'<text style="{SANS}" x="40" y="{H-14}" font-size="10" fill="#6f7bb0">Prerequisites from the {escape(D["source"])}. Alternative routes and programme-admission conditions are left out.</text>')
    extra = ('.node{cursor:pointer}.dim{opacity:.16!important;transition:opacity .15s}.up .node-box{}'
             '.edge.on,.flow.on{stroke-opacity:1!important}.edge.on{stroke:#fbbf24!important}.hl-up rect:first-of-type{stroke:#38bdf8!important;stroke-width:2.2!important}'
             '.hl-down rect:first-of-type{stroke:#fbbf24!important;stroke-width:2.2!important}.hl-self rect:first-of-type{stroke:#fff!important;stroke-width:2.6!important}') if interactive else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Prerequisite graph of my BSc Computer Science modules at the University of Pretoria">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070a1f"/><stop offset=".55" stop-color="#15104a"/><stop offset="1" stop-color="#090c28"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
  <linearGradient id="goldS" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#f59e0b"/></linearGradient>
  <linearGradient id="goldF" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#fbbf24"/></linearGradient>
  <linearGradient id="nm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#a5b4fc"/></linearGradient>
  <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#6366f1" stop-opacity=".34"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#8aa4ff" fill-opacity=".07"/></pattern>
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  .flow{{stroke-dasharray:4 12;animation:flow 3.2s linear infinite;stroke-opacity:.8}} @keyframes flow{{to{{stroke-dashoffset:-32}}}}
  .fade{{animation:fade .8s ease both}} @keyframes fade{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  .pulse{{animation:pulse 2.4s ease-in-out infinite}} @keyframes pulse{{50%{{opacity:.35}}}}
  .sweep{{animation:sweep 9s linear infinite}} @keyframes sweep{{from{{transform:translateY(-6px)}}to{{transform:translateY({H+6}px)}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  {extra}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <ellipse cx="{W*0.62:.0f}" cy="{H/2:.0f}" rx="420" ry="{H*0.5:.0f}" fill="url(#halo)"/>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
  <rect class="sweep" width="{W}" height="2" fill="url(#edge)" opacity=".18"/>
  <text style="{SANS}" x="40" y="46" font-size="12.5" font-weight="700" letter-spacing="3" fill="#8b9bd8">PREREQUISITE GRAPH</text>
  <rect x="40" y="60" width="56" height="3" rx="1.5" fill="url(#edge)"/>
  <text style="{SANS}" x="40" y="84" font-size="19" font-weight="800" fill="url(#nm)">BSc Computer Science, University of Pretoria: {len(mods)} modules, {sum(len(m["prereqs"]) for m in mods.values())} prerequisites</text>
  <g>{edges}</g>
  <g>{nodes}</g>
  {legend}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#8b7cf6" stroke-opacity=".28"/>
</svg>
'''

# ------------------------------------------------------------------ interactive page
def build_html():
    svg = build_svg(interactive=True)
    data = {c: dict(name=m["full"], status=m["status"], mark=m.get("mark"), year=m["year"], prereqs=m["prereqs"]) for c, m in mods.items()}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Alessandro Paravano - my degree as a graph</title>
<style>
  body{{margin:0;background:#070a1f;color:#e5e7ff;font:15px/1.5 {SANS.split(":",1)[1]};padding:24px 16px 60px}}
  main{{max-width:1040px;margin:0 auto}} h1{{font-size:1.4rem;margin:0 0 4px}} p{{color:#aab3e6;margin:0 0 16px}}
  .wrap{{overflow-x:auto;border-radius:18px}} svg{{display:block;width:100%;min-width:760px;height:auto}}
  #panel{{margin-top:16px;padding:16px 18px;border:1px solid rgba(139,124,246,.3);border-radius:14px;background:#0e1138;min-height:118px}}
  #panel b{{color:#fff}} #panel small{{color:#8b9bd8;letter-spacing:.14em;text-transform:uppercase;font-size:11px;font-weight:700}}
  pre{{margin:10px 0 0;padding:12px 14px;border-radius:10px;background:#070a1f;color:#7dd3fc;font:13px/1.5 {MONO.split(":",1)[1]};overflow-x:auto}}
  .k{{color:#c4b5fd}} .s{{color:#fbbf24}}
</style></head><body><main>
<h1>My degree, as a graph</h1>
<p>Hover (or tap) a module. <span style="color:#38bdf8">Blue</span> modules are what it needed, <span style="color:#fbbf24">gold</span> ones are what it unlocks.</p>
<div class="wrap">{svg}</div>
<div id="panel"><small>Neo4j, if I had used it</small><pre id="q"><span class="k">MATCH</span> (m:Module) <span class="k">RETURN</span> m   <span style="color:#6f7bb0">// pick a module above</span></pre></div>
</main>
<script>
const D = {json.dumps(data)};
const svg = document.querySelector("svg"), nodes = [...svg.querySelectorAll(".node")], edges = [...svg.querySelectorAll(".edge,.flow,.tip")];
const kids = {{}}; for (const c in D) kids[c] = Object.keys(D).filter(k => D[k].prereqs.includes(c));
const walk = (c, next) => {{ const out = new Set(), todo = [c]; while (todo.length) for (const n of next(todo.pop())) if (!out.has(n)) {{ out.add(n); todo.push(n); }} return out; }};
function show(code) {{
  const up = walk(code, c => D[c].prereqs), down = walk(code, c => kids[c]);
  nodes.forEach(n => {{ const c = n.dataset.code; n.classList.remove("hl-up","hl-down","hl-self","dim");
    if (c === code) n.classList.add("hl-self"); else if (up.has(c)) n.classList.add("hl-up"); else if (down.has(c)) n.classList.add("hl-down"); else n.classList.add("dim"); }});
  svg.querySelectorAll(".edge,.flow").forEach(e => {{ const f = e.dataset.from, t = e.dataset.to;
    const inUp = (up.has(f) || f === code) && (up.has(t) || t === code) , inDown = (down.has(t) || t === code) && (down.has(f) || f === code);
    e.classList.toggle("on", inUp || inDown); e.classList.toggle("dim", !(inUp || inDown)); }});
  svg.querySelectorAll(".tip").forEach(e => e.classList.add("dim"));
  const d = D[code], list = a => [...a].sort().join(", ") || "none";
  const mark = d.mark ? ` · <b style="color:#fbbf24">${{d.mark}}%</b>` : "";
  document.getElementById("panel").innerHTML = `<small>${{d.status.replace("-", " ")}} · ${{d.year}}</small><br><b>${{code}}</b> ${{d.name}}${{mark}}<br>
    <span style="color:#38bdf8">needs:</span> ${{list(up)}} &nbsp; <span style="color:#fbbf24">unlocks:</span> ${{list(down)}}
    <pre><span class="k">MATCH</span> path = (m:Module)-[:<span class="s">PREREQUISITE_OF</span>*]-&gt;(:Module {{code: <span class="s">"${{code}}"</span>}})
<span class="k">RETURN</span> path   <span style="color:#6f7bb0">// ${{up.size}} module${{up.size === 1 ? "" : "s"}} on the way in, ${{down.size}} on the way out</span></pre>`;
}}
function clear() {{ nodes.forEach(n => n.classList.remove("hl-up","hl-down","hl-self","dim")); edges.forEach(e => e.classList.remove("on","dim")); }}
nodes.forEach(n => {{ n.addEventListener("mouseenter", () => show(n.dataset.code)); n.addEventListener("click", () => show(n.dataset.code)); n.addEventListener("mouseleave", clear); }});
</script></body></html>
'''

# ------------------------------------------------------------------ Neo4j script
def build_cypher():
    lines = ["// My degree as a Neo4j graph. Paste into Neo4j Browser (or `cypher-shell < modules.cypher`).",
             f"// Source: {D['source']}.  Regenerate with: python3 scripts/make_graph.py", ""]
    for c, m in sorted(mods.items()):
        mark = f", mark: {m['mark']}" if "mark" in m else ""
        lines.append(f"CREATE (:Module {{code: '{c}', name: '{m['full'].replace(chr(39), '')}', year: {m['year']}, status: '{m['status']}'{mark}}});")
    lines.append("")
    for c, m in sorted(mods.items()):
        for p in m["prereqs"]:
            lines.append(f"MATCH (a:Module {{code: '{p}'}}), (b:Module {{code: '{c}'}}) CREATE (a)-[:PREREQUISITE_OF]->(b);")
    lines += ["", "// The long way to the capstone:",
              "// MATCH path = (:Module {code: 'COS110'})-[:PREREQUISITE_OF*]->(:Module {code: 'COS301'}) RETURN path;", "",
              "// The most connected module (spoiler: COS 110, with eight dependants):",
              "// MATCH (m:Module)-[r:PREREQUISITE_OF]->() RETURN m.code, count(r) AS unlocks ORDER BY unlocks DESC LIMIT 3;"]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    bad = crossings()
    (ROOT / "assets" / "prerequisites.svg").write_text(build_svg(), encoding="utf-8")
    (ROOT / "data" / "modules.cypher").write_text(build_cypher(), encoding="utf-8")
    print(f"{len(mods)} modules, {sum(len(m['prereqs']) for m in mods.values())} edges, {NL} layers, canvas {W}x{H}")
    print("edges running through an unrelated node:", bad or "none")
    for i, L in enumerate(layers):
        print(f"  layer {i} ({D['layers'][i]}):", ", ".join(f"{c}@{y[c]:.0f}" for c in sorted(L, key=lambda c: y[c])))
