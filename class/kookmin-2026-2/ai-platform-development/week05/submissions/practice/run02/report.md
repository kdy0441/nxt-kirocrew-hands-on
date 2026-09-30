# 창고 재고 집계 보고서 (2차)

- 원본 파일: warehouse-a.md, warehouse-b.md, warehouse-c.md
- 저재고 기준(low_stock_basis): `item_total` (전체 창고 품목별 합계가 임계값 5 미만)
- 전체 총수량(grand_total): **54**

## 창고별 합계

| 창고 | 합계 |
| --- | ---: |
| A | 22 |
| B | 16 |
| C | 16 |

## 품목별 총수량

| 품목 | 총수량 |
| --- | ---: |
| mug | 17 |
| bottle | 12 |
| sensor | 11 |
| hub | 13 |
| cable | 1 |

## 저재고 목록

전체 창고의 품목별 총수량이 5 미만인 품목입니다.

| 품목 | 총수량 |
| --- | ---: |
| cable | 1 |
