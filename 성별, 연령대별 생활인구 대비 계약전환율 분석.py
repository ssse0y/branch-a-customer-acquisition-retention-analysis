import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# 1. 생활인구 데이터 전처리
# =========================================================

people["기준일ID"] = pd.to_numeric(
    people["기준일ID"],
    errors="coerce"
)

people["기준일ID"] = pd.to_datetime(
    people["기준일ID"].astype("Int64").astype(str),
    format="%Y%m%d",
    errors="coerce"
)

people = people[
    (people["기준일ID"] >= "2024-12-01") &
    (people["기준일ID"] <= "2026-01-31")
].copy()

target_dong = [11200650, 11200690]

people = people[
    people["행정동코드"].isin(target_dong)
].copy()

# =========================================================
# 2. 연령대별 생활인구 컬럼 정의
# =========================================================

age_groups = [
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70+"
]

male_cols = [
    "남자20세부터24세생활인구수",
    "남자25세부터29세생활인구수",
    "남자30세부터34세생활인구수",
    "남자35세부터39세생활인구수",
    "남자40세부터44세생활인구수",
    "남자45세부터49세생활인구수",
    "남자50세부터54세생활인구수",
    "남자55세부터59세생활인구수",
    "남자60세부터64세생활인구수",
    "남자65세부터69세생활인구수",
    "남자70세이상생활인구수"
]

female_cols = [
    "여자20세부터24세생활인구수",
    "여자25세부터29세생활인구수",
    "여자30세부터34세생활인구수",
    "여자35세부터39세생활인구수",
    "여자40세부터44세생활인구수",
    "여자45세부터49세생활인구수",
    "여자50세부터54세생활인구수",
    "여자55세부터59세생활인구수",
    "여자60세부터64세생활인구수",
    "여자65세부터69세생활인구수",
    "여자70세이상생활인구수"
]


# =========================================================
# 3. 두 행정동 합산 → 일자별 평균 생활인구 계산
# =========================================================

# 같은 날짜/시간대의 두 동 생활인구 합산
hourly_people = (
    people
    .groupby(
        ["기준일ID", "시간대구분"],
        as_index=False
    )[male_cols + female_cols]
    .sum()
)

# 24시간 평균 → 일자별 생활인구
daily_people = (
    hourly_people
    .groupby(
        "기준일ID",
        as_index=False
    )[male_cols + female_cols]
    .mean()
)


# =========================================================
# 4. wide → long 형태 변환
#    기준일 / 성별 / 연령대 / 생활인구수
# =========================================================

population_list = []

for age, male_col, female_col in zip(
    age_groups,
    male_cols,
    female_cols
):

    # 남성
    male_temp = daily_people[
        ["기준일ID", male_col]
    ].copy()

    male_temp.columns = [
        "기준일",
        "생활인구수"
    ]

    male_temp["성별"] = "남성"
    male_temp["연령대"] = age

    # 여성
    female_temp = daily_people[
        ["기준일ID", female_col]
    ].copy()

    female_temp.columns = [
        "기준일",
        "생활인구수"
    ]

    female_temp["성별"] = "여성"
    female_temp["연령대"] = age

    population_list.append(male_temp)
    population_list.append(female_temp)


daily_population = pd.concat(
    population_list,
    ignore_index=True
)

daily_population = daily_population[
    ["기준일", "성별", "연령대", "생활인구수"]
]


# =========================================================
# 5. 계약 데이터 불러오기
# =========================================================

contract = pd.read_excel("bd_cd_merge.xlsx")

contract["Contract_Date"] = pd.to_datetime(
    contract["Contract_Date"]
)

# 분석 기간 필터
contract = contract[
    (contract["Contract_Date"] >= "2024-12-01") &
    (contract["Contract_Date"] <= "2026-01-31")
].copy()


# =========================================================
# 6. 계약 데이터 연령대 생성
# =========================================================

bins = [
    20,
    25,
    30,
    35,
    40,
    45,
    50,
    55,
    60,
    65,
    70,
    float("inf")
]

labels = [
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70+"
]

contract["연령대"] = pd.cut(
    contract["Age"],
    bins=bins,
    labels=labels,
    right=False
)

# 날짜만 남기기
contract["기준일"] = (
    contract["Contract_Date"]
    .dt.normalize()
)


# =========================================================
# 7. 일자별 신규 계약 건수 계산
# =========================================================

daily_contract = (
    contract
    .dropna(subset=["연령대"])
    .groupby(
        ["기준일", "Gender", "연령대"],
        observed=True
    )
    .size()
    .reset_index(name="신규계약건수")
)

daily_contract = daily_contract.rename(
    columns={"Gender": "성별"}
)


# =========================================================
# 8. 생활인구 + 계약 데이터 결합
# =========================================================

daily_result = daily_population.merge(
    daily_contract,
    on=["기준일", "성별", "연령대"],
    how="left"
)

daily_result["신규계약건수"] = (
    daily_result["신규계약건수"]
    .fillna(0)
)


# =========================================================
# 9. 일자별 계약전환율 계산
# =========================================================

daily_result["계약전환율"] = (
    daily_result["신규계약건수"]
    / daily_result["생활인구수"]
)


# =========================================================
# 10. 성별 × 연령대별 최종 평균값 생성
# =========================================================

final = (
    daily_result
    .groupby(
        ["성별", "연령대"],
        observed=True,
        as_index=False
    )
    .agg(
        생활인구수=("생활인구수", "mean"),
        신규계약건수_일평균=("신규계약건수", "mean"),
        계약전환율=("계약전환율", "mean")
    )
)

# 보기 좋게 정리
final["생활인구수"] = final["생활인구수"].round(0)

final["신규계약건수_일평균"] = (
    final["신규계약건수_일평균"]
    .round(3)
)

final["계약전환율_pct"] = (
    final["계약전환율"] * 100
).round(3)


# =========================================================
# 11. 최종 표 출력
# =========================================================

print("=== 최종 결과 ===")
display(final)


# =========================================================
# 12. 산점도 생성
# =========================================================

plt.figure(figsize=(10, 7))

for gender in ["남성", "여성"]:

    temp = final[
        final["성별"] == gender
    ]

    plt.scatter(
        temp["생활인구수"],
        temp["계약전환율_pct"],
        s=100,
        label=gender
    )

    for _, row in temp.iterrows():

        plt.text(
            row["생활인구수"] + 20,
            row["계약전환율_pct"],
            f'{row["연령대"]} {row["성별"]}',
            fontsize=8
        )

plt.xlabel("생활인구 수")
plt.ylabel("계약전환율 (%)")
plt.title("생활인구 수 대비 연령대별 계약 전환율")
plt.legend()
plt.grid(alpha=0.3)

plt.show()
