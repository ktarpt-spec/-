"""外観立面図・サイン計画図（A3横・SVG）"""
import sys, os
from plans import SVG, C, PAGE_W, PAGE_H, title_block, FONT

LOGO = "#24418f"
H1 = 4950          # 1F階高（CAD展開図 1FL→2FL より）
HT = 3900          # 基準階階高（想定）
FLOORS = 13
BW = 14300         # 正面（Y1面）外壁幅（X3～X1 外々・CADより）

# 正面ファサード 1F 構成（u: 立面左端 = X1側 からの距離）
F1_PARTS = [  # (u0, u1, kind, label)
    (0, 2300, "entry", "当社専用アプローチ（既設）"),
    (2300, 3300, "panel", "パネルA"),
    (3300, 5000, "window", "SSW-2（既設ガラス）"),
    (5000, 6800, "panel", "パネルA"),
    (6800, 10300, "ecp", "ECP（防災センター）"),
    (10300, BW, "bldg_entry", "ビルエントランス"),
]


def logo(g, x, y, size, color=LOGO, anchor="middle"):
    g.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
          f'font-family="Inter, DejaVu Sans, sans-serif" font-weight="500" letter-spacing="{size*0.02:.2f}">fukka</text>')


def callout(g, x, y, tx, ty, label, size=2.1, anchor="start", col="#333"):
    g.line(x, y, tx, ty, st=col, w=0.15)
    g.circle(x, y, 0.45, fill=col, st=col)
    g.text(tx + (0.8 if anchor == "start" else -0.8), ty + 0.7, label, size, anchor=anchor, fill=col)


def whole_elevation(g, ox, oy, s):
    """全体立面（模式）。ox,oy = GL左端"""
    H = H1 + HT * (FLOORS - 1) + 1500
    g.rect(ox, oy - H * s, BW * s, H * s, fill="#e9ecef", st="#555", sw=0.25)
    # 基準階：縦ルーバー＋ガラス
    for i in range(1, FLOORS):
        y0 = oy - (H1 + HT * i) * s
        g.line(ox, y0, ox + BW * s, y0, st="#9aa3ab", w=0.15)
        tenant = i in (3, 4)
        g.rect(ox + 600 * s, y0 + 700 * s, (BW - 1200) * s, (HT - 1300) * s,
               fill="#cfdae3" if not tenant else "#e8dcc6", st="#7f8c97", sw=0.12)
        for k in range(1, 14):
            xx = ox + (600 + k * (BW - 1200) / 14) * s
            g.line(xx, y0 + 700 * s, xx, y0 + (HT - 600) * s, st="#8d969e", w=0.25)
    g.rect(ox, oy - (H1 + HT * 2) * s, BW * s, (H1 + HT * 2) * s, fill="none", st="#555", sw=0.25)
    # 1F
    for u0, u1, k, _ in F1_PARTS:
        fill = {"entry": "#5d554e", "window": "#cfdae3", "bldg_entry": "#b7c4cf"}.get(k, "#d6d3cf")
        g.rect(ox + u0 * s, oy - (H1 - 900) * s, (u1 - u0) * s, (H1 - 900) * s, fill=fill, st="#666", sw=0.12)
    # 当社区画ハイライト
    for i in (3, 4):
        y0 = oy - (H1 + HT * i) * s
        g.rect(ox - 2, y0, BW * s + 4, HT * s, fill="none", st=C["red"], sw=0.35, extra='stroke-dasharray="1.2,0.6"')
    g.rect(ox - 2, oy - H1 * s, 6800 * s + 2, H1 * s, fill="none", st=C["red"], sw=0.35, extra='stroke-dasharray="1.2,0.6"')
    g.line(ox - 10, oy, ox + BW * s + 10, oy, st="#333", w=0.4)
    g.text(ox + BW * s + 3, oy + 0.8, "GL", 2.0, anchor="start")
    labels = [("1F", H1 / 2)] + [(f"{i+1}F", H1 + HT * (i - 1) + HT / 2) for i in range(1, FLOORS)]
    for name, hh in labels:
        col = C["red"] if name in ("1F", "4F", "5F") else "#777"
        g.text(ox - 3, oy - hh * s + 0.8, name, 2.0 if col != "#777" else 1.7, anchor="end", fill=col,
               weight="bold" if col != "#777" else "normal")
    g.text(ox + BW * s / 2, oy + 6, "正面全体立面（Y1通り・模式）", 2.4, weight="bold")
    g.text(ox + BW * s / 2, oy + 9.5, "S=1/300　赤破線＝当社区画", 1.9, fill=C["sub"])
    return H


def front_detail(g, ox, oy, s):
    """1F 正面部分立面（サイン・素材）"""
    top = H1 + 1800
    # 2F 下部
    g.rect(ox, oy - top * s, BW * s, (top - H1) * s, fill="#eceff2", st="#666", sw=0.2)
    g.rect(ox + 600 * s, oy - (top - 300) * s, (BW - 1200) * s, (top - H1 - 300) * s, fill="#d3dde5", st="#7f8c97", sw=0.15)
    for k in range(1, 14):
        xx = ox + (600 + k * (BW - 1200) / 14) * s
        g.line(xx, oy - (top - 300) * s, xx, oy - H1 * s, st="#8d969e", w=0.35)
    g.line(ox, oy - H1 * s, ox + BW * s, oy - H1 * s, st="#555", w=0.35)
    g.text(ox + BW * s + 2, oy - H1 * s + 0.8, "▽2FL", 2.0, anchor="start", fill="#555")
    # 1F 庇・軒天
    g.rect(ox, oy - H1 * s, BW * s, 900 * s, fill="#cfcac4", st="#666", sw=0.15)
    hh = H1 - 900
    for u0, u1, k, lab in F1_PARTS:
        x0 = ox + u0 * s; w = (u1 - u0) * s
        if k == "panel":
            g.rect(x0, oy - hh * s, w, hh * s, fill="#d9d6d2", st="#777", sw=0.15)
            for j in range(1, 4):
                g.line(x0, oy - hh * s * j / 4, x0 + w, oy - hh * s * j / 4, st="#bdb8b2", w=0.12)
        elif k == "ecp":
            g.rect(x0, oy - hh * s, w, hh * s, fill="#cbc7c2", st="#777", sw=0.15)
            for j in range(1, 8):
                g.line(x0, oy - hh * s * j / 8, x0 + w, oy - hh * s * j / 8, st="#b3aea8", w=0.1)
        elif k == "window":
            g.rect(x0, oy - hh * s, w, hh * s, fill="#c9d6df", st="#555", sw=0.3)
            g.rect(x0 + 0.6, oy - hh * s + 0.6, w - 1.2, hh * s - 1.2, fill="none", st="#888", sw=0.15)
            # 600mm後退した木調縦ルーバースクリーン（透過して見える）
            for j in range(12):
                xx = x0 + 1.4 + j * (w - 2.8) / 11
                g.line(xx, oy - 300 * s, xx, oy - 2700 * s, st="#a98458", w=0.9)
            g.rect(x0 + w / 2 - 300 * s, oy - 1750 * s, 600 * s, 220 * s, fill="#f4efe6", st="none")
            logo(g, x0 + w / 2, oy - 1575 * s, 140 * s * 1.25)
        elif k == "entry":
            # 既設アプローチ（風除室）：道路側は既設ガラス扉、奥に当社の木調欄間＋ロゴと店内へのガラス扉
            g.rect(x0, oy - hh * s, w, hh * s, fill="#cdd8df", st="#555", sw=0.3)
            g.rect(x0 + 0.8, oy - (hh - 200) * s, w - 1.6, (hh - 200) * s, fill="#b8946a", st="none")   # 奥の木調壁（透視）
            for j in range(1, 10):
                g.line(x0 + 0.8 + j * (w - 1.6) / 10, oy - (hh - 200) * s, x0 + 0.8 + j * (w - 1.6) / 10, oy - 2500 * s, st="#a07c54", w=0.15)
            g.rect(x0 + w * 0.27, oy - 2400 * s, w * 0.46, 2400 * s, fill="#efe6d6", st="#8b7355", sw=0.2)       # 奥：店内へのガラス扉
            logo(g, x0 + w / 2, oy - 2950 * s, 200 * s * 1.25, color="#f3ead9")
            g.rect(x0 + 0.8, oy - (hh - 200) * s, w - 1.6, 0.8, fill="#fff3d6", st="none")                 # 間接照明
            # 道路側の既設ガラス扉（両開き）
            g.rect(x0 + 0.4, oy - 2600 * s, w - 0.8, 2600 * s, fill="none", st="#555", sw=0.35)
            g.line(x0 + w / 2, oy - 2600 * s, x0 + w / 2, oy, st="#555", w=0.3)
        elif k == "bldg_entry":
            g.rect(x0, oy - hh * s, w, hh * s, fill="#b9c6d0", st="#555", sw=0.3)
            for j in range(1, 4):
                g.line(x0 + w * j / 4, oy - hh * s, x0 + w * j / 4, oy, st="#7d8a95", w=0.3)
            g.rect(x0 + w * 0.25, oy - 2400 * s, w * 0.5, 2400 * s, fill="#a4b3bf", st="#555", sw=0.25)
            g.line(x0 + w * 0.5, oy - 2400 * s, x0 + w * 0.5, oy, st="#555", w=0.2)
            # S1 案内板（ビル標準）
            sx = x0 + 400 * s
            g.rect(sx, oy - 1700 * s, 640 * s, 340 * s, fill="#3a3d42", st="#222", sw=0.15)
            g.rect(sx + 30 * s, oy - (1700 - 105) * s, 580 * s, 205 * s, fill="#f5f3ef")
            logo(g, sx + 320 * s, oy - (1700 - 245) * s, 110 * s * 1.25)
        g.text(x0 + w / 2, oy + 3.6, lab, 1.8, fill="#555")
    g.line(ox - 8, oy, ox + BW * s + 8, oy, st="#333", w=0.45)
    g.text(ox + BW * s + 2, oy + 0.8, "▽GL", 2.0, anchor="start")
    # 寸法（UとH）
    def hd(u0, u1, yy, label):
        a, b = ox + u0 * s, ox + u1 * s
        g.line(a, yy, b, yy, st="#555", w=0.12)
        for p in (a, b):
            g.line(p - 0.6, yy + 0.6, p + 0.6, yy - 0.6, st="#555", w=0.25)
        g.text((a + b) / 2, yy - 0.7, label, 1.8, fill="#444")
    for u0, u1, *_ in F1_PARTS:
        hd(u0, u1, oy + 9, f"{u1-u0:,}")
    hd(0, BW, oy + 14, f"{BW:,}（X1～X3 外壁・CADより）")
    vx = ox - 6
    for a, b, lab in [(0, H1, f"1F階高 {H1:,}"), (H1, top, "")]:
        if not lab:
            continue
        g.line(vx, oy - a * s, vx, oy - b * s, st="#555", w=0.12)
        g.add(f'<text x="{vx-0.8}" y="{oy-(a+b)/2*s}" font-size="1.8" fill="#444" text-anchor="middle" font-family="{FONT}" '
              f'transform="rotate(-90 {vx-0.8} {oy-(a+b)/2*s})">{lab}</text>')
    # 当社区画
    g.rect(ox - 0.5, oy - H1 * s, 6800 * s + 1, H1 * s, fill="none", st=C["red"], sw=0.35, extra='stroke-dasharray="1.5,0.8"')
    g.text(ox + 1, oy - H1 * s - 1.5, "当社区画（1F・正面）", 2.2, anchor="start", fill=C["red"], weight="bold")
    # 引出し注記
    wx = ox + 3300 * s; ex = ox
    callout(g, wx + 9, oy - 1575 * s, ox + 40, oy - top * s - 10,
            "①木調縦ルーバー（不燃・ガラス面より600mm以上後退）＋小型ロゴ　非照明・背面から電球色の間接光のみ")
    callout(g, ex + 7, oy - 2950 * s, ox + 4, oy - top * s - 16,
            "②アプローチ（既設ガラス扉の奥）：木調壁・欄間に店名ロゴ（H≒160・アイボリー）　リースライン内・グレアのない間接照明")
    callout(g, ox + (10300 + 720) * s, oy - 1530 * s, ox + 150, oy - top * s - 4,
            "③S1：ビル共用案内板に店名・ロゴ（ビル標準仕様／乳半アクリル・LED内照）", anchor="start")
    g.text(ox + BW * s / 2, oy + 21, "1階 正面部分立面図（サイン位置・使用素材）", 2.6, weight="bold")
    g.text(ox + BW * s / 2, oy + 24.8, "S=1/70", 1.9, fill=C["sub"])


def sign_details(g, x, y):
    g.text(x, y, "サイン詳細（ビル指定仕様に準拠）", 2.6, anchor="start", weight="bold")
    sc = 0.07
    tx = x + 48
    # S1
    y1 = y + 5
    g.rect(x, y1, 640 * sc, 340 * sc, fill="#3a3d42", st="#222", sw=0.2)
    g.text(x + 30 * sc, y1 + 55 * sc, "日本橋WASAMIビル", 1.4, anchor="start", fill="#ddd")
    g.rect(x + 30 * sc, y1 + 75 * sc, 580 * sc, 235 * sc, fill="#f6f4f0")
    logo(g, x + 320 * sc, y1 + 228 * sc, 10)
    g.text(tx, y1 + 2.5, "S1　W640×H340", 2.1, anchor="start", weight="bold")
    for i, t in enumerate(["ビル共用案内板（エントランス）", "乳半アクリル＋ロゴ出力・LED内照", "表示：ロゴのみ／約0.14㎡"]):
        g.text(tx, y1 + 6.3 + i * 3.1, t, 1.8, anchor="start")
    # S2
    y2 = y1 + 30
    g.rect(x + 12, y2, 300 * sc, 300 * sc, fill="#33363a", st="#222", sw=0.2)
    logo(g, x + 12 + 150 * sc, y2 + 165 * sc, 5.2, color="#f2f2f2")
    g.text(x + 12 + 150 * sc, y2 + 250 * sc, "1F・4F・5F", 1.3, fill="#cfcfcf")
    g.text(tx, y2 + 2.5, "S2　W300×H300", 2.1, anchor="start", weight="bold")
    for i, t in enumerate(["X1通り側・ビル指定位置", "マットアクリル＋ダイノック", "白切文字／約0.09㎡"]):
        g.text(tx, y2 + 6.3 + i * 3.1, t, 1.8, anchor="start")
    # まとめ
    y3 = y2 + 34
    g.text(x, y3, "外装サイン方針", 2.5, anchor="start", weight="bold")
    g.text(x, y3 + 3.6, "（貸主ご意向：落ち着いた外観）", 2.0, anchor="start", fill=C["sub"])
    rules = ["突出・袖看板、壁面大型看板は設けない",
             "ガラス面のフィルム・ポスター広告なし",
             "S1・S2以外の屋外サインなし",
             "点滅・映像・赤色光・ネオン不使用",
             "店名・ロゴのみ（価格・施術内容の広告なし）",
             "電球色2700～3000Kの間接光、調光・タイマー",
             "ガラス面から600mm以上離隔、既設サッシ無加工",
             "表示面積 合計約0.35㎡（上限10㎡）",
             "4・5F窓：防炎ロールスクリーンのみ"]
    for i, t in enumerate(rules):
        g.text(x, y3 + 8.6 + i * 3.6, "・" + t, 2.0, anchor="start")


def make():
    g = SVG()
    title_block(g, "外観立面図・サイン計画図", "1/300・1/70", "A-04",
                ["・1F階高4,950は貸主CAD（展開図 1FL→2FL）より。基準階階高3,900、2F以上の外装は完成予想CGからの模式表現。",
                 "・サイン位置・形状はビル側指定（内装マニュアル7-(6)）に準拠。最終仕様は運営管理者と協議のうえ承認を得る。",
                 "・正面の当社区画は既設アプローチ・SSW-2ガラス面を含む約6.8m（1階 98.36㎡区画）。ガラス面への熱割れ計算が必要なフィルム等は使用しない。"])
    g.text(PAGE_W / 2, 18, "外観立面図・サイン計画図（正面 Y1通り）", 4.2, weight="bold")
    whole_elevation(g, 30, 248, 1 / 300)
    front_detail(g, 92, 205, 1 / 70)
    sign_details(g, 318, 44)
    return g.svg()


if __name__ == "__main__":
    open(os.path.join(sys.argv[1], "elevation_front.svg"), "w").write(make())
