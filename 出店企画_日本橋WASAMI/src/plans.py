"""平面計画図（A3横・SVG）を生成する"""
import math, pickle, sys, os
import base64
from geometry import FLOORS, AREA, SCAN_1F, area, treat_count

PAGE_W, PAGE_H = 420, 297
FONT = "'IPAGothic','IPAPGothic',sans-serif"

C = dict(wall="#2b2522", shell="#8c8580", tint="#f6f1e8", treat="#efe4d2", mri="#e3e8ec",
         service="#ecebe8", core="#f1f1f1", corridor="#fbefe3", accent="#9a7b55", text="#2b2522",
         sub="#7a726b", wood="#c7a57c", red="#b5523b", blue="#2d5c8a")


class SVG:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def line(self, x1, y1, x2, y2, st="#000", w=0.2, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{st}" stroke-width="{w}"{d} {extra}/>')

    def rect(self, x, y, w, h, fill="none", st="none", sw=0.2, extra=""):
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{st}" stroke-width="{sw}" {extra}/>')

    def text(self, x, y, s, size=2.6, fill=C["text"], anchor="middle", weight="normal", extra=""):
        lines = str(s).split("\n")
        y0 = y - (len(lines) - 1) * size * 0.6
        for i, ln in enumerate(lines):
            self.add(f'<text x="{x:.2f}" y="{y0 + i*size*1.2:.2f}" font-size="{size}" fill="{fill}" '
                     f'text-anchor="{anchor}" font-weight="{weight}" font-family="{FONT}" {extra}>{ln}</text>')

    def path(self, d, fill="none", st="#000", sw=0.2, extra=""):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{st}" stroke-width="{sw}" {extra}/>')

    def circle(self, x, y, r, fill="none", st="#000", sw=0.2):
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')

    def svg(self, w=PAGE_W, h=PAGE_H):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">'
                '<defs><pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="1.6" stroke="#d9a77a" stroke-width="0.35"/></pattern>'
                '<pattern id="hatchg" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="1.2" stroke="#9c9c9c" stroke-width="0.25"/></pattern>'
                '<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>'
                f'<rect width="{w}" height="{h}" fill="white"/>' + "\n".join(self.o) + "</svg>")


def title_block(g, title, scale, sheet, note_lines=()):
    g.rect(8, 8, PAGE_W - 16, PAGE_H - 16, st="#333", sw=0.35)
    y = PAGE_H - 30
    g.rect(PAGE_W - 128, y, 120, 22, fill="white", st="#333", sw=0.3)
    g.line(PAGE_W - 128, y + 8, PAGE_W - 8, y + 8, st="#333", w=0.2)
    g.line(PAGE_W - 48, y + 8, PAGE_W - 48, y + 22, st="#333", w=0.2)
    g.text(PAGE_W - 124, y + 5.4, "fukka 日本橋院（仮称） 出店計画 ／ 日本橋WASAMIビル", 2.6, anchor="start", weight="bold")
    g.text(PAGE_W - 124, y + 13.5, title, 3.0, anchor="start", weight="bold")
    g.text(PAGE_W - 124, y + 19.3, "基本計画（出店企画書添付資料）　2026.10", 2.2, anchor="start", fill=C["sub"])
    g.text(PAGE_W - 28, y + 13.5, f"S={scale}", 2.8, weight="bold")
    g.text(PAGE_W - 28, y + 19.3, f"No.{sheet}　A3", 2.2, fill=C["sub"])
    yy = PAGE_H - 30
    for i, ln in enumerate(note_lines):
        g.text(14, yy + i * 3.4, ln, 2.15, anchor="start", fill=C["sub"])


def north_marker(g, x, y):
    """方位：真北は未確認のため、図の向き（通り）のみを示す"""
    g.rect(x - 16, y - 6, 32, 15, fill="white", st="#999", sw=0.2)
    g.text(x, y - 1.6, "図の向き", 2.0, weight="bold")
    g.text(x, y + 2.0, "左：正面道路（Y1側）", 1.7, fill=C["sub"])
    g.text(x, y + 5.0, "上：X1通り側　※真北は要確認", 1.7, fill=C["sub"])


def draw_floor(f, ox, oy, s, scan=None):
    """ox,oy = 図面上の貸室原点(x=0,y=0)位置[mm-paper]、s = 縮尺(paper/real)"""
    g = SVG()
    P = lambda x, y: (ox + x * s, oy - y * s)
    W, D = f["W"], f["D"]

    # --- 1F: 募集図面（貸主提供）を下図に
    if scan is not None:
        path, cx0, cy0, iw, ih = scan
        k = 1000 / SCAN_1F["px_per_m"] * s          # px → paper
        x0 = ox + (cx0 - SCAN_1F["px0"]) * k
        y0 = oy - (SCAN_1F["py0"] - cy0) * k
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        g.add(f'<image x="{x0:.2f}" y="{y0:.2f}" width="{iw*k:.2f}" height="{ih*k:.2f}" opacity="0.55" '
              f'href="data:image/png;base64,{b64}"/>')

    # --- 貸室床（切欠きを除く）
    nt = f.get("notch")
    pts = [(0, 0), (W, 0), (W, nt[1]), (nt[0], nt[1]), (nt[0], D), (0, D)] if nt else [(0, 0), (W, 0), (W, D), (0, D)]
    g.add('<polygon points="' + " ".join("%.2f,%.2f" % P(*q) for q in pts) + f'" fill="{C["tint"]}" opacity="0.92"/>')

    # --- コア（上階）
    for r in f.get("core", []):
        x, y = P(r["x0"], r["y1"])
        tc_ = r["kind"] == "tcore"
        g.rect(x, y, (r["x1"] - r["x0"]) * s, (r["y1"] - r["y0"]) * s, fill=C["tint"] if tc_ else C["core"], st=C["shell"], sw=0.3)
        cxp, cyp = P((r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2)
        g.text(cxp, cyp + 0.8, r["name"], 2.0, fill=C["text"] if tc_ else C["sub"], weight="bold" if tc_ else "normal")
    if f.get("core"):
        g.text(ox + (W / 2) * s, oy + 4800 * s + 4.5,
               "※コアは募集図面（4・5階）をもとに作図。実寸はビル側図面にて要確認", 2.0, fill=C["sub"])
        e0, e1, _ = f["evh"]
        p1, p2 = P(e0, 0), P(e1, 0)
        g.line(*p1, *p2, st=C["red"], w=0.35, dash="1,0.6")
        g.text((p1[0] + p2[0]) / 2, p1[1] + 3.0, "防火扉（随時閉鎖・既設）", 1.7, fill=C["red"])

    # --- 部屋（塗り）
    for r in f["rooms"]:
        fill = dict(treat=C["treat"], mri=C["mri"], service=C["service"], corridor="url(#hatch)", hall="#f3ebdd",
                    room="#f8f4ee", existing="#eeeeee").get(r["kind"])
        if fill:
            x, y = P(r["x0"], r["y1"])
            g.rect(x, y, (r["x1"] - r["x0"]) * s, (r["y1"] - r["y0"]) * s, fill=fill)

    # --- 外壁（上階：模式表現）
    if scan is None:
        t = 250 * s
        x, y = P(0, D)
        g.path(f"M{x - t},{oy} L{x - t},{y - t} L{x + W*s + t},{y - t} L{x + W*s + t},{oy}",
               st=C["shell"], sw=t * 1.0, fill="none", extra='stroke-linejoin="miter"')
        g.line(x, oy, x + W * s, oy, st=C["shell"], w=0.7)
        # 窓
        for o in f.get("openings", []):
            if o["side"] == "W":
                a, b = P(0, o["a"])[1], P(0, o["b"])[1]
                g.line(x - t * 1.0, a, x - t * 1.0, b, st="white", w=t * 0.8)
                g.line(x - t * 0.75, a, x - t * 0.75, b, st="#6d8fa8", w=0.15)
                g.line(x - t * 0.25, a, x - t * 0.25, b, st="#6d8fa8", w=0.15)
            if o["side"] == "N":
                a, b = P(o["a"], 0)[0], P(o["b"], 0)[0]
                g.line(a, y - t, b, y - t, st="white", w=t * 0.8)
                g.line(a, y - t * 0.75, b, y - t * 0.75, st="#6d8fa8", w=0.15)
                g.line(a, y - t * 0.25, b, y - t * 0.25, st="#6d8fa8", w=0.15)
        for cxm, cym in f["columns"]:
            px, py = P(cxm, cym)
            g.rect(px - 400 * s, py - 250 * s, 800 * s, 650 * s, fill=C["shell"])
    else:
        for cxm, cym in f["columns"]:
            px, py = P(cxm, cym)
            g.rect(px - 400 * s, py - 50 * s, 800 * s, 400 * s, fill="#cfc9c3", st=C["shell"], sw=0.15)

    # --- 家具
    furniture(g, f, P, s)

    # --- 間仕切壁
    wt = max(0.6, 100 * s)
    for r in f["rooms"]:
        if r["kind"] in ("open", "existing", "hall"):
            continue
        x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
        edges = dict(S=((x0, y0), (x1, y0)), N=((x0, y1), (x1, y1)), W=((x0, y0), (x0, y1)), E=((x1, y0), (x1, y1)))
        if r["kind"] == "corridor":
            # 避難経路：北側・西側のみ間仕切
            edges = {k: v for k, v in edges.items() if k in ("N",)}
            if f["floor"] != "1F":
                edges["W"] = ((x0, y0), (x0, y1)); edges["E"] = ((x1, y0), (x1, y1))
        for k, ((a, b), (c, d)) in edges.items():
            if k in r.get("nowall", []):
                continue
            # 外壁・コア境界上の辺は描かない（既設）
            if k == "S" and y0 <= 0 and f["floor"] != "1F":
                continue
            if f["floor"] == "1F" and ((k == "S" and y0 <= 0) or (k == "N" and y1 >= f["D"]) or (k == "E" and x1 >= f["W"]) or (k == "W" and x0 <= 0)):
                if r["kind"] != "mri":
                    continue
            if f["floor"] != "1F" and ((k == "N" and y1 >= f["D"]) or (k == "W" and x0 <= 0) or (k == "E" and x1 >= f["W"])):
                continue
            p1, p2 = P(a, b), P(c, d)
            col = C["blue"] if r["kind"] == "mri" else C["wall"]
            g.line(*p1, *p2, st=col, w=wt * (1.6 if r["kind"] == "mri" else 1), extra='stroke-linecap="square"')

    # --- 建具
    for r in f["rooms"]:
        for dd in r["doors"]:
            door(g, r, dd, P, s, wt)
        for w in r.get("windows", []):   # 観察窓
            xx = r["x1"] if w["side"] == "E" else r["x0"]
            p1, p2 = P(xx, w["a"]), P(xx, w["b"])
            g.line(*p1, *p2, st="white", w=wt * 1.7)
            for o in (-0.35, 0.35):
                g.line(p1[0] + o, p1[1], p2[0] + o, p2[1], st=C["blue"], w=0.2)
            g.text(p1[0] - 1.2, (p1[1] + p2[1]) / 2, "観察窓", 1.5, fill=C["blue"], anchor="end")
    # --- 上階：階段附室・トイレへの扉（廊下に面する）
    if f.get("stair_door"):
        for (a, b), lab in ((f["stair_door"], "特別避難階段へ"), (f["toilet_door"], "共用トイレへ")):
            p1, p2 = P(a, 0), P(b, 0)
            g.line(*p1, *p2, st="white", w=wt * 1.6)
            g.path(f"M{p1[0]},{p1[1]} L{p1[0]},{p1[1] + (b-a)*s} A{(b-a)*s},{(b-a)*s} 0 0 0 {p2[0]},{p2[1]}", st=C["wall"], sw=0.18)
            g.text((p1[0] + p2[0]) / 2, p1[1] + (b - a) * s + 3.0, lab, 1.7, fill=C["accent"], weight="bold")
    for (px_, py_) in f.get("plants", []):
        a, b = P(px_, py_); g.circle(a, b, 280 * s, fill="#cfdcc4", st="#8aa07a", sw=0.15)

    # --- エントランス
    for e in f.get("entrances", []):
        if e["side"] == "EVH":
            ax, ay = P(e["at"], -3600)
            bx, by = P(e["at"], 1300)
            g.line(ax, ay, bx, by, st=C["red"], w=0.45, extra='marker-end="url(#arr)"')
            g.text(ax + 1.5, ay + 3, "患者動線（EVより）", 2.1, fill=C["red"], weight="bold", anchor="start")
        elif e["side"] == "CORE":
            a, b = e["at"] - e["w"] / 2, e["at"] + e["w"] / 2
            p1, p2 = P(a, 1400), P(b, 1400)
            g.line(*p1, *p2, st="white", w=wt * 1.6)
            g.line(p1[0], p1[1] - 0.3, (p1[0] + p2[0]) / 2, p1[1] - 0.3, st="#6d8fa8", w=0.35)
            g.line((p1[0] + p2[0]) / 2, p1[1] + 0.3, p2[0], p2[1] + 0.3, st="#6d8fa8", w=0.35)
            g.text((p1[0] + p2[0]) / 2, p1[1] - 1.6, e["note"], 1.9, fill=C["blue"])
            ax, ay = P(e["at"], -3600)
            bx, by = P(e["at"], 2000)
            g.line(ax, ay, bx, by, st=C["red"], w=0.45, extra='marker-end="url(#arr)"')
            g.text(ax + 1.5, ay + 3, "患者動線（EVより）", 2.1, fill=C["red"], weight="bold", anchor="start")
        elif e["side"] == "S":
            a, b = e["at"] - e["w"] / 2, e["at"] + e["w"] / 2
            ax, ay = P(e["at"], -1500)
            bx, by = P(e["at"], 900)
            g.line(ax, ay, bx, by, st=C["sub"], w=0.35, extra='marker-end="url(#arr)"')
            g.text(ax, ay + 3.2, e["note"], 1.9, fill=C["sub"])
        elif e["side"] == "X":
            ax, ay = P(-2600, e["at"][1])
            bx, by = P(e["at"][0] + 900, e["at"][1])
            g.line(ax, ay, bx, by, st=C["red"], w=0.5, extra='marker-end="url(#arr)"')
            g.text(ax - 1, ay - 2, "患者動線（道路より直接）", 2.2, fill=C["red"], weight="bold", anchor="start")

    # --- 避難経路矢印（上階）
    cor = [r for r in f["rooms"] if r["kind"] == "corridor" and f["floor"] != "1F"]
    for r in cor:
        ax, ay = P(r["x1"] - 300, 700); bx, by = P(f.get("stair_door", (r["x0"], 0))[1] + 300, 700)
        g.line(ax, ay, bx, by, st=C["accent"], w=0.4, dash="1.2,0.8", extra='marker-end="url(#arr)"')
        sd = f.get("stair_door", (r["x0"], r["x0"] + 900))
        sx, sy = P((sd[0] + sd[1]) / 2, 0)
        g.line(sx - 900 * s / 2 * 1.4, sy, sx + 900 * s / 2 * 1.4, sy, st="white", w=wt * 1.4)
        g.path(f"M{sx-0.63*900*s},{sy} A{900*s},{900*s} 0 0 1 {sx+0.63*900*s},{sy}", st=C["wall"], sw=0.18)

    # --- 室名
    for r in f["rooms"]:
        if not r["label"] or not r["name"]:
            continue
        cx, cy = P(*(r.get("lp") or ((r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2)))
        a = area(r)
        if r["id"] == "mri":
            a += sum(area(o) for o in f["rooms"] if o["id"] == "mri2")
        if r["kind"] == "treat":
            portrait = (r["y1"] - r["y0"]) > (r["x1"] - r["x0"]) - 100
            cx, cy = P((r["x0"] + r["x1"]) / 2 + (450 if portrait else 0), r["y0"] + (260 if portrait else 650))
            g.text(cx, cy - 2.3, r["name"].replace("\n", " "), 1.9, weight="bold")
            g.text(cx, cy + 0.2, f"{a:.1f}㎡（約{a/1.62:.1f}畳）", 1.6, fill=C["sub"])
        elif r["kind"] in ("corridor", "hall"):
            g.text(cx, cy + 0.9, r["name"], 2.0, fill=C["accent"], weight="bold")
        else:
            big = 2.5 if s > 0.011 else 2.3
            g.text(cx, cy - 1.0, r["name"], big, weight="bold")
            if r["kind"] not in ("open", "existing"):
                g.text(cx, cy + 0.5 + big * 1.1 * (r["name"].count("\n") + 0.6), f"{a:.1f}㎡", 1.9, fill=C["sub"])
    if f.get("reception"):
        rc = f["reception"]
        m = math.radians((rc["a0"] + rc["a1"]) / 2)
        cx, cy = P(rc["cx"] + 150 * math.cos(m), rc["cy"] + 150 * math.sin(m))
        g.text(cx, cy + 0.9, "受付", 2.6, weight="bold")

    # --- 区画線（リースライン）
    if f["floor"] == "1F":
        nt = f["notch"]
        pts = [(0, 0), (W, 0), (W, nt[1]), (nt[0], nt[1]), (nt[0], D), (0, D)]
    else:
        e0, e1, ed = f["evh"]
        pts = [(0, -4800), (2000, -4800), (2000, 0), (e0, 0), (e0, ed), (e1, ed), (e1, 0), (W, 0), (W, D), (0, D)]
    g.add('<polygon points="' + " ".join("%.2f,%.2f" % P(*q) for q in pts) + f'" fill="none" stroke="{C["red"]}" stroke-width="0.45"/>')
    # --- 寸法
    dims(g, f, P, s)
    # --- 通り芯
    for k, v in f["grid"].items():
        if -500 < v < W + 500:
            px, py = P(v, D)
            go = 30
            g.line(px, py - 2, px, py - go + 2.4, st="#999", w=0.12, dash="2,0.6,0.4,0.6")
            g.circle(px, py - go, 2.4, fill="white", st="#777", sw=0.2)
            g.text(px, py - go + 0.9, k, 2.0, fill="#555")
    return g


def door(g, r, dd, P, s, wt):
    side, at, w, typ = dd["side"], dd["at"], dd["w"], dd["type"]
    if side in ("S", "N"):
        yy = r["y0"] if side == "S" else r["y1"]
        p1, p2 = P(at - w / 2, yy), P(at + w / 2, yy)
        g.line(*p1, *p2, st="white", w=wt * 1.8)
        if typ == "slide":
            off = 1 if side == "S" else -1
            g.line(p1[0], p1[1] + off * 0.55, p2[0] + w * s * 0.15, p2[1] + off * 0.55, st=C["wall"], w=0.35)
        else:
            sgn = 1 if side == "S" else -1  # 室内側へ開く
            g.path(f"M{p1[0]},{p1[1]} L{p1[0]},{p1[1] - sgn*w*s} A{w*s},{w*s} 0 0 {1 if sgn>0 else 0} {p2[0]},{p2[1]}",
                   st=C["wall"], sw=0.18)
    else:
        xx = r["x0"] if side == "W" else r["x1"]
        p1, p2 = P(xx, at - w / 2), P(xx, at + w / 2)
        g.line(*p1, *p2, st="white", w=wt * 1.8 if r["kind"] != "mri" else wt * 3)
        if typ == "slide":
            off = 0.55 if side == "W" else -0.55
            g.line(p1[0] + off, p1[1], p2[0] + off, p2[1] - w * s * 0.15, st=C["wall"], w=0.35)
        else:
            sgn = 1 if side == "W" else -1
            g.path(f"M{p1[0]},{p1[1]} L{p1[0] + sgn*w*s},{p1[1]} A{w*s},{w*s} 0 0 {0 if sgn>0 else 1} {p2[0]},{p2[1]}",
                   st=C["wall"], sw=0.18)


def furniture(g, f, P, s):
    fw = "#9c8f84"
    def box(x0, y0, x1, y1, fill="white", st=fw, sw=0.15, rx=0):
        a, b = P(x0, y1)
        g.rect(a, b, (x1 - x0) * s, (y1 - y0) * s, fill=fill, st=st, sw=sw, extra=f'rx="{rx}"')
    for r in f["rooms"]:
        x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
        cx = (x0 + x1) / 2
        if r["kind"] == "treat":
            # ベッド（窓側に頭）＋ワゴン＋スツール＋荷物カゴ
            if y1 - y0 > x1 - x0 - 100:
                bx0 = x0 + 250
                box(bx0, y1 - 2150, bx0 + 800, y1 - 200, fill="#fff", rx=0.6)
                box(bx0 + 120, y1 - 600, bx0 + 680, y1 - 280, fill="#f2ede6", rx=0.4)
                box(x1 - 650, y1 - 650, x1 - 200, y1 - 200, fill="#e8dccb")
                a, b = P(x1 - 520, y1 - 1500); g.circle(a, b, 200 * s)
                box(x1 - 650, y0 + 250, x1 - 250, y0 + 600, fill="#f4efe8")
            else:
                box(x0 + 300, y1 - 1050, x0 + 2250, y1 - 250, fill="#fff", rx=0.6)
                box(x0 + 2000, y1 - 980, x0 + 2230, y1 - 320, fill="#f2ede6", rx=0.3)
                a, b = P(x1 - 420, y1 - 1500); g.circle(a, b, 190 * s)
                box(x1 - 600, y0 + 200, x1 - 200, y0 + 550, fill="#e8dccb")
        elif r["kind"] == "mri" and r.get("mri_axis") == "y":
            # 1.5T 超電導MRI（ボア軸＝Y方向）。ガントリーを北側、寝台を南側（操作室の観察窓側）に配置
            gx, gy = x0 + 2100, 4350
            box(gx - 1100, gy - 1000, gx + 1100, gy + 1000, fill="#dfe6ec", st=C["blue"], sw=0.25, rx=1.5)
            a, b = P(gx, gy); g.circle(a, b, 330 * s, fill="white", st=C["blue"], sw=0.2)
            box(gx - 300, 500, gx + 300, gy - 1000, fill="white", st=C["blue"], sw=0.2, rx=0.5)
            g.text(a, b - 14, "1.5T MRI（富士フイルム）", 1.7, fill=C["blue"], anchor="middle")
            # 5ガウスライン目安（破線）
            g.add(f'<ellipse cx="{a:.2f}" cy="{b:.2f}" rx="{2000*s:.2f}" ry="{2500*s:.2f}" fill="none" stroke="{C["blue"]}" stroke-width="0.15" stroke-dasharray="1,0.8"/>')
        elif r["id"] == "ex":
            box(x0 + 200, y0 + 300, x0 + 1600, y0 + 900)
            a, b = P(x0 + 900, y0 + 1350); g.circle(a, b, 230 * s)
            a, b = P(x0 + 1900, y0 + 1300); g.circle(a, b, 230 * s)
            box(x1 - 900, y1 - 2100, x1 - 200, y1 - 200, rx=0.5)
        elif r["id"] == "tr":
            box(x0 + 400, y0 + 900, x0 + 2400, y0 + 1600, rx=0.5)
            box(x0 + 150, y0 + 150, x0 + 1600, y0 + 600, fill="#ecebe8")
            box(x1 - 700, y0 + 150, x1 - 200, y0 + 600, fill="#ecebe8")
        elif r["id"] == "op":
            box(x0 + 150, y1 - 750, x1 - 150, y1 - 150, fill="#ecebe8")
            a, b = P(x0 + 1000, y1 - 1150); g.circle(a, b, 220 * s)
            g.line(*P(x1, y1 - 300), *P(x1, y1 - 1800), st=C["blue"], w=0.6)  # 観察窓
        elif r["id"] == "mech":
            box(x0 + 150, y1 - 700, x1 - 150, y1 - 150, fill="#e6e6e6")
            box(x0 + 150, y0 + 1000, x0 + 900, y1 - 900, fill="#e6e6e6")
        elif r["id"] in ("lm", "slm", "slw", "mch"):
            n = int((y1 - y0 - 300) / 400)
            for i in range(n):
                box(x0 + 100, y0 + 150 + i * 400, x0 + 550, y0 + 550 + i * 400, fill="#e8dccb")
            if x1 - x0 > 1300:
                box(x1 - 550, y0 + 500, x1 - 150, y0 + 1500, fill="#f4efe8", rx=0.4)
        elif r["id"] == "lw":
            n = int((x1 - x0 - 300) / 400)
            for i in range(n):
                box(x0 + 150 + i * 400, y0 + 100, x0 + 550 + i * 400, y0 + 550, fill="#e8dccb")
            box(x0 + 150, y1 - 550, x0 + 1500, y1 - 100, fill="#efe4d2")
            for i in range(2):
                a, b = P(x0 + 450 + i * 700, y1 - 850); g.circle(a, b, 180 * s)
        elif r["id"] == "pw":
            box(x0 + 100, y0 + 150, x0 + 550, y1 - 300, fill="#efe4d2")
            for i in range(3):
                a, b = P(x0 + 800, y0 + 600 + i * 700); g.circle(a, b, 180 * s)
        elif r["id"] == "sr":
            box(x0 + 1000, y0 + 1500, x0 + 3200, y0 + 2700, rx=0.8, fill="#f4efe8")
            for xx in (1300, 2100, 2900):
                for yy in (1150, 3050):
                    a, b = P(x0 + xx, y0 + yy); g.circle(a, b, 220 * s)
            box(x0 + 100, y1 - 700, x0 + 2700, y1 - 100, fill="#ecebe8")
            g.text(*P(x0 + 1400, y1 - 450), "ミニキッチン", 1.5, fill=C["sub"])
            box(x1 - 700, y1 - 700, x1 - 150, y1 - 100, fill="#ecebe8")
        elif r["id"] in ("cs",):
            box(x0 + 600, y0 + 1300, x0 + 2100, y0 + 2100, rx=0.6, fill="#f4efe8")
            for yy in (1000, 2400):
                a, b = P(x0 + 1350, y0 + yy); g.circle(a, b, 230 * s)
        elif r["id"] in ("of5", "st4"):
            box(x0 + 150, y0 + 200, x1 - 150, y0 + 900, fill="#f4efe8")
            for i in range(2 if x1 - x0 > 2000 else 1):
                a, b = P(x0 + 750 + i * 1100, y0 + 1300); g.circle(a, b, 220 * s)
            box(x0 + 150, y1 - 550, x1 - 150, y1 - 150, fill="#ecebe8")
        elif r["kind"] == "service" and r["id"] not in ("bk",):
            box(x0 + 120, y0 + 120, x0 + 600, y1 - 120, fill="#ecebe8")
            if x1 - x0 > 1800:
                box(x1 - 600, y0 + 120, x1 - 120, y1 - 120, fill="#ecebe8")
    # 手洗い
    for r in f["rooms"]:
        for (sx_, sy_) in r.get("sinks", []):
            box(sx_ - 250, sy_ - 200, sx_ + 250, sy_ + 200, fill="white", st=fw, sw=0.15, rx=0.4)
            a, b = P(sx_, sy_); g.circle(a, b, 110 * s, st=fw, sw=0.12)
    # 待合椅子
    for (x, y, rot) in f.get("chairs", []):
        cx, cy = P(x, y)
        g.add(f'<g transform="translate({cx:.2f},{cy:.2f}) rotate({-rot+90})">'
              f'<rect x="{-300*s}" y="{-300*s}" width="{600*s}" height="{600*s}" rx="0.6" fill="#ece3d6" stroke="{fw}" stroke-width="0.15"/>'
              f'<rect x="{-300*s}" y="{-300*s}" width="{600*s}" height="{130*s}" fill="#d8c9b5"/></g>')
    # 受付カウンター（円弧）
    rc = f.get("reception")
    if rc:
        cx, cy = P(rc["cx"], rc["cy"])
        R1, R2 = rc["r"] * s, (rc["r"] - 550) * s
        def arc(R, a0, a1):
            return (cx + R * math.cos(math.radians(a0)), cy - R * math.sin(math.radians(a0)),
                    cx + R * math.cos(math.radians(a1)), cy - R * math.sin(math.radians(a1)))
        a = arc(R1, rc["a0"], rc["a1"]); b = arc(R2, rc["a1"], rc["a0"])
        g.path(f"M{a[0]:.2f},{a[1]:.2f} A{R1},{R1} 0 0 0 {a[2]:.2f},{a[3]:.2f} L{b[0]:.2f},{b[1]:.2f} "
               f"A{R2},{R2} 0 0 1 {b[2]:.2f},{b[3]:.2f} Z", fill=C["wood"], st="#7d6347", sw=0.2)
        if rc.get("back"):
            # 背面シェルフ壁（銀座院と同様のロゴ壁）
            bx0, by0, bx1, by1 = rc["back"]
            box(bx0, by0, bx1, by1, fill="#d9c3a3", st="#7d6347", sw=0.2)
            lx, ly = P((bx0 + bx1) / 2, by1)
            if bx1 - bx0 > by1 - by0:
                g.text(lx, ly - 0.7, "ロゴ壁・収納棚", 1.6, fill=C["sub"])
            else:
                lx, ly = P(bx1 - 1400, by1 + 250)
                g.text(lx, ly, "ロゴ壁・収納棚", 1.6, fill=C["sub"])
        mid = (rc["a0"] + rc["a1"]) / 2
        for k in (-38, 38):
            ang = math.radians(mid + k)
            a2, b2 = cx + (R2 - 380 * s) * math.cos(ang), cy - (R2 - 380 * s) * math.sin(ang)
            g.circle(a2, b2, 200 * s, st=fw, sw=0.15)
    # フリースペース家具
    lg = f.get("lounge")
    if lg:
        x0, y0, x1, y1 = lg["x0"], lg["y0"], lg["x1"], lg["y1"]
        # 造作ベンチ（窓なし面を囲うL型）＋ ラウンドテーブル
        box(x0, y0, x0 + 600, y1, fill="#ece3d6")
        box(x0, y1 - 600, x0 + 3800, y1, fill="#ece3d6")
        for i, (tx, ty) in enumerate([(1800, 1700), (3500, 900)]):
            a, b = P(x0 + tx, y0 + ty); g.circle(a, b, 450 * s, fill="#f4efe8", st=fw, sw=0.15)
        for tx, ty in [(5200, 1900), (6400, 1900), (5200, 700), (6400, 700)]:
            box(x0 + tx - 300, y0 + ty - 300, x0 + tx + 300, y0 + ty + 300, fill="#ece3d6", rx=0.6)
        box(x0 + 5500, y0 + 1050, x0 + 6100, y0 + 1550, fill="#f4efe8", rx=0.4)
        a, b = P(x1 - 300, y0 + 400)
        g.text(*P(x0 + 1800, y1 - 1200), "造作ベンチ", 1.5, fill=C["sub"])
        box(x1 + 50, y0 - 400, x1 + 450, y0 + 1400, fill="#ecebe8")
        g.text(*P(x1 + 250, y0 + 1700), "WS", 1.4, fill=C["sub"])


def dims(g, f, P, s):
    W, D = f["W"], f["D"]
    off = 7.5

    def hdim(xa, xb, yy, label, up=True):
        p1, p2 = P(xa, yy), P(xb, yy)
        y = p1[1]
        g.line(p1[0], y, p2[0], y, st="#555", w=0.12)
        for p in (p1, p2):
            g.line(p[0] - 0.6, y + 0.6, p[0] + 0.6, y - 0.6, st="#555", w=0.25)
            g.line(p[0], y - 1, p[0], y + 1, st="#555", w=0.12)
        g.text((p1[0] + p2[0]) / 2, y - 0.7, label, 1.9, fill="#444")

    def vdim(ya, yb, xx, label):
        p1, p2 = P(xx, ya), P(xx, yb)
        x = p1[0]
        g.line(x, p1[1], x, p2[1], st="#555", w=0.12)
        for p in (p1, p2):
            g.line(x - 0.6, p[1] + 0.6, x + 0.6, p[1] - 0.6, st="#555", w=0.25)
            g.line(x - 1, p[1], x + 1, p[1], st="#555", w=0.12)
        g.add(f'<text x="{x - 0.8:.2f}" y="{(p1[1]+p2[1])/2:.2f}" font-size="1.9" fill="#444" text-anchor="middle" '
              f'font-family="{FONT}" transform="rotate(-90 {x - 0.8:.2f} {(p1[1]+p2[1])/2:.2f})">{label}</text>')

    yb = D + 2600 / (s * 100) * 0 + 1200
    if f["floor"] == "1F":
        hdim(0, W, D + 1900, f"{W:,}")
        for a, b in [(0, 4200), (4200, 6300), (6300, 7400), (7400, 8800), (8800, W)]:
            hdim(a, b, D + 1150, f"{b-a:,}")
        vdim(0, D, -1300, f"{D:,}")
        for a, b in [(0, 2800), (2800, 4000), (4000, D)]:
            vdim(a, b, W + 700, f"{b-a:,}")
    else:
        hdim(0, W, D + 1900, f"{W:,}（想定）")
        xs = sorted({r["x0"] for r in f["rooms"] if r["kind"] == "treat" and r["y1"] == D} | {W})
        for a, b in zip(xs, xs[1:]):
            hdim(a, b, D + 1100, f"{b-a:,}")
        vdim(0, D, -1350, f"{D:,}（想定）")
        for a, b in [(0, 1300), (1300, 4500), (4500, 6100), (6100, D)]:
            vdim(a, b, W + 750, f"{b-a:,}")


def legend(g, x, y, items):
    for i, (fill, label) in enumerate(items):
        g.rect(x, y + i * 4.6, 6, 3.2, fill=fill, st="#999", sw=0.15)
        g.text(x + 8, y + i * 4.6 + 2.5, label, 2.1, anchor="start")


def summary_table(g, x, y, f):
    extra = {r["id"]: area(r) for r in f["rooms"] if r["id"] == "mri2"}
    rows = [(r["name"].replace("\n", ""), area(r) + (extra.get("mri2", 0) if r["id"] == "mri" else 0)) for r in f["rooms"]
            if r["kind"] in ("treat", "room", "mri", "service") and r["name"]]
    g.text(x, y, "諸室面積表（内法・概算）", 2.4, anchor="start", weight="bold")
    yy = y + 3.6
    tr = [a for n, a in rows if n.startswith("施術室")]
    other = [(n, a) for n, a in rows if not n.startswith("施術室")]
    if tr:
        g.text(x, yy, f"施術室 × {len(tr)}室", 2.0, anchor="start"); g.text(x + 52, yy, f"各{min(tr):.1f}～{max(tr):.1f}㎡", 2.0, anchor="end"); yy += 3.1
    for n, a in other:
        g.text(x, yy, n, 2.0, anchor="start"); g.text(x + 52, yy, f"{a:.1f}㎡", 2.0, anchor="end"); yy += 3.1
    g.line(x, yy - 1.8, x + 52, yy - 1.8, st="#bbb", w=0.15)
    return yy


SCAN = ("assets/plan_1F_scan.png", 450, 380, 2650, 1720)   # 募集図面（1階）切出し：path, 左上px, 幅, 高さ


def make_plan(floor):
    f = FLOORS[floor]
    s = 1 / 100
    scale = "1/100"
    if floor == "1F":
        ox, oy = 42, 142
        g0 = draw_floor(f, ox, oy, s, scan=(os.path.join(os.path.dirname(__file__), SCAN[0]),) + SCAN[1:])
    else:
        ox, oy = 48, 150
        g0 = draw_floor(f, ox, oy, s)
    g = SVG()
    g.o = g0.o
    tc = treat_count()
    m2, tsubo = AREA[floor]
    notes = {
        "1F": ["・下図（グレー）は貸主提供の募集図面（1階 店舗区画）。赤線＝貸室区画（98.36㎡）、着色部・室配置が当社計画（C工事）。",
               "・MRI：富士フイルム製1.5T（ゼロヘリウム型想定・クエンチ配管不要）。検査室約31.5㎡・機械室約5.4㎡・操作室約3.9㎡。破線は5ガウスライン目安。機種仕様書で要確認。",
               "・床荷重5,000N/㎡の1Fに配置。荷重分散架台・搬入経路（マシンハッチ1,830×2,500）・振動・騒音・電源容量をビル側と協議。",
               "・道路側ガラス面から600mm以内には造作・サインを設けない（内装マニュアル7-(7)）。",
               "・トイレは館内共用トイレを利用。間仕切・内装材は全て不燃材、カーペットは防炎品。"],
        "4F": [f"・施術室 4F {tc['4F']}室 ＋ 5F {tc['5F']}室 ＝ 計{tc['4F']+tc['5F']}室（要件15～20室）。各室 約6.5㎡（約4畳）。間仕切は上部開放の欄間式（欄間h=500）。",
               "・受付はEVホール正面・フロア中央に大きく配置（銀座院と同じ円形カウンター＋木の天井リング）。ロビーは柱・壁のない開放的な空間。",
               "・特別避難階段・共用トイレへは廊下・通路で直接つながる計画（EVホール～階段附室を廊下状に確保：内装マニュアル6-(7)）。",
               "・X1側（施術室側）は窓なし。通路は両側居室部分を有効1,600mm（令119条）。平面は募集図面をもとに作図、実施設計時に白図で確定。"],
        "5F": [f"・施術室 {tc['5F']}室（各 約6.5㎡・約4畳）、フリースペース、スタッフ休憩室・スタッフ更衣室（男女）・物品庫を5階に集約。",
               "・フリースペースは施術前後の待合・カウンセリング・セミナー兼用のラウンジ。",
               "・特別避難階段・共用トイレへは廊下・通路で直接つながる計画（4Fと同一）。",
               "・X1側（施術室側）は窓なし。平面形状は募集図面（4・5階 G229.86㎡）をもとに作図、実施設計時にビル側白図で寸法を確定。"],
    }[floor]
    no = {"1F": "A-01", "4F": "A-02", "5F": "A-03"}[floor]
    title_block(g, f["title"], scale, no, notes)
    if floor == "1F":
        legend(g, 330, 70, [(C["tint"], f"貸室 {m2}㎡（約{tsubo}坪）"), ("#f8f4ee", "診察・処置・操作・更衣"),
                            (C["mri"], "MRI室（シールド工事）"), (C["service"], "機械室"),
                            ("#eeeeee", "既設アプローチ（区画内）")])
        summary_table(g, 330, 104, f)
        g.text(14, 20, "← 正面道路（Y1通り・歩道）", 2.6, anchor="start", fill=C["red"], weight="bold")
    else:
        legend(g, 330, 70, [(C["tint"], f"貸室 G{m2}㎡（約{tsubo}坪）"), (C["treat"], "施術室（銀座院仕様）"),
                            ("#f8f4ee", "個室（更衣・カウンセリング等）"), (C["service"], "バックヤード"),
                            ("#f3ebdd", "廊下・通路（階段・トイレへ）"), (C["core"], "共用部（コア）")])
        summary_table(g, 330, 108, f)
        g.text(14, 20, "← 正面道路（Y1通り）", 2.6, anchor="start", fill=C["red"], weight="bold")
    north_marker(g, 395, 38)
    g.text(PAGE_W / 2, 18, f"{f['title']}", 4.2, weight="bold")
    g.text(PAGE_W / 2, 24.5, f"貸室面積 {'G' if floor != '1F' else ''}{m2}㎡（約{tsubo}坪）", 3.0, fill=C["red"], weight="bold")
    return g.svg()


if __name__ == "__main__":
    out = sys.argv[1]
    for fl in ("1F", "4F", "5F"):
        open(os.path.join(out, f"plan_{fl}.svg"), "w").write(make_plan(fl))
    print("ok", treat_count())
