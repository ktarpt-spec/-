"""貸主様式「出店企画書」(xls→xlsx変換済) に記入する。 usage: fill_xlsx.py <template.xlsx> <out.xlsx>"""
import sys
import openpyxl
from openpyxl.styles import Alignment, PatternFill, Font
from geometry import treat_count

src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src)
ws = wb.active
TODO = PatternFill("solid", fgColor="FFF4C2")
WRAP = Alignment(wrap_text=True, vertical="center")
tc = treat_count()
N = tc["4F"] + tc["5F"]


def put(cell, value, todo=False, merge=None, size=None):
    if merge:
        ws.merge_cells(merge)
    c = ws[cell]
    c.value = value
    c.alignment = WRAP
    if size:
        c.font = Font(name=c.font.name, size=size)
    if todo:
        c.fill = TODO


put("F2", "2026年　10月　　日", todo=True)
put("E4", "【要記入】", todo=True, merge="E4:G4")
put("E5", "【要記入】", todo=True, merge="E5:G5")
put("E6", "【要記入】", todo=True, merge="E6:G6")

put("C8", "fukka（フッカ）日本橋院（仮称）", merge="C8:G8")
put("C9", "医療機関（診療所）＋個室施術フロア\n1F（約29.75坪）：診察・処置・MRI検査／4・5F（各約69.53坪）：施術（個室%d室）　※診療科目【要記入】" % N,
    todo=True, merge="C9:G9", size=9)
put("C10", "日本橋・東京駅周辺に勤務するオフィスワーカー（30～60代男女）、近隣居住者、\n銀座院の既存ご利用者のうち東京駅・日本橋方面からの来院者", merge="C10:G10", size=9)
put("C11", "診察・検査（MRI）、処置、個室での施術（予約制）", merge="C11:G11", size=9)

rows = [
    ("診察・検査（MRI）", "1F診察室・MRI室。予約制で待ち時間を抑えた検査導線"),
    ("処置", "1F処置室。診察後にそのまま処置へ移れる配置"),
    ("施術（個室）", f"4・5F 個室施術室{N}室。銀座院と同一の内装・運営"),
    ("物販（必要に応じ）", "受付周りでのアフターケア用品の案内のみ"),
]
for i, (name, feat) in enumerate(rows):
    r = 14 + i
    put(f"B{r}", name, size=9)
    put(f"C{r}", "", todo=True)
    put(f"D{r}", feat, merge=f"D{r}:E{r}", size=8)
    put(f"F{r}", "【要記入】", todo=True, merge=f"F{r}:G{r}", size=9)

put("C19", "銀座院の内装（白い塗り壁・木目・ベージュ系カーペット、中央の円形受付カウンター）を踏襲し、"
           "規模を拡大して施術ブースを増設（4F・5F 各10室、各約4畳）。4Fは受付を中央に大きく配置した開放的なロビー。\n"
           "■添付：内観パース（P.9～11）、平面図 A-01（1F・P.4）・A-02（4F・P.5）・A-03（5F・P.6）、仕上表（P.12）",
    size=9)
put("C20", "貸主様のご意向に沿い、看板を目立たせない落ち着いた外観とします。"
           "ビル指定のサイン位置（S1・S2）に店名ロゴのみ表示し、1F正面は木調ルーバー越しの電球色の間接光に留めます。\n"
           "■添付：外観パース（P.8）、立面図 A-04（P.7・サイン位置・使用素材明記）、平面図 A-01",
    size=9)
put("C21", "1F：MRI装置（磁気シールド工事・専用電源・空調／チラー）、診察・処置用医療機器\n"
           f"4・5F：施術ベッド{N}台、受付カウンター、更衣ロッカー、5F：スタッフ休憩室（ミニキッチン）・スタッフ更衣室・物品庫",
    size=9)
put("C22", "【要記入】（例：平日 10:00～20:00／土日祝 10:00～18:00）", todo=True)
put("C23", "【要記入】", todo=True)
put("C24", "【要記入】（参考：施術室%d室×1日稼働枠×稼働率×営業日数×客単価 ＋ 診察・検査収入）" % N, todo=True, size=9)
put("C25", "店舗内装イメージ資料、店舗外装イメージ資料\n"
           "（添付資料.pdf：計画概要、銀座院のご紹介、平面図A-01～03、立面図・サイン計画A-04、外観・内観パース、仕上表・ビル規定対応）", size=9)
put("C26", "【要記入】", todo=True)
put("C27", "・面積：1F 98.36㎡（約29.75坪）、4F・5F 各G229.86㎡（約69.53坪）、合計約168.8坪（募集資料）。図面寸法は実施設計時にビル側図面で確定します。\n"
           "・本ビルは誘導用途区画のため、診療所・施術所用途の適合性を事前にご確認させていただきます。\n"
           "・MRIは床荷重5,000N/㎡の1Fに配置。機種決定後、重量・搬入経路・シールド工事をビル側と協議します。",
    size=8)

for r, h in {9: 36, 10: 36, 11: 30, 14: 30, 15: 30, 16: 30, 17: 30, 19: 72, 20: 80, 21: 44, 24: 36, 25: 40, 27: 70}.items():
    ws.row_dimensions[r].height = h
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.save(out)
print("saved", out)
