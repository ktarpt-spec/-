"""添付資料（A3横）HTML を組み立てる。 usage: build_pdf.py <outdir>  → <outdir>/添付資料.html"""
import os, sys
from geometry import FLOORS, AREA, area, treat_count

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
.ph { position: absolute; border: 0.4mm dashed #b9ab98; border-radius: 1.2mm; background: #faf7f2; color: #9a8b78; font-size: 3mm; display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.6 }
.card { position: absolute; background: #f6f1e8; border-radius: 1.2mm; padding: 3mm 4mm }
.card b { display: block; font-size: 6.5mm; color: #9a7b55; font-family: Inter, 'IPAGothic', sans-serif; margin-top: 1mm }
.card span { font-size: 2.8mm; color: #6b625b }
.todo { color: #b5523b !important; font-size: 4.2mm !important }
"""


def page(title, en, inner, no):
    return (f'<div class="pg"><div class="frame"></div><div class="hd"><h1>{title}</h1><span class="en">{en}</span></div>'
            f'<div class="body">{inner}</div><div class="ft"><span>{FOOT}</span><span>{no}</span></div></div>')


def img(src, x, y, w, h, d="images_bl"):
    return f'<div class="img" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm"><img src="{d}/{src}"></div>'


def cap(x, y, w, t, s, tag=""):
    tg = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<div class="cap" style="left:{x}mm;top:{y}mm;width:{w}mm">{tg}{t}<small>{s}</small></div>'


def absimg(src, x, y, w, h, d="images_bl", r=0):
    return f'<div class="img" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;border-radius:{r}mm"><img src="{d}/{src}"></div>'


pages = []
# ---------------------------------------------------------------- 1. 表紙（外観＋内観）
m1, t1 = AREA["1F"]; m4, t4 = AREA["4F"]
pages.append(f"""<div class="pg" style="background:#f4efe6">
{absimg("ext.png", 0, 0, 262, 168)}
{absimg("v4_lobby.png", 0, 170, 130, 127)}{absimg("v1_lobby.png", 132, 170, 130, 127)}
<div style="position:absolute;left:4mm;top:156mm;background:rgba(40,34,30,.62);color:#fff;font-size:3mm;padding:1.2mm 3mm;border-radius:0.8mm">外観イメージ（正面・1F専用アプローチ）</div>
<div style="position:absolute;left:4mm;top:286mm;background:rgba(40,34,30,.62);color:#fff;font-size:3mm;padding:1.2mm 3mm;border-radius:0.8mm">4F 受付ロビー</div>
<div style="position:absolute;left:136mm;top:286mm;background:rgba(40,34,30,.62);color:#fff;font-size:3mm;padding:1.2mm 3mm;border-radius:0.8mm">1F 受付・待合</div>
<div style="position:absolute;left:276mm;top:30mm;right:18mm">
 <div style="font-family:Inter,sans-serif;color:#9a7b55;letter-spacing:1mm;font-size:3.6mm">STORE OPENING PROPOSAL</div>
 <div style="font-size:11mm;font-weight:bold;margin-top:5mm;line-height:1.3">出店企画書<br>添付資料</div>
 <div style="font-family:Inter,sans-serif;font-size:15mm;color:#24418f;margin-top:12mm;font-weight:500">fukka</div>
 <div style="font-size:5mm;margin-top:1mm">日本橋院（仮称）</div>
 <div style="margin-top:10mm;font-size:3.3mm;line-height:1.95;border-top:0.4mm solid #9a7b55;padding-top:4mm">
  物件：日本橋WASAMIビル<br>　　　東京都中央区日本橋三丁目（JR東京駅 徒歩1分）<br>
  1階：店舗区画 {m1}㎡（約{t1}坪）<br>4階・5階：各 G{m4}㎡（約{t4}坪）<br>合計：約168.8坪／施術室 {N}室・MRI室</div>

 <div style="position:relative;margin-top:8mm;height:58mm;border-radius:1.2mm;overflow:hidden"><img src="images_bl/v5_free.png" style="width:100%;height:100%;object-fit:cover"></div>
 <div style="font-size:2.8mm;color:#6b625b;margin-top:1.5mm">5F フリースペース</div>
 <div style="font-size:3mm;margin-top:6mm;color:#6b625b">2026年10月　基本計画</div>
</div></div>""")

# ---------------------------------------------------------------- 2. 計画概要（各階の写真）
fl_rows = ""
for k, f in FLOORS.items():
    items = "、".join(dict.fromkeys(r["name"].replace("\n", "") for r in f["rooms"]
                                     if r["name"] and r["kind"] not in ("corridor", "existing", "hall") and not r["name"].startswith("施術室")))
    t = f"施術室 {tc[k]}室（各約4畳）、" if tc[k] else ""
    m2, tb = AREA[k]
    fl_rows += f"<tr><th>{k}<br><span style='font-weight:normal;font-size:2.6mm'>{m2}㎡<br>約{tb}坪</span></th><td>{t}{items}</td></tr>"
rows = ""
for i, (fl, ph, ax, ttl, txt) in enumerate([
        ("1F", "v1_lobby.png", "ax1.png", "医療フロア", "道路から直接入れる専用アプローチ。受付待合・診察室・処置室・MRI室（操作室から観察窓）"),
        ("4F", "v4_lobby.png", "ax4.png", "受付・施術フロア", f"EVを降りると正面に円形受付の開放的なロビー。男女更衣室・施術室{tc['4F']}室"),
        ("5F", "v5_free.png", "ax5.png", "施術・スタッフフロア", f"施術室{tc['5F']}室・フリースペース。スタッフ休憩室・更衣室・物品庫を集約")]):
    y = i * 83
    rows += absimg(ph, 134, y, 128, 78) + absimg(ax, 266, y, 122, 78)
    rows += f'<div style="position:absolute;left:136mm;top:{y+2}mm;background:#9a7b55;color:#fff;font-size:3.6mm;font-weight:bold;padding:1mm 3mm;border-radius:0.8mm">{fl}　{ttl}</div>'
    rows += f'<div style="position:absolute;left:136mm;top:{y+70}mm;width:124mm;background:rgba(40,34,30,.6);color:#fff;font-size:2.6mm;padding:1mm 2mm;border-radius:0.6mm">{txt}</div>'
overview = f"""
<div style="position:absolute;left:0;top:0;width:126mm">
 <div class="kpi"><div><b>168.8<small style="font-size:3.5mm">坪</small></b><span>1F {t1}坪＋4F・5F 各{t4}坪</span></div><div><b>{N}</b><span>施術室（各 約4畳）</span></div></div>
 <div class="kpi" style="margin-top:3mm"><div><b>MRI</b><span>1F（床荷重5,000N/㎡）</span></div><div><b>1<small style="font-size:3.5mm">分</small></b><span>JR東京駅（22番出口）徒歩</span></div></div>
 <h3 style="font-size:4.2mm;margin:6mm 0 2mm">コンセプト</h3>
 <p style="font-size:3.1mm;line-height:1.75;margin:0">銀座院の空間（白い塗り壁、木目、ベージュのカーペット、中央の円形受付と木の天井リング）をそのまま拡大し、施術室を増やした「銀座院の大型版」。外観はビルの意匠を活かし、看板を目立たせない落ち着いた表現とします。</p>
 <h3 style="font-size:4.2mm;margin:6mm 0 2mm">フロア構成</h3>
 <table>{fl_rows}</table>
 <h3 style="font-size:4.2mm;margin:5mm 0 2mm">動線</h3>
 <p style="font-size:3mm;line-height:1.7;margin:0">検査・診察：道路 → 1F専用アプローチ → 受付 → 診察・MRI<br>施術：ビルEV → 4F受付 → 更衣室 → 4F／5F施術室<br>スタッフ：5F休憩室・更衣室・物品庫を拠点に各階へ</p>
</div>
{rows}
"""
pages.append(page("計画概要", "PLAN OVERVIEW", overview, "P.2"))

# ---------------------------------------------------------------- 3. 銀座院のご紹介（新規）
ginza = f"""
{absimg("ginza_ref.jpg", 0, 0, 236, 150, d="images")}
{cap(0, 153, 236, "fukka 銀座院（既存）", "日本橋院は、この銀座院の内装・トーン＆マナーをそのまま踏襲して計画しています。", "銀座院")}
<div class="ph" style="left:0;top:172mm;width:116mm;height:72mm">銀座院 外観写真<br>（ご提供いただき差し替え）</div>
<div class="ph" style="left:120mm;top:172mm;width:116mm;height:72mm">銀座院 施術室写真<br>（ご提供いただき差し替え）</div>
<div style="position:absolute;left:244mm;top:0;width:144mm">
 <h3 style="font-size:4.4mm;margin:0 0 3mm">銀座院の運営実績</h3>
</div>
""" + "".join(f'<div class="card" style="left:{244 + (i % 2) * 73}mm;top:{10 + (i // 2) * 30}mm;width:71mm;height:27mm"><span>{k}</span><b class="todo">【要記入】</b><span>{u}</span></div>'
              for i, (k, u) in enumerate([("開院", "年　月"), ("施術室数", "室"), ("月間来院者数", "名／月"), ("会員数・リピート率", "名／％"),
                                          ("月間売上（直近）", "万円"), ("口コミ評価", "Google ★")])) + f"""
<div style="position:absolute;left:244mm;top:104mm;width:144mm">
 <h3 style="font-size:4.2mm;margin:0 0 2mm">銀座院の特長</h3>
 <ul style="font-size:3.1mm;line-height:1.8;margin:0;padding-left:5mm;color:#2b2522">
  <li>【要記入】（例：完全個室の施術室と、白と木目を基調とした落ち着いた空間）</li>
  <li>【要記入】（例：予約制による待ち時間の少ない運営）</li>
  <li>【要記入】（例：医師・有資格スタッフによる施術・検査体制）</li></ul>
 <h3 style="font-size:4.2mm;margin:6mm 0 2mm">日本橋院で目指すこと</h3>
 <p style="font-size:3.1mm;line-height:1.75;margin:0">銀座院で培った運営をもとに、施術室を{N}室に拡大し、1階にMRIを備えた医療フロアを新設。東京駅・日本橋エリアのオフィスワーカーや近隣の方に、同じ品質のサービスを提供します。</p>
 <p class="note" style="margin-top:4mm">※【要記入】欄・写真枠は、数値・写真をご提供いただければ差し替えます。</p>
</div>"""
pages.append(page("銀座院のご紹介", "GINZA CLINIC", ginza, "P.3"))

# ---------------------------------------------------------------- 4-7 図面
for i, name in enumerate(["plan_1F.svg", "plan_4F.svg", "plan_5F.svg", "elevation_front.svg"]):
    pages.append(f'<div class="pg">{D(name)}<div class="ft" style="bottom:3mm"><span></span><span>P.{4+i}</span></div></div>')

# ---------------------------------------------------------------- 8 外装
ext = f"""{img("ext.png", 0, 0, 236, 148)}{img("ext_entry.png", 242, 0, 146, 91)}{img("ext_front.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "正面（Y1通り）外観イメージ", "ビル既設の外装はそのまま。当社の表示は、1F専用アプローチ奥の木調欄間のロゴ、SSW-2ガラス奥（600mm後退）の木調ルーバー上の小型ロゴ、ビル共用案内板（S1）のみ。突出看板・ガラス面広告はありません（立面図 A-04 と同一仕様）。", "外装")}
{cap(242, 94, 146, "1F 専用アプローチまわり", "既設ガラス扉の奥に木調の袖壁・欄間と店名ロゴ。電球色の間接光のみで、夜もまぶしさのない落ち着いた表情です。", "外装")}
{cap(242, 222, 146, "正面全景", "4・5F窓面は内側の防炎ロールスクリーンのみで、サイン表示はありません。")}
"""
pages.append(page("外装イメージ", "EXTERIOR IMAGE", ext, "P.8"))

# ---------------------------------------------------------------- 9 1F
p1 = f"""{img("v1_lobby.png", 0, 0, 236, 148)}{img("v1_mri.png", 242, 0, 146, 91)}{img("v1_op.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "1F 受付・待合", "専用アプローチから入ると正面に円形受付。銀座院と同じ木の天井リングとロゴ壁。待合は少人数でゆったりと。道路側ガラスの内側は600mm後退した木調ルーバーで外からの視線をやわらげます。", "1F")}
{cap(242, 94, 146, "MRI室（平面図A-01と同形状）", "約4.1m×4.4mの独立区画。電磁シールド工事を行い、装置は東側に配置。", "1F")}
{cap(242, 222, 146, "MRI操作室から観察窓越しに", "操作室とMRI室の間に壁を設け、観察窓から検査中の様子を確認できます。", "1F")}
"""
pages.append(page("内装イメージ　1階（受付待合・診察・処置・MRI）", "INTERIOR IMAGE 1F", p1, "P.9"))

# ---------------------------------------------------------------- 10 4F
p4 = f"""{img("v4_lobby.png", 0, 0, 236, 148)}{img("v4_front.png", 242, 0, 146, 91)}{img("v4_room.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "4F 受付ロビー", "EVホールから続く柱・壁のない開放的なロビー。中央に大きな円形受付、木の天井リング、棚とロゴ壁で銀座院の雰囲気を再現。待合いすはゆとりをもって配置。", "4F")}
{img("v4_aisle.png", 0, 176, 116, 72)}{img("ax4.png", 120, 176, 116, 72)}
{cap(242, 94, 146, "EVホール側から見た受付", "エレベーターを降りて正面に受付が見える配置です。", "4F")}
{cap(242, 222, 146, f"施術室（約6.5㎡・約4畳）", "ベッド・スツール・荷物かご・フック。木目の引戸で統一（窓なし）。", "4F")}
"""
pages.append(page("内装イメージ　4階（受付ロビー・更衣室・施術室）", "INTERIOR IMAGE 4F", p4, "P.10"))

# ---------------------------------------------------------------- 11 5F
p5 = f"""{img("v5_free.png", 0, 0, 236, 148)}{img("v5_staff.png", 242, 0, 146, 91)}{img("ax5.png", 242, 128, 146, 91)}
{cap(0, 152, 236, "5F フリースペース", "施術前後の待合・カウンセリング・セミナーに使えるラウンジ。造作ベンチと丸テーブル、銀座院と同じ素材と色。", "5F")}
{cap(242, 94, 146, "スタッフ休憩室（約18㎡）", "道路側の窓に面した明るい休憩室。ミニキッチン・冷蔵庫付き。スタッフ更衣室（男女）・物品庫も5階に集約。", "5F")}
{cap(242, 222, 146, "5F 俯瞰", f"施術室{tc['5F']}室／フリースペース／スタッフ休憩室・更衣室／物品・リネン庫", "5F")}
"""
pages.append(page("内装イメージ　5階（施術室・フリースペース・スタッフエリア）", "INTERIOR IMAGE 5F", p5, "P.11"))

# ---------------------------------------------------------------- 12 仕上表・ビル規定
fin = [
    ("床", "タイルカーペット（防炎品・防炎表示付、ベージュ系・銀座院同等柄）／MRI室・処置室：ビニル床シート", "4・5F：既設OAフロア（h=100）上に施工"),
    ("巾木", "ソフト巾木 H60（ベージュ）", ""),
    ("壁", "軽量鉄骨下地＋石膏ボード（不燃）AEP塗装（白・塗り壁調）／受付背面：木目調不燃化粧板", "施術室間仕切は上部開放の欄間式（欄間 h=500）"),
    ("天井", "4・5F：既設天井（CH2,800）／1F：直天（想定FL+3,700）のため石膏ボード天井を新設（CH約3,000）　受付上部：木目調リング（不燃）", "既設の感知器・スプリンクラー・非常照明の機能を妨げない"),
    ("建具", "施術室：木目調不燃化粧板 引戸 W900×H2,100／MRI室：シールド扉（専門業者）", "鍵1本をビル側へお預け"),
    ("家具", "受付カウンター（木目＋白天板）、待合いす（ベージュ張地・木脚）、施術ベッド", "防災設備の機能を妨げない配置"),
    ("照明", "LEDライン照明・ダウンライト（電球色～温白色 3,000～3,500K、調光）", "4・5F電気容量：1Φ約100VA/㎡、3Φ約200VA/㎡（募集資料）"),
    ("カーテン等", "4・5F道路側窓：防炎ロールスクリーン（アイボリー）", "防炎物品（防炎ラベル縫付）"),
    ("MRI室", "電磁（RF）シールド工事・必要に応じ磁気シールド（専門業者）、専用空調・チラー", "重量・振動・騒音・電源容量はビル側と事前協議"),
]
fr = "".join(f"<tr><th>{a}</th><td>{b}</td><td class='note'>{c}</td></tr>" for a, b, c in fin)
rules = [
    ("床荷重", "1～3F 5,000N/㎡、4・5F 3,000N/㎡（室内全体の荷重制限は別途）。重量物のMRIは1Fに配置し、重量・脚部・配置を事前相談"),
    ("間仕切", "不燃材を使用。上部開放の欄間式（欄間 h≥500）とし、防災設備の追加が必要な場合はB工事で対応"),
    ("避難経路", "2～5F：EVホールから避難階段附室まで廊下状に整備。当計画は廊下・通路で特別避難階段・共用トイレに直結。EVホール入口の防火扉の開閉を妨げる造作・什器なし"),
    ("ファサード・サイン", "既設サッシ・ガラスは無加工、ガラス面から600mm程度離隔。サインはビル指定位置（S1・S2）のみ、店名・ロゴに限定。点滅・映像・赤色光・露出ネオン不使用、表示面積10㎡以下"),
    ("電気・空調", "設定容量内で計画（設定容量を超える電源増設・保安電源の増設は不可）。空調吹出口・吸込口の機能を妨げない"),
    ("特殊設備", "騒音・振動・熱を発生する機器（MRI装置・チラー等）はビル側の承認を得て設置。躯体のはつり・ホールインアンカーは原則不可"),
    ("給排水", "4・5F：給水 PS内バルブ止め（40A）、排水 区画内スラブ上ころがしキャップ止め（100A）。漏水対策（防水・漏水検知）を指示に従い実施"),
    ("点検口・収納", "共用配管・配線部に点検口を設置。共用倉庫・従業員ロッカーはないため、店舗内（5F）に確保"),
    ("用途", "誘導用途区画（日本橋・東京駅前地区）のため、診療所・施術所としての用途適合性を事前に確認"),
    ("提出図書", "B工事指示書・基本設計図書：着工2.5か月前（B工事見積は1か月）／工事申請書・実施設計図：着工1か月前／竣工図：竣工後1か月以内"),
]
rr = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rules)
p12 = f"""<div style="position:absolute;left:0;top:0;width:200mm"><h3 style="font-size:4.2mm;margin:0 0 3mm">仕上表（概略・基本計画段階）</h3>
<table style="font-size:2.85mm"><tr><th>部位</th><th>仕上</th><th>備考</th></tr>{fr}</table></div>
<div style="position:absolute;left:208mm;top:0;width:180mm"><h3 style="font-size:4.2mm;margin:0 0 3mm">内装マニュアル（ビル規定）への対応</h3>
<table style="font-size:2.85mm">{rr}</table>
<p class="note" style="margin-top:3mm">※出典：内装マニュアル（2026年8月7日発行）、募集資料。本資料は出店審査用の基本計画です。図面寸法は募集図面・1F CADからの読取り値で、実施設計時にビル側の白図・設備図に基づき確定します。パースはイメージで、実際の仕上・家具とは異なる場合があります。</p></div>"""
pages.append(page("仕上表・ビル規定への対応", "FINISH SCHEDULE / COMPLIANCE", p12, "P.12"))

html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(pages)}</body></html>'
open(os.path.join(out, "添付資料.html"), "w").write(html)
print("pages", len(pages))
