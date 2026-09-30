# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.4
#
# v1.1
# ・125営業日 BandWidth 正規化
# ・Squeeze / BandWidth環境分類
#
# v1.2
# ・BB下限タッチ
# ・日中BB下限下抜け
# ・BB内復帰
# ・BB下限より下で終値
# ・低BandWidthから下方向拡大候補
#
# v1.3
# ・安値切り上げ
# ・前日終値より上昇
# ・陽線
# ・下落停止候補
#
# v1.3.2
# ・最初のBB下限タッチを0日目
# ・0～3営業日目の固定観察
# ・再タッチでは期間を延長しない
#
# v1.3.3
# ・観察完了 / 未完了イベント分離
# ・完了イベントだけで統計
#
# v1.4
# ・前日高値を終値で上回る条件を追加
# ・反発開始候補を追加
# ・イベント最初の反発開始を記録
# ・下落停止と反発開始をイベント単位で比較
# ・反発開始タイミングを0～3営業日で集計
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

APP_VERSION = "1.4"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125
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
# BandWidth状態
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
# BandWidth方向分類
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
# Squeeze状態分類
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
# 下落停止条件
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

    # 研究中の下落停止候補
    df["Decline_Stop_Combo"] = (
        df["Higher_Low"]
        & df["Close_Up"]
    )

    return df


# ============================================================
# v1.4
# 反発開始条件
#
# 終値が前日の高値を上回ったか
#
# まだ研究候補であり、
# 売買条件として正式採用したわけではない
# ============================================================

def calculate_rebound_start_conditions(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Prev_High"] = (
        df["High"].shift(1)
    )

    df["Close_Above_Prev_High"] = (
        df["Prev_High"].notna()
        & (
            df["Close"]
            > df["Prev_High"]
        )
    )

    return df


# ============================================================
# v1.3 従来の直近タッチ追跡
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
# v1.3 従来の下落停止候補
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
# 固定観察イベント
# ============================================================

def calculate_fixed_bb_event_units(
    data: pd.DataFrame,
    observation_days: int = 3,
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
    event_start_position = None
    event_start_date = pd.NaT

    for position in range(
        row_count
    ):

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

        if (
            active_event_id is None
            and is_touch
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

        if (
            active_event_id is not None
            and event_start_position is not None
        ):

            event_ids[
                position
            ] = active_event_id

            event_start_dates[
                position
            ] = event_start_date

            days_from_event_start[
                position
            ] = (
                position
                - event_start_position
            )

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

    df["Fixed_Event_Window"] = (
        df["BB_Event_ID"].notna()
    )

    # v1.3 下落停止候補
    df[
        "Fixed_Window_Decline_Stop_Candidate"
    ] = (
        df["Fixed_Event_Window"]
        & df["Decline_Stop_Combo"]
    )

    # v1.4 反発開始候補
    df[
        "Fixed_Window_Rebound_Start_Candidate"
    ] = (
        df["Fixed_Event_Window"]
        & df["Close_Above_Prev_High"]
    )

    return df


# ============================================================
# v1.3.3
# 観察完了 / 未完了
# ============================================================

def calculate_event_completion(
    data: pd.DataFrame,
    observation_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    row_count = len(df)

    df[
        "Event_Observation_Complete"
    ] = False

    df[
        "Event_Observation_Status"
    ] = "イベント外"

    df["Event_End_Date"] = pd.NaT

    event_start_positions = np.where(
        df[
            "New_BB_Lower_Event"
        ].to_numpy(dtype=bool)
    )[0]

    for start_position in (
        event_start_positions
    ):

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

            end_date = (
                df.index[end_position]
            )

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
# イベント最初の下落停止確認
# ============================================================

def calculate_first_decline_stop_per_event(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    flags = [
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

        candidate = bool(
            df.iloc[position][
                "Fixed_Window_Decline_Stop_Candidate"
            ]
        )

        if (
            pd.notna(event_id)
            and candidate
        ):

            event_id_int = int(
                event_id
            )

            if (
                event_id_int
                not in seen_event_ids
            ):

                flags[position] = True

                seen_event_ids.add(
                    event_id_int
                )

    df[
        "First_Decline_Stop_In_Event"
    ] = flags

    return df


# ============================================================
# v1.4
# イベント最初の反発開始確認
# ============================================================

def calculate_first_rebound_start_per_event(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    flags = [
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

        candidate = bool(
            df.iloc[position][
                "Fixed_Window_Rebound_Start_Candidate"
            ]
        )

        if (
            pd.notna(event_id)
            and candidate
        ):

            event_id_int = int(
                event_id
            )

            if (
                event_id_int
                not in seen_event_ids
            ):

                flags[
                    position
                ] = True

                seen_event_ids.add(
                    event_id_int
                )

    df[
        "First_Rebound_Start_In_Event"
    ] = flags

    return df


# ============================================================
# 下落停止確認時のBB状態
# ============================================================

def calculate_first_stop_bb_state(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    states = []

    for position in range(
        len(df)
    ):

        row = df.iloc[
            position
        ]

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
# v1.4
# 反発開始確認時のBB状態
# ============================================================

def calculate_first_rebound_bb_state(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    states = []

    for position in range(
        len(df)
    ):

        row = df.iloc[
            position
        ]

        if not bool(
            row[
                "First_Rebound_Start_In_Event"
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
        "First_Rebound_BB_State"
    ] = states

    return df


# ============================================================
# イベント結果
# ============================================================

def calculate_event_results(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df[
        "Event_Has_Decline_Stop"
    ] = False

    df[
        "Event_Has_Rebound_Start"
    ] = False

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

        has_rebound = bool(
            df.loc[
                event_mask,
                "First_Rebound_Start_In_Event",
            ].any()
        )

        df.loc[
            event_mask,
            "Event_Has_Decline_Stop",
        ] = has_stop

        df.loc[
            event_mask,
            "Event_Has_Rebound_Start",
        ] = has_rebound

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

    # v1.3
    df = calculate_decline_stop_conditions(
        df
    )

    # v1.4
    df = calculate_rebound_start_conditions(
        df
    )

    # v1.3 従来追跡
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

    # 固定イベント
    df = calculate_fixed_bb_event_units(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    # 完了 / 未完了
    df = calculate_event_completion(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    # 最初の下落停止
    df = (
        calculate_first_decline_stop_per_event(
            df
        )
    )

    # 最初の反発開始
    df = (
        calculate_first_rebound_start_per_event(
            df
        )
    )

    df = calculate_first_stop_bb_state(
        df
    )

    df = calculate_first_rebound_bb_state(
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
    "下落停止 vs 反発開始 比較研究版"
)

st.info(
    "v1.4では、v1.3.3の固定観察方式を維持したまま、"
    "『終値が前日の高値を上回る』状態を"
    "反発開始候補として追加します。"
    "まだ売買条件ではありません。"
)


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
# ⑦ v1.4 反発開始候補
# ============================================================

st.subheader(
    "⑦ v1.4 反発開始候補"
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
        "v1.4の『反発開始候補』です。"
    )

else:

    st.write(
        "現在はv1.4の"
        "反発開始候補には該当していません。"
    )


st.caption(
    "『前日高値を終値で上回る』は研究候補です。"
    "買いシグナルとして正式採用したものではありません。"
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

display_df = display_df.rename(
    columns={
        "Close":
            "終値",

        "Low":
            "安値",

        "Prev_High":
            "前日高値",

        "BB_Lower":
            "BB下限",

        "Higher_Low":
            "安値切上",

        "Close_Up":
            "終値上昇",

        "Decline_Stop_Combo":
            "下落停止条件",

        "Close_Above_Prev_High":
            "前日高値超え",

        "BB_Event_ID":
            "イベントID",

        "Days_From_BB_Event_Start":
            "開始から営業日",

        "Event_Observation_Status":
            "観察状態",

        "First_Decline_Stop_In_Event":
            "最初の下落停止",

        "First_Rebound_Start_In_Event":
            "最初の反発開始",
    }
)

st.dataframe(
    display_df.round(2),
    use_container_width=True,
)


# ============================================================
# ⑫ 観察完了イベント準備
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
# ⑫ v1.3.3 基準集計
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


col4, col5, col6 = st.columns(3)

with col4:

    st.metric(
        "下落停止確認",
        f"{stop_count}回",
    )

with col5:

    st.metric(
        "下落停止未確認",
        f"{stop_no_count}回",
    )

with col6:

    st.metric(
        "下落停止確認率",
        (
            "計算不可"
            if pd.isna(stop_rate)
            else f"{stop_rate:.1f}%"
        ),
    )


# ============================================================
# ⑬ v1.4 反発開始集計
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


col4, col5 = st.columns(2)

with col4:

    st.metric(
        "反発開始候補日数",
        f"{rebound_candidate_days}日",
    )

with col5:

    st.metric(
        "イベント内の重複候補日",
        f"{rebound_duplicate_days}日",
    )


st.caption(
    "反発開始確認率は勝率ではありません。"
    "BB下限イベントの0～3営業日目に"
    "終値が前日高値を上回ったイベントの割合です。"
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


    col1, col2, col3, col4 = (
        st.columns(4)
    )


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
# ⑮ 反発開始のタイミング
# ============================================================

st.subheader(
    "⑮ 反発開始を何営業日目に確認したか"
)


if completed_first_rebound_df.empty:

    st.info(
        "反発開始確認イベントがありません。"
    )

else:

    rebound_day_0 = int(
        (
            completed_first_rebound_df[
                "Days_From_BB_Event_Start"
            ]
            == 0
        ).sum()
    )

    rebound_day_1 = int(
        (
            completed_first_rebound_df[
                "Days_From_BB_Event_Start"
            ]
            == 1
        ).sum()
    )

    rebound_day_2 = int(
        (
            completed_first_rebound_df[
                "Days_From_BB_Event_Start"
            ]
            == 2
        ).sum()
    )

    rebound_day_3 = int(
        (
            completed_first_rebound_df[
                "Days_From_BB_Event_Start"
            ]
            == 3
        ).sum()
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "0日目",
            f"{rebound_day_0}回",
        )


    with col2:

        st.metric(
            "1営業日目",
            f"{rebound_day_1}回",
        )


    with col3:

        st.metric(
            "2営業日目",
            f"{rebound_day_2}回",
        )


    with col4:

        st.metric(
            "3営業日目",
            f"{rebound_day_3}回",
        )


# ============================================================
# ⑯ 両方確認された場合の順序
# ============================================================

st.subheader(
    "⑯ 下落停止と反発開始の確認順序"
)


if comparison_df.empty:

    st.info(
        "比較データがありません。"
    )

else:

    rebound_after_count = int(
        (
            comparison_df[
                "関係"
            ]
            == "反発開始が後"
        ).sum()
    )

    same_day_count = int(
        (
            comparison_df[
                "関係"
            ]
            == "同日"
        ).sum()
    )

    rebound_before_count = int(
        (
            comparison_df[
                "関係"
            ]
            == "反発開始が先"
        ).sum()
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "反発開始が後",
            f"{rebound_after_count}回",
        )


    with col2:

        st.metric(
            "同日",
            f"{same_day_count}回",
        )


    with col3:

        st.metric(
            "反発開始が先",
            f"{rebound_before_count}回",
        )


st.caption(
    "『反発開始が先』もエラーではありません。"
    "現在の2条件は独立した研究条件なので、"
    "前日高値超えが先に成立するケースも記録します。"
)


# ============================================================
# ⑰ 下落停止確認タイミング
# ============================================================

st.subheader(
    "⑰ 下落停止を何営業日目に確認したか"
)


if completed_first_stop_df.empty:

    st.info(
        "下落停止確認イベントがありません。"
    )

else:

    stop_day_0 = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 0
        ).sum()
    )

    stop_day_1 = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 1
        ).sum()
    )

    stop_day_2 = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 2
        ).sum()
    )

    stop_day_3 = int(
        (
            completed_first_stop_df[
                "Days_From_BB_Event_Start"
            ]
            == 3
        ).sum()
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "0日目",
            f"{stop_day_0}回",
        )


    with col2:

        st.metric(
            "1営業日目",
            f"{stop_day_1}回",
        )


    with col3:

        st.metric(
            "2営業日目",
            f"{stop_day_2}回",
        )


    with col4:

        st.metric(
            "3営業日目",
            f"{stop_day_3}回",
        )


# ============================================================
# ⑱ 反発開始確認時のBB状態
# ============================================================

st.subheader(
    "⑱ 反発開始確認時のBB状態"
)


if completed_first_rebound_df.empty:

    st.info(
        "対象データがありません。"
    )

else:

    rebound_below_count = int(
        (
            completed_first_rebound_df[
                "First_Rebound_BB_State"
            ]
            == "BB下限より下で終値"
        ).sum()
    )

    rebound_reclaim_count = int(
        (
            completed_first_rebound_df[
                "First_Rebound_BB_State"
            ]
            == "下抜け後BB内復帰"
        ).sum()
    )

    rebound_inside_count = int(
        (
            completed_first_rebound_df[
                "First_Rebound_BB_State"
            ]
            == "終値はBB内"
        ).sum()
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "BB下限より下で終値",
            f"{rebound_below_count}回",
        )


    with col2:

        st.metric(
            "下抜け後BB内復帰",
            f"{rebound_reclaim_count}回",
        )


    with col3:

        st.metric(
            "終値はBB内",
            f"{rebound_inside_count}回",
        )


# ============================================================
# ⑲ イベント比較一覧
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
# ⑳ 反発開始確認日の詳細
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


    rebound_display = (
        rebound_display.rename(
            columns={
                "BB_Event_ID":
                    "イベントID",

                "BB_Event_Start_Date":
                    "イベント開始日",

                "Days_From_BB_Event_Start":
                    "確認営業日",

                "Open":
                    "始値",

                "High":
                    "高値",

                "Low":
                    "安値",

                "Close":
                    "終値",

                "Prev_High":
                    "前日高値",

                "BB_Lower":
                    "BB下限",

                "Close_Above_Prev_High":
                    "前日高値超え",

                "Higher_Low":
                    "安値切上",

                "Close_Up":
                    "終値上昇",

                "Decline_Stop_Combo":
                    "下落停止条件",

                "BB_Lower_Reclaim":
                    "BB内復帰",

                "First_Rebound_BB_State":
                    "反発確認時BB状態",

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
        rebound_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉑ 観察完了・下落停止未確認
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
# ㉒ 観察完了・反発開始未確認
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

    rebound_unconfirmed_display = (
        rebound_unconfirmed_display.rename(
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
            }
        )
    )

    st.dataframe(
        rebound_unconfirmed_display.round(2),
        use_container_width=True,
    )


# ============================================================
# ㉓ 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "㉓ 現在の研究段階"
)

st.write(
    "【実装済み】GOOG / NVDA 切り替え"
)

st.write(
    "【実装済み】20日・2標準偏差BB"
)

st.write(
    "【実装済み】BandWidth・125営業日正規化"
)

st.write(
    "【研究分類】低BandWidthゾーン"
)

st.write(
    "【実装済み】BB下限タッチ・下抜け・BB内復帰"
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
    "【v1.4 検証中】終値が前日高値を上回る＝反発開始候補"
)

st.write(
    "【v1.4 実装】下落停止と反発開始をイベント単位で比較"
)

st.write(
    "【未検証】反発開始まで待つことに利益上の優位性があるか"
)

st.write(
    "【未実装】1R損切り"
)

st.write(
    "【未実装】1.5R / 2R到達検証"
)

st.write(
    "【未実装】次営業日エントリー"
)

st.write(
    "【未実装】イベント単位Rバックテスト"
)


# ============================================================
# 最終説明
# ============================================================

st.divider()

st.warning(
    "重要：下落停止確認率や反発開始確認率は"
    "勝率ではありません。"
    "現在はBB下限イベント後に各価格条件が"
    "何回成立したかを調べている段階です。"
)

st.info(
    "今後のRバックテストでは、"
    "その日の終値を使って条件成立を確認した場合、"
    "同じ日の終値で買ったことにはしません。"
    "原則として次営業日の価格から検証し、"
    "未来情報の混入を防ぎます。"
)

st.caption(
    "このプログラムは研究・検証用です。"
    "反発開始候補は買いシグナルとして"
    "正式採用したものではありません。"
)
