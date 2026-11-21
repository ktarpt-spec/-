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
from finance import model
fin = model()[2]
rent_p, op_p, ad_p = (fin[k] / fin['sales'] * 100 for k in ('rent', 'op', 'ad'))


def put(cell, value, todo=False, merge=None, size=None):
    if merge and merge not in {str(r) for r in ws.merged_cells.ranges}:
        ws.merge_cells(merge)
    c = ws[cell]
    c.value = value
    c.alignment = WRAP
    if size:
        c.font = Font(name=c.font.name, size=size)
    if todo:
        c.fill = TODO


EST = PatternFill("solid", fgColor="EAF2E3")   # 市場平均による概算（緑）

put("F2", "2026年　10月　12日")
put("E4", "福岡県福岡市中央区赤坂1丁目14番35号 赤坂門AIビル5階", merge="E4:G4", size=9)
put("E5", "株式会社ふっか", merge="E5:G5")
put("E6", "代表取締役　松田 圭太", merge="E6:G6")

put("C8", "1階：整形外科ふっか 東京駅院　／　4・5階：整痛院ふっか 東京駅院", merge="C8:G8", size=10)
put("C9", "1階：整形外科（診察・処置）\n"
          "4・5階：痛み・しびれ専門の整痛院（評価・モビライゼーション・運動療法・認知アプローチ／完全予約制）",
    merge="C9:G9", size=9)
put("C10", "腰痛・肩こり・坐骨神経痛など慢性的な痛み・しびれに悩む40～70代の男女。\n"
           "日本橋・東京駅周辺のオフィスワーカー、近隣居住者、出張・来訪者、銀座院の既存利用者", merge="C10:G10", size=9)
put("C11", "整痛施術（独自のMSMメソッド：手技・運動療法）、整形外科の診察・処置、セルフケア用品", merge="C11:G11", size=9)

rows = [  # 品目, ％, 特徴, 価格帯（＊は市場平均による概算）
    ("整痛施術（個室）", "70", f"4F 運動室{N}室・5F 評価室3室・認知室4室。予約制（30分枠：モビライゼーション15分＋運動15分）",
     "痛み消失コース（6ヶ月）880,000円（税込）\n理想の体コース（12ヶ月）1,320,000円（税込）"),
    ("診察", "15", "1F 診察室4室。痛みの原因を診察し、施術方針を説明",
     "自費診療 3,000～9,000円"),
    ("処置", "13", "1F 処置室3室。注射・物理療法等の処置",
     "自費診療 3,000～15,000円＊"),
    ("物販", "2", "セルフケア用品・サポーター等（受付で案内）", "3,000円〜20,000円"),
]
for i, (name, pct, feat, price) in enumerate(rows):
    r = 14 + i
    put(f"B{r}", name, size=9)
    put(f"C{r}", pct + "%", size=9)
    ws[f"C{r}"].fill = EST
    put(f"D{r}", feat, merge=f"D{r}:E{r}", size=8)
    put(f"F{r}", price, merge=f"F{r}:G{r}", size=8)
    if "＊" in price:
        ws[f"F{r}"].fill = EST

put("C19", "銀座院の内装（白い塗り壁・木目・ベージュ系カーペット、中央の円形受付カウンターと木の天井リング）を踏襲し、"
           "10億モデル店舗として、4Fに受付・待合（12～24名）・運動室13室（各約7.2㎡：ベッド・鏡2面・ホワイトボード）・女性更衣室、5Fに評価室3室（各18㎡）・認知室4室・撮影室・フリースペース（ジム予定）・スタッフルームを配置。1Fは玄関（既設扉）正面に受付、道路側ガラス面の内側に木調縦ルーバーを設けた待合とし、診察室4室・処置室3室を同じ素材感でまとめる。\n"
           "■添付：内観パース（P.9～11）、平面図 A-01（1F・P.3）・A-02（4F・P.4）・A-03（5F・P.5）、仕上表（P.14）",
    size=9)
put("C20", "貸主様のご意向に沿い、看板を目立たせない落ち着いた外観とします。"
           "ビル指定のサイン位置（S1・S2）に店名ロゴのみ表示します。1F玄関ポーチ・道路側ガラス面（約4.5m）・サッシは既設のまま無加工とし、"
           "ガラス面の600mm内側に木調縦ルーバー（電球色の間接光）を設けます。玄関は既設SUS両開き扉越しに受付の木調ロゴ壁が見える控えめな表現です。\n"
           "■添付：外観パース（P.8）、立面図 A-04（P.6・サイン位置・使用素材明記）、1F玄関ポーチ・ガラス面詳細図 A-05（P.7）、平面図 A-01",
    size=9)
put("C21", "1F：受付カウンター、待合いす15席、診察室4室（診察デスク・診察台・電子カルテ）、処置室3室（処置ベッド・器材棚・物理療法機器）、"
          "全室に手洗い器、スタッフ室\n"
           f"4F：受付カウンター、待合12席、運動室{N}室（ベッド・姿勢鏡2面・ホワイトボード）、女性更衣ロッカー・パウダー\n"
           "5F：評価室3室（ベッド・スライド式姿勢鏡・ホワイトボード）、認知室4室、撮影室（歩行撮影）、ジム（トレーニング機器・マット・ミラー）、スタッフルーム（キッチン）・ロッカー40",
    size=9)
put("C22", "7:00～23:00 予定（30分枠）　※ビル開館7:00～22:00、22時以降はセキュリティカードで入退館", size=9)
put("C23", "不定休（年末年始を除き原則無休）")
ws["C23"].fill = EST
put("C24", f"最終月商 {fin['sales']:,}万円（3年目・年商 約{fin['sales'] * 12 / 10000:.0f}億円：整形外科 月3,000万円＋整痛院 月7,000万円）予定　※賃料比率 約{rent_p:.0f}%・営業利益率 約{op_p:.0f}%：別シート「収支計画」／添付資料P.12参照", size=9)
put("C25", "店舗内装イメージ資料、店舗外装イメージ資料\n"
           "（添付資料.pdf：計画概要、平面図A-01～03、立面図・サイン計画A-04、1F玄関ポーチ・ガラス面詳細A-05、外観・内観パース、収支計画、銀座院のご紹介、仕上表・ビル規定対応）\n"
           "補足資料（審査ご確認事項への回答）.pdf：契約・開設の関係、設計施工の体制図・質疑応答ルール、許認可一覧・工程", size=9)
put("C26", "松田 圭太\nTEL：090-5386-3810　Mail：kta@medicalbookjapan.co.jp", size=9)
put("C27", "・面積：1F 98.36㎡（約29.75坪）、4F・5F 各G229.86㎡（約69.53坪）、合計約168.8坪（募集資料）。図面寸法は実施設計時にビル側図面で確定します。\n"
           "・賃借は株式会社ふっかが1・4・5階を一括で行い、1階は診療所開設者の一般社団法人福十字へ転貸します（借室申込書・補足資料参照）。\n"
           "・本ビルは誘導用途区画のため、診療所・施術所用途の適合性を事前にご確認させていただきます。\n"
           f"・賃料比率（最終月商比 約{rent_p:.0f}%）は、駅徒歩1分の立地による広告費の圧縮（売上比 約{ad_p:.0f}%）と自費100%による粗利率 約94%で吸収し、営業利益率 約{op_p:.0f}%を見込みます（収支計画参照）。\n"
           "・緑色セル（＊）は市場平均等による概算値です（構成比・休日・処置の価格帯）。",
    size=8)

for r, h in {9: 36, 10: 36, 11: 30, 14: 34, 15: 34, 16: 30, 17: 30, 19: 80, 20: 92, 21: 76, 24: 33, 25: 52, 26: 36, 27: 112}.items():
    ws.row_dimensions[r].height = h
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.save(out)
print("saved", out)
