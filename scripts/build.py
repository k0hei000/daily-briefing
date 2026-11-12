#!/usr/bin/env python3
"""Validate daily briefings and build the dashboard.

Usage:
    python3 scripts/build.py            # validate all + build dist/index.html
    python3 scripts/build.py --check    # validate only

Reads  : data/briefings/YYYY-MM-DD.json, topics.yaml, templates/dashboard.html
Writes : dist/index.html (self-contained page with the last N days embedded)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BRIEF_DIR = ROOT / "data" / "briefings"
TEMPLATE = ROOT / "templates" / "dashboard.html"
OUT = ROOT / "dist" / "index.html"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_settings() -> dict:
    cfg = yaml.safe_load((ROOT / "topics.yaml").read_text(encoding="utf-8")) or {}
    return cfg.get("settings", {}) or {}


def validate(path: Path, b: dict) -> list[str]:
    errs: list[str] = []
    where = path.name
    if not DATE_RE.match(str(b.get("date", ""))):
        errs.append(f"{where}: date が YYYY-MM-DD ではありません")
    if b.get("date") and f"{b['date']}.json" != path.name:
        errs.append(f"{where}: ファイル名と date が一致しません")
    topics = b.get("topics")
    if not isinstance(topics, list) or not topics:
        errs.append(f"{where}: topics が空です")
        topics = []
    seen = set()
    for t in topics:
        for k in ("id", "name", "color", "items"):
            if k not in t:
                errs.append(f"{where}: topic に {k} がありません ({t.get('id')})")
        for it in t.get("items", []):
            iid = it.get("id")
            if not iid or iid in seen:
                errs.append(f"{where}: item id が空か重複しています ({iid})")
            seen.add(iid)
            for k in ("title", "summary", "detail"):
                if not str(it.get(k, "")).strip():
                    errs.append(f"{where}: {iid} の {k} が空です")
            if it.get("importance") not in (1, 2, 3):
                errs.append(f"{where}: {iid} の importance は 1〜3 にしてください")
            srcs = it.get("sources") or []
            if not srcs:
                errs.append(f"{where}: {iid} に sources がありません")
            for s in srcs:
                if not str(s.get("url", "")).startswith(("http://", "https://")):
                    errs.append(f"{where}: {iid} の source url が不正です: {s.get('url')}")
    pod = b.get("podcast") or {}
    script = pod.get("script")
    if not isinstance(script, list) or not script:
        errs.append(f"{where}: podcast.script が空です")
    else:
        for i, line in enumerate(script):
            if not str(line.get("speaker", "")).strip() or not str(line.get("text", "")).strip():
                errs.append(f"{where}: podcast.script[{i}] に speaker/text がありません")
    return errs


def main() -> int:
    check_only = "--check" in sys.argv
    settings = load_settings()
    keep = int(settings.get("archive_days", 30))

    files = sorted(BRIEF_DIR.glob("*.json"))
    briefings, errors = [], []
    for f in files:
        try:
            b = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{f.name}: JSON として読めません: {e}")
            continue
        errors.extend(validate(f, b))
        briefings.append(b)

    if errors:
        print("検証エラー:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {len(briefings)} 日分のブリーフィングを検証しました")
    if check_only:
        return 0

    briefings.sort(key=lambda b: b["date"], reverse=True)
    briefings = briefings[:keep]
    data = json.dumps(briefings, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")  # never close the <script> early
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/[]", data, 1)
    if "/*__DATA__*/" in html:
        print("テンプレートのデータ差し込み位置が見つかりません")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)} ({len(briefings)} days, {OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
