#!/usr/bin/env python3
"""Build aap-web/new-pools.html from the scraped Wix design list.

Reads /tmp/pools.tsv (media_id <tab> original filename), downloads a web-sized
copy of each pool image into assets/pools/, and generates new-pools.html using
the same look as index.html. One-off tool; re-runnable.
"""
import os, re, sys, html, urllib.request, pathlib, time

ROOT = pathlib.Path(__file__).parent
IMGDIR = ROOT / "assets" / "pools"
IMGDIR.mkdir(parents=True, exist_ok=True)
TSV = os.path.join(os.path.dirname(__file__), "_pools.tsv")

WIX = "https://static.wixstatic.com/media/{id}/v1/fill/w_1000,h_750,al_c,q_80/{id}"

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "pool"

def parse(line):
    mid, fname = line.rstrip("\n").split("\t", 1)
    base = re.sub(r"\.(jpe?g|png)$", "", fname, flags=re.I).strip()
    base = re.sub(r"\s+", " ", base)
    # skip obvious non-models
    if re.match(r"^(20\d{6}|whatsapp image|img[-_ ])", base, re.I):
        return None
    if base.upper().startswith("ALSO AVAILABLE"):
        return None
    name, dims, length = base, "", None
    m = re.match(r"^(.*?)\s*[-–]\s*(.+)$", base)
    if m and re.search(r"\d", m.group(2)):
        name, dims = m.group(1).strip(), m.group(2).strip()
    # round pools: "3M ROUND X 1.45 DEEP"
    rnd = re.search(r"([\d.]+)\s*M?\s*ROUND", dims, re.I) or re.search(r"([\d.]+)\s*M?\s*ROUND", base, re.I)
    if rnd:
        length = float(rnd.group(1))
        dims = dims or (base_after_dash(base))
    else:
        d = re.search(r"([\d.]+)\s*[xX]\s*([\d.]+(?:-[\d.]+)?)\s*[xX]\s*([\d.]+(?:-[\d.]+)?)", dims or base)
        if d:
            length = float(d.group(1))
            dims = "{} x {} x {} m".format(d.group(1), d.group(2), d.group(3))
    if length is None:
        # last resort: trailing number in the name = length
        n = re.search(r"(\d+(?:\.\d+)?)\s*$", name)
        if n:
            length = float(n.group(1))
    if length is None:
        return None
    bucket = min(10, max(2, int(length // 1) if length >= 2 else 2))
    return dict(id=mid, name=name.title().replace("Lappool", "Lap Pool"),
                dims=dims, length=length, bucket=bucket, slug=slugify(base))

def base_after_dash(b):
    m = re.match(r"^.*?[-–]\s*(.+)$", b)
    return m.group(1).strip() if m else ""

rows = []
seen = set()
for line in open(TSV, encoding="utf-8"):
    if not line.strip():
        continue
    r = parse(line)
    if not r:
        continue
    key = (r["name"], r["dims"])
    if key in seen:
        continue
    seen.add(key)
    rows.append(r)

rows.sort(key=lambda r: (r["bucket"], r["length"], r["name"]))
print(f"{len(rows)} designs parsed")

# download
ua = {"User-Agent": "Mozilla/5.0"}
for r in rows:
    dest = IMGDIR / (r["slug"] + ".jpg")
    r["file"] = f"assets/pools/{dest.name}"
    if dest.exists() and dest.stat().st_size > 3000:
        continue
    url = WIX.format(id=r["id"])
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=ua)
            data = urllib.request.urlopen(req, timeout=30).read()
            dest.write_bytes(data)
            print(f"  {dest.name}  {len(data)//1024} KB")
            break
        except Exception as e:
            print(f"  retry {dest.name}: {e}")
            time.sleep(2)
    else:
        print(f"  FAILED {dest.name}")

# group
from collections import OrderedDict
groups = OrderedDict()
for r in rows:
    groups.setdefault(r["bucket"], []).append(r)

STYLE = (ROOT / "index.html").read_text(encoding="utf-8")
style = STYLE[STYLE.index("<style>"):STYLE.index("</style>") + len("</style>")]

def esc(s): return html.escape(s, quote=True)

cards = []
navbits = []
for b, items in groups.items():
    navbits.append(f'<a href="#r{b}">{b}m</a>')
    cards.append(f'<h2 id="r{b}" style="margin-top:1.2em">{b} metre range</h2>')
    cards.append('<div class="poolgrid">')
    for r in items:
        dims = f'<p class="dims">{esc(r["dims"])}</p>' if r["dims"] else ""
        cards.append(f'''  <figure class="pcard">
    <img loading="lazy" src="{r['file']}" alt="{esc(r['name'])} fibreglass pool {esc(r['dims'])}">
    <figcaption>
      <h3>{esc(r['name'])}</h3>
      {dims}
      <a href="index.html#contact">Get a quote for this design &rarr;</a>
    </figcaption>
  </figure>''')
    cards.append('</div>')

PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New Fibreglass Pools &mdash; Shapes &amp; Sizes | All About Pools Cape Town</title>
<meta name="description" content="Browse our full range of fibreglass swimming pool designs, from 2 metre plunge pools to 10 metre lap pools. Supplied and installed across Cape Town's northern suburbs.">
{style}
<style>
  .poolnav{{position:sticky;top:74px;z-index:40;background:rgba(255,255,255,.97);border-bottom:1px solid var(--line);padding:12px 0}}
  .poolnav .wrap{{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}}
  .poolnav a{{padding:7px 14px;border:1px solid var(--line);border-radius:999px;font-weight:700;font-size:.86rem;color:var(--navy)}}
  .poolnav a:hover{{background:var(--blue);color:#fff;border-color:var(--blue)}}
  .poolgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin:22px 0 46px}}
  .pcard{{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;transition:.18s}}
  .pcard:hover{{transform:translateY(-4px);box-shadow:0 14px 34px rgba(11,42,59,.13)}}
  .pcard img{{width:100%;height:230px;object-fit:cover;background:var(--sand)}}
  .pcard figcaption{{padding:18px}}
  .pcard h3{{color:var(--navy);font-size:1.08rem;margin-bottom:.2em}}
  .pcard .dims{{color:var(--muted);font-size:.9rem;margin-bottom:.7em}}
  .pcard a{{font-weight:700;color:var(--blue);font-size:.9rem}}
  @media(max-width:900px){{.poolgrid{{grid-template-columns:repeat(2,1fr)}}}}
  @media(max-width:560px){{.poolgrid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>

<div class="mocknote">
  DRAFT &mdash; new-pools page rebuilt from your current site, {len(rows)} designs. Photos carry the sizes. For review, {time.strftime('%d %b %Y')}.
</div>

<header>
  <div class="wrap bar">
    <div class="logo">ALL ABOUT <span>POOLS</span></div>
    <nav>
      <ul>
        <li><a href="index.html#services">Services</a></li>
        <li><a href="new-pools.html">New Pools</a></li>
        <li><a href="index.html#beforeafter">Before &amp; After</a></li>
        <li><a href="index.html#process">How It Works</a></li>
        <li><a href="index.html#faq">FAQ</a></li>
        <li><a href="index.html#contact">Contact</a></li>
      </ul>
    </nav>
    <div class="head-cta">
      <a class="phone-link" href="tel:0677327874">067 732 7874</a>
      <a class="btn btn-wa" href="https://wa.me/27677327874">WhatsApp Us</a>
    </div>
  </div>
</header>

<section class="hero" style="min-height:420px">
  <div class="wrap">
    <h1>New Fibreglass Pools</h1>
    <p>Our full range of fibreglass pool shapes, from 2 metre plunge pools to 10 metre lap pools. Supplied and installed by our own team across Cape Town's northern suburbs.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="index.html#contact">Get a Free On-Site Quote</a>
    </div>
  </div>
</section>

<div class="poolnav"><div class="wrap">{''.join(navbits)}</div></div>

<section>
  <div class="wrap">
    {''.join(cards)}
    <p class="center" style="margin-top:20px;color:var(--muted);font-size:.94rem">Don't see the size you need? We can help you choose. <a href="index.html#contact" style="color:var(--blue);font-weight:700">Ask us &rarr;</a></p>
  </div>
</section>

<footer>
  <div class="wrap">
    <p><b style="color:#fff">ALL ABOUT POOLS</b> &nbsp;&middot;&nbsp; Pool renovations, fibreglass linings &amp; installations &nbsp;&middot;&nbsp; Edgemead, Cape Town</p>
    <p style="margin-top:8px">067 732 7874 &nbsp;&middot;&nbsp; info@allaboutpools.co.za</p>
  </div>
</footer>

<div class="mobile-actions">
  <a class="call" href="tel:0677327874">Call Now</a>
  <a class="wa" href="https://wa.me/27677327874">WhatsApp</a>
</div>

</body>
</html>
'''

(ROOT / "new-pools.html").write_text(PAGE, encoding="utf-8")
print("wrote new-pools.html")
