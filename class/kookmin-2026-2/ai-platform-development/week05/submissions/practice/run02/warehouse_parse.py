"""창고 재고 md 파서. check_result.py와 동일한 정규식 규칙을 사용한다.

제공 검사기(practice/tests/check_result.py)와 동일하게:
- 창고 제목: ^# 창고 (\\S+) 재고$
- 품목 행:   ^\\|\\s*([a-zA-Z0-9_-]+)\\s*\\|\\s*(\\d+)\\s*\\|$
제목 누락/중복, 품목 행 누락/중복이면 예외를 던진다.
수량은 정수로 저장한다.
"""

import re
from pathlib import Path

HEADING = re.compile(r'^# 창고 (\S+) 재고$', re.M)
ROW = re.compile(r'^\|\s*([a-zA-Z0-9_-]+)\s*\|\s*(\d+)\s*\|$', re.M)


def parse_warehouse(path):
    """warehouse-*.md 한 개를 읽어 (창고이름, {품목: 정수수량})를 반환한다.

    검사기와 동일한 규칙으로 파싱하며, 제목이 없거나 품목 행이 없거나
    창고/품목이 중복되면 ValueError를 던진다.
    """
    path = Path(path)
    source = path.read_text(encoding='utf-8')

    heading = HEADING.search(source)
    if not heading:
        raise ValueError('창고 제목 누락: ' + path.name)
    # 한 파일에 제목이 여럿이면 중복으로 본다.
    if len(HEADING.findall(source)) != 1:
        raise ValueError('창고 제목 중복: ' + path.name)
    warehouse_name = heading[1]

    rows = ROW.findall(source)
    if not rows or len({name for name, _ in rows}) != len(rows):
        raise ValueError('품목 행 누락 또는 중복: ' + path.name)

    items = {name: int(qty) for name, qty in rows}
    return warehouse_name, items


def warehouse_total(items):
    """품목별 수량 딕셔너리의 정수 합계를 반환한다."""
    return sum(items.values())


if __name__ == '__main__':
    import sys
    name, items = parse_warehouse(sys.argv[1])
    print(name, items, 'total=', warehouse_total(items))
