"""日本橋WASAMIビル fukka 出店計画 ― 各階プランの共通ジオメトリ（単位: mm）

座標系（各階）:
  x : 正面道路（Y1通り側）の貸室内壁面を 0 とし、奥（Y8側）へ +
  y : コア側の貸室内壁面を 0 とし、X1通り側（窓側）へ +
1F : 募集図面（店舗区画 98.36㎡／約29.75坪）・1F CAD より。原点 = CAD座標 (9750, 14750)
4・5F : 募集図面（各階 G229.86㎡／約69.53坪）より。原点 = CAD X座標 11036（Y1柱芯の422mm手前）
"""
import json

AREA = {"1F": (98.36, 29.75), "4F": (229.86, 69.53), "5F": (229.86, 69.53)}
CAD_ORIGIN = {"1F": (9750, 14750), "4F": (11036, 12700), "5F": (11036, 12700)}

# 1F 募集図面スキャン（150dpi）上の位置合わせ：貸室原点(0,0)の画素位置と縮尺
SCAN_1F = dict(px0=539, py0=1243, px_per_m=115.6)

GRID_1F = {f"Y{i+1}": 11458 + 2700 * i - 9750 for i in range(8)}
GRID_UP = {f"Y{i+1}": 422 + 2700 * i for i in range(8)}


def R(id, name, x0, y0, x1, y1, kind="room", doors=(), label=True, lp=None, windows=(), sinks=(), nowall=(), mri_axis=None):
    """kind: treat / room / mri / open / hall(廊下・通路) / service / core / tcore(区画内の既設部) / existing"""
    return dict(id=id, name=name, x0=x0, y0=y0, x1=x1, y1=y1, kind=kind,
                doors=[dict(side=d[0], at=d[1], w=d[2], type=(d[3] if len(d) > 3 else "slide"))
                       for d in doors],
                label=label, lp=lp, windows=[dict(side=w[0], a=w[1], b=w[2]) for w in windows],
                sinks=list(sinks), nowall=list(nowall), mri_axis=mri_axis)


# ---------------------------------------------------------------- 1F（98.36㎡）
F1_W, F1_D = 13900, 6550
PORCH_X, PORCH_Y0 = 1780, 4500   # 玄関ポーチ：奥の既設扉位置・コア側の壁（1F CAD より）
EXAM_X = [(4200, 6400), (6400, 8600), (8600, 10800), (10800, 13030)]   # 診察室 4室（X1側・各約5.6㎡）
TREAT_X = [(4200, 6900), (6900, 9600), (9600, 12300)]                  # 処置室 3室（コア側・各約7.6㎡）
F1 = dict(
    floor="1F", W=F1_W, D=F1_D, ch=3700, partition_h=2700,
    title="1階 平面計画図（受付・待合・診察室・処置室）",
    # 右上の切欠き（区画外の小室）
    notch=(13030, 4360, F1_W, F1_D),
    rooms=[
        R("vest", "玄関ポーチ\n（既設・道路側開放）", 0, PORCH_Y0, PORCH_X, F1_D, "existing", lp=(890, 5500)),
        R("wait", "待合（15席）", 0, 0, 4200, PORCH_Y0, "open", lp=(2500, 4150)),
        R("corr", "廊下", 4200, 2800, 13030, 4000, "hall", lp=(8700, 3400)),
    ] + [R(f"ex{i+1}", f"診察室{i+1}", x0, 4000, x1, F1_D, "room", doors=[("S", x0 + 1100, 900)],
           lp=(x0 + 950, 4600), sinks=[(x0 + 350, 4300)])
         for i, (x0, x1) in enumerate(EXAM_X)]
      + [R(f"tr{i+1}", f"処置室{i+1}", x0, 0, x1, 2800, "room", doors=[("N", x0 + 1350, 1000)],
           lp=(x0 + 1350, 2350), sinks=[(x1 - 400, 2500)])
         for i, (x0, x1) in enumerate(TREAT_X)]
      + [R("sf", "スタッフ室", 12300, 0, F1_W, 2800, "service", doors=[("N", 12680, 700, "swing")], lp=(13100, 1500)),
         R("st1", "倉庫", 13030, 2800, F1_W, 4360, "service", doors=[("W", 3400, 700, "swing")], lp=(13470, 3700))],
    reception=dict(cx=3920, cy=5420, r=920, a0=100, a1=260, back=(3920, 4560, 4200, 6450), depth=430),
    chairs=[(1000, 600 + 600 * k, 180) for k in range(6)]
           + [(x, y, 270) for y in (1300, 2350, 3400) for x in (1900, 2500, 3100)],
    plants=[(1000, 4180), (1650, 350)],
    # 道路側：既設ガラス面（A工事・変更不可）。室内側はガラス面から600mm後退した木調縦ルーバー
    openings=[dict(side="W", a=0, b=PORCH_Y0, kind="window", note="道路側ガラス面（既設・A工事）")],
    louver=dict(x=600, y0=150, y1=PORCH_Y0 - 150, pitch=140),
    porch_door=dict(x=PORCH_X, y0=4650, y1=6300, leaves=(850, 800), note="既設SUS製両開き扉（A工事）"),
    entrances=[dict(side="S", at=3000, w=800, note="館内側出入口（既設）"),
               dict(side="X", at=(PORCH_X, 5475), w=1650, note="既設両開き扉")],
    columns=[(GRID_1F[k], F1_D) for k in ("Y1", "Y2", "Y3", "Y4", "Y5")],
    grid=GRID_1F,
)

# ---------------------------------------------------------------- 4F / 5F（各 G229.86㎡）
UW, UD = 21000, 8600
ROW_Y0 = 6100          # 窓側施術室列の手前
AISLE_Y0 = 4500        # 通路（両側居室のため有効1,600mm）
NROW = 8
ROOM_W = UW / NROW     # 2,625
COR_X0, COR_X1, COR_Y1 = 2050, 11000, 1400   # 避難経路（EVホール～階段附室）
EVH = (9150, 11000, -4100)                    # EVホール（区画内）


def window_row(prefix):
    rooms = []
    for i in range(NROW):
        x0 = round(i * ROOM_W)
        x1 = round((i + 1) * ROOM_W)
        rooms.append(R(f"{prefix}{i+1:02d}", f"施術室\n{prefix}{i+1:02d}", x0, ROW_Y0, x1, UD,
                       "treat", doors=[("S", (x0 + x1) / 2, 900)]))
    return rooms


CORE = [  # 募集図面（4・5F）より。tcore＝貸室区画に含まれる既設部分
    R("sto", "倉庫\n（区画内）", 0, -4800, 2000, 0, "tcore"),
    R("anx", "附室", 2050, -4800, 3400, -850, "core"),
    R("ps1", "PS・DS", 2050, -850, 8800, 0, "core"),
    R("st", "特別避難階段", 3450, -4800, 6050, -850, "core"),
    R("ev1", "乗用EV", 6200, -4800, 8800, -850, "core"),
    R("evh", "EVホール\n（区画内）", EVH[0], EVH[2], EVH[1], 0, "tcore"),
    R("ev2", "非常用EV", 11250, -4800, 13900, 0, "core"),
    R("wc", "共用トイレ（男女別）", 14000, -4800, 18600, 0, "core"),
    R("eq", "設備・\nメンテ", 18700, -4800, UW, 0, "core"),
]
PANTRY_XY = (18100, 0, 18900, 2200)   # 既設カウンターキッチン（募集図面）


# 4・5F 共通：西側は特別避難階段に面する廊下、中央はEVホールから続くロビー、東側はトイレへの通路
HALL_W = R("hw", "廊下", COR_X0, 0, 5600, 1300, "hall", lp=(4300, 650))
PASS_E = R("he", "通路\n（トイレへ）", 15200, 0, 16400, AISLE_Y0, "hall", lp=(15800, 1800))
AISLE = R("ais", "通路", 0, AISLE_Y0, UW, ROW_Y0, "hall", lp=(15800, 5500))


def upper(floor, rooms, title, **kw):
    d = dict(floor=floor, W=UW, D=UD, ch=2800, partition_h=2300, title=title,
             rooms=rooms,
             reception=None, chairs=[], core=CORE, evh=EVH,
             entrances=[dict(side="EVH", at=10075, w=1850, note="EVホールより（防火扉・既設）")],
             stair_door=(2250, 3100),
             store_door=(500, 1300),
             toilet_door=(15400, 16200),
             columns=[(v, UD) for v in GRID_UP.values()],
             grid=GRID_UP,
             openings=[dict(side="W", a=300, b=UD - 300, kind="window")])
    d.update(kw)
    return d


# ---------------------------------------------------------------- 4F：運動室13室・受付・待合・女性更衣室（10億モデル）
EX_W_Y0, EX_AIS = 5500, (3900, 5500)     # 窓側の運動室列（奥行3,100）・通路（有効1,600）
EX_S_Y0 = 1500                           # コア側の運動室列（奥行2,400）
EX_N = 9
F4_ROOMS = (
    [R(f"4{i+1:02d}", f"運動室\n4{i+1:02d}", round(i * UW / EX_N), EX_W_Y0, round((i + 1) * UW / EX_N), UD, "treat",
       doors=[("S", round((i + 0.5) * UW / EX_N), 900)]) for i in range(EX_N)]
    + [R(f"4{10+i}", f"運動室\n4{10+i}", x0, EX_S_Y0, x0 + 3000, EX_AIS[0], "treat", doors=[("N", x0 + 1500, 900)])
       for i, x0 in enumerate((0, 3000, 6000, 15000))]
    + [R("hw", "廊下（階段・倉庫へ）", 0, 0, 9000, EX_S_Y0, "hall", lp=(4500, 750)),
       R("lb", "受付・待合ロビー", 9000, 0, 15000, EX_AIS[0], "open", lp=(12000, 300)),
       R("he", "通路（トイレへ）", 15000, 0, 18000, EX_S_Y0, "hall", lp=(16500, 1050)),
       R("lw", "更衣室（女性）\nパウダー付", 18000, 0, UW, EX_AIS[0], "room", doors=[("N", 20500, 800)], lp=(19300, 2050)),
       R("ais", "通路", 0, EX_AIS[0], UW, EX_AIS[1], "hall", lp=(12000, 4700))])
F4 = upper("4F", F4_ROOMS, "4階 平面計画図（運動室13室・受付・待合・女性更衣室）",
           reception=dict(cx=13900, cy=2650, r=1050, a0=100, a1=260, back=(14700, 1600, 15000, 3700)),
           chairs=[(9350, y, 180) for y in (1800, 2400, 3000, 3600)]
                  + [(x, y, 180) for x in (11300, 11900) for y in (1300, 1900, 2500, 3100)],
           plants=[(12500, 3650)])

# ---------------------------------------------------------------- 5F：評価室3室・認知室4室・撮影室・スタッフルーム・フリースペース（ジム）
F5_ROOMS = (
    [R(f"ev{i+1}", f"評価室{i+1}", x0, 4600, x0 + 4500, UD, "room", doors=[("S", x0 + 900, 900)], lp=(x0 + 2250, 7900))
     for i, x0 in enumerate((0, 4500, 9000))]
    + [R(f"cg{i+1}", f"認知室\n{i+1}", 4000 + 1500 * i, 1300, 5500 + 1500 * i, 3000, "room", doors=[("N", 4750 + 1500 * i, 700)])
       for i in range(4)]
    + [R("ph", "撮影室（歩行）", 0, 1300, 4000, 3000, "room", doors=[("N", 3400, 800)], lp=(1700, 2550)),
       R("sto", "倉庫", 11500, 1300, 13500, 3000, "service", doors=[("N", 12500, 800, "swing")]),
       R("slk", "スタッフ\n更衣・ロッカー", 13500, 1300, 16400, 3000, "room", doors=[("N", 14000, 800)], lp=(15000, 2150)),
       R("sr", "スタッフルーム", 16400, 0, UW, 3000, "room", doors=[("N", 17000, 900)], lp=(19700, 2450)),
       R("hw", "廊下", 0, 0, 16400, 1300, "hall", lp=(6000, 650)),
       R("lk", "", 10000, 1300, 11500, 3000, "hall", label=False),
       R("ais", "通路", 0, 3000, 13500, 4600, "hall", lp=(6750, 3800)),
       R("gym", "フリースペース（ジム予定）", 13500, 3000, UW, UD, "open", lp=(17250, 8100))])
F5 = upper("5F", F5_ROOMS, "5階 平面計画図（評価室・認知室・ジム・スタッフルーム）")

FLOORS = {"1F": F1, "4F": F4, "5F": F5}


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) / 1e6


def treat_count():
    return {k: sum(1 for r in f["rooms"] if r["kind"] == "treat") for k, f in FLOORS.items()}


if __name__ == "__main__":
    import sys
    json.dump(FLOORS, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    print(treat_count())
