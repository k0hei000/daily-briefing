# Daily Briefing

毎朝、関心トピックのニュースを集めてダッシュボードとポッドキャスト台本にまとめる個人用リポジトリ。
Claude Code の Routine（スケジュール実行）で自動更新されます。

- **ダッシュボード**: https://claude.ai/artifact/YSj9M9tagvGjk5NFrn91UK （非公開・本人のみ閲覧可）
- **更新時刻**: 毎朝 5:43（日本時間）

## 使い方

| やりたいこと | 方法 |
| --- | --- |
| 今日のニュースを見る | ダッシュボードを開く。カードをタップで詳細、上のチップでトピック絞り込み |
| ポッドキャストを聞く | 画面下の ▶ を押す（端末の日本語音声で読み上げ）。「台本」で全文表示、行タップでそこから再生 |
| 過去の日を見る | 上部の日付セレクタ／前日・翌日ボタン（最大30日分） |
| トピックを足す・消す | `topics.yaml` を編集して push（Claude Code に「トピックに◯◯を追加して」と頼んでもOK） |
| 手動で今すぐ更新 | Claude Code でこのリポジトリを開き「今日のブリーフィングを作って」 |

## 仕組み

```
Routine (毎朝)
  └─ prompts/daily-run.md の手順を実行
       1. topics.yaml を読む
       2. トピックごとに WebSearch で収集（サブエージェント並列）
       3. data/briefings/YYYY-MM-DD.json を書く（記事＋ポッドキャスト台本）
       4. python3 scripts/build.py → dist/index.html
       5. git commit & push
       6. dist/index.html を claude.ai Artifact に再公開
```

ローカルで確認: `python3 scripts/build.py` 後に `dist/index.html` をブラウザで開く。
