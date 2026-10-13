# 1階 図面一式（平面計画・玄関ポーチ詳細・外装・内装）を A3 横の HTML として出力する
import math

RED = "#C3172E"; NAVY = "#1F2B5E"; INK = "#222"; SUB = "#666"
WOOD = "#B8926A"; WOODL = "#D9BE9C"; BEIGE = "#F6EEE3"; IVORY = "#FBF7F0"; GREY = "#E6E6E6"; MRI = "#DDE5EE"
FONT = "'Noto Sans Mono CJK JP','Noto Sans CJK JP',monospace"

# 部屋の内法（貸主図面からの読み取り。原点＝区画内側の左上、x＝奥へ、y＝隣地側→館内側）
W, D = 13900, 6615
PORCH = (0, 595, 1680, 2300)          # 玄関ポーチ x0,y0,x1,y1
DOOR_X = 1680
LS = dict(x=-3303.3, y=-2822.3, w=27914, h=19734)   # 貸主図面(pt)→mm の配置


class S:
    """SVG を組み立てる小さなヘルパー（座標は mm）"""
    def __init__(self, scale):
        self.k = scale            # 1:scale
        self.o = []

    def t(self, size_pt):         # 紙面上のポイント数 → モデル寸法
        return size_pt * 0.3528 * self.k

    def add(self, s): self.o.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=0.25, extra=""):
        self.add(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="{self.t(sw):.1f}" {extra}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=0.25, dash=None, extra=""):
        d = f'stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{stroke}" stroke-width="{self.t(sw):.1f}" {d} {extra}/>')

    def path(self, d, fill="none", stroke=INK, sw=0.25, extra=""):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{self.t(sw):.1f}" {extra}/>')

    def text(self, x, y, s, size=7, fill=INK, anchor="start", weight=400, rot=0, extra=""):
        r = f'transform="rotate({rot} {x:.0f} {y:.0f})"' if rot else ""
        self.add(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{self.t(size):.0f}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {r} {extra}>{s}</text>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=0.25, dash=None):
        d = f'stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="{self.t(sw):.1f}" {d}/>')

    def arrow(self, pts, color=RED, sw=0.6, dash=None):
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        da = f'stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{self.t(sw):.1f}" {da} marker-end="url(#ah)"/>')

    def dim(self, x1, y1, x2, y2, label, off=0, size=6, vertical=False):
        """寸法線（水平 or 垂直）"""
        tk = self.t(1.2)
        if not vertical:
            y = y1 + off
            self.line(x1, y, x2, y, SUB, 0.18)
            for x in (x1, x2):
                self.line(x - tk, y + tk, x + tk, y - tk, SUB, 0.25)
                self.line(x, y1, x, y + (tk if off > 0 else -tk), SUB, 0.12, "40 40")
            self.text((x1 + x2) / 2, y - self.t(1.2), label, size, SUB, "middle")
        else:
            x = x1 + off
            self.line(x, y1, x, y2, SUB, 0.18)
            for y in (y1, y2):
                self.line(x - tk, y + tk, x + tk, y - tk, SUB, 0.25)
            self.text(x - self.t(1.2), (y1 + y2) / 2, label, size, SUB, "middle", rot=-90)

    def svg(self, vb, w_mm, h_mm, cls=""):
        x, y, w, h = vb
        defs = f'''<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>
<pattern id="hatch" width="120" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="120" stroke="#9a9a9a" stroke-width="14"/></pattern>
<pattern id="slat" width="90" height="90" patternUnits="userSpaceOnUse"><rect width="90" height="90" fill="{WOODL}"/><rect width="38" height="90" fill="{WOOD}"/></pattern>
<pattern id="vslat" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="{WOODL}"/><rect width="26" height="60" fill="{WOOD}"/></pattern>
<clipPath id="cp{id(self)}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'''
        return f'<svg class="{cls}" width="{w_mm}mm" height="{h_mm}mm" viewBox="{x} {y} {w} {h}" font-family="{FONT}">{defs}<g clip-path="url(#cp{id(self)})">{"".join(self.o)}</g></svg>'


def underlay(s, op=0.42):
    s.add(f'<image href="landlord.svg" x="{LS["x"]}" y="{LS["y"]}" width="{LS["w"]}" height="{LS["h"]}" opacity="{op}" preserveAspectRatio="none"/>')


def door(s, hx, hy, length, a0, a1, sw=0.3, color=INK):
    """開き戸：ヒンジ(hx,hy)、扉長さ、閉→開の角度(度、0=+x, 90=+y)"""
    r0, r1 = math.radians(a0), math.radians(a1)
    x0, y0 = hx + length * math.cos(r0), hy + length * math.sin(r0)
    x1, y1 = hx + length * math.cos(r1), hy + length * math.sin(r1)
    s.line(hx, hy, x1, y1, color, sw)
    sweep = 1 if a1 > a0 else 0
    s.path(f"M{x0:.0f},{y0:.0f} A{length},{length} 0 0 {sweep} {x1:.0f},{y1:.0f}", stroke=color, sw=0.15)


def wall(s, x1, y1, x2, y2, t=100, fill="#3a3a3a"):
    if x1 == x2:
        s.rect(x1 - t / 2, min(y1, y2), t, abs(y2 - y1), fill, "none", 0)
    else:
        s.rect(min(x1, x2), y1 - t / 2, abs(x2 - x1), t, fill, "none", 0)


def person(s, x, ground, h=1700, color="#777"):
    hr = h * 0.075
    s.circle(x, ground - h + hr, hr, "none", color, 0.25)
    s.line(x, ground - h + 2 * hr, x, ground - h * 0.48, color, 0.25)
    s.line(x - h * 0.17, ground - h * 0.72, x + h * 0.17, ground - h * 0.72, color, 0.25)
    s.line(x, ground - h * 0.48, x - h * 0.1, ground, color, 0.25)
    s.line(x, ground - h * 0.48, x + h * 0.1, ground, color, 0.25)


# ------------------------------------------------------------------ A-01 平面計画図
def sheet_plan():
    s = S(50)
    underlay(s)
    # 区画
    s.rect(0, 0, W, D, "none", RED, 0.7)
    # 用途の塗り分け
    zones = [
        (0, 0, 4200, D, BEIGE),                       # 受付・待合
        (4200, 0, 2500, 2550, IVORY), (6700, 0, 2100, 2550, GREY),
        (4200, 2550, 4600, 1200, "#EFE4D4"),          # 廊下
        (4200, 3750, 2100, D - 3750, IVORY), (6300, 3750, 1100, D - 3750, IVORY), (7400, 3750, 1400, D - 3750, IVORY),
        (8800, 0, 5100, D, MRI),
    ]
    for x, y, w, h, c in zones:
        s.rect(x, y, w, h, c, "none", 0, 'opacity="0.85"')
    # 玄関ポーチ（屋外・区画内）
    x0, y0, x1, y1 = PORCH
    s.rect(x0, y0, x1 - x0, y1 - y0, "#ffffff", "none", 0)
    s.rect(x0, y0, x1 - x0, y1 - y0, "url(#hatch)", "none", 0, 'opacity="0.35"')
    s.rect(x0, y0, x1 - x0, y1 - y0, "none", RED, 0.35, 'stroke-dasharray="80 50"')
    # ポーチ上の小スペース（収納）
    s.path("M560,40 L1640,40 L1640,545 L560,545 Z", WOODL, WOOD, 0.25)
    s.text(1100, 380, "収納", 5.5, INK, "middle")
    # 新設間仕切り（C工事）
    for a in [(4200, 0, 4200, 2550), (6700, 0, 6700, 2550), (4200, 3750, 4200, D), (6300, 3750, 6300, D),
              (7400, 3750, 7400, D), (4200, 2550, 5150, 2550), (6050, 2550, 7250, 2550), (8150, 2550, 8800, 2550),
              (4200, 3750, 4550, 3750), (5450, 3750, 6450, 3750), (7250, 3750, 7550, 3750), (8350, 3750, 8800, 3750)]:
        wall(s, *a)
    # MRI 電磁シールド壁
    for a in [(8800, 0, 8800, 2650), (8800, 3650, 8800, D)]:
        wall(s, *a, t=160, fill=NAVY)
    wall(s, 8800, 4400, 8800, 5600, t=160, fill="#8FB0D0")   # シールド窓
    # 扉（C工事）
    door(s, 5150, 2550, 900, 0, -90)          # 診察室
    door(s, 7250, 2550, 900, 0, -90)          # 機械室
    door(s, 4550, 3750, 900, 0, 90)           # 処置室
    door(s, 6450, 3750, 800, 0, 90)           # 更衣
    door(s, 7550, 3750, 800, 0, 90)           # 操作室
    door(s, 8800, 2650, 1000, 90, 180, 0.35, NAVY)   # MRI シールド扉
    # 既設 SUS 両開き扉（A工事）
    door(s, DOOR_X, 595, 1000, 90, 0, 0.7, RED)
    door(s, DOOR_X, 2300, 640, -90, 0, 0.7, RED)
    s.line(DOOR_X, 595, DOOR_X, 2300, RED, 0.12, "60 40")
    # 受付
    s.rect(2900, 60, 1250, 420, WOODL, WOOD, 0.2)               # 背面収納
    s.path("M2900,900 L4150,900 L4150,1500 L2900,1500 Z", WOOD, "#7a5a3a", 0.3)   # カウンター
    s.circle(3300, 700, 170, "#fff", SUB); s.circle(3800, 700, 170, "#fff", SUB)
    # 待合のベンチ
    for (cx, cy) in [(900, 3300), (1450, 3300), (2000, 3300), (900, 4250), (1450, 4250), (2000, 4250), (900, 5200), (1450, 5200)]:
        s.rect(cx - 230, cy - 230, 460, 460, "#EFE2CF", "#b39a7a", 0.2, 'rx="60"')
    s.circle(3300, 3300, 260, "#cfe3c8", "#8aa982", 0.2)
    s.circle(3600, 5900, 220, "#cfe3c8", "#8aa982", 0.2)
    # ガラス面から600mm内側の木調スクリーン
    s.rect(600, 2450, 70, 3900, "url(#vslat)", WOOD, 0.2)
    s.line(0, 6350, 600, 6350, SUB, 0.15)
    s.text(300, 6250, "600", 5, SUB, "middle")
    # 車いす回転
    s.circle(2350, 1700, 750, "none", SUB, 0.2, "60 50")
    # MRI 本体
    s.rect(10350, 900, 1700, 1900, "#c7d3e0", NAVY, 0.3, 'rx="150"')
    s.circle(11200, 1850, 380, "#fff", NAVY, 0.3)
    s.rect(10950, 2800, 500, 2700, "#fff", NAVY, 0.25)
    s.circle(11200, 2100, 2450, "none", NAVY, 0.15, "80 60")
    # 動線
    s.arrow([(-1100, 1450), (2500, 1450), (2750, 1450)], RED, 0.7)
    s.arrow([(2990, D + 900), (2990, 5200)], "#555", 0.5, "120 80")
    s.arrow([(3000, 2000), (4600, 3150), (8300, 3150)], RED, 0.4, "100 70")
    # 文字
    T = s.text
    T(-1100, 1300, "患者動線（道路より）", 6, RED, weight=700)
    T(840, 1400, "玄関ポーチ", 6.5, INK, "middle", 700)
    T(840, 1620, "（屋外・区画内）", 5, SUB, "middle")
    T(840, 1840, "道路側は開放", 5, RED, "middle")
    T(DOOR_X + 120, 2520, "既設SUS両開き扉（A工事）", 5, RED)
    T(3525, 1280, "受付", 7, "#fff", "middle", 700)
    T(1400, 2850, "待合（8席）", 7, INK, "middle", 700)
    T(700, 6150, "木調スクリーン H2,100（ガラス面から600離す）", 4.6, "#7a5a3a")
    T(2350, 2300, "車いす回転φ1,500", 4.6, SUB, "middle")
    T(3000, D + 1100, "館内側出入口（既設）→ EV・4/5階 整痛院", 5, "#555", "middle")
    for (x, y, a, b) in [(5450, 1000, "診察室", "6.4㎡"), (7750, 1000, "MRI機械室", "5.4㎡"), (6500, 3250, "廊下", ""),
                         (5250, 5100, "処置室", "5.9㎡"), (6850, 5000, "MRI更衣", "3.1㎡"), (8100, 5100, "MRI操作室", "3.9㎡")]:
        T(x, y, a, 6.5, INK, "middle", 700)
        if b: T(x, y + 260, b, 5, SUB, "middle")
    T(11350, 6050, "MRI検査室（電磁シールド）", 6.5, NAVY, "middle", 700)
    T(11350, 6310, "31.5㎡　1.5T", 5, SUB, "middle")
    T(13750, 450, "駐車場側出入口（既設）→ MRI搬入口として利用を検討", 4.6, SUB, "end")
    # 寸法
    s.dim(0, 0, 1680, 0, "1,680", -650); s.dim(1680, 0, 4200, 0, "2,520", -650)
    s.dim(4200, 0, 6700, 0, "2,500", -650); s.dim(6700, 0, 8800, 0, "2,100", -650); s.dim(8800, 0, W, 0, "5,100", -650)
    s.dim(0, 0, W, 0, "13,900", -1150)
    s.dim(0, 0, 0, 595, "595", -650, vertical=True); s.dim(0, 595, 0, 2300, "1,705", -650, vertical=True)
    s.dim(0, 2300, 0, D, "4,315", -650, vertical=True); s.dim(0, 0, 0, D, "6,615", -1150, vertical=True)
    T(-1400, D + 700, "道路（歩道）", 6, RED, weight=700)
    return s.svg((-1500, -1500, 16300, 9400), 326, 188)


AREAS = [("玄関ポーチ（屋外）", "2.9"), ("受付・待合", "24.3"), ("診察室", "6.4"), ("MRI機械室", "5.4"), ("廊下", "5.5"),
         ("処置室", "5.9"), ("MRI更衣（1名）", "3.1"), ("MRI操作室", "3.9"), ("MRI検査室", "31.5")]


def title_block(no, title, scale, sub="基本計画（出店企画書添付資料）　2026.10　改訂1"):
    return f'''<div class="tb"><div class="tb1">整形外科ふっか／整痛院ふっか 東京駅院 出店計画 ／ 日本橋WASAMIビル</div>
<div class="tb2"><div><b>{title}</b><span>{sub}</span></div><div class="sc"><b>{scale}</b><span>No.{no}　A3</span></div></div></div>'''


def page(inner, no, title, scale):
    return f'<section class="sheet">{inner}{title_block(no, title, scale)}</section>'


def build_plan():
    rows = "".join(f"<tr><td>{a}</td><td>{b}㎡</td></tr>" for a, b in AREAS)
    inner = f'''<h1>1階 平面計画図（玄関ポーチ・受付待合・診察室・処置室・MRI室）</h1>
<p class="sub">貸室面積 98.36㎡（約29.75坪）　玄関ポーチを含む</p>
<div class="fig" style="left:14mm;top:24mm">{sheet_plan()}</div>
<div class="legend" style="left:14mm;top:214mm">
<div class="lg"><i style="background:{BEIGE}"></i>受付・待合</div><div class="lg"><i style="background:{IVORY}"></i>診察・処置・更衣・操作</div>
<div class="lg"><i style="background:{MRI}"></i>MRI室（シールド工事）</div><div class="lg"><i style="background:{GREY}"></i>機械室</div>
<div class="lg"><i class="ht"></i>玄関ポーチ（屋外・区画内）</div><div class="lg"><i style="background:{RED};height:1mm"></i>既設SUS扉（A工事）</div></div>
<table class="area" style="left:14mm;top:226mm"><tr><th colspan="2">諸室面積表（内法・概算）</th></tr>{rows}</table>
<div class="notes" style="left:84mm;top:226mm;width:150mm"><b>改訂内容（2026.10）</b>
<p>・入口は風除室ではなく「玄関ポーチ＋既設SUS製両開き扉（A工事）」に修正。道路側は開放（扉・ガラスなし）。</p>
<p>・玄関ポーチは賃貸区画に含む。屋外のため床・天井は既設のまま、造作は置かない。</p>
<p>・既設扉は店内側に開く（大扉 約1,000）。受付カウンターは扉の開く範囲から離し、手前に車いす回転スペースφ1,500を確保。</p>
<p>・道路側ガラス面から600mm以内には造作・サインを設けない（内装マニュアル）。木調スクリーンは600mm内側に自立させる。</p>
<p>・下図（グレー）は貸主提供の1階図面。寸法は図面からの読み取り値で、実施設計時にCADで確定する。</p></div>'''
    return page(inner, "A-01", "1階 平面計画図（改訂）", "S=1/50")


CSS = """
@page{size:420mm 297mm;margin:0}
*{box-sizing:border-box}body{margin:0;background:#ccc;font-family:'Noto Sans CJK JP',sans-serif;color:#222}
.sheet{position:relative;width:420mm;height:297mm;background:#fff;margin:0 auto 8mm;overflow:hidden;break-after:page}
.sheet::before{content:"";position:absolute;inset:6mm;border:0.5mm solid #333}
h1{position:absolute;left:0;right:0;top:11mm;margin:0;text-align:center;font:700 5.2mm/1 'Noto Sans Mono CJK JP',monospace;letter-spacing:.02em}
.sub{position:absolute;left:0;right:0;top:18mm;margin:0;text-align:center;color:#C3172E;font:700 3.4mm/1 'Noto Sans Mono CJK JP',monospace}
.fig{position:absolute}
.fig h2,.cap{font:700 3.2mm/1 'Noto Sans Mono CJK JP',monospace;margin:0 0 1.5mm}
.tb{position:absolute;right:6mm;bottom:6mm;width:176mm;border-top:0.4mm solid #333;border-left:0.4mm solid #333;font-family:'Noto Sans Mono CJK JP',monospace}
.tb1{padding:2.2mm 4mm;font:700 3mm/1.2 inherit;border-bottom:0.3mm solid #333}
.tb2{display:grid;grid-template-columns:1fr 38mm}
.tb2>div{padding:2.2mm 4mm;display:flex;flex-direction:column;gap:1.6mm}
.tb2 b{font-size:3.5mm}.tb2 span{font-size:2.3mm;color:#555}
.tb2 .sc{border-left:0.3mm solid #333;align-items:center}
.legend{position:absolute;display:flex;gap:5mm;flex-wrap:wrap;width:240mm;font:2.5mm/1 'Noto Sans Mono CJK JP',monospace}
.lg{display:flex;align-items:center;gap:1.5mm}.lg i{display:inline-block;width:6mm;height:3.5mm;border:0.2mm solid #999}
.lg i.ht{background:repeating-linear-gradient(45deg,#fff 0 .6mm,#bbb .6mm 1mm)}
table{position:absolute;border-collapse:collapse;font:2.4mm/1.35 'Noto Sans Mono CJK JP',monospace}
table th,table td{border-bottom:0.15mm solid #bbb;padding:0.6mm 2mm;text-align:left}
table th{border-bottom:0.3mm solid #333}
.area td:last-child{text-align:right}
.notes{position:absolute;font:2.4mm/1.55 'Noto Sans Mono CJK JP',monospace;color:#333}
.notes b{display:block;font-size:2.8mm;margin-bottom:1mm;color:#C3172E}.notes p{margin:0}
.callout{position:absolute;font:2.4mm/1.5 'Noto Sans Mono CJK JP',monospace}
.photo{position:absolute;display:flex;flex-direction:column;gap:1mm;font:2.3mm/1.3 'Noto Sans Mono CJK JP',monospace}
.photo img{width:100%;object-fit:cover;border:0.2mm solid #bbb}
.chips{position:absolute;display:grid;grid-template-columns:repeat(4,1fr);gap:2mm;font:2.2mm/1.3 'Noto Sans Mono CJK JP',monospace}
.chips div{display:flex;flex-direction:column;gap:1mm}.chips i{display:block;height:9mm;border:0.2mm solid #bbb}
@media print{body{background:#fff}.sheet{margin:0}}
"""

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from sheets2 import build_porch, build_ext, build_int
    html = f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>1階 図面 改訂1</title><style>{CSS}</style></head><body>"
    html += build_plan() + build_porch() + build_ext() + build_int() + "</body></html>"
    open("sheets.html", "w").write(html)
    print("ok")
