#!/usr/bin/env python3

"""
Caddy の JSON アクセスログ（1 行に 1 つの JSON オブジェクト）を解析し、アクティブな KonomiTV インスタンス数を推定します。

フィルタ条件:
- User-Agent が "KonomiTV/" で始まる
- リクエストパスが以下のいずれか (クエリ文字列は許可):
  - /api/v1/channels
  - /api/v1/channels/xml

集計内容:
- マッチしたリクエストの総数
- ユニーク IP 数（request.client_ip を優先、なければ request.remote_ip を使用）
- KonomiTV バージョン別のクラスタリング（"KonomiTV/" 以降のトークン）

また、過去 N 分間（デフォルト: 10 分）の「アクティブ」な集計も出力します。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ALLOWED_PATHS = {
    "/api/v1/channels",
    "/api/v1/channels/xml",
}


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="Estimate active KonomiTV instances from Caddy JSON access logs."
    )
    parser.add_argument(
        "--active-minutes",
        type=int,
        default=10,
        help="Window minutes for 'currently active' estimation (default: 10). Use 0 to disable active window.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Show top N versions (default: 30).",
    )
    return parser.parse_args()


def get_log_file_path() -> Path:
    """
    ログファイルのパスを取得します。
    CountActiveServers.py から見て ../logs/Caddy-Access.log を返します。
    """
    script_dir = Path(__file__).parent
    log_file = script_dir / ".." / "logs" / "Caddy-Access.log"
    return log_file.resolve()


def iter_lines() -> Iterable[str]:
    """
    ログファイルから行を読み込みます。
    """
    log_path = get_log_file_path()
    with open(log_path, encoding="utf-8", errors="replace") as f:
        yield from f


def get_first_header(headers: Any, key: str) -> str | None:
    """
    Caddy ログから指定されたヘッダーの最初の値を取得します。
    Caddy ログでは通常、ヘッダーは { 'User-Agent': ['...'] } のような形式で保存されています。
    """
    if not isinstance(headers, dict):
        return None
    v = headers.get(key)
    if isinstance(v, list) and v:
        if isinstance(v[0], str):
            return v[0]
        return str(v[0])
    if isinstance(v, str):
        return v
    return None


def extract_version(user_agent: str) -> str:
    """
    User-Agent 文字列から KonomiTV のバージョンを抽出します。
    例: "KonomiTV/0.13.0" または "KonomiTV/0.13.0-dev"
    空白文字までを保持します。
    """
    try:
        after = user_agent.split("/", 1)[1]
    except IndexError:
        return "unknown"
    return after.split()[0].strip() or "unknown"


def extract_path(uri: str) -> str:
    """
    URI からパス部分を抽出します。
    Caddy の request.uri は通常 "/path?query" の形式です。
    urlsplit はスキームやホストがなくても動作します。
    """
    try:
        return urlsplit(uri).path or ""
    except Exception:
        return ""


@dataclass
class Stats:
    """
    統計情報を保持するデータクラス。
    """
    matched_requests: int = 0
    unique_ips: set[str] = field(default_factory=set)
    per_version_req: Counter[str] = field(default_factory=Counter)
    per_version_ips: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))


def handle_record(obj: Any) -> tuple[float, str, str] | None:
    """
    レコードがフィルタ条件に一致する場合、(ts, ip, version) を返します。
    一致しない場合は None を返します。
    """
    if not isinstance(obj, dict):
        return None

    # Caddy アクセスログのタイムスタンプフィールドは通常 'ts' で、Unix 秒（float）です。
    ts = obj.get("ts")
    if not isinstance(ts, int | float):
        # 欠落している場合は「不明な時刻」として扱います。
        ts = 0.0
    else:
        ts = float(ts)

    req = obj.get("request", {})
    if not isinstance(req, dict):
        return None

    headers = req.get("headers", {})
    ua = get_first_header(headers, "User-Agent")
    if not ua or not ua.startswith("KonomiTV/"):
        return None

    uri = req.get("uri", "")
    if not isinstance(uri, str):
        return None
    path = extract_path(uri)
    if path not in ALLOWED_PATHS:
        return None

    # client_ip が存在する場合はそれを優先します（Caddy は trusted_proxies が設定されている場合にこれを導出できます）。
    ip = req.get("client_ip") or req.get("remote_ip")
    if not isinstance(ip, str) or not ip:
        return None

    ver = extract_version(ua)
    return (ts, ip, ver)


def update_stats(stats: Stats, ip: str, ver: str) -> None:
    """
    統計情報を更新します。
    """
    stats.matched_requests += 1
    stats.unique_ips.add(ip)
    stats.per_version_req[ver] += 1
    stats.per_version_ips[ver].add(ip)


def format_epoch(ts: float) -> str:
    """
    Unix タイムスタンプを ISO 形式の文字列に変換します。
    """
    if ts <= 0:
        return "unknown"
    dt = datetime.fromtimestamp(ts, tz=UTC)
    return dt.isoformat()


def print_report(title: str, stats: Stats, top_n: int) -> None:
    """
    統計情報のレポートを出力します。
    バージョンはユニーク IP 数の降順、次にリクエスト数の降順でソートされます。
    """
    print("")
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(f"Matched requests: {stats.matched_requests:,}")
    print(f"Unique IPs (estimate): {len(stats.unique_ips):,}")
    print("")

    # バージョンをユニーク IP 数の降順、次にリクエスト数の降順でソートします。
    items = []
    for ver, ips in stats.per_version_ips.items():
        items.append((len(ips), stats.per_version_req[ver], ver))
    items.sort(reverse=True)

    print(f"Top versions by unique IPs (showing up to {top_n}):")
    shown = 0
    for uniq_ip_count, req_count, ver in items:
        print(f"  - {ver:16s}  unique_ips={uniq_ip_count:7,}  requests={req_count:9,}")
        shown += 1
        if shown >= top_n:
            break

    if len(items) > top_n:
        rest = len(items) - top_n
        print(f"  ... (+{rest} more versions)")


def main() -> int:
    """
    メイン処理を実行します。
    """
    args = parse_args()

    overall = Stats()
    active = Stats()

    # 最大のタイムスタンプから「現在時刻」を導出します（ローカル時計より堅牢です）。
    now_ts: float | None = None
    max_ts_seen = 0.0

    # 第 1 パス: マッチするイベントを解析・収集します（メモリ内に最小限の情報のみ保持します）。
    matched_events: list[tuple[float, str, str]] = []
    log_path = get_log_file_path()
    for line in iter_lines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        rec = handle_record(obj)
        if rec is None:
            continue
        ts, ip, ver = rec
        matched_events.append((ts, ip, ver))
        if ts > max_ts_seen:
            max_ts_seen = ts

        # 全体統計はその場で更新できます。
        update_stats(overall, ip, ver)

    if matched_events:
        now_ts = max_ts_seen
    else:
        now_ts = 0.0

    # アクティブウィンドウ
    active_minutes = int(args.active_minutes)
    if active_minutes > 0 and now_ts > 0:
        window_sec = active_minutes * 60
        cutoff = now_ts - window_sec
        for ts, ip, ver in matched_events:
            if ts >= cutoff:
                update_stats(active, ip, ver)

    # 出力
    print(f"Input source: {log_path}")
    print(f"Max ts seen (used as 'now'): {format_epoch(now_ts)} (unix={now_ts:.3f})")

    print_report("OVERALL (entire input)", overall, args.top)

    if active_minutes > 0 and now_ts > 0:
        print_report(f"ACTIVE (last {active_minutes} minutes)", active, args.top)
    else:
        print("\n(active window disabled or no valid timestamps found)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
