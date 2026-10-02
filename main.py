# ============================================================
# GOOG / NVDA BB研究
# Version 3.4.2 - Streamlit軽量化 / 分割版
#
# このファイルは画面表示を担当します。
# 研究計算・データ取得・キャッシュは research_core.py に分離しています。
# ============================================================

from research_core import *

st.title(
    "📊 GOOG・NVDA BB下限研究"
)

st.caption(
    f"Version {APP_VERSION} ｜ "
    "固定ルール・別5年間時間方向検証版 / 再実行高速化"
)
st.caption(
    "v3.4.2は研究条件を変えず、計算キャッシュと画面/研究計算の分割でStreamlitの再実行負荷を軽減します。"
)

st.info(
    "v3.4.1ではv3.3までの研究結果をすべて維持し、売買条件を変更せず時間方向の別5年間検証を追加します。"
    "前5年を2016-10-01～2021-09-30、現5年を2021-10-01～2026-09-30へ完全固定し、GOOG / NVDAへ同じルール・同じコストを適用します。"
    "前5年の結果を見て条件を調整せず、現在5年間で見えた特徴が別時期にも再現するかだけを確認します。"
)

# v2.5.1: 実際の結果は後段で計算されるため、ここに空の表示場所だけ作り、
# 計算完了後にこの位置へ番号選択・コピー欄を描画する。
quick_copy_top_placeholder = st.container()
with quick_copy_top_placeholder:
    st.caption("📋 結果コピー欄は計算完了後にここへ表示されます。")


# ============================================================
# ① 銘柄・期間
# ============================================================

st.subheader(
    "① 銘柄を選択"
)

ticker = st.radio(
    "研究する銘柄",
    options=[
        "GOOG",
        "NVDA",
    ],
    horizontal=True,
)

period_label = st.selectbox(
    "表示するデータ期間",
    options=[
        "1年",
        "2年",
        "5年",
        "10年",
    ],
    index=2,
)

period_map = {
    "1年": "1y",
    "2年": "2y",
    "5年": "5y",
    "10年": "10y",
}

period = period_map[
    period_label
]


# ============================================================
# v2.8 研究用取引コスト設定
# ============================================================

st.subheader(
    "①-2 v2.8 研究用取引コスト設定"
)

cost_col1, cost_col2 = st.columns(2)

with cost_col1:
    commission_percent = st.number_input(
        "売買手数料率（片道・%）",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f",
        key="v28_commission_percent",
        help="EntryとExitそれぞれの約定金額に対してかかる研究用の仮定です。",
    )

with cost_col2:
    slippage_percent = st.number_input(
        "スリッページ率（片道・%）",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f",
        key="v28_slippage_percent",
        help="買いは不利に高く、売りは不利に安く約定する研究用の仮定です。",
    )

commission_rate = float(commission_percent) / 100.0
slippage_rate = float(slippage_percent) / 100.0

st.caption(
    "初期値は手数料0.10%・スリッページ0.10%を片道ごとに置く研究用仮定です。"
    "特定の証券会社の実コストを表すものではなく、画面から変更できます。"
)


# ============================================================
# データ取得
# ============================================================

with st.spinner(
    f"{ticker} の株価データを取得しています..."
):

    df = prepare_data(
        ticker,
        period,
    )


if df.empty:

    st.error(
        f"{ticker} の株価データを取得できませんでした。"
    )

    st.stop()


valid_df = df.dropna(
    subset=[
        "BB_Middle",
        "BB_Upper",
        "BB_Lower",
        "BandWidth",
    ]
).copy()


if valid_df.empty:

    st.error(
        "ボリンジャーバンドを計算するための"
        "十分なデータがありません。"
    )

    st.stop()


latest = valid_df.iloc[-1]
latest_date = valid_df.index[-1]


# ============================================================
# ② 最新状態
# ============================================================

st.divider()

st.subheader(
    f"② {ticker} 最新状態"
)

st.write(
    "データ日：",
    latest_date.strftime(
        "%Y年%m月%d日"
    ),
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "終値",
        f"${format_number(latest['Close'])}",
    )

    st.metric(
        "BB下限",
        f"${format_number(latest['BB_Lower'])}",
    )

with col2:

    st.metric(
        "BandWidth",
        f"{format_number(latest['BandWidth'])}%",
    )

    st.metric(
        "終値→BB下限",
        f"{format_number(latest['Lower_Distance_Close'])}%",
    )

with col3:

    st.metric(
        "前日高値",
        f"${format_number(latest['Prev_High'])}",
    )

    st.write(
        "終値が前日高値を上回る：",
        yes_no(
            latest[
                "Close_Above_Prev_High"
            ]
        ),
    )


# ============================================================
# ③ BB下限との位置
# ============================================================

st.subheader(
    "③ BB下限との位置関係"
)

close_distance = latest[
    "Lower_Distance_Close"
]

low_distance = latest[
    "Lower_Distance_Low"
]

if close_distance < 0:

    st.warning(
        "終値はBB下限より下にあります。"
    )

elif close_distance <= 1:

    st.info(
        "終値はBB下限から1％以内です。"
        "研究上のBB下限付近候補です。"
    )

else:

    st.success(
        "終値はBB下限から1％より離れています。"
    )

if low_distance <= 0:

    st.warning(
        "当日の安値はBB下限に到達、"
        "または下回っています。"
    )

else:

    st.write(
        "当日の安値はBB下限より上です。"
    )

st.caption(
    "1％は正式なエントリー条件ではありません。"
)


# ============================================================
# ④ BandWidth環境
# ============================================================

st.subheader(
    "④ BandWidth・スクイーズ環境"
)

st.write(
    "Squeeze分類：",
    latest[
        "Squeeze_State"
    ],
)

st.write(
    "BandWidth方向：",
    latest[
        "BandWidth_Direction"
    ],
)

if pd.notna(
    latest[
        "Normalized_BandWidth"
    ]
):

    st.metric(
        "正規化BandWidth",
        (
            f"{latest['Normalized_BandWidth'] * 100:.2f}%"
        ),
    )


# ============================================================
# ⑤ BB下限イベント
# ============================================================

st.subheader(
    "⑤ BB下限イベント"
)

st.write(
    "現在のBB下限状態：",
    latest[
        "Lower_Band_Event"
    ],
)

col1, col2 = st.columns(2)

with col1:

    st.write(
        "BB下限タッチ：",
        yes_no(
            latest[
                "BB_Lower_Touch"
            ]
        ),
    )

    st.write(
        "日中BB下限下抜け：",
        yes_no(
            latest[
                "BB_Lower_Intraday_Break"
            ]
        ),
    )

with col2:

    st.write(
        "下抜け後BB内復帰：",
        yes_no(
            latest[
                "BB_Lower_Reclaim"
            ]
        ),
    )

    st.write(
        "BB下限より下で終値：",
        yes_no(
            latest[
                "BB_Lower_Close_Below"
            ]
        ),
    )


# ============================================================
# ⑥ 下落停止候補
# ============================================================

st.subheader(
    "⑥ 下落停止候補"
)

st.write(
    "安値切り上げ：",
    yes_no(
        latest[
            "Higher_Low"
        ]
    ),
)

st.write(
    "前日終値より上昇：",
    yes_no(
        latest[
            "Close_Up"
        ]
    ),
)

st.write(
    "下落停止候補：",
    yes_no(
        latest[
            "Decline_Stop_Combo"
        ]
    ),
)

st.caption(
    "現在の下落停止候補は"
    "『安値切り上げ＋前日終値より上昇』です。"
    "まだ有効性は未検証です。"
)


# ============================================================
# ⑦ 反発開始候補
# ============================================================

st.subheader(
    "⑦ 反発開始候補"
)

st.write(
    "前日高値：",
    f"${format_number(latest['Prev_High'])}",
)

st.write(
    "現在終値：",
    f"${format_number(latest['Close'])}",
)

st.write(
    "終値が前日高値を上回る：",
    yes_no(
        latest[
            "Close_Above_Prev_High"
        ]
    ),
)

if bool(
    latest[
        "Fixed_Window_Rebound_Start_Candidate"
    ]
):

    st.info(
        "現在はBB下限固定観察期間内で、"
        "終値が前日の高値を上回っています。"
        "反発開始候補です。"
    )

else:

    st.write(
        "現在は反発開始候補には"
        "該当していません。"
    )

st.caption(
    "『前日高値を終値で上回る』は研究候補です。"
)


# ============================================================
# ⑧ 固定イベント状態
# ============================================================

st.subheader(
    "⑧ 固定観察イベント"
)

st.write(
    "イベント番号：",
    format_event_id(
        latest[
            "BB_Event_ID"
        ]
    ),
)

st.write(
    "固定観察期間内：",
    yes_no(
        latest[
            "Fixed_Event_Window"
        ]
    ),
)

if pd.notna(
    latest[
        "Days_From_BB_Event_Start"
    ]
):

    st.write(
        "イベント開始から：",
        (
            f"{int(latest['Days_From_BB_Event_Start'])}"
            "営業日目"
        ),
    )

if bool(
    latest[
        "Fixed_Event_Window"
    ]
):

    st.write(
        "観察状態：",
        latest[
            "Event_Observation_Status"
        ],
    )

st.write(
    "イベント最初の下落停止確認：",
    yes_no(
        latest[
            "First_Decline_Stop_In_Event"
        ]
    ),
)

st.write(
    "イベント最初の反発開始確認：",
    yes_no(
        latest[
            "First_Rebound_Start_In_Event"
        ]
    ),
)


# ============================================================
# ⑨ 株価チャート
# ============================================================

st.divider()

st.subheader(
    "⑨ 株価とボリンジャーバンド"
)

max_chart_days = min(
    500,
    len(valid_df),
)

min_chart_days = min(
    60,
    max_chart_days,
)

default_chart_days = min(
    250,
    max_chart_days,
)

if max_chart_days > min_chart_days:

    chart_days = st.slider(
        "チャート表示営業日数",
        min_value=min_chart_days,
        max_value=max_chart_days,
        value=max(
            min_chart_days,
            default_chart_days,
        ),
        step=10,
    )

else:

    chart_days = max_chart_days

price_chart = (
    valid_df[
        [
            "Close",
            "BB_Upper",
            "BB_Middle",
            "BB_Lower",
        ]
    ]
    .tail(chart_days)
    .copy()
)

price_chart.columns = [
    "終値",
    "BB上限",
    "BB中央線",
    "BB下限",
]

st.line_chart(
    price_chart,
    use_container_width=True,
)


# ============================================================
# ⑩ BandWidthチャート
# ============================================================

st.subheader(
    "⑩ BandWidth"
)

bandwidth_chart = (
    valid_df[
        ["BandWidth"]
    ]
    .tail(chart_days)
    .copy()
)

st.line_chart(
    bandwidth_chart,
    use_container_width=True,
)


# ============================================================
# ⑪ 最新30営業日
# ============================================================

st.subheader(
    "⑪ 最新30営業日の状態"
)

display_df = (
    valid_df[
        [
            "Close",
            "Low",
            "Prev_High",
            "BB_Lower",
            "Higher_Low",
            "Close_Up",
            "Decline_Stop_Combo",
            "Close_Above_Prev_High",
            "BB_Event_ID",
            "Days_From_BB_Event_Start",
            "Event_Observation_Status",
            "First_Decline_Stop_In_Event",
            "First_Rebound_Start_In_Event",
        ]
    ]
    .tail(30)
    .copy()
)

display_df.columns = [
    "終値",
    "安値",
    "前日高値",
    "BB下限",
    "安値切上",
    "終値上昇",
    "下落停止条件",
    "前日高値超え",
    "イベントID",
    "開始から営業日",
    "観察状態",
    "最初の下落停止",
    "最初の反発開始",
]

st.dataframe(
    display_df.round(2),
    use_container_width=True,
)


# ============================================================
# 完了イベント準備
# ============================================================

event_start_df = valid_df[
    valid_df[
        "New_BB_Lower_Event"
    ]
].copy()

completed_event_start_df = (
    event_start_df[
        event_start_df[
            "Event_Observation_Complete"
        ]
    ]
    .copy()
)

incomplete_event_start_df = (
    event_start_df[
        ~event_start_df[
            "Event_Observation_Complete"
        ]
    ]
    .copy()
)

completed_event_ids = set(
    completed_event_start_df[
        "BB_Event_ID"
    ]
    .dropna()
    .astype(int)
    .tolist()
)

completed_mask = (
    valid_df[
        "BB_Event_ID"
    ]
    .fillna(-1)
    .astype(int)
    .isin(
        completed_event_ids
    )
)

completed_window_df = (
    valid_df[
        completed_mask
    ]
    .copy()
)

completed_first_stop_df = (
    valid_df[
        completed_mask
        & valid_df[
            "First_Decline_Stop_In_Event"
        ]
    ]
    .copy()
)

completed_first_rebound_df = (
    valid_df[
        completed_mask
        & valid_df[
            "First_Rebound_Start_In_Event"
        ]
    ]
    .copy()
)


# ============================================================
# ⑫ 下落停止集計
# ============================================================

st.subheader(
    "⑫ v1.3.3 基準・下落停止集計"
)

all_event_count = len(
    event_start_df
)

completed_event_count = len(
    completed_event_start_df
)

incomplete_event_count = len(
    incomplete_event_start_df
)

stop_count = len(
    completed_first_stop_df
)

stop_no_count = max(
    0,
    completed_event_count
    - stop_count,
)

if completed_event_count > 0:

    stop_rate = (
        stop_count
        / completed_event_count
        * 100
    )

else:

    stop_rate = np.nan

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "全固定BB下限イベント",
        f"{all_event_count}回",
    )

with col2:
    st.metric(
        "観察完了イベント",
        f"{completed_event_count}回",
    )

with col3:
    st.metric(
        "観察未完了イベント",
        f"{incomplete_event_count}回",
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "下落停止確認",
        f"{stop_count}回",
    )

with col2:
    st.metric(
        "下落停止未確認",
        f"{stop_no_count}回",
    )

with col3:
    st.metric(
        "下落停止確認率",
        (
            "計算不可"
            if pd.isna(stop_rate)
            else f"{stop_rate:.1f}%"
        ),
    )


# ============================================================
# ⑬ 反発開始集計
# ============================================================

st.subheader(
    "⑬ v1.4 反発開始候補のイベント集計"
)

rebound_count = len(
    completed_first_rebound_df
)

rebound_no_count = max(
    0,
    completed_event_count
    - rebound_count,
)

if completed_event_count > 0:

    rebound_rate = (
        rebound_count
        / completed_event_count
        * 100
    )

else:

    rebound_rate = np.nan

rebound_candidate_days = int(
    completed_window_df[
        "Fixed_Window_Rebound_Start_Candidate"
    ].sum()
)

rebound_duplicate_days = max(
    0,
    rebound_candidate_days
    - rebound_count,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "反発開始確認イベント",
        f"{rebound_count}回",
    )

with col2:
    st.metric(
        "反発開始未確認イベント",
        f"{rebound_no_count}回",
    )

with col3:
    st.metric(
        "反発開始確認率",
        (
            "計算不可"
            if pd.isna(rebound_rate)
            else f"{rebound_rate:.1f}%"
        ),
    )

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "反発開始候補日数",
        f"{rebound_candidate_days}日",
    )

with col2:
    st.metric(
        "イベント内の重複候補日",
        f"{rebound_duplicate_days}日",
    )

st.caption(
    "反発開始確認率は勝率ではありません。"
)


# ============================================================
# ⑭ 下落停止 vs 反発開始
# ============================================================

st.subheader(
    "⑭ 下落停止候補 vs 反発開始候補"
)

comparison_rows = []

for event_id in sorted(
    completed_event_ids
):

    event_rows = completed_window_df[
        completed_window_df[
            "BB_Event_ID"
        ]
        == event_id
    ]

    stop_rows = event_rows[
        event_rows[
            "First_Decline_Stop_In_Event"
        ]
    ]

    rebound_rows = event_rows[
        event_rows[
            "First_Rebound_Start_In_Event"
        ]
    ]

    has_stop = not stop_rows.empty
    has_rebound = not rebound_rows.empty

    if has_stop:

        stop_day = int(
            stop_rows.iloc[0][
                "Days_From_BB_Event_Start"
            ]
        )

    else:

        stop_day = np.nan

    if has_rebound:

        rebound_day = int(
            rebound_rows.iloc[0][
                "Days_From_BB_Event_Start"
            ]
        )

    else:

        rebound_day = np.nan

    if (
        has_stop
        and has_rebound
    ):

        if rebound_day > stop_day:
            relation = "反発開始が後"

        elif rebound_day == stop_day:
            relation = "同日"

        else:
            relation = "反発開始が先"

    elif has_stop:
        relation = "下落停止のみ"

    elif has_rebound:
        relation = "反発開始のみ"

    else:
        relation = "両方なし"

    comparison_rows.append(
        {
            "イベントID": event_id,
            "下落停止確認": has_stop,
            "下落停止営業日": stop_day,
            "反発開始確認": has_rebound,
            "反発開始営業日": rebound_day,
            "関係": relation,
        }
    )

comparison_df = pd.DataFrame(
    comparison_rows
)

if comparison_df.empty:

    st.info(
        "比較できる完了イベントがありません。"
    )

else:

    both_count = int(
        (
            comparison_df[
                "下落停止確認"
            ]
            & comparison_df[
                "反発開始確認"
            ]
        ).sum()
    )

    stop_only_count = int(
        (
            comparison_df[
                "下落停止確認"
            ]
            & ~comparison_df[
                "反発開始確認"
            ]
        ).sum()
    )

    rebound_only_count = int(
        (
            ~comparison_df[
                "下落停止確認"
            ]
            & comparison_df[
                "反発開始確認"
            ]
        ).sum()
    )

    neither_count = int(
        (
            ~comparison_df[
                "下落停止確認"
            ]
            & ~comparison_df[
                "反発開始確認"
            ]
        ).sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "両方確認",
            f"{both_count}回",
        )

    with col2:
        st.metric(
            "下落停止のみ",
            f"{stop_only_count}回",
        )

    with col3:
        st.metric(
            "反発開始のみ",
            f"{rebound_only_count}回",
        )

    with col4:
        st.metric(
            "両方なし",
            f"{neither_count}回",
        )


# ============================================================
# ⑮ 反発開始タイミング
# ============================================================

st.subheader(
    "⑮ 反発開始を何営業日目に確認したか"
)

if completed_first_rebound_df.empty:

    st.info(
        "反発開始確認イベントがありません。"
    )

else:

    cols = st.columns(4)

    for day in range(4):

        count = int(
            (
                completed_first_rebound_df[
                    "Days_From_BB_Event_Start"
                ]
                == day
            ).sum()
        )

        label = (
            "0日目"
            if day == 0
            else f"{day}営業日目"
        )

        with cols[day]:

            st.metric(
                label,
                f"{count}回",
            )


# ============================================================
# ⑯ 確認順序
# ============================================================

st.subheader(
    "⑯ 下落停止と反発開始の確認順序"
)

if comparison_df.empty:

    st.info(
        "比較データがありません。"
    )

else:

    labels = [
        "反発開始が後",
        "同日",
        "反発開始が先",
    ]

    cols = st.columns(3)

    for i, label in enumerate(labels):

        count = int(
            (
                comparison_df[
                    "関係"
                ]
                == label
            ).sum()
        )

        with cols[i]:

            st.metric(
                label,
                f"{count}回",
            )

st.caption(
    "『反発開始が先』もエラーではありません。"
    "現在の2条件は独立した研究条件です。"
)


# ============================================================
# ⑰ 下落停止タイミング
# ============================================================

st.subheader(
    "⑰ 下落停止を何営業日目に確認したか"
)

if completed_first_stop_df.empty:

    st.info(
        "下落停止確認イベントがありません。"
    )

else:

    cols = st.columns(4)

    for day in range(4):

        count = int(
            (
                completed_first_stop_df[
                    "Days_From_BB_Event_Start"
                ]
                == day
            ).sum()
        )

        label = (
            "0日目"
            if day == 0
            else f"{day}営業日目"
        )

        with cols[day]:

            st.metric(
                label,
                f"{count}回",
            )


# ============================================================
# ⑱ 反発開始確認時BB状態
# ============================================================

st.subheader(
    "⑱ 反発開始確認時のBB状態"
)

if completed_first_rebound_df.empty:

    st.info(
        "対象データがありません。"
    )

else:

    labels = [
        "BB下限より下で終値",
        "下抜け後BB内復帰",
        "終値はBB内",
    ]

    cols = st.columns(3)

    for i, label in enumerate(labels):

        count = int(
            (
                completed_first_rebound_df[
                    "First_Rebound_BB_State"
                ]
                == label
            ).sum()
        )

        with cols[i]:

            st.metric(
                label,
                f"{count}回",
            )


# ============================================================
# ⑲ イベント比較
# ============================================================

st.subheader(
    "⑲ イベントごとの下落停止・反発開始比較"
)

if comparison_df.empty:

    st.info(
        "比較データがありません。"
    )

else:

    st.dataframe(
        comparison_df.tail(60),
        use_container_width=True,
    )


# ============================================================
# ⑳ 反発開始詳細
# ============================================================

st.subheader(
    "⑳ イベント最初の反発開始確認一覧"
)

if completed_first_rebound_df.empty:

    st.info(
        "反発開始確認イベントがありません。"
    )

else:

    rebound_display = (
        completed_first_rebound_df[
            [
                "BB_Event_ID",
                "BB_Event_Start_Date",
                "Days_From_BB_Event_Start",
                "Open",
                "High",
                "Low",
                "Close",
                "Prev_High",
                "BB_Lower",
                "Close_Above_Prev_High",
                "Higher_Low",
                "Close_Up",
                "Decline_Stop_Combo",
                "BB_Lower_Reclaim",
                "First_Rebound_BB_State",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
            ]
        ]
        .tail(60)
        .copy()
    )

    rebound_display[
        "Normalized_BandWidth"
    ] *= 100

    rebound_display.columns = [
        "イベントID",
        "イベント開始日",
        "確認営業日",
        "始値",
        "高値",
        "安値",
        "終値",
        "前日高値",
        "BB下限",
        "前日高値超え",
        "安値切上",
        "終値上昇",
        "下落停止条件",
        "BB内復帰",
        "反発確認時BB状態",
        "BandWidth %",
        "正規化BW %",
        "BW環境",
    ]

    st.dataframe(
        rebound_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉑ 下落停止未確認
# ============================================================

st.subheader(
    "㉑ 観察完了・下落停止未確認イベント"
)

stop_event_ids = set(
    completed_first_stop_df[
        "BB_Event_ID"
    ]
    .dropna()
    .astype(int)
    .tolist()
)

stop_unconfirmed_df = (
    completed_event_start_df[
        ~completed_event_start_df[
            "BB_Event_ID"
        ]
        .astype(int)
        .isin(
            stop_event_ids
        )
    ]
    .copy()
)

if stop_unconfirmed_df.empty:

    st.info(
        "下落停止未確認イベントはありません。"
    )

else:

    st.dataframe(
        stop_unconfirmed_df[
            [
                "BB_Event_ID",
                "Close",
                "Low",
                "BB_Lower",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
                "Downside_Expansion_State",
            ]
        ]
        .round(2),
        use_container_width=True,
    )


# ============================================================
# ㉒ 反発開始未確認
# ============================================================

st.subheader(
    "㉒ 観察完了・反発開始未確認イベント"
)

rebound_event_ids = set(
    completed_first_rebound_df[
        "BB_Event_ID"
    ]
    .dropna()
    .astype(int)
    .tolist()
)

rebound_unconfirmed_df = (
    completed_event_start_df[
        ~completed_event_start_df[
            "BB_Event_ID"
        ]
        .astype(int)
        .isin(
            rebound_event_ids
        )
    ]
    .copy()
)

if rebound_unconfirmed_df.empty:

    st.info(
        "反発開始未確認イベントはありません。"
    )

else:

    rebound_unconfirmed_display = (
        rebound_unconfirmed_df[
            [
                "BB_Event_ID",
                "Close",
                "Low",
                "BB_Lower",
                "BB_Lower_Reclaim",
                "BB_Lower_Close_Below",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
                "Downside_Expansion_State",
            ]
        ]
        .copy()
    )

    rebound_unconfirmed_display[
        "Normalized_BandWidth"
    ] *= 100

    rebound_unconfirmed_display.columns = [
        "イベントID",
        "開始日終値",
        "開始日安値",
        "開始日BB下限",
        "開始日BB内復帰",
        "開始日BB下終値",
        "BandWidth %",
        "正規化BW %",
        "BW環境",
        "下方向拡大状態",
    ]

    st.dataframe(
        rebound_unconfirmed_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉓ v1.5 / v1.5.1 R設計ルール
# ============================================================

st.divider()

st.subheader(
    "㉓ v1.5 / v1.5.1 R設計ルール"
)

st.write(
    "【正式採用】シグナル確認日の次営業日始値を仮Entry"
)

st.write(
    "【検証中】イベント開始日～シグナル確認日までの最安値を仮Stop"
)

st.write(
    "【計算】1R ＝ 仮Entry − 仮Stop"
)

st.write(
    "【計算】1.5R目標 ＝ Entry ＋ 1.5 × 1R"
)

st.write(
    "【計算】2R目標 ＝ Entry ＋ 2 × 1R"
)

st.write(
    "【除外】Entry ≦ Stop は現在のロングR設計では計算不可"
)

st.write(
    "【v1.5.1 診断】1R率 ＝ 1R ÷ Entry × 100"
)

st.write(
    "【未採用】1R率による除外条件はまだ設定しない"
)

st.warning(
    "v1.6では、R計算可能イベントについて"
    "-1Rと+1.5R / +2Rの先着判定を追加します。"
)


# ============================================================
# ㉔ 下落停止R集計
# ============================================================

st.subheader(
    "㉔ 下落停止・R設計集計"
)

stop_r_all = (
    completed_first_stop_df
    .copy()
)

stop_r_valid = (
    stop_r_all[
        stop_r_all[
            "Stop_R_Valid"
        ]
    ]
    .copy()
)

stop_r_invalid = (
    stop_r_all[
        ~stop_r_all[
            "Stop_R_Valid"
        ]
    ]
    .copy()
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "下落停止確認イベント",
        f"{len(stop_r_all)}回",
    )

with col2:
    st.metric(
        "R計算可能",
        f"{len(stop_r_valid)}回",
    )

with col3:
    st.metric(
        "R計算不可",
        f"{len(stop_r_invalid)}回",
    )


# ============================================================
# ㉕ 反発開始R集計
# ============================================================

st.subheader(
    "㉕ 反発開始・R設計集計"
)

rebound_r_all = (
    completed_first_rebound_df
    .copy()
)

rebound_r_valid = (
    rebound_r_all[
        rebound_r_all[
            "Rebound_R_Valid"
        ]
    ]
    .copy()
)

rebound_r_invalid = (
    rebound_r_all[
        ~rebound_r_all[
            "Rebound_R_Valid"
        ]
    ]
    .copy()
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "反発開始確認イベント",
        f"{len(rebound_r_all)}回",
    )

with col2:
    st.metric(
        "R計算可能",
        f"{len(rebound_r_valid)}回",
    )

with col3:
    st.metric(
        "R計算不可",
        f"{len(rebound_r_invalid)}回",
    )


# ============================================================
# ㉖ 下落停止R詳細
# ============================================================

st.subheader(
    "㉖ 下落停止エントリー・R詳細一覧"
)

if stop_r_all.empty:

    st.info(
        "下落停止確認イベントがありません。"
    )

else:

    stop_r_display = (
        stop_r_all[
            [
                "BB_Event_ID",
                "BB_Event_Start_Date",
                "Days_From_BB_Event_Start",
                "Stop_Signal_Date",
                "Stop_Entry_Date",
                "Stop_Entry_Price",
                "Stop_Stop_Price",
                "Stop_Risk_1R",
                "Stop_Risk_1R_Percent",
                "Stop_Target_1_5R",
                "Stop_Target_2R",
                "Stop_R_Status",
            ]
        ]
        .copy()
    )

    stop_r_display.columns = [
        "イベントID",
        "イベント開始日",
        "確認営業日",
        "シグナル確認日",
        "Entry日",
        "仮Entry",
        "仮Stop",
        "1R",
        "1R率 %",
        "1.5R目標",
        "2R目標",
        "R状態",
    ]

    st.dataframe(
        stop_r_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉗ 反発開始R詳細
# ============================================================

st.subheader(
    "㉗ 反発開始エントリー・R詳細一覧"
)

if rebound_r_all.empty:

    st.info(
        "反発開始確認イベントがありません。"
    )

else:

    rebound_r_display = (
        rebound_r_all[
            [
                "BB_Event_ID",
                "BB_Event_Start_Date",
                "Days_From_BB_Event_Start",
                "Rebound_Signal_Date",
                "Rebound_Entry_Date",
                "Rebound_Entry_Price",
                "Rebound_Stop_Price",
                "Rebound_Risk_1R",
                "Rebound_Risk_1R_Percent",
                "Rebound_Target_1_5R",
                "Rebound_Target_2R",
                "Rebound_R_Status",
            ]
        ]
        .copy()
    )

    rebound_r_display.columns = [
        "イベントID",
        "イベント開始日",
        "確認営業日",
        "シグナル確認日",
        "Entry日",
        "仮Entry",
        "仮Stop",
        "1R",
        "1R率 %",
        "1.5R目標",
        "2R目標",
        "R状態",
    ]

    st.dataframe(
        rebound_r_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉘ 同一イベントR比較
# ============================================================

st.subheader(
    "㉘ 同一イベント・下落停止 vs 反発開始 R比較"
)

stop_compare = (
    stop_r_all[
        [
            "BB_Event_ID",
            "Stop_Entry_Date",
            "Stop_Entry_Price",
            "Stop_Stop_Price",
            "Stop_Risk_1R",
            "Stop_Risk_1R_Percent",
            "Stop_R_Valid",
        ]
    ]
    .copy()
)

rebound_compare = (
    rebound_r_all[
        [
            "BB_Event_ID",
            "Rebound_Entry_Date",
            "Rebound_Entry_Price",
            "Rebound_Stop_Price",
            "Rebound_Risk_1R",
            "Rebound_Risk_1R_Percent",
            "Rebound_R_Valid",
        ]
    ]
    .copy()
)

r_compare_df = pd.merge(
    stop_compare,
    rebound_compare,
    on="BB_Event_ID",
    how="inner",
)

if r_compare_df.empty:

    st.info(
        "両方のシグナルが確認された"
        "同一イベントがありません。"
    )

else:

    r_compare_df[
        "Entry_Difference"
    ] = (
        r_compare_df[
            "Rebound_Entry_Price"
        ]
        - r_compare_df[
            "Stop_Entry_Price"
        ]
    )

    r_compare_df[
        "Risk_Difference"
    ] = (
        r_compare_df[
            "Rebound_Risk_1R"
        ]
        - r_compare_df[
            "Stop_Risk_1R"
        ]
    )

    r_compare_df = (
        r_compare_df.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "Stop_Entry_Date":
                    "下落停止Entry日",

                "Stop_Entry_Price":
                    "下落停止Entry",

                "Stop_Stop_Price":
                    "下落停止Stop",

                "Stop_Risk_1R":
                    "下落停止1R",

                "Stop_Risk_1R_Percent":
                    "下落停止1R率 %",

                "Stop_R_Valid":
                    "下落停止R有効",

                "Rebound_Entry_Date":
                    "反発Entry日",

                "Rebound_Entry_Price":
                    "反発Entry",

                "Rebound_Stop_Price":
                    "反発Stop",

                "Rebound_Risk_1R":
                    "反発1R",

                "Rebound_Risk_1R_Percent":
                    "反発1R率 %",

                "Rebound_R_Valid":
                    "反発R有効",

                "Entry_Difference":
                    "Entry価格差_反発-下落停止",

                "Risk_Difference":
                    "1R差_反発-下落停止",
            }
        )
    )

    st.dataframe(
        r_compare_df.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉙ R計算不可
# ============================================================

st.subheader(
    "㉙ R計算不可の確認"
)

invalid_rows = []

for _, row in (
    stop_r_invalid.iterrows()
):

    invalid_rows.append(
        {
            "種類":
                "下落停止",

            "イベントID":
                int(
                    row[
                        "BB_Event_ID"
                    ]
                ),

            "シグナル日":
                row[
                    "Stop_Signal_Date"
                ],

            "Entry日":
                row[
                    "Stop_Entry_Date"
                ],

            "Entry":
                row[
                    "Stop_Entry_Price"
                ],

            "Stop":
                row[
                    "Stop_Stop_Price"
                ],

            "理由":
                row[
                    "Stop_R_Status"
                ],
        }
    )

for _, row in (
    rebound_r_invalid.iterrows()
):

    invalid_rows.append(
        {
            "種類":
                "反発開始",

            "イベントID":
                int(
                    row[
                        "BB_Event_ID"
                    ]
                ),

            "シグナル日":
                row[
                    "Rebound_Signal_Date"
                ],

            "Entry日":
                row[
                    "Rebound_Entry_Date"
                ],

            "Entry":
                row[
                    "Rebound_Entry_Price"
                ],

            "Stop":
                row[
                    "Rebound_Stop_Price"
                ],

            "理由":
                row[
                    "Rebound_R_Status"
                ],
        }
    )

if invalid_rows:

    invalid_df = pd.DataFrame(
        invalid_rows
    )

    st.dataframe(
        invalid_df.round(2),
        use_container_width=True,
    )

else:

    st.success(
        "対象となったシグナルは"
        "すべてR計算可能です。"
    )


# ============================================================
# v1.5.1 1R率診断表示
# ============================================================

def show_risk_percent_diagnostics(
    title: str,
    data: pd.DataFrame,
    percent_column: str,
    event_id_column: str = "BB_Event_ID",
):

    st.subheader(title)

    diagnostic_df = (
        data[
            data[percent_column].notna()
        ]
        .copy()
    )

    if diagnostic_df.empty:

        st.info(
            "1R率を診断できるイベントがありません。"
        )

        return

    values = diagnostic_df[
        percent_column
    ].astype(float)

    minimum = values.min()
    median = values.median()
    mean = values.mean()
    maximum = values.max()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "最小1R率",
            f"{minimum:.4f}%",
        )

    with col2:
        st.metric(
            "中央値",
            f"{median:.2f}%",
        )

    with col3:
        st.metric(
            "平均",
            f"{mean:.2f}%",
        )

    with col4:
        st.metric(
            "最大1R率",
            f"{maximum:.2f}%",
        )

    # この区分は診断表示だけ。
    # 売買条件・除外条件には使用しない。
    bucket_labels = [
        "1%未満",
        "1%以上～2%未満",
        "2%以上～3%未満",
        "3%以上～5%未満",
        "5%以上",
    ]

    bucket_counts = [
        int((values < 1.0).sum()),
        int(((values >= 1.0) & (values < 2.0)).sum()),
        int(((values >= 2.0) & (values < 3.0)).sum()),
        int(((values >= 3.0) & (values < 5.0)).sum()),
        int((values >= 5.0).sum()),
    ]

    bucket_df = pd.DataFrame(
        {
            "1R率区分": bucket_labels,
            "件数": bucket_counts,
        }
    )

    bucket_df["割合 %"] = (
        bucket_df["件数"]
        / len(values)
        * 100
    )

    st.dataframe(
        bucket_df.round(2),
        use_container_width=True,
        hide_index=True,
    )

    small_r_df = (
        diagnostic_df[
            diagnostic_df[percent_column] < 1.0
        ][
            [
                event_id_column,
                percent_column,
            ]
        ]
        .copy()
    )

    if small_r_df.empty:

        st.success(
            "1R率1％未満のイベントはありません。"
        )

    else:

        small_r_df = small_r_df.sort_values(
            percent_column
        )

        small_r_df.columns = [
            "イベントID",
            "1R率 %",
        ]

        st.write(
            "診断用：1R率1％未満のイベント"
        )

        st.dataframe(
            small_r_df.round(4),
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "1％・2％・3％・5％の区分は分布を見やすくするための診断区分です。"
        "現在の売買条件・除外条件ではありません。"
    )

    # --------------------------------------------------------
    # v1.5.2 コピー用テキスト
    # st.code の右上に表示されるStreamlit標準コピーアイコンで、
    # iPhoneから診断結果をまとめてコピーできるようにする。
    # --------------------------------------------------------

    copy_lines = [
        title,
        f"診断イベント数: {len(values)}回",
        f"最小1R率: {minimum:.4f}%",
        f"中央値: {median:.4f}%",
        f"平均: {mean:.4f}%",
        f"最大1R率: {maximum:.4f}%",
        "",
        "1R率区分,件数,割合%",
    ]

    for _, bucket_row in bucket_df.iterrows():
        copy_lines.append(
            f"{bucket_row['1R率区分']},"
            f"{int(bucket_row['件数'])},"
            f"{float(bucket_row['割合 %']):.2f}"
        )

    copy_lines.append("")

    if small_r_df.empty:
        copy_lines.append(
            "1R率1%未満のイベント: なし"
        )
    else:
        copy_lines.append(
            "1R率1%未満のイベント"
        )
        copy_lines.append(
            "イベントID,1R率%"
        )

        for _, small_row in small_r_df.iterrows():
            copy_lines.append(
                f"{format_event_id(small_row['イベントID'])},"
                f"{float(small_row['1R率 %']):.6f}"
            )

    copy_text = "\n".join(copy_lines)

    st.write(
        "📋 コピー用診断結果"
    )

    st.caption(
        "下の枠の右上にあるコピーアイコンを押すと、"
        "この診断結果をまとめてコピーできます。"
    )

    st.code(
        copy_text,
        language=None,
    )


# ============================================================
# ㉚ 下落停止 1R率診断
# ============================================================

show_risk_percent_diagnostics(
    "㉚ v1.5.2 下落停止・1R率診断",
    stop_r_valid,
    "Stop_Risk_1R_Percent",
)


# ============================================================
# ㉛ 反発開始 1R率診断
# ============================================================

show_risk_percent_diagnostics(
    "㉛ v1.5.2 反発開始・1R率診断",
    rebound_r_valid,
    "Rebound_Risk_1R_Percent",
)


# ============================================================
# v1.6 R先着判定の準備
# ============================================================

first_hit_result_sets = {}

for prefix_name, r_valid_df in [
    ("Stop", stop_r_valid),
    ("Rebound", rebound_r_valid),
]:

    for target_r in [1.5, 2.0]:

        result_parts = []

        for horizon in FIRST_HIT_HORIZONS:

            part = calculate_first_hit_results(
                df,
                r_valid_df,
                prefix_name,
                target_r,
                horizon,
            )

            if not part.empty:
                result_parts.append(part)

        if result_parts:
            combined = pd.concat(
                result_parts,
                ignore_index=True,
            )
        else:
            combined = pd.DataFrame()

        first_hit_result_sets[
            (prefix_name, target_r)
        ] = combined


# ============================================================
# ㉜ v1.6 先着判定ルール
# ============================================================

st.divider()

st.subheader(
    "㉜ v1.6 R先着判定ルール"
)

st.write(
    "【対象】R計算可能イベントのみ。1R率による除外は行いません。"
)

st.write(
    "【開始】シグナル確認後の次営業日始値でEntryし、Entry日を1営業日目とします。"
)

st.write(
    "【比較A】-1R Stop と +1.5R Target のどちらへ先に到達したかを判定します。"
)

st.write(
    "【比較B】-1R Stop と +2R Target のどちらへ先に到達したかを判定します。"
)

st.write(
    "【保有期間】5・10・20営業日を同時に表示し、まだ1つに固定しません。"
)

st.write(
    "【同日両方】OpenがStopとTargetの間にあり、同じ日足でHighがTarget以上かつLowがStop以下なら、順序不明として分離します。"
)

st.write(
    "【ギャップ】保有中の営業日OpenがStop以下ならStop先着、Target以上ならTarget先着として扱います。"
)

st.write(
    "【期間末】決着前にデータが終わり、必要営業日数を観察できない場合は『将来データ不足』として分離します。"
)

st.warning(
    "v1.6のTarget先着・Stop先着は価格水準の到達研究です。"
    "手数料・スリッページ・実際の約定価格を含む最終損益ではありません。"
)


def show_first_hit_section(
    section_title: str,
    results: pd.DataFrame,
):

    st.subheader(section_title)

    if results.empty:
        st.info("対象イベントがありません。")
        return

    summary_df = build_first_hit_summary(
        results
    )

    display_columns = [
        "保有期間",
        "対象",
        "Target先着",
        "Stop先着",
        "同日両方到達・順序不明",
        "期間内未到達",
        "将来データ不足",
    ]

    st.dataframe(
        summary_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    percent_display = summary_df[
        [
            "保有期間",
            "Target先着 %",
            "Stop先着 %",
            "同日両方到達・順序不明 %",
            "期間内未到達 %",
            "将来データ不足 %",
        ]
    ].copy()

    percent_display.columns = [
        "保有期間",
        "Target先着 %",
        "Stop先着 %",
        "同日両方 %",
        "期間内未到達 %",
        "将来データ不足 %",
    ]

    st.write("全対象イベントに対する割合")

    st.dataframe(
        percent_display.round(2),
        use_container_width=True,
        hide_index=True,
    )

    copy_text = make_first_hit_copy_text(
        section_title,
        summary_df,
    )

    st.write("📋 コピー用先着判定結果")

    st.caption(
        "下の枠の右上にあるコピーアイコンから、件数をまとめてコピーできます。"
    )

    st.code(
        copy_text,
        language=None,
    )


# ============================================================
# ㉝ 下落停止 1.5R
# ============================================================

show_first_hit_section(
    "㉝ v1.6 下落停止・1.5R先着判定",
    first_hit_result_sets[("Stop", 1.5)],
)


# ============================================================
# ㉞ 下落停止 2R
# ============================================================

show_first_hit_section(
    "㉞ v1.6 下落停止・2R先着判定",
    first_hit_result_sets[("Stop", 2.0)],
)


# ============================================================
# ㉟ 反発開始 1.5R
# ============================================================

show_first_hit_section(
    "㉟ v1.6 反発開始・1.5R先着判定",
    first_hit_result_sets[("Rebound", 1.5)],
)


# ============================================================
# ㊱ 反発開始 2R
# ============================================================

show_first_hit_section(
    "㊱ v1.6 反発開始・2R先着判定",
    first_hit_result_sets[("Rebound", 2.0)],
)


# ============================================================
# ㊲ 20営業日・イベント詳細
# ============================================================

st.subheader(
    "㊲ v1.6 20営業日・イベント別先着詳細"
)

strategy_label = st.radio(
    "詳細表示するシグナル",
    options=[
        "下落停止",
        "反発開始",
    ],
    horizontal=True,
    key="v16_detail_strategy",
)

target_label = st.radio(
    "詳細表示するTarget",
    options=[
        "+1.5R",
        "+2R",
    ],
    horizontal=True,
    key="v16_detail_target",
)

detail_prefix = (
    "Stop"
    if strategy_label == "下落停止"
    else "Rebound"
)

detail_target_r = (
    1.5
    if target_label == "+1.5R"
    else 2.0
)

detail_results = first_hit_result_sets[
    (detail_prefix, detail_target_r)
]

if detail_results.empty:

    st.info("詳細表示できるイベントがありません。")

else:

    detail_20 = detail_results[
        detail_results["Horizon"] == 20
    ].copy()

    detail_20 = detail_20[
        [
            "BB_Event_ID",
            "Signal_Date",
            "Entry_Date",
            "Entry_Price",
            "Stop_Price",
            "Risk_1R",
            "Risk_1R_Percent",
            "Target_Price",
            "Outcome",
            "Outcome_Date",
            "Outcome_Day",
            "Available_Days",
        ]
    ]

    detail_20.columns = [
        "イベントID",
        "シグナル日",
        "Entry日",
        "Entry",
        "Stop",
        "1R",
        "1R率 %",
        "Target",
        "結果",
        "決着日",
        "Entryから何営業日目",
        "観察可能日数",
    ]

    st.dataframe(
        detail_20.round(4),
        use_container_width=True,
        hide_index=True,
    )

    detail_copy = detail_20.to_csv(
        index=False
    )

    st.write("📋 コピー用20営業日詳細")

    st.code(
        detail_copy,
        language=None,
    )



# ============================================================
# v1.7 R損益の準備
# ============================================================

r_pnl_result_sets = {}

for key, first_hit_results in first_hit_result_sets.items():
    r_pnl_result_sets[key] = calculate_r_pnl_results(
        df,
        first_hit_results,
    )


# ============================================================
# ㊳ v1.7 R損益ルール
# ============================================================

st.divider()

st.subheader(
    "㊳ v1.7 期間末決済を含むR損益ルール"
)

st.write(
    "【Target先着】+1.5Rまたは+2Rとして計算します。"
)

st.write(
    "【Stop先着】-1Rとして計算します。"
)

st.write(
    "【期間内未到達】5・10・20営業日目の終値で決済したと仮定します。"
)

st.write(
    "【期間末R】(期間末終値 − Entry) ÷ 1R で計算します。"
)

st.write(
    "【同日両方到達】日足では順序が分からないため、R損益には入れず別枠のまま残します。"
)

st.write(
    "【将来データ不足】R損益には入れず別枠のまま残します。"
)

st.write(
    "【1R率】全件を本体集計とし、1R率1%以上は参考診断として別表示します。正式フィルターではありません。"
)

st.warning(
    "v1.7の平均Rは手数料・スリッページ前です。"
    "Target / Stop先着時は設定水準で決済したルールベースRとして計算し、"
    "ギャップによる実際の約定価格差はまだ反映しません。"
)


def show_r_pnl_section(
    section_title: str,
    results: pd.DataFrame,
):

    st.subheader(section_title)

    if results is None or results.empty:
        st.info("対象イベントがありません。")
        return

    summary_all = build_r_pnl_summary(
        results
    )

    display_cols = [
        "保有期間",
        "対象",
        "R損益計算可能",
        "Target決済",
        "Stop決済",
        "期間末終値決済",
        "順序不明",
        "データ不足",
        "合計R",
        "平均R",
        "中央値R",
        "プラスR",
        "マイナスR",
        "ゼロR",
    ]

    st.write("全R計算可能イベント")

    st.dataframe(
        summary_all[display_cols].round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用R損益集計")

    st.code(
        make_r_pnl_copy_text(
            section_title,
            summary_all,
        ),
        language=None,
    )

    diagnostic = results[
        pd.to_numeric(
            results["Risk_1R_Percent"],
            errors="coerce",
        ) >= 1.0
    ].copy()

    diagnostic_summary = build_r_pnl_summary(
        diagnostic
    )

    st.write(
        "参考診断：1R率1%以上のみ（正式フィルターではありません）"
    )

    st.dataframe(
        diagnostic_summary[display_cols].round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用・1R率1%以上参考診断")

    st.code(
        make_r_pnl_copy_text(
            f"{section_title}・1R率1%以上参考診断",
            diagnostic_summary,
        ),
        language=None,
    )


# ============================================================
# ㊴ 下落停止 1.5R R損益
# ============================================================

show_r_pnl_section(
    "㊴ v1.7 下落停止・1.5R R損益",
    r_pnl_result_sets[("Stop", 1.5)],
)


# ============================================================
# ㊵ 下落停止 2R R損益
# ============================================================

show_r_pnl_section(
    "㊵ v1.7 下落停止・2R R損益",
    r_pnl_result_sets[("Stop", 2.0)],
)


# ============================================================
# ㊶ 反発開始 1.5R R損益
# ============================================================

show_r_pnl_section(
    "㊶ v1.7 反発開始・1.5R R損益",
    r_pnl_result_sets[("Rebound", 1.5)],
)


# ============================================================
# ㊷ 反発開始 2R R損益
# ============================================================

show_r_pnl_section(
    "㊷ v1.7 反発開始・2R R損益",
    r_pnl_result_sets[("Rebound", 2.0)],
)


# ============================================================
# ㊸ v1.7 20営業日 R損益詳細
# ============================================================

st.subheader(
    "㊸ v1.7 20営業日・イベント別R損益詳細"
)

v17_strategy_label = st.radio(
    "R損益詳細を表示するシグナル",
    options=["下落停止", "反発開始"],
    horizontal=True,
    key="v17_detail_strategy",
)

v17_target_label = st.radio(
    "R損益詳細を表示するTarget",
    options=["+1.5R", "+2R"],
    horizontal=True,
    key="v17_detail_target",
)

v17_prefix = (
    "Stop"
    if v17_strategy_label == "下落停止"
    else "Rebound"
)

v17_target_r = (
    1.5
    if v17_target_label == "+1.5R"
    else 2.0
)

v17_detail = r_pnl_result_sets[
    (v17_prefix, v17_target_r)
]

if v17_detail.empty:
    st.info("R損益詳細を表示できるイベントがありません。")
else:
    v17_detail_20 = v17_detail[
        v17_detail["Horizon"] == 20
    ].copy()

    v17_detail_20 = v17_detail_20[
        [
            "BB_Event_ID",
            "Signal_Date",
            "Entry_Date",
            "Entry_Price",
            "Stop_Price",
            "Risk_1R",
            "Risk_1R_Percent",
            "Target_Price",
            "Outcome",
            "Exit_Type",
            "Exit_Date",
            "Exit_Price",
            "Realized_R",
            "R_PnL_Status",
        ]
    ]

    v17_detail_20.columns = [
        "イベントID",
        "シグナル日",
        "Entry日",
        "Entry",
        "Stop",
        "1R",
        "1R率 %",
        "Target",
        "先着判定",
        "決済方法",
        "決済日",
        "決済価格",
        "R損益",
        "R損益状態",
    ]

    st.dataframe(
        v17_detail_20.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用20営業日R損益詳細")

    st.code(
        v17_detail_20.to_csv(index=False),
        language=None,
    )


# ============================================================
# v1.8 同一イベント・ペア比較の準備
# ============================================================

paired_r_result_sets = {}

for target_r in [1.5, 2.0]:
    paired_r_result_sets[target_r] = build_paired_r_results(
        r_pnl_result_sets[("Stop", target_r)],
        r_pnl_result_sets[("Rebound", target_r)],
    )


# ============================================================
# ㊹ v1.8 ペア比較ルール
# ============================================================

st.divider()

st.subheader(
    "㊹ v1.8 同一イベント・ペア比較ルール"
)

st.write(
    "【対象】下落停止と反発開始の両方でR設計できた同じBB下限イベントだけを比較します。"
)

st.write(
    "【比較条件】同じTarget（1.5Rまたは2R）・同じ保有期間（5・10・20営業日）で比較します。"
)

st.write(
    "【R差】反発開始R − 下落停止R。プラスならそのイベントでは反発開始側、マイナスなら下落停止側のR損益が高かったことを表します。"
)

st.write(
    "【比較不可】どちらか一方でも同日順序不明・データ不足などでR損益を計算できない場合は、ペア差を計算しません。"
)

st.warning(
    "この比較もGOOG / NVDAの選択期間内の過去データによる研究値です。"
    "平均R差がプラス・マイナスでも、その方式を正式採用する判定にはしません。"
)


def show_paired_r_section(
    section_title: str,
    paired_results: pd.DataFrame,
):

    st.subheader(section_title)

    if paired_results is None or paired_results.empty:
        st.info("同一イベントのペア比較対象がありません。")
        return

    summary_all = build_paired_r_summary(
        paired_results
    )

    st.write("全ペアイベント")

    st.dataframe(
        summary_all.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用ペア比較集計")

    st.code(
        make_paired_r_copy_text(
            section_title,
            summary_all,
        ),
        language=None,
    )

    min_event_id = get_min_stop_risk_event_id(
        paired_results
    )

    if min_event_id is not None:
        min_rows = paired_results[
            paired_results["BB_Event_ID"] == min_event_id
        ].copy()

        min_stop_risk = pd.to_numeric(
            min_rows["Risk_1R_Percent_Stop"],
            errors="coerce",
        ).dropna()

        min_rebound_risk = pd.to_numeric(
            min_rows["Risk_1R_Percent_Rebound"],
            errors="coerce",
        ).dropna()

        stop_risk_text = (
            f"{float(min_stop_risk.iloc[0]):.6f}%"
            if not min_stop_risk.empty
            else "N/A"
        )

        rebound_risk_text = (
            f"{float(min_rebound_risk.iloc[0]):.6f}%"
            if not min_rebound_risk.empty
            else "N/A"
        )

        st.write(
            f"参考診断：ペア内で下落停止1R率が最小のイベントID {min_event_id} "
            f"（下落停止 {stop_risk_text} / 反発開始 {rebound_risk_text}）"
        )

        min_detail_cols = [
            "BB_Event_ID",
            "Horizon",
            "Signal_Date_Stop",
            "Entry_Date_Stop",
            "Risk_1R_Percent_Stop",
            "Realized_R_Stop",
            "Signal_Date_Rebound",
            "Entry_Date_Rebound",
            "Risk_1R_Percent_Rebound",
            "Realized_R_Rebound",
            "R_Difference_Rebound_Minus_Stop",
            "Pair_Result",
        ]

        st.dataframe(
            min_rows[min_detail_cols].round(6),
            use_container_width=True,
            hide_index=True,
        )

        without_min = paired_results[
            paired_results["BB_Event_ID"] != min_event_id
        ].copy()

        summary_without_min = build_paired_r_summary(
            without_min
        )

        st.write(
            "参考診断：上の最小1Rイベント1件だけを除いた場合（正式フィルターではありません）"
        )

        st.dataframe(
            summary_without_min.round(4),
            use_container_width=True,
            hide_index=True,
        )

        st.write("📋 コピー用・最小1Rイベント1件除外参考診断")

        st.code(
            make_paired_r_copy_text(
                f"{section_title}・最小1Rイベント1件除外参考診断",
                summary_without_min,
            ),
            language=None,
        )


# ============================================================
# ㊺ 下落停止 vs 反発開始・1.5R ペア比較
# ============================================================

show_paired_r_section(
    "㊺ v1.8 同一イベント・下落停止 vs 反発開始・1.5R",
    paired_r_result_sets[1.5],
)


# ============================================================
# ㊻ 下落停止 vs 反発開始・2R ペア比較
# ============================================================

show_paired_r_section(
    "㊻ v1.8 同一イベント・下落停止 vs 反発開始・2R",
    paired_r_result_sets[2.0],
)


# ============================================================
# ㊼ v1.8 20営業日・ペア詳細
# ============================================================

st.subheader(
    "㊼ v1.8 20営業日・同一イベントR差詳細"
)

v18_target_label = st.radio(
    "ペア詳細を表示するTarget",
    options=["+1.5R", "+2R"],
    horizontal=True,
    key="v18_pair_detail_target",
)

v18_target_r = (
    1.5
    if v18_target_label == "+1.5R"
    else 2.0
)

v18_detail = paired_r_result_sets[
    v18_target_r
].copy()

if v18_detail.empty:
    st.info("ペア詳細を表示できるイベントがありません。")
else:
    v18_detail = v18_detail[
        v18_detail["Horizon"] == 20
    ].copy()

    v18_detail = v18_detail[
        [
            "BB_Event_ID",
            "Signal_Date_Stop",
            "Entry_Date_Stop",
            "Entry_Price_Stop",
            "Risk_1R_Percent_Stop",
            "Exit_Type_Stop",
            "Realized_R_Stop",
            "Signal_Date_Rebound",
            "Entry_Date_Rebound",
            "Entry_Price_Rebound",
            "Risk_1R_Percent_Rebound",
            "Exit_Type_Rebound",
            "Realized_R_Rebound",
            "R_Difference_Rebound_Minus_Stop",
            "Pair_Result",
        ]
    ]

    v18_detail.columns = [
        "イベントID",
        "下落停止シグナル日",
        "下落停止Entry日",
        "下落停止Entry",
        "下落停止1R率 %",
        "下落停止決済",
        "下落停止R",
        "反発開始シグナル日",
        "反発開始Entry日",
        "反発開始Entry",
        "反発開始1R率 %",
        "反発開始決済",
        "反発開始R",
        "R差_反発-下落",
        "ペア結果",
    ]

    st.dataframe(
        v18_detail.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用20営業日ペア詳細")

    st.code(
        v18_detail.to_csv(index=False),
        language=None,
    )


# ============================================================
# v1.9 意思決定比較の準備
# ============================================================

# 方針Bの反発確認シグナル行（完了イベントだけ）
completed_wait_rebound_df = (
    valid_df[
        completed_mask
        & valid_df["Wait_Rebound_After_Stop"]
    ]
    .copy()
)

# 方針BでR設計可能なEntryだけを、既存の先着/R損益関数へ渡す。
wait_rebound_r_valid = (
    completed_wait_rebound_df[
        completed_wait_rebound_df["WaitRebound_R_Valid"]
    ]
    .copy()
)

v19_policy_b_r_pnl_sets = {}

for target_r in [1.5, 2.0]:
    parts = []

    for horizon in FIRST_HIT_HORIZONS:
        first_hit = calculate_first_hit_results(
            df,
            wait_rebound_r_valid,
            "WaitRebound",
            target_r,
            horizon,
        )

        if not first_hit.empty:
            pnl = calculate_r_pnl_results(
                df,
                first_hit,
            )
            if not pnl.empty:
                parts.append(pnl)

    v19_policy_b_r_pnl_sets[target_r] = (
        pd.concat(parts, ignore_index=True)
        if parts
        else pd.DataFrame()
    )

v19_decision_result_sets = {}

for target_r in [1.5, 2.0]:
    all_parts = []

    for horizon in FIRST_HIT_HORIZONS:
        part = build_v19_decision_results(
            completed_first_stop_df,
            r_pnl_result_sets[("Stop", target_r)],
            completed_wait_rebound_df,
            v19_policy_b_r_pnl_sets[target_r],
            horizon,
            target_r,
        )
        if not part.empty:
            all_parts.append(part)

    v19_decision_result_sets[target_r] = (
        pd.concat(all_parts, ignore_index=True)
        if all_parts
        else pd.DataFrame()
    )


# ============================================================
# ㊽ v1.9 意思決定比較ルール
# ============================================================

st.divider()

st.subheader(
    "㊽ v1.9 下落停止時点からの意思決定比較ルール"
)

st.write(
    "【共通の起点】観察完了したBB下限イベントで、下落停止シグナルが確認された時点を1つの意思決定機会とします。"
)

st.write(
    "【方針A】下落停止確認後の次営業日始値でEntryします。v1.5以降の下落停止R設計と同じです。"
)

st.write(
    "【方針B】下落停止を確認した日から固定イベント終了まで反発開始（終値 > 前日高値）を待ちます。確認できれば次営業日始値でEntryします。"
)

st.write(
    "【重要】下落停止より前に反発開始条件が出ていただけのケースは方針Bの確認には使いません。同日成立は待ち0営業日として使います。"
)

st.write(
    "【見送り】固定イベント終了まで反発開始を確認できなければ、イベントを削除せず『見送り = 0R機会』として残します。"
)

st.write(
    "【方針B機会平均R】Entryした取引のR損益に、見送り0Rを含めて意思決定機会全体で平均します。『方針B Entry取引平均R』とは別物です。"
)

st.write(
    "【比較】R差 = 方針B機会R − 方針A R。5・10・20営業日、1.5R・2Rを同じ母集団で比較します。"
)

st.warning(
    "方針Bの見送り0Rは『資金が0%増減した』という意味ではなく、"
    "このBB下限イベントでは取引しなかったという機会ベースの比較値です。"
    "手数料・スリッページ・待機資金の別用途はまだ含めません。"
)


def show_v19_decision_section(
    section_title: str,
    results: pd.DataFrame,
):

    st.subheader(section_title)

    if results is None or results.empty:
        st.info("意思決定比較の対象イベントがありません。")
        return

    summary = build_v19_decision_summary(results)

    st.dataframe(
        summary.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用意思決定比較")

    st.code(
        make_v19_decision_copy_text(
            section_title,
            summary,
        ),
        language=None,
    )


# ============================================================
# ㊾ v1.9 1.5R
# ============================================================

show_v19_decision_section(
    "㊾ v1.9 下落停止でEntry vs 反発開始まで待つ・1.5R",
    v19_decision_result_sets[1.5],
)


# ============================================================
# ㊿ v1.9 2R
# ============================================================

show_v19_decision_section(
    "㊿ v1.9 下落停止でEntry vs 反発開始まで待つ・2R",
    v19_decision_result_sets[2.0],
)


# ============================================================
# v1.9 20営業日・意思決定詳細
# ============================================================

st.subheader(
    "v1.9 20営業日・意思決定イベント詳細"
)

v19_detail_target_label = st.radio(
    "v1.9詳細を表示するTarget",
    options=["+1.5R", "+2R"],
    horizontal=True,
    key="v19_decision_detail_target",
)

v19_detail_target_r = (
    1.5 if v19_detail_target_label == "+1.5R" else 2.0
)

v19_detail = v19_decision_result_sets[v19_detail_target_r].copy()

if v19_detail.empty:
    st.info("v1.9詳細を表示できるイベントがありません。")
else:
    v19_detail = v19_detail[v19_detail["Horizon"] == 20].copy()

    detail_cols = [
        "BB_Event_ID",
        "Stop_Signal_Date",
        "Policy_A_R",
        "Policy_A_Exit_Type",
        "Policy_B_Action",
        "WaitRebound_Signal_Date",
        "Wait_Rebound_Days_From_Stop",
        "Policy_B_Trade_R",
        "Policy_B_Opportunity_R",
        "Policy_B_Exit_Type",
        "Decision_R_Difference_B_Minus_A",
        "Decision_Result",
    ]

    detail_display = v19_detail[detail_cols].copy()
    detail_display.columns = [
        "イベントID",
        "下落停止シグナル日",
        "方針A_R",
        "方針A決済",
        "方針B行動",
        "反発確認日",
        "待ち営業日",
        "方針B_Entry取引R",
        "方針B_機会R",
        "方針B決済",
        "R差_B-A",
        "比較結果",
    ]

    st.dataframe(
        detail_display.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用v1.9 20営業日詳細")
    st.code(detail_display.to_csv(index=False), language=None)


# ============================================================
# v2.0 原因分解
# ============================================================

st.divider()

st.subheader(
    "51 v2.0 v1.9意思決定差の原因分解ルール"
)

st.write(
    "【目的】v1.9で観測された方針Aと方針Bの平均R差が、どのイベントから生じたのかを分解します。新しいEntry条件は追加しません。"
)

st.write(
    "【見送り診断】方針Bが反発未確認で見送ったイベントについて、同じイベントで方針Aなら何Rだったかを残します。"
)

st.write(
    "【待ち日数診断】方針BがEntryしたイベントを、下落停止から反発確認まで0・1・2・3営業日に分けます。"
)

st.write(
    "【差が出たイベント】方針Bが高い / 方針Aが高い / 同じ、の3グループに分けて平均R差を確認します。"
)

st.write(
    "【比較不可診断】v1.9で比較不可だったイベントを、R設計不可・同日順序不明などの理由別に表示します。"
)

st.warning(
    "この分解結果を見てから待ち日数や見送り条件を後付けで売買ルール化すると、過去データへの過適合になり得ます。"
    "v2.0では原因を観察するだけで、正式なフィルターにはしません。"
)


def show_v20_analysis_for_target(target_r: float):
    results = v19_decision_result_sets[target_r]
    target_label = "+1.5R" if np.isclose(target_r, 1.5) else "+2R"

    st.subheader(
        f"52 v2.0 方針Bが見送ったイベント・方針A結果 {target_label}"
    )
    skip_summary = build_v20_skip_summary(results)
    st.dataframe(skip_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・見送りイベント診断")
    st.code(
        make_v20_copy_text(
            f"【v2.0 方針B見送りイベント・方針A結果 {target_label}】",
            skip_summary,
        ),
        language=None,
    )

    st.subheader(
        f"53 v2.0 反発確認までの待ち営業日別診断 {target_label}"
    )
    wait_summary = build_v20_wait_day_summary(results)
    st.dataframe(wait_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・待ち営業日別診断")
    st.code(
        make_v20_copy_text(
            f"【v2.0 待ち営業日別診断 {target_label}】",
            wait_summary,
        ),
        language=None,
    )

    st.subheader(
        f"54 v2.0 A/B結果差グループ診断 {target_label}"
    )
    difference_summary = build_v20_difference_group_summary(results)
    st.dataframe(difference_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・A/B結果差グループ診断")
    st.code(
        make_v20_copy_text(
            f"【v2.0 A/B結果差グループ診断 {target_label}】",
            difference_summary,
        ),
        language=None,
    )

    st.subheader(
        f"55 v2.0 比較不可理由 {target_label}"
    )
    unavailable_summary = build_v20_unavailable_summary(results)
    st.dataframe(unavailable_summary, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・比較不可理由")
    st.code(
        make_v20_copy_text(
            f"【v2.0 比較不可理由 {target_label}】",
            unavailable_summary,
        ),
        language=None,
    )


v20_target_label = st.radio(
    "v2.0 原因分解で表示するTarget",
    options=["+1.5R", "+2R"],
    index=1,
    horizontal=True,
    key="v20_cause_target",
)

v20_target_r = 1.5 if v20_target_label == "+1.5R" else 2.0
show_v20_analysis_for_target(v20_target_r)

# 20営業日の「差が出たイベント」だけを個別確認できる表。
st.subheader(
    f"56 v2.0 20営業日・差が出たイベント詳細 {v20_target_label}"
)

v20_detail_source = v19_decision_result_sets[v20_target_r].copy()
v20_detail = v20_detail_source[
    (v20_detail_source["Horizon"] == 20)
    & v20_detail_source["Decision_Comparison_Valid"]
    & (v20_detail_source["Decision_Result"] != "同じ")
].copy()

if v20_detail.empty:
    st.info("20営業日でA/BのR差が出たイベントはありません。")
else:
    v20_detail_display = v20_detail[
        [
            "BB_Event_ID",
            "Stop_Signal_Date",
            "Policy_A_R",
            "Policy_A_Exit_Type",
            "Policy_B_Action",
            "WaitRebound_Signal_Date",
            "Wait_Rebound_Days_From_Stop",
            "Policy_B_Trade_R",
            "Policy_B_Opportunity_R",
            "Policy_B_Exit_Type",
            "Decision_R_Difference_B_Minus_A",
            "Decision_Result",
        ]
    ].copy()
    v20_detail_display.columns = [
        "イベントID",
        "下落停止シグナル日",
        "方針A_R",
        "方針A決済",
        "方針B行動",
        "反発確認日",
        "待ち営業日",
        "方針B_Entry取引R",
        "方針B_機会R",
        "方針B決済",
        "R差_B-A",
        "比較結果",
    ]
    st.dataframe(v20_detail_display.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・20営業日差イベント詳細")
    st.code(v20_detail_display.to_csv(index=False), language=None)


# ============================================================
# v2.1 下落停止時点の事前情報比較
# ============================================================

st.divider()

st.subheader(
    "57 v2.1 下落停止時点の事前情報比較ルール"
)

st.write(
    "【目的】v2.0で見えた『反発未確認を見送る効果』について、下落停止シグナル日の終値確定時点で既に分かっていた情報に違いがあったかを調べます。"
)

st.write(
    "【重要】結果ラベルは固定イベント終了までの反発確認有無ですが、比較するBB・BandWidth・OHLC情報はすべて下落停止シグナル日までの値だけです。"
)

st.write(
    "【3グループ】同日反発確認 / 後日反発確認 / 反発未確認・見送り に分けます。"
)

st.write(
    "【中心比較】同日反発27件は、下落停止日の時点ですでに反発条件も成立しているため、未来の識別研究から外します。中心比較は『その日はまだ反発していない』イベントだけで、後日反発 vs 見送りを比べます。"
)

st.warning(
    "v2.1は差を発見するための記述統計です。今回のGOOG標本を見て閾値を作り、そのまま同じ標本で有効性を主張することはしません。新しい売買フィルターはまだ採用しません。"
)

v21_signal_df = build_v21_signal_dataset(
    completed_first_stop_df,
    completed_wait_rebound_df,
)

st.subheader(
    "58 v2.1 下落停止45イベントの反発確認グループ"
)

v21_group_summary = build_v21_group_count_summary(v21_signal_df)
st.dataframe(
    v21_group_summary.round(4),
    use_container_width=True,
    hide_index=True,
)
st.write("📋 コピー用・反発確認グループ")
st.code(
    make_v21_copy_text(
        "【v2.1 下落停止45イベントの反発確認グループ】",
        v21_group_summary,
    ),
    language=None,
)

st.subheader(
    "59 v2.1 同日反発を除外・後日反発 vs 見送り 数値事前情報"
)

st.caption(
    "中心比較は、下落停止日に反発開始条件がまだ成立していなかったイベントだけです。後日反発と見送りの差は、売買条件ではなく次の検証候補を探すための観察値です。"
)

v21_numeric_summary = build_v21_numeric_summary(v21_signal_df)
st.dataframe(
    v21_numeric_summary.round(4),
    use_container_width=True,
    hide_index=True,
)
st.write("📋 コピー用・数値事前情報")
st.code(
    make_v21_copy_text(
        "【v2.1 後日反発 vs 見送り・数値事前情報】",
        v21_numeric_summary,
    ),
    language=None,
)

st.subheader(
    "60 v2.1 同日反発を除外・真偽事前情報"
)

v21_boolean_summary = build_v21_boolean_summary(v21_signal_df)
st.dataframe(
    v21_boolean_summary.round(4),
    use_container_width=True,
    hide_index=True,
)
st.write("📋 コピー用・真偽事前情報")
st.code(
    make_v21_copy_text(
        "【v2.1 後日反発 vs 見送り・真偽事前情報】",
        v21_boolean_summary,
    ),
    language=None,
)

st.subheader(
    "61 v2.1 同日反発を除外・状態別事前情報"
)

v21_category_summary = build_v21_category_summary(v21_signal_df)
st.dataframe(
    v21_category_summary.round(4),
    use_container_width=True,
    hide_index=True,
)
st.write("📋 コピー用・状態別事前情報")
st.code(
    make_v21_copy_text(
        "【v2.1 後日反発 vs 見送り・状態別事前情報】",
        v21_category_summary,
    ),
    language=None,
)

st.subheader(
    "62 v2.1 後日反発6件 / 見送り12件・イベント詳細"
)

v21_core_detail = v21_signal_df[
    v21_signal_df["V21_Outcome_Group"].isin(["後日反発確認", "反発未確認・見送り"])
].copy()

if v21_core_detail.empty:
    st.info("中心比較の対象イベントはありません。")
else:
    v21_detail_display = v21_core_detail[
        [
            "BB_Event_ID",
            "V21_Stop_Signal_Date",
            "V21_Outcome_Group",
            "V21_Rebound_Confirm_Date",
            "V21_Wait_Days",
            "Days_From_BB_Event_Start",
            "Lower_Distance_Close",
            "Lower_Distance_Low",
            "BandWidth",
            "Normalized_BandWidth",
            "BandWidth_Change_1D",
            "V21_Close_vs_Prev_High_Pct",
            "V21_Candle_Body_Pct",
            "V21_Close_Location_In_Range_Pct",
            "First_Stop_BB_State",
            "BandWidth_Direction",
            "Squeeze_State",
            "Downside_Expansion_State",
        ]
    ].copy()

    v21_detail_display.columns = [
        "イベントID",
        "下落停止シグナル日",
        "結果グループ",
        "反発確認日",
        "待ち営業日",
        "イベント開始からの日数",
        "終値-BB下限距離_%",
        "安値-BB下限距離_%",
        "BandWidth_%",
        "正規化BandWidth_0to1",
        "BandWidth変化_1D",
        "終値-前日高値距離_%",
        "ローソク実体_%",
        "日中レンジ内終値位置_%",
        "下落停止時BB状態",
        "BandWidth方向",
        "Squeeze状態",
        "下方向拡大状態",
    ]

    st.dataframe(
        v21_detail_display.round(4),
        use_container_width=True,
        hide_index=True,
    )
    st.write("📋 コピー用・v2.1中心比較イベント詳細")
    st.code(
        v21_detail_display.to_csv(index=False, float_format="%.4f"),
        language=None,
    )


# ============================================================
# v2.2 固定イベント終了後の反発確認追跡
# ============================================================

st.divider()

st.subheader(
    "63 v2.2 見送りイベント・固定イベント終了後の追跡ルール"
)

st.write(
    "【目的】v2.1で『反発未確認・見送り』となったイベントが、day0～day3の固定観察窓を過ぎた直後に反発していなかったかを確認します。"
)

st.write(
    "【反発条件】既存と同じ Close > Prev_High を使用します。固定イベント終了日の翌営業日を『終了後1営業日＝元イベントday4』として、最大20営業日先まで最初の成立日を追跡します。"
)

st.write(
    "【重要】これは固定観察窓3日の感度診断です。day4以降の情報を、過去のday3時点のEntry判断へ逆流させません。売買ルールも変更しません。"
)

st.warning(
    "固定イベント終了後に別のBB下限イベントが始まる場合があります。v2.2ではその有無も表示し、後の反発を元イベントだけの効果だと決めつけません。"
)

# v2.2.3: 追跡は全日足 df を使用する。
# 表示用 valid_df や他セクションの一時変数に依存させない。
v22_tracking_df = build_v22_post_window_rebound_tracking(
    df,
    v21_signal_df,
    V22_MAX_FOLLOW_DAYS,
)

st.subheader(
    "64 v2.2 見送りイベント・固定窓終了後N営業日以内の反発確認"
)

v22_horizon_summary = build_v22_horizon_summary(
    v22_tracking_df,
    V22_POST_WINDOW_HORIZONS,
)

st.dataframe(
    v22_horizon_summary.round(4),
    use_container_width=True,
    hide_index=True,
)

st.write("📋 コピー用・固定窓終了後N営業日以内の反発確認")
st.code(
    make_v22_copy_text(
        "【v2.2 見送りイベント・固定窓終了後反発確認】",
        v22_horizon_summary,
    ),
    language=None,
)

st.subheader(
    "65 v2.2 初回反発確認タイミング"
)

v22_timing_summary = build_v22_timing_summary(v22_tracking_df)
st.dataframe(
    v22_timing_summary.round(4),
    use_container_width=True,
    hide_index=True,
)

st.write("📋 コピー用・初回反発確認タイミング")
st.code(
    make_v22_copy_text(
        "【v2.2 見送りイベント・初回反発確認タイミング】",
        v22_timing_summary,
    ),
    language=None,
)

st.subheader(
    "66 v2.2 見送りイベント・固定窓終了後追跡詳細"
)

if v22_tracking_df.empty:
    st.info("v2.2の追跡対象イベントはありません。")
else:
    v22_detail_display = v22_tracking_df[
        [
            "BB_Event_ID",
            "V22_Event_Start_Date",
            "V22_Stop_Signal_Date",
            "V22_Event_End_Date",
            "V22_First_Rebound_Date",
            "V22_Days_After_Event_End",
            "V22_Days_From_Event_Start",
            "V22_Days_From_Stop",
            "V22_Available_Follow_Days",
            "V22_20D_Status",
            "V22_New_BB_Event_Before_Rebound",
            "V22_New_BB_Event_Count_To_Check_End",
        ]
    ].copy()

    v22_detail_display.columns = [
        "イベントID",
        "イベント開始日",
        "下落停止シグナル日",
        "固定イベント終了日",
        "固定窓後の初回反発確認日",
        "固定窓終了後営業日",
        "元イベント基準day",
        "下落停止からの営業日",
        "追跡可能営業日",
        "20営業日追跡状態",
        "反発確認までに新規BBイベントあり",
        "確認終了までの新規BBイベント数",
    ]

    st.dataframe(
        v22_detail_display.round(4),
        use_container_width=True,
        hide_index=True,
    )

    st.write("📋 コピー用・v2.2見送りイベント追跡詳細")
    st.code(
        v22_detail_display.to_csv(index=False, float_format="%.4f"),
        language=None,
    )


# ============================================================
# v2.3 固定窓後の遅い反発Entry研究
# ============================================================

st.divider()

st.subheader(
    "67 v2.3 固定窓後の遅い反発を待つ方針C・研究ルール"
)

st.write(
    "【対象】v2.1で固定day0～day3内に反発確認できず見送ったイベントだけを使います。"
)
st.write(
    "【方針C】固定窓終了後も最大5営業日または10営業日まで待ち、最初に Close > Prev_High を確認した翌営業日OpenでEntryします。"
)
st.write(
    "【Stop】元BBイベントday0から、遅い反発確認日までに付けたLowの最小値です。反発確認より後の安値は使いません。"
)
st.write(
    "【評価】+1.5R / +2R、Entry日を1営業日目として5・10・20営業日を既存の先着判定と期間末R損益で評価します。"
)
st.warning(
    "方針Cは研究候補です。固定窓を正式に延長したわけではありません。また反発までに新しいBB下限イベントが始まったケースは別集計します。"
)

v23_design_df = build_v23_late_rebound_r_design(
    df,
    v22_tracking_df,
)

st.subheader(
    "68 v2.3 遅い反発Entry・R設計詳細"
)

if v23_design_df.empty:
    st.info("v2.3の遅い反発Entry対象はありません。")
else:
    v23_design_display = v23_design_df[
        [
            "BB_Event_ID",
            "V23_Event_Start_Date",
            "V23_Event_End_Date",
            "V23Late_Signal_Date",
            "V23_Days_After_Event_End",
            "V23Late_Entry_Date",
            "V23Late_Entry_Price",
            "V23Late_Stop_Price",
            "V23Late_Risk_1R",
            "V23Late_Risk_1R_Percent",
            "V23Late_Target_1_5R",
            "V23Late_Target_2R",
            "V23Late_R_Status",
            "V23_New_BB_Event_Before_Rebound",
            "V23_New_BB_Event_Count",
        ]
    ].copy()
    v23_design_display.columns = [
        "イベントID",
        "元イベント開始日",
        "固定窓終了日",
        "遅い反発確認日",
        "固定窓終了後営業日",
        "Entry日",
        "Entry価格",
        "Stop価格",
        "1R",
        "1R率_%",
        "1.5R_Target",
        "2R_Target",
        "R設計状態",
        "反発までに新規BBイベントあり",
        "新規BBイベント数",
    ]
    st.dataframe(v23_design_display.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.3遅い反発Entry R設計詳細")
    st.code(v23_design_display.to_csv(index=False, float_format="%.4f"), language=None)

# 遅い反発EntryのR損益を一度だけ計算し、5日待ち/10日待ちの両方で利用する。
v23_pnl_sets = {}
for target_r in [1.5, 2.0]:
    parts = []
    valid_design = (
        v23_design_df[v23_design_df["V23Late_R_Valid"].eq(True)].copy()
        if not v23_design_df.empty else pd.DataFrame()
    )
    for horizon in FIRST_HIT_HORIZONS:
        first_hit = calculate_first_hit_results(
            df,
            valid_design,
            "V23Late",
            target_r,
            horizon,
        )
        if not first_hit.empty:
            pnl = calculate_r_pnl_results(df, first_hit)
            if not pnl.empty:
                parts.append(pnl)
    v23_pnl_sets[target_r] = (
        pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    )


def show_v23_policy_section(section_title, wait_limit, target_r):
    st.subheader(section_title)
    summary = build_v23_policy_summary(
        v22_tracking_df,
        v23_design_df,
        v23_pnl_sets[target_r],
        wait_limit,
        target_r,
    )
    st.dataframe(summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.3方針C R損益")
    st.code(make_v23_copy_text(f"【{section_title}】", summary), language=None)
    return summary


v23_summary_69 = show_v23_policy_section(
    "69 v2.3 方針C・固定窓後5営業日まで待つ・1.5R",
    5,
    1.5,
)

v23_summary_70 = show_v23_policy_section(
    "70 v2.3 方針C・固定窓後5営業日まで待つ・2R",
    5,
    2.0,
)

v23_summary_71 = show_v23_policy_section(
    "71 v2.3 方針C・固定窓後10営業日まで待つ・1.5R",
    10,
    1.5,
)

v23_summary_72 = show_v23_policy_section(
    "72 v2.3 方針C・固定窓後10営業日まで待つ・2R",
    10,
    2.0,
)

st.subheader(
    "73 v2.3 新規BBイベント有無別・10日待ち・20日保有・2R"
)

v23_new_bb_summary = build_v23_new_bb_split_summary(
    v23_design_df,
    v23_pnl_sets[2.0],
    10,
    2.0,
    20,
)
st.dataframe(v23_new_bb_summary.round(4), use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.3新規BBイベント有無別")
st.code(
    make_v23_copy_text(
        "【v2.3 新規BBイベント有無別・10日待ち・20日保有・2R】",
        v23_new_bb_summary,
    ),
    language=None,
)

st.subheader(
    "74 v2.3 遅い反発Entry・10日待ち・20日保有・2R詳細"
)

v23_detail = pd.DataFrame()
if not v23_design_df.empty:
    d = v23_design_df[
        pd.to_numeric(v23_design_df["V23_Days_After_Event_End"], errors="coerce").le(10)
    ].copy()
    p = v23_pnl_sets[2.0]
    if not p.empty:
        p20 = p[p["Horizon"].eq(20)][
            ["BB_Event_ID", "Exit_Type", "Exit_Date", "Realized_R", "R_PnL_Valid", "R_PnL_Status"]
        ].copy()
        p20["BB_Event_ID"] = pd.to_numeric(p20["BB_Event_ID"], errors="coerce").astype("Int64")
        d["BB_Event_ID"] = pd.to_numeric(d["BB_Event_ID"], errors="coerce").astype("Int64")
        d = d.merge(p20, on="BB_Event_ID", how="left", validate="one_to_one")
    v23_detail = d[
        [
            "BB_Event_ID",
            "V23_Event_Start_Date",
            "V23_Event_End_Date",
            "V23Late_Signal_Date",
            "V23_Days_After_Event_End",
            "V23Late_Entry_Date",
            "V23Late_Entry_Price",
            "V23Late_Stop_Price",
            "V23Late_Risk_1R_Percent",
            "V23_New_BB_Event_Before_Rebound",
            "Exit_Type",
            "Exit_Date",
            "Realized_R",
            "R_PnL_Status",
        ]
    ].copy()
    v23_detail.columns = [
        "イベントID",
        "元イベント開始日",
        "固定窓終了日",
        "遅い反発確認日",
        "固定窓終了後営業日",
        "Entry日",
        "Entry価格",
        "Stop価格",
        "1R率_%",
        "反発までに新規BBイベントあり",
        "決済",
        "決済日",
        "実現R",
        "R損益状態",
    ]

if v23_detail.empty:
    st.info("表示対象がありません。")
else:
    st.dataframe(v23_detail.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.3遅い反発Entry詳細")
    st.code(v23_detail.to_csv(index=False, float_format="%.4f"), language=None)


# ============================================================
# v2.4 イベント連結・二重計上診断
# ============================================================

st.divider()

st.subheader(
    "75 v2.4 元イベント→新規BBイベント連結・研究ルール"
)

st.write(
    "【目的】v2.3で『反発までに新規BBイベントあり』となったケースを、元イベントの遅い反発として数えるべきか、新しいBBイベント側の既存反発として扱うべきかを確認します。"
)
st.write(
    "【二重計上チェック】遅い反発確認日が、新規BBイベントのday0～day3固定窓内にあり、そのイベントの『最初の反発開始』と同じ日かを照合します。"
)
st.write(
    "【R設計チェック】同じ反発日・同じ翌営業日Entryでも、v2.3は元イベントday0からStopを作り、既存Reboundは新イベントday0からStopを作るため、1Rが異なる可能性を表示します。"
)
st.warning(
    "v2.4では新しいEntry条件を追加しません。イベントの所属と二重計上だけを診断します。"
)

v24_linkage_df = build_v24_event_linkage(
    df,
    v22_tracking_df,
    v23_design_df,
)

st.subheader(
    "76 v2.4 元見送りイベント・新規BBイベント連結一覧"
)

if v24_linkage_df.empty:
    st.info("v2.4の連結診断対象がありません。")
else:
    v24_linkage_display = v24_linkage_df[
        [
            "元イベントID",
            "元イベント開始日",
            "元固定窓終了日",
            "遅い反発確認日",
            "新規BBイベント数",
            "新規BBイベントID一覧",
            "連結先イベントID",
            "連結先イベント開始日",
            "連結先イベント終了日",
            "連結先観察完了",
            "連結先下落停止日",
            "連結先下落停止day",
            "連結先最初の反発日",
            "連結先反発day",
            "連結先シグナル関係",
            "遅い反発は連結先固定窓内",
            "遅い反発=連結先最初の反発",
        ]
    ].copy()
    st.dataframe(v24_linkage_display.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.4イベント連結一覧")
    st.code(
        make_v24_copy_text(
            "【v2.4 元見送りイベント・新規BBイベント連結一覧】",
            v24_linkage_display,
        ),
        language=None,
    )

st.subheader(
    "77 v2.4 新規BBイベントありケース・連結詳細"
)

v24_linked_only = pd.DataFrame()
if not v24_linkage_df.empty:
    v24_linked_only = v24_linkage_df[
        pd.to_numeric(v24_linkage_df["新規BBイベント数"], errors="coerce").gt(0)
    ].copy()

if v24_linked_only.empty:
    st.info("新規BBイベントありの対象はありません。")
else:
    v24_linked_detail = v24_linked_only[
        [
            "元イベントID",
            "遅い反発確認日",
            "連結先イベントID",
            "連結先イベント開始日",
            "連結先下落停止日",
            "連結先下落停止day",
            "連結先最初の反発日",
            "連結先反発day",
            "連結先シグナル関係",
            "遅い反発は連結先固定窓内",
            "遅い反発=連結先最初の反発",
            "連結先観察完了",
        ]
    ].copy()
    st.dataframe(v24_linked_detail.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.4新規BBイベントあり連結詳細")
    st.code(v24_linked_detail.to_csv(index=False, float_format="%.4f"), language=None)

st.subheader(
    "78 v2.4 二重計上診断サマリー"
)

v24_summary = build_v24_linkage_summary(v24_linkage_df)
st.dataframe(v24_summary, use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.4二重計上診断")
st.code(
    make_v24_copy_text(
        "【v2.4 二重計上診断サマリー】",
        v24_summary,
    ),
    language=None,
)

st.subheader(
    "79 v2.4 同一反発シグナル・元イベントStop vs 新イベントStop"
)

if v24_linked_only.empty:
    st.info("比較対象がありません。")
else:
    v24_r_design_compare = v24_linked_only[
        [
            "元イベントID",
            "連結先イベントID",
            "遅い反発確認日",
            "v2.3_Entry日",
            "連結先Rebound_Entry日",
            "Entry日同一",
            "v2.3_Entry価格",
            "連結先Rebound_Entry価格",
            "Entry価格同一",
            "v2.3_Stop価格",
            "連結先Rebound_Stop価格",
            "Stop価格同一",
            "v2.3_1R率_%",
            "連結先Rebound_1R率_%",
            "連結先Rebound_R設計可能",
            "連結先Rebound_R状態",
        ]
    ].copy()
    st.dataframe(v24_r_design_compare.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.4同一反発シグナルR設計比較")
    st.code(v24_r_design_compare.to_csv(index=False, float_format="%.4f"), language=None)

st.subheader(
    "80 v2.4 イベント連結の扱い"
)
st.write(
    "【検証中】遅い反発が新規BBイベント側の最初の反発と同一なら、独立した2つの反発事例として数えず、同一シグナルの別R設計として扱う候補です。"
)
st.write(
    "【未採用】新規BBイベントありをEntry条件にはしません。件数が少なく、同じ標本から条件を作ると過去データへの合わせ込みになるためです。"
)
st.write(
    "【確認済み】77～79番で、新規BBイベントありケースの同一反発シグナル重複を確認しました。v2.5で新イベント基準へリセットして再計算します。"
)

# ============================================================
# v2.5 新BBイベント発生時リセット方式
# ============================================================

st.divider()

st.subheader(
    "81 v2.5 新BBイベント発生時リセット方式・研究ルール"
)
st.write(
    "【目的】固定窓終了後に新しいBB下限イベントが発生したら、旧イベントの延長追跡を終了し、新イベントを独立した通常イベントとして評価し直します。"
)
st.write(
    "【新イベントあり】旧イベントの遅い反発としては数えず、新イベント側の最初の反発・新イベントday0起点Stopを使用します。"
)
st.write(
    "【新イベントなし】固定窓後の遅い反発を旧イベントの延長として残し、v2.3と同じR設計を使用します。"
)
st.write(
    "【二重計上防止】実効イベントIDと反発シグナル日が同一なら1取引だけ残します。"
)
st.warning(
    "v2.5はイベント定義の研究です。新BBイベント発生をEntry条件として正式採用するものではありません。"
)

v25_design_df = build_v25_reset_r_design(
    df,
    v24_linkage_df,
    v23_design_df,
)

st.subheader(
    "82 v2.5 リセット後・重複除去済み実効イベント一覧"
)
if v25_design_df.empty:
    st.info("v2.5の対象イベントがありません。")
else:
    v25_design_display = v25_design_df[
        [
            "V25_Source_Event_ID",
            "V25_Effective_Event_ID",
            "V25_Mode",
            "V25_Source_Event_Start_Date",
            "V25_Effective_Event_Start_Date",
            "V25Reset_Signal_Date",
            "V25Reset_Entry_Date",
            "V25Reset_Entry_Price",
            "V25Reset_Stop_Price",
            "V25Reset_Risk_1R_Percent",
            "V25Reset_R_Valid",
            "V25Reset_R_Status",
            "V25_Duplicate_Count",
        ]
    ].copy()
    v25_design_display.columns = [
        "元イベントID",
        "実効イベントID",
        "扱い",
        "元イベント開始日",
        "実効イベント開始日",
        "反発確認日",
        "Entry日",
        "Entry価格",
        "Stop価格",
        "1R率_%",
        "R設計可能",
        "R設計状態",
        "同一実効シグナル重複数",
    ]
    st.dataframe(v25_design_display.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.5実効イベント一覧")
    st.code(v25_design_display.to_csv(index=False, float_format="%.4f"), language=None)

v25_pnl_sets = {}
for target_r in [1.5, 2.0]:
    parts = []
    valid_design = (
        v25_design_df[v25_design_df["V25Reset_R_Valid"].eq(True)].copy()
        if not v25_design_df.empty else pd.DataFrame()
    )
    for horizon in FIRST_HIT_HORIZONS:
        first_hit = calculate_first_hit_results(
            df,
            valid_design,
            "V25Reset",
            target_r,
            horizon,
        )
        if not first_hit.empty:
            pnl = calculate_r_pnl_results(df, first_hit)
            if not pnl.empty:
                parts.append(pnl)
    v25_pnl_sets[target_r] = (
        pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    )

st.subheader(
    "83 v2.5 リセット方式・1.5R"
)
v25_summary_15 = build_v25_reset_summary(
    v25_design_df,
    v25_pnl_sets[1.5],
    1.5,
)
st.dataframe(v25_summary_15.round(4), use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.5リセット方式1.5R")
st.code(
    make_v25_copy_text(
        "【83 v2.5 リセット方式・1.5R】",
        v25_summary_15,
    ),
    language=None,
)

st.subheader(
    "84 v2.5 リセット方式・2R"
)
v25_summary_20 = build_v25_reset_summary(
    v25_design_df,
    v25_pnl_sets[2.0],
    2.0,
)
st.dataframe(v25_summary_20.round(4), use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.5リセット方式2R")
st.code(
    make_v25_copy_text(
        "【84 v2.5 リセット方式・2R】",
        v25_summary_20,
    ),
    language=None,
)

st.subheader(
    "85 v2.5 v2.3旧イベント基準 vs リセット基準・20日保有・2R"
)
v25_compare_20_2r = build_v25_compare_v23_v25(
    v23_design_df,
    v23_pnl_sets[2.0],
    v25_design_df,
    v25_pnl_sets[2.0],
    horizon=20,
    target_r=2.0,
)
if v25_compare_20_2r.empty:
    st.info("比較対象がありません。")
else:
    st.dataframe(v25_compare_20_2r.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.3 vs v2.5 20日2R比較")
    st.code(v25_compare_20_2r.to_csv(index=False, float_format="%.4f"), language=None)

st.subheader(
    "86 v2.5 リセット方式の扱い"
)
st.write(
    "【研究上の整理】新イベントありは旧イベントの遅い反発と二重に数えず、新イベント側のR設計へ一本化します。"
)
st.write(
    "【検証中】新イベントなしの遅い反発6件と、新イベントへリセットしたケースを同じ売買ルールとして運用すべきかは未確定です。"
)
st.write(
    "【未採用】v2.5リセット方式を実運用Entryルールとして採用すること。"
)


# ============================================================
# v2.6 独立BBイベント台帳
# ============================================================

st.divider()

st.subheader(
    "87 v2.6 独立BBイベント台帳・研究ルール"
)
st.write(
    "【正式採用・研究データ管理】1つの観察完了BBイベントを1つの独立した研究単位として扱います。"
)
st.write(
    "【イベント境界】最初のBB下限タッチをday0とし、day0～day3の固定窓だけをそのイベント自身の観察期間とします。"
)
st.write(
    "【二重計上防止】固定窓後の遅い反発は元イベントへ追加しません。新しいBB下限イベントが始まれば、新しいイベントIDの別イベントとしてのみ記録します。"
)
st.write(
    "【R結果】台帳には固定窓内で確認された下落停止・反発開始について、既存の20営業日・2R結果を横並びで記録します。"
)
st.warning(
    "v2.6は研究母集団の整理です。下落停止・反発開始・新イベント発生のどれかを正式な売買条件として採用する変更ではありません。"
)

v26_ledger = build_v26_event_ledger(
    df,
    completed_event_start_df,
    r_pnl_result_sets[("Stop", 2.0)],
    r_pnl_result_sets[("Rebound", 2.0)],
)

v26_audit_summary = build_v26_audit_summary(
    v26_ledger,
    completed_event_start_df,
)

st.subheader(
    "88 v2.6 独立BBイベント台帳・監査サマリー"
)
st.dataframe(v26_audit_summary, use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.6独立イベント監査")
st.code(
    make_v26_copy_text(
        "【88 v2.6 独立BBイベント台帳・監査サマリー】",
        v26_audit_summary,
    ),
    language=None,
)

st.subheader(
    "89 v2.6 独立BBイベント台帳・全イベント"
)
if v26_ledger.empty:
    st.info("観察完了した独立BBイベントがありません。")
else:
    st.dataframe(v26_ledger.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.6独立BBイベント台帳")
    st.code(
        make_v26_copy_text(
            "【89 v2.6 独立BBイベント台帳・全イベント】",
            v26_ledger,
        ),
        language=None,
    )

v26_type_summary = build_v26_event_type_summary(v26_ledger)
st.subheader(
    "90 v2.6 独立BBイベント・シグナル構成"
)
st.dataframe(v26_type_summary.round(4), use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.6イベント種別")
st.code(
    make_v26_copy_text(
        "【90 v2.6 独立BBイベント・シグナル構成】",
        v26_type_summary,
    ),
    language=None,
)

v26_20d_2r_summary = build_v26_20d_2r_summary(v26_ledger)
st.subheader(
    "91 v2.6 独立BBイベント・20日保有・2R集計"
)
st.dataframe(v26_20d_2r_summary.round(4), use_container_width=True, hide_index=True)
st.write("📋 コピー用・v2.6独立イベント20日2R")
st.code(
    make_v26_copy_text(
        "【91 v2.6 独立BBイベント・20日保有・2R集計】",
        v26_20d_2r_summary,
    ),
    language=None,
)

st.subheader(
    "92 v2.6 旧延長追跡の扱い"
)
st.write(
    "【研究母集団から分離】v2.2～v2.5の固定窓後追跡は、観察窓の感度と二重計上を確認する診断履歴として残します。"
)
st.write(
    "【正式採用・研究データ管理】今後の基本集計では89番の独立イベント台帳を母集団とし、旧イベントの固定窓後反発を同じイベントへ追加しません。"
)
st.write(
    "【未採用】固定窓後の遅い反発をEntry条件として使うこと。"
)


# ============================================================
# v2.7 ギャップ時の実約定差をR損益へ反映
# ============================================================

st.divider()

st.subheader(
    "93 v2.7 ギャップ約定差反映・研究ルール"
)
st.write(
    "【目的】Stop / Target到達日の寄り付きが設定価格を飛び越えた場合、従来の固定-1R / +Target Rではなく、その日のOpenを決済価格としてR損益を再計算します。"
)
st.write(
    "【Stopギャップ】OpenがStopより下なら、そのOpenで決済したと仮定するため損失は-1Rを下回る場合があります。"
)
st.write(
    "【Targetギャップ】OpenがTargetより上なら、そのOpenで決済したと仮定するため利益は+2Rを上回る場合があります。"
)
st.write(
    "【日中到達】OpenがStopとTargetの間にあり日中に水準へ到達した場合は、従来どおり設定Stop / Target価格で決済します。"
)
st.write(
    "【期間末】期間内未到達は従来どおり指定保有期間の終値で決済します。"
)
st.warning(
    "v2.7はギャップ時のOpen約定差だけを反映します。手数料・スリッページ・板状況はまだ含めないため、最終的な実運用損益ではありません。"
)

v27_gap_pnl_sets = {}
for key, first_hit_results in first_hit_result_sets.items():
    v27_gap_pnl_sets[key] = calculate_gap_aware_r_pnl_results(
        df,
        first_hit_results,
    )

v27_gap_compare_parts = []
for prefix_name, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
    part = build_v27_gap_comparison_summary(
        r_pnl_result_sets[(prefix_name, 2.0)],
        v27_gap_pnl_sets[(prefix_name, 2.0)],
        label,
    )
    if not part.empty:
        v27_gap_compare_parts.append(part)

v27_gap_compare_summary = (
    pd.concat(v27_gap_compare_parts, ignore_index=True)
    if v27_gap_compare_parts else pd.DataFrame()
)

st.subheader(
    "94 v2.7 2R・ギャップ反映前後比較"
)
if v27_gap_compare_summary.empty:
    st.info("ギャップ比較対象がありません。")
else:
    st.dataframe(v27_gap_compare_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.7ギャップ反映前後比較")
    st.code(
        "【94 v2.7 2R・ギャップ反映前後比較】\n"
        + v27_gap_compare_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v27_changed_parts = []
for prefix_name, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
    part = build_v27_gap_changed_detail(
        r_pnl_result_sets[(prefix_name, 2.0)],
        v27_gap_pnl_sets[(prefix_name, 2.0)],
        label,
        horizon=20,
    )
    if not part.empty:
        v27_changed_parts.append(part)

v27_gap_changed_20d = (
    pd.concat(v27_changed_parts, ignore_index=True)
    if v27_changed_parts else pd.DataFrame()
)

st.subheader(
    "95 v2.7 20日保有・2R・ギャップでRが変化したイベント"
)
if v27_gap_changed_20d.empty:
    st.info("20日保有・2Rでは、ギャップによってR損益が変化したイベントはありません。")
else:
    st.dataframe(v27_gap_changed_20d.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.7ギャップ差イベント")
    st.code(
        "【95 v2.7 20日保有・2R・ギャップでRが変化したイベント】\n"
        + v27_gap_changed_20d.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "96 v2.7 ギャップ反映の扱い"
)
st.write(
    "【研究計算を改善】Stop / TargetをOpenで飛び越えた場合は、Openを決済価格としてR損益へ反映します。"
)
st.write(
    "【維持】同日Stop/Target両方到達で順序不明のケースは、引き続きR損益から除外します。"
)
st.write(
    "【v2.7時点では未実装 → v2.8で実装】手数料・スリッページを含むネットR損益。"
)
st.write(
    "【未採用】ギャップ結果を見てEntry条件・Stop条件・Target条件を変更すること。"
)


# ============================================================
# v2.8 手数料・スリッページ反映 Net R
# ============================================================

st.divider()

st.subheader(
    "97 v2.8 取引コスト反映・研究ルール"
)
st.write(
    f"【現在の研究設定】売買手数料は片道 {commission_percent:.2f}%、スリッページは片道 {slippage_percent:.2f}% です。"
)
st.write(
    "【Entry】買いのスリッページは不利な方向へ加算し、Entry価格を高くして計算します。"
)
st.write(
    "【Exit】売りのスリッページは不利な方向へ減算し、ギャップ反映後のExit価格を低くして計算します。"
)
st.write(
    "【手数料】EntryとExitそれぞれのコスト反映約定金額に、設定した片道手数料率を適用します。"
)
st.write(
    "【R基準】Net Rの分母は従来の計画時1Rを維持します。したがって、取引コストが元の1Rを何R消費したかを直接比較できます。"
)
st.warning(
    "このコスト設定は研究用仮定です。板・出来高・部分約定・税金・為替コストなどは含みません。"
)

v28_net_pnl_sets = {}
for key, gap_results in v27_gap_pnl_sets.items():
    v28_net_pnl_sets[key] = calculate_v28_net_cost_results(
        gap_results,
        commission_rate=commission_rate,
        slippage_rate=slippage_rate,
    )

v28_cost_compare_parts = []
for prefix_name, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
    part = build_v28_cost_comparison_summary(
        v28_net_pnl_sets[(prefix_name, 2.0)],
        label,
        commission_rate,
        slippage_rate,
    )
    if not part.empty:
        v28_cost_compare_parts.append(part)

v28_cost_compare_summary = (
    pd.concat(v28_cost_compare_parts, ignore_index=True)
    if v28_cost_compare_parts else pd.DataFrame()
)

st.subheader(
    "98 v2.8 2R・ギャップ反映Gross vs コスト後Net比較"
)
if v28_cost_compare_summary.empty:
    st.info("コスト比較対象がありません。")
else:
    st.dataframe(v28_cost_compare_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.8 Gross vs Net比較")
    st.code(
        "【98 v2.8 2R・ギャップ反映Gross vs コスト後Net比較】\n"
        + v28_cost_compare_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v28_cost_detail_parts = []
for prefix_name, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
    part = build_v28_cost_detail(
        v28_net_pnl_sets[(prefix_name, 2.0)],
        label,
        horizon=20,
    )
    if not part.empty:
        v28_cost_detail_parts.append(part)

v28_cost_detail_20d = (
    pd.concat(v28_cost_detail_parts, ignore_index=True)
    if v28_cost_detail_parts else pd.DataFrame()
)

st.subheader(
    "99 v2.8 20日保有・2R・イベント別コスト後Net R"
)
if v28_cost_detail_20d.empty:
    st.info("20日保有・2Rのコスト詳細対象がありません。")
else:
    st.dataframe(v28_cost_detail_20d.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.8イベント別Net R")
    st.code(
        "【99 v2.8 20日保有・2R・イベント別コスト後Net R】\n"
        + v28_cost_detail_20d.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "100 v2.8 取引コスト反映の扱い"
)
st.write(
    "【研究計算を改善】v2.7のギャップ反映Exitを土台に、Entry / Exit双方へ手数料とスリッページを反映します。"
)
st.write(
    "【比較維持】Gross Rも残すため、コストだけで何R減ったかを確認できます。"
)
st.write(
    "【設定変更可能】画面上部の①-2で手数料率とスリッページ率を変更できます。0.00%にすれば該当コストを無効化できます。"
)
st.write(
    "【未実装】板・出来高・部分約定・税金・為替コストを含む実運用約定モデル。"
)
st.write(
    "【未採用】コスト結果を見てEntry / Stop / Target条件を後付け変更すること。"
)


# ============================================================
# v2.9 固定時系列分割・Net R安定性診断
# ============================================================

st.divider()

st.subheader(
    "101 v2.9 固定時系列分割・研究ルール"
)
st.write(
    "【固定分割】v2.6の独立BBイベント台帳をイベント開始日順に並べ、前半=floor(N/2)、後半=残りとして機械的に分けます。"
)
st.write(
    "【共通境界】下落停止と反発開始で別々の境界は作りません。55件の独立イベント母集団に対して同じ前半 / 後半を使います。"
)
st.write(
    "【条件固定】Entry / Stop / Target / ギャップ約定 / 手数料 / スリッページはv2.8と同じままです。"
)
st.warning(
    "後半データもこれまでの研究で既に見ているため、これは真の未使用OOS検証ではありません。過去結果の時系列安定性を診断するための分割です。"
)

v29_split_master, v29_split_audit = build_v29_time_split_master(v26_ledger)

st.subheader(
    "102 v2.9 固定時系列分割・監査サマリー"
)
if v29_split_audit.empty:
    st.info("時系列分割の監査対象がありません。")
else:
    st.dataframe(v29_split_audit, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.9時系列分割監査")
    st.code(
        "【102 v2.9 固定時系列分割・監査サマリー】\n"
        + v29_split_audit.to_csv(index=False, date_format="%Y-%m-%d").rstrip(),
        language=None,
    )

v29_time_summary_parts = []
for prefix_name, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
    part = build_v29_time_split_net_summary(
        v28_net_pnl_sets[(prefix_name, 2.0)],
        v29_split_master,
        label,
    )
    if not part.empty:
        v29_time_summary_parts.append(part)

v29_time_summary = (
    pd.concat(v29_time_summary_parts, ignore_index=True)
    if v29_time_summary_parts else pd.DataFrame()
)

st.subheader(
    "103 v2.9 2R・コスト後Net R・前半後半比較"
)
if v29_time_summary.empty:
    st.info("時系列比較対象がありません。")
else:
    st.dataframe(v29_time_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.9前半後半Net R")
    st.code(
        "【103 v2.9 2R・コスト後Net R・前半後半比較】\n"
        + v29_time_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v29_20d_difference = build_v29_20d_difference(v29_time_summary)

st.subheader(
    "104 v2.9 20日保有・2R・前半→後半差"
)
if v29_20d_difference.empty:
    st.info("20日保有・2Rの前半後半比較対象がありません。")
else:
    st.dataframe(v29_20d_difference.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v2.9 20日2R前半後半差")
    st.code(
        "【104 v2.9 20日保有・2R・前半→後半差】\n"
        + v29_20d_difference.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "105 v2.9 時系列分割の扱い"
)
st.write(
    "【診断目的】全期間平均がプラスでも、前半または後半の一方だけで作られていないかを確認します。"
)
st.write(
    "【未採用】前半 / 後半の結果を見て、良かった期間だけを選んだりEntry条件を後付け変更したりすること。"
)
st.write(
    "【v3.1】GOOG / NVDAの20日2Rを、Target・Stop・期間末・ギャップ別に分解して銘柄差の中身を確認します。"
)




# ============================================================
# v3.0 GOOG / NVDA 同一ルール・同一コスト比較
# ============================================================

st.divider()

st.subheader(
    "106 v3.0 GOOG / NVDA 銘柄横断・研究ルール"
)
st.write(
    f"【同一期間】画面上部で選択中の {period_label} をGOOG / NVDAの両方へ使用します。"
)
st.write(
    "【条件固定】BBイベント、下落停止、反発開始、翌営業日Open Entry、イベント起点Stop、2R Targetを両銘柄で変更しません。"
)
st.write(
    f"【同一コスト】両銘柄とも片道手数料 {commission_percent:.2f}%、片道スリッページ {slippage_percent:.2f}% を使用します。"
)
st.write(
    "【同一約定処理】Stop / Targetのギャップはv2.7と同じOpen約定、Net Rはv2.8と同じ計算です。"
)
st.warning(
    "NVDAの結果を見てからNVDAだけ条件を変えることはしません。v3.0は銘柄横断の再現性診断であり、正式な売買条件の採用判定ではありません。"
)

v30_bundles = {}
for v30_symbol in ["GOOG", "NVDA"]:
    with st.spinner(f"v3.0: {v30_symbol} を同一ルールで計算しています..."):
        v30_prepared = df if v30_symbol == ticker else prepare_data(v30_symbol, period)
        v30_bundles[v30_symbol] = build_v30_ticker_bundle(
            v30_symbol,
            v30_prepared,
            commission_rate,
            slippage_rate,
        )

v30_audit = build_v30_cross_ticker_audit(v30_bundles, period_label)

st.subheader(
    "107 v3.0 GOOG / NVDA 同一ルール・監査サマリー"
)
if v30_audit.empty:
    st.info("銘柄横断監査の対象がありません。")
else:
    st.dataframe(v30_audit, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.0銘柄横断監査")
    st.code(
        "【107 v3.0 GOOG / NVDA 同一ルール・監査サマリー】\n"
        + v30_audit.to_csv(index=False, date_format="%Y-%m-%d").rstrip(),
        language=None,
    )

v30_net_summary = build_v30_cross_ticker_net_summary(v30_bundles)

st.subheader(
    "108 v3.0 GOOG / NVDA 2R・コスト後Net R比較"
)
if v30_net_summary.empty:
    st.info("GOOG / NVDAのNet R比較対象がありません。")
else:
    st.dataframe(v30_net_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.0 GOOG / NVDA Net R比較")
    st.code(
        "【108 v3.0 GOOG / NVDA 2R・コスト後Net R比較】\n"
        + v30_net_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v30_20d_summary = build_v30_20d_cross_ticker(v30_net_summary)

st.subheader(
    "109 v3.0 GOOG / NVDA 20日保有・2R比較"
)
if v30_20d_summary.empty:
    st.info("20日保有・2Rの銘柄横断比較対象がありません。")
else:
    st.dataframe(v30_20d_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.0 20日2R銘柄比較")
    st.code(
        "【109 v3.0 GOOG / NVDA 20日保有・2R比較】\n"
        + v30_20d_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v30_ticker_difference = build_v30_ticker_difference(v30_20d_summary)

st.subheader(
    "110 v3.0 20日保有・2R・NVDA−GOOG差"
)
if v30_ticker_difference.empty:
    st.info("20日保有・2Rの銘柄差を計算できません。")
else:
    st.dataframe(v30_ticker_difference.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.0 NVDA−GOOG差")
    st.code(
        "【110 v3.0 20日保有・2R・NVDA−GOOG差】\n"
        + v30_ticker_difference.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "111 v3.0 銘柄横断結果の扱い"
)
st.write(
    "【診断目的】GOOGで固定してきた同一ルールをNVDAへそのまま適用し、銘柄が変わったときのNet Rの振る舞いを確認します。"
)
st.write(
    "【別集計】GOOGとNVDAのイベントやR損益は混ぜず、銘柄別のまま表示します。"
)
st.write(
    "【未採用】結果の良い銘柄だけを選ぶこと、NVDAの結果を見てNVDA専用条件を後付けすること。"
)
st.write(
    "【注意】NVDAも今回確認することで研究済みデータになります。真の未使用OOSは将来データまたは別途凍結した期間で確認する必要があります。"
)


# ============================================================
# v3.1 GOOG / NVDA 20日2R 損益構造分解
# ============================================================

st.divider()

st.subheader(
    "112 v3.1 GOOG / NVDA 20日2R・損益構造分解ルール"
)
st.write(
    "【条件固定】v3.0までのBBイベント、シグナル、Entry、Stop、2R Target、ギャップ、手数料、スリッページを変更しません。"
)
st.write(
    "【分解のみ】20営業日・2RのNet R計算可能イベントを、Target通常・Targetギャップ・Stop通常・Stopギャップ・期間末の5区分へ整理します。"
)
st.write(
    "【目的】GOOGとNVDAの平均R差が、Target側・Stop側・期間末・ギャップのどこから生じているかを記述します。"
)
st.warning(
    "v3.1は原因候補の記述診断です。結果を見て銘柄専用条件を追加したり、特定区分を後から除外したりしません。"
)

v31_structure = build_v31_20d_structure(v30_bundles)

st.subheader(
    "113 v3.1 GOOG / NVDA 20日保有・2R・決済構造別Net R"
)
if v31_structure.empty:
    st.info("20日2Rの損益構造分解対象がありません。")
else:
    st.dataframe(v31_structure.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.1 決済構造別Net R")
    st.code(
        "【113 v3.1 GOOG / NVDA 20日保有・2R・決済構造別Net R】\n"
        + v31_structure.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v31_structure_difference = build_v31_cross_ticker_structure_difference(v31_structure)

st.subheader(
    "114 v3.1 20日保有・2R・決済構造別NVDA−GOOG差"
)
if v31_structure_difference.empty:
    st.info("決済構造別の銘柄差を計算できません。")
else:
    st.dataframe(v31_structure_difference.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.1 決済構造別NVDA−GOOG差")
    st.code(
        "【114 v3.1 20日保有・2R・決済構造別NVDA−GOOG差】\n"
        + v31_structure_difference.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

v31_reconciliation = build_v31_reconciliation_audit(v31_structure, v30_20d_summary)

st.subheader(
    "115 v3.1 20日保有・2R・構造分解監査"
)
if v31_reconciliation.empty:
    st.info("v3.1構造分解の監査対象がありません。")
else:
    st.dataframe(v31_reconciliation.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.1 構造分解監査")
    st.code(
        "【115 v3.1 20日保有・2R・構造分解監査】\n"
        + v31_reconciliation.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "116 v3.1 損益構造分解の扱い"
)
st.write(
    "【診断】Target / Stop / 期間末とギャップの件数・Net R寄与を銘柄別に確認します。"
)
st.write(
    "【維持】GOOG / NVDAのイベントは混ぜず、v3.0と同じ20日2R母集団を使います。"
)
st.write(
    "【未採用】結果の悪い決済構造だけを除外すること、銘柄ごとに後付けでルールを変えること。"
)
st.write(
    "【次段階候補】構造差が確認できても、それだけで原因とは断定せず、市場環境候補を事前定義してから検証します。"
)



# ============================================================
# v3.2 GOOG / NVDA 20営業日 MFE / MAE 価格経路診断
# ============================================================

st.divider()

st.subheader(
    "117 v3.2 GOOG / NVDA MFE / MAE・価格経路診断ルール"
)
st.write(
    "【条件固定】v3.1までのBBイベント、下落停止 / 反発開始、Entry、Stop、2R Target、ギャップ、コスト条件は変更しません。"
)
st.write(
    "【MFE】Entry後20営業日の最高値が、計画時点1Rに対して最大何R上へ進んだかを測ります。"
)
st.write(
    "【MAE】Entry後20営業日の最安値が、計画時点1Rに対して最大何R下へ進んだかを正の不利幅として測ります。"
)
st.write(
    "【固定20日窓】Stop / Targetで実際の研究上の決済が先に起きても、原因診断では20営業日を最後まで観察します。"
)
st.warning(
    "MFE / MAEは売買損益ではありません。決済後の値動きも含む反実仮想的な価格経路診断です。日足OHLCでは同一日の値動き順序も分かりません。"
)

v32_path_detail = build_v32_path_detail(v30_bundles, horizon=20)
v32_path_summary = build_v32_path_summary(v32_path_detail)
v32_threshold_difference = build_v32_threshold_difference(v32_path_summary)
v32_first_hit_vs_path = build_v32_first_hit_vs_path(v32_path_detail)
v32_audit = build_v32_audit(v32_path_detail, v30_bundles, horizon=20)

st.subheader(
    "118 v3.2 GOOG / NVDA 20営業日・MFE / MAEサマリー"
)
if v32_path_summary.empty:
    st.info("MFE / MAEサマリーの対象がありません。")
else:
    st.dataframe(v32_path_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.2 MFE / MAEサマリー")
    st.code(
        "【118 v3.2 GOOG / NVDA 20営業日・MFE / MAEサマリー】\n"
        + v32_path_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "119 v3.2 20営業日・MFE到達率・NVDA−GOOG差"
)
if v32_threshold_difference.empty:
    st.info("MFE到達率の銘柄差を計算できません。")
else:
    st.dataframe(v32_threshold_difference.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.2 MFE到達率差")
    st.code(
        "【119 v3.2 20営業日・MFE到達率・NVDA−GOOG差】\n"
        + v32_threshold_difference.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "120 v3.2 20営業日・2R到達 vs 2R先着"
)
if v32_first_hit_vs_path.empty:
    st.info("2R到達と先着の比較対象がありません。")
else:
    st.dataframe(v32_first_hit_vs_path.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.2 2R到達 vs 2R先着")
    st.code(
        "【120 v3.2 20営業日・2R到達 vs 2R先着】\n"
        + v32_first_hit_vs_path.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "121 v3.2 MFE / MAE・経路監査"
)
if v32_audit.empty:
    st.info("v3.2経路監査の対象がありません。")
else:
    st.dataframe(v32_audit, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.2 MFE / MAE経路監査")
    st.code(
        "【121 v3.2 MFE / MAE・経路監査】\n"
        + v32_audit.to_csv(index=False).rstrip(),
        language=None,
    )

st.subheader(
    "122 v3.2 MFE / MAE・イベント別詳細"
)
if v32_path_detail.empty:
    st.info("v3.2イベント別経路詳細がありません。")
else:
    v32_detail_display = v32_path_detail.copy()
    st.dataframe(v32_detail_display.round(4), use_container_width=True, hide_index=True)
    st.caption("詳細表は原因確認用です。個別イベントを見て後付けで除外条件を作りません。")

st.subheader(
    "123 v3.2 価格経路診断の扱い"
)
st.write(
    "【診断目的】NVDAで2R先着が少なかった理由を、上方向MFE・下方向MAE・Stop先着後の戻りに分解します。"
)
st.write(
    "【重要】20日内に2Rへ後から到達しても、Stopが先なら元の2R売買ルールでは勝ちへ変更しません。"
)
st.write(
    "【未採用】MFE結果を見てNVDAだけTargetを1.5Rへ変更すること、個別の悪いイベントを除外すること。"
)
st.write(
    "【次段階】MFEの0.5R / 1R / 1.5R / 2R到達率がどの段階からGOOG / NVDAで分岐するかを確認してから、次の仮説を決めます。"
)



# ============================================================
# v3.3 Stop先着 → その後2R・価格経路分解
# ============================================================

st.divider()

st.subheader(
    "124 v3.3 Stop先着→その後2R・価格経路分解ルール"
)
st.write(
    "【条件固定】v3.2までのEntry、1R Stop、2R Target、20営業日観察窓は変更しません。"
)
st.write(
    "【対象】下落停止シグナルで2RよりStopが先だったイベントを、20日内にその後2Rへ到達した群 / 到達しなかった群へ分けます。"
)
st.write(
    "【Stop超過幅】2R到達前だと確定できる価格情報からMAEを計算し、1Rを引いて計画Stopをさらに何R下回ったかを測ります。2R到達日のLowは日内順序不明として別列に分離します。"
)
st.warning(
    "この診断は『Stopを広げればよかった』という売買ルール変更ではありません。Stop決済後の反実仮想的な値動きを調べる原因診断です。"
)

v33_stop_recovery_detail = build_v33_stop_recovery_detail(v30_bundles, horizon=20)
v33_group_summary = build_v33_group_summary(v33_stop_recovery_detail)
v33_nvda_recovered_detail = v33_stop_recovery_detail[
    v33_stop_recovery_detail["銘柄"].eq("NVDA")
    & v33_stop_recovery_detail["20日観察完了"].eq(True)
    & v33_stop_recovery_detail["Stop先着後20日内2R到達"].eq(True)
].copy() if not v33_stop_recovery_detail.empty else pd.DataFrame()
v33_audit = build_v33_audit(v33_stop_recovery_detail, v32_path_detail)

st.subheader(
    "125 v3.3 Stop先着イベント・20日価格経路グループ比較"
)
if v33_group_summary.empty:
    st.info("v3.3グループ比較の対象がありません。")
else:
    st.dataframe(v33_group_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.3 Stop先着グループ比較")
    st.code(
        "【125 v3.3 Stop先着イベント・20日価格経路グループ比較】\n"
        + v33_group_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "126 v3.3 NVDA下落停止・Stop先着→20日内2R到達イベント詳細"
)
if v33_nvda_recovered_detail.empty:
    st.info("NVDAのStop先着→20日内2R到達イベントがありません。")
else:
    v33_nvda_display_cols = [
        "イベントID", "シグナル日", "Entry日", "Entry価格", "Stop価格", "2R価格", "1R率_%",
        "Stop到達日", "Stop到達営業日", "Stop約定種別", "Stop時Gross_R",
        "2R初回到達日", "2R初回到達営業日", "Stop→2R営業日差",
        "2R到達前確定MAE_R", "2R到達前確定Stop超過幅_R",
        "2R到達日まで最大MAE_R_日内順序不明", "2R到達日までStop超過最大幅_R_日内順序不明",
        "20日最大MAE_R", "20日最大Stop超過幅_R", "20日終値_R",
    ]
    v33_nvda_display = v33_nvda_recovered_detail[v33_nvda_display_cols].copy()
    st.dataframe(v33_nvda_display.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.3 NVDA Stop先着→2R詳細")
    st.code(
        "【126 v3.3 NVDA下落停止・Stop先着→20日内2R到達イベント詳細】\n"
        + v33_nvda_display.to_csv(index=False, float_format="%.4f", date_format="%Y-%m-%d").rstrip(),
        language=None,
    )

st.subheader(
    "127 v3.3 Stop先着→その後2R・経路監査"
)
if v33_audit.empty:
    st.info("v3.3経路監査の対象がありません。")
else:
    st.dataframe(v33_audit, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.3 Stop先着→その後2R経路監査")
    st.code(
        "【127 v3.3 Stop先着→その後2R・経路監査】\n"
        + v33_audit.to_csv(index=False).rstrip(),
        language=None,
    )

st.subheader(
    "128 v3.3 Stop先着後の価格経路診断の扱い"
)
st.write(
    "【診断目的】NVDA下落停止でStop先着後に2Rへ戻ったケースが、Stopをわずかに割る型か、大きく下落してから戻る型かを確認します。"
)
st.write(
    "【比較】同じStop先着でも20日内2R未到達群を残し、回復したイベントだけを後付けで成功例として扱いません。"
)
st.write(
    "【未採用】Stop幅の拡大、1R率フィルター、NVDA専用ルール、個別イベント除外。"
)
st.write(
    "【次段階】経路の深さと回復日数を確認した後でのみ、Stop設計を別仮説として検証する価値があるか判断します。"
)

# ============================================================
# v3.4.1 固定ルール・別5年間による時間方向検証
# ============================================================

st.divider()

st.subheader(
    "129 v3.4.1 固定ルール・別5年間時間方向検証ルール"
)
st.write(
    "【条件固定】BBイベント、下落停止、反発開始、翌営業日Open Entry、イベント起点1R Stop、2R Target、5 / 10 / 20営業日を変更しません。"
)
st.write(
    f"【コスト固定】画面上部と同じ片道手数料 {commission_percent:.2f}%、片道スリッページ {slippage_percent:.2f}% を両期間・両銘柄へ使用します。"
)
st.write(
    f"【ウォームアップ】各評価窓の前 {V34_WARMUP_CALENDAR_DAYS} 暦日を指標計算だけに使用し、イベントID・Entry・損益の母集団には含めません。"
)
st.write(
    "【期間完全固定】前5年は2016-10-01～2021-09-30、現5年は2021-10-01～2026-09-30です。実行日や最新データ日では動きません。"
)
st.warning(
    "前5年はこの研究で条件調整に使っていない過去期間を時間方向に確認するものです。ただし将来データによる前向きOOSではありません。結果を見てルールを変更すると、この検証期間も以後は未使用ではなくなります。"
)
st.write(
    "【監査強化】133番では130番の観察完了BBイベント数と131番の全6集計行の母集団件数、さらに下落停止 / 反発開始の対象件数まで自動照合します。"
)

# v3.4.2: v3.4.1の固定5年検証を一括キャッシュする。
# 手数料・スリッページが同じなら、クイックコピー等の画面操作で再計算しない。
with st.spinner("固定5年検証データを読み込んでいます（初回だけ計算します）..."):
    (
        v34_period_bundles,
        v34_windows,
        v34_audit,
        v34_net_summary,
        v34_20d_difference,
        v34_reconciliation,
    ) = build_v342_cached_time_validation(
        commission_rate,
        slippage_rate,
    )

st.caption(
    "【固定】前5年: "
    f"{v34_windows['前5年'][0].date()} ～ {v34_windows['前5年'][1].date()} ｜ "
    "現5年: "
    f"{v34_windows['現5年'][0].date()} ～ {v34_windows['現5年'][1].date()}"
)

st.subheader(
    "130 v3.4.1 固定5年窓・監査サマリー"
)
if v34_audit.empty:
    st.info("v3.4.1固定5年窓の監査対象がありません。")
else:
    st.dataframe(v34_audit, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.4.1固定5年窓監査")
    st.code(
        "【130 v3.4.1 固定5年窓・監査サマリー】\n"
        + v34_audit.to_csv(index=False, date_format="%Y-%m-%d").rstrip(),
        language=None,
    )

st.subheader(
    "131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較"
)
if v34_net_summary.empty:
    st.info("v3.4.1のNet R比較対象がありません。")
else:
    st.dataframe(v34_net_summary.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.4.1前5年 vs 現5年Net R")
    st.code(
        "【131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較】\n"
        + v34_net_summary.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "132 v3.4.1 20日保有・2R・前5年→現5年差"
)
if v34_20d_difference.empty:
    st.info("v3.4.1の20日2R期間差を計算できませんでした。")
else:
    st.dataframe(v34_20d_difference.round(4), use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.4.1 20日2R期間差")
    st.code(
        "【132 v3.4.1 20日保有・2R・前5年→現5年差】\n"
        + v34_20d_difference.to_csv(index=False, float_format="%.4f").rstrip(),
        language=None,
    )

st.subheader(
    "133 v3.4.1 時間方向検証・最終監査"
)
if v34_reconciliation.empty:
    st.info("v3.4.1時間方向検証の最終監査対象がありません。")
else:
    st.dataframe(v34_reconciliation, use_container_width=True, hide_index=True)
    st.write("📋 コピー用・v3.4.1時間方向検証最終監査")
    st.code(
        "【133 v3.4.1 時間方向検証・最終監査】\n"
        + v34_reconciliation.to_csv(index=False).rstrip(),
        language=None,
    )

st.subheader(
    "134 v3.4.1 時間方向検証結果の扱い"
)
st.write(
    "【検証目的】現在5年間で見えたGOOG / NVDAの差が、その直前の別5年間でも同じ方向に現れるかを確認します。"
)
st.write(
    "【重要】前5年が良い / 悪いという結果を見て、期間・Stop・Target・1R率・銘柄専用条件を後付け変更しません。"
)
st.write(
    "【比較方法】まず監査を通し、その後に5 / 10 / 20営業日のNet R、最後に20日2Rの期間差を読みます。"
)
st.write(
    "【未採用】前5年の結果を使ったパラメータ最適化、NVDA専用救済ルール、Stop幅拡大、極小1R除外。"
)

# ============================================================
# v3.4.1 番号選択・クイックコピー
# ============================================================

# 長いページをスクロールしなくても、サイドバーから番号を選んで
# コピー用結果をすぐ表示できるようにする。
def _quick_copy_text(title, frame):
    if frame is None or not isinstance(frame, pd.DataFrame) or frame.empty:
        return f"【{title}】\n表示対象がありません。"
    return f"【{title}】\n" + frame.to_csv(index=False, float_format="%.4f")


quick_copy_results = {
    "64 v2.2 見送りイベント・固定窓終了後N営業日以内の反発確認": _quick_copy_text(
        "64 v2.2 見送りイベント・固定窓終了後N営業日以内の反発確認",
        v22_horizon_summary,
    ),
    "65 v2.2 初回反発確認タイミング": _quick_copy_text(
        "65 v2.2 初回反発確認タイミング",
        v22_timing_summary,
    ),
    "66 v2.2 見送りイベント・固定窓終了後追跡詳細": _quick_copy_text(
        "66 v2.2 見送りイベント・固定窓終了後追跡詳細",
        v22_detail_display if "v22_detail_display" in globals() else pd.DataFrame(),
    ),
    "68 v2.3 遅い反発Entry・R設計詳細": _quick_copy_text(
        "68 v2.3 遅い反発Entry・R設計詳細",
        v23_design_display if "v23_design_display" in globals() else pd.DataFrame(),
    ),
    "69 v2.3 方針C・固定窓後5営業日まで待つ・1.5R": _quick_copy_text(
        "69 v2.3 方針C・固定窓後5営業日まで待つ・1.5R", v23_summary_69
    ),
    "70 v2.3 方針C・固定窓後5営業日まで待つ・2R": _quick_copy_text(
        "70 v2.3 方針C・固定窓後5営業日まで待つ・2R", v23_summary_70
    ),
    "71 v2.3 方針C・固定窓後10営業日まで待つ・1.5R": _quick_copy_text(
        "71 v2.3 方針C・固定窓後10営業日まで待つ・1.5R", v23_summary_71
    ),
    "72 v2.3 方針C・固定窓後10営業日まで待つ・2R": _quick_copy_text(
        "72 v2.3 方針C・固定窓後10営業日まで待つ・2R", v23_summary_72
    ),
    "73 v2.3 新規BBイベント有無別・10日待ち・20日保有・2R": _quick_copy_text(
        "73 v2.3 新規BBイベント有無別・10日待ち・20日保有・2R", v23_new_bb_summary
    ),
    "74 v2.3 遅い反発Entry・10日待ち・20日保有・2R詳細": _quick_copy_text(
        "74 v2.3 遅い反発Entry・10日待ち・20日保有・2R詳細", v23_detail
    ),
    "76 v2.4 元見送りイベント・新規BBイベント連結一覧": _quick_copy_text(
        "76 v2.4 元見送りイベント・新規BBイベント連結一覧",
        v24_linkage_display if "v24_linkage_display" in globals() else pd.DataFrame(),
    ),
    "77 v2.4 新規BBイベントありケース・連結詳細": _quick_copy_text(
        "77 v2.4 新規BBイベントありケース・連結詳細",
        v24_linked_detail if "v24_linked_detail" in globals() else pd.DataFrame(),
    ),
    "78 v2.4 二重計上診断サマリー": _quick_copy_text(
        "78 v2.4 二重計上診断サマリー", v24_summary
    ),
    "79 v2.4 同一反発シグナル・元イベントStop vs 新イベントStop": _quick_copy_text(
        "79 v2.4 同一反発シグナル・元イベントStop vs 新イベントStop",
        v24_r_design_compare if "v24_r_design_compare" in globals() else pd.DataFrame(),
    ),
    "82 v2.5 リセット後・重複除去済み実効イベント一覧": _quick_copy_text(
        "82 v2.5 リセット後・重複除去済み実効イベント一覧",
        v25_design_display if "v25_design_display" in globals() else pd.DataFrame(),
    ),
    "83 v2.5 リセット方式・1.5R": _quick_copy_text(
        "83 v2.5 リセット方式・1.5R", v25_summary_15
    ),
    "84 v2.5 リセット方式・2R": _quick_copy_text(
        "84 v2.5 リセット方式・2R", v25_summary_20
    ),
    "85 v2.5 v2.3旧イベント基準 vs リセット基準・20日保有・2R": _quick_copy_text(
        "85 v2.5 v2.3旧イベント基準 vs リセット基準・20日保有・2R",
        v25_compare_20_2r,
    ),
    "88 v2.6 独立BBイベント台帳・監査サマリー": _quick_copy_text(
        "88 v2.6 独立BBイベント台帳・監査サマリー", v26_audit_summary
    ),
    "89 v2.6 独立BBイベント台帳・全イベント": _quick_copy_text(
        "89 v2.6 独立BBイベント台帳・全イベント", v26_ledger
    ),
    "90 v2.6 独立BBイベント・シグナル構成": _quick_copy_text(
        "90 v2.6 独立BBイベント・シグナル構成", v26_type_summary
    ),
    "91 v2.6 独立BBイベント・20日保有・2R集計": _quick_copy_text(
        "91 v2.6 独立BBイベント・20日保有・2R集計", v26_20d_2r_summary
    ),
    "94 v2.7 2R・ギャップ反映前後比較": _quick_copy_text(
        "94 v2.7 2R・ギャップ反映前後比較", v27_gap_compare_summary
    ),
    "95 v2.7 20日保有・2R・ギャップでRが変化したイベント": _quick_copy_text(
        "95 v2.7 20日保有・2R・ギャップでRが変化したイベント", v27_gap_changed_20d
    ),
    "98 v2.8 2R・ギャップ反映Gross vs コスト後Net比較": _quick_copy_text(
        "98 v2.8 2R・ギャップ反映Gross vs コスト後Net比較", v28_cost_compare_summary
    ),
    "99 v2.8 20日保有・2R・イベント別コスト後Net R": _quick_copy_text(
        "99 v2.8 20日保有・2R・イベント別コスト後Net R", v28_cost_detail_20d
    ),
    "102 v2.9 固定時系列分割・監査サマリー": _quick_copy_text(
        "102 v2.9 固定時系列分割・監査サマリー", v29_split_audit
    ),
    "103 v2.9 2R・コスト後Net R・前半後半比較": _quick_copy_text(
        "103 v2.9 2R・コスト後Net R・前半後半比較", v29_time_summary
    ),
    "104 v2.9 20日保有・2R・前半→後半差": _quick_copy_text(
        "104 v2.9 20日保有・2R・前半→後半差", v29_20d_difference
    ),
    "107 v3.0 GOOG / NVDA 同一ルール・監査サマリー": _quick_copy_text(
        "107 v3.0 GOOG / NVDA 同一ルール・監査サマリー", v30_audit
    ),
    "108 v3.0 GOOG / NVDA 2R・コスト後Net R比較": _quick_copy_text(
        "108 v3.0 GOOG / NVDA 2R・コスト後Net R比較", v30_net_summary
    ),
    "109 v3.0 GOOG / NVDA 20日保有・2R比較": _quick_copy_text(
        "109 v3.0 GOOG / NVDA 20日保有・2R比較", v30_20d_summary
    ),
    "110 v3.0 20日保有・2R・NVDA−GOOG差": _quick_copy_text(
        "110 v3.0 20日保有・2R・NVDA−GOOG差", v30_ticker_difference
    ),
    "113 v3.1 GOOG / NVDA 20日保有・2R・決済構造別Net R": _quick_copy_text(
        "113 v3.1 GOOG / NVDA 20日保有・2R・決済構造別Net R", v31_structure
    ),
    "114 v3.1 20日保有・2R・決済構造別NVDA−GOOG差": _quick_copy_text(
        "114 v3.1 20日保有・2R・決済構造別NVDA−GOOG差", v31_structure_difference
    ),
    "115 v3.1 20日保有・2R・構造分解監査": _quick_copy_text(
        "115 v3.1 20日保有・2R・構造分解監査", v31_reconciliation
    ),
    "118 v3.2 GOOG / NVDA 20営業日・MFE / MAEサマリー": _quick_copy_text(
        "118 v3.2 GOOG / NVDA 20営業日・MFE / MAEサマリー", v32_path_summary
    ),
    "119 v3.2 20営業日・MFE到達率・NVDA−GOOG差": _quick_copy_text(
        "119 v3.2 20営業日・MFE到達率・NVDA−GOOG差", v32_threshold_difference
    ),
    "120 v3.2 20営業日・2R到達 vs 2R先着": _quick_copy_text(
        "120 v3.2 20営業日・2R到達 vs 2R先着", v32_first_hit_vs_path
    ),
    "121 v3.2 MFE / MAE・経路監査": _quick_copy_text(
        "121 v3.2 MFE / MAE・経路監査", v32_audit
    ),
    "125 v3.3 Stop先着イベント・20日価格経路グループ比較": _quick_copy_text(
        "125 v3.3 Stop先着イベント・20日価格経路グループ比較", v33_group_summary
    ),
    "126 v3.3 NVDA下落停止・Stop先着→20日内2R到達イベント詳細": _quick_copy_text(
        "126 v3.3 NVDA下落停止・Stop先着→20日内2R到達イベント詳細",
        v33_nvda_display if "v33_nvda_display" in globals() else pd.DataFrame(),
    ),
    "127 v3.3 Stop先着→その後2R・経路監査": _quick_copy_text(
        "127 v3.3 Stop先着→その後2R・経路監査", v33_audit
    ),
    "130 v3.4.1 固定5年窓・監査サマリー": _quick_copy_text(
        "130 v3.4.1 固定5年窓・監査サマリー", v34_audit
    ),
    "131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較": _quick_copy_text(
        "131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較", v34_net_summary
    ),
    "132 v3.4.1 20日保有・2R・前5年→現5年差": _quick_copy_text(
        "132 v3.4.1 20日保有・2R・前5年→現5年差", v34_20d_difference
    ),
    "133 v3.4.1 時間方向検証・最終監査": _quick_copy_text(
        "133 v3.4.1 時間方向検証・最終監査", v34_reconciliation
    ),
}

@st.fragment
def render_quick_copy_fragment():
    """クイックコピー操作だけを再実行し、アプリ全体の再起動を防ぐ。"""
    with quick_copy_top_placeholder:
        st.divider()
        st.subheader("📋 番号で結果をすぐコピー")
        st.caption(
            "v3.4.2ではこの選択欄だけが独立して再実行されます。番号を選ぶだけでコピー欄が切り替わり、研究計算全体は再実行しません。"
        )
        quick_copy_choice = st.selectbox(
            "結果番号を選択",
            options=list(quick_copy_results.keys()),
            index=list(quick_copy_results.keys()).index("133 v3.4.1 時間方向検証・最終監査"),
            key="quick_copy_choice_v342",
        )
        st.success(f"表示中：{quick_copy_choice}")
        st.caption("下のコピー欄の右上にあるコピーアイコンを押すと全文をコピーできます。")
        st.code(
            quick_copy_results[quick_copy_choice],
            language=None,
        )


render_quick_copy_fragment()



# ============================================================
# 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "現在の研究段階"
)

st.write(
    "【実装済み】GOOG / NVDA 切り替え"
)

st.write(
    "【実装済み】20日・2標準偏差BB"
)

st.write(
    "【正常動作確認済み】0～3営業日の固定イベント"
)

st.write(
    "【正常動作確認済み】観察完了・未完了分離"
)

st.write(
    "【検証中】安値切り上げ＋終値上昇＝下落停止候補"
)

st.write(
    "【検証中】終値が前日高値を上回る＝反発開始候補"
)

st.write(
    "【正式採用 for research execution】シグナル確認後の次営業日始値＝Entry"
)

st.write(
    "【検証中】イベント開始～確認日の最安値＝Stop"
)

st.write(
    "【正常動作確認済み】v1.5 1R / 1.5R / 2R価格計算"
)

st.write(
    "【正常動作確認済み】v1.5.2 1R率診断・コピー"
)

st.write(
    "【未採用】1R率による除外条件"
)

st.write(
    "【v1.6 実装】5・10・20営業日のR先着判定"
)

st.write(
    "【v1.6 実装】同日Stop・Target両方到達を順序不明として分離"
)

st.write(
    "【v1.6 実装】期間末の将来データ不足を分離"
)

st.write(
    "【未検証】下落停止と反発開始のどちらにR上の優位性があるか"
)

st.write(
    "【未採用】最大保有期間を5・10・20営業日のどれかに固定すること"
)

st.write(
    "【v1.7 実装】期間内未到達を5・10・20営業日目の終値で期間末決済"
)

st.write(
    "【v1.7 実装】Target / Stop / 期間末決済をR損益へ統合"
)

st.write(
    "【v1.7 実装】全件と1R率1%以上の参考診断を並列表示"
)

st.write(
    "【未採用】1R率1%以上を正式な売買フィルターにすること"
)

st.write(
    "【v1.8 実装】同じBB下限イベントで下落停止と反発開始を1対1比較"
)

st.write(
    "【v1.8 実装】反発開始R − 下落停止Rを5・10・20営業日で比較"
)

st.write(
    "【v1.8 実装】ペア内の下落停止1R率最小イベント1件の影響を参考診断"
)

st.write(
    "【未採用】最小1Rイベントを正式に除外すること"
)

st.write(
    "【v1.9 実装】下落停止シグナル時点を共通の意思決定起点に固定"
)

st.write(
    "【v1.9 実装】方針A＝下落停止後Entry、方針B＝反発開始を待ち、未確認なら見送り0R機会"
)

st.write(
    "【v1.9 実装】下落停止より前だけに出た反発条件を方針Bへ流用しない"
)

st.write(
    "【v1.9 実装】方針Bの待ち営業日・Entry件数・見送り件数・機会平均Rを表示"
)

st.write(
    "【未採用】方針A / 方針Bのどちらかを正式な売買方式に固定すること"
)

st.write(
    "【v2.0 実装】方針Bが見送ったイベントで、方針Aなら何Rだったかを分離"
)

st.write(
    "【v2.0 実装】反発確認までの待ち営業日0・1・2・3日別にR結果を分離"
)

st.write(
    "【v2.0 実装】方針Bが高い / 方針Aが高い / 同じ、の原因グループを分離"
)

st.write(
    "【v2.0 実装】比較不可イベントを理由別に表示"
)

st.write(
    "【未採用】v2.0の原因分解結果を新しい売買フィルターとして使うこと"
)

st.write(
    "【v2.1 実装】下落停止シグナル確定時点までの事前情報だけで反発確認グループを比較"
)

st.write(
    "【v2.1 実装】同日反発を除外し、後日反発 vs 反発未確認・見送りを比較"
)

st.write(
    "【v2.1 実装】BB位置・BandWidth・価格反応・状態分類を記述統計で比較"
)

st.write(
    "【未採用】v2.1で見つかった差をそのまま新しいEntry / 見送り条件にすること"
)

st.write(
    "【v2.2 実装】見送りイベントを固定窓終了後20営業日まで追跡し、最初の反発確認日を診断"
)

st.write(
    "【v2.2 実装】固定窓終了後1 / 2 / 3 / 5 / 10 / 20営業日以内の反発確認件数を比較"
)

st.write(
    "【未採用】v2.2の追跡結果を使って固定観察窓やEntryルールを変更すること"
)

st.write(
    "【v2.4 確認済み】新規BBイベントありケースは新イベント側の反発シグナルと重複するため、独立2事例として数えない"
)

st.write(
    "【v2.5 実装】新BBイベント発生時に旧イベント追跡を終了し、新イベント基準のRebound R設計へリセット"
)

st.write(
    "【v2.5 実装】重複除去後の1.5R / 2R、5 / 10 / 20営業日R損益を再計算"
)

st.write(
    "【未採用】v2.5リセット方式を正式な売買ルールにすること"
)

st.write(
    "【v2.6 正式採用・研究データ管理】観察完了BBイベントを1イベント=1行の独立イベント台帳で管理"
)

st.write(
    "【v2.6 正式採用・研究データ管理】固定窓後の遅い反発を元イベントへ追加せず、新BBイベントは別IDとして集計"
)

st.write(
    "【v2.6 実装】独立イベントIDの重複・欠落監査と20日2R結果の統合集計"
)

st.write(
    "【v2.7 実装】Stop / TargetをOpenで飛び越えたギャップ時はOpen約定としてR損益へ反映"
)

st.write(
    "【v2.8 実装】Entry / Exit双方の手数料・スリッページを含むNet R損益"
)

st.write(
    "【v2.8 実装】画面から片道手数料率・片道スリッページ率を変更し、Gross RとNet Rを比較"
)

st.write(
    "【v2.9 実装】独立BBイベント母集団を共通境界で前半 / 後半へ固定分割し、Net Rの時系列安定性を診断"
)

st.write(
    "【v2.9 注意】後半は既に研究で見た期間を含むため、真の未使用OOSではない"
)

st.write(
    "【v3.0 実装】GOOG / NVDAを同一期間・同一ルール・同一コストで別々に同時計算し、銘柄横断の再現性を診断"
)

st.write(
    "【v3.0 注意】NVDAの結果を見てから銘柄専用条件を後付けせず、両銘柄の結果を混ぜない"
)

st.write(
    "【v3.1 実装】20日2RをTarget通常・Targetギャップ・Stop通常・Stopギャップ・期間末へ固定分解し、銘柄差の中身を診断"
)

st.write(
    "【v3.1 注意】構造差は原因の証明ではなく、悪い区分を後付け除外しない"
)

st.write(
    "【v3.2 実装】GOOG / NVDAのEntry後20営業日を固定観察し、MFE / MAEを計画時点1Rで正規化"
)

st.write(
    "【v3.2 実装】0.5R / 1R / 1.5R / 2R到達率と、2R到達がStopより先か後かを分離"
)

st.write(
    "【v3.2 注意】固定20日MFE / MAEは決済後の価格も含む原因診断であり、実現損益ではない"
)

st.write(
    "【v3.3 実装】下落停止のStop先着イベントを、20日内にその後2Rへ到達 / 未到達へ分け、回復までのMAEとStop超過幅を診断"
)

st.write(
    "【v3.3 注意】Stop先着後の回復は反実仮想診断であり、Stop幅拡大を正式採用した意味ではない"
)

st.write(
    "【v3.4.1 実装】売買条件を固定し、重ならない前5年 / 現5年を同じウォームアップ・同じコストで時間方向比較"
)

st.write(
    "【v3.4.1 注意】前5年は未使用過去期間の検証であり、将来データによる前向きOOSではない"
)

st.write(
    "【未実装】R期待値・最大ドローダウン等を含む本格バックテスト"
)


# ============================================================
# 最終説明
# ============================================================

st.divider()

st.warning(
    "重要：Target先着率や平均Rだけで正式な売買ルールは決めません。"
    "同日順序不明・期間内未到達・将来データ不足を分離し、"
    "v3.4.1ではv3.3までの条件を固定したまま、重ならない前5年 / 現5年で時間方向の再現性を診断します。"
    "板・出来高・部分約定・税金・為替コストなどはまだ含みません。"
)

st.info(
    "シグナルは当日の終値確定後に判定し、Entryには次営業日の始値を使用します。"
    "Stopはシグナル確認時点までの情報だけで決定します。"
    "Entry後のHigh / Low / Openは、研究上の結果判定にのみ使用します。"
)

st.info(
    "v1.8でも1R率が小さいイベントは本体集計から削除しません。"
    "まず全R計算可能イベントで先着結果を確認し、"
    "極小1Rが結果へ与える影響はその後に分けて検証します。"
)

st.info(
    "v1.7の平均Rは、Target先着・Stop先着・期間末終値決済を統合した"
    "コスト前の研究値です。同日順序不明と将来データ不足は平均Rから除外します。"
)

st.info(
    "1R率1%以上の結果は、極小1Rの影響を見るための参考診断です。"
    "過去結果を見て1%を正式採用したものではありません。"
)

st.info(
    "v1.8のペア比較は、同じBB下限イベントについて下落停止と反発開始を同じTarget・同じ保有期間で比較します。"
    "R差は『反発開始R − 下落停止R』です。最小1Rイベント除外表示は感度確認だけで、正式な除外条件ではありません。"
)

st.info(
    "v1.9の意思決定比較は、将来『両方のシグナルが出たイベント』だけを後から選びません。"
    "下落停止が出た時点を母集団の起点にし、反発を待って出なかったイベントも見送りとして残します。"
)

st.info(
    "方針Bの機会平均Rには見送り0Rを含みます。Entry取引だけの平均Rも別列で表示し、"
    "『取引の質』と『見送りを含む意思決定全体』を混同しないようにしています。"
)

st.info(
    "v2.0はv1.9の平均R差を、見送り・待ち営業日・差グループ・比較不可理由に分解します。"
    "原因を確認するための診断であり、結果を見て特定の待ち日数や見送り条件を正式採用するものではありません。"
)

st.info(
    "v2.1は下落停止シグナル日の終値確定時点までに観測できた情報だけを使い、"
    "同日反発を除いた『後日反発 vs 反発未確認・見送り』を比較します。"
    "ここで見つかった差は次の検証候補であり、同じ標本内で新しい売買ルールとして採用しません。"
)

st.info(
    "v2.2はv2.1で見送りとなったイベントだけを固定イベント終了後に追跡し、"
    "day3という観察窓の長さに結果が依存していないかを診断します。"
    "day4以降の反発情報を過去のEntry判断には使用しません。"
)

st.caption(
    "このプログラムは研究・検証用です。"
    "売買シグナルとして正式採用したものではありません。"
)
