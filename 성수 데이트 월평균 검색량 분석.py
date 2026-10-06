import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# 1. 네이버 데이터랩 데이터 불러오기
# =========================================================

# 실제 데이터는 7번째 행(엑셀 기준)부터 시작
df = pd.read_excel(
    "datalab (1).xlsx",
    header=6
)

# 컬럼명 변경
df.columns = ["날짜", "검색량"]

# 날짜 형식 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# 검색량 숫자형 변환
df["검색량"] = pd.to_numeric(
    df["검색량"],
    errors="coerce"
)

# 결측치 제거
df = df.dropna(
    subset=["날짜", "검색량"]
)


# =========================================================
# 2. 연도 / 월 생성
# =========================================================

df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month


# =========================================================
# 3. 월평균 검색량 계산
# =========================================================

monthly_search = (
    df
    .groupby(["연도", "월"], as_index=False)
    .agg(
        월평균검색량=("검색량", "mean")
    )
)

# 보기 좋게 반올림
monthly_search["월평균검색량"] = (
    monthly_search["월평균검색량"]
    .round(2)
)

print("=== 월평균 성수 데이트 검색량 ===")
display(monthly_search)


# =========================================================
# 4. 2024 / 2025 월평균 라인그래프
# =========================================================

plt.figure(figsize=(10, 6))

for year in [2024, 2025]:

    temp = monthly_search[
        monthly_search["연도"] == year
    ]

    plt.plot(
        temp["월"],
        temp["월평균검색량"],
        marker="o",
        linewidth=2,
        label=str(year)
    )


plt.xticks(
    range(1, 13),
    [f"{m}월" for m in range(1, 13)]
)

plt.xlabel("월")
plt.ylabel("월평균 검색량 지수")
plt.title("'성수 데이트' 월평균 검색량 추이")

plt.legend(title="연도")
plt.grid(alpha=0.3)

plt.show()
