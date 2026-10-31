// 問題データの検証：正解が右下マスと一致し、8つの選択肢がすべて見た目で区別できるか
// 実行: node tools/verify.js
const path = require("path");
const { ITEMS, PRACTICE, build, cellKey } = require(path.join(__dirname, "..", "items.js"));
let ng = 0;
for (const item of [PRACTICE, ...ITEMS]) {
  const b = build(item);
  const keys = b.options.map(cellKey);
  const errs = [];
  if (keys[0] !== cellKey(b.cells[8])) errs.push("正解が右下マスと一致しない");
  if (new Set(keys).size !== 8) errs.push("見た目が同じ選択肢がある");
  if (errs.length) { ng++; console.log(`NG ${item.id}: ${errs.join(" / ")}`); }
}
console.log(ng ? `${ng}問に問題あり` : `全${ITEMS.length}問＋練習問題 OK`);
process.exit(ng ? 1 : 0);
