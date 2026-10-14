# fukka 日本橋院（仮称）出店企画 ― 日本橋WASAMIビル 1F・4F・5F

## 成果物（output/）
| ファイル | 内容 |
|---|---|
| `出店企画書_fukka日本橋院.xlsx` | 貸主様式「出店企画書」に記入したもの（黄色セル＝要記入） |
| `添付資料_平面図・立面図・内外装イメージ.pdf` | A3横 11ページ：表紙／計画概要／平面図 1F・4F・5F／立面図・サイン計画／外観・内観イメージ／仕上表・ビル規定対応 |
| `補足資料_審査ご確認事項への回答.pdf` | A3横 4ページ：審査の観点と回答一覧／契約・開設の関係／設計施工の体制・質疑ルール／許認可一覧・工程（`src/build_supp.py`） |
| `drawings/*.svg` | 図面単体（A3、CADやIllustratorで開けます） |
| `images/*.png` | パース単体（1600×1000） |

## 再生成（src/）
```
python3 src/geometry.py src/build/floors.json        # 各階プラン（ここを編集）
python3 src/plans.py output/drawings                  # 平面図（1Fは募集図面スキャンを下図に使用）
python3 src/elevations.py output/drawings             # 立面図・サイン
cd src && node render_all.mjs ../output/images        # パース（three.js）
python3 build_pdf.py ../output && node shot.mjs ../output/添付資料.html ../output/添付資料_平面図・立面図・内外装イメージ.pdf
python3 fill_xlsx.py <貸主様式.xlsx> ../output/出店企画書_fukka日本橋院.xlsx
```
※ 面積：1F 98.36㎡（約29.75坪）、4F・5F 各G229.86㎡（約69.53坪）。1Fの下図は `src/assets/plan_1F_scan.png`（貸主の募集図面）。
