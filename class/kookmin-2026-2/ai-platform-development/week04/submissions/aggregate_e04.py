# -*- coding: utf-8 -*-
"""
빛담 가을사진전(E04) 집계 스크립트
- 원본 CSV 3개를 읽어 참가/회계/구매를 집계한다.
- 근거 문서/조항:
  * ACCOUNT-01(회계기준) 제1조 기간·기초잔액 / 제2조 부호 / 제3조 현재잔액·E04 순지출 / 제5조 구매계획 산식
  * APPROVAL-SPACE-04(장소사용승인서) 정원 160
  * CHANGE-SPACE-04(정원변경승인서, 2026-09-23) 정원 160 -> 180 (SPACE-04 대체)
  * NOTICE-04(행사안내) 홍보 정원 180 (홍보용, 승인서 아님)
  * CLUB-01(동아리운영규칙) 제1조 물품 기본인원=확정 / 제3조 대기자 미리 합산 금지
  * RULE-01(지원금지침) 지원 대상/제외
원본은 수정하지 않는다(읽기 전용).
"""
import csv, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_csv(name):
    path = os.path.join(DATA, name)
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows, len(rows)

# ---- 읽기 ----
apps, n_apps = read_csv("참가신청.csv")
accts, n_accts = read_csv("회계내역.csv")
plans, n_plans = read_csv("구매계획.csv")

EVENT = "E04"

# ---- 1) 참가 상태별 인원 (CLUB-01 제1조: 확정/대기/취소) ----
status_count = {"확정": 0, "대기": 0, "취소": 0}
for r in apps:
    st = r["신청상태"]
    status_count[st] = status_count.get(st, 0) + 1
confirmed = status_count["확정"]

# ---- 2) 확정자의 선택 (인화체험/식음료) ----
# 값: 신청 / 미신청 / 받지않음
choice = {
    "인화체험": {"신청": 0, "미신청": 0},
    "식음료": {"신청": 0, "받지않음": 0},
}
for r in apps:
    if r["신청상태"] != "확정":
        continue
    ph = r["인화체험"]
    fb = r["식음료"]
    choice["인화체험"][ph] = choice["인화체험"].get(ph, 0) + 1
    choice["식음료"][fb] = choice["식음료"].get(fb, 0) + 1

# ---- 3) 회계 (ACCOUNT-01) ----
# 제1조 기초 잔액: 학교지원금 0, 동아리회비 800000
opening = {"학교지원금": 0, "동아리회비": 800000}
# 제2조 부호: 수입/환불입금 = +, 지출/환불지급 = -
PLUS = {"수입", "환불입금"}
MINUS = {"지출", "환불지급"}

# 재원별 현재 잔액 (전체 행사 E01~E04 합산)
balance = {"학교지원금": opening["학교지원금"], "동아리회비": opening["동아리회비"]}
for r in accts:
    fund = r["재원"]
    typ = r["유형"]
    amt = int(r["금액"])
    if fund not in balance:
        balance[fund] = 0
    if typ in PLUS:
        balance[fund] += amt
    elif typ in MINUS:
        balance[fund] -= amt

# E04 재원별 순지출 = 지출 + 환불지급 - 환불입금 (수입 제외) [ACCOUNT-01 제3조]
e04_net = {"학교지원금": 0, "동아리회비": 0}
for r in accts:
    if r["행사_ID"] != EVENT:
        continue
    fund = r["재원"]
    typ = r["유형"]
    amt = int(r["금액"])
    if fund not in e04_net:
        e04_net[fund] = 0
    if typ == "지출" or typ == "환불지급":
        e04_net[fund] += amt
    elif typ == "환불입금":
        e04_net[fund] -= amt
    # 수입은 순지출에서 제외

# ---- 4) 구매계획 산식 (ACCOUNT-01 제5조) ----
# 참가자 기준: 확정인원 * 계수 * 단가
# 고정 기준: 계수 * 단가
# 시나리오: 확정140 / 승인정원(변경 후 180) / 홍보180 -- 문서 근거로 140,160,180 세 값 모두 계산
scenarios = {"n140_확정": 140, "n160_구정원": 160, "n180_신정원_및_홍보": 180}

def purchase_cost(headcount):
    total = 0
    by_item = []
    by_fund = {}
    for p in plans:
        basis = p["수량기준"]
        coef = int(p["계수"])
        unit = int(p["단가"])
        fund = p["예정재원"]
        if basis == "참가자":
            qty = headcount * coef
        else:  # 고정
            qty = coef
        cost = qty * unit
        total += cost
        by_item.append({"항목_ID": p["항목_ID"], "물품": p["물품"],
                         "수량기준": basis, "수량": qty, "단가": unit,
                         "예정비용": cost, "예정재원": fund})
        by_fund[fund] = by_fund.get(fund, 0) + cost
    return {"총_예정비용": total, "재원별": by_fund, "항목별": by_item}

purchase = {k: purchase_cost(v) for k, v in scenarios.items()}

# ---- 정원 판정 ----
capacity = {
    "구_승인정원_APPROVAL-SPACE-04": 160,
    "신_승인정원_CHANGE-SPACE-04": 180,
    "홍보정원_NOTICE-04": 180,
    "현재_유효_승인정원": 180,
    "확정_인원": confirmed,
    "확정_정원_이내": confirmed <= 180,
}

# ---- 지원금 판정 참고 (RULE-01 / ACCOUNT-01 제4조) ----
flags = []
for r in accts:
    if r["행사_ID"] != EVENT:
        continue
    if r["재원"] != "학교지원금":
        continue
    item = r["항목"]; use = r["용도"]; proof = r["증빙"]; tid = r["거래_ID"]
    if item == "기념품":
        flags.append({"거래_ID": tid, "사유": "기념품은 지원 제외(RULE-01 제3조)", "금액": int(r["금액"])})
    if proof == "없음":
        flags.append({"거래_ID": tid, "사유": "증빙 없음 -> 확인 필요(RULE-01 제4조)", "금액": int(r["금액"])})
    if use.strip() == "" or item == "인화비":
        flags.append({"거래_ID": tid, "사유": "용도 불명확 -> 확인 필요(RULE-01 제4조)", "금액": int(r["금액"])})

result = {
    "행사": EVENT,
    "읽은_행수": {"참가신청": n_apps, "회계내역": n_accts, "구매계획": n_plans},
    "참가상태별_인원": status_count,
    "확정자_선택": choice,
    "기초잔액_ACCOUNT-01_제1조": opening,
    "현재잔액_전체_ACCOUNT-01_제3조": balance,
    "E04_순지출_ACCOUNT-01_제3조": e04_net,
    "정원": capacity,
    "구매계획_시나리오_ACCOUNT-01_제5조": purchase,
    "지원금_확인필요_플래그_RULE-01": flags,
    "확인필요_주석": [
        "잔여 지원금 500,000원은 미입금이라 현재 현금에 미포함(APPROVAL-FUND-04 / RULE-01 제5조).",
        "구매계획 CSV는 예정 비용이며 회계 거래/기지급에 합산하지 않음(ACCOUNT-01 제4조).",
        "대기자(40)는 확정 인원에 미리 합산하지 않음(CLUB-01 제3조).",
    ],
}

out_json = os.path.join(OUT_DIR, "E04_집계.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 콘솔 요약
print("읽은 행수:", result["읽은_행수"])
print("참가상태별:", status_count)
print("확정자 선택:", choice)
print("현재잔액(전체):", balance)
print("E04 순지출:", e04_net)
print("정원:", capacity)
for k, v in purchase.items():
    print(f"구매계획[{k}] 총예정비용={v['총_예정비용']} 재원별={v['재원별']}")
print("지원금 확인필요 플래그 수:", len(flags))
print("JSON 저장:", out_json)
