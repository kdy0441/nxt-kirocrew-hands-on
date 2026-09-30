"""Task A (DAG leaf): aggregate warehouse A into an intermediate file.

Independent of tasks B and C. Reads practice/data/warehouse-a.md (read-only)
via the shared warehouse_parse module and writes the per-warehouse result
(warehouse total, per-item quantities, warehouse_row low-stock list) to
submissions/practice/run01/partial-a.json.
"""

import json
import os

from warehouse_parse import parse_warehouse

HERE = os.path.dirname(os.path.abspath(__file__))
# submissions/practice/run01 -> week05 (three levels up), then practice/data
WEEK05 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(WEEK05, "practice", "data", "warehouse-a.md")
OUTPUT = os.path.join(HERE, "partial-a.json")


def main():
    parsed = parse_warehouse(SOURCE)
    warehouse = parsed["warehouse"]

    # warehouse_row basis: each low-stock row carries its warehouse label.
    low_stock = [
        {"item": row["item"], "quantity": row["quantity"], "warehouse": warehouse}
        for row in parsed["low_stock_rows"]
    ]

    partial = {
        "warehouse": warehouse,
        "source_file": parsed["source_file"],
        "total": parsed["total"],
        "items": parsed["items"],
        "low_stock": low_stock,
    }

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(partial, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(json.dumps(partial, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
