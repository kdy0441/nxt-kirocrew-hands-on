"""Combine per-warehouse intermediate files into result.json.

Reads partial-a.json, partial-b.json, partial-c.json (produced by task_a/b/c.py)
and writes result.json following practice/출력형식.md.

low_stock_basis is 'warehouse_row': a row is low-stock when its quantity in a
single warehouse is below the threshold (5).
"""
import json
from pathlib import Path

THRESHOLD = 5
RUN_DIR = Path(__file__).resolve().parent
PARTIAL_FILES = ["partial-a.json", "partial-b.json", "partial-c.json"]


def load_partials():
    partials = []
    for name in PARTIAL_FILES:
        with open(RUN_DIR / name, encoding="utf-8") as f:
            partials.append(json.load(f))
    return partials


def build_result(partials):
    source_files = sorted(p["source_file"] for p in partials)

    warehouse_totals = {}
    item_totals = {}
    low_stock = []

    for p in partials:
        warehouse_totals[p["warehouse"]] = int(p["total"])
        for item, qty in p["items"].items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)
        for row in p["low_stock"]:
            low_stock.append({
                "item": row["item"],
                "quantity": int(row["quantity"]),
                "warehouse": row["warehouse"],
            })

    grand_total = sum(warehouse_totals.values())

    return {
        "source_files": source_files,
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": int(grand_total),
        "low_stock_basis": "warehouse_row",
        "threshold": THRESHOLD,
        "low_stock": low_stock,
    }


def write_report(result):
    """Render report.md from the result dict so every figure matches result.json."""
    lines = []
    lines.append("# 창고 재고 집계 보고서")
    lines.append("")
    lines.append(f"- 원본 파일: {', '.join(result['source_files'])}")
    lines.append(f"- 저재고 기준(low_stock_basis): `{result['low_stock_basis']}` "
                 f"(임계값 {result['threshold']} 미만)")
    lines.append(f"- 전체 총수량(grand_total): **{result['grand_total']}**")
    lines.append("")

    lines.append("## 창고별 합계")
    lines.append("")
    lines.append("| 창고 | 합계 |")
    lines.append("| --- | ---: |")
    for wh, total in result["warehouse_totals"].items():
        lines.append(f"| {wh} | {total} |")
    lines.append("")

    lines.append("## 품목별 총수량")
    lines.append("")
    lines.append("| 품목 | 총수량 |")
    lines.append("| --- | ---: |")
    for item, qty in result["item_totals"].items():
        lines.append(f"| {item} | {qty} |")
    lines.append("")

    lines.append("## 저재고 목록")
    lines.append("")
    lines.append(f"창고별 행의 수량이 {result['threshold']} 미만인 항목입니다.")
    lines.append("")
    if result["low_stock"]:
        lines.append("| 품목 | 수량 | 창고 |")
        lines.append("| --- | ---: | --- |")
        for row in result["low_stock"]:
            lines.append(f"| {row['item']} | {row['quantity']} | {row['warehouse']} |")
    else:
        lines.append("저재고 항목이 없습니다.")
    lines.append("")

    with open(RUN_DIR / "report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    partials = load_partials()
    result = build_result(partials)
    with open(RUN_DIR / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    write_report(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
