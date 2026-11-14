# -*- coding: utf-8 -*-
"""HOTFOLK® web generator. Spustenie: python3 build.py [výstupný_priečinok] [--preview]
--preview pridá do odkazov index.html (na prezeranie bez servera)."""
import sys, os, re, json, shutil, html as H
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import *

OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
PREVIEW = "--preview" in sys.argv
IMG_DIR = os.path.join(OUT, "assets/img")
SIZES = {f[:-4]: Image.open(os.path.join(IMG_DIR, f)).size for f in os.listdir(IMG_DIR) if f.endswith(".jpg")}

LB = {"sk": ("Zavrieť", "Predchádzajúca", "Ďalšia"), "cz": ("Zavřít", "Předchozí", "Další"),
      "de": ("Schließen", "Vorheriges", "Nächstes"), "en": ("Close", "Previous", "Next")}
NOSCRIPT = {"sk": "Tento web je len pre dospelých (18+). Na zobrazenie obsahu zapnite JavaScript.",
            "cz": "Tento web je jen pro dospělé (18+). Pro zobrazení obsahu zapněte JavaScript.",
            "de": "Diese Website ist nur für Erwachsene (18+). Bitte aktivieren Sie JavaScript, um die Inhalte zu sehen.",
            "en": "This site is for adults only (18+). Please enable JavaScript to view the content."}
NF = {"sk": ("Stránka sa nenašla", "Táto stránka neexistuje alebo sa presunula.", "Späť na úvod"),
      "cz": ("Stránka nenalezena", "Tato stránka neexistuje nebo byla přesunuta.", "Zpět na úvod"),
      "de": ("Seite nicht gefunden", "Diese Seite existiert nicht oder wurde verschoben.", "Zur Startseite"),
      "en": ("Page not found", "This page doesn't exist or has moved.", "Back to home")}

ICON = {
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "pat": '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="15" cy="9.5" r="6"/><rect x="3" y="3.5" width="3.6" height="17"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3c-2.8 0-4.5 1.9-4.5 4.6V11H7v4h2.5v6h4v-6h3l.5-4h-3.5V8.8c0-.5.3-.8.5-.8Z"/></svg>',
}
AR = '<span class="ar">→</span>'
COLORS = ["var(--red)", "var(--green)", "var(--blue)", "var(--orange)"]


def e(s):
    return H.escape(s, quote=True)


def depth(path):
    return path.count("/")


ABS = False


def href(frm, to):
    if ABS:
        return "/" + to
    up = "../" * depth(frm)
    t = to
    if PREVIEW:
        t = t + "index.html"
    return (up + t) or "./"


def asset(frm, p):
    if ABS:
        return "/assets/" + p
    return "../" * depth(frm) + "assets/" + p


def price(v, lang):
    if lang == "en":
        return "€%.2f" % v
    return ("%.2f" % v).replace(".", ",") + " €"


def img(frm, name, alt, cls="", lazy=True, sizes=True):
    w, h = SIZES[name]
    return '<img src="%s" alt="%s" width="%d" height="%d"%s%s>' % (
        asset(frm, "img/%s.jpg" % name), e(alt), w, h, ' loading="lazy" decoding="async"' if lazy else "", (' class="%s"' % cls) if cls else "")


def head(lang, page, path):
    t = T[lang]
    alts = "".join('<link rel="alternate" hreflang="%s" href="%s/%s">' % (HTML_LANG[l], DOMAIN, SLUG[l][page]) for l in LANGS)
    alts += '<link rel="alternate" hreflang="x-default" href="%s/%s">' % (DOMAIN, SLUG["sk"][page])
    ld = ""
    if page == "home":
        ld = '<script type="application/ld+json">%s</script>' % json.dumps({
            "@context": "https://schema.org", "@type": "Organization", "name": "HOTFOLK®",
            "legalName": "HOTFOLK s.r.o.", "url": DOMAIN + "/", "logo": DOMAIN + "/assets/img/logo.png",
            "email": MAIL_INFO, "telephone": PHONE, "sameAs": [IG, FB, ESHOP + "/"],
            "address": {"@type": "PostalAddress", "streetAddress": "Nábrežná 4", "postalCode": "039 01", "addressLocality": "Turčianske Teplice", "addressCountry": "SK"},
        }, ensure_ascii=False)
    detect = ""
    if lang == "sk" and page == "home":
        # prvá návšteva: presmerovanie podľa jazyka prehliadača (len pre ľudí, nie pre roboty)
        detect = """<script>(function(){try{var s=localStorage.getItem('hf_lang');if(s){var u={cz:'%s',de:'%s',en:'%s'}[s];if(u)location.replace(u);return}var l=(navigator.language||'sk').slice(0,2).toLowerCase();var m={cs:'%s',de:'%s'};var t=m[l]||(l!=='sk'&&/^[a-z]{2}$/.test(l)&&!/bot|crawl|spider/i.test(navigator.userAgent)?'%s':null);if(t){localStorage.setItem('hf_lang',l==='cs'?'cz':l==='de'?'de':'en');location.replace(t)}}catch(e){}})();</script>""" % (
            href(path, SLUG["cz"]["home"]), href(path, SLUG["de"]["home"]), href(path, SLUG["en"]["home"]),
            href(path, SLUG["cz"]["home"]), href(path, SLUG["de"]["home"]), href(path, SLUG["en"]["home"]))
    return """<!DOCTYPE html>
<html lang="%(hl)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canon)s">
%(alts)s
<meta name="rating" content="adult">
<meta property="og:type" content="website">
<meta property="og:site_name" content="HOTFOLK®">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canon)s">
<meta property="og:image" content="%(dom)s/assets/img/og.jpg">
<meta property="og:locale" content="%(loc)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF7F0">
<link rel="icon" type="image/png" sizes="32x32" href="%(fav)s">
<link rel="apple-touch-icon" href="%(ati)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="%(css)s">
%(detect)s%(ld)s
</head>
""" % dict(hl=HTML_LANG[lang], title=e(t["title"][page]), desc=e(t["desc"][page]), canon=DOMAIN + "/" + SLUG[lang][page],
           alts=alts, dom=DOMAIN, loc=OG_LOCALE[lang], fav=asset(path, "img/favicon-32.png"), ati=asset(path, "img/apple-touch-icon.png"),
           css=asset(path, "style.css?v=10"), detect=detect, ld=ld)


def langs_html(lang, page, path, cls=""):
    return '<div class="langs %s">%s</div>' % (cls, "".join(
        '<a href="%s" data-lang="%s" hreflang="%s"%s>%s</a>' % (href(path, SLUG[l][page]), l, HTML_LANG[l], ' class="on" aria-current="true"' if l == lang else "", LANG_LABEL[l])
        for l in LANGS))


def header(lang, page, path):
    t = T[lang]
    links = "".join('<a href="%s" class="%s%s"%s>%s</a>' % (href(path, SLUG[lang][p]), "on " if p == page else "", "hotlink" if p == "uncensored" else "", ' aria-current="page"' if p == page else "", t["nav"][p])
                    for p in ["vote", "gallery", "uncensored", "business", "about", "contact"])
    return """<body>
<header class="hdr"><div class="wrap">
<a class="logo" href="%(home)s" aria-label="HOTFOLK®"><img src="%(logo)s" alt="HOTFOLK®" width="900" height="670"></a>
<nav class="nav" id="nav">%(links)s<div class="m-extra">%(mlangs)s<a class="btn red" href="%(eshop)s/">%(es)s %(ar)s</a></div></nav>
%(langs)s
<a class="btn red" href="%(eshop)s/">%(es)s %(ar)s</a>
<button class="burger" aria-label="%(menu)s" aria-controls="nav" aria-expanded="false"><span></span><span></span><span></span></button>
</div></header>
<main>
""" % dict(home=href(path, SLUG[lang]["home"]), logo=asset(path, "img/logo.png"), links=links, langs=langs_html(lang, page, path, "desk"),
           mlangs=langs_html(lang, page, path), eshop=ESHOP, es=t["eshop"], ar=AR, menu=t["menu"])


def footer(lang, page, path):
    t = T[lang]; f = t["footer"]
    nav = "".join('<li><a href="%s">%s</a></li>' % (href(path, SLUG[lang][p]), t["nav"][p]) for p in PAGES)
    shop = "".join('<li><a href="%s%s">%s</a></li>' % (ESHOP, u, n) for n, u in f["shop_links"])
    g = t["gate"]
    return """</main>
<footer class="ftr">
<div class="orn thin"></div>
<div class="top wrap">
<div><a class="logo" href="%(home)s"><img src="%(logo)s" alt="HOTFOLK®" width="900" height="670" loading="lazy"></a><p>%(about)s</p>
<div class="soc"><a href="%(ig)s" target="_blank" rel="noopener" aria-label="Instagram">%(iic)s</a><a href="%(fb)s" target="_blank" rel="noopener" aria-label="Facebook">%(fic)s</a><a href="%(pat)s" target="_blank" rel="noopener" aria-label="Patreon">%(pic)s</a></div></div>
<div><h4>%(navh)s</h4><ul>%(nav)s</ul></div>
<div><h4>%(shoph)s</h4><ul>%(shop)s</ul></div>
<div><h4>%(ch)s</h4><ul><li><a href="mailto:%(mi)s">%(mi)s</a></li><li><a href="mailto:%(mb)s">%(mb)s</a></li><li><a href="tel:%(ph)s">%(pht)s</a></li><li><a href="%(ig)s" target="_blank" rel="noopener">@hotfolk_official</a></li><li><a href="%(pat)s" target="_blank" rel="noopener">patreon.com/hotfolk</a></li></ul></div>
</div>
<div class="bot wrap"><div><a href="%(eshop)s/obchodne-podmienky/">%(terms)s</a><a href="%(eshop)s/podmienky-ochrany-osobnych-udajov/">%(priv)s</a></div><div>© <span class="yr">2026</span> HOTFOLK s.r.o. · %(adult)s</div></div>
</footer>
<div class="lb" role="dialog" aria-modal="true"><button class="x" aria-label="%(lbx)s">×</button><button class="pv" aria-label="%(lbp)s">‹</button><img alt=""><button class="nx" aria-label="%(lbn)s">›</button><div class="cnt"></div></div>
<div class="gate" role="dialog" aria-modal="true" aria-labelledby="gate-h"><div class="box"><img src="%(logo)s" alt="HOTFOLK®"><h2 id="gate-h">%(gh)s</h2><p>%(gp)s</p><div class="ctas"><button class="btn red yes">%(gy)s</button><a class="btn" href="https://www.google.com/">%(gn)s</a></div></div></div>
<noscript><style>main,.ftr,.hdr .nav{display:none!important}</style><div class="gate open" style="display:flex"><div class="box"><img src="%(logo)s" alt="HOTFOLK®"><h2>%(gh)s</h2><p>%(nsp)s</p></div></div></noscript>
<script src="%(js)s" defer></script>
</body>
</html>
""" % dict(home=href(path, SLUG[lang]["home"]), logo=asset(path, "img/logo.png"), about=f["about"], ig=IG, fb=FB, iic=ICON["ig"], fic=ICON["fb"],
           navh=f["nav"], nav=nav, shoph=f["shop"], shop=shop, ch=f["contact"], mi=MAIL_INFO, mb=MAIL_B2B, ph=PHONE_HREF, pht=PHONE,
           pat=PATREON, pic=ICON["pat"], lbx=LB[lang][0], lbp=LB[lang][1], lbn=LB[lang][2], nsp=NOSCRIPT[lang], eshop=ESHOP, terms=f["terms"], priv=f["privacy"], adult=f["adult"], gh=g["h"], gp=g["p"], gy=g["yes"], gn=g["no"], js=asset(path, "app.js?v=4"))


def cal_rows(lang, path, group):
    t = T[lang]["cal"]; out = []
    for p in PRODUCTS[group]:
        name, desc = t["items"][p["id"]]
        tag = ""
        if p["tag"]:
            tag = '<span class="tag%s">%s</span>' % (" hot" if p["tag"] == "18" else (" new" if p["tag"] == "limited" else ""), t["tags"][p["tag"]])
        out.append('<li class="row"><a href="%s%s"><span class="th">%s</span><span><h4>%s %s</h4><p>%s</p></span><span class="pr">%s <i>→</i></span></a></li>' % (
            ESHOP, p["url"], img(path, p["img"], "HOTFOLK " + name + " 2027"), name, tag, desc, price(p["price"], lang)))
    return "".join(out)


def form_html(lang, to, default_topic=0, qty=False):
    f = T[lang]["form"]
    opts = "".join('<option%s>%s</option>' % (" selected" if i == default_topic else "", o) for i, o in enumerate(f["topics"]))
    q = '<div class="fld"><label for="f-qty">%s</label><input id="f-qty" name="%s" type="number" min="1" inputmode="numeric"></div>' % (f["qty"], f["qty"]) if qty else ""
    return """<form class="form rv" data-to="%(to)s" data-subj="%(subj)s" data-key="%(key)s">
<h3>%(h)s</h3><p>%(p)s</p>
<input type="hidden" name="subject" value="%(subj)s"><input type="checkbox" name="botcheck" class="sr" tabindex="-1" autocomplete="off">
<div class="two"><div class="fld"><label for="f-name">%(name)s</label><input id="f-name" name="%(name)s" required autocomplete="name"></div>
<div class="fld"><label for="f-mail">%(email)s</label><input id="f-mail" name="email" type="email" required autocomplete="email"></div></div>
<div class="two"><div class="fld"><label for="f-co">%(company)s</label><input id="f-co" name="%(company)s" autocomplete="organization"></div>
<div class="fld"><label for="f-topic">%(topic)s</label><select id="f-topic" name="%(topic)s">%(opts)s</select></div></div>
%(q)s
<div class="fld"><label for="f-msg">%(msg)s</label><textarea id="f-msg" name="%(msg)s" required></textarea></div>
<button class="btn red" type="submit">%(send)s %(ar)s</button>
<p class="legal">%(legal)s</p>
<div class="ok" role="status">%(ok)s</div>
</form>""" % dict(to=to, subj=e(f["subj"]), key=WEB3FORMS_KEY, h=f["h"], p=f["p"], name=f["name"], email=f["email"], company=f["company"], topic=f["topic"],
                  opts=opts, q=q, msg=f["msg"], send=f["send"], ar=AR, legal=f["legal"], ok=f["ok"])


def sec_head(num, h2, p="", extra=""):
    return '<div class="sec-head"><div class="rv"><span class="num">%s</span><h2>%s</h2></div><div class="rv d1">%s%s</div></div>' % (
        num, h2, ('<p>%s</p>' % p) if p else "", extra)


# ───────── stránky ─────────
def page_home(lang, path):
    t = T[lang]; h = t["hero"]
    meta = "".join('<div><b>%s</b>%s</div>' % m for m in h["meta"])
    tick = "".join("<span>%s</span>" % x for x in t["ticker"]) * 2
    pil = "".join('<div class="pillar rv d%d"><div class="ic" style="background:%s">%d</div><h3>%s</h3><p>%s</p></div>' % (i + 1, COLORS[i], i + 1, a, b) for i, (a, b) in enumerate(t["intro"]["pillars"]))
    c = t["cal"]
    tiles = "".join('<a class="tile rv d%d" href="%s%s">%s<div class="tx"><h3>%s</h3><span>%s →</span></div></a>' % (i % 4, ESHOP, u, img(path, im, n), n, s) for i, (n, s, im, u) in enumerate(t["shop"]["tiles"]))
    g = t["gal"]
    teaser_imgs = ["zeny-09", "zeny-01", "muzi-01", "zeny-02", "plavky-02", "zeny-07", "doplnky-04"]
    cat = lambda n: n.split("-")[0]
    teaser = "".join('<a href="%s" data-lb>%s</a>' % (asset(path, "img/%s.jpg" % n), img(path, n, g["alt"][cat(n)])) for n in teaser_imgs)
    bb = t["b2b_band"]
    s = t["social"]
    return """
<section class="hero"><div class="wrap">
<div>
<span class="eyebrow rv">%(eyebrow)s</span>
<h1 class="rv d1">%(h1)s</h1>
<p class="tagline rv d2">%(tag)s</p>
<p class="lead rv d2">%(lead)s</p>
<div class="ctas rv d3"><a class="btn red" href="#kalendare">%(cta1)s %(ar)s</a><a class="btn" href="%(gal)s">%(cta2)s</a></div>
<div class="hero-meta rv d3">%(meta)s</div>
</div>
<div class="mosaic rv d2">
<figure>%(m1)s</figure><figure>%(m2)s</figure><figure>%(m3)s</figure>
<div class="badge"><b>%(bb)s</b><span>%(bs)s</span></div>
</div>
</div></section>
<div class="ticker" aria-hidden="true"><div class="track">%(tick)s</div></div>

<section class="sec tint"><div class="wrap">
<span class="eyebrow rv">%(inum)s</span>
<p class="lead-l rv d1">%(itext)s</p>
<div class="pillars">%(pil)s</div>
</div></section>

<section class="sec" id="kalendare"><div class="wrap">
%(chead)s
<div class="cal-cols">
<div class="rv"><h3>%(wall)s</h3><ul class="rows">%(wrows)s</ul></div>
<div class="rv d1"><h3>%(desk)s</h3><ul class="rows">%(drows)s</ul>
<p class="note">%(note)s</p>
<a class="btn red" style="margin-top:18px" href="%(eshop)s/kalendare/">%(all)s %(ar)s</a></div>
</div>
</div></section>

<section class="sec tint"><div class="wrap">
%(shead)s
<div class="tiles">%(tiles)s</div>
</div></section>

<section class="sec"><div class="wrap">
%(ghead)s
<div class="teaser rv">%(teaser)s</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<a class="vteaser rv" href="%(vt_link)s">
<div class="vt-ph">%(vt_imgs)s</div>
<div class="vt-tx"><span class="eyebrow">%(vt_eb)s</span><h2>%(vt_h)s</h2><p>%(vt_p)s</p><span class="btn red">%(vt_cta)s %(ar)s</span></div>
</a>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<div class="band rv">
<div><h2>%(bbh)s</h2><p>%(bbp)s</p><a class="btn light" href="%(biz)s">%(bbc)s %(ar)s</a></div>
<ul>%(bbl)s</ul>
</div>
</div></section>

%(casting)s
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="unc-teaser rv">
<div class="ph">%(ut_img)s<span class="stamp">%(ut_st)s</span></div>
<div class="tx"><span class="eyebrow">18+ · Patreon</span><h2>%(ut_h)s</h2><p>%(ut_p)s</p><a class="btn red" href="%(ut_link)s">%(ut_cta)s %(ar)s</a></div>
</div>
</div></section>

<section class="sec cream"><div class="wrap social">
<h2 class="rv">%(sh)s</h2>
<div class="ctas rv d1"><a class="btn" href="%(ig)s" target="_blank" rel="noopener">%(sig)s · @hotfolk_official</a><a class="btn" href="%(fb)s" target="_blank" rel="noopener">%(sfb)s</a></div>
</div></section>
""" % dict(eyebrow=h["eyebrow"], h1=h["h1"], tag=h["tag"], lead=h["lead"], cta1=h["cta1"], cta2=h["cta2"], ar=AR, gal=href(path, SLUG[lang]["gallery"]), meta=meta,
           m1=img(path, "zeny-09", g["alt"]["zeny"], lazy=False), m2=img(path, "zeny-01", g["alt"]["zeny"], lazy=False), m3=img(path, "muzi-03", g["alt"]["muzi"], lazy=False),
           bb=h["badge"][0], bs=h["badge"][1], tick=tick, inum=t["intro"]["num"], itext=t["intro"]["text"], pil=pil,
           chead=sec_head(c["num"], c["h2"], c["p"]), wall=c["wall"], desk=c["desk"], wrows=cal_rows(lang, path, "wall"), drows=cal_rows(lang, path, "desk"),
           note=c["note"], eshop=ESHOP, all=c["all"],
           shead=sec_head(t["shop"]["num"], t["shop"]["h2"], t["shop"]["p"]), tiles=tiles,
           ghead=sec_head(g["num"], g["h2"], g["p"], '<p style="margin-top:18px"><a class="link" href="%s">%s →</a></p>' % (href(path, SLUG[lang]["gallery"]), g["more"])),
           teaser=teaser, bbh=bb["h2"], bbp=bb["p"], bbc=bb["cta"], biz=href(path, SLUG[lang]["business"]), bbl="".join("<li>%s</li>" % x for x in bb["list"]),
           sh=s["h2"], ig=IG, fb=FB, sig=s["ig"], sfb=s["fb"],
           ut_img=img(path, "zeny-11", g["alt"]["zeny"]), ut_st=t["unc"]["sticker"], ut_h=t["unc"]["home_h"], ut_p=t["unc"]["home_p"],
           ut_cta=t["unc"]["home_cta"], ut_link=href(path, SLUG[lang]["uncensored"]),
           casting=casting(lang, path), vt_link=href(path, SLUG[lang]["vote"]), vt_imgs="".join(img(path, m["img"], m["name"]) for m in VOTE["models"]),
           vt_eb=t["vote"]["eyebrow"], vt_h=t["vote"]["home_h"], vt_p=t["vote"]["home_p"], vt_cta=t["vote"]["home_cta"])


def page_gallery(lang, path):
    g = T[lang]["gal"]
    fl = "".join('<button data-f="%s"%s>%s</button>' % (k, ' class="on"' if k == "all" else "", v) for k, v in g["filters"].items())
    cnt = {}
    def alt(c):
        cnt[c] = cnt.get(c, 0) + 1
        return "%s – %d" % (g["alt"][c], cnt[c])
    items = "".join('<a href="%s" data-lb data-c="%s">%s</a>' % (asset(path, "img/%s.jpg" % n), c, img(path, n, alt(c))) for n, c in GALLERY_MIXED)
    return """
<section class="phero"><div class="wrap"><span class="eyebrow rv">HOTFOLK® 2027</span><h1 class="rv d1">%s</h1><p class="lead rv d2">%s</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="filters rv" role="group">%s</div>
<div class="masonry">%s</div>
</div></section>
""" % (g["h1"], g["lead"], fl, items)


def page_business(lang, path):
    b = T[lang]["biz"]
    def checks(l): return '<ul class="checks">%s</ul>' % "".join("<li>%s</li>" % x for x in l)
    steps = "".join('<div class="step rv d%d"><h3>%s</h3><p>%s</p></div>' % (i, a, c) for i, (a, c) in enumerate(b["steps"]))
    return """
<section class="phero"><div class="wrap"><span class="eyebrow rv">%(eb)s</span><h1 class="rv d1">%(h1)s</h1><p class="lead rv d2">%(lead)s</p>
<div class="ctas rv d3" style="margin-top:32px"><a class="btn red" href="#formular">%(c1)s %(ar)s</a><a class="btn" href="mailto:%(mb)s">%(mb)s</a></div></div></section>
<section class="sec tint"><div class="wrap split">
<div class="media rv">%(i1)s</div>
<div class="rv d1"><span class="eyebrow">01</span><h2>%(s1h)s</h2><p>%(s1p)s</p>%(s1l)s<a class="btn red" href="#formular">%(c1)s %(ar)s</a></div>
</div></section>
<section class="sec"><div class="wrap split rev">
<div class="media rv">%(i2)s</div>
<div class="rv d1"><span class="eyebrow">02</span><h2>%(s2h)s</h2><p>%(s2p)s</p>%(s2l)s<a class="btn red" href="#formular">%(c2)s %(ar)s</a></div>
</div></section>
<section class="sec tint"><div class="wrap split">
<div class="media rv">%(i3)s</div>
<div class="rv d1"><span class="eyebrow">03</span><h2>%(s3h)s</h2><p>%(s3p)s</p><a class="btn" style="margin-top:12px" href="mailto:%(mb)s">%(c3)s %(ar)s</a></div>
</div></section>
<section class="sec cream"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(sth)s</h2></div></div>
<div class="steps">%(steps)s</div>
</div></section>
<section class="sec" id="formular"><div class="wrap cgrid">
<div>%(cards)s</div>
%(form)s
</div></section>
""" % dict(eb=b["eyebrow"], h1=b["h1"], lead=b["lead"], c1=b["s1"]["cta"], c2=b["s2"]["cta"], c3=b["s3"]["cta"], ar=AR, mb=MAIL_B2B,
           i1=img(path, "zeny-03", b["s1"]["h2"]), i2=img(path, "muzi-03", b["s2"]["h2"]), i3=img(path, "doplnky-03", b["s3"]["h2"]),
           s1h=b["s1"]["h2"], s1p=b["s1"]["p"], s1l=checks(b["s1"]["list"]), s2h=b["s2"]["h2"], s2p=b["s2"]["p"], s2l=checks(b["s2"]["list"]),
           s3h=b["s3"]["h2"], s3p=b["s3"]["p"], sth=b["steps_h"], steps=steps, cards=contact_cards(lang, b2b_first=True),
           form=form_html(lang, MAIL_B2B, default_topic=1, qty=True))


def contact_cards(lang, b2b_first=False):
    c = T[lang]["contact"]
    info = '<a class="ccard" href="mailto:%s"><span class="ci">%s</span><span><small>%s</small><b>%s</b></span></a>' % (MAIL_INFO, ICON["mail"], c["c_info"], MAIL_INFO)
    b2b = '<a class="ccard" href="mailto:%s"><span class="ci">%s</span><span><small>%s</small><b>%s</b></span></a>' % (MAIL_B2B, ICON["mail"], c["c_b2b"], MAIL_B2B)
    ph = '<a class="ccard" href="tel:%s"><span class="ci">%s</span><span><small>%s</small><b>%s</b></span></a>' % (PHONE_HREF, ICON["phone"], c["c_phone"], PHONE)
    ig = '<a class="ccard" href="%s" target="_blank" rel="noopener"><span class="ci">%s</span><span><small>Instagram</small><b>@hotfolk_official</b></span></a>' % (IG, ICON["ig"])
    fb = '<a class="ccard" href="%s" target="_blank" rel="noopener"><span class="ci">%s</span><span><small>Facebook</small><b>Hotfolkofficial</b></span></a>' % (FB, ICON["fb"])
    order = [b2b, info, ph, ig, fb] if b2b_first else [info, b2b, ph, ig, fb]
    return '<div class="cards rv">%s</div><div class="firm rv"><b>%s</b><br>%s</div>' % ("".join(order), c["firm_h"], c["firm"])


def page_about(lang, path):
    a = T[lang]["about"]
    story = "".join("<p>%s</p>" % p for p in a["story"])
    vals = "".join('<div class="value rv d%d"><h3>%s</h3><p>%s</p></div>' % (i, x, y) for i, (x, y) in enumerate(a["values"]))
    team = "".join('<div class="member rv d%d"><div class="av" style="background:%s">%s</div><h3>%s</h3><p>%s</p></div>' % (
        i, COLORS[i], "".join(w[0] for w in n.split()[:2]), n, r) for i, (n, r) in enumerate(a["team"]))
    return """
<section class="phero"><div class="wrap"><span class="eyebrow rv">%(eb)s</span><h1 class="rv d1">%(h1)s</h1><p class="lead rv d2">%(lead)s</p></div></section>
<section class="sec tint"><div class="wrap split">
<div class="media rv">%(im)s</div>
<div class="rv d1"><h2>%(sh)s</h2>%(story)s</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(vh)s</h2></div></div>
<div class="values">%(vals)s</div>
</div></section>
<section class="sec cream"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(th)s</h2></div></div>
<div class="team">%(team)s</div>
</div></section>
%(casting)s""" % dict(casting=casting(lang, path), eb=a["eyebrow"], h1=a["h1"], lead=a["lead"], im=img(path, "zeny-02", a["story_h"]), sh=a["story_h"], story=story,
           vh=a["values_h"], vals=vals, th=a["team_h"], team=team)


def page_contact(lang, path):
    c = T[lang]["contact"]
    return """
<section class="phero"><div class="wrap"><span class="eyebrow rv">%s</span><h1 class="rv d1">%s</h1><p class="lead rv d2">%s</p></div></section>
<section class="sec" style="padding-top:10px"><div class="wrap cgrid">
<div>%s</div>
%s
</div></section>
""" % (c["eyebrow"], c["h1"], c["lead"], contact_cards(lang), form_html(lang, MAIL_INFO))


def page_uncensored(lang, path):
    u = T[lang]["unc"]
    why = "".join('<div class="pillar rv d%d"><div class="ic" style="background:%s">%d</div><h3>%s</h3><p>%s</p></div>' % (i + 1, COLORS[i], i + 1, a, b) for i, (a, b) in enumerate(u["why"]))
    how = "".join('<div class="step rv d%d"><h3>%s</h3><p>%s</p></div>' % (i, a, b) for i, (a, b) in enumerate(u["how"]))
    alt = T[lang]["gal"]["alt"]["zeny"]
    st = '<span class="stamp">%s</span>' % u["sticker"]
    return """
<section class="phero unc"><div class="wrap unc-grid">
<div>
<span class="eyebrow rv">%(eb)s</span>
<h1 class="rv d1">%(h1)s</h1>
<p class="lead rv d2">%(lead)s</p>
<div class="ctas rv d3" style="margin-top:32px"><a class="btn red" href="%(pat)s" target="_blank" rel="noopener">%(cta)s %(ar)s</a><a class="btn" href="%(es)s/nastenny-kalendar-topless/">%(cta2)s</a></div>
</div>
<div class="unc-mosaic rv d2">
<figure class="big">%(i1)s%(st)s</figure>
<figure>%(i2)s</figure><figure>%(i3)s</figure>
</div>
</div></section>
<section class="sec tint"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(whyh)s</h2></div></div>
<div class="pillars" style="margin-top:0">%(why)s</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(th)s</h2></div><div class="rv d1"><p>%(tp)s</p></div></div>
<div class="tiers rv">%(tiers)s</div>
</div></section>
<section class="sec cream"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(howh)s</h2></div></div>
<div class="steps steps3">%(how)s</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="band band2 rv">
<div><h2>%(bh)s</h2><p style="margin:0">%(bp)s</p></div>
<div><a class="btn light" href="%(pat)s" target="_blank" rel="noopener">patreon.com/hotfolk %(ar)s</a></div>
</div>
<p class="note" style="margin-top:22px">%(note)s</p>
</div></section>
""" % dict(eb=u["eyebrow"], h1=u["h1"], lead=u["lead"], pat=PATREON, cta=u["cta"], cta2=u["cta2"], ar=AR, es=ESHOP,
           i1=img(path, "zeny-11", alt, lazy=False), i2=img(path, "zeny-10", alt, lazy=False), i3=img(path, "zeny-12", alt, lazy=False), st=st,
           whyh=u["why_h"], why=why, th=u["tiers_h"], tp=u["tiers_p"],
           tiers="".join('<a class="tier" href="%s" target="_blank" rel="noopener"><b>%s</b><span>%s</span></a>' % (PATREON, ("$%d" % v) if lang == "en" else ("%d $" % v), u["per"]) for v in PATREON_TIERS), howh=u["how_h"], how=how, bh=u["band_h"], bp=u["band_p"], note=u["note"])


def page_vote(lang, path):
    v = T[lang]["vote"]
    rules = href(path, SLUG[lang]["rules"])
    cfg = {"api": VOTE_API, "round": VOTE["round"], "end": VOTE["end"], "lang": lang, "models": [m["id"] for m in VOTE["models"]],
           "t": {"votes": v["votes"], "left": v["left"], "closed": v["closed"], "sending": v["sending"],
                 "ok": v["ok"] % {"draw": VOTE["draw_by"][lang]}, "dup": v["dup"], "err": v["err"]}}
    cards = "".join("""<article class="vcard rv d%(i)d" data-id="%(id)s">
<div class="vph">%(img)s<span class="vmine">✓ %(mine)s</span></div>
<div class="vbody"><h3>%(name)s</h3>
<div class="vres"><div class="vbar"><i></i></div><div class="vnums"><span class="vpct">0 %%</span><span class="vn"></span></div></div>
<button class="btn red vbtn" type="button">%(vote)s %(ar)s</button></div>
</article>""" % dict(i=i, id=m["id"], img=img(path, m["img"], m["name"], lazy=False), name=m["name"], vote=v["vote"], ar=AR, mine=v["chosen"])
        for i, m in enumerate(VOTE["models"]))
    how = "".join('<div class="step rv d%d"><h3>%s</h3><p>%s</p></div>' % (i, a, b) for i, (a, b) in enumerate(v["how"]))
    return """
<section class="phero"><div class="wrap">
<span class="eyebrow rv">%(eb)s</span><h1 class="rv d1">%(h1)s</h1><p class="lead rv d2">%(lead)s</p>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<div id="vote" data-cfg='%(cfg)s'>
<div class="vtop rv"><div><small>%(ends)s</small><b class="vcd">%(endtxt)s</b></div><div class="vtotal"><small>%(total)s</small><b>–</b></div></div>
<p class="vsoon rv">%(soon)s</p>
<div class="vgrid">%(cards)s</div>
<form class="form vform" hidden novalidate>
<h3>%(fh)s</h3><p>%(fp)s</p>
<p class="vpick">%(chosen)s: <b class="vchosen"></b></p>
<input type="text" name="website" class="sr" tabindex="-1" autocomplete="off">
<div class="two"><div class="fld"><label for="v-name">%(name)s</label><input id="v-name" name="name" required autocomplete="given-name"></div>
<div class="fld"><label for="v-mail">%(email)s</label><input id="v-mail" name="email" type="email" required autocomplete="email"></div></div>
<label class="vcons"><input type="checkbox" name="consent" required> <span>%(consent)s</span></label>
<button class="btn red" type="submit">%(send)s</button>
</form>
<div class="vmsg" role="status" hidden></div>
</div>
</div></section>
<section class="sec cream"><div class="wrap">
<div class="sec-head"><div class="rv"><h2>%(ph)s</h2></div><div class="rv d1"><p>%(prize)s</p><p style="margin-top:14px"><a class="link" href="%(rules)s">%(rl)s →</a></p></div></div>
<div class="steps steps3">%(how)s</div>
</div></section>
<script src="%(js)s" defer></script>
""" % dict(eb=v["eyebrow"], h1=v["h1"], lead=v["lead"] % {"month": VOTE["month"][lang]}, cfg=e(json.dumps(cfg, ensure_ascii=False)),
           ends=v["ends"], endtxt=VOTE["end_txt"][lang], total=v["total"], soon=v["soon"], cards=cards, fh=v["form_h"], fp=v["form_p"],
           chosen=v["chosen"], name=v["name"], email=v["email"], consent=v["consent"] % {"rules": rules}, send=v["send"],
           ph=v["prize_h"], prize=v["prize"], rules=rules, rl=v["rules_link"], how=how, js=asset(path, "vote.js?v=1"))


def page_rules(lang, path):
    r = T[lang]["rules"]
    secs = "".join('<section class="rsec"><h2>%s</h2>%s</section>' % (h, "".join("<p>%s</p>" % x for x in ps)) for h, ps in r["sec"])
    return """
<section class="phero"><div class="wrap"><h1 class="rv">%s</h1><p class="lead rv d1">%s</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap rules">%s</div></section>
""" % (r["h1"], r["lead"], secs)


def casting(lang, path, tint=""):
    c = T[lang]["cast"]
    stats = "".join('<div><b>%s</b><span>%s</span></div>' % x for x in c["stats"])
    return """<section class="sec %(tint)s"><div class="wrap cast">
<div class="cast-ph rv"><img class="sticker" src="%(stk)s" alt="%(eb)s" width="1100" height="1650" loading="lazy" decoding="async"></div>
<div class="rv d1"><span class="eyebrow">%(eb)s</span><h2>%(h2)s</h2><p>%(p)s</p>
<div class="cast-stats">%(stats)s</div>
<a class="btn red" href="%(link)s#casting">%(cta)s %(ar)s</a><p class="note">%(note)s</p></div>
</div></section>
""" % dict(tint=tint, stk=asset(path, "img/casting.webp"), eb=c["eyebrow"], h2=c["h2"], p=c["p"],
           stats=stats, link=href(path, SLUG[lang]["contact"]), cta=c["cta"], ar=AR, note=c["note"])


RENDER = {"vote": page_vote, "rules": page_rules, "uncensored": page_uncensored, "home": page_home, "gallery": page_gallery, "business": page_business, "about": page_about, "contact": page_contact}


def build():
    files = []
    for lang in LANGS:
        for page in PAGES:
            path = SLUG[lang][page]
            body = head(lang, page, path) + header(lang, page, path) + RENDER[page](lang, path) + footer(lang, page, path)
            fp = os.path.join(OUT, path, "index.html")
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "w", encoding="utf-8").write(body)
            files.append(path)
    # 404 – absolútne cesty, bez presmerovania jazyka
    global ABS
    ABS = True
    for lang in LANGS:
        pre = "" if lang == "sk" else lang + "/"
        t = NF[lang]
        hd = head(lang, "home", "")
        hd = re.sub(r'<link rel="(canonical|alternate)"[^>]*>', "", hd)
        hd = re.sub(r"<script>\(function\(\)\{try\{var s=localStorage.*?</script>", "", hd, flags=re.S)
        hd = re.sub(r"<title>.*?</title>", "<title>%s | HOTFOLK®</title>" % t[0], hd).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">')
        hd = re.sub(r'<script type="application/ld\+json">.*?</script>', "", hd, flags=re.S)
        body = hd + header(lang, "home", "") + """
<section class="phero"><div class="wrap"><span class="eyebrow">404</span><h1>%s</h1><p class="lead">%s</p>
<div class="ctas" style="margin-top:30px"><a class="btn red" href="/%s">%s %s</a><a class="btn" href="%s/">E-shop</a></div></div></section>
""" % (t[0], t[1], pre, t[2], AR, ESHOP) + footer(lang, "home", "")
        open(os.path.join(OUT, pre, "404.html"), "w", encoding="utf-8").write(body)
    ABS = False
    # sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for lang in LANGS:
        for page in PAGES:
            sm.append("<url><loc>%s/%s</loc>%s<changefreq>monthly</changefreq><priority>%s</priority></url>" % (
                DOMAIN, SLUG[lang][page], "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>' % (HTML_LANG[l], DOMAIN, SLUG[l][page]) for l in LANGS),
                "1.0" if page == "home" else "0.7"))
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % DOMAIN)
    # presmerovania zo starého WordPressu
    redir = [("/fotogaleria/", "/galeria/"), ("/historia/", "/o-nas/"), ("/blog/", "/"),
             ("/viktoriabiele/", ESHOP + "/plavky-hotfolk/"), ("/bielebrazilkysriasenimivanka/", ESHOP + "/plavky-hotfolk/"),
             ("/eliskacierne/", ESHOP + "/plavky-hotfolk/"), ("/plavky-hotfolk/", ESHOP + "/plavky-hotfolk/"),
             ("/nastenny-kalendar-zadeckovy/", ESHOP + "/nastenny-kalendar-zadeckovy/"), ("/stolovy-kalendar-pre-panov/", ESHOP + "/stolovy-kalendar-pre-panov/"),
             ("/eshop/", ESHOP + "/"), ("/patreon/", PATREON)]
    ht = ["# HOTFOLK® – WebSupport (Apache)", "Options -Indexes", "DirectoryIndex index.html", "ErrorDocument 404 /404.html",
          '<If "%{REQUEST_URI} =~ m#^/cz/#">', "ErrorDocument 404 /cz/404.html", "</If>",
          '<If "%{REQUEST_URI} =~ m#^/de/#">', "ErrorDocument 404 /de/404.html", "</If>",
          '<If "%{REQUEST_URI} =~ m#^/en/#">', "ErrorDocument 404 /en/404.html", "</If>", "",
          "<IfModule mod_headers.c>",
          'Header always set Strict-Transport-Security "max-age=31536000"',
          'Header always set X-Frame-Options "SAMEORIGIN"',
          'Header always set X-Content-Type-Options "nosniff"',
          'Header always set Referrer-Policy "strict-origin-when-cross-origin"',
          '<FilesMatch "\\.(jpe?g|png|webp|ico)$">', 'Header set Cache-Control "public, max-age=31536000"', "</FilesMatch>",
          '<FilesMatch "\\.(css|js)$">', 'Header set Cache-Control "public, max-age=2592000"', "</FilesMatch>",
          '<FilesMatch "\\.html$">', 'Header set Cache-Control "no-cache"', "</FilesMatch>",
          "</IfModule>", "",
          "RewriteEngine On", "# www + https", "RewriteCond %{HTTPS} off [OR]", "RewriteCond %{HTTP_HOST} !^www\\. [NC]",
          "RewriteCond %{HTTP_HOST} ^(?:www\\.)?(.+)$ [NC]", "RewriteRule ^ https://www.%1%{REQUEST_URI} [L,R=301]", "",
          "# staré adresy z WordPressu", "RewriteRule ^wp-(admin|login\\.php) / [L,R=301]",
          "# /index.html → /",
          "RewriteCond %{THE_REQUEST} \\s/(.*/)?index\\.html[\\s?]",
          "RewriteRule ^(.*/)?index\\.html$ /$1 [R=301,L]"]
    for a, b in redir:
        ht.append("Redirect 301 %s %s" % (a, b if b.startswith("http") else DOMAIN + b))
    ht += ["", "<IfModule mod_expires.c>", "ExpiresActive On", 'ExpiresByType image/jpeg "access plus 1 year"', 'ExpiresByType image/png "access plus 1 year"',
           'ExpiresByType text/css "access plus 1 month"', 'ExpiresByType application/javascript "access plus 1 month"', "</IfModule>",
           "<IfModule mod_deflate.c>", "AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml", "</IfModule>"]
    open(os.path.join(OUT, ".htaccess"), "w").write("\n".join(ht) + "\n")
    open(os.path.join(OUT, "_redirects"), "w").write("\n".join("%s %s 301" % (a, b) for a, b in redir) + "\n")
    print("OK", len(files), "stránok", "(preview)" if PREVIEW else "")


if __name__ == "__main__":
    build()
