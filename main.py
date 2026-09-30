# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.3.1
#
# v1.1
# ・125営業日 BandWidth 正規化
# ・Squeeze基準確認
# ・研究用低BandWidthゾーン
# ・BandWidth収縮 / 拡大分類
#
# v1.2
# ・BB下限タッチ
# ・日中BB下限下抜け
# ・BB内復帰
# ・BB下限より下で終値
# ・低BandWidthから下方向拡大候補
#
# v1.3
# ・前日安値を割らない
# ・安値切り上げ
# ・前日終値より上昇
# ・陽線
# ・安値切り上げ＋終値上昇
# ・BB下限イベント後3営業日追跡
# ・下落停止候補
#
# v1.3.1
# ・BB下限局面を「イベント単位」に整理
# ・近接したBB下限タッチを同一イベントとして管理
# ・イベントIDを付与
# ・同一イベント内の最初の下落停止候補だけを記録
# ・候補日の重複件数を表示
# ・最初の下落停止確認時のBB状態を分類
# ・イベント単位の一覧を追加
#
# 注意
# 現段階では売買判断を行わない
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# Streamlit 基本設定
# ============================================================

st.set_page_config(
    page_title="GOOG・NVDA BB研究",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# 定数
# ============================================================

APP_VERSION = "1.3.1"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125

# 研究用
LOW_BANDWIDTH_ZONE = 0.20

# BB下限タッチ後を何営業日追跡するか
# 現段階では研究用の仮設定
LOWER_EVENT_LOOKBACK_DAYS = 3


# ============================================================
# 株価データ取得
# ============================================================

@st.cache_data(ttl=3600)
def get_stock_data(
    ticker: str,
    period: str,
) -> pd.DataFrame:

    try:

        data = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            multi_level_index=False,
        )

        if data is None or data.empty:
            return pd.DataFrame()

        data = data.copy()

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for column in required_columns:

            if column not in data.columns:
                return pd.DataFrame()

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

        data = data.dropna(
            subset=[
                "Open",
                "High",
                "Low",
                "Close",
            ]
        )

        return data

    except Exception:
        return pd.DataFrame()


# ============================================================
# ボリンジャーバンド
# ============================================================

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2.0,
) -> pd.DataFrame:

    df = data.copy()

    df["BB_Middle"] = (
        df["Close"]
        .rolling(window=period)
        .mean()
    )

    df["BB_Std"] = (
        df["Close"]
        .rolling(window=period)
        .std(ddof=0)
    )

    df["BB_Upper"] = (
        df["BB_Middle"]
        + std_multiplier * df["BB_Std"]
    )

    df["BB_Lower"] = (
        df["BB_Middle"]
        - std_multiplier * df["BB_Std"]
    )

    return df


# ============================================================
# BandWidth
# ============================================================

def calculate_bandwidth(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["BandWidth"] = np.where(
        df["BB_Middle"] != 0,
        (
            (
                df["BB_Upper"]
                - df["BB_Lower"]
            )
            / df["BB_Middle"]
        )
        * 100,
        np.nan,
    )

    return df


# ============================================================
# BB下限との距離
# ============================================================

def calculate_lower_band_distance(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Lower_Distance_Close"] = np.where(
        df["BB_Lower"] != 0,
        (
            (
                df["Close"]
                - df["BB_Lower"]
            )
            / df["BB_Lower"]
        )
        * 100,
        np.nan,
    )

    df["Lower_Distance_Low"] = np.where(
        df["BB_Lower"] != 0,
        (
            (
                df["Low"]
                - df["BB_Lower"]
            )
            / df["BB_Lower"]
        )
        * 100,
        np.nan,
    )

    return df


# ============================================================
# BandWidth 状態計算
# ============================================================

def calculate_bandwidth_state(
    data: pd.DataFrame,
    lookback: int = 125,
) -> pd.DataFrame:

    df = data.copy()

    df["BandWidth_Min_125"] = (
        df["BandWidth"]
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .min()
    )

    df["BandWidth_Max_125"] = (
        df["BandWidth"]
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .max()
    )

    bandwidth_range = (
        df["BandWidth_Max_125"]
        - df["BandWidth_Min_125"]
    )

    df["Normalized_BandWidth"] = np.where(
        bandwidth_range > 0,
        (
            df["BandWidth"]
            - df["BandWidth_Min_125"]
        )
        / bandwidth_range,
        np.nan,
    )

    df["BandWidth_Change_1D"] = (
        df["BandWidth"]
        - df["BandWidth"].shift(1)
    )

    df["BandWidth_Change_3D"] = (
        df["BandWidth"]
        - df["BandWidth"].shift(3)
    )

    df["BandWidth_Change_5D"] = (
        df["BandWidth"]
        - df["BandWidth"].shift(5)
    )

    df["Official_Squeeze"] = (
        df["BandWidth"].notna()
        & df["BandWidth_Min_125"].notna()
        & np.isclose(
            df["BandWidth"],
            df["BandWidth_Min_125"],
            rtol=1e-10,
            atol=1e-12,
        )
    )

    df["Low_BandWidth_Zone"] = (
        df["Normalized_BandWidth"].notna()
        & (
            df["Normalized_BandWidth"]
            <= LOW_BANDWIDTH_ZONE
        )
    )

    return df


# ============================================================
# BandWidth方向
# ============================================================

def classify_bandwidth_direction(
    row,
) -> str:

    change_1d = row["BandWidth_Change_1D"]
    change_3d = row["BandWidth_Change_3D"]
    change_5d = row["BandWidth_Change_5D"]

    if (
        pd.isna(change_1d)
        or pd.isna(change_3d)
        or pd.isna(change_5d)
    ):
        return "判定不可"

    if (
        change_1d < 0
        and change_3d < 0
        and change_5d < 0
    ):
        return "収縮中"

    if (
        change_1d > 0
        and change_3d > 0
        and change_5d > 0
    ):
        return "拡大中"

    if (
        change_5d < 0
        and change_1d > 0
    ):
        return "拡大開始候補"

    if (
        change_5d > 0
        and change_1d < 0
    ):
        return "収縮開始候補"

    return "混合状態"


# ============================================================
# Squeeze状態
# ============================================================

def classify_squeeze_state(
    row,
) -> str:

    normalized = row["Normalized_BandWidth"]

    if pd.isna(normalized):
        return "判定不可"

    if bool(row["Official_Squeeze"]):
        return "公式Squeeze基準"

    if bool(row["Low_BandWidth_Zone"]):

        if row["BandWidth_Change_1D"] > 0:
            return "低BandWidth・拡大開始候補"

        if row["BandWidth_Change_1D"] < 0:
            return "低BandWidth・収縮中"

        return "低BandWidth"

    return "非Squeeze"


# ============================================================
# v1.2
# BB下限イベント
# ============================================================

def calculate_lower_band_events(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["BB_Lower_Touch"] = (
        df["BB_Lower"].notna()
        & (df["Low"] <= df["BB_Lower"])
    )

    df["BB_Lower_Intraday_Break"] = (
        df["BB_Lower"].notna()
        & (df["Low"] < df["BB_Lower"])
    )

    df["BB_Lower_Reclaim"] = (
        df["BB_Lower_Intraday_Break"]
        & (df["Close"] >= df["BB_Lower"])
    )

    df["BB_Lower_Close_Below"] = (
        df["BB_Lower"].notna()
        & (df["Close"] < df["BB_Lower"])
    )

    return df


# ============================================================
# BB下限状態分類
# ============================================================

def classify_lower_band_event(
    row,
) -> str:

    if pd.isna(row["BB_Lower"]):
        return "判定不可"

    if bool(row["BB_Lower_Close_Below"]):
        return "BB下限より下で終値"

    if bool(row["BB_Lower_Reclaim"]):
        return "下抜け後BB内復帰"

    if bool(row["BB_Lower_Touch"]):
        return "BB下限タッチ"

    return "BB下限未到達"


# ============================================================
# v1.2
# 低BandWidthから下方向へ拡大
# ============================================================

def calculate_downside_expansion(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Prev_Low_BandWidth_Zone"] = (
        df["Low_BandWidth_Zone"]
        .shift(1, fill_value=False)
        .astype(bool)
    )

    df["BandWidth_Expanding_1D"] = (
        df["BandWidth_Change_1D"] > 0
    )

    df["Downside_Expansion_Candidate"] = (
        df["Prev_Low_BandWidth_Zone"]
        & df["BandWidth_Expanding_1D"]
        & df["BB_Lower_Touch"]
    )

    df["Downside_Expansion_Close_Below"] = (
        df["Downside_Expansion_Candidate"]
        & df["BB_Lower_Close_Below"]
    )

    df["Downside_Expansion_Reclaim"] = (
        df["Downside_Expansion_Candidate"]
        & df["BB_Lower_Reclaim"]
    )

    return df


# ============================================================
# 下方向拡大状態
# ============================================================

def classify_downside_expansion(
    row,
) -> str:

    if bool(row["Downside_Expansion_Close_Below"]):
        return "低BW→下方向拡大・BB下で終値"

    if bool(row["Downside_Expansion_Reclaim"]):
        return "低BW→下方向拡大・BB内復帰"

    if bool(row["Downside_Expansion_Candidate"]):
        return "低BW→下方向拡大候補"

    return "該当なし"


# ============================================================
# v1.3
# 下落停止基本条件
# ============================================================

def calculate_decline_stop_conditions(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Prev_Low"] = (
        df["Low"].shift(1)
    )

    df["Prev_Close"] = (
        df["Close"].shift(1)
    )

    # 前日安値を割らない
    df["No_Lower_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] >= df["Prev_Low"])
    )

    # 安値切り上げ
    df["Higher_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] > df["Prev_Low"])
    )

    # 前日終値より上
    df["Close_Up"] = (
        df["Prev_Close"].notna()
        & (df["Close"] > df["Prev_Close"])
    )

    # 陽線
    df["Bullish_Candle"] = (
        df["Close"] > df["Open"]
    )

    # 研究用複合条件
    df["Decline_Stop_Combo"] = (
        df["Higher_Low"]
        & df["Close_Up"]
    )

    return df


# ============================================================
# v1.3
# BB下限タッチ後3営業日追跡
# ============================================================

def calculate_lower_event_window(
    data: pd.DataFrame,
    lookback_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    recent_touch = pd.Series(
        False,
        index=df.index,
        dtype=bool,
    )

    days_since_touch = pd.Series(
        np.nan,
        index=df.index,
        dtype=float,
    )

    for days_ago in range(
        0,
        lookback_days + 1,
    ):

        shifted_touch = (
            df["BB_Lower_Touch"]
            .shift(
                days_ago,
                fill_value=False,
            )
            .astype(bool)
        )

        recent_touch = (
            recent_touch
            | shifted_touch
        )

        not_assigned = (
            days_since_touch.isna()
            & shifted_touch
        )

        days_since_touch.loc[
            not_assigned
        ] = days_ago

    df["Recent_BB_Lower_Event"] = (
        recent_touch
    )

    df["Days_Since_BB_Lower_Touch"] = (
        days_since_touch
    )

    return df


# ============================================================
# v1.3
# 下落停止候補
# ============================================================

def calculate_decline_stop_candidates(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Recent_Event_No_Lower_Low"] = (
        df["Recent_BB_Lower_Event"]
        & df["No_Lower_Low"]
    )

    df["Recent_Event_Higher_Low"] = (
        df["Recent_BB_Lower_Event"]
        & df["Higher_Low"]
    )

    df["Recent_Event_Close_Up"] = (
        df["Recent_BB_Lower_Event"]
        & df["Close_Up"]
    )

    df["Recent_Event_Bullish_Candle"] = (
        df["Recent_BB_Lower_Event"]
        & df["Bullish_Candle"]
    )

    df["Recent_Event_Reclaim"] = (
        df["Recent_BB_Lower_Event"]
        & df["BB_Lower_Reclaim"]
    )

    # v1.3の下落停止候補
    df["Decline_Stop_Candidate"] = (
        df["Recent_BB_Lower_Event"]
        & df["Decline_Stop_Combo"]
    )

    # 研究用確認項目数
    df["Decline_Stop_Condition_Count"] = (
        df[
            [
                "Higher_Low",
                "Close_Up",
                "Bullish_Candle",
                "BB_Lower_Reclaim",
            ]
        ]
        .astype(int)
        .sum(axis=1)
    )

    return df


# ============================================================
# v1.3
# 下落停止状態分類
# ============================================================

def classify_decline_stop(
    row,
) -> str:

    if not bool(
        row["Recent_BB_Lower_Event"]
    ):
        return "BB下限イベントなし"

    if bool(
        row["Decline_Stop_Candidate"]
    ):

        if bool(
            row["BB_Lower_Reclaim"]
        ):
            return "下落停止候補・BB内復帰あり"

        return "下落停止候補"

    if bool(
        row["BB_Lower_Reclaim"]
    ):
        return "BB内復帰のみ"

    if bool(
        row["Higher_Low"]
    ):
        return "安値切り上げのみ"

    if bool(
        row["Close_Up"]
    ):
        return "終値上昇のみ"

    return "下落停止未確認"


# ============================================================
# v1.3.1
# BB下限局面をイベント単位に整理
#
# 考え方
#
# BB下限タッチが発生したらイベント開始。
#
# その後3営業日以内に再びBB下限タッチがあれば、
# 同じ下落局面として同一イベントにまとめる。
#
# 最後のBB下限タッチから3営業日を超えてから
# 新しいBB下限タッチが発生した場合、
# 新しいイベントとして扱う。
#
# これは研究用のイベント定義。
# ============================================================

def calculate_bb_event_units(
    data: pd.DataFrame,
    gap_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    row_count = len(df)

    event_ids = [
        np.nan
    ] * row_count

    new_event_flags = [
        False
    ] * row_count

    event_start_dates = [
        pd.NaT
    ] * row_count

    days_from_event_start = [
        np.nan
    ] * row_count

    event_counter = 0

    active_event_id = None

    last_touch_position = None

    event_start_position = None

    event_start_date = pd.NaT


    for position in range(
        row_count
    ):

        is_touch = bool(
            df.iloc[position][
                "BB_Lower_Touch"
            ]
        )

        # ----------------------------------------------------
        # BB下限タッチが発生
        # ----------------------------------------------------

        if is_touch:

            # 初回タッチ
            # または前回タッチから3営業日を超えた
            if (
                last_touch_position is None
                or (
                    position
                    - last_touch_position
                    > gap_days
                )
            ):

                event_counter += 1

                active_event_id = (
                    event_counter
                )

                event_start_position = (
                    position
                )

                event_start_date = (
                    df.index[position]
                )

                new_event_flags[
                    position
                ] = True

            # 最後にタッチした位置を更新
            last_touch_position = (
                position
            )

        # ----------------------------------------------------
        # 最後のタッチから3営業日以内なら
        # イベント継続中
        # ----------------------------------------------------

        if (
            active_event_id is not None
            and last_touch_position is not None
            and (
                position
                - last_touch_position
                <= gap_days
            )
        ):

            event_ids[
                position
            ] = active_event_id

            event_start_dates[
                position
            ] = event_start_date

            if (
                event_start_position
                is not None
            ):

                days_from_event_start[
                    position
                ] = (
                    position
                    - event_start_position
                )

        # ----------------------------------------------------
        # 最後のタッチから3営業日を超えた
        # ----------------------------------------------------

        elif (
            last_touch_position
            is not None
            and (
                position
                - last_touch_position
                > gap_days
            )
        ):

            active_event_id = None

            event_start_position = None

            event_start_date = pd.NaT


    df["BB_Event_ID"] = (
        event_ids
    )

    df["New_BB_Lower_Event"] = (
        new_event_flags
    )

    df["BB_Event_Start_Date"] = (
        event_start_dates
    )

    df["Days_From_BB_Event_Start"] = (
        days_from_event_start
    )

    return df


# ============================================================
# v1.3.1
# 各イベントで最初に発生した下落停止候補
# ============================================================

def calculate_first_decline_stop_per_event(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    first_candidate_flags = [
        False
    ] * len(df)

    seen_event_ids = set()

    for position in range(
        len(df)
    ):

        event_id = (
            df.iloc[position][
                "BB_Event_ID"
            ]
        )

        is_candidate = bool(
            df.iloc[position][
                "Decline_Stop_Candidate"
            ]
        )

        if (
            pd.notna(event_id)
            and is_candidate
        ):

            event_id_int = int(
                event_id
            )

            if (
                event_id_int
                not in seen_event_ids
            ):

                first_candidate_flags[
                    position
                ] = True

                seen_event_ids.add(
                    event_id_int
                )


    df[
        "First_Decline_Stop_In_Event"
    ] = first_candidate_flags


    # --------------------------------------------------------
    # 最初の下落停止確認時のBB状態
    # --------------------------------------------------------

    first_states = []

    for position in range(
        len(df)
    ):

        if not bool(
            df.iloc[position][
                "First_Decline_Stop_In_Event"
            ]
        ):

            first_states.append(
                "対象外"
            )

            continue

        if bool(
            df.iloc[position][
                "BB_Lower_Close_Below"
            ]
        ):

            first_states.append(
                "BB下限より下で終値"
            )

        elif bool(
            df.iloc[position][
                "BB_Lower_Reclaim"
            ]
        ):

            first_states.append(
                "下抜け後BB内復帰"
            )

        else:

            first_states.append(
                "終値はBB内"
            )


    df[
        "First_Stop_BB_State"
    ] = first_states

    return df


# ============================================================
# 全データ準備
# ============================================================

def prepare_data(
    ticker: str,
    period: str,
) -> pd.DataFrame:

    df = get_stock_data(
        ticker,
        period,
    )

    if df.empty:
        return df

    # 1. BB
    df = calculate_bollinger_bands(
        df,
        BB_PERIOD,
        BB_STD,
    )

    # 2. BandWidth
    df = calculate_bandwidth(
        df
    )

    # 3. BB下限との距離
    df = calculate_lower_band_distance(
        df
    )

    # 4. BandWidth状態
    df = calculate_bandwidth_state(
        df,
        SQUEEZE_LOOKBACK,
    )

    # 5. BandWidth方向
    df[
        "BandWidth_Direction"
    ] = df.apply(
        classify_bandwidth_direction,
        axis=1,
    )

    # 6. Squeeze状態
    df[
        "Squeeze_State"
    ] = df.apply(
        classify_squeeze_state,
        axis=1,
    )

    # 7. BB下限イベント
    df = calculate_lower_band_events(
        df
    )

    df[
        "Lower_Band_Event"
    ] = df.apply(
        classify_lower_band_event,
        axis=1,
    )

    # 8. 下方向拡大
    df = calculate_downside_expansion(
        df
    )

    df[
        "Downside_Expansion_State"
    ] = df.apply(
        classify_downside_expansion,
        axis=1,
    )

    # 9. 下落停止基本条件
    df = calculate_decline_stop_conditions(
        df
    )

    # 10. BB下限イベント後追跡
    df = calculate_lower_event_window(
        df,
        LOWER_EVENT_LOOKBACK_DAYS,
    )

    # 11. 下落停止候補
    df = calculate_decline_stop_candidates(
        df
    )

    df[
        "Decline_Stop_State"
    ] = df.apply(
        classify_decline_stop,
        axis=1,
    )

    # 12. v1.3.1
    # BB下限局面をイベント単位化
    df = calculate_bb_event_units(
        df,
        LOWER_EVENT_LOOKBACK_DAYS,
    )

    # 13. v1.3.1
    # イベント最初の下落停止候補
    df = (
        calculate_first_decline_stop_per_event(
            df
        )
    )

    return df


# ============================================================
# 表示補助
# ============================================================

def format_number(
    value,
    digits=2,
):

    if pd.isna(value):
        return "計算不可"

    return f"{value:,.{digits}f}"


def yes_no(
    value,
) -> str:

    if bool(value):
        return "はい"

    return "いいえ"


def format_days_since_touch(
    value,
) -> str:

    if pd.isna(value):
        return "直近3営業日以内になし"

    value = int(value)

    if value == 0:
        return "本日"

    return f"{value}営業日前"


def format_event_id(
    value,
) -> str:

    if pd.isna(value):
        return "なし"

    return str(
        int(value)
    )


# ============================================================
# タイトル
# ============================================================

st.title(
    "📊 GOOG・NVDA BB下限研究"
)

st.caption(
    f"Version {APP_VERSION} ｜ "
    "BB下限イベント単位整理版"
)

st.info(
    "v1.3の下落停止候補を残したまま、"
    "v1.3.1では同じBB下限局面から発生する"
    "複数の候補日をイベント単位で整理します。"
    "まだ買い・売り判断は行いません。"
)


# ============================================================
# ① 銘柄
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


# ============================================================
# 期間
# ============================================================

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

    st.warning(
        "Yahoo Finance側の一時的な通信エラーの"
        "可能性があります。"
        "少し時間を置いて再読み込みしてください。"
    )

    st.stop()


# ============================================================
# BB計算済みデータ
# ============================================================

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

latest_date = (
    valid_df.index[-1]
)


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


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "終値",
        f"${format_number(latest['Close'])}",
    )

    st.metric(
        "BB中央線",
        f"${format_number(latest['BB_Middle'])}",
    )

    st.metric(
        "BB下限",
        f"${format_number(latest['BB_Lower'])}",
    )


with col2:

    st.metric(
        "BB上限",
        f"${format_number(latest['BB_Upper'])}",
    )

    st.metric(
        "BandWidth",
        f"{format_number(latest['BandWidth'])}%",
    )

    st.metric(
        "終値とBB下限の距離",
        f"{format_number(latest['Lower_Distance_Close'])}%",
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
    "現在は研究表示です。"
)


# ============================================================
# ④ Squeeze
# ============================================================

st.subheader(
    "④ スクイーズ状態"
)

squeeze_state = latest[
    "Squeeze_State"
]

direction_state = latest[
    "BandWidth_Direction"
]


if squeeze_state == "公式Squeeze基準":

    st.warning(
        "現在のBandWidthは"
        "過去125営業日の最低水準です。"
    )

elif squeeze_state == "低BandWidth・収縮中":

    st.info(
        "研究分類："
        "BandWidthは125営業日の中で低い位置にあり、"
        "現在も収縮方向です。"
    )

elif squeeze_state == "低BandWidth・拡大開始候補":

    st.warning(
        "研究分類："
        "低BandWidth状態から"
        "拡大し始めている可能性があります。"
    )

elif squeeze_state == "低BandWidth":

    st.info(
        "研究分類："
        "BandWidthは125営業日の中で"
        "低い位置にあります。"
    )

elif squeeze_state == "非Squeeze":

    st.success(
        "現在は低BandWidthゾーンではありません。"
    )

else:

    st.write(
        "スクイーズ状態はまだ判定できません。"
    )


st.write(
    "BandWidth方向：",
    direction_state,
)


# ============================================================
# ⑤ 正規化BandWidth
# ============================================================

st.subheader(
    "⑤ 125営業日内でのBandWidth位置"
)

normalized = latest[
    "Normalized_BandWidth"
]


if pd.isna(normalized):

    st.info(
        "125営業日の計算に必要な"
        "データが不足しています。"
    )

else:

    normalized_percent = (
        normalized * 100
    )

    st.metric(
        "正規化BandWidth",
        f"{format_number(normalized_percent)}%",
    )

    st.write(
        "0％に近いほど過去125営業日の"
        "最低BandWidthに近く、"
        "100％に近いほど最高BandWidthに近い状態です。"
    )

    st.write(
        "過去125営業日の最小BandWidth：",
        f"{format_number(latest['BandWidth_Min_125'])}%",
    )

    st.write(
        "過去125営業日の最大BandWidth：",
        f"{format_number(latest['BandWidth_Max_125'])}%",
    )


st.caption(
    "20％以下は研究用の仮分類です。"
    "正式な売買条件ではありません。"
)


# ============================================================
# ⑥ BandWidth変化
# ============================================================

st.subheader(
    "⑥ BandWidth変化"
)

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "前日比",
        format_number(
            latest[
                "BandWidth_Change_1D"
            ]
        ),
    )


with col2:

    st.metric(
        "3営業日前比",
        format_number(
            latest[
                "BandWidth_Change_3D"
            ]
        ),
    )


with col3:

    st.metric(
        "5営業日前比",
        format_number(
            latest[
                "BandWidth_Change_5D"
            ]
        ),
    )


st.write(
    "現在の方向分類：",
    direction_state,
)


# ============================================================
# ⑦ BB下限イベント
# ============================================================

st.subheader(
    "⑦ BB下限イベント"
)

st.write(
    "現在のBB下限状態：",
    latest[
        "Lower_Band_Event"
    ],
)


event_col1, event_col2 = (
    st.columns(2)
)


with event_col1:

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


with event_col2:

    st.write(
        "下抜け後、終値でBB内復帰：",
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
# ⑧ 下方向拡大
# ============================================================

st.subheader(
    "⑧ 低BandWidthからの下方向拡大"
)

st.write(
    "現在の分類：",
    latest[
        "Downside_Expansion_State"
    ],
)


if bool(
    latest[
        "Downside_Expansion_Close_Below"
    ]
):

    st.warning(
        "低BandWidth状態からBandWidthが拡大し、"
        "終値もBB下限より下です。"
    )

elif bool(
    latest[
        "Downside_Expansion_Reclaim"
    ]
):

    st.info(
        "低BandWidth状態からBandWidthが拡大し、"
        "日中はBB下限を下抜けましたが、"
        "終値ではBB内へ復帰しています。"
    )

elif bool(
    latest[
        "Downside_Expansion_Candidate"
    ]
):

    st.info(
        "低BandWidthからの"
        "下方向拡大開始候補です。"
    )

else:

    st.write(
        "現在は研究用の"
        "下方向拡大条件には該当していません。"
    )


# ============================================================
# ⑨ v1.3 下落停止候補
# ============================================================

st.subheader(
    "⑨ 下落停止候補"
)

st.write(
    "現在の研究分類：",
    latest[
        "Decline_Stop_State"
    ],
)

st.write(
    "直近のBB下限タッチ：",
    format_days_since_touch(
        latest[
            "Days_Since_BB_Lower_Touch"
        ]
    ),
)


stop_col1, stop_col2 = (
    st.columns(2)
)


with stop_col1:

    st.write(
        "前日安値を割らない：",
        yes_no(
            latest[
                "No_Lower_Low"
            ]
        ),
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


with stop_col2:

    st.write(
        "陽線：",
        yes_no(
            latest[
                "Bullish_Candle"
            ]
        ),
    )

    st.write(
        "当日のBB内復帰：",
        yes_no(
            latest[
                "BB_Lower_Reclaim"
            ]
        ),
    )

    st.write(
        "安値切り上げ＋終値上昇：",
        yes_no(
            latest[
                "Decline_Stop_Combo"
            ]
        ),
    )


st.metric(
    "確認項目数",
    (
        f"{int(latest['Decline_Stop_Condition_Count'])}"
        " / 4"
    ),
)


# ============================================================
# ⑩ v1.3.1 イベント単位
# ============================================================

st.subheader(
    "⑩ BB下限イベント単位"
)

st.write(
    "現在のイベント番号：",
    format_event_id(
        latest[
            "BB_Event_ID"
        ]
    ),
)

st.write(
    "本日が新しいBB下限イベント開始日：",
    yes_no(
        latest[
            "New_BB_Lower_Event"
        ]
    ),
)

st.write(
    "このイベントで最初の下落停止確認日：",
    yes_no(
        latest[
            "First_Decline_Stop_In_Event"
        ]
    ),
)


if pd.notna(
    latest[
        "BB_Event_Start_Date"
    ]
):

    event_start = pd.to_datetime(
        latest[
            "BB_Event_Start_Date"
        ]
    )

    st.write(
        "イベント開始日：",
        event_start.strftime(
            "%Y年%m月%d日"
        ),
    )


if bool(
    latest[
        "First_Decline_Stop_In_Event"
    ]
):

    st.info(
        "この日は、現在のBB下限イベントで"
        "最初に確認された下落停止候補です。"
        "将来のイベント単位検証では、"
        "この日を代表確認日として扱う候補になります。"
    )


st.caption(
    "同じBB下限局面で候補が3日連続しても、"
    "イベント単位では最初の1回だけを"
    "別に記録します。"
    "v1.3の元の候補日は削除していません。"
)


# ============================================================
# ⑪ 株価チャート
# ============================================================

st.divider()

st.subheader(
    "⑪ 株価とボリンジャーバンド"
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
# ⑫ BandWidth
# ============================================================

st.subheader(
    "⑫ BandWidth"
)

bandwidth_chart = (
    valid_df[
        [
            "BandWidth",
        ]
    ]
    .tail(chart_days)
    .copy()
)

bandwidth_chart.columns = [
    "BandWidth",
]

st.line_chart(
    bandwidth_chart,
    use_container_width=True,
)


# ============================================================
# ⑬ 正規化BandWidth
# ============================================================

st.subheader(
    "⑬ 正規化BandWidth"
)

normalized_chart = (
    valid_df[
        [
            "Normalized_BandWidth",
        ]
    ]
    .tail(chart_days)
    .copy()
    * 100
)

normalized_chart.columns = [
    "正規化BandWidth %",
]

st.line_chart(
    normalized_chart,
    use_container_width=True,
)


# ============================================================
# ⑭ 最新30営業日
# ============================================================

st.subheader(
    "⑭ 最新30営業日の状態確認"
)


display_df = (
    valid_df[
        [
            "Close",
            "Low",
            "BB_Lower",
            "Lower_Distance_Close",
            "BandWidth",
            "Normalized_BandWidth",
            "Lower_Band_Event",
            "Higher_Low",
            "Close_Up",
            "Bullish_Candle",
            "Decline_Stop_State",
            "BB_Event_ID",
            "First_Decline_Stop_In_Event",
        ]
    ]
    .tail(30)
    .copy()
)


display_df[
    "Normalized_BandWidth"
] = (
    display_df[
        "Normalized_BandWidth"
    ]
    * 100
)


display_df = display_df.rename(
    columns={
        "Close":
            "終値",

        "Low":
            "安値",

        "BB_Lower":
            "BB下限",

        "Lower_Distance_Close":
            "終値→BB下限 %",

        "BandWidth":
            "BandWidth %",

        "Normalized_BandWidth":
            "正規化BW %",

        "Lower_Band_Event":
            "BB下限イベント",

        "Higher_Low":
            "安値切上",

        "Close_Up":
            "終値上昇",

        "Bullish_Candle":
            "陽線",

        "Decline_Stop_State":
            "下落停止状態",

        "BB_Event_ID":
            "イベントID",

        "First_Decline_Stop_In_Event":
            "イベント最初確認",
    }
)


numeric_columns = [
    "終値",
    "安値",
    "BB下限",
    "終値→BB下限 %",
    "BandWidth %",
    "正規化BW %",
]


display_df[
    numeric_columns
] = (
    display_df[
        numeric_columns
    ]
    .round(2)
)


st.dataframe(
    display_df,
    use_container_width=True,
)


# ============================================================
# ⑮ 基本分類件数
# ============================================================

st.subheader(
    "⑮ 基本分類件数"
)


research_df = valid_df.dropna(
    subset=[
        "Normalized_BandWidth",
    ]
).copy()


if research_df.empty:

    st.info(
        "分類集計に必要なデータがありません。"
    )

else:

    official_count = int(
        research_df[
            "Official_Squeeze"
        ].sum()
    )

    low_bw_count = int(
        research_df[
            "Low_BandWidth_Zone"
        ].sum()
    )

    touch_count = int(
        research_df[
            "BB_Lower_Touch"
        ].sum()
    )

    reclaim_count = int(
        research_df[
            "BB_Lower_Reclaim"
        ].sum()
    )

    close_below_count = int(
        research_df[
            "BB_Lower_Close_Below"
        ].sum()
    )

    downside_count = int(
        research_df[
            "Downside_Expansion_Candidate"
        ].sum()
    )

    total_count = len(
        research_df
    )


    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "判定可能日",
            f"{total_count}日",
        )

    with col2:

        st.metric(
            "125日最低BW基準日",
            f"{official_count}日",
        )

    with col3:

        st.metric(
            "研究用 低BWゾーン",
            f"{low_bw_count}日",
        )


    col4, col5, col6 = (
        st.columns(3)
    )

    with col4:

        st.metric(
            "BB下限タッチ",
            f"{touch_count}日",
        )

    with col5:

        st.metric(
            "下抜け後BB内復帰",
            f"{reclaim_count}日",
        )

    with col6:

        st.metric(
            "BB下限より下で終値",
            f"{close_below_count}日",
        )


    st.metric(
        "低BW→下方向拡大候補",
        f"{downside_count}日",
    )


# ============================================================
# ⑯ v1.3 下落停止条件件数
# ============================================================

st.subheader(
    "⑯ 下落停止条件の発生件数"
)


if research_df.empty:

    st.info(
        "下落停止条件を集計できません。"
    )

else:

    no_lower_low_count = int(
        research_df[
            "No_Lower_Low"
        ].sum()
    )

    higher_low_count = int(
        research_df[
            "Higher_Low"
        ].sum()
    )

    close_up_count = int(
        research_df[
            "Close_Up"
        ].sum()
    )

    bullish_count = int(
        research_df[
            "Bullish_Candle"
        ].sum()
    )

    combo_count = int(
        research_df[
            "Decline_Stop_Combo"
        ].sum()
    )

    recent_event_count = int(
        research_df[
            "Recent_BB_Lower_Event"
        ].sum()
    )

    raw_decline_stop_count = int(
        research_df[
            "Decline_Stop_Candidate"
        ].sum()
    )


    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "前日安値を割らない",
            f"{no_lower_low_count}日",
        )

    with col2:

        st.metric(
            "安値切り上げ",
            f"{higher_low_count}日",
        )

    with col3:

        st.metric(
            "前日終値より上昇",
            f"{close_up_count}日",
        )


    col4, col5, col6 = (
        st.columns(3)
    )

    with col4:

        st.metric(
            "陽線",
            f"{bullish_count}日",
        )

    with col5:

        st.metric(
            "安値切上＋終値上昇",
            f"{combo_count}日",
        )

    with col6:

        st.metric(
            "BB下限イベント後3日以内",
            f"{recent_event_count}日",
        )


    st.metric(
        "v1.3 下落停止候補日",
        f"{raw_decline_stop_count}日",
    )


# ============================================================
# ⑰ v1.3.1 イベント単位集計
# ============================================================

st.subheader(
    "⑰ BB下限イベント単位の集計"
)


if research_df.empty:

    st.info(
        "イベント単位の集計ができません。"
    )

else:

    event_count = int(
        research_df[
            "New_BB_Lower_Event"
        ].sum()
    )

    first_stop_count = int(
        research_df[
            "First_Decline_Stop_In_Event"
        ].sum()
    )

    raw_candidate_count = int(
        research_df[
            "Decline_Stop_Candidate"
        ].sum()
    )

    duplicate_candidate_count = max(
        0,
        (
            raw_candidate_count
            - first_stop_count
        ),
    )

    no_stop_event_count = max(
        0,
        (
            event_count
            - first_stop_count
        ),
    )


    first_stop_df = research_df[
        research_df[
            "First_Decline_Stop_In_Event"
        ]
    ].copy()


    first_below_count = int(
        (
            first_stop_df[
                "First_Stop_BB_State"
            ]
            == "BB下限より下で終値"
        ).sum()
    )


    first_reclaim_count = int(
        (
            first_stop_df[
                "First_Stop_BB_State"
            ]
            == "下抜け後BB内復帰"
        ).sum()
    )


    first_inside_count = int(
        (
            first_stop_df[
                "First_Stop_BB_State"
            ]
            == "終値はBB内"
        ).sum()
    )


    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "BB下限イベント数",
            f"{event_count}回",
        )

    with col2:

        st.metric(
            "下落停止確認イベント",
            f"{first_stop_count}回",
        )

    with col3:

        st.metric(
            "下落停止未確認イベント",
            f"{no_stop_event_count}回",
        )


    col4, col5 = (
        st.columns(2)
    )

    with col4:

        st.metric(
            "v1.3 候補日数",
            f"{raw_candidate_count}日",
        )

    with col5:

        st.metric(
            "イベント内の重複候補日",
            f"{duplicate_candidate_count}日",
        )


    st.write(
        "イベント最初の下落停止確認時のBB状態"
    )


    col6, col7, col8 = (
        st.columns(3)
    )

    with col6:

        st.metric(
            "BB下限より下で終値",
            f"{first_below_count}回",
        )

    with col7:

        st.metric(
            "下抜け後BB内復帰",
            f"{first_reclaim_count}回",
        )

    with col8:

        st.metric(
            "終値はBB内",
            f"{first_inside_count}回",
        )


    st.caption(
        "重要："
        "v1.3の候補日数と、"
        "v1.3.1の下落停止確認イベント数は"
        "意味が異なります。"
        "イベント単位では同じBB下限局面を"
        "重複して数えないようにしています。"
    )


# ============================================================
# ⑱ v1.3
# 元の下落停止候補一覧
# ============================================================

st.subheader(
    "⑱ v1.3 下落停止候補日の一覧"
)


decline_stop_df = valid_df[
    valid_df[
        "Decline_Stop_Candidate"
    ]
].copy()


if decline_stop_df.empty:

    st.info(
        "選択した期間には"
        "下落停止候補がありません。"
    )

else:

    decline_display = (
        decline_stop_df[
            [
                "Open",
                "Close",
                "Low",
                "BB_Lower",
                "Days_Since_BB_Lower_Touch",
                "Higher_Low",
                "Close_Up",
                "Bullish_Candle",
                "BB_Lower_Reclaim",
                "BandWidth",
                "Normalized_BandWidth",
                "BB_Event_ID",
                "First_Decline_Stop_In_Event",
                "Decline_Stop_State",
            ]
        ]
        .tail(50)
        .copy()
    )


    decline_display[
        "Normalized_BandWidth"
    ] = (
        decline_display[
            "Normalized_BandWidth"
        ]
        * 100
    )


    decline_display = (
        decline_display.rename(
            columns={
                "Open":
                    "始値",

                "Close":
                    "終値",

                "Low":
                    "安値",

                "BB_Lower":
                    "BB下限",

                "Days_Since_BB_Lower_Touch":
                    "BBタッチから営業日",

                "Higher_Low":
                    "安値切上",

                "Close_Up":
                    "終値上昇",

                "Bullish_Candle":
                    "陽線",

                "BB_Lower_Reclaim":
                    "BB内復帰",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "BB_Event_ID":
                    "イベントID",

                "First_Decline_Stop_In_Event":
                    "イベント最初確認",

                "Decline_Stop_State":
                    "下落停止状態",
            }
        )
    )


    numeric_cols = [
        "始値",
        "終値",
        "安値",
        "BB下限",
        "BBタッチから営業日",
        "BandWidth %",
        "正規化BW %",
    ]


    decline_display[
        numeric_cols
    ] = (
        decline_display[
            numeric_cols
        ]
        .round(2)
    )


    st.dataframe(
        decline_display,
        use_container_width=True,
    )


    st.caption(
        "この表にはv1.3の候補日を"
        "すべて残しています。"
        "同じイベント内で複数日が"
        "表示される場合があります。"
    )


# ============================================================
# ⑲ v1.3.1
# イベント最初の下落停止確認だけ抽出
# ============================================================

st.subheader(
    "⑲ イベント最初の下落停止確認一覧"
)


first_event_df = valid_df[
    valid_df[
        "First_Decline_Stop_In_Event"
    ]
].copy()


if first_event_df.empty:

    st.info(
        "選択した期間には"
        "イベント単位の下落停止確認がありません。"
    )

else:

    first_event_display = (
        first_event_df[
            [
                "BB_Event_ID",
                "BB_Event_Start_Date",
                "Days_From_BB_Event_Start",
                "Days_Since_BB_Lower_Touch",
                "Open",
                "Close",
                "Low",
                "BB_Lower",
                "Higher_Low",
                "Close_Up",
                "Bullish_Candle",
                "BB_Lower_Reclaim",
                "BB_Lower_Close_Below",
                "First_Stop_BB_State",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
            ]
        ]
        .tail(50)
        .copy()
    )


    first_event_display[
        "Normalized_BandWidth"
    ] = (
        first_event_display[
            "Normalized_BandWidth"
        ]
        * 100
    )


    first_event_display = (
        first_event_display.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "BB_Event_Start_Date":
                    "イベント開始日",

                "Days_From_BB_Event_Start":
                    "開始から営業日",

                "Days_Since_BB_Lower_Touch":
                    "直近タッチから営業日",

                "Open":
                    "始値",

                "Close":
                    "終値",

                "Low":
                    "安値",

                "BB_Lower":
                    "BB下限",

                "Higher_Low":
                    "安値切上",

                "Close_Up":
                    "終値上昇",

                "Bullish_Candle":
                    "陽線",

                "BB_Lower_Reclaim":
                    "BB内復帰",

                "BB_Lower_Close_Below":
                    "BB下終値",

                "First_Stop_BB_State":
                    "確認時BB状態",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "Squeeze_State":
                    "BW環境",
            }
        )
    )


    event_numeric_cols = [
        "開始から営業日",
        "直近タッチから営業日",
        "始値",
        "終値",
        "安値",
        "BB下限",
        "BandWidth %",
        "正規化BW %",
    ]


    first_event_display[
        event_numeric_cols
    ] = (
        first_event_display[
            event_numeric_cols
        ]
        .round(2)
    )


    st.dataframe(
        first_event_display,
        use_container_width=True,
    )


    st.caption(
        "この表では、"
        "同じBB下限イベントの中で"
        "最初に成立した下落停止候補だけを"
        "1行として表示しています。"
        "将来の1R・1.5R・2R検証では、"
        "このイベント単位のデータを使う候補です。"
    )


# ============================================================
# ⑳ BB下限注目イベント
# ============================================================

st.subheader(
    "⑳ BB下限の注目イベント"
)


event_df = valid_df[
    (
        valid_df[
            "BB_Lower_Touch"
        ]
        | valid_df[
            "Downside_Expansion_Candidate"
        ]
    )
].copy()


if event_df.empty:

    st.info(
        "選択した期間には"
        "BB下限の注目イベントがありません。"
    )

else:

    event_display = (
        event_df[
            [
                "Close",
                "Low",
                "BB_Lower",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
                "Lower_Band_Event",
                "Downside_Expansion_State",
                "BB_Event_ID",
                "New_BB_Lower_Event",
            ]
        ]
        .tail(50)
        .copy()
    )


    event_display[
        "Normalized_BandWidth"
    ] = (
        event_display[
            "Normalized_BandWidth"
        ]
        * 100
    )


    event_display = (
        event_display.rename(
            columns={
                "Close":
                    "終値",

                "Low":
                    "安値",

                "BB_Lower":
                    "BB下限",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "Squeeze_State":
                    "スクイーズ状態",

                "Lower_Band_Event":
                    "BB下限イベント",

                "Downside_Expansion_State":
                    "下方向拡大状態",

                "BB_Event_ID":
                    "イベントID",

                "New_BB_Lower_Event":
                    "新イベント開始",
            }
        )
    )


    event_numeric_columns = [
        "終値",
        "安値",
        "BB下限",
        "BandWidth %",
        "正規化BW %",
    ]


    event_display[
        event_numeric_columns
    ] = (
        event_display[
            event_numeric_columns
        ]
        .round(2)
    )


    st.dataframe(
        event_display,
        use_container_width=True,
    )


# ============================================================
# ㉑ 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "㉑ 現在の研究段階"
)


st.write(
    "【実装済み】GOOG / NVDA 切り替え"
)

st.write(
    "【実装済み】20日・2標準偏差BB"
)

st.write(
    "【実装済み】BandWidth"
)

st.write(
    "【実装済み】125営業日BandWidth正規化"
)

st.write(
    "【研究分類】低BandWidthゾーン"
)

st.write(
    "【実装済み】BandWidth収縮・拡大分類"
)

st.write(
    "【v1.2 実装済み】BB下限タッチ"
)

st.write(
    "【v1.2 実装済み】BB下限下抜け"
)

st.write(
    "【v1.2 実装済み】BB内復帰"
)

st.write(
    "【v1.2 実装済み】BB下限より下で終値"
)

st.write(
    "【v1.3 実装済み】安値切り上げ"
)

st.write(
    "【v1.3 実装済み】前日終値より上昇"
)

st.write(
    "【v1.3 実装済み】陽線"
)

st.write(
    "【v1.3 研究分類】安値切り上げ＋終値上昇"
)

st.write(
    "【v1.3 研究分類】下落停止候補"
)

st.write(
    "【v1.3.1 実装済み】BB下限局面のイベントID"
)

st.write(
    "【v1.3.1 実装済み】近接BBタッチの同一イベント化"
)

st.write(
    "【v1.3.1 実装済み】イベント最初の下落停止確認"
)

st.write(
    "【v1.3.1 実装済み】候補日の重複件数確認"
)

st.write(
    "【v1.3.1 研究分類】確認時のBB状態分離"
)

st.write(
    "【未検証】下落停止候補に利益上の優位性があるか"
)

st.write(
    "【未実装】反発開始判定"
)

st.write(
    "【未実装】1R損切り"
)

st.write(
    "【未実装】1.5R / 2R到達検証"
)

st.write(
    "【未実装】イベント単位バックテスト"
)


# ============================================================
# 重要説明
# ============================================================

st.divider()

st.warning(
    "重要："
    "v1.3.1では同じBB下限局面を"
    "重複して数えにくくするため、"
    "イベント単位の分類を追加しました。"
    "ただし『3営業日』という区切りも、"
    "下落停止条件そのものもまだ研究中です。"
    "利益が出ることはまだ検証していません。"
)


st.caption(
    "このプログラムは研究・検証用です。"
    "表示された状態は将来の株価上昇・下落を"
    "保証するものではありません。"
)
