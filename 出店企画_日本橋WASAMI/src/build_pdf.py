"""添付資料（A3横）HTML を組み立てる。 usage: build_pdf.py <outdir>  → <outdir>/添付資料.html"""
import os, sys
from geometry import FLOORS, area, treat_count

out = sys.argv[1]
D = lambda p: open(os.path.join(out, "drawings", p)).read()
tc = treat_count(); N = tc["4F"] + tc["5F"]
FOOT = "fukka 日本橋院（仮称） 出店企画書 添付資料 ／ 日本橋WASAMIビル 1F・4F・5F"

css = """
@page { size: 420mm 297mm; margin: 0 }
* { box-sizing: border-box }
body { margin: 0; font-family: 'IPAGothic', sans-serif; color: #2b2522 }
.pg { width: 420mm; height: 297mm; position: relative; overflow: hidden; page-break-after: always; background: #fff }
.pg > svg { width: 420mm; height: 297mm; display: block }
.frame { position: absolute; inset: 8mm; border: 0.35mm solid #333 }
.hd { position: absolute; left: 16mm; top: 13mm; right: 16mm; display: flex; align-items: baseline; gap: 6mm; border-bottom: 0.5mm solid #9a7b55; padding-bottom: 2.5mm }
.hd h1 { font-size: 7.5mm; margin: 0; letter-spacing: 0.3mm }
.hd .en { font-family: Inter, sans-serif; font-size: 3.6mm; color: #9a7b55; letter-spacing: 0.6mm }
.ft { position: absolute; left: 16mm; right: 16mm; bottom: 11mm; font-size: 2.8mm; color: #888; display: flex; justify-content: space-between }
.body { position: absolute; left: 16mm; right: 16mm; top: 30mm; bottom: 18mm }
.img { position: absolute; overflow: hidden; border-radius: 1.2mm }
.img img { width: 100%; height: 100%; object-fit: cover; display: block }
.cap { position: absolute; font-size: 3.4mm; font-weight: bold }
.cap small { display: block; font-weight: normal; color: #6b625b; font-size: 2.8mm; margin-top: 0.8mm; line-height: 1.5 }
.tag { display: inline-block; background: #9a7b55; color: #fff; font-size: 2.6mm; padding: 0.6mm 2mm; border-radius: 0.8mm; margin-right: 2mm; vertical-align: 0.4mm }
table { border-collapse: collapse; width: 100%; font-size: 3.1mm }
th, td { border: 0.25mm solid #c9c0b5; padding: 1.6mm 2.2mm; text-align: left; vertical-align: top; line-height: 1.45 }
th { background: #f3ede4; font-weight: bold; white-space: nowrap }
.note { font-size: 2.7mm; color: #6b625b; line-height: 1.6 }
.kpi { display: flex; gap: 4mm }
.kpi div { flex: 1; background: #f6f1e8; border-radius: 1.2mm; padding: 3mm 4mm }
.kpi b { display: block; font-size: 7mm; color: #9a7b55; font-family: Inter, sans-serif }
.kpi span { font-size: 2.9mm }
"""


def page(title, en, inner, no):
    return (f'<div class="pg"><div class="frame"></div><div class="hd"><h1>{title}</h1><span class="en">{en}</span></div>'
            f'<div class="body">{inner}</div><div class="ft"><span>{FOOT}</span><span>{no}</span></div></div>')


def img(src, x, y, w, h):
    return f'<div class="img" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm"><img src="images/{src}"></div>'


def cap(x, y, w, t, s, tag=""):
    tg = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<div class="cap" style="left:{x}mm;top:{y}mm;width:{w}mm">{tg}{t}<small>{s}</small></div>'


pages = []
# 1. 表紙
pages.append(f'''<div class="pg" style="background:#f6f1e8">
<div class="img" style="left:0;top:0;width:250mm;height:297mm;border-radius:0"><img src="images/v4_lobby.png"></div>
<div style="position:absolute;left:268mm;top:46mm;right:20mm">
 <div style="font-family:Inter,sans-serif;color:#9a7b55;letter-spacing:1mm;font-size:4mm">STORE OPENING PROPOSAL</div>
 <div style="font-size:12mm;font-weight:bold;margin-top:6mm;line-height:1.3">出店企画書<br>添付資料</div>
 <div style="font-family:Inter,sans-serif;font-size:15mm;color:#24418f;margin-top:16mm;font-weight:500">fukka</div>
 <div style="font-size:5.2mm;margin-top:2mm">日本橋院（仮称）</div>
 <div style="margin-top:16mm;font-size:3.6mm;line-height:1.9;border-top:0.4mm solid #9a7b55;padding-top:5mm">
  物件：日本橋WASAMIビル（東京都中央区日本橋三丁目）<br>計画区画：1階 店舗区画（約99.7㎡）<br>　　　　　4階・5階（募集面積 G229.86㎡）<br>
  内容：平面計画図・立面図・サイン計画・外観／内観イメージ・仕上表<br>2026年10月　基本計画</div>
</div></div>''')

# 2. 計画概要
fl_rows = ""
for k, f in FLOORS.items():
    items = "、".join(dict.fromkeys(r["name"].replace("\n", "") for r in f["rooms"]
                                     if r["name"] and r["kind"] not in ("corridor", "existing") and not r["name"].startswith("施術室")))
    t = f"施術室 {tc[k]}室、" if tc[k] else ""
    fl_rows += f"<tr><th>{k}</th><td>{t}{items}</td></tr>"
overview = f'''
<div style="position:absolute;left:0;top:0;width:180mm">
 <div class="kpi"><div><b>3</b><span>フロア（1F・4F・5F）</span></div><div><b>{N}</b><span>施術室（4F {tc["4F"]}室＋5F {tc["5F"]}室）</span></div><div><b>1</b><span>MRI室（1F）</span></div></div>
 <h3 style="font-size:4.2mm;margin:7mm 0 2.5mm">コンセプト</h3>
 <p style="font-size:3.3mm;line-height:1.75;margin:0">銀座院の空間（白い塗り壁、木目、ベージュ系カーペット、中央の円形受付と木の天井リング）をそのまま拡大し、
 施術ブースを増やした「銀座院の大型版」として計画します。1階は道路から直接入れる既設アプローチを活かした医療フロア（診察・処置・MRI）、
 4階は受付・待合・更衣と施術室、5階は施術室とフリースペース・スタッフエリアとしています。</p>
 <h3 style="font-size:4.2mm;margin:7mm 0 2.5mm">フロア構成</h3>
 <table>{fl_rows}</table>
 <h3 style="font-size:4.2mm;margin:7mm 0 2.5mm">動線</h3>
 <p style="font-size:3.1mm;line-height:1.7;margin:0">新規・検査の患者：道路 → 1F専用アプローチ → 受付 → 診察・MRI<br>
 施術の利用者：ビルEV → 4F受付 → 更衣室 → 4F／5F施術室（EV移動）<br>
 スタッフ：5F休憩室・更衣室・事務室を拠点に各階へ</p>
</div>
{img("ax4.png", 190, 0, 198, 116)}{cap(192, 117, 190, "4F 俯瞰（受付・待合・更衣・施術室）", "", "4F")}
{img("ax5.png", 190, 128, 96, 98)}{cap(192, 228, 94, "5F 俯瞰", "", "5F")}
{img("ax1.png", 292, 128, 96, 98)}{cap(294, 228, 94, "1F 俯瞰", "", "1F")}
'''
pages.append(page("計画概要", "PLAN OVERVIEW", overview, "P.2"))

# 3-6 図面
for i, name in enumerate(["plan_1F.svg", "plan_4F.svg", "plan_5F.svg", "elevation_front.svg"]):
    pages.append(f'<div class="pg">{D(name)}<div class="ft" style="bottom:3mm"><span></span><span>P.{3+i}</span></div></div>')

# 7 外観
ext = f'''{img("ext.png", 0, 0, 236, 148)}{img("ext_entry.png", 242, 0, 146, 91)}
{cap(0, 152, 236, "正面（Y1通り）外観イメージ", "既設の外装はそのまま、当社の表示は1F専用アプローチ奥の木調壁ロゴ、SSW-2ガラス奥の木調ルーバー、ビル共用案内板（S1）のみ。突出看板・ガラス面広告は設けません。", "外装")}
{cap(242, 94, 146, "1F 専用アプローチまわり", "木調パネル＋アイボリーのロゴ（リースライン内）。照明は電球色の間接光のみで、夜間もまぶしさが出ない計画です。", "外装")}
{cap(242, 130, 146, "サイン表示（合計 約0.35㎡）", "S1 ビル案内板：ロゴのみ／S2 ビル指定位置：W300角プレート／1F窓：600mm後退ルーバー上の小型ロゴ（非照明）／4・5F窓：表示なし（ロールスクリーンのみ）")}
'''
pages.append(page("外装イメージ", "EXTERIOR IMAGE", ext, "P.7"))

# 8 1F
p1 = f'''{img("v1_lobby.png", 0, 0, 236, 148)}{img("v1_mri.png", 242, 0, 146, 91)}{img("ax1.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "1F 受付・待合", "道路側アプローチから入ると正面に円形受付。銀座院と同じ木の天井リングと木目のロゴ壁。道路側ガラス面の内側は600mm後退した木調ルーバーで外からの視線をやわらげます。", "1F")}
{cap(242, 94, 146, "MRI室", "磁気シールド工事を行う独立区画。操作室から観察窓で確認。", "1F")}
{cap(242, 222, 146, "1F 俯瞰", "受付待合／診察・処置／MRI（操作室・機械室）", "1F")}
'''
pages.append(page("内装イメージ　1階（診察・処置・MRI・受付待合）", "INTERIOR IMAGE 1F", p1, "P.8"))

# 9 4F
p4 = f'''{img("v4_lobby.png", 0, 0, 236, 148)}{img("v4_aisle.png", 242, 0, 146, 91)}{img("v4_room.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "4F 受付・待合（フロア中央の受付）", "EVホールから自動ドアを入ると正面に受付。銀座院と同じ円形カウンター、木の天井リング、棚とロゴ壁の構成を拡大して再現しています。", "4F")}
{cap(242, 94, 146, "施術室前の通路", "窓側に施術室を並べ、木目の引戸と白い壁で統一。", "4F")}
{cap(242, 222, 146, "施術室（約6.4㎡）", "ベッド・スツール・荷物かご・棚。窓側で自然光を確保。", "4F")}
'''
pages.append(page("内装イメージ　4階（受付・待合・更衣室・施術室）", "INTERIOR IMAGE 4F", p4, "P.9"))

# 10 5F
p5 = f'''{img("v5_free.png", 0, 0, 236, 148)}{img("ax5.png", 242, 0, 146, 91)}{img("ginza_ref.jpg", 242, 128, 146, 91)}
{cap(0, 152, 236, "5F フリースペース", "施術前後の待合、カウンセリング、小規模セミナーに使えるラウンジ。造作ベンチと丸テーブルで、銀座院と同じ素材・色を使います。", "5F")}
{cap(242, 94, 146, "5F 俯瞰", f"施術室{tc['5F']}室／フリースペース／スタッフ休憩室・更衣室・事務室", "5F")}
{cap(242, 222, 146, "参考：銀座院（既存）", "トーン＆マナーはこの内装を基準にしています。", "参考")}
'''
pages.append(page("内装イメージ　5階（施術室・フリースペース・スタッフ休憩室）", "INTERIOR IMAGE 5F", p5, "P.10"))

# 11 仕上表・ビル規定対応
fin = [
    ("床", "タイルカーペット（防炎品・ベージュ系、銀座院同等柄）／MRI室・処置室：ビニル床シート", "OAフロア（4・5F）上に施工"),
    ("巾木", "ソフト巾木 H60（ベージュ）", ""),
    ("壁", "LGS＋PB12.5（不燃）下地　AEP塗装（白・塗り壁調）／受付背面：木目調不燃化粧板", "施術室間仕切は上部開放の欄間式（欄間 h=500）"),
    ("天井", "既設天井（4・5F CH2,800）／1F：PB下地 AEP（CH約3,000）　受付上部：木目調リング（不燃）", "既設防災設備（感知器・SP・非常照明）を活かす"),
    ("建具", "施術室：木目調不燃化粧板 引戸 W900×H2,100／エントランス：ガラス自動ドア", "鍵1本をビル側へお預け"),
    ("家具", "受付カウンター（木目＋白天板）、待合チェア（ベージュ張地・木脚）、施術ベッド", "家具は防炎・難燃材料を優先"),
    ("照明", "LEDライン照明・ダウンライト（電球色～温白色 3000～3500K、調光）", "ビル電源容量内（1Φ約100VA/㎡、3Φ約200VA/㎡）"),
    ("カーテン等", "窓：防炎ロールスクリーン（アイボリー）", "防炎ラベル縫付"),
    ("MRI室", "磁気シールド・RFシールド工事（専門業者）、専用電源・空調・チラー", "床荷重・搬入経路・振動対策をビル側と協議"),
]
fr = "".join(f"<tr><th>{a}</th><td>{b}</td><td class='note'>{c}</td></tr>" for a, b, c in fin)
rules = [
    ("床荷重", "1F 5,000N/㎡、4・5F 3,000N/㎡。重量物（MRI）は1Fに配置"),
    ("間仕切", "不燃材使用。欄間式とし、防災設備の追加が必要な場合はB工事で対応"),
    ("避難経路", "2～5F：EVホール～避難階段附室を廊下状に整備。防火扉の開閉を妨げる造作なし"),
    ("ファサード", "既設サッシ・ガラスは無加工、ガラス面から600mm以上離隔"),
    ("サイン", "ビル指定場所（S1・S2）のみ。点滅・映像・赤色光・ネオン不使用、店名ロゴのみ"),
    ("設備", "空調・電源は基準容量内。給排水（診察室・処置室の手洗い）は区画内の排水位置から計画、必要に応じ防水・漏水検知"),
    ("用途", "誘導用途区画のため診療所・施術所としての適合性を事前確認"),
    ("提出図書", "B工事指示書・基本設計図書：着工2.5か月前／実施設計図・工事申請書：着工1か月前"),
]
rr = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rules)
p11 = f'''<div style="position:absolute;left:0;top:0;width:220mm"><h3 style="font-size:4.2mm;margin:0 0 3mm">仕上表（概略・基本計画段階）</h3>
<table><tr><th>部位</th><th>仕上</th><th>備考</th></tr>{fr}</table></div>
<div style="position:absolute;left:230mm;top:0;width:158mm"><h3 style="font-size:4.2mm;margin:0 0 3mm">内装マニュアル（ビル規定）への対応</h3>
<table>{rr}</table>
<p class="note" style="margin-top:5mm">※本資料は出店審査用の基本計画です。寸法・面積は募集資料および1F CADからの想定値で、
実施設計時にビル側の白図・設備図に基づき確定します。パースはイメージで、実際の仕上・家具とは異なる場合があります。</p></div>'''
pages.append(page("仕上表・ビル規定への対応", "FINISH SCHEDULE / COMPLIANCE", p11, "P.11"))

html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(pages)}</body></html>'
open(os.path.join(out, "添付資料.html"), "w").write(html)
print("pages", len(pages))
