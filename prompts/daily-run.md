# 毎日のブリーフィング生成手順

このファイルは毎朝の Routine（スケジュール実行）で Claude Code が読む手順書です。
上から順に実行してください。途中で人に質問せず、最後まで自動で終わらせます。

## 0. 準備

1. リポジトリ `k0hei000/daily-briefing` が手元に無ければ `add_repo`（access: push）で接続して clone する。
2. `git pull --ff-only origin main` で最新化する。
3. 今日の日付（日本時間）を取得する: `TZ=Asia/Tokyo date +%F` → 以下 `DATE`。
4. `data/briefings/DATE.json` が既にあれば、その日の分は作り直す（上書き）。
5. `topics.yaml` を読み、`enabled: true` のトピックと `settings` を把握する。
6. 重複を避けるため、直近3日分の `data/briefings/*.json` の見出しと URL を確認しておく。

## 1. ニュース収集（トピックごと）

- 有効なトピックごとにサブエージェントを1つずつ並列で起動して調べてよい（推奨）。
  各エージェントには、そのトピックの `name` `subcategories` `focus` `avoid` `max_items`、
  `settings.lookback_hours`、`DATE`、直近3日で既出の見出し/URL、下の「item の形式」を渡す。
- 調査は WebSearch を中心に行う（環境によって WebFetch は外部サイトに届かない）。
  日本語と英語の両方で検索する。
- ルール:
  - 実在する記事だけを使う。URL は検索結果で実際に確認できたものだけ。推測で作らない。
  - 公開日が `lookback_hours` より古いものは原則入れない。
    ただし「日本のポーカー業界」のように更新頻度が低いトピックは14日前まで可。
  - 既出（直近3日に載せたもの）は、大きな続報がない限り入れない。続報なら見出しに【続報】と付ける。
  - 良いニュースが少ない日は件数を無理に埋めない（0件も可）。
  - 数字・固有名詞は出典にあるものだけ。不確かな点は detail に「未確認」と明記する。

### item の形式

```json
{
  "id": "<topic id>-<連番>",          // 例: "ai-1"
  "title": "日本語の見出し（40字以内）",
  "subcategory": "topics.yaml の subcategories のいずれか",
  "summary": "一覧に出す概要。日本語2文・120字程度",
  "detail": "詳細。日本語 Markdown 400〜700字。背景・何が起きたか・具体的な数字や仕組み・今後の見通しを、箇条書きを交えて",
  "why_it_matters": "読者にとっての意味（1〜2文）。トピックの focus にある観点で書く",
  "importance": 3,                     // 1〜3（3が最重要）
  "published": "YYYY-MM-DD",
  "sources": [{ "title": "媒体名: 記事タイトル", "url": "https://..." }]
}
```

## 2. ブリーフィング JSON を書く

`data/briefings/DATE.json` に次の形で保存する（UTF-8・日本語）:

```json
{
  "date": "DATE",
  "generated_at": "ISO8601（+09:00）",
  "headline": "今日いちばん押さえるべきことを1〜2文で",
  "topics": [
    { "id": "ai", "name": "最新のAI活用事例", "color": "#6366f1", "items": [ ... ] }
  ],
  "podcast": {
    "title": "M月D日のブリーフィング",
    "duration_min": 8,
    "script": [ { "speaker": "アオイ", "text": "..." }, { "speaker": "ケン", "text": "..." } ]
  }
}
```

- `topics` の順番・id・name・color は `topics.yaml` に合わせる。

## 3. ポッドキャスト台本を書く

ブラウザの読み上げ機能で再生されるので、**耳で聞いて分かる文章**にする。

- 話者は2人: **アオイ**（進行役・要点をまとめる）と **ケン**（聞き手・素朴な質問や「つまり？」を入れる）。
- 長さ: `settings.podcast_minutes` 分 × 約300字（8分なら約2,400字）。1セリフは最大120字程度。
- 構成:
  1. オープニング（日付と今日の目次を一言で）
  2. トピックごとに重要度の高い順で2〜4件ずつ紹介。各ニュースは「何が起きた → なぜ大事 → 一言コメント」
  3. 最後に「今日これだけ覚えておけばOK」を3点でまとめてクロージング
- 記号・URL・英字略語の羅列は避け、読みにくい固有名詞はカタカナ併記（例: 「Anthropic（アンソロピック）」）。
- ポーカーの話題では GLORY ACADEMY の運営に役立つ観点を一言添える。

## 4. ビルドと検証

```bash
python3 scripts/build.py
```

- エラーが出たら JSON を直して再実行する（通るまで）。
- `dist/index.html` が更新される。

## 5. GitHub に保存

```bash
git add -A
git commit -m "briefing: DATE"
git push origin main
```

push がネットワークエラーで失敗したら、間隔をあけて最大4回まで再試行する。

## 6. ダッシュボード（claude.ai Artifact）を更新

`config.json` の `artifact.slug` が公開先のダッシュボードです。

1. `get_artifact`（slug）で現在の version を取得する。
2. `publish_files` で `dist/index.html` を `index.html` として公開する
   （slug と base_version を指定。title / icon は省略して既存のものを維持）。
   - Artifact ツールしか無い環境では、`Artifact` の publish に `url: config.json の artifact.url` と
     `file_path: dist/index.html` を渡す（先に `action: "read"` で読む）。
3. `config.json` の slug が空のときだけ新規作成し（title: `Daily Briefing`, icon: `news`）、
   返ってきた slug と url を `config.json` に書いて commit / push する。

## 7. 完了報告

最後に短く報告する: 日付、トピックごとの件数、headline、ダッシュボードの URL。
失敗した手順があれば、どこで何が起きたかをそのまま書く。
