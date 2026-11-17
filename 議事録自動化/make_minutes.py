#!/usr/bin/env python3
"""議事録の内容（JSON）から、Googleドキュメント用のHTMLを作る。

使い方:
    python3 make_minutes.py 入力.json 出力.html

JSONの形は 議事録データの例.json を参照。
文字列の中の **太字** は太字になる。
Googleドキュメントへの変換で崩れない書き方（インラインstyle・表で描く図）だけを使う。
"""
import html
import json
import re
import sys

NAVY = "#1a3d6d"
BLUE = "#3d6aa8"
LIGHT_BLUE = "#6f93c8"
PALE = "#e8eef7"
GREEN = "#1a8a4a"
PALE_GREEN = "#d9f2e3"
PALER_GREEN = "#eefaf2"
YELLOW = "#fff6d6"
RED = "#c0392b"
PALE_RED = "#fde2e1"
LINE = "#c9d3e3"
WHITE_BORDER = "border:1px solid #ffffff;"

TONE_BG = {"good": PALE_GREEN, "bad": PALE_RED, "neutral": PALE, "warn": YELLOW}
TONE_FG = {"good": NAVY, "bad": RED, "neutral": NAVY, "warn": "#8a6d00"}


def t(s):
    """エスケープして **太字** を <b> にする。"""
    s = html.escape(str(s), quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def lines(items, prefix=""):
    if isinstance(items, str):
        items = [items]
    return "".join(f'<p style="margin:0">{prefix}{t(x)}</p>' for x in items)


def box(inner, bg, border):
    return (f'<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%; border-color:{border};">'
            f'<tr><td style="background:{bg}; border:1px solid {border};">{inner}</td></tr></table>')


def h2(text):
    return f'<h2 style="color:{NAVY};">{t(text)}</h2>'


def h3(text):
    return f'<h3 style="color:{NAVY};">● {t(text)}</h3>'


def note(text):
    return f'<p style="font-size:9pt; color:#666; margin:0;">※{t(text)}</p>' if text else ""


def kv_table(rows, label_width=20):
    """[(ラベル, 中身HTML, ラベル背景)] の2列表。"""
    out = [f'<table border="1" cellpadding="6" style="border-collapse:collapse; width:100%; border-color:{LINE};">']
    for i, (label, body, bg) in enumerate(rows):
        w = f" width:{label_width}%;" if i == 0 else ""
        out.append(f'<tr><td style="background:{bg};{w}"><b>{label}</b></td><td>{body}</td></tr>')
    out.append("</table>")
    return "".join(out)


def grid(headers, rows, widths=None, pick=None, head_dark=False, row_styles=None):
    """普通の表。pick は強調する列番号（採用案）。"""
    out = [f'<table border="1" cellpadding="6" style="border-collapse:collapse; width:100%; border-color:{LINE};">']
    hs = f"background:{NAVY}; color:#ffffff;" if head_dark else f"background:{PALE};"
    out.append(f'<tr style="{hs}">')
    for i, h in enumerate(headers):
        w = f" width:{widths[i]}%;" if widths else ""
        bg = f" background:{PALE_GREEN};" if pick == i and not head_dark else ""
        out.append(f'<td style="{w}{bg}"><b>{t(h)}</b></td>')
    out.append("</tr>")
    for r, row in enumerate(rows):
        rs = (row_styles or {}).get(r, "")
        out.append(f'<tr style="{rs}">' if rs else "<tr>")
        for i, c in enumerate(row):
            bg = f' style="background:{PALER_GREEN};"' if pick == i else ""
            body = lines(c) if isinstance(c, list) else t(c)
            out.append(f"<td{bg}>{body}</td>")
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


# ---- 図 ----

def cards(items):
    cells = []
    w = round(100 / max(len(items), 1))
    for c in items:
        tone = c.get("tone", "neutral")
        cells.append(
            f'<td style="background:{TONE_BG[tone]}; text-align:center; width:{w}%; border:3px solid #ffffff;">'
            f'<p style="margin:0; font-size:9pt; color:#555;">{t(c["label"])}</p>'
            f'<p style="margin:0; font-size:18pt; color:{TONE_FG[tone]};"><b>{t(c["value"])}</b></p>'
            f'<p style="margin:0; font-size:9pt;">{t(c.get("note", ""))}</p></td>')
    return f'<table cellpadding="10" style="border-collapse:collapse; width:100%;"><tr>{"".join(cells)}</tr></table>'


def funnel(block):
    """段々に減る図。steps: [{label, value}], drops: 段の間の説明。"""
    steps = block["steps"]
    drops = block.get("drops", [])
    colors = [NAVY, BLUE, LIGHT_BLUE, "#9db6dc", "#c3d3ea"]
    out = []
    n = len(steps)
    for i, s in enumerate(steps):
        width = 96 - i * (56 / max(n - 1, 1)) if n > 1 else 96
        side = (100 - width) / 2
        color = colors[min(i, len(colors) - 1)]
        out.append(
            f'<table border="0" cellpadding="7" style="border-collapse:collapse; width:100%;"><tr>'
            f'<td style="width:{side:.0f}%; {WHITE_BORDER}"></td>'
            f'<td style="width:{width:.0f}%; background:{color}; color:#ffffff; text-align:center; border:1px solid {color};">'
            f'{t(s["label"])}　<b>{t(s["value"])}</b></td>'
            f'<td style="width:{side:.0f}%; {WHITE_BORDER}"></td></tr></table>')
        if i < n - 1:
            d = drops[i] if i < len(drops) else ""
            out.append(f'<p style="text-align:center; color:{RED}; font-size:9pt; margin:0;">▼ {t(d)}</p>')
    return "".join(out)


def bars(block):
    """横棒グラフ。items: [{label, value(数値), display(表示), tone}]"""
    items = block["items"]
    vmax = max(float(i["value"]) for i in items) or 1
    out = []
    for it in items:
        pct = max(4, round(float(it["value"]) / vmax * 74))
        color = {"good": GREEN, "bad": RED, "light": LIGHT_BLUE}.get(it.get("tone"), BLUE)
        rest = 74 - pct
        tail = f'<td style="width:{rest}%; {WHITE_BORDER}"></td>' if rest > 0 else ""
        out.append(
            f'<table border="0" cellpadding="4" style="border-collapse:collapse; width:100%;"><tr>'
            f'<td style="width:26%; {WHITE_BORDER}">{t(it["label"])}</td>'
            f'<td style="width:{pct}%; background:{color}; color:#ffffff; {WHITE_BORDER}"><b>{t(it.get("display", it["value"]))}</b></td>'
            f'{tail}</tr></table>')
    return "".join(out)


def flow(block):
    """流れ図。steps: [{head, body}]。最後の箱は緑。5個を超えると2段に分ける。"""
    steps = block["steps"]
    out = []
    for start in range(0, len(steps), 5):
        chunk = steps[start:start + 5]
        n = len(chunk)
        arrow_w = 3
        box_w = (100 - arrow_w * (n - 1)) / n
        cells = []
        for i, s in enumerate(chunk):
            last = start + i == len(steps) - 1
            color, bg = (GREEN, PALE_GREEN) if last else (NAVY, TONE_BG.get(s.get("bg"), PALE))
            cells.append(
                f'<td style="width:{box_w:.0f}%; border:2px solid {color}; background:{bg}; text-align:center;">'
                f'<b>{t(s.get("head", ""))}</b>{lines(s.get("body", []))}</td>')
            if i < n - 1:
                cells.append(f'<td style="width:{arrow_w}%; text-align:center; {WHITE_BORDER}">➡</td>')
        if start > 0:
            out.append(f'<p style="margin:0; color:{NAVY};">⤷</p>')
        out.append(f'<table cellpadding="6" style="border-collapse:collapse; width:100%;"><tr>{"".join(cells)}</tr></table>')
    return "".join(out)


def block_html(b):
    kind = b["type"]
    out = [h3(b["title"])] if b.get("title") else []
    if kind == "funnel":
        out.append(funnel(b))
    elif kind == "bars":
        out.append(bars(b))
    elif kind == "flow":
        out.append(flow(b))
    elif kind == "compare":
        out.append(grid(b["headers"], b["rows"], widths=b.get("widths"), pick=b.get("pick")))
    elif kind == "table":
        styles = {i: f"background:{YELLOW};" for i in b.get("highlight", [])}
        out.append(grid(b["headers"], b["rows"], widths=b.get("widths"), head_dark=True, row_styles=styles))
    elif kind == "cards":
        out.append(cards(b["items"]))
    else:
        raise ValueError(f"unknown block type: {kind}")
    out.append(note(b.get("note")))
    return "".join(out)


def discussion_items(items):
    out = []
    for d in items:
        if isinstance(d, list):
            out.append(f"<li><b>【{t(d[0])}】</b> {t(d[1])}</li>")
        else:
            out.append(f"<li>{t(d)}</li>")
    return "<ul>" + "".join(out) + "</ul>"


def agenda(n, a):
    out = [f'<h2 style="color:#ffffff; background:{NAVY};">議題{n}　{t(a["title"])}</h2>']
    out.append(box('<p style="margin:0"><b>★ 要約</b></p>' + lines(a["summary"], "▶ "), YELLOW, "#e6d48a"))
    if a.get("background"):
        out.append(h3("背景・現状") + "<ul>" + "".join(f"<li>{t(x)}</li>" for x in a["background"]) + "</ul>")
    for b in a.get("blocks_top", []):
        out.append(block_html(b))
    if a.get("discussion"):
        out.append(h3("議論のポイント") + discussion_items(a["discussion"]))
    for b in a.get("blocks", []):
        out.append(block_html(b))
    c = a.get("conclusion", {})
    if c.get("done") or c.get("hold"):
        out.append(h3("結論"))
        out.append(box(lines(c.get("done", []), "✅ ") + lines(c.get("hold", []), "△ "), PALE_GREEN, "#9fd3b4"))
    out.append('<p style="margin:0"></p>')
    out.append(kv_table([
        ("● 責任者", lines(a.get("owner", "未定")), PALE),
        ("⏰ 期限", lines(a.get("due", "未定")), PALE),
        ("➡ 次の一手", lines(a.get("next", ["未定"]), "□ "), PALE),
        ("⚠ リスク", lines(a.get("risks", ["特になし"]), "・"), PALE_RED),
        ("❓ 未決", lines(a.get("open", ["特になし"]), "・"), YELLOW),
    ]))
    return "".join(out)


def top_banner(d):
    """いちばん上：どの会議か・日付・参加者を大きく。"""
    def row(label, body):
        return (f'<tr><td style="background:{NAVY}; color:#ffffff; width:16%; text-align:center; border:1px solid {NAVY};">'
                f'<b>{label}</b></td><td style="background:{PALE}; font-size:13pt; border:1px solid {LINE};">{body}</td></tr>')
    people = "　／　".join(t(p) for p in d["participants"])
    extra = (f'<p style="margin:0; font-size:9pt; color:#666;">{t(d["participants_note"])}</p>'
             if d.get("participants_note") else "")
    return (f'<table cellpadding="8" style="border-collapse:collapse; width:100%;">'
            + row("会議", f'<b>{t(d.get("meeting", d["title"]))}</b>')
            + row("日付", f'<b>{t(d["date"])}</b>')
            + row("参加者", f'<b>{people}</b>{extra}')
            + "</table>")


def build(d):
    out = ['<html><head><meta charset="utf-8"></head>'
           '<body style="font-family: \'Noto Sans JP\', Arial, sans-serif; font-size: 11pt; color: #222; line-height: 1.6;">']
    out.append(f'<h1 style="color:{NAVY};">議事録</h1>')
    out.append(top_banner(d))
    out.append('<p style="margin:0"></p>')
    ach = d["achievement"]
    out.append(kv_table([
        ("◆ 時間", lines(d.get("time", "不明")), PALE),
        ("◆ 目的", lines(d["purpose"]), PALE),
        ("◆ ゴール", lines(d["goal"]), PALE),
        ("◆ 達成度", f'<p style="margin:0"><b>{t(ach["mark"])}</b></p>' + lines(ach.get("lines", [])), PALE),
    ]))
    if d.get("cards"):
        out.append(h2("■ 数字でひと目") + cards(d["cards"]))
    marks = "❶❷❸❹❺"
    out.append(h2("■ 今日のポイント（3行で）"))
    out.append(box("".join(f'<p style="margin:0">{marks[i]} {t(p)}</p>' for i, p in enumerate(d["points"])), YELLOW, "#e6d48a"))
    out.append(h2("✅ やること一覧"))
    rows = [[str(i + 1), x["what"], x.get("who", "未定"), x.get("due", "未定"), x.get("status", "□ 未着手")]
            for i, x in enumerate(d["actions"])]
    out.append(grid(["#", "やること", "だれが", "いつまで", "状態"], rows, widths=[5, 50, 20, 13, 12], head_dark=True))
    for i, a in enumerate(d["agendas"], 1):
        out.append(agenda(i, a))
    nm = d.get("next_meeting", {})
    out.append(h2("■ 次回までに確認すること"))
    out.append(kv_table([
        ("日時", lines(nm.get("date", "未定")), PALE),
        ("確認事項", lines(nm.get("checks", ["特になし"]), "□ "), PALE),
    ]))
    src = d.get("source", {})
    out.append('<hr><p style="font-size:9pt; color:#888;">自動生成：Plaudの文字起こしからClaudeが作成。内容は必ず確認してください。<br>'
               f'元データ：{t(src.get("name", ""))}（{t(src.get("url", ""))}）／推定した項目には「（推定）」と記載</p>')
    out.append("</body></html>")
    result = "".join(out)
    bad = sorted({c for c in result if ord(c) > 0xFFFF})
    if bad:
        raise ValueError(f"Googleドキュメントで文字化けする文字があります: {bad}")
    return result


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(build(data))
