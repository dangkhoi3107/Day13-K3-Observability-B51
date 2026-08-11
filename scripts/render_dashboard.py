from __future__ import annotations

import argparse
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOGS = REPO_ROOT / "data" / "logs.jsonl"
DEFAULT_CONFIG = REPO_ROOT / "config" / "dashboard.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "submission" / "evidence" / "cp2-dashboard-runtime.html"


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    index = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[index])


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            record["_parsed_ts"] = parse_timestamp(record.get("ts"))
            records.append(record)
    return records


def minute_key(record: dict[str, Any]) -> datetime | None:
    timestamp = record.get("_parsed_ts")
    if not isinstance(timestamp, datetime):
        return None
    return timestamp.replace(second=0, microsecond=0)


def sparkline(values: list[float], color: str) -> str:
    if not values:
        values = [0.0]
    width, height, padding = 430, 92, 8
    low, high = min(values), max(values)
    spread = high - low or 1.0
    denominator = max(1, len(values) - 1)
    points = []
    for index, value in enumerate(values):
        x = padding + index * (width - 2 * padding) / denominator
        y = height - padding - (value - low) * (height - 2 * padding) / spread
        points.append(f"{x:.1f},{y:.1f}")
    escaped = html.escape(color, quote=True)
    return (
        f'<svg class="spark" viewBox="0 0 {width} {height}" role="img">'
        '<line x1="8" y1="84" x2="422" y2="84" class="axis" />'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{escaped}" '
        'stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />'
        f'<circle cx="{points[-1].split(",")[0]}" cy="{points[-1].split(",")[1]}" '
        f'r="5" fill="{escaped}" /></svg>'
    )


def panel(
    *,
    title: str,
    unit: str,
    primary: str,
    details: list[str],
    threshold: str,
    healthy: bool,
    series: list[float],
    color: str,
) -> str:
    status = "Within threshold" if healthy else "Threshold exceeded"
    status_class = "ok" if healthy else "bad"
    detail_html = "".join(f"<span>{html.escape(item)}</span>" for item in details)
    return f"""
    <section class="panel">
      <div class="panel-head"><div><h2>{html.escape(title)}</h2><p>{html.escape(unit)}</p></div>
      <span class="status {status_class}">{status}</span></div>
      <div class="primary">{html.escape(primary)}</div>
      <div class="details">{detail_html}</div>
      {sparkline(series, color)}
      <div class="threshold">Threshold/SLO: {html.escape(threshold)}</div>
    </section>
    """.strip()


def build_dashboard(records: list[dict[str, Any]], config: dict[str, Any]) -> str:
    dashboard = config["dashboard"]
    timestamps = [r["_parsed_ts"] for r in records if isinstance(r.get("_parsed_ts"), datetime)]
    window_end = max(timestamps) if timestamps else datetime.now(timezone.utc)
    window_start = window_end - timedelta(minutes=int(dashboard["time_range_minutes"]))
    window = [
        record
        for record in records
        if not isinstance(record.get("_parsed_ts"), datetime)
        or window_start <= record["_parsed_ts"] <= window_end
    ]

    received = [r for r in window if r.get("event") == "request_received"]
    responses = [r for r in window if r.get("event") == "response_sent"]
    failures = [r for r in window if r.get("event") == "request_failed"]
    latencies = [float(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
    costs = [float(r["cost_usd"]) for r in responses if isinstance(r.get("cost_usd"), (int, float))]
    tokens_in = [int(r["tokens_in"]) for r in responses if isinstance(r.get("tokens_in"), (int, float))]
    tokens_out = [int(r["tokens_out"]) for r in responses if isinstance(r.get("tokens_out"), (int, float))]
    quality = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]
    error_types = Counter(str(r.get("error_type", "UnknownError")) for r in failures)

    buckets: dict[datetime, dict[str, list[float] | int]] = defaultdict(
        lambda: {"requests": 0, "latency": [], "cost": [], "tokens": [], "quality": [], "errors": 0}
    )
    for record in window:
        key = minute_key(record)
        if key is None:
            continue
        bucket = buckets[key]
        event = record.get("event")
        if event == "request_received":
            bucket["requests"] = int(bucket["requests"]) + 1
        elif event == "request_failed":
            bucket["errors"] = int(bucket["errors"]) + 1
        elif event == "response_sent":
            for field, destination in (
                ("latency_ms", "latency"),
                ("cost_usd", "cost"),
                ("quality_score", "quality"),
            ):
                value = record.get(field)
                if isinstance(value, (int, float)):
                    values = bucket[destination]
                    assert isinstance(values, list)
                    values.append(float(value))
            token_total = sum(
                int(record.get(field, 0))
                for field in ("tokens_in", "tokens_out")
                if isinstance(record.get(field), (int, float))
            )
            token_values = bucket["tokens"]
            assert isinstance(token_values, list)
            token_values.append(float(token_total))

    ordered = [buckets[key] for key in sorted(buckets)]
    latency_series = [percentile(bucket["latency"], 95) for bucket in ordered if isinstance(bucket["latency"], list)]
    traffic_series = [float(bucket["requests"]) for bucket in ordered]
    error_series = [
        (float(bucket["errors"]) / float(bucket["requests"]) * 100)
        if bucket["requests"]
        else 0.0
        for bucket in ordered
    ]
    cost_series = [sum(bucket["cost"]) for bucket in ordered if isinstance(bucket["cost"], list)]
    token_series = [sum(bucket["tokens"]) for bucket in ordered if isinstance(bucket["tokens"], list)]
    quality_series = [mean(bucket["quality"]) if bucket["quality"] else 0.0 for bucket in ordered if isinstance(bucket["quality"], list)]

    panel_config = {item["id"]: item for item in dashboard["panels"]}
    p50, p95, p99 = (percentile(latencies, p) for p in (50, 95, 99))
    error_rate = (len(failures) / len(received) * 100) if received else 0.0
    total_cost = sum(costs)
    total_in, total_out = sum(tokens_in), sum(tokens_out)
    quality_avg = mean(quality) if quality else 0.0
    peak_traffic = max(traffic_series, default=0.0)

    cards = [
        panel(
            title="1. Latency percentiles",
            unit="milliseconds (ms)",
            primary=f"P95 {p95:,.0f} ms",
            details=[f"P50 {p50:,.0f} ms", f"P99 {p99:,.0f} ms", f"{len(latencies)} responses"],
            threshold="P95 ≤ 3,000 ms",
            healthy=p95 <= float(panel_config["latency"]["threshold"]["value"]),
            series=latency_series,
            color="#67e8f9",
        ),
        panel(
            title="2. Request traffic",
            unit="requests per minute",
            primary=f"{len(received)} requests",
            details=[f"Peak {peak_traffic:,.0f} req/min", f"{len(responses)} successful", f"{len(failures)} failed"],
            threshold="≥ 1 request/minute",
            healthy=peak_traffic >= float(panel_config["traffic"]["threshold"]["value"]),
            series=traffic_series,
            color="#a78bfa",
        ),
        panel(
            title="3. Error rate & breakdown",
            unit="percent (%)",
            primary=f"{error_rate:.2f}%",
            details=[f"{name}: {count}" for name, count in error_types.items()] or ["No request failures", "Breakdown: empty"],
            threshold="Error rate ≤ 2%",
            healthy=error_rate <= float(panel_config["errors"]["threshold"]["value"]),
            series=error_series,
            color="#fb7185",
        ),
        panel(
            title="4. AI cost",
            unit="US dollars (USD)",
            primary=f"${total_cost:.4f}",
            details=[f"Average ${mean(costs):.4f}" if costs else "Average $0.0000", f"{len(costs)} billed responses"],
            threshold="Window total ≤ $2.50",
            healthy=total_cost <= float(panel_config["cost"]["threshold"]["value"]),
            series=cost_series,
            color="#fbbf24",
        ),
        panel(
            title="5. Input / output tokens",
            unit="tokens",
            primary=f"{total_in + total_out:,} total",
            details=[f"Input {total_in:,}", f"Output {total_out:,}"],
            threshold="Each aggregate ≤ 50,000 tokens",
            healthy=max(total_in, total_out) <= float(panel_config["tokens"]["threshold"]["value"]),
            series=token_series,
            color="#34d399",
        ),
        panel(
            title="6. Quality proxy",
            unit="score 0–1",
            primary=f"{quality_avg:.3f}",
            details=[f"{len(quality)} scored responses", "Mean quality_score"],
            threshold="Mean ≥ 0.75",
            healthy=quality_avg >= float(panel_config["quality"]["threshold"]["value"]),
            series=quality_series,
            color="#60a5fa",
        ),
    ]

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Day 13 AI Observability Dashboard</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, "Segoe UI", sans-serif; background:#07111f; color:#e5edf8; }}
* {{ box-sizing:border-box; }} body {{ margin:0; padding:34px 42px 42px; min-width:1400px; background:radial-gradient(circle at 90% 0,#172554 0,#07111f 42%); }}
header {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px; }}
h1 {{ margin:0 0 8px; font-size:34px; letter-spacing:-.03em; }} header p {{ margin:0; color:#9fb0c8; }}
.meta {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; max-width:760px; }} .pill {{ background:#10223a; border:1px solid #27405f; border-radius:999px; padding:8px 12px; color:#c7d5e8; font-size:13px; }}
.grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:18px; }} .panel {{ min-height:420px; padding:22px; border:1px solid #223a59; border-radius:18px; background:linear-gradient(145deg,rgba(18,37,61,.96),rgba(8,22,39,.96)); box-shadow:0 18px 46px rgba(0,0,0,.2); }}
.panel-head {{ display:flex; justify-content:space-between; gap:14px; align-items:flex-start; }} h2 {{ margin:0; font-size:18px; }} .panel-head p {{ margin:5px 0 0; color:#8296b1; font-size:12px; text-transform:uppercase; letter-spacing:.09em; }}
.status {{ font-size:11px; font-weight:700; padding:6px 8px; border-radius:8px; white-space:nowrap; }} .status.ok {{ color:#6ee7b7; background:#064e3b66; }} .status.bad {{ color:#fda4af; background:#88133766; }}
.primary {{ font-size:38px; font-weight:800; margin:24px 0 14px; letter-spacing:-.035em; }} .details {{ display:flex; gap:8px; flex-wrap:wrap; min-height:56px; }} .details span {{ background:#0b1a2d; border:1px solid #203752; color:#bac9dc; padding:7px 9px; border-radius:8px; font-size:12px; }}
.spark {{ width:100%; height:104px; margin:20px 0 10px; }} .axis {{ stroke:#314763; stroke-width:1; stroke-dasharray:4 5; }} .threshold {{ border-top:1px solid #243b58; padding-top:14px; color:#aebed1; font-size:13px; }}
footer {{ margin-top:20px; color:#7186a2; font-size:12px; display:flex; justify-content:space-between; }}
</style></head><body>
<header><div><h1>Day 13 · AI Observability</h1><p>Runtime dashboard generated from structured JSON logs</p></div>
<div class="meta"><span class="pill">Source: data/logs.jsonl</span><span class="pill">Time range: {dashboard['time_range_minutes']} minutes</span><span class="pill">Refresh: {dashboard['refresh_seconds']} seconds</span><span class="pill">Records in window: {len(window)}</span></div></header>
<main class="grid">{"".join(cards)}</main>
<footer><span>Window: {window_start.isoformat(timespec="seconds")} → {window_end.isoformat(timespec="seconds")}</span><span>Generated: {generated_at}</span></footer>
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the six-panel dashboard from data/logs.jsonl")
    parser.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    records = load_records(args.logs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_dashboard(records, config), encoding="utf-8")
    print(f"Rendered {len(records)} log records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
