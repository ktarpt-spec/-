/**
 * 定例会アンケート リアルタイムダッシュボード（Google Apps Script）
 *
 * Googleフォームの編集画面 →「⋮」→「スクリプト エディタ」で開いたプロジェクトに
 * このファイル（Code.gs）と index.html を貼り付けて、ウェブアプリとしてデプロイします。
 * 詳しい手順は README.md を参照してください。
 */

// フォームのスクリプトエディタ以外（単独のスクリプト）で使う場合は、
// フォーム編集画面URLの /forms/d/【ここ】/edit の部分を入れてください。
var FORM_ID = '';

// 5段階の選択式を点数化するとき、選択肢の並び順の先頭を何点にするか（先頭=5点 … 末尾=1点）
var SCALE_SIZE = 5;

function getForm_() {
  return FORM_ID ? FormApp.openById(FORM_ID) : FormApp.getActiveForm();
}

/** ウェブアプリの入口。?format=json ならJSON（JSONPも可）、それ以外はダッシュボード画面を返す */
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.format === 'json') {
    var body = JSON.stringify(getData());
    if (p.callback && /^[\w.$]+$/.test(p.callback)) {
      return ContentService.createTextOutput(p.callback + '(' + body + ')')
        .setMimeType(ContentService.MimeType.JAVASCRIPT);
    }
    return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
  }
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('定例会アンケート ダッシュボード')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** フォームの設問と全回答をまとめて返す（ダッシュボードから定期的に呼ばれる） */
function getData() {
  var form = getForm_();
  var T = FormApp.ItemType;
  var questions = [];

  form.getItems().forEach(function (item) {
    var type = item.getType();
    var q = { id: item.getId(), title: item.getTitle(), type: String(type), choices: [], other: false };
    if (type === T.MULTIPLE_CHOICE) {
      var mc = item.asMultipleChoiceItem();
      q.choices = mc.getChoices().map(function (c) { return c.getValue(); });
      q.other = mc.hasOtherOption();
    } else if (type === T.CHECKBOX) {
      var cb = item.asCheckboxItem();
      q.choices = cb.getChoices().map(function (c) { return c.getValue(); });
      q.other = cb.hasOtherOption();
    } else if (type === T.LIST) {
      q.choices = item.asListItem().getChoices().map(function (c) { return c.getValue(); });
    } else if (type === T.SCALE) {
      var sc = item.asScaleItem();
      q.min = sc.getLowerBound();
      q.max = sc.getUpperBound();
    } else if (type === T.RATING) {
      q.min = 1;
      q.max = item.asRatingItem().getRatingScale();
    } else if (type !== T.TEXT && type !== T.PARAGRAPH_TEXT) {
      return; // セクション見出し・画像などは対象外
    }
    // 5択の単一選択は「点数」をつける（先頭=5点）
    q.scored = (type === T.MULTIPLE_CHOICE || type === T.LIST) && q.choices.length === SCALE_SIZE;
    if (type === T.SCALE || type === T.RATING) q.scored = true;
    questions.push(q);
  });

  var responses = form.getResponses().map(function (r) {
    var answers = {};
    r.getItemResponses().forEach(function (ir) {
      answers[ir.getItem().getId()] = ir.getResponse();
    });
    var email = '';
    try { email = r.getRespondentEmail() || ''; } catch (err) {}
    return { id: r.getId(), timestamp: r.getTimestamp().toISOString(), email: email, answers: answers };
  });

  return {
    title: form.getTitle(),
    questions: questions,
    responses: responses,
    fetchedAt: new Date().toISOString()
  };
}
