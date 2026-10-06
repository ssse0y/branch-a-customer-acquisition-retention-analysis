# =========================================================
# 2030 월별 적금 신규 계약 건수
# =========================================================

# 적금만 필터링
saving_2030 = df_2030[
    df_2030["상품군"] == "적금"
].copy()

# 월 생성
saving_2030["월"] = saving_2030["Contract_Date"].dt.month

# 월별 신규 계약 건수 집계
monthly_saving = (
    saving_2030
    .groupby("월")
    .size()
    .reindex(range(1, 13), fill_value=0)
    .reset_index(name="신규계약건수")
)


import matplotlib.pyplot as plt

# 월평균
monthly_avg = monthly_saving["신규계약건수"].mean()

plt.figure(figsize=(10, 5))

bars = plt.bar(
    monthly_saving["월"],
    monthly_saving["신규계약건수"]
)

# 월평균 점선
plt.axhline(
    y=monthly_avg,
    linestyle="--",
    linewidth=1.5,
    label=f"월평균 {monthly_avg:.1f}건"
)

plt.xticks(
    range(1, 13),
    [f"{m}월" for m in range(1, 13)]
)

plt.xlabel("월")
plt.ylabel("신규 계약 건수")
plt.title("2030 월별 적금 신규 계약 건수")

plt.legend()

plt.grid(
    axis="y",
    alpha=0.2
)

plt.show()
