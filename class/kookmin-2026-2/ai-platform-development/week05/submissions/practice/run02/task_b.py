"""Task B (DAG leaf): aggregate warehouse B into an intermediate file.

Independent of tasks A and C. Reads practice/data/warehouse-b.md (read-only)
via the shared warehouse_parse module and writes the per-warehouse result
(warehouse total, per-item quantities, warehouse_row low-stock list) to
submissions/practice/run01/partial-b.json.
"""

import json
import os

from warehouse_parse import parse_warehouse

HERE = os.path.dirname(os.path.abspath(__file__))
# submissions/practice/run01 -> week05 (three levels up), then practice/data
WEEK05 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(WEEK05, "practice", "data", "warehouse-b.md")
OUTPUT = os.path.join(HERE, "partial-b.json")


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
