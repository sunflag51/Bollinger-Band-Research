# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.3.3
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
# ・BB下限タッチ後の下落停止候補
#
# v1.3.2
# ・最初のBB下限タッチを0日目
# ・0～3営業日目の固定観察
# ・途中の再タッチでは期間を延長しない
# ・固定期間内の最初の下落停止候補を記録
#
# v1.3.3
# ・観察完了イベントと未完了イベントを分離
# ・統計は観察完了イベントだけを母数にする
# ・データ末尾の未完了イベントを失敗扱いしない
# ・完了イベントの確認率を表示
# ・完了イベントだけで確認タイミングを集計
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

APP_VERSION = "1.3.3"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125

# 研究用低BandWidthゾーン
LOW_BANDWIDTH_ZONE = 0.20

# 最初のBB下限タッチを0日目として
# 0・1・2・3営業日目を観察
LOWER_EVENT_OBSERVATION_DAYS = 3


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
# BandWidth 状態
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
# 低BandWidthから下方向拡大
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
# 下方向拡大分類
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

    df["Prev_Low"] = df["Low"].shift(1)
    df["Prev_Close"] = df["Close"].shift(1)

    df["No_Lower_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] >= df["Prev_Low"])
    )

    df["Higher_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] > df["Prev_Low"])
    )

    df["Close_Up"] = (
        df["Prev_Close"].notna()
        & (df["Close"] > df["Prev_Close"])
    )

    df["Bullish_Candle"] = (
        df["Close"] > df["Open"]
    )

    # 現在の研究用「下落停止候補」
    df["Decline_Stop_Combo"] = (
        df["Higher_Low"]
        & df["Close_Up"]
    )

    return df


# ============================================================
# v1.3
# 従来の直近BB下限タッチ追跡
#
# 過去バージョンとの比較のため残す
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
# 従来の下落停止候補
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

    df["Decline_Stop_Candidate"] = (
        df["Recent_BB_Lower_Event"]
        & df["Decline_Stop_Combo"]
    )

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
# v1.3.2
# 固定観察期間方式
#
# 最初のBB下限タッチ = 0日目
# 0・1・2・3営業日目だけ観察
#
# 再タッチしても期間を延長しない
# ============================================================

def calculate_fixed_bb_event_units(
    data: pd.DataFrame,
    observation_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    row_count = len(df)

    event_ids = [np.nan] * row_count
    new_event_flags = [False] * row_count
    event_start_dates = [pd.NaT] * row_count
    days_from_event_start = [np.nan] * row_count

    event_counter = 0
    active_event_id = None
    event_start_position = None
    event_start_date = pd.NaT

    for position in range(row_count):

        # 前の固定観察期間が終了したか
        if (
            active_event_id is not None
            and event_start_position is not None
            and (
                position
                - event_start_position
                > observation_days
            )
        ):

            active_event_id = None
            event_start_position = None
            event_start_date = pd.NaT

        is_touch = bool(
            df.iloc[position][
                "BB_Lower_Touch"
            ]
        )

        # イベントがない状態でタッチしたら開始
        if (
            active_event_id is None
            and is_touch
        ):

            event_counter += 1

            active_event_id = event_counter
            event_start_position = position
            event_start_date = df.index[position]

            new_event_flags[position] = True

        # 固定観察期間内
        if (
            active_event_id is not None
            and event_start_position is not None
        ):

            event_ids[position] = (
                active_event_id
            )

            event_start_dates[position] = (
                event_start_date
            )

            days_from_event_start[position] = (
                position
                - event_start_position
            )

    df["BB_Event_ID"] = event_ids

    df["New_BB_Lower_Event"] = (
        new_event_flags
    )

    df["BB_Event_Start_Date"] = (
        event_start_dates
    )

    df["Days_From_BB_Event_Start"] = (
        days_from_event_start
    )

    df["Fixed_Event_Window"] = (
        df["BB_Event_ID"].notna()
    )

    df[
        "Fixed_Window_Decline_Stop_Candidate"
    ] = (
        df["Fixed_Event_Window"]
        & df["Decline_Stop_Combo"]
    )

    return df


# ============================================================
# v1.3.3
# 観察完了 / 未完了判定
#
# イベント開始位置から3営業日後まで
# 実データが存在する場合だけ「観察完了」
#
# 例
#
# 0日目 タッチ
# 1日目 データあり
# 2日目 データあり
# 3日目 データあり
#
# → 完了
#
# データ末尾で2日目までしか存在しない
#
# → 未完了
# ============================================================

def calculate_event_completion(
    data: pd.DataFrame,
    observation_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    row_count = len(df)

    df["Event_Observation_Complete"] = False
    df["Event_Observation_Status"] = "イベント外"
    df["Event_End_Date"] = pd.NaT

    event_start_positions = np.where(
        df["New_BB_Lower_Event"].to_numpy(
            dtype=bool
        )
    )[0]

    for start_position in event_start_positions:

        event_id = int(
            df.iloc[start_position][
                "BB_Event_ID"
            ]
        )

        end_position = (
            start_position
            + observation_days
        )

        event_mask = (
            df["BB_Event_ID"]
            == event_id
        )

        if end_position < row_count:

            end_date = df.index[
                end_position
            ]

            df.loc[
                event_mask,
                "Event_Observation_Complete",
            ] = True

            df.loc[
                event_mask,
                "Event_Observation_Status",
            ] = "観察完了"

            df.loc[
                event_mask,
                "Event_End_Date",
            ] = end_date

        else:

            df.loc[
                event_mask,
                "Event_Observation_Complete",
            ] = False

            df.loc[
                event_mask,
                "Event_Observation_Status",
            ] = "観察未完了"

    return df


# ============================================================
# イベント内最初の下落停止確認
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
                "Fixed_Window_Decline_Stop_Candidate"
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

    return df


# ============================================================
# 最初の下落停止確認時のBB状態
# ============================================================

def calculate_first_stop_bb_state(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    states = []

    for position in range(
        len(df)
    ):

        row = df.iloc[position]

        if not bool(
            row[
                "First_Decline_Stop_In_Event"
            ]
        ):

            states.append(
                "対象外"
            )

            continue

        if bool(
            row[
                "BB_Lower_Close_Below"
            ]
        ):

            states.append(
                "BB下限より下で終値"
            )

        elif bool(
            row[
                "BB_Lower_Reclaim"
            ]
        ):

            states.append(
                "下抜け後BB内復帰"
            )

        else:

            states.append(
                "終値はBB内"
            )

    df[
        "First_Stop_BB_State"
    ] = states

    return df


# ============================================================
# イベント結果
# ============================================================

def calculate_event_results(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Event_Has_Decline_Stop"] = False

    event_ids = (
        df["BB_Event_ID"]
        .dropna()
        .astype(int)
        .unique()
    )

    for event_id in event_ids:

        event_mask = (
            df["BB_Event_ID"]
            == event_id
        )

        has_stop = bool(
            df.loc[
                event_mask,
                "First_Decline_Stop_In_Event",
            ].any()
        )

        df.loc[
            event_mask,
            "Event_Has_Decline_Stop",
        ] = has_stop

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

    df = calculate_bollinger_bands(
        df,
        BB_PERIOD,
        BB_STD,
    )

    df = calculate_bandwidth(
        df
    )

    df = calculate_lower_band_distance(
        df
    )

    df = calculate_bandwidth_state(
        df,
        SQUEEZE_LOOKBACK,
    )

    df[
        "BandWidth_Direction"
    ] = df.apply(
        classify_bandwidth_direction,
        axis=1,
    )

    df[
        "Squeeze_State"
    ] = df.apply(
        classify_squeeze_state,
        axis=1,
    )

    df = calculate_lower_band_events(
        df
    )

    df[
        "Lower_Band_Event"
    ] = df.apply(
        classify_lower_band_event,
        axis=1,
    )

    df = calculate_downside_expansion(
        df
    )

    df[
        "Downside_Expansion_State"
    ] = df.apply(
        classify_downside_expansion,
        axis=1,
    )

    df = calculate_decline_stop_conditions(
        df
    )

    # v1.3 従来方式
    df = calculate_lower_event_window(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    df = calculate_decline_stop_candidates(
        df
    )

    df[
        "Decline_Stop_State"
    ] = df.apply(
        classify_decline_stop,
        axis=1,
    )

    # v1.3.2 固定イベント
    df = calculate_fixed_bb_event_units(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    # v1.3.3 観察完了判定
    df = calculate_event_completion(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    df = (
        calculate_first_decline_stop_per_event(
            df
        )
    )

    df = calculate_first_stop_bb_state(
        df
    )

    df = calculate_event_results(
        df
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

    return (
        "はい"
        if bool(value)
        else "いいえ"
    )


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
    "観察完了・未完了分離版"
)

st.info(
    "v1.3.3では、最初のBB下限タッチから"
    "0～3営業日目までの4営業日を"
    "最後まで観察できたイベントと、"
    "データ末尾のため観察できていないイベントを"
    "分離します。"
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
# ④ スクイーズ
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


st.write(
    "現在の分類：",
    squeeze_state,
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

    st.metric(
        "正規化BandWidth",
        f"{format_number(normalized * 100)}%",
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


# ============================================================
# ⑨ 下落停止候補
# ============================================================

st.subheader(
    "⑨ v1.3 下落停止候補"
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


col1, col2 = st.columns(2)


with col1:

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


with col2:

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
        "安値切上＋終値上昇：",
        yes_no(
            latest[
                "Decline_Stop_Combo"
            ]
        ),
    )


# ============================================================
# ⑩ 固定イベント状態
# ============================================================

st.subheader(
    "⑩ v1.3.3 固定観察イベント"
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
    "新しいイベント開始日：",
    yes_no(
        latest[
            "New_BB_Lower_Event"
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
        f"{int(latest['Days_From_BB_Event_Start'])}営業日目",
    )


if bool(
    latest[
        "Fixed_Event_Window"
    ]
):

    st.write(
        "イベント観察状態：",
        latest[
            "Event_Observation_Status"
        ],
    )


st.write(
    "固定期間内の下落停止候補：",
    yes_no(
        latest[
            "Fixed_Window_Decline_Stop_Candidate"
        ]
    ),
)

st.write(
    "イベント最初の下落停止確認：",
    yes_no(
        latest[
            "First_Decline_Stop_In_Event"
        ]
    ),
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
# ⑬ 正規化BandWidth
# ============================================================

st.subheader(
    "⑬ 正規化BandWidth"
)

normalized_chart = (
    valid_df[
        ["Normalized_BandWidth"]
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
            "BandWidth",
            "Normalized_BandWidth",
            "Lower_Band_Event",
            "Higher_Low",
            "Close_Up",
            "Bullish_Candle",
            "BB_Event_ID",
            "Days_From_BB_Event_Start",
            "Event_Observation_Status",
            "First_Decline_Stop_In_Event",
        ]
    ]
    .tail(30)
    .copy()
)

display_df[
    "Normalized_BandWidth"
] *= 100

display_df = display_df.rename(
    columns={
        "Close": "終値",
        "Low": "安値",
        "BB_Lower": "BB下限",
        "BandWidth": "BandWidth %",
        "Normalized_BandWidth": "正規化BW %",
        "Lower_Band_Event": "BB下限状態",
        "Higher_Low": "安値切上",
        "Close_Up": "終値上昇",
        "Bullish_Candle": "陽線",
        "BB_Event_ID": "イベントID",
        "Days_From_BB_Event_Start": "開始から営業日",
        "Event_Observation_Status": "観察状態",
        "First_Decline_Stop_In_Event": "最初確認",
    }
)

st.dataframe(
    display_df.round(2),
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

    total_count = len(
        research_df
    )

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


    col1, col2, col3 = st.columns(3)

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


    col4, col5, col6 = st.columns(3)

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


# ============================================================
# ⑯ v1.3 従来集計
# ============================================================

st.subheader(
    "⑯ v1.3 下落停止条件の発生件数"
)

if not research_df.empty:

    st.write(
        "前日安値を割らない：",
        f"{int(research_df['No_Lower_Low'].sum())}日",
    )

    st.write(
        "安値切り上げ：",
        f"{int(research_df['Higher_Low'].sum())}日",
    )

    st.write(
        "前日終値より上昇：",
        f"{int(research_df['Close_Up'].sum())}日",
    )

    st.write(
        "陽線：",
        f"{int(research_df['Bullish_Candle'].sum())}日",
    )

    st.write(
        "安値切上＋終値上昇：",
        f"{int(research_df['Decline_Stop_Combo'].sum())}日",
    )

    st.write(
        "v1.3 下落停止候補日：",
        f"{int(research_df['Decline_Stop_Candidate'].sum())}日",
    )


# ============================================================
# ⑰ v1.3.3
# 観察完了・未完了イベント集計
# ============================================================

st.subheader(
    "⑰ v1.3.3 観察完了・未完了イベント集計"
)


# イベント開始行
event_start_df = valid_df[
    valid_df[
        "New_BB_Lower_Event"
    ]
].copy()


# 全イベント
all_event_count = len(
    event_start_df
)


# 観察完了イベント
completed_event_start_df = (
    event_start_df[
        event_start_df[
            "Event_Observation_Complete"
        ]
    ]
    .copy()
)


# 観察未完了イベント
incomplete_event_start_df = (
    event_start_df[
        ~event_start_df[
            "Event_Observation_Complete"
        ]
    ]
    .copy()
)


completed_event_count = len(
    completed_event_start_df
)

incomplete_event_count = len(
    incomplete_event_start_df
)


# 観察完了イベントID
completed_event_ids = set(
    completed_event_start_df[
        "BB_Event_ID"
    ]
    .dropna()
    .astype(int)
    .tolist()
)


# 完了イベントの最初の下落停止確認
completed_first_stop_df = (
    valid_df[
        valid_df[
            "First_Decline_Stop_In_Event"
        ]
        & valid_df[
            "BB_Event_ID"
        ]
        .fillna(-1)
        .astype(int)
        .isin(
            completed_event_ids
        )
    ]
    .copy()
)


completed_confirmed_count = len(
    completed_first_stop_df
)

completed_unconfirmed_count = max(
    0,
    completed_event_count
    - completed_confirmed_count,
)


if completed_event_count > 0:

    confirmation_rate = (
        completed_confirmed_count
        / completed_event_count
        * 100
    )

else:

    confirmation_rate = np.nan


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


col4, col5, col6 = st.columns(3)


with col4:

    st.metric(
        "完了イベント・下落停止確認",
        f"{completed_confirmed_count}回",
    )


with col5:

    st.metric(
        "完了イベント・下落停止未確認",
        f"{completed_unconfirmed_count}回",
    )


with col6:

    if pd.isna(
        confirmation_rate
    ):

        rate_text = "計算不可"

    else:

        rate_text = (
            f"{confirmation_rate:.1f}%"
        )

    st.metric(
        "下落停止確認率",
        rate_text,
    )


st.caption(
    "確認率は利益率・勝率ではありません。"
    "BB下限タッチから0～3営業日目までに、"
    "研究中の『安値切り上げ＋前日終値より上昇』"
    "が確認された割合です。"
)


# ============================================================
# ⑱ 完了イベントの候補日重複
# ============================================================

st.subheader(
    "⑱ 観察完了イベントの候補日集計"
)


completed_window_df = (
    valid_df[
        valid_df[
            "BB_Event_ID"
        ]
        .fillna(-1)
        .astype(int)
        .isin(
            completed_event_ids
        )
    ]
    .copy()
)


completed_candidate_count = int(
    completed_window_df[
        "Fixed_Window_Decline_Stop_Candidate"
    ].sum()
)


completed_duplicate_count = max(
    0,
    completed_candidate_count
    - completed_confirmed_count,
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "完了イベント内の候補日数",
        f"{completed_candidate_count}日",
    )


with col2:

    st.metric(
        "イベント内の重複候補日",
        f"{completed_duplicate_count}日",
    )


# ============================================================
# ⑲ 完了イベントの確認タイミング
# ============================================================

st.subheader(
    "⑲ 下落停止を何営業日目に確認したか"
)


if completed_first_stop_df.empty:

    st.info(
        "観察完了イベント内に"
        "下落停止確認がありません。"
    )

else:

    day_0_count = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 0
        ).sum()
    )

    day_1_count = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 1
        ).sum()
    )

    day_2_count = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 2
        ).sum()
    )

    day_3_count = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 3
        ).sum()
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric(
            "0日目",
            f"{day_0_count}回",
        )

    with col2:
        st.metric(
            "1営業日目",
            f"{day_1_count}回",
        )

    with col3:
        st.metric(
            "2営業日目",
            f"{day_2_count}回",
        )

    with col4:
        st.metric(
            "3営業日目",
            f"{day_3_count}回",
        )


# ============================================================
# ⑳ 完了イベント確認時のBB状態
# ============================================================

st.subheader(
    "⑳ 下落停止確認時のBB状態"
)


if completed_first_stop_df.empty:

    st.info(
        "集計対象がありません。"
    )

else:

    below_count = int(
        (
            completed_first_stop_df[
                "First_Stop_BB_State"
            ]
            == "BB下限より下で終値"
        ).sum()
    )

    reclaim_count = int(
        (
            completed_first_stop_df[
                "First_Stop_BB_State"
            ]
            == "下抜け後BB内復帰"
        ).sum()
    )

    inside_count = int(
        (
            completed_first_stop_df[
                "First_Stop_BB_State"
            ]
            == "終値はBB内"
        ).sum()
    )


    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric(
            "BB下限より下で終値",
            f"{below_count}回",
        )

    with col2:
        st.metric(
            "下抜け後BB内復帰",
            f"{reclaim_count}回",
        )

    with col3:
        st.metric(
            "終値はBB内",
            f"{inside_count}回",
        )


# ============================================================
# ㉑ 観察完了イベント一覧
# ============================================================

st.subheader(
    "㉑ 観察完了BB下限イベント一覧"
)


if completed_event_start_df.empty:

    st.info(
        "観察完了イベントがありません。"
    )

else:

    completed_display = (
        completed_event_start_df[
            [
                "BB_Event_ID",
                "Close",
                "Low",
                "BB_Lower",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
                "Event_End_Date",
                "Event_Has_Decline_Stop",
            ]
        ]
        .tail(50)
        .copy()
    )

    completed_display[
        "Normalized_BandWidth"
    ] *= 100

    completed_display = (
        completed_display.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "Close":
                    "開始日終値",

                "Low":
                    "開始日安値",

                "BB_Lower":
                    "開始日BB下限",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "Squeeze_State":
                    "BW環境",

                "Event_End_Date":
                    "観察終了日",

                "Event_Has_Decline_Stop":
                    "下落停止確認",
            }
        )
    )

    st.dataframe(
        completed_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉒ 観察未完了イベント一覧
# ============================================================

st.subheader(
    "㉒ 観察未完了イベント一覧"
)


if incomplete_event_start_df.empty:

    st.success(
        "現在、観察未完了イベントはありません。"
    )

else:

    incomplete_display = (
        incomplete_event_start_df[
            [
                "BB_Event_ID",
                "Close",
                "Low",
                "BB_Lower",
                "BandWidth",
                "Normalized_BandWidth",
                "Squeeze_State",
            ]
        ]
        .copy()
    )

    incomplete_display[
        "Normalized_BandWidth"
    ] *= 100

    incomplete_display = (
        incomplete_display.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "Close":
                    "開始日終値",

                "Low":
                    "開始日安値",

                "BB_Lower":
                    "開始日BB下限",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "Squeeze_State":
                    "BW環境",
            }
        )
    )

    st.dataframe(
        incomplete_display.round(2),
        use_container_width=True,
    )

    st.warning(
        "このイベントは0～3営業日目を"
        "最後まで観察できていないため、"
        "下落停止確認率の母数から除外しています。"
    )


# ============================================================
# ㉓ 完了イベント最初の下落停止確認一覧
# ============================================================

st.subheader(
    "㉓ 観察完了イベント・最初の下落停止確認一覧"
)


if completed_first_stop_df.empty:

    st.info(
        "対象データがありません。"
    )

else:

    first_display = (
        completed_first_stop_df[
            [
                "BB_Event_ID",
                "BB_Event_Start_Date",
                "Days_From_BB_Event_Start",
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

    first_display[
        "Normalized_BandWidth"
    ] *= 100

    first_display = first_display.rename(
        columns={
            "BB_Event_ID":
                "イベントID",

            "BB_Event_Start_Date":
                "イベント開始日",

            "Days_From_BB_Event_Start":
                "確認営業日",

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

    st.dataframe(
        first_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉔ 完了イベントの下落停止未確認一覧
# ============================================================

st.subheader(
    "㉔ 観察完了・下落停止未確認イベント一覧"
)


confirmed_event_ids = set(
    completed_first_stop_df[
        "BB_Event_ID"
    ]
    .dropna()
    .astype(int)
    .tolist()
)


completed_unconfirmed_df = (
    completed_event_start_df[
        ~completed_event_start_df[
            "BB_Event_ID"
        ]
        .astype(int)
        .isin(
            confirmed_event_ids
        )
    ]
    .copy()
)


if completed_unconfirmed_df.empty:

    st.info(
        "観察完了イベントの中に"
        "下落停止未確認イベントはありません。"
    )

else:

    unconfirmed_display = (
        completed_unconfirmed_df[
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
                "Event_End_Date",
            ]
        ]
        .copy()
    )

    unconfirmed_display[
        "Normalized_BandWidth"
    ] *= 100

    unconfirmed_display = (
        unconfirmed_display.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "Close":
                    "開始日終値",

                "Low":
                    "開始日安値",

                "BB_Lower":
                    "開始日BB下限",

                "BB_Lower_Reclaim":
                    "開始日BB内復帰",

                "BB_Lower_Close_Below":
                    "開始日BB下終値",

                "BandWidth":
                    "BandWidth %",

                "Normalized_BandWidth":
                    "正規化BW %",

                "Squeeze_State":
                    "BW環境",

                "Downside_Expansion_State":
                    "下方向拡大状態",

                "Event_End_Date":
                    "観察終了日",
            }
        )
    )

    st.dataframe(
        unconfirmed_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉕ 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "㉕ 現在の研究段階"
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
    "【v1.2 実装済み】BB下限タッチ・下抜け・BB内復帰"
)

st.write(
    "【v1.3 実装済み】安値切り上げ・終値上昇・陽線"
)

st.write(
    "【検証中】安値切り上げ＋終値上昇＝下落停止候補"
)

st.write(
    "【v1.3.2 正常動作確認済み】0～3営業日固定観察"
)

st.write(
    "【v1.3.2 正常動作確認済み】再タッチによる期間延長なし"
)

st.write(
    "【v1.3.3 実装】観察完了・未完了イベント分離"
)

st.write(
    "【v1.3.3 実装】完了イベントだけで確認率を計算"
)

st.write(
    "【未検証】下落停止確認に利益上の優位性があるか"
)

st.write(
    "【未実装】反発開始候補"
)

st.write(
    "【未実装】1R損切り"
)

st.write(
    "【未実装】1.5R / 2R到達検証"
)

st.write(
    "【未実装】次営業日エントリーによるイベントバックテスト"
)


# ============================================================
# 最終説明
# ============================================================

st.divider()

st.warning(
    "重要：下落停止確認率は勝率ではありません。"
    "現在調べているのは、BB下限タッチ後の"
    "0～3営業日目に『安値切り上げ＋終値上昇』"
    "が確認されたかどうかだけです。"
)

st.info(
    "将来バックテストするときは、"
    "その日の終値を使って下落停止を確認した場合、"
    "同じ日の終値で買ったことにはしません。"
    "原則として次営業日以降の価格を使い、"
    "未来情報を使った成績の水増しを防ぎます。"
)

st.caption(
    "このプログラムは研究・検証用です。"
    "表示された状態は将来の株価上昇・下落を"
    "保証するものではありません。"
)
