"""중간 파일(warehouse-a/b/c.json)을 모아 result.json과 report.md를 만든다.

aggregate_a/b/c.py가 만든 창고별 중간 파일을 읽어 practice/출력형식.md 구조로
result.json을 쓴다. 2차(run02) 기준을 사용한다:
- low_stock_basis: "item_total" (전체 창고 품목 합계 기준)
- threshold: 5 (수량이 이 값보다 작을 때 저재고)

제공 검사기(practice/tests/check_result.py)가 검사하는 기준과 동일하다.
report.md의 모든 수치는 result 딕셔너리에서 그대로 렌더링해 JSON과 일치시킨다.
"""

import json
from pathlib import Path

THRESHOLD = 5
HERE = Path(__file__).resolve().parent
# aggregate_a/b/c.py가 이 폴더에 저장한 중간 파일
INTERMEDIATE_FILES = ['warehouse-a.json', 'warehouse-b.json', 'warehouse-c.json']
DATA = HERE.parent.parent.parent / 'practice' / 'data'


def load_intermediates():
    parts = []
    for name in INTERMEDIATE_FILES:
        parts.append(json.loads((HERE / name).read_text(encoding='utf-8')))
    return parts


def build_result(parts):
    warehouse_totals = {}
    item_totals = {}
    for p in parts:
        warehouse_totals[p['warehouse']] = int(p['total'])
        for item, qty in p['items'].items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)

    grand_total = sum(warehouse_totals.values())

    # 2차 기준: 전체 품목 합계가 threshold 미만인 품목. 품목명 오름차순.
    low_stock = [
        {'item': name, 'quantity': qty}
        for name, qty in sorted(item_totals.items())
        if qty < THRESHOLD
    ]

    # source_files: 실제 입력 파일 이름 목록(정렬).
    source_files = sorted(p.name for p in DATA.glob('warehouse-*.md'))

    return {
        'source_files': source_files,
        'warehouse_totals': warehouse_totals,
        'item_totals': item_totals,
        'grand_total': int(grand_total),
        'low_stock_basis': 'item_total',
        'threshold': THRESHOLD,
        'low_stock': low_stock,
    }


def write_report(result):
    lines = [
        '# 창고 재고 집계 보고서',
        '',
        f"- 원본 파일: {', '.join(result['source_files'])}",
        f"- 저재고 기준(low_stock_basis): `{result['low_stock_basis']}` "
        f"(전체 품목 합계가 임계값 {result['threshold']} 미만)",
        f"- 전체 총수량(grand_total): **{result['grand_total']}**",
        '',
        '## 창고별 합계',
        '',
        '| 창고 | 합계 |',
        '| --- | ---: |',
    ]
    for wh, total in result['warehouse_totals'].items():
        lines.append(f'| {wh} | {total} |')
    lines += ['', '## 품목별 총수량', '', '| 품목 | 총수량 |', '| --- | ---: |']
    for item, qty in result['item_totals'].items():
        lines.append(f'| {item} | {qty} |')
    lines += ['', '## 저재고 목록', '',
              f"전체 품목 합계가 {result['threshold']} 미만인 항목입니다.", '']
    if result['low_stock']:
        lines += ['| 품목 | 총수량 |', '| --- | ---: |']
        for row in result['low_stock']:
            lines.append(f"| {row['item']} | {row['quantity']} |")
    else:
        lines.append('저재고 항목이 없습니다.')
    lines.append('')
    (HERE / 'report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parts = load_intermediates()
    result = build_result(parts)
    (HERE / 'result.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    write_report(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
