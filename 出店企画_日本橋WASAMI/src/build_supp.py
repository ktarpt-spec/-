"""審査ご確認事項への補足資料（A3横・4ページ） usage: build_supp.py <outdir>  → <outdir>/補足資料.html
貸主審査の3つの観点（賃料の支払能力／用途・許認可の適法性／ビル・他テナントへの影響）と、
ご指摘①～⑤（開設者・契約関係・用途適合性・設計施工体制・許認可）に回答する。
【　】は確定後に記入する項目。"""
import os, sys
from style import css, page

out = sys.argv[1]
FOOT = "整形外科ふっか／整痛院ふっか 東京駅院 出店企画書 補足資料（審査ご確認事項への回答） ／ 日本橋WASAMIビル 1F・4F・5F"
F = lambda t="　　　　": f'<span class="fill">【{t}】</span>'
extra = """
.fill { color: #b5523b; font-weight: bold }
.sec h3 { font-size: 4.2mm; margin: 0 0 2.5mm; color: #2b2522 }
.sec p, .sec li { font-size: 3mm; line-height: 1.7; margin: 0 }
.sec ul { margin: 0; padding-left: 4.5mm }
.view { background: #f6f1e8; border-radius: 1.2mm; padding: 3.5mm 4.5mm; margin-bottom: 3.5mm }
.view h4 { font-size: 3.7mm; margin: 0 0 1.5mm; color: #9a7b55 }
.view li { font-size: 2.85mm; line-height: 1.65 }
.st { display: inline-block; font-size: 2.5mm; padding: 0.4mm 1.6mm; border-radius: 0.8mm; color: #fff; white-space: nowrap }
.ok { background: #1baf7a } .wip { background: #eb6834 } .plan { background: #2a78d6 } .na { background: #898781 }
table.t th, table.t td { padding: 1.3mm 1.8mm; font-size: 2.75mm; line-height: 1.5 }
"""
ST = {"ok": "対応済", "wip": "依頼・選定中", "plan": "予定", "na": "対象外"}
st = lambda k, t=None: f'<span class="st {k}">{t or ST[k]}</span>'
pages = []

# ---------------------------------------------------------------- 補足-1 回答一覧
views = [
    ("① 賃料を払い続けられるか", [
        "賃貸借の当事者は株式会社ふっか（1F・4F・5F一括）。1Fを転貸しても、貸主様への賃料は当社が全額の支払義務を負います。",
        "最終月商8,480万円・賃料比率 約11%・営業利益率 約38%、開業5か月目に単月黒字の計画（添付資料P.12・別シート「収支計画」）。",
        "整痛院ふっかは全国9院を運営（2016年開業・2023年法人化）。銀座院の運営実績をそのまま拡大する計画です（添付資料P.13）。",
        f"決算書（直近{F('　期')}期分）・納税証明書・会社概要をご提出します。"]),
    ("② 用途と許認可が適法か", [
        "1F 整形外科：一般社団法人（開設者）が中央区保健所の開設許可を受けて開設し、医師を管理者に選任（補足-2）。",
        "4・5F 整痛院：株式会社ふっか直営の施術所。医療機関とは受付・会計・表示を分けます。",
        "誘導用途区画での診療所・施術所の用途適合性は、貸主様へ確認をご依頼中です（補足-4）。",
        "必要な許認可・届出を一覧にし、提出先と時期を明示しています（補足-4）。"]),
    ("③ ビルや他テナントに迷惑をかけないか", [
        "MRI（1.5T）は床荷重5,000N/㎡の1Fに配置。荷重分散架台・電磁シールド・騒音・振動・搬入経路を専門業者と計画（補足-3）。",
        "5ガウスラインは区画内に収まる配置。ゼロヘリウム型のためクエンチ配管不要（平面図 A-01）。",
        "1Fは道路から玄関ポーチで直接出入り、4・5FはEV利用の完全予約制で、共用部の滞留を抑えます。",
        "看板を目立たせない外観。サインはビル指定位置（S1・S2）のみ、既設ガラス・サッシは無加工（A-04・A-05）。",
        "ビル側との質疑は窓口を一本化し、1営業日以内に一次回答（補足-3）。"]),
]
vh = "".join(f'<div class="view"><h4>{t}</h4><ul>' + "".join(f"<li>{x}</li>" for x in xs) + "</ul></div>" for t, xs in views)
qa = [
    ("①", "1階の開設者・管理者（医師）と契約当事者",
     f"開設者：一般社団法人{F('法人名')}／管理者：管理医師{F('氏名')}（医師）。賃貸借の契約当事者は株式会社ふっか。",
     f"管理医師の就任承諾書・医師免許証（写）、法人の登記事項証明書・定款（写）を{F('　月　日')}までに提出", "補足-2", "wip"),
    ("②", "開設者と申込主体の関係・法的整理",
     "株式会社ふっかが3フロアを一括で賃借し、1Fを開設法人へ転貸（民法612条により貸主様の書面承諾が前提）。転貸賃料は原賃料の面積按分相当とし、医療法の非営利性に反しない整理とします。",
     "転貸借契約書（案）・転貸承諾書（案）を賃貸借契約前にご提示。保健所の事前相談で契約関係を確認", "補足-2", "plan"),
    ("③", "誘導用途区画での用途適合性（貸主様の事前確認）",
     f"貸主様へ確認をご依頼中（依頼日：{F('　月　日')}）。",
     "ご回答の受領後に計画を確定。条件が付く場合は計画に反映", "補足-4", "wip"),
    ("④", "設計事務所・施工会社の任命と質疑体制",
     f"候補先から選定中。{F('　月　日')}までに決定し、任命を証する書類を提出。",
     "体制図・責任者・質疑応答ルール（窓口一本化／一次回答1営業日以内／質疑管理表／週1回定例）を定めました", "補足-3", "wip"),
    ("⑤", "必要な許認可の一覧と取得見込み時期",
     "診療所開設許可・開設届、MRIの高周波利用設備許可、消防の届出、施術所の届出要否、理学療法士の免許（写）等を一覧化。",
     "提出先・主体・時期を一覧表で管理し、進捗をご報告", "補足-4", "plan"),
]
qt = ("<tr><th>No.</th><th>ご確認事項</th><th>現状・回答</th><th>今後の対応・提出書類</th><th>参照</th><th>状況</th></tr>"
      + "".join(f"<tr><td><b>{a}</b></td><td><b>{b}</b></td><td>{c}</td><td>{d}</td><td style='white-space:nowrap'>{e}</td><td>{st(k)}</td></tr>" for a, b, c, d, e, k in qa))
p1 = f"""<div class="sec" style="position:absolute;left:0;top:0;width:150mm">
<h3>貸主様の審査の観点と当社の回答</h3>{vh}</div>
<div class="sec" style="position:absolute;left:158mm;top:0;width:230mm">
<h3>ご確認事項①～⑤への回答一覧</h3>
<table class="t">{qt}</table>
<p class="note" style="margin-top:3mm">{F('　')}は確定後に記入します（法人名・医師名・日付・登録番号等）。各手続の要否・時期は、保健所・消防署等との事前相談で確定します。
状況：{st('ok')} {st('wip')} {st('plan')} {st('na')}</p></div>"""
pages.append(page("審査ご確認事項への回答（概要）", "SUMMARY OF ANSWERS", p1, "補足-1", FOOT))

# ---------------------------------------------------------------- 補足-2 契約・開設の関係
def bx(x, y, w, h, title, sub, fill="#f6f1e8", st_="#9a7b55"):
    lines = "".join(f'<tspan x="{x + w / 2}" dy="4.6">{t}</tspan>' for t in sub)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{fill}" stroke="{st_}" stroke-width="0.4"/>'
            f'<text x="{x + w / 2}" y="{y + 7}" font-size="3.6" font-weight="bold" text-anchor="middle" fill="#2b2522">{title}</text>'
            f'<text x="{x + w / 2}" y="{y + 8.5}" font-size="2.8" text-anchor="middle" fill="#52514e">{lines}</text>')

def ar(x1, y1, x2, y2, lab, dx=2, anchor="start", dash=False):
    d = ' stroke-dasharray="1.6,1"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2b2522" stroke-width="0.45" marker-end="url(#a)"{d}/>'
            f'<text x="{(x1 + x2) / 2 + dx}" y="{(y1 + y2) / 2 + 1}" font-size="2.8" fill="#9a7b55" font-weight="bold" text-anchor="{anchor}">{lab}</text>')

svg = f"""<svg viewBox="0 0 175 220" style="width:175mm;height:220mm;font-family:'IPAGothic',sans-serif">
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2b2522"/></marker></defs>
{bx(45, 2, 85, 22, "貸主", ["日本橋WASAMIビル", "（1F・4F・5F）"], "#ffffff", "#898781")}
{ar(87.5, 24, 87.5, 46, "定期建物賃貸借契約（1F・4F・5F 一括）")}
{bx(35, 46, 105, 28, "株式会社ふっか（借主・申込主体）", ["代表取締役 松田 圭太", "賃料全額の支払義務（1Fを含む）"], "#f3ede4")}
{ar(60, 74, 35, 110, "転貸借契約（1F）", -2, "end")}
<text x="12" y="98" font-size="2.6" fill="#b5523b">※貸主様の書面承諾（民法612条）</text>
{ar(115, 74, 140, 110, "直営", 2)}
{bx(2, 110, 78, 30, "一般社団法人" + "　" * 0, ["【法人名】", "診療所の開設者（中央区保健所の開設許可）"])}
{bx(95, 110, 78, 30, "整痛院ふっか 東京駅院", ["4・5F 施術所（株式会社ふっか直営）", "完全予約制・施術室20室"])}
{ar(41, 168, 41, 140, "管理者に選任", 2)}
{bx(2, 168, 78, 26, "管理医師【氏名】", ["医師（常勤）", "診療所の管理者（医療法10条）"], "#ffffff")}
{bx(2, 140 + 0, 0.01, 0.01, "", [])}
<text x="41" y="203" font-size="3.2" font-weight="bold" text-anchor="middle" fill="#2b2522">1F 整形外科ふっか 東京駅院</text>
<text x="41" y="208" font-size="2.7" text-anchor="middle" fill="#52514e">診察・処置・MRI検査（自費診療）</text>
<line x1="88" y1="108" x2="88" y2="200" stroke="#c3c2b7" stroke-width="0.4" stroke-dasharray="1.5,1"/>
<text x="88" y="214" font-size="2.6" text-anchor="middle" fill="#898781">受付・会計・表示を分け、医療機関（1F）と施術所（4・5F）を明確に区分</text>
</svg>"""
legal = [
    ("開設主体", "一般社団法人は診療所の開設主体になれます。医師以外の者による開設のため、中央区保健所（特別区）で開設許可を受け、開設後10日以内に開設届を提出します（医療法7条・8条）。"),
    ("非営利性", "営利を目的とする医療機関の開設は認められません（医療法7条7項）。開設法人が自ら診療所を運営し、転貸賃料は原賃料の面積按分相当に設定して、利益の移転と見られない契約内容とします。保健所の事前相談で契約書を確認いただきます。"),
    ("管理者", f"管理者は医師とし（医療法10条）、原則として常勤で、他の医療機関の管理者は兼ねません（医療法12条）。就任承諾書・医師免許証（写）を提出します。氏名：{F('　')}"),
    ("転貸", "転貸には貸主様の承諾が必要です（民法612条）。転貸借は原契約の期間・用途・ビル規定の範囲内とし、原契約が終了すれば転貸借も終了します。賃料・原状回復・ビル規定の遵守は株式会社ふっかが貸主様に対して責任を負います。"),
    ("4・5F 施術所", "整痛院（整体・運動療法）は株式会社ふっかの直営です。あん摩マッサージ指圧・はり・きゅう・柔道整復の施術を行う場合は、施術所開設届を提出します（補足-4）。医療機関（1F）とは受付・会計・広告表示を分けます。"),
    ("提出予定書類", f"一般社団法人の登記事項証明書・定款／管理医師の就任承諾書・医師免許証（写）／転貸借契約書（案）／転貸承諾書（案）／株式会社ふっかの登記事項証明書・決算書（{F('　期')}期分）"),
]
lt = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in legal)
p2 = f"""<div style="position:absolute;left:0;top:0;width:180mm"><h3 style="font-size:4.2mm;margin:0 0 2mm">契約・開設の関係図（①②）</h3>{svg}</div>
<div class="sec" style="position:absolute;left:190mm;top:0;width:198mm"><h3>法的な整理</h3>
<table class="t">{lt}</table>
<p class="note" style="margin-top:3mm">※根拠条文は概要です。開設許可の要件・必要書類は中央区保健所の事前相談で確認し、契約書の最終版は専門家（弁護士・行政書士）の確認を経てご提出します。</p></div>"""
pages.append(page("契約・開設の関係と法的な整理", "CONTRACT & OPERATOR STRUCTURE", p2, "補足-2", FOOT))

# ---------------------------------------------------------------- 補足-3 プロジェクト体制
def role(x, y, w, h, head, name, lines, fill="#f6f1e8", stc="#9a7b55"):
    t = "".join(f'<tspan x="{x + 3}" dy="4.2">{s}</tspan>' for s in lines)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{fill}" stroke="{stc}" stroke-width="0.4"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="7" rx="1.5" fill="{stc}"/>'
            f'<text x="{x + 3}" y="{y + 5}" font-size="3.1" font-weight="bold" fill="#fff">{head}</text>'
            f'<text x="{x + 3}" y="{y + 12}" font-size="3" font-weight="bold" fill="#2b2522">{name}</text>'
            f'<text x="{x + 3}" y="{y + 13}" font-size="2.55" fill="#52514e">{t}</text>')
ln = lambda x1, y1, x2, y2, d=False: f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#898781" stroke-width="0.4"{" stroke-dasharray=\"1.5,1\"" if d else ""}/>'
org = f"""<svg viewBox="0 0 232 126" style="width:232mm;height:126mm;font-family:'IPAGothic',sans-serif">
{role(4, 2, 70, 30, "貸主・管理会社", "日本橋WASAMIビル", ["B工事指定業者（設計・施工）", "工事区分・内装マニュアルの審査"], "#ffffff", "#898781")}
{role(84, 2, 70, 30, "統括責任者（ビル側窓口）", "株式会社ふっか【氏名・役職】", ["プロジェクト全体の責任者", "質疑・申請・工程の窓口を一本化"], "#f3ede4", "#9a7b55")}
{role(164, 2, 64, 30, "開設法人・管理医師", "一般社団法人【法人名】", ["保健所の事前相談・開設許可", "医療機器・医療運営の要件"], "#ffffff", "#9a7b55")}
{ln(74, 17, 84, 17)}{ln(154, 17, 164, 17)}
{ln(119, 32, 119, 42)}{ln(30, 42, 208, 42)}
{ln(30, 42, 30, 48)}{ln(76, 42, 76, 48)}{ln(122, 42, 122, 48)}{ln(168, 42, 168, 48)}{ln(208, 42, 208, 48)}
{role(4, 48, 50, 52, "設計担当", "設計事務所【社名】", ["一級建築士【氏名】", "登録番号【　　】", "建築士事務所登録【　　】", "基本・実施設計・B工事指示書", "ビル側図面との整合"], "#f6f1e8", "#2a78d6")}
{role(56, 48, 42, 52, "施工会社", "【社名】", ["建設業許可【許可番号】", "（内装仕上工事業ほか）", "現場代理人【氏名】", "主任技術者【氏名】"], "#f6f1e8", "#2a78d6")}
{role(100, 48, 44, 52, "設備担当", "【社名・氏名】", ["電気容量・幹線の確認", "MRI専用電源・チラー", "空調・換気・給排水", "B工事業者との調整"], "#f6f1e8", "#2a78d6")}
{role(146, 48, 44, 52, "MRI設置協力", "富士フイルム系販売店ほか", ["装置・据付・保守", "電磁シールド工事業者", "荷重分散架台・搬入揚重", "搬入経路・養生計画"], "#f6f1e8", "#2a78d6")}
{role(192, 48, 36, 52, "許認可", "【行政書士 等】", ["保健所・消防署", "総合通信局", "への申請・届出"], "#f6f1e8", "#2a78d6")}
<text x="4" y="110" font-size="2.9" fill="#2b2522" font-weight="bold">選定状況：設計事務所・施工会社は候補先から選定中。【　月　日】までに決定し、下記(1)の書類を提出します。</text>
<text x="4" y="116" font-size="2.6" fill="#52514e">B工事（A工事の変更・躯体や共用設備に関わる工事）は貸主様指定の業者が実施設計・施工し、当社設計者は基本設計と指示書を担当します（工事区分表による）。</text>
<text x="4" y="121" font-size="2.6" fill="#52514e">ビル側との連絡は統括責任者に一本化し、設計・施工・設備・MRIの各担当は統括責任者を通じて回答します。</text>
</svg>"""
proof = ["設計業務委託契約書（写）または設計者の任命書", "工事請負契約書（写）または発注内示書・任命書", "ビル側協議に関する委任状（統括責任者 → 各担当）",
         "一級建築士免許証・建築士事務所登録通知書（写）", "建設業許可通知書（写）・技術者の資格者証（写）", "会社概要・医療施設の設計施工実績"]
rules = [("窓口", "統括責任者に一本化（メール・電話の受付先を一つに）"), ("一次回答", "1営業日以内（受付・担当・回答予定日を連絡）"),
         ("本回答", "期限を明示（原則5営業日以内、調査が必要な事項は回答日を通知）"), ("追跡", "質疑管理表で全件管理し、毎週貸主様・管理会社へ共有"),
         ("定例打合せ", "設計期間・工事期間とも週1回（工程・課題・B工事調整）"), ("記録", "議事録は2営業日以内に共有。変更は書面（変更指示書）で確定")]
rt = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rules)
qhead = ["No.", "受付日", "質問者", "内容", "担当", "一次回答", "本回答期限", "回答日", "状態"]
qrows = [["001", "11/5", "管理会社", "MRI搬入経路（マシンハッチ）と養生範囲", "MRI協力", "11/6", "11/12", "11/11", "完了"],
         ["002", "11/8", "B工事業者", "1F床（FL-300）の嵩上げ方法と荷重", "設計", "11/9", "11/15", "—", "対応中"]]
qtbl = "<tr>" + "".join(f"<th>{h}</th>" for h in qhead) + "</tr>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in qrows)
p3 = f"""<div style="position:absolute;left:0;top:0;width:235mm"><h3 style="font-size:4.2mm;margin:0 0 2mm">プロジェクト体制図（④）</h3>{org}
<h3 style="font-size:3.8mm;margin:0 0 2mm">質疑管理表（様式例）</h3><table class="t">{qtbl}</table>
<p class="note" style="margin-top:1.5mm">※記入例です。実際の運用では表計算ファイルを共有し、全件を番号で追跡します。</p></div>
<div class="sec" style="position:absolute;left:245mm;top:0;width:143mm">
<h3>(1) 任命の事実を証明する書類</h3><ul>{"".join(f"<li>{x}</li>" for x in proof)}</ul>
<p class="note" style="margin-top:1.5mm">管理会社様の審査に合わせ、選定後すみやかに提出します。</p>
<h3 style="margin-top:5mm">(2) 責任者の明確化</h3>
<p>左の体制図のとおり、統括・設計・施工・設備・MRI設置・許認可の各責任者を一人ずつ定め、氏名・資格・登録番号を記入した体制表を提出します。</p>
<h3 style="margin-top:5mm">(3) 質疑応答の運用ルール</h3>
<table class="t">{rt}</table></div>"""
pages.append(page("設計・施工のプロジェクト体制と質疑応答ルール", "PROJECT TEAM & Q&A RULES", p3, "補足-3", FOOT))

# ---------------------------------------------------------------- 補足-4 許認可一覧・スケジュール
permits = [
    ("用途", "誘導用途区画での診療所・施術所の用途適合性の確認", "都市計画（誘導用途）・ビル規定", "貸主様（必要に応じ中央区）", "当社→貸主様", f"依頼中（{F('　月　日')}依頼）", "wip"),
    ("契約", "転貸の承諾（1F）", "民法612条", "貸主様", "株式会社ふっか", "賃貸借契約時", "plan"),
    ("医療", "保健所の事前相談（図面・契約関係・医療機器）", "医療法", "中央区保健所", "開設法人", "設計段階（着工前）", "plan"),
    ("医療", "診療所開設許可申請（医師以外の開設）", "医療法7条", "中央区保健所", "開設法人", "竣工後・開設前", "plan"),
    ("医療", "診療所開設届", "医療法8条・同施行令", "中央区保健所", "開設法人", "開設後10日以内", "plan"),
    ("医療", "管理医師の選任（医師免許証の写し）", "医療法10条", "（開設許可申請に添付）", "開設法人", f"{F('　月')}までに選任", "wip"),
    ("MRI", "高周波利用設備（医療用設備）の許可", "電波法100条", "関東総合通信局", "開設法人（メーカー代行）", "装置設置前", "plan"),
    ("MRI", "放射線関係の届出（エックス線装置）", "医療法15条3項", "中央区保健所", "—", "MRIは対象外（X線装置を置く場合のみ）", "na"),
    ("施術所", "施術所開設届（あん摩マッサージ指圧・はり・きゅう／柔道整復）", "あはき法9条の2・柔整法19条", "中央区保健所", "株式会社ふっか", "国家資格施術を行う場合、開設後10日以内", "na"),
    ("人員", "理学療法士の免許証（写し）", "理学療法士及び作業療法士法", "貸主様（審査資料）", "株式会社ふっか", f"在籍予定{F('　')}名分を提出", "plan"),
    ("消防", "防火対象物工事等計画届", "火災予防条例（東京都）", "所轄消防署", "施工会社", "工事着手の7日前まで", "plan"),
    ("消防", "防火対象物使用開始届", "火災予防条例（東京都）", "所轄消防署", "開設法人・当社", "使用開始の7日前まで", "plan"),
    ("サイン", "屋外広告物（S1・S2）の手続", "東京都屋外広告物条例", "中央区（ビル側と協議）", "当社", "掲出前（要否をビル側と確認）", "plan"),
    ("廃棄物", "感染性廃棄物の処理委託契約", "廃棄物処理法", "許可業者と契約", "開設法人", "開設前", "plan"),
    ("保険", "保険医療機関の指定申請", "健康保険法", "関東信越厚生局", "—", "自費診療のみのため申請しない", "na"),
]
pt = ("<tr><th>区分</th><th>手続</th><th>根拠</th><th>提出先</th><th>主体</th><th>時期（見込み）</th><th>状況</th></tr>"
      + "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td><td>{d}</td><td>{e}</td><td>{f_}</td><td>{st(k)}</td></tr>" for a, b, c, d, e, f_, k in permits))
# 工程（入居可能日 2027年2月1日から逆算した想定）
months = ["10月", "11月", "12月", "1月", "2月", "3月", "4月", "5月"]
bars = [("出店審査・用途確認", 0, 1.6, "#eb6834"), ("設計・施工体制の確定", 0.6, 1.6, "#eb6834"), ("保健所・消防の事前相談", 1.0, 3.0, "#2a78d6"),
        ("基本設計・B工事指示書", 1.0, 2.6, "#2a78d6"), ("賃貸借・転貸承諾の契約", 2.0, 2.8, "#2a78d6"), ("実施設計・各種申請", 2.6, 4.0, "#2a78d6"),
        ("内装・MRI工事（入居後）", 4.0, 6.5, "#1baf7a"), ("開設許可・使用開始届", 6.2, 7.0, "#1baf7a"), ("開院", 7.0, 7.4, "#9a7b55")]
gx, gw, rh = 42, 11, 6.4
g = [f'<text x="{gx + i * gw + gw / 2}" y="5" font-size="2.7" text-anchor="middle" fill="#52514e">{m}</text>' for i, m in enumerate(months)]
g += [f'<line x1="{gx + i * gw}" y1="7" x2="{gx + i * gw}" y2="{9 + len(bars) * rh}" stroke="#e1e0d9" stroke-width="0.3"/>' for i in range(len(months) + 1)]
g.append(f'<text x="{gx}" y="-1" font-size="2.4" fill="#898781">2026年</text><text x="{gx + 3 * gw}" y="-1" font-size="2.4" fill="#898781">2027年</text>')
for i, (lab, a, b, col) in enumerate(bars):
    y = 9 + i * rh
    g.append(f'<text x="{gx - 2}" y="{y + 3.6}" font-size="2.6" text-anchor="end" fill="#2b2522">{lab}</text>')
    g.append(f'<rect x="{gx + a * gw}" y="{y}" width="{(b - a) * gw}" height="4.2" rx="1" fill="{col}"/>')
x2 = gx + 4 * gw
g.append(f'<line x1="{x2}" y1="7" x2="{x2}" y2="{9 + len(bars) * rh}" stroke="#b5523b" stroke-width="0.5" stroke-dasharray="1.2,0.8"/>'
         f'<text x="{x2 + 1}" y="{11 + len(bars) * rh}" font-size="2.5" fill="#b5523b">入居可能日 2027/2/1</text>')
gantt = f'<svg viewBox="0 -4 130 {16 + len(bars) * rh}" style="width:130mm;font-family:\'IPAGothic\',sans-serif">{"".join(g)}</svg>'
p4 = f"""<div class="sec" style="position:absolute;left:0;top:0;width:250mm"><h3>必要な許認可・届出の一覧と取得見込み（③⑤）</h3>
<table class="t">{pt}</table>
<p class="note" style="margin-top:2mm">※要否・時期は保健所・消防署・総合通信局との事前相談で確定します。4・5Fの整痛院（整体・運動療法）には法律上の届出制度はありませんが、国家資格の施術を行う場合は施術所開設届を提出します。</p></div>
<div class="sec" style="position:absolute;left:258mm;top:0;width:130mm">
<h3>工程の想定</h3><p class="note" style="margin-bottom:2mm">入居可能日（2027年2月1日）から逆算した想定です。B工事指示書は着工2.5か月前、工事申請は着工1か月前に提出（内装マニュアル）。日程はビル側・保健所と調整のうえ確定します。</p>
<div style="width:130mm;overflow:hidden">{gantt}</div>
<h3 style="margin-top:4mm">提出をお約束する書類</h3><ul>
<li>貸主様の用途適合性のご回答受領後、計画の確定版</li>
<li>開設法人・管理医師の書類一式（補足-2）</li>
<li>設計・施工の任命書類と体制表（補足-3）</li>
<li>理学療法士の免許証（写）</li>
<li>許認可の進捗表（月1回更新）</li></ul></div>"""
pages.append(page("許認可・届出の一覧と工程", "PERMITS & SCHEDULE", p4, "補足-4", FOOT))

html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}{extra}</style></head><body>{"".join(pages)}</body></html>'
open(os.path.join(out, "補足資料.html"), "w").write(html)
print("pages", len(pages))
