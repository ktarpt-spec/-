"""日本橋WASAMIビル fukka 出店計画 ― 各階プランの共通ジオメトリ（単位: mm）

座標系（全階共通）:
  x : 正面道路（Y1通り側）の内壁面を 0 とし、奥（Y8側）へ +
  y : コア側の内壁面を 0 とし、X1通り側（北面窓側）へ +
1Fの貸室原点は CAD 座標 (9750, 14750)、4・5Fの原点は CAD 座標 (9750, 12700) を想定。
"""
import json

CAD_ORIGIN = {"1F": (9750, 14750), "4F": (9750, 12700), "5F": (9750, 12700)}

# 通り芯（CAD座標から換算）
GRID_Y = {f"Y{i+1}": 11458 + 2700 * i - 9750 for i in range(8)}  # x方向位置（貸室座標）
GRID_X_CAD = {"X3": 8029, "X2": 11529, "X1": 21329}


def R(id, name, x0, y0, x1, y1, kind="room", doors=(), sub=None, label=True, lp=None):
    """kind: treat / room / mri / open / service / core / corridor"""
    return dict(id=id, name=name, x0=x0, y0=y0, x1=x1, y1=y1, kind=kind,
                doors=[dict(side=d[0], at=d[1], w=d[2], type=(d[3] if len(d) > 3 else "slide"))
                       for d in doors],
                sub=sub, label=label, lp=lp)


# ---------------------------------------------------------------- 1F
F1_W, F1_D = 13900, 6550
F1 = dict(
    floor="1F", W=F1_W, D=F1_D, ch=3700, partition_h=2700,
    title="1階 平面計画図（診察・処置・MRI・受付待合）",
    rooms=[
        R("vest", "エントランス\n（既設アプローチ）", 0, 4950, 1900, F1_D, "existing", lp=(950, 5300)),
        R("ex", "診察室", 5000, 4100, 8000, F1_D, "room", doors=[("S", 6500, 900)], lp=(6300, 6050)),
        R("tr", "処置室", 5000, 0, 8000, 2900, "room", doors=[("N", 6500, 1000)], lp=(6500, 2350)),
        R("op", "MRI操作室", 8000, 0, 10000, 2900, "room", doors=[("N", 9000, 800)], lp=(9000, 900)),
        R("mech", "MRI機械室", 8000, 4100, 10000, F1_D, "service", doors=[("S", 9000, 800, "swing")]),
        R("mri", "MRI室\n（磁気シールド）", 10000, 0, F1_W, F1_D, "mri",
          doors=[("W", 3500, 1200, "swing")], lp=(11000, 1500)),
        R("corr", "廊下", 5000, 2900, 10000, 4100, "corridor", label=True),
        R("wait", "待合", 0, 0, 3900, 4950, "open", lp=(1500, 4150)),
    ],
    reception=dict(cx=4500, cy=5350, r=1200, a0=100, a1=260, back=(4600, 4250, 4950, 6450)),
    chairs=[(x, y, 90) for x in (800, 1750, 2700) for y in (1000, 2000, 3000)],
    openings=[  # 既設開口（外壁）
        dict(side="W", a=1550, b=3250, kind="window", note="道路側ガラス面（サイン規制範囲）"),
        dict(side="E", a=250, b=4950, kind="window", note="駐車場側ガラス"),
    ],
    entrances=[dict(side="S", at=3250, w=800, note="館内側出入口（既設SD-27）"),
               dict(side="X", at=(1900, 5750), w=1200, note="アプローチ扉")],
    columns=[(GRID_Y[k], F1_D) for k in ("Y1", "Y2", "Y3", "Y4", "Y5")],
)

# ---------------------------------------------------------------- 4F / 5F 共通
UW, UD = 23000, 8600
ROW_Y0 = 6100          # 窓側施術室列の手前
AISLE_Y0 = 4900        # 通路
ROOM_W = 2550
COR_Y1 = 1400          # 避難経路（EVホール～階段附室）


def window_row(prefix):
    rooms = []
    for i in range(9):
        x0 = i * ROOM_W
        rooms.append(R(f"{prefix}{i+1:02d}", f"施術室\n{prefix}{i+1:02d}", x0, ROW_Y0, x0 + ROOM_W, UD,
                       "treat", doors=[("S", x0 + ROOM_W / 2, 900)]))
    return rooms


CORE = [  # 共用部（コア）想定：1F CAD・マイソク平面より
    R("st", "特別避難階段", 4550, -5100, 7050, 0, "core"),
    R("ev1", "乗用EV", 7150, -2600, 9650, 0, "core"),
    R("evh", "EVホール", 9750, -5100, 12350, 0, "core"),
    R("ev2", "非常用EV", 12450, -2600, 14650, 0, "core"),
    R("wc", "共用トイレ\n（男女別）", 14850, -5100, 19950, 0, "core"),
    R("ps", "PS・EPS／\nメンテ階段", 20050, -5100, UD * 0 + UW, 0, "core"),
]

F4 = dict(
    floor="4F", W=UW, D=UD, ch=2800, partition_h=2300,
    title="4階 平面計画図（受付・待合・更衣室・施術室）",
    rooms=window_row("4") + [
        R("cor", "避難経路（廊下状）", 4550, 0, 12350, COR_Y1, "corridor"),
        R("lm", "更衣室（男性）", 0, 0, 2800, 2300, "room", doors=[("E", 1150, 800)]),
        R("lw", "更衣室（女性）", 0, 2300, 2800, AISLE_Y0, "room", doors=[("E", 3600, 800)]),
        R("pw", "パウダー\nコーナー", 2800, 0, 4550, AISLE_Y0, "open", lp=(3900, 3300)),
        R("cs", "カウンセリング室", 4550, COR_Y1, 7300, AISLE_Y0, "room", doors=[("E", 3800, 900)]),
        R("w1", "待合", 7300, COR_Y1, 10000, AISLE_Y0, "open", lp=(8750, 4500)),
        R("w2", "待合", 12600, 0, 17600, AISLE_Y0, "open", lp=(15100, 3900)),
        R("st4", "スタッフ\nステーション", 17600, 0, 20300, AISLE_Y0, "service", doors=[("N", 18950, 900)]),
        R("sp4", "物品・\nリネン庫", 20300, 0, UW, AISLE_Y0, "service", doors=[("N", 21650, 900)]),
        R("ais", "", 0, AISLE_Y0, UW, ROW_Y0, "open", label=False),
    ],
    reception=dict(cx=11300, cy=3250, r=1150, a0=195, a1=345, back=(10100, 4250, 12500, 4650)),
    chairs=[(x, y, 180) for x in (13300, 14300, 15300, 16300) for y in (1000,)] +
           [(x, y, 180) for x in (13300, 14300, 15300, 16300) for y in (2300,)] +
           [(x, y, 90) for x in (7900, ) for y in (2200, 3200, 4200)] +
           [(x, y, 270) for x in (9600,) for y in (2200, 3200)],
    entrances=[dict(side="CORE", at=11275, w=1600, note="自動ドア（エントランス）")],
    columns=[(GRID_Y[k], UD) for k in GRID_Y],
    openings=[dict(side="W", a=300, b=UD - 300, kind="window"), dict(side="N", a=300, b=UW - 300, kind="window")],
    core=CORE,
)

F5 = dict(
    floor="5F", W=UW, D=UD, ch=2800, partition_h=2300,
    title="5階 平面計画図（施術室・フリースペース・スタッフ休憩室）",
    rooms=window_row("5") + [
        R("cor", "避難経路（廊下状）", 4550, 0, 12350, COR_Y1, "corridor"),
        R("sr", "スタッフ休憩室", 0, 0, 4550, AISLE_Y0, "room", doors=[("N", 3700, 900)]),
        R("sl", "スタッフ\n更衣室", 4550, COR_Y1, 7300, AISLE_Y0, "room", doors=[("N", 6400, 800)]),
        R("fs", "フリースペース", 7300, COR_Y1, 15500, AISLE_Y0, "open", lp=(12300, 4500)),
        R("fs0", "", 12350, 0, 15500, COR_Y1, "open", label=False),
        R("510", "施術室\n510", 15500, 2300, 18100, AISLE_Y0, "treat", doors=[("N", 16800, 900)]),
        R("ln5", "リネン・\n洗濯室", 15500, 0, 18100, 2300, "service", doors=[("W", 1150, 800)]),
        R("of5", "事務室", 18100, 0, 20800, AISLE_Y0, "room", doors=[("N", 19450, 900)]),
        R("sp5", "物品庫", 20800, 0, UW, AISLE_Y0, "service", doors=[("N", 21900, 900)]),
        R("ais", "", 0, AISLE_Y0, UW, ROW_Y0, "open", label=False),
    ],
    reception=None,
    chairs=[],
    lounge=dict(x0=7800, y0=1900, x1=15000, y1=4500),
    entrances=[dict(side="CORE", at=11275, w=1600, note="自動ドア（スタッフ・患者）")],
    columns=[(GRID_Y[k], UD) for k in GRID_Y],
    openings=[dict(side="W", a=300, b=UD - 300, kind="window"), dict(side="N", a=300, b=UW - 300, kind="window")],
    core=CORE,
)

FLOORS = {"1F": F1, "4F": F4, "5F": F5}


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) / 1e6


def treat_count():
    return {k: sum(1 for r in f["rooms"] if r["kind"] == "treat") for k, f in FLOORS.items()}


if __name__ == "__main__":
    import sys
    json.dump(FLOORS, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    print(treat_count())
