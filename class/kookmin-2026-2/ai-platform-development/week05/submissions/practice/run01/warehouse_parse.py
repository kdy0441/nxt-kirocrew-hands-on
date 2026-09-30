"""Shared warehouse parser module.

Reads a single warehouse-*.md file and returns a structured aggregate.
Imported by the three per-warehouse tasks (task_a/b/c.py).

Low-stock basis: warehouse_row (a row's quantity < 5).
"""

import os
import re

_HEADING_RE = re.compile(r"^# 창고 (\S+) 재고$")
_ROW_RE = re.compile(r"^\|\s*([a-zA-Z0-9_-]+)\s*\|\s*(\d+)\s*\|$")


def parse_warehouse(path):
    """Parse one warehouse-*.md file.

    Returns a dict:
      {
        "warehouse": <letter from the '# 창고 X 재고' heading>,
        "source_file": <basename of path>,
        "total": <int, sum of all quantities>,
        "items": {item: int qty, ...},
        "low_stock_rows": [{"item": ..., "quantity": int}, ...]  # qty < 5
      }
    Quantities are stored as ints, not strings.
    """
    warehouse = None
    items = {}
    low_stock_rows = []

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")

            heading = _HEADING_RE.match(line)
            if heading:
                warehouse = heading.group(1)
                continue

            row = _ROW_RE.match(line)
            if not row:
                # Skips the header row (| 품목 | 수량 |) and the
                # separator row (|---|---:|) and any blank lines.
                continue

            item = row.group(1)
            qty = int(row.group(2))
            items[item] = items.get(item, 0) + qty
            if qty < 5:
                low_stock_rows.append({"item": item, "quantity": qty})

    return {
        "warehouse": warehouse,
        "source_file": os.path.basename(path),
        "total": sum(items.values()),
        "items": items,
        "low_stock_rows": low_stock_rows,
    }


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(parse_warehouse(sys.argv[1]), ensure_ascii=False, indent=2))
