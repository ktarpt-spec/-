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
F1 = dict(
    floor="1F", W=F1_W, D=F1_D, ch=3700, partition_h=2700,
    title="1階 平面計画図（受付待合・診察室・処置室・MRI室）",
    # 右上の切欠き（区画外の小室）
    notch=(13030, 4360, F1_W, F1_D),
    rooms=[
        R("vest", "玄関ポーチ\n（既設・道路側開放）", 0, PORCH_Y0, PORCH_X, F1_D, "existing", lp=(890, 5500)),
        R("wait", "待合", 0, 0, 4200, PORCH_Y0, "open", lp=(2300, 3700)),
        R("corr", "廊下", 4200, 2800, 8800, 4000, "hall", lp=(6300, 3400)),
        R("ex", "診察室", 4200, 4000, 6700, F1_D, "room", doors=[("S", 5450, 900)], lp=(5200, 6050),
          sinks=[(4550, 4300)]),
        R("mech", "MRI機械室", 6700, 4000, 8800, F1_D, "service", doors=[("S", 7750, 900, "swing")], lp=(7750, 5900)),
        R("tr", "処置室", 4200, 0, 6300, 2800, "room", doors=[("N", 5250, 1000)], lp=(5250, 2300),
          sinks=[(4500, 300)]),
        R("mch", "MRI更衣\n（1名）", 6300, 0, 7400, 2800, "room", doors=[("N", 6850, 700)], lp=(6850, 1700)),
        R("op", "MRI操作室", 7400, 0, 8800, 2800, "room", doors=[("N", 8100, 700)], lp=(8100, 2200),
          windows=[("E", 400, 2400)]),
        R("mri", "MRI検査室（電磁シールド）", 8800, 0, F1_W, 4360, "mri",
          doors=[("W", 3400, 1200, "swing")], lp=(11300, 650), nowall=["N"], mri_axis="y"),
        R("mri2", "", 8800, 4360, 13030, F1_D, "mri", nowall=["S", "E"], label=False),
    ],
    # 受付：既設扉の内側 1,220mm を空け、正面の木調ロゴ壁の前に配置
    reception=dict(cx=3920, cy=5420, r=920, a0=100, a1=260, back=(3920, 4560, 4200, 6450), depth=430),
    chairs=[(1300, 900, 270), (2200, 900, 270), (3100, 900, 270), (1750, 1900, 270), (2650, 1900, 270)],
    plants=[(3550, 350), (1150, 4150)],
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
             rooms=window_row(floor[0]) + rooms + [AISLE],
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


def east_rooms(n):
    return [R(f"{n}09", f"施術室\n{n}09", 16400, 1900, 18700, AISLE_Y0, "treat", doors=[("N", 17550, 900)]),
            R(f"{n}10", f"施術室\n{n}10", 18700, 1900, UW, AISLE_Y0, "treat", doors=[("N", 19850, 900)])]


F4 = upper("4F", [
    R("hw", "廊下", 0, 0, 5600, 1300, "hall", lp=(4300, 650)), PASS_E,
    R("lm", "更衣室\n（男性）", 0, 1300, COR_X0, AISLE_Y0, "room", doors=[("S", 1300, 800)], lp=(1250, 2700)),
    R("lw", "更衣室（女性）\nパウダー付", COR_X0, 1300, 5600, AISLE_Y0, "room", doors=[("S", 2900, 800)], lp=(3600, 2700)),
    R("lb", "受付・待合ロビー", 5600, 0, 15200, AISLE_Y0, "open", lp=(10100, 600)),
    R("dk", "ドリンク\nコーナー", 16400, 0, 18900, 1900, "open", lp=(17500, 1200)),
    R("cs", "相談室", 18900, 0, UW, 1900, "room", doors=[("W", 950, 800)], lp=(20000, 1400)),
] + east_rooms(4), "4階 平面計画図（受付ロビー・更衣室・施術室10室）",
    reception=dict(cx=10100, cy=3650, r=1450, a0=200, a1=340, back=(8600, 4150, 11600, 4500)),
    chairs=[(6500, 1500, 180), (7450, 1500, 180), (6500, 2600, 180), (7450, 2600, 180),
            (13700, 1500, 0), (12750, 1500, 0), (13700, 2600, 0), (12750, 2600, 0)],
    plants=[(5900, 4100), (14900, 4100), (8300, 600), (11900, 600)])

F5 = upper("5F", [
    R("hw", "廊下", 0, 0, 7600, 1300, "hall", lp=(5600, 650)), PASS_E,
    R("sr", "スタッフ休憩室", 0, 1300, 5000, AISLE_Y0, "room", doors=[("S", 4300, 900)], lp=(4150, 2700)),
    R("slm", "スタッフ\n更衣（男）", 5000, 1300, 6300, AISLE_Y0, "room", doors=[("S", 5650, 700)], lp=(5650, 3900)),
    R("slw", "スタッフ\n更衣（女）", 6300, 1300, 7600, AISLE_Y0, "room", doors=[("S", 6950, 700)], lp=(6950, 3900)),
    R("fs", "フリースペース", 7600, 0, 15200, AISLE_Y0, "open", lp=(11400, 4500)),
    R("sp5", "物品・リネン庫\n（既設キッチン含む）", 16400, 0, UW, 1900, "service", doors=[("W", 950, 800)], lp=(17700, 950)),
] + east_rooms(5), "5階 平面計画図（施術室10室・フリースペース・スタッフ休憩室）",
    lounge=dict(x0=8000, y0=1500, x1=14600, y1=4200),
    plants=[(7900, 4100), (14900, 4100)])

FLOORS = {"1F": F1, "4F": F4, "5F": F5}


def area(r):
    return (r["x1"] - r["x0"]) * (r["y1"] - r["y0"]) / 1e6


def treat_count():
    return {k: sum(1 for r in f["rooms"] if r["kind"] == "treat") for k, f in FLOORS.items()}


if __name__ == "__main__":
    import sys
    json.dump(FLOORS, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    print(treat_count())
