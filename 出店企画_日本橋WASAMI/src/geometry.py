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


def R(id, name, x0, y0, x1, y1, kind="room", doors=(), label=True, lp=None):
    """kind: treat / room / mri / open / service / core / tcore(区画内の既設部) / corridor / existing"""
    return dict(id=id, name=name, x0=x0, y0=y0, x1=x1, y1=y1, kind=kind,
                doors=[dict(side=d[0], at=d[1], w=d[2], type=(d[3] if len(d) > 3 else "slide"))
                       for d in doors],
                label=label, lp=lp)


# ---------------------------------------------------------------- 1F（98.36㎡）
F1_W, F1_D = 13900, 6550
F1 = dict(
    floor="1F", W=F1_W, D=F1_D, ch=3700, partition_h=2700,
    title="1階 平面計画図（受付待合・診察室・処置室・MRI室）",
    # 右上の切欠き（区画外の小室）
    notch=(13030, 4360, F1_W, F1_D),
    rooms=[
        R("vest", "エントランス\n（既設アプローチ）", 0, 4260, 1730, F1_D, "existing", lp=(865, 4900)),
        R("ex", "診察室", 5000, 4100, 8000, F1_D, "room", doors=[("S", 6500, 900)], lp=(6300, 6050)),
        R("tr", "処置室", 5000, 0, 8000, 2900, "room", doors=[("N", 6500, 1000)], lp=(6500, 2350)),
        R("op", "MRI操作室", 8000, 0, 9800, 2900, "room", doors=[("N", 8900, 800)], lp=(8900, 900)),
        R("mch", "MRI更衣室", 8000, 4100, 9800, F1_D, "room", doors=[("S", 8900, 800)], lp=(8900, 5600)),
        R("mri", "MRI室（磁気シールド）", 9800, 0, F1_W, 4360, "mri",
          doors=[("W", 3500, 1100, "swing")], lp=(11300, 3850)),
        R("mech", "MRI機械室", 9800, 4360, 13030, F1_D, "service", doors=[("W", 5450, 800, "swing")], lp=(11400, 5450)),
        R("corr", "廊下", 5000, 2900, 9800, 4100, "corridor"),
        R("wait", "待合", 0, 0, 3900, 4260, "open", lp=(1500, 3800)),
    ],
    reception=dict(cx=4500, cy=5350, r=1200, a0=100, a1=260, back=(4600, 4250, 4950, 6450)),
    chairs=[(x, y, 90) for x in (800, 1750, 2700) for y in (700, 1650, 2600)],
    openings=[dict(side="W", a=1550, b=3250, kind="window", note="道路側ガラス面（サイン規制範囲）")],
    entrances=[dict(side="S", at=3000, w=800, note="館内側出入口（既設）"),
               dict(side="X", at=(1730, 5400), w=1200, note="アプローチ扉")],
    columns=[(GRID_1F[k], F1_D) for k in ("Y1", "Y2", "Y3", "Y4", "Y5")],
    grid=GRID_1F,
)

# ---------------------------------------------------------------- 4F / 5F（各 G229.86㎡）
UW, UD = 21000, 8600
ROW_Y0 = 6100          # 窓側施術室列の手前
AISLE_Y0 = 4900        # 通路
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
PANTRY = R("pt", "既設\n給湯", 18100, 0, 18900, 2200, "existing")


def upper(floor, rooms, title, **kw):
    d = dict(floor=floor, W=UW, D=UD, ch=2800, partition_h=2300, title=title,
             rooms=window_row(floor[0]) + rooms + [PANTRY, R("ais", "", 0, AISLE_Y0, UW, ROW_Y0, "open", label=False)],
             reception=None, chairs=[], core=CORE, evh=EVH,
             entrances=[dict(side="CORE", at=10100, w=1600, note="自動ドア（エントランス）")],
             stair_door=(2250, 3100),
             toilet_door=15800,
             columns=[(v, UD) for v in GRID_UP.values()],
             grid=GRID_UP,
             openings=[dict(side="W", a=300, b=UD - 300, kind="window"), dict(side="N", a=300, b=UW - 300, kind="window")])
    d.update(kw)
    return d


CORR = R("cor", "避難経路（廊下状）", COR_X0, 0, COR_X1, COR_Y1, "corridor")

F4 = upper("4F", [
    CORR,
    R("lm", "更衣室\n（男性）", 0, 0, COR_X0, 2400, "room", doors=[("E", 1900, 700)], lp=(1025, 1300)),
    R("lw", "更衣室（女性）", 0, 2400, 2900, AISLE_Y0, "room", doors=[("N", 1900, 800)], lp=(1450, 3500)),
    R("w1", "待合", 2900, COR_Y1, 8400, AISLE_Y0, "open", lp=(5600, 4450)),
    R("w2", "待合", 12000, 0, 16600, AISLE_Y0, "open", lp=(14300, 4450)),
    R("cs", "カウンセリング室", 16600, 2400, 18900, AISLE_Y0, "room", doors=[("N", 17750, 900)]),
    R("ln4", "物品・\nリネン庫", 16600, 0, 18100, 2400, "service", doors=[("W", 1200, 800)]),
    R("st4", "スタッフ\nステーション", 18900, 0, UW, AISLE_Y0, "service", doors=[("N", 19950, 900)]),
], "4階 平面計画図（受付・待合・更衣室・施術室）",
    reception=dict(cx=10200, cy=3300, r=1150, a0=195, a1=345, back=(9000, 4250, 11400, 4650)),
    chairs=[(x, 1100, 180) for x in (12800, 13800, 14800, 15800)] + [(x, 2400, 180) for x in (12800, 13800, 14800, 15800)] +
           [(x, 2300, 270) for x in (3500, 4400, 5300, 6200)] + [(x, 3400, 270) for x in (3500, 4400, 5300, 6200)])

F5 = upper("5F", [
    CORR,
    R("ln5", "リネン庫", 0, 0, COR_X0, COR_Y1, "service", doors=[("N", 1025, 800)], lp=(1025, 600)),
    R("sr", "スタッフ休憩室", 0, COR_Y1, 4300, AISLE_Y0, "room", doors=[("N", 3600, 900)]),
    R("slm", "スタッフ\n更衣（男）", 4300, COR_Y1, 5700, AISLE_Y0, "room", doors=[("N", 5000, 700)]),
    R("slw", "スタッフ\n更衣（女）", 5700, COR_Y1, 7100, AISLE_Y0, "room", doors=[("N", 6400, 700)]),
    R("fs", "フリースペース", 7100, COR_Y1, 14000, AISLE_Y0, "open", lp=(10600, 4450)),
    R("509", "施術室\n509", 14000, 2400, 16600, AISLE_Y0, "treat", doors=[("N", 15300, 900)]),
    R("510", "施術室\n510", 16600, 2400, 19200, AISLE_Y0, "treat", doors=[("N", 17900, 900)]),
    R("sp5", "物品庫", 16600, 0, 18100, 2400, "service", doors=[("W", 1200, 800)]),
    R("of5", "事務室", 19200, 0, UW, AISLE_Y0, "room", doors=[("N", 20100, 900)]),
], "5階 平面計画図（施術室・フリースペース・スタッフ休憩室）",
    lounge=dict(x0=7400, y0=1900, x1=12800, y1=4500))

FLOORS = {"1F": F1, "4F": F4, "5F": F5}


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) / 1e6


def treat_count():
    return {k: sum(1 for r in f["rooms"] if r["kind"] == "treat") for k, f in FLOORS.items()}


if __name__ == "__main__":
    import sys
    json.dump(FLOORS, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    print(treat_count())
