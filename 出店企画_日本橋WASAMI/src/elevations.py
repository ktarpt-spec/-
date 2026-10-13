"""外観立面図・サイン計画図（A3横・SVG）"""
import sys, os
from plans import SVG, C, PAGE_W, PAGE_H, title_block, FONT

LOGO = "#24418f"
H1 = 4950          # 1F階高（CAD展開図 1FL→2FL より）
HT = 3900          # 基準階階高（想定）
FLOORS = 13
BW = 14300         # 正面（Y1面）外壁幅（X3～X1 外々・CADより）

# 正面ファサード 1F 構成（u: 立面左端 = X1側 からの距離）
F1_PARTS = [  # (u0, u1, kind, label)　u = 6,800 − 平面y（1F CAD より）
    (0, 450, "panel", "パネルA"),
    (450, 2150, "porch", "玄関ポーチ（道路側開放）"),
    (2150, 2300, "panel", ""),
    (2300, 6800, "window", "既設ガラス面（A工事）"),
    (6800, 10300, "ecp", "ECP（防災センター）"),
    (10300, BW, "bldg_entry", "ビルエントランス"),
]
GLASS_MULLION = 4700   # ガラス面の中間方立（u）


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
        fill = {"porch": "#5d554e", "window": "#cfdae3", "bldg_entry": "#b7c4cf"}.get(k, "#d6d3cf")
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
            # 既設ガラス面（A工事・無加工）＋600mm後退の木調縦ルーバー（全幅）
            g.rect(x0, oy - hh * s, w, hh * s, fill="#c9d6df", st="#555", sw=0.3)
            g.rect(x0, oy - hh * s, w, hh * s * 0.12, fill="#b7c6d1", st="none")
            n = int((u1 - u0 - 300) / 140)
            for j in range(n + 1):
                xx = x0 + (150 + j * (u1 - u0 - 300) / n) * s
                g.line(xx, oy - 150 * s, xx, oy - 2950 * s, st="#a98458", w=0.75)
            g.rect(x0 + 0.2, oy - 3000 * s, w - 0.4, 0.5, fill="#fff1d2", st="none")      # 上部の間接光
            mx = ox + GLASS_MULLION * s
            g.line(mx, oy - hh * s, mx, oy, st="#555", w=0.45)
            g.rect(x0 + 0.6, oy - hh * s + 0.6, w - 1.2, hh * s - 1.2, fill="none", st="#777", sw=0.15)
            lx = ox + 3500 * s
            g.rect(lx - 300 * s, oy - 1750 * s, 600 * s, 220 * s, fill="#f4efe6", st="none")
            logo(g, lx, oy - 1575 * s, 140 * s * 1.25)
        elif k == "porch":
            # 玄関ポーチ（既設・道路側開放）：奥に既設SUS両開き扉、その奥に受付の木調ロゴ壁
            PCH = 3625
            g.rect(x0, oy - hh * s, w, (hh - PCH) * s, fill="#d6d3cf", st="#777", sw=0.15)      # 開口上部
            g.rect(x0, oy - PCH * s, w, PCH * s, fill="#6d665f", st="#555", sw=0.3)            # ポーチ内（陰）
            g.rect(x0 + 0.5, oy - PCH * s, w - 1.0, 0.6, fill="#f3dfb8", st="none")             # 軒天の照明
            dx0, dx1 = x0 + 90 * s, x0 + w - 90 * s
            g.rect(dx0, oy - 2400 * s, dx1 - dx0, 2400 * s, fill="#b48c5e", st="#8f969c", sw=0.45)   # 扉越しの木調ロゴ壁
            logo(g, (dx0 + dx1) / 2, oy - 1650 * s, 150 * s * 1.25, color="#f3ead9")
            g.line((dx0 + dx1) / 2 + 25 * s, oy - 2400 * s, (dx0 + dx1) / 2 + 25 * s, oy, st="#8f969c", w=0.4)
            for xx in (dx0 + 0.25, dx1 - 0.25):
                g.line(xx, oy - 2400 * s, xx, oy, st="#8f969c", w=0.5)
            g.rect(dx0, oy - (PCH - 40) * s, dx1 - dx0, (PCH - 2440) * s, fill="#837b73", st="#8f969c", sw=0.2)
            for xx in ((dx0 + dx1) / 2 - 120 * s, (dx0 + dx1) / 2 + 170 * s):
                g.line(xx, oy - 1300 * s, xx, oy - 800 * s, st="#c9cdd1", w=0.35)
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
        if lab:
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
        hd(u0, u1, oy + 9, f"{u1-u0:,}" if u1 - u0 > 300 else "")
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
    callout(g, ox + 3500 * s + 9, oy - 1575 * s, ox + 40, oy - top * s - 10,
            "①既設ガラス面（約4.5m・無加工）の室内側：木調縦ルーバー（不燃・ガラス面より600mm後退）＋小型ロゴ　背面から電球色の間接光のみ")
    callout(g, ox + 1300 * s, oy - 1650 * s, ox + 4, oy - top * s - 16,
            "②玄関ポーチ（既設・道路側開放・造作なし）：奥の既設SUS両開き扉越しに受付の木調ロゴ壁が見える")
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
             "玄関ポーチは既設のまま（造作・看板なし）",
             "表示面積 合計約0.35㎡（上限10㎡）",
             "4・5F窓：防炎ロールスクリーンのみ"]
    for i, t in enumerate(rules):
        g.text(x, y3 + 8.6 + i * 3.6, "・" + t, 2.0, anchor="start")


def make():
    g = SVG()
    title_block(g, "外観立面図・サイン計画図", "1/300・1/70", "A-04",
                ["・1F階高4,950は貸主CAD（展開図 1FL→2FL）より。基準階階高3,900、2F以上の外装は完成予想CGからの模式表現。",
                 "・サイン位置・形状はビル側指定（内装マニュアル7-(6)）に準拠。最終仕様は運営管理者と協議のうえ承認を得る。",
                 "・正面の当社区画は玄関ポーチ（道路側開放）と既設ガラス面 約4.5mを含む約6.8m（1階 98.36㎡区画・CADより）。ガラス面・サッシは無加工、フィルム等は貼らない。"])
    g.text(PAGE_W / 2, 18, "外観立面図・サイン計画図（正面 Y1通り）", 4.2, weight="bold")
    whole_elevation(g, 30, 248, 1 / 300)
    front_detail(g, 92, 205, 1 / 70)
    sign_details(g, 318, 44)
    return g.svg()


if __name__ == "__main__":
    open(os.path.join(sys.argv[1], "elevation_front.svg"), "w").write(make())


# ====================================================================== A-05 1F玄関ポーチ・道路側ガラス面 詳細
def make_entry_detail():
    from geometry import F1, PORCH_X, PORCH_Y0
    g = SVG()
    title_block(g, "1F 玄関ポーチ・道路側ガラス面 詳細図", "1/40・1/50", "A-05",
                ["・玄関ポーチは区画内（道路側開放・扉なし）。床・壁・軒天・奥の両開き扉（SUS製）は既設（A工事）のまま使用し、ポーチ内に造作・看板は設けない。",
                 "・道路側ガラス面（約4.5m）・サッシは既設（A工事）で変更不可。室内側にガラス面から600mm後退した木調縦ルーバー（不燃・C工事）を設け、外からの視線をやわらげる。",
                 "・受付カウンターは扉の内側1,220mmを空けて配置（扉は店内側へ開く）。ロゴは受付背面の木調壁に表示し、扉越しに見える控えめな表示とする。",
                 "・寸法は1F CAD（貸主）からの読取り値。ポーチ床の段差・勾配（FL-70～±0・スロープ1/26）、軒天高さ（FL+3,625）は既設図による。実施設計時に確定。"])
    g.text(PAGE_W / 2, 18, "1F 玄関ポーチ・道路側ガラス面 詳細図", 4.2, weight="bold")
    D = F1["D"]
    rc = F1["reception"]; pd = F1["porch_door"]; lv = F1["louver"]
    WOOD, WOODD, GL, WALL = "#b8946a", "#7d6347", "#6d8fa8", "#8c8580"

    def hdim(P, x0, x1, y, lab, off=0.8):
        a, b = P(x0, y); c, d = P(x1, y)
        g.line(a, b, c, d, st="#555", w=0.12)
        for q in (a, c):
            g.line(q - 0.6, b + 0.6, q + 0.6, b - 0.6, st="#555", w=0.25)
        g.text((a + c) / 2, b - off, lab, 1.8, fill="#444")

    def vdim(P, y0, y1, x, lab):
        a, b = P(x, y0); c, d = P(x, y1)
        g.line(a, b, c, d, st="#555", w=0.12)
        for q in (b, d):
            g.line(a - 0.6, q + 0.6, a + 0.6, q - 0.6, st="#555", w=0.25)
        g.add(f'<text x="{a-1:.2f}" y="{(b+d)/2:.2f}" font-size="1.8" fill="#444" text-anchor="middle" font-family="{FONT}" transform="rotate(-90 {a-1:.2f} {(b+d)/2:.2f})">{lab}</text>')

    # ---------------- 平面詳細 S=1/40（左：道路）
    s = 1 / 40
    ox, oy = 52, 214
    P = lambda x, y: (ox + x * s, oy - y * s)
    g.text(ox + 50, 27, "平面詳細　S=1/40", 2.8, weight="bold")
    def rectm(x0, y0, x1, y1, **kw):
        a, b = P(x0, y1); g.rect(a, b, (x1 - x0) * s, (y1 - y0) * s, **kw)
    rectm(0, 0, 4300, D, fill="#f6f1e8")                         # 店内
    rectm(0, PORCH_Y0, PORCH_X, D, fill="#e4e1dc")                # ポーチ（既設床）
    rectm(-250, D, 4300, D + 250, fill=WALL)                      # X1側外壁
    rectm(-400, D - 200, 0, D + 250, fill=WALL)                   # 隅切り部
    rectm(0, PORCH_Y0, PORCH_X, PORCH_Y0 + 150, fill=WALL)        # ポーチ／ガラス面間の既設壁
    rectm(-120, PORCH_Y0 - 60, 0, PORCH_Y0 + 150, fill=WALL)
    rectm(PORCH_X, pd["y1"], PORCH_X + 100, D, fill=WALL)         # 扉両脇
    rectm(PORCH_X, PORCH_Y0, PORCH_X + 100, pd["y0"], fill=WALL)
    # 既設ガラス面
    a1, b1 = P(-60, 0); a2, b2 = P(-60, PORCH_Y0 - 60)
    g.line(a1, b1, a2, b2, st="white", w=1.6)
    for d_ in (-0.35, 0.35):
        g.line(a1 + d_, b1, a2 + d_, b2, st=GL, w=0.25)
    for yy in (0, 2075, PORCH_Y0 - 60):
        rectm(-110, yy - 40, -10, yy + 40, fill="#666")
    # 木調縦ルーバー
    n = int((lv["y1"] - lv["y0"]) // lv["pitch"])
    for k in range(n + 1):
        yy = lv["y0"] + k * (lv["y1"] - lv["y0"]) / n
        rectm(lv["x"] - 25, yy - 18, lv["x"] + 25, yy + 18, fill=WOOD, st=WOODD, sw=0.08)
    # 両開き扉（店内側へ）
    x = PORCH_X + 50
    for hy, L_, sg in ((pd["y1"], pd["leaves"][0], -1), (pd["y0"], pd["leaves"][1], 1)):
        h_ = P(x, hy); e_ = P(x, hy + sg * L_); o_ = P(x + L_, hy)
        g.line(*h_, *e_, st="#8f969c", w=0.7)
        g.line(*h_, *o_, st="#555", w=0.3)
        g.path(f"M{o_[0]:.2f},{o_[1]:.2f} A{L_*s:.2f},{L_*s:.2f} 0 0 {1 if sg < 0 else 0} {e_[0]:.2f},{e_[1]:.2f}", st="#777", sw=0.15)
    # 受付
    import math
    cx, cy = P(rc["cx"], rc["cy"]); R1, R2 = rc["r"] * s, (rc["r"] - rc["depth"]) * s
    def pt(R, a): return cx + R * math.cos(math.radians(a)), cy - R * math.sin(math.radians(a))
    p0, p1_, q0, q1 = pt(R1, rc["a0"]), pt(R1, rc["a1"]), pt(R2, rc["a1"]), pt(R2, rc["a0"])
    g.path(f"M{p0[0]:.2f},{p0[1]:.2f} A{R1},{R1} 0 0 0 {p1_[0]:.2f},{p1_[1]:.2f} L{q0[0]:.2f},{q0[1]:.2f} A{R2},{R2} 0 0 1 {q1[0]:.2f},{q1[1]:.2f} Z",
           fill=WOOD, st=WOODD, sw=0.2)
    bx0, by0, bx1, by1 = rc["back"]
    rectm(bx0, by0, bx1, by1, fill="#d9c3a3", st=WOODD, sw=0.2)
    g.text(*P(rc["cx"] - 420, rc["cy"] + 60), "受付", 2.4, weight="bold")
    # 待合椅子
    for (cx_, cy_, _) in F1["chairs"]:
        if cy_ < 2500:
            rectm(cx_ - 300, cy_ - 300, cx_ + 300, cy_ + 300, fill="#ece3d6", st="#9b8b78", sw=0.12)
    # 室名・動線
    g.text(*P(PORCH_X / 2, D - 900), "玄関ポーチ", 2.4, weight="bold")
    g.text(*P(PORCH_X / 2, D - 1250), "（既設・造作なし）", 1.9, fill=C["sub"])
    g.text(*P(2400, 3000), "待合", 2.6, weight="bold")
    g.text(*P(-1300, 5900), "道路（歩道）", 2.2, fill=C["red"], weight="bold")
    g.line(*P(-1400, 5475), *P(rc["cx"] - rc["r"] - 150, 5475), st=C["red"], w=0.45, extra='marker-end="url(#arr)"')
    g.text(*P(-750, 4900), "開放", 2.0, fill=C["red"])
    # 注記
    def note(xm, ym, tx, ty, t):
        callout(g, *P(xm, ym), tx, ty, t, size=1.85)
    note(PORCH_X + 50, 5900, 120, 56, "①既設SUS製両開き扉（A工事・店内側へ開く）")
    note(lv["x"], 450, ox + 20, 223, "②木調縦ルーバー（不燃・@140・ガラス面より600後退）")
    note(-60, 250, ox + 20, 229, "③既設ガラス面 約4.5m（A工事・変更不可）")
    note(bx0 + 140, 6000, 120, 62, "④受付背面：木調ロゴ壁（扉越しに見える）")
    # 寸法
    hdim(P, 0, PORCH_X, D + 700, f"{PORCH_X:,}")
    hdim(P, PORCH_X, rc["cx"] - rc["r"], rc["cy"] - 650, f"{rc['cx'] - rc['r'] - PORCH_X:,}")
    hdim(P, -60, lv["x"], 300, "600")
    vdim(P, PORCH_Y0, D, -1700, f"{D - PORCH_Y0:,}")
    vdim(P, 0, PORCH_Y0, -1700, f"{PORCH_Y0:,}")
    for yy in (PORCH_Y0 - 1400, 5475 + 900):
        a, b = P(-900, yy); c, d = P(4100, yy)
    a, b = P(-900, 5300); c, d = P(4200, 5300)
    g.line(a, b, c, d, st="#333", w=0.2, dash="3,1,0.6,1")
    g.text(a - 2, b + 0.8, "A", 2.4, weight="bold"); g.text(c + 2, d + 0.8, "A", 2.4, weight="bold")
    a, b = P(-900, 1600); c, d = P(1500, 1600)
    g.line(a, b, c, d, st="#333", w=0.2, dash="3,1,0.6,1")
    g.text(a - 2, b + 0.8, "B", 2.4, weight="bold"); g.text(c + 2, d + 0.8, "B", 2.4, weight="bold")

    # ---------------- 断面 A-A（ポーチ・扉・受付） S=1/50
    s2 = 1 / 50
    H1c, PCH, CHI = 4950, 3625, 3000
    sx, sy = 213, 150
    Q = lambda x, z: (sx + x * s2, sy - z * s2)
    g.text(sx + 30, 27, "断面 A-A（玄関ポーチ）S=1/50", 2.8, weight="bold")
    g.line(*Q(-1100, 0), *Q(4400, 0), st="#333", w=0.45)
    a, b = Q(-300, H1c + 250); g.rect(a, b, 4700 * s2, 250 * s2, fill=WALL)              # 2Fスラブ
    a, b = Q(-300, H1c); g.rect(a, b, 300 * s2, (H1c - PCH) * s2, fill=WALL)            # 外壁（梁型）
    a, b = Q(0, PCH + 80); g.rect(a, b, PORCH_X * s2, 80 * s2, fill="#d9d6d2")         # ポーチ軒天（既設）
    a, b = Q(PORCH_X, H1c); g.rect(a, b, 100 * s2, (H1c - 2400) * s2, fill=WALL)        # 扉上部の壁
    a, b = Q(PORCH_X + 20, 2400); g.rect(a, b, 60 * s2, 2400 * s2, fill="#c9d6df", st="#8f969c", sw=0.3)   # SUS扉
    a, b = Q(PORCH_X + 100, CHI + 60); g.rect(a, b, 2600 * s2, 60 * s2, fill="#eeeae4", st="#999", sw=0.1)  # 店内天井
    a, b = Q(bx0, 2450); g.rect(a, b, (bx1 - bx0) * s2, 2450 * s2, fill="#d9c3a3", st=WOODD, sw=0.2)       # ロゴ壁
    a, b = Q(rc["cx"] - rc["r"], 1000); g.rect(a, b, rc["depth"] * s2, 1000 * s2, fill=WOOD, st=WOODD, sw=0.2)
    g.text(*Q(PORCH_X / 2, 1800), "玄関ポーチ", 1.9, fill=C["sub"])
    g.text(*Q(rc["cx"] - 500, 1500), "受付", 1.9, fill=C["sub"])
    g.text(*Q(-850, 1200), "道路", 2.0, fill=C["red"], weight="bold")
    vdim(Q, 0, PCH, -700, "軒天 FL+3,625")
    vdim(Q, 0, 2400, PORCH_X - 250, "扉 H2,400")
    vdim(Q, 0, H1c, 4300, "1F階高 4,950")
    hdim(Q, 0, PORCH_X, -450, f"{PORCH_X:,}")
    callout(g, *Q(PORCH_X + 50, 1200), sx + 40, 162, "既設SUS両開き扉", size=1.8)
    callout(g, *Q(PORCH_X / 2, PCH + 40), sx + 40, 168, "既設軒天・照明（A工事）", size=1.8)

    # ---------------- 断面 B-B（ガラス面・ルーバー） S=1/50
    tx, ty = 345, 150
    Q2 = lambda x, z: (tx + x * s2, ty - z * s2)
    g.text(tx + 20, 27, "断面 B-B（道路側ガラス面）S=1/50", 2.8, weight="bold")
    g.line(*Q2(-1100, 0), *Q2(3000, 0), st="#333", w=0.45)
    a, b = Q2(-300, H1c + 250); g.rect(a, b, 3300 * s2, 250 * s2, fill=WALL)
    a, b = Q2(-300, H1c); g.rect(a, b, 300 * s2, (H1c - 4050) * s2, fill=WALL)
    a, b = Q2(-120, 4050); g.rect(a, b, 80 * s2, 4050 * s2, fill="#c9d6df", st=GL, sw=0.3)          # ガラス
    a, b = Q2(lv["x"] - 25, CHI - 50); g.rect(a, b, 50 * s2, (CHI - 200) * s2, fill=WOOD, st=WOODD, sw=0.2)   # ルーバー
    a, b = Q2(0, CHI + 60); g.rect(a, b, 2800 * s2, 60 * s2, fill="#eeeae4", st="#999", sw=0.1)
    a, b = Q2(lv["x"] - 200, CHI); g.rect(a, b, 400 * s2, 50 * s2, fill="#fff3d6", st="#d9b97a", sw=0.15)
    for k in range(4):
        g.line(*Q2(lv["x"], CHI - 50), *Q2(lv["x"] + 150, 2700 - k * 500), st="#e8c98a", w=0.12, dash="0.6,0.6")
    a, b = Q2(1500, 450); g.rect(a, b, 600 * s2, 450 * s2, fill="#ece3d6", st="#9b8b78", sw=0.15)
    g.text(*Q2(1800, 700), "待合", 1.9, fill=C["sub"])
    g.text(*Q2(-850, 1200), "道路", 2.0, fill=C["red"], weight="bold")
    hdim(Q2, -80, lv["x"], -450, "600")
    vdim(Q2, 0, 4050, -700, "既設ガラス H≒4,050")
    vdim(Q2, 0, CHI, 2600, f"天井 CH{CHI:,}")
    callout(g, *Q2(lv["x"], 1700), tx - 5, 162, "木調縦ルーバー（不燃・C工事）", size=1.8)
    callout(g, *Q2(lv["x"], CHI + 20), tx - 5, 168, "間接照明（電球色2,700K・調光）", size=1.8)
    callout(g, *Q2(-80, 3300), tx - 5, 174, "既設ガラス・サッシ（無加工）", size=1.8)

    # ---------------- 正面（道路から）S=1/80
    s3 = 1 / 80
    fx, fy = 230, 248
    R_ = lambda u, z: (fx + u * s3, fy - z * s3)
    g.text(fx, fy - H1c * s3 - 6, "正面（道路から見た当社区画）S=1/80", 2.6, anchor="start", weight="bold")
    a, b = R_(0, H1c); g.rect(a, b, 6800 * s3, 900 * s3, fill="#cfcac4", st="#777", sw=0.15)
    for u0, u1, k, lab in F1_PARTS[:4]:
        x0, w = fx + u0 * s3, (u1 - u0) * s3
        if k == "panel":
            a, b = R_(u0, 4050); g.rect(a, b, w, 4050 * s3, fill="#d9d6d2", st="#777", sw=0.15)
        elif k == "porch":
            a, b = R_(u0, 4050); g.rect(a, b, w, (4050 - PCH) * s3, fill="#d6d3cf", st="#777", sw=0.15)
            a, b = R_(u0, PCH); g.rect(a, b, w, PCH * s3, fill="#6d665f", st="#555", sw=0.25)
            a, b = R_(u0 + 90, 2400); g.rect(a, b, w - 180 * s3, 2400 * s3, fill="#b48c5e", st="#8f969c", sw=0.3)
            logo(g, x0 + w / 2, fy - 1650 * s3, 150 * s3 * 1.25, color="#f3ead9")
            g.line(x0 + w / 2, fy - 2400 * s3, x0 + w / 2, fy, st="#8f969c", w=0.3)
        elif k == "window":
            a, b = R_(u0, 4050); g.rect(a, b, w, 4050 * s3, fill="#c9d6df", st="#555", sw=0.25)
            n = int((u1 - u0 - 300) / 140)
            for j in range(n + 1):
                xx = x0 + (150 + j * (u1 - u0 - 300) / n) * s3
                g.line(xx, fy - 150 * s3, xx, fy - 2950 * s3, st="#a98458", w=0.45)
            mx = fx + GLASS_MULLION * s3
            g.line(mx, fy - 4050 * s3, mx, fy, st="#555", w=0.3)
            lx = fx + 3500 * s3
            g.rect(lx - 300 * s3, fy - 1750 * s3, 600 * s3, 220 * s3, fill="#f4efe6")
            logo(g, lx, fy - 1575 * s3, 140 * s3 * 1.25)
        if lab:
            g.text(x0 + w / 2, fy + 3.2, lab, 1.6, fill="#555")
    g.line(fx - 4, fy, fx + 6800 * s3 + 4, fy, st="#333", w=0.4)
    g.text(fx + 6800 * s3 + 6, fy - 40, "ポーチ奥：既設SUS扉越しに受付の木調ロゴ壁", 1.8, anchor="start", fill="#444")
    g.text(fx + 6800 * s3 + 6, fy - 36.5, "ガラス面：600mm奥の木調縦ルーバー＋小型ロゴ", 1.8, anchor="start", fill="#444")
    g.text(fx + 6800 * s3 + 6, fy - 33, "看板・ガラス面への貼物なし", 1.8, anchor="start", fill="#444")
    g.text(fx + 6800 * s3 + 6, fy - 29.5, "→ 立面図 A-04・外装イメージ P.8 と同一", 1.8, anchor="start", fill=C["red"])
    return g.svg()


if __name__ == "__main__" and len(sys.argv) > 1:
    open(os.path.join(sys.argv[1], "entry_detail.svg"), "w").write(make_entry_detail())
