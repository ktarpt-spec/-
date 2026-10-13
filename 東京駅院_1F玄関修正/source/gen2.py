# 既存図面セットのトーンに合わせた 1階部分の差し替え版
import math
from gen import S, door, wall, person, RED, NAVY, INK, SUB, W, D, PORCH, DOOR_X, LS

# 既存図面の色
TEN = "#F3E9DC"; ROOM = "#F7F2E8"; MRIC = "#DCE4EC"; MECH = "#E4E4E4"; APP = "#E9E9E9"
COL = "#8F8984"; WOODC = "#B8926A"; GLS = "#BFD0DC"; GLSL = "#6F8FAA"; PANEL = "#D9D6D1"; PANEL2 = "#CFCBC4"
BAND = "#CBC6BE"; GOLD = "#9B7B55"
MONO = "'Noto Sans Mono CJK JP',monospace"


def tb(title, scale, no, sub="基本計画（出店企画書添付資料）　2026.10　改訂（1階 玄関）"):
    return f'''<div class="tb"><div class="tb1">整形外科ふっか／整痛院ふっか 東京駅院 出店計画 ／ 日本橋WASAMIビル</div>
<div class="tb2"><div><b>{title}</b><span>{sub}</span></div><div class="sc"><b>{scale}</b><span>No.{no}　A3</span></div></div></div>'''


def sheet(inner, title, scale, no):
    return f'<section class="sheet">{inner}{tb(title, scale, no)}</section>'


# ================================================================= A-01
def a01_svg():
    s = S(100)
    s.add(f'<image href="landlord.svg" x="{LS["x"]}" y="{LS["y"]}" width="{LS["w"]}" height="{LS["h"]}" opacity="0.55" preserveAspectRatio="none"/>')
    zones = [(0, 0, 4200, D, TEN), (4200, 0, 2500, 2550, ROOM), (6700, 0, 2100, 2550, MECH), (4200, 2550, 4600, 1200, "#EFE4D4"),
             (4200, 3750, 2100, D - 3750, ROOM), (6300, 3750, 1100, D - 3750, ROOM), (7400, 3750, 1400, D - 3750, ROOM), (8800, 0, 5100, D, MRIC)]
    for x, y, w, h, c in zones:
        s.rect(x, y, w, h, c, "none", 0, 'opacity="0.92"')
    x0, y0, x1, y1 = PORCH
    s.rect(x0, y0, x1 - x0, y1 - y0, APP, "none", 0)
    s.rect(0, 0, W, D, "none", "#C0392B", 0.6)
    s.path("M560,40 L1640,40 L1640,545 L560,545 Z", "#E6D3B8", WOODC, 0.2)
    for a in [(4200, 0, 4200, 2550), (6700, 0, 6700, 2550), (4200, 3750, 4200, D), (6300, 3750, 6300, D), (7400, 3750, 7400, D),
              (4200, 2550, 5150, 2550), (6050, 2550, 7250, 2550), (8150, 2550, 8800, 2550), (4200, 3750, 4550, 3750),
              (5450, 3750, 6450, 3750), (7250, 3750, 7550, 3750), (8350, 3750, 8800, 3750)]:
        wall(s, *a, t=110, fill="#2b2b2b")
    for a in [(8800, 0, 8800, 2650), (8800, 3650, 8800, D)]:
        wall(s, *a, t=170, fill="#2F5B8C")
    door(s, 5150, 2550, 900, 0, -90); door(s, 7250, 2550, 900, 0, -90); door(s, 4550, 3750, 900, 0, 90)
    door(s, 6450, 3750, 800, 0, 90); door(s, 7550, 3750, 800, 0, 90); door(s, 8800, 2650, 1000, 90, 180, 0.3, "#2F5B8C")
    door(s, DOOR_X, 595, 1000, 90, 0, 0.6, INK); door(s, DOOR_X, 2300, 640, -90, 0, 0.6, INK)
    # 受付（正面の木調壁＋カウンター）
    s.rect(4060, 0, 140, 2550, WOODC, "none", 0)
    s.rect(2900, 900, 1250, 600, WOODC, "#7a5a3a", 0.25, 'rx="80"')
    s.circle(3300, 650, 160, "#fff", SUB); s.circle(3750, 650, 160, "#fff", SUB)
    for (cx, cy) in [(900, 3300), (1450, 3300), (2000, 3300), (900, 4250), (1450, 4250), (2000, 4250), (900, 5200), (1450, 5200)]:
        s.rect(cx - 230, cy - 230, 460, 460, "#EFE2CF", "#b39a7a", 0.18, 'rx="60"')
    s.circle(3300, 3300, 260, "#cfe3c8", "#8aa982", 0.2); s.circle(3600, 5900, 220, "#cfe3c8", "#8aa982", 0.2)
    s.rect(600, 2450, 70, 3900, WOODC, "none", 0)
    # MRI
    s.rect(10350, 900, 1700, 1900, "#c7d3e0", "#2F5B8C", 0.3, 'rx="150"'); s.circle(11200, 1850, 380, "#fff", "#2F5B8C", 0.3)
    s.rect(10950, 2800, 500, 2700, "#fff", "#2F5B8C", 0.25); s.circle(11200, 2100, 2450, "none", "#2F5B8C", 0.15, "80 60")
    s.arrow([(-2900, 1450), (2700, 1450)], "#C0392B", 0.6)
    s.arrow([(2990, D + 2100), (2990, 5300)], "#555", 0.4)
    T = s.text
    T(-2900, 1250, "患者動線（道路より直接）", 6, "#C0392B", weight=700)
    T(840, 1380, "玄関ポーチ", 6.2, INK, "middle", 700)
    T(840, 1640, "（既設・屋外／区画内）", 4.8, SUB, "middle")
    T(DOOR_X + 100, 2520, "既設SUS両開き扉", 4.8, INK)
    T(3525, 1270, "受付", 6.5, "#fff", "middle", 700)
    T(1450, 2850, "待合", 6.5, INK, "middle", 700)
    T(3700, 2220, "木調壁＋ロゴ", 4.4, "#7a5a3a", "end")
    T(3000, D + 2350, "館内側出入口（既設）", 5, "#555", "middle")
    for (x, y, a, b) in [(5450, 900, "診察室", "6.4㎡"), (7750, 900, "MRI機械室", "5.4㎡"), (6500, 3250, "廊下", ""),
                         (5250, 5000, "処置室", "5.9㎡"), (6850, 4900, "MRI更衣", "（1名）"), (8100, 5000, "MRI操作室", "3.9㎡")]:
        T(x, y, a, 6, INK, "middle", 700)
        if b: T(x, y + 330, b, 4.8, SUB, "middle")
    T(11350, 6000, "MRI検査室（電磁シールド）", 6, INK, "middle", 700); T(11350, 6330, "31.5㎡", 4.8, SUB, "middle")
    T(11200, 650, "1.5T MRI（富士フイルム）", 4.4, "#2F5B8C", "middle")
    # 寸法
    s.dim(0, 0, 1680, 0, "1,680", -1300); s.dim(1680, 0, 4200, 0, "2,520", -1300); s.dim(4200, 0, 6300, 0, "2,100", -1300)
    s.dim(6300, 0, 7400, 0, "1,100", -1300); s.dim(7400, 0, 8800, 0, "1,400", -1300); s.dim(8800, 0, W, 0, "5,100", -1300)
    s.dim(0, 0, W, 0, "13,900", -2200)
    s.dim(0, 0, 0, D, "6,550", -1300, vertical=True)
    return s.svg((-3300, -3600, 27000, 20000), 270, 200)


def build_a01():
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in
                   [("玄関ポーチ（屋外）", "2.9㎡"), ("診察室", "6.4㎡"), ("MRI機械室", "5.4㎡"), ("処置室", "5.9㎡"),
                    ("MRI更衣（1名）", "3.1㎡"), ("MRI操作室", "3.9㎡"), ("MRI検査室（電磁シールド）", "31.5㎡")])
    lg = "".join(f'<div class="lg"><i style="background:{c}"></i>{t}</div>' for c, t in
                 [(TEN, "貸室 98.36㎡（約29.75坪）"), (ROOM, "診察・処置・操作・更衣"), (MRIC, "MRI室（シールド工事）"), (MECH, "機械室"), (APP, "玄関ポーチ（既設・区画内）")])
    inner = f'''<h1>1階 平面計画図（玄関ポーチ・受付待合・診察室・処置室・MRI室）</h1>
<p class="sub">貸室面積 98.36㎡（約29.75坪）</p>
<p class="road">← 正面道路（Y1通り・歩道）</p>
<div class="fig" style="left:12mm;top:30mm">{a01_svg()}</div>
<div class="orient">図の向き<br><span>左：正面道路（Y1側）<br>上：X1通り側　※真北は要確認</span></div>
<div class="legend v" style="left:298mm;top:66mm">{lg}</div>
<table class="area" style="left:298mm;top:108mm;width:82mm"><tr><th colspan="2">諸室面積表（内法・概算）</th></tr>{rows}</table>
<div class="notes" style="left:12mm;top:240mm;width:200mm">
<p>・下図（グレー）は貸主提供の募集図面（1階 店舗区画）。赤線＝貸室区画（98.36㎡）、着色部・室配置が当社計画（C工事）。</p>
<p>・入口は既設の玄関ポーチ（道路側は開放）と既設SUS製両開き扉（A工事・無加工）の1か所。風除室は設けない。</p>
<p>・扉は店内側に開くため、扉の内側1,220mmは何も置かない。正面の木調壁にロゴ、受付は扉から見える位置に置く。</p>
<p>・MRI：富士フイルム製1.5T（ゼロヘリウム型想定）。床荷重5,000N/㎡の1Fに配置。搬入経路・振動・電源容量はビル側と協議。</p>
<p>・道路側ガラス面から600mm以内には造作・サインを設けない（内装マニュアル）。トイレは館内共用トイレを利用。</p></div>'''
    return sheet(inner, "1階 平面計画図（受付待合・診察室・処置室・MRI室）", "S=1/100", "A-01")


# ================================================================= A-04
SEG = [("当社専用アプローチ（既設ポーチ）", 0, 2300), ("パネルA", 2300, 3300), ("SSW-2（既設ガラス）", 3300, 5000),
       ("パネルA", 5000, 6800), ("ECP（防災センター）", 6800, 10300), ("ビルエントランス", 10300, 14300)]
OPEN, F1 = 4050, 4950


def facade_1f(s, labels=True):
    s.rect(-200, -F1 - 1700, 14700, 1700, "#E9EEF2", "#999", 0.2)
    for k in range(16):
        s.rect(400 + k * 850, -F1 - 1550, 780, 1400, "#D3DEE7", "#9fb0bf", 0.15)
    s.rect(0, -F1, 14300, F1 - OPEN, BAND, "#999", 0.2)
    # アプローチ（開放のくぼみ）
    s.rect(0, -OPEN, 2300, OPEN, "#E2DED8", INK, 0.3)
    s.path(f"M0,{-OPEN} L600,{-OPEN+380} L600,0 L0,0 Z", "#CFCAC2", "#888", 0.15)        # 斜め壁
    s.path(f"M2300,{-OPEN} L2120,{-OPEN+380} L2120,0 L2300,0 Z", "#D5D1CA", "#888", 0.15)  # 右脇壁
    s.rect(600, -OPEN + 380, 1520, OPEN - 380, "#EDEAE5", "#888", 0.15)                   # 奥
    s.rect(650, -2400, 1420, 2400, GLS, "#7d8790", 0.35)                                    # 既設SUS扉
    s.line(1360, -2400, 1360, 0, "#7d8790", 0.3)
    s.rect(820, -2150, 400, 900, WOODC, "none", 0, 'opacity="0.55"')                         # 扉越しの木調壁
    s.text(1020, -1800, "fukka", 6, "#fff", "middle", 700)
    s.rect(2150, -2250, 110, 380, "#2f3134", "none", 0)                                      # S2 脇壁サイン
    # パネルA
    for x0, x1 in ((2300, 3300), (5000, 6800)):
        s.rect(x0, -OPEN, x1 - x0, OPEN, PANEL, "#999", 0.2)
        for r in range(1, 4):
            s.line(x0, -OPEN * r / 4, x1, -OPEN * r / 4, "#aaa", 0.12)
    # SSW-2
    s.rect(3300, -OPEN, 1700, OPEN, GLS, "#7d8790", 0.3)
    for k in range(10):
        s.rect(3420 + k * 150, -2700, 60, 2650, WOODC, "none", 0)
    s.rect(3920, -1700, 500, 170, "#fff", "none", 0); s.text(4170, -1580, "fukka", 4.2, NAVY, "middle", 700)
    # ECP
    s.rect(6800, -OPEN, 3500, OPEN, PANEL2, "#999", 0.2)
    for r in range(1, 8):
        s.line(6800, -OPEN * r / 8, 10300, -OPEN * r / 8, "#aaa", 0.12)
    # エントランス
    s.rect(10300, -OPEN, 4000, OPEN, "#B9CAD6", "#7d8790", 0.3)
    for k in range(1, 4):
        s.line(10300 + k * 1000, -OPEN, 10300 + k * 1000, 0, "#7d8790", 0.3)
    s.rect(11300, -2500, 2000, 2500, "#A8BCCB", "#7d8790", 0.3); s.line(12300, -2500, 12300, 0, "#7d8790", 0.3)
    s.rect(10700, -1550, 400, 220, "#2b2b2b", "none", 0); s.rect(10720, -1530, 360, 180, "#f6f2ea", "none", 0)
    s.text(10900, -1405, "fukka", 3.6, NAVY, "middle", 700)
    s.line(-600, 0, 14900, 0, INK, 0.5)
    s.rect(-60, -F1, 6920, F1, "none", "#C0392B", 0.45, 'stroke-dasharray="120 70"')
    if labels:
        s.text(-40, -F1 - 120, "当社区画（1F・正面）", 5, "#C0392B", weight=700)
        x = 0
        for name, a, b in SEG:
            s.text((a + b) / 2, 520, name, 4.4, SUB, "middle")
            s.dim(a, 0, b, 0, f"{b - a:,}", 1100, 4.4)
        s.dim(0, 0, 14300, 0, "14,300（X1〜X3 外壁・CADより）", 1800, 4.4)
        s.dim(-500, -F1, -500, 0, "1F階高 4,950", 0, 4.4, vertical=True)
        s.text(14500, -F1 + 60, "▽2FL", 4.6, SUB); s.text(14500, 60, "▽GL", 4.6, SUB)


def a04_center():
    s = S(70)
    facade_1f(s)
    leaders = [(1400, -1100, -7400, "②S2：ポーチ脇壁（ビル指定サインスペース）に店名サイン。奥の既設SUS扉越しに受付の木調壁ロゴが見える"),
               (4170, -1600, -6800, "①木調縦ルーバー（不燃・ガラス面より600mm以上後退）＋小型ロゴ　非照明・背面から電球色の間接光のみ"),
               (10900, -1450, -6200, "③S1：ビル共用案内板に店名・ロゴ（ビル標準仕様／乳半アクリル・LED内照）")]
    for x, y, ty, t in leaders:
        s.line(x, y, x - 150, ty + 120, INK, 0.15)
        s.circle(x, y, 40, INK, "none", 0)
        s.text(x - 150, ty, t, 4.4, INK)
    return s.svg((-900, -7900, 16000, 10300), 228, 147)


def a04_left():
    s = S(300)
    H = F1 + 12 * 3900
    s.rect(0, -H, 14300, H, "#EEF0F2", "#888", 0.2)
    for f in range(12):
        y0 = -F1 - (f + 1) * 3900
        fill = "#EBDDC8" if f in (2, 3) else "#D3DEE7"
        s.rect(700, y0 + 500, 12900, 2700, fill, "#9fb0bf", 0.15)
        for k in range(1, 12):
            s.line(700 + k * 1075, y0 + 500, 700 + k * 1075, y0 + 3200, "#9fb0bf", 0.1)
        s.text(-400, y0 + 2200, f"{f + 2}F", 5, "#C0392B" if f in (2, 3) else SUB, "end", 700 if f in (2, 3) else 400)
        if f in (2, 3):
            s.rect(-150, y0 + 200, 14600, 3400, "none", "#C0392B", 0.4, 'stroke-dasharray="300 200"')
    cols = [("#6b6157", 0, 2300), (PANEL, 2300, 3300), (GLS, 3300, 5000), (PANEL, 5000, 6800), (PANEL2, 6800, 10300), ("#B9CAD6", 10300, 14300)]
    for c, a, b in cols:
        s.rect(a, -OPEN, b - a, OPEN, c, "#888", 0.15)
    s.rect(0, -F1, 14300, F1 - OPEN, BAND, "none", 0)
    s.text(-400, -1800, "1F", 5, "#C0392B", "end", 700)
    s.rect(-150, -F1 - 200, 7100, F1 + 200, "none", "#C0392B", 0.4, 'stroke-dasharray="300 200"')
    s.line(-2000, 0, 16500, 0, INK, 0.5)
    return s.svg((-2500, -H - 1500, 19500, H + 3000), 65, 186)


def build_a04():
    inner = f'''<div class="fig" style="left:14mm;top:34mm">{a04_left()}<p class="cap c">正面全体立面（Y1通り・模式）<br><span>S=1/300　赤破線＝当社区画</span></p></div>
<div class="fig" style="left:82mm;top:44mm">{a04_center()}<p class="cap c">1階 正面部分立面図（サイン位置・使用素材）<br><span>S=1/70</span></p></div>
<div class="signs" style="left:316mm;top:14mm">
<h3>サイン詳細（ビル指定仕様に準拠）</h3>
<div class="sg"><div class="s1"><small>日本橋WASAMIビル</small><b>fukka</b></div><p><b>S1</b>　W640×H340<br>ビル共用案内板（エントランス）<br>乳半アクリル＋ロゴ出力・LED内照<br>表示：ロゴのみ／約0.14㎡</p></div>
<div class="sg"><div class="s2"><b>fukka</b><small>1F・4F・5F</small></div><p><b>S2</b>　W300×H300<br>玄関ポーチ脇壁（店舗用サインスペース）<br>マットアクリル＋ダイノック<br>白切文字／約0.09㎡　※寸法・位置はビル基準</p></div>
<h3 style="margin-top:6mm">外装サイン方針</h3><p class="mut">（貸主ご意向：落ち着いた外観）</p>
<ul><li>突出・袖看板、壁面大型看板は設けない</li><li>ガラス面のフィルム・ポスター広告なし</li><li>S1・S2以外の屋外サインなし</li>
<li>点滅・映像・赤色光・ネオン不使用</li><li>店名・ロゴのみ（価格・施術内容の広告なし）</li><li>電球色2700〜3000Kの間接光、調光・タイマー</li>
<li>ガラス面から600mm以上離隔、既設サッシ無加工</li><li>玄関ポーチは既設のまま（造作・扉の追加なし）</li><li>4・5F窓：防炎ロールスクリーンのみ</li></ul></div>
<div class="notes" style="left:14mm;top:250mm;width:230mm">
<p>・1F階高4,950は貸主CAD（展開図 1FL→2FL）より。基準階階高3,900、2F以上の外装は完成予想CGからの模式表現。</p>
<p>・当社専用アプローチは「道路側開放の玄関ポーチ＋奥の既設SUS製両開き扉（A工事）」。風除室・ガラス扉の新設はしない（改訂）。</p>
<p>・サイン位置・形状はビル側指定（内装マニュアル7-(6)）に準拠。最終仕様は運営管理者と協議のうえ承認を得る。</p></div>'''
    return sheet(inner, "外観立面図・サイン計画図", "S=1/300・1/70", "A-04")


# ================================================================= A-05
def a05_plan():
    s = S(40)
    s.rect(-200, -300, 4600, 3200, "#fff", "none", 0)
    s.rect(1680, 300, 2700, 2300, ROOM, "none", 0)                    # 店内
    s.rect(0, 595, 1680, 1705, APP, "none", 0)                        # ポーチ床
    s.path("M-80,-80 L560,550 L560,640 L-80,0 Z", COL, "none", 0)     # 斜め壁
    s.rect(560, 545, 1120, 90, COL, "none", 0)                         # 上側の壁
    s.rect(-80, 2300, 1760, 160, COL, "none", 0)                       # 下側の脇壁
    s.rect(-160, 2300, 160, 400, COL, "none", 0)
    s.rect(1620, 300, 120, 300, COL, "none", 0); s.rect(1620, 2300, 120, 300, COL, "none", 0)
    s.rect(300, 2240, 700, 60, "#2f3134", "none", 0)                   # S2
    # 既設扉
    s.line(1680, 640, 1680, 2300, GLSL, 0.6)
    door(s, 1680, 640, 1000, 90, 0, 0.35, INK); door(s, 1680, 2300, 640, -90, 0, 0.35, INK)
    s.rect(4060, 300, 140, 2300, WOODC, "none", 0)                     # 正面の木調壁
    s.rect(2900, 900, 1150, 600, WOODC, "#7a5a3a", 0.25, 'rx="80"')
    s.line(-900, 1450, 4400, 1450, INK, 0.2, "200 60 40 60")
    s.text(-880, 1400, "A", 7, INK, weight=700); s.text(4400, 1400, "A", 7, INK, "end", 700)
    s.arrow([(-1100, 1700), (-150, 1700)], "#C0392B", 0.6)
    s.arrow([(250, 1700), (2700, 1700)], "#C0392B", 0.5, "100 60")
    T = s.text
    T(-1100, 1950, "道路（歩道）", 5.5, "#C0392B", weight=700)
    T(840, 1200, "玄関ポーチ（既設）", 5.5, INK, "middle", 700)
    T(840, 1450, "1,680×1,705", 4.6, SUB, "middle")
    T(-60, 2850, "道路側：開放", 4.6, "#C0392B")
    T(3300, 2350, "店内（受付・待合）", 5, SUB, "middle")
    s.dim(0, 640, 1680, 640, "1,680", -1100, 4.6)
    s.dim(0, 640, 0, 2300, "1,705", -500, 4.6, vertical=True)
    return s


def a05_section():
    s = S(40)
    s.path(f"M-1300,{-F1-300} L4300,{-F1-300} L4300,{-F1} L0,{-F1} L0,{-OPEN} L-300,{-OPEN} L-300,{-F1-300} Z", COL, "none", 0)
    s.line(-1300, 0, 4300, 0, INK, 0.5)
    s.rect(0, -OPEN, 1680, 120, "#E9E6E1", "#888", 0.2)                  # 軒天
    s.rect(0, -OPEN + 120, 1680, OPEN - 120, "#F4F2EE", "none", 0)       # 奥の脇壁（見え掛かり）
    s.rect(400, -2350, 700, 330, "#2f3134", "none", 0)                    # S2
    s.text(750, -2140, "fukka", 6, "#fff", "middle", 700)
    s.rect(1650, -2400, 60, 2400, GLS, GLSL, 0.3)                         # 既設扉
    s.rect(1640, -OPEN, 80, OPEN - 2400, COL, "none", 0)
    s.rect(1720, -3000, 2600, 60, "#E2DED8", "#888", 0.2)                # 店内天井 CH3,000
    s.rect(4060, -3000, 140, 3000, WOODC, "none", 0)                      # 正面の木調壁
    s.text(4130, -2050, "fukka", 4.6, "#fff", "middle", 700, rot=-90)
    s.rect(2900, -1050, 600, 1050, WOODC, "#7a5a3a", 0.25)
    s.rect(1720, -3000, 2340, 3000, ROOM, "none", 0, 'opacity="0.6"')
    s.add('<rect x="2600" y="-2940" width="300" height="40" fill="#F2D49B"/>')
    person(s, -650, 0); person(s, 850, 0)
    s.arrow([(-1100, -900), (2600, -900)], "#C0392B", 0.5, "100 60")
    lab = [(1680, -1200, "①既設SUS製両開き扉（A工事・無加工）H≒2,400"), (750, -2180, "②S2：ポーチ脇壁サイン（ビル指定スペース）"),
           (840, -OPEN + 60, "③床・軒天・壁：既設のまま（造作・扉の追加なし）"), (4130, -2600, "④店内正面：木調壁＋店名ロゴ（扉越しに見える）"),
           (2750, -2920, "⑤間接照明（電球色2,700K・調光）")]
    for i, (x, y, t) in enumerate(lab):
        ty = -4600 + i * 420
        s.circle(x, y, 40, INK, "none", 0)
        s.line(x, y, 4500, ty - 50, INK, 0.12)
        s.text(4550, ty, t, 4.4, INK)
    T = s.text
    T(-1250, 400, "道路（歩道）", 5, "#C0392B", weight=700); T(840, 400, "玄関ポーチ（屋外）", 5, INK, "middle")
    T(2900, 400, "店内（受付）", 5, INK, "middle")
    T(-150, -OPEN + 500, "開放", 5.5, "#C0392B", "end", 700)
    s.dim(-1250, -F1, -1250, 0, "1F階高 4,950", 0, 4.4, vertical=True)
    s.dim(0, 0, 1680, 0, "1,680", 750, 4.4)
    return s


def a05_front():
    s = S(60)
    s.rect(-300, -F1, 2900, F1 - OPEN, BAND, "#999", 0.2)
    s.rect(0, -OPEN, 2300, OPEN, "#E2DED8", INK, 0.3)
    s.path(f"M0,{-OPEN} L600,{-OPEN+380} L600,0 L0,0 Z", "#CFCAC2", "#888", 0.15)
    s.path(f"M2300,{-OPEN} L2120,{-OPEN+380} L2120,0 L2300,0 Z", "#D5D1CA", "#888", 0.15)
    s.rect(600, -OPEN + 380, 1520, OPEN - 380, "#EDEAE5", "#888", 0.15)
    s.rect(650, -2400, 1420, 2400, GLS, "#7d8790", 0.35); s.line(1360, -2400, 1360, 0, "#7d8790", 0.3)
    s.rect(820, -2150, 400, 900, WOODC, "none", 0, 'opacity="0.55"'); s.text(1020, -1800, "fukka", 6, "#fff", "middle", 700)
    s.rect(2150, -2250, 110, 380, "#2f3134", "none", 0)
    s.rect(2300, -OPEN, 300, OPEN, PANEL, "#999", 0.2); s.rect(-300, -OPEN, 300, OPEN, "#cfcfcf", "#999", 0.2)
    s.line(-500, 0, 2800, 0, INK, 0.5)
    return s


def build_a05():
    p = a05_plan(); sec = a05_section(); fr = a05_front()
    labels = '''<div class="callout" style="left:16mm;top:122mm;width:140mm">
①既設SUS製両開き扉（A工事・無加工）<br>②S2：ポーチ脇壁サイン（ビル指定サインスペース）<br>③床・軒天・壁：既設のまま（造作・扉の追加なし）<br>④店内正面：木調壁＋店名ロゴ（扉越しに見える）</div>'''
    inner = f'''<h1>1F 専用アプローチ（玄関ポーチ）詳細図</h1>
<div class="fig" style="left:14mm;top:26mm"><p class="cap c">平面詳細　S=1/40</p>{p.svg((-1300, -200, 5800, 3400), 145, 85)}</div>
<div class="fig" style="left:166mm;top:26mm"><p class="cap c">断面詳細 A-A　S=1/40</p>{sec.svg((-1400, -5300, 9600, 6100), 240, 152)}</div>
{labels}
<div class="fig" style="left:16mm;top:150mm"><p class="cap">正面（道路から見た姿）S=1/60</p>{fr.svg((-400, -5100, 3200, 5400), 53, 90)}</div>
<div class="callout" style="left:74mm;top:190mm;width:70mm;color:#555">手前：開放（扉なし）<br>奥：既設SUS扉＋店内の木調壁ロゴ<br><span style="color:#C0392B">→ 外装イメージ（P.8）と同一</span></div>
<div class="notes" style="left:14mm;top:256mm;width:230mm">
<p>・既設アプローチ（玄関ポーチ）は区画内。道路側は開放で、扉は奥の既設SUS製両開き扉（A工事）1か所のみ。扉・サッシは無加工。</p>
<p>・当社工事（C工事）は店内側のみ：正面の木調壁＋店名ロゴ、受付カウンター、天井・間接照明。ポーチ内には造作を設けない。</p>
<p>・S2サインはビル指定の店舗用サインスペース（店舗入口脇壁面・屋外）に掲出。寸法・表示はビル基準で事前協議。</p>
<p>・床・軒天は既設仕上げのまま使用。扉高さ・軒天高さ・ポーチ照明の有無は実施設計時に確認（寸法は貸主図面からの読み取り値）。</p></div>'''
    return sheet(inner, "1F専用アプローチ 詳細図（平面・断面・正面）", "S=1/40・1/60", "A-05")


# ================================================================= 外装イメージ・内装イメージ
def build_ext_img():
    return '''<section class="sheet img"><h2 class="ih">外装イメージ<span>EXTERIOR IMAGE</span></h2>
<figure class="big"><img src="../r3/r_main.png"><figcaption><em>外装</em><b>正面（Y1通り）外観イメージ</b><br>ビル既設の外装はそのまま。当社の表示は、玄関ポーチ脇壁のS2サイン、SSW-2ガラス奥（600mm後退）の木調ルーバー上の小型ロゴ、ビル共用案内板（S1）のみ。突出看板・ガラス面広告はありません（立面図 A-04 と同一仕様）。</figcaption></figure>
<figure class="r1"><img src="../r3/r_approach.png"><figcaption><em>外装</em><b>1F 専用アプローチ（玄関ポーチ）まわり</b><br>道路側は開放のまま。ポーチ奥の既設SUS扉越しに、店内正面の木調壁と店名ロゴが見えます。電球色のダウンライトで、夜も落ち着いた表情です。</figcaption></figure>
<figure class="r2"><img src="../r3/r_front.png"><figcaption><b>正面全景</b><br>4・5F窓面は内側の防炎ロールスクリーンのみで、サイン表示はありません。</figcaption></figure>
<p class="pg">P.8</p></section>'''


def build_int_img():
    return '''<section class="sheet img"><h2 class="ih">内装イメージ（1F 入口・受付）<span>INTERIOR IMAGE</span></h2>
<figure class="big"><img src="../r3/r_interior.png"><figcaption><em>内装</em><b>待合から受付を見る</b><br>既設扉（左の壁の奥）から入るとすぐ、正面の木調壁と店名ロゴ、受付カウンターが見えます。扉の内側1,220mmは何も置かず、車いすでもそのまま受付に着けます。</figcaption></figure>
<div class="fin"><h3>主な仕上げ</h3><table>
<tr><td>正面壁</td><td>木目調不燃化粧板（縦ルーバー）＋店名ロゴ</td></tr><tr><td>受付</td><td>木調カウンター H1,050／天板 人工大理石</td></tr>
<tr><td>床</td><td>タイルカーペット（防炎）／入口1.2mは長尺シート</td></tr><tr><td>壁</td><td>EP（アイボリー）</td></tr>
<tr><td>天井</td><td>PB t9.5+12.5 EP（白）CH3,000</td></tr><tr><td>照明</td><td>電球色2,700K・調光（間接照明＋ダウンライト）</td></tr></table>
<p>銀座院と同じ「木調×アイボリー」。内装材はすべて不燃材、カーペットは防炎品。</p></div>
<p class="pg">P.9</p></section>'''


CSS2 = """
@page{size:420mm 297mm;margin:0}
*{box-sizing:border-box}body{margin:0;background:#bbb;font-family:'Noto Sans CJK JP',sans-serif;color:#222}
.sheet{position:relative;width:420mm;height:297mm;background:#fff;margin:0 auto 8mm;overflow:hidden;break-after:page}
.sheet::before{content:"";position:absolute;inset:5mm;border:0.45mm solid #333;pointer-events:none}
h1{position:absolute;left:0;right:0;top:11mm;margin:0;text-align:center;font:700 5mm/1 'Noto Sans Mono CJK JP',monospace}
.sub{position:absolute;left:0;right:0;top:18mm;margin:0;text-align:center;color:#C0392B;font:700 3.2mm/1 'Noto Sans Mono CJK JP',monospace}
.road{position:absolute;left:12mm;top:12mm;margin:0;color:#C0392B;font:700 2.8mm/1 'Noto Sans Mono CJK JP',monospace}
.fig{position:absolute}.cap{font:700 3mm/1.3 'Noto Sans Mono CJK JP',monospace;margin:0 0 1.5mm}.cap.c{text-align:center}.cap span{font-weight:400;font-size:2.3mm;color:#666}
.orient{position:absolute;right:12mm;top:28mm;width:40mm;border:0.25mm solid #888;padding:2mm;text-align:center;font:700 2.4mm/1.5 'Noto Sans Mono CJK JP',monospace}
.orient span{font-weight:400;font-size:2mm;color:#555}
.legend.v{position:absolute;display:flex;flex-direction:column;gap:2mm;font:2.4mm/1 'Noto Sans Mono CJK JP',monospace}
.lg{display:flex;align-items:center;gap:2mm}.lg i{display:inline-block;width:7mm;height:3.6mm;border:0.2mm solid #aaa}
table{position:absolute;border-collapse:collapse;font:2.4mm/1.4 'Noto Sans Mono CJK JP',monospace}
table th{font-weight:700;text-align:left;padding:0 0 1mm}table td{padding:0.3mm 0;border-bottom:0.12mm solid #ccc}.area td:last-child{text-align:right}
.notes{position:absolute;font:2.2mm/1.6 'Noto Sans Mono CJK JP',monospace;color:#444}.notes p{margin:0}
.callout{position:absolute;font:2.4mm/1.7 'Noto Sans Mono CJK JP',monospace}
.tb{position:absolute;right:5mm;bottom:5mm;width:172mm;border-top:0.4mm solid #333;border-left:0.4mm solid #333;font-family:'Noto Sans Mono CJK JP',monospace}
.tb1{padding:2.4mm 4mm;font-weight:700;font-size:2.9mm;border-bottom:0.3mm solid #333}
.tb2{display:grid;grid-template-columns:1fr 36mm}.tb2>div{padding:2.4mm 4mm;display:flex;flex-direction:column;gap:2mm}
.tb2 b{font-size:3.3mm}.tb2 span{font-size:2.1mm;color:#555}.tb2 .sc{border-left:0.3mm solid #333;align-items:center}
.signs{position:absolute;width:92mm;font:2.3mm/1.5 'Noto Sans Mono CJK JP',monospace}
.signs h3{font-size:3mm;margin:0 0 3mm}.signs .mut{color:#666;margin:-2mm 0 1mm}.signs ul{margin:0;padding-left:3mm}.signs li{list-style:"・"}
.sg{display:grid;grid-template-columns:44mm 1fr;gap:3mm;align-items:start;margin-bottom:4mm}.sg p{margin:0}
.s1{background:#2b2b2b;padding:2.2mm;height:23mm;display:flex;flex-direction:column}.s1 small{color:#ddd;font-size:1.6mm}
.s1 b{flex:1;background:#f6f2ea;color:#2f3c80;display:grid;place-items:center;font:700 9mm/1 'Noto Sans CJK JP',sans-serif;margin-top:1mm}
.s2{background:#2f3134;color:#fff;width:23mm;height:23mm;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1mm;margin-left:10mm}
.s2 b{font:600 5mm/1 'Noto Sans CJK JP',sans-serif}.s2 small{font-size:1.4mm;color:#ccc}
.img .ih{position:absolute;left:12mm;top:9mm;right:12mm;margin:0;padding-bottom:3mm;border-bottom:0.35mm solid #9B7B55;font:700 8mm/1 'Noto Sans CJK JP',sans-serif}
.img .ih span{font:500 3.6mm/1 'Noto Sans CJK JP',sans-serif;letter-spacing:.2em;color:#9B7B55;margin-left:6mm}
.img figure{position:absolute;margin:0}.img img{width:100%;display:block;border-radius:1.2mm;object-fit:cover}
.img figcaption{font:2.6mm/1.6 'Noto Sans Mono CJK JP',monospace;color:#444;margin-top:3mm}
.img figcaption b{font-size:3.3mm;color:#222}.img em{font-style:normal;background:#9B7B55;color:#fff;font-size:2.3mm;padding:.4mm 2mm;border-radius:.8mm;margin-right:2mm}
.img .big{left:12mm;top:26mm;width:246mm}.img .big img{height:154mm}
.img .r1{left:266mm;top:26mm;width:142mm}.img .r1 img{height:89mm}
.img .r2{left:266mm;top:154mm;width:142mm}.img .r2 img{height:89mm}
.img .pg{position:absolute;right:12mm;bottom:8mm;margin:0;font:2.4mm 'Noto Sans Mono CJK JP',monospace;color:#777}
.fin{position:absolute;left:266mm;top:26mm;width:142mm;font:2.6mm/1.6 'Noto Sans Mono CJK JP',monospace}
.fin h3{font-size:3.4mm;margin:0 0 2mm}.fin table{position:static;width:100%}.fin td:first-child{width:22mm;color:#9B7B55;font-weight:700}
@media print{body{background:#fff}.sheet{margin:0}}
"""

if __name__ == "__main__":
    html = f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>1階 差し替え</title><style>{CSS2}</style></head><body>"
    html += build_a01() + build_a04() + build_a05() + build_ext_img() + build_int_img() + "</body></html>"
    open("sheets_v2.html", "w").write(html)
    print("ok")
