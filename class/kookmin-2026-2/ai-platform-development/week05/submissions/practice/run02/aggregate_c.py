"""DAG 작업 C: 창고 C 집계 (A·B와 독립).

warehouse_parse.parse_warehouse로 practice/data/warehouse-c.md를 읽어
{"warehouse": "C", "total": <int>, "items": {품목: 정수수량}} 형태의
중간 파일 warehouse-c.json을 이 스크립트 폴더에 저장한다.
"""

import json
from pathlib import Path

from warehouse_parse import parse_warehouse, warehouse_total

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent.parent / 'practice' / 'data' / 'warehouse-c.md'
OUT = HERE / 'warehouse-c.json'


def main():
    warehouse_name, items = parse_warehouse(DATA)
    result = {
        'warehouse': warehouse_name,
        'total': warehouse_total(items),
        'items': items,
    }
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print('wrote', OUT.name, result)


if __name__ == '__main__':
    main()
