import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# 1. 데이터 불러오기
# =========================================================

df = pd.read_excel("bd_cd_merge.xlsx")

# 날짜 변환
df["Contract_Date"] = pd.to_datetime(df["Contract_Date"])

# =========================================================
# 2. 2030 고객만 필터링
#    20세 이상 ~ 39세 이하
# =========================================================

df_2030 = df[
    (df["Age"] >= 20) &
    (df["Age"] <= 39)
].copy()

print("2030 전체 계약 건수:", len(df_2030))


# =========================================================
# 3. 상품군 재분류 함수
# =========================================================

def classify_product(row):

    name = str(row["상품명"])
    original = str(row["상품분류"])

    # -----------------------------------------------------
    # 1) 정책 / 청약
    # -----------------------------------------------------
    policy_keywords = [
        "청약",
        "희망",
        "청년",
        "장병",
        "미소드림",
        "미래두배",
        "내일저축",
        "지킴이",
        "연금",
        "퇴직공제",
        "군인",
        "공무원",
        "사학연금"
    ]

    if any(keyword in name for keyword in policy_keywords):
        return "정책/청약"


    # -----------------------------------------------------
    # 2) 기업 / 사업자
    # -----------------------------------------------------
    business_keywords = [
        "사업자",
        "기업",
        "하도급",
        "부가가치세",
        "매입자",
        "당좌"
    ]

    if any(keyword in name for keyword in business_keywords):
        return "기업/사업자"


    # -----------------------------------------------------
    # 3) 입출금통장
    # -----------------------------------------------------
    account_keywords = [
        "통장",
        "보통예금",
        "저축예금",
        "입금전용",
        "증권저축계좌"
    ]

    if (
        original == "요구불예금"
        or any(keyword in name for keyword in account_keywords)
    ):
        return "입출금통장"


    # -----------------------------------------------------
    # 4) 적금
    # -----------------------------------------------------
    if "적금" in name or original == "적금":
        return "적금"


    # -----------------------------------------------------
    # 5) 정기예금
    # -----------------------------------------------------
    deposit_keywords = [
        "정기예금",
        "정기 예금",
        "양도성예금증서",
        "CD",
        "자유적립예금"
    ]

    if (
        any(keyword in name for keyword in deposit_keywords)
        or original == "정기예금"
    ):
        return "정기예금"


    # -----------------------------------------------------
    # 6) 기타
    # -----------------------------------------------------
    return "기타"


df_2030["상품군"] = df_2030.apply(
    classify_product,
    axis=1
)


# 상품군 분포 확인
print("\n=== 상품군별 계약 건수 ===")
print(df_2030["상품군"].value_counts())


# =========================================================
# 4. 월 컬럼 생성
# =========================================================

df_2030["월"] = df_2030["Contract_Date"].dt.month


# =========================================================
# 5. 검증지표 1
#    2030 월별 상품 계약 수
# =========================================================

monthly_contract = (
    df_2030
    .groupby(["월", "상품군"])
    .size()
    .reset_index(name="계약수")
)

# 피벗
monthly_pivot = (
    monthly_contract
    .pivot(
        index="월",
        columns="상품군",
        values="계약수"
    )
    .fillna(0)
)

# 상품 순서
product_order = [
    "적금",
    "정기예금",
    "정책/청약",
    "입출금통장",
    "기타",
    "기업/사업자"
]

# 실제 존재하는 컬럼만 사용
existing_products = [
    x for x in product_order
    if x in monthly_pivot.columns
]

monthly_pivot = monthly_pivot[
    existing_products
]

print("\n=== 월별 계약 수 ===")
display(monthly_pivot)


# =========================================================
# 6. 월별 상품 계약 수 그래프
# =========================================================

plt.figure(figsize=(12, 6))

for product in monthly_pivot.columns:

    if product == "적금":

        # 핵심 상품은 더 강조
        plt.plot(
            monthly_pivot.index,
            monthly_pivot[product],
            marker="o",
            linewidth=2.5,
            label=product
        )

    else:

        plt.plot(
            monthly_pivot.index,
            monthly_pivot[product],
            marker="o",
            alpha=0.5,
            label=product
        )


plt.xticks(
    range(1, 13),
    [f"{m}월" for m in range(1, 13)]
)

plt.xlabel("월")
plt.ylabel("계약 수")
plt.title("2030 월별 상품 계약 수")

plt.legend(
    ncol=6,
    fontsize=8
)

plt.grid(alpha=0.2)

plt.show()


# =========================================================
# 7. 검증지표 2
#    2030 상품군별 중도해지율
# =========================================================

# Cancellation:
# yes = 중도해지
# no = 유지

df_2030["중도해지여부"] = (
    df_2030["Cancellation"]
    .astype(str)
    .str.lower()
    .eq("yes")
    .astype(int)
)


cancel_rate = (
    df_2030
    .groupby("상품군")
    .agg(
        전체계약수=("Acc_ID", "count"),
        중도해지수=("중도해지여부", "sum"),
        중도해지율=("중도해지여부", "mean")
    )
    .reset_index()
)


# 상품 순서 맞추기
cancel_rate["상품군"] = pd.Categorical(
    cancel_rate["상품군"],
    categories=product_order,
    ordered=True
)

cancel_rate = (
    cancel_rate
    .sort_values("상품군")
    .dropna(subset=["상품군"])
)

print("\n=== 상품군별 중도해지율 ===")
display(cancel_rate)


# =========================================================
# 8. 상품군별 중도해지율 그래프
# =========================================================

plt.figure(figsize=(10, 6))

bars = plt.bar(
    cancel_rate["상품군"],
    cancel_rate["중도해지율"]
)

# 막대 위 값 표시
for bar, rate in zip(
    bars,
    cancel_rate["중도해지율"]
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.002,
        f"{rate:.2f}",
        ha="center",
        fontsize=10
    )


plt.xlabel("상품군")
plt.ylabel("중도해지율")
plt.title("2030 상품군별 중도해지율")

plt.ylim(
    0,
    cancel_rate["중도해지율"].max() * 1.2
)

plt.grid(
    axis="y",
    alpha=0.2
)

plt.show()


# =========================================================
# 9. 적금 핵심 수치 확인
# =========================================================

saving_result = cancel_rate[
    cancel_rate["상품군"] == "적금"
]

print("\n=== 적금 결과 ===")
display(saving_result)
