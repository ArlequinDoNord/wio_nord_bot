# -*- coding: utf-8 -*-
"""
tools/tax_report.py
Аналитика налоговых ставок и их влияния на казну.

Периоды строятся из журнала смен ставок (admin_logs: set_tax / set_sale_tax),
а не из захардкоженных дат. До первой записи действует дефолт из settings
(15% и 15%). Для каждого периода считаются поступления в казну по видам налога
и средний доход в сутки.

Запуск локально (нужна БД):
    .venv\\Scripts\\python.exe tools/tax_report.py [путь_к_nordmark.db]
На проде (БД в контейнере):
    Get-Content -Raw tools\\tax_report.py | ssh arlequin@89.19.210.194 "docker exec -i wio_nord_bot-wio_nord_bot-1 python -u - /app/data/nordmark.db"

Ограничения:
- Налог с продаж у производителей восстанавливается из строк shop_payout с
  «(N% налог)» в описании: выплата = оборот − налог, поэтому налог = выплата·N/(100−N).
- Налог с рынка/улова — явные строки казны «Налог: …».
- Оборот здесь не выгружается целиком: учитываются только производители. Ставка
  в долях оборота проверяется по этой выборке.
- Поступления в казну включают покупки в магазине (не только налоги) — колонка
  «казна всего» нужна для контекста, а не как доход от налогов.
- Даты — UTC (CURRENT_TIMESTAMP SQLite).
"""
import re
import sqlite3
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NAL = "\u041d\u0430\u043b\u043e\u0433"            # Налог
OTCH = "\u043e\u0442\u0447"                        # отч
PCT_NAL = re.compile(r"\((\d+)% \u043d\u0430\u043b\u043e\u0433\)")  # (N% налог)
DEFAULT_REPORT = 15
DEFAULT_SALE = 15
FMT = "%Y-%m-%d %H:%M:%S"
# Смены в пределах часа (например, отчёты и продажи подряд) — один период.
MERGE_WINDOW_SEC = 3600


def _ts(s):
    return datetime.strptime(s[:19], FMT)


def build_periods(conn):
    """[(name, start, end, report_pct, sale_pct)] по журналу смен ставок."""
    events = []
    for row in conn.execute(
            "SELECT action, details, created_at FROM admin_logs "
            "WHERE action IN ('set_tax', 'set_sale_tax') ORDER BY id"):
        m = re.search(r"percent=(\d+)", row[1] or "")
        if not m:
            continue
        events.append((row[2][:19], row[0], int(m.group(1))))
    first = conn.execute("SELECT MIN(created_at) FROM transactions").fetchone()[0]
    if not first:
        return []
    report, sale = DEFAULT_REPORT, DEFAULT_SALE
    cur = {"start": first[:19], "report": report, "sale": sale}
    closed = []
    for ts, action, pct in events:
        if (_ts(ts) - _ts(cur["start"])).total_seconds() > MERGE_WINDOW_SEC:
            closed.append((cur["start"], ts, cur["report"], cur["sale"]))
            cur = {"start": ts, "report": cur["report"], "sale": cur["sale"]}
        if action == "set_tax":
            cur["report"] = pct
        else:
            cur["sale"] = pct
    closed.append((cur["start"], datetime.now(timezone.utc).strftime(FMT),
                   cur["report"], cur["sale"]))
    return [(f"P{i}", a, b, r, s) for i, (a, b, r, s) in enumerate(closed)]


def stats(conn, a, b):
    d = max((_ts(b) - _ts(a)).total_seconds() / 86400.0, 1e-9)
    q = lambda sql, args: conn.execute(sql, args).fetchone()[0] or 0
    rep_net = q("SELECT SUM(amount) FROM transactions WHERE tx_type='report' "
                "AND created_at >= ? AND created_at < ?", (a, b))
    rep_tax = q("SELECT SUM(amount) FROM transactions WHERE to_user=0 AND description LIKE ? "
                "AND description LIKE ? AND created_at >= ? AND created_at < ?",
                ("%" + NAL + "%", "%" + OTCH + "%", a, b))
    rep_n = q("SELECT COUNT(*) FROM transactions WHERE tx_type='report' "
              "AND created_at >= ? AND created_at < ?", (a, b))
    sale_explicit = q("SELECT SUM(amount) FROM transactions WHERE to_user=0 "
                      "AND description LIKE ? AND description NOT LIKE ? "
                      "AND created_at >= ? AND created_at < ?",
                      (NAL + ":%", "%" + OTCH + "%", a, b))
    sale_implied = 0.0
    turnover = 0.0
    for amount, desc in conn.execute(
            "SELECT amount, description FROM transactions WHERE tx_type='shop_payout' "
            "AND created_at >= ? AND created_at < ?", (a, b)):
        m = PCT_NAL.search(desc or "")
        if m and 0 < int(m.group(1)) < 100:
            p = int(m.group(1))
            gross = amount / (1 - p / 100.0)
            sale_implied += gross - amount
            turnover += gross
    treas_in = q("SELECT SUM(amount) FROM transactions WHERE to_user=0 "
                 "AND created_at >= ? AND created_at < ?", (a, b))
    # sale_explicit («Налог: …» в казне) и sale_implied (из shop_payout) — один и тот же
    # налог с одних и тех же продаж. Складывать нельзя: берём явные строки казны,
    # implied — только как проверку ставки через оборот.
    return {
        "days": d,
        "rep_net": rep_net / d,
        "rep_tax": rep_tax / d,
        "rep_share": (rep_tax / (rep_net + rep_tax)) if (rep_net + rep_tax) else 0.0,
        "rep_n": rep_n / d,
        "sale_tax": sale_explicit / d,
        "sale_turnover": turnover / d,
        "sale_check_implied": sale_implied / d,
        "treasury_all": treas_in / d,
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "nordmark.db"
    conn = sqlite3.connect(path)
    periods = build_periods(conn)
    print("| период | с | по | дней | отчёты, % | продажи, % | отчётов/сут | "
          "оборот отчётов/сут | налог с отчётов/сут | доля налога в отчётах | "
          "оборот продаж/сут | налог с продаж/сут | ставка по обороту продаж | "
          "налоги всего/сут | казна всего/сут |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, a, b, r, s in periods:
        st = stats(conn, a, b)
        rate = (st["sale_check_implied"] / st["sale_turnover"] * 100) if st["sale_turnover"] else 0.0
        taxes = st["rep_tax"] + st["sale_tax"]
        print(f"| {name} | {a[:16]} | {b[:16]} | {st['days']:.1f} | {r} | {s} | "
              f"{st['rep_n']:.1f} | {st['rep_net'] + st['rep_tax']:.0f} | {st['rep_tax']:.0f} | "
              f"{st['rep_share'] * 100:.1f}% | {st['sale_turnover']:.0f} | {st['sale_tax']:.0f} | "
              f"{rate:.1f}% | {taxes:.0f} | {st['treasury_all']:.0f} |")


if __name__ == "__main__":
    main()
