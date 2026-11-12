# daily-briefing

個人用の毎日の情報収集ダッシュボード & ポッドキャスト。Claude Code の Routine（スケジュール実行）で毎朝自動更新する。

## 構成

- `topics.yaml` — 追いかけるトピックの設定（追加・削除はここだけ）
- `prompts/daily-run.md` — 毎日の自動実行の手順書。**「今日のブリーフィングを作って」と頼まれたらこれに従う**
- `data/briefings/YYYY-MM-DD.json` — 1日分のニュースとポッドキャスト台本
- `templates/dashboard.html` — ダッシュボードのテンプレート（データは build 時に埋め込み）
- `scripts/build.py` — JSON の検証と `dist/index.html` の生成
- `dist/index.html` — 生成物。claude.ai の Artifact として公開する
- `config.json` — 公開先 Artifact の slug / URL

## ルール

- 日付は日本時間（`TZ=Asia/Tokyo`）。
- ニュースは実在する記事と URL だけを使う。推測で作らない。
- ゴシップ・芸能・スキャンダルは入れない。
- JSON を変更したら必ず `python3 scripts/build.py` を通してから commit する。
- 作業は `main` ブランチに直接 commit / push してよい（個人用リポジトリ）。
- 読者は GLORY ACADEMY（ポーカーの学び場）の運営者。ポーカー関連は運営視点の示唆を添える。
