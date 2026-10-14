"""添付資料・補足資料 共通のページ様式（A3横）"""
FOOT = "整形外科ふっか／整痛院ふっか 東京駅院 出店企画書 添付資料 ／ 日本橋WASAMIビル 1F・4F・5F"

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


def page(title, en, inner, no, foot=FOOT):
    return (f'<div class="pg"><div class="frame"></div><div class="hd"><h1>{title}</h1><span class="en">{en}</span></div>'
            f'<div class="body">{inner}</div><div class="ft"><span>{foot}</span><span>{no}</span></div></div>')


