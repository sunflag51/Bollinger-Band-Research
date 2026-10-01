# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.5.2
#
# v1.4まで
# ・BB下限イベント
# ・0～3営業日の固定観察
# ・下落停止候補
# ・反発開始候補
# ・観察完了 / 未完了分離
#
# v1.5
# ・シグナル確認日の次営業日始値を仮Entry
# ・イベント開始～シグナル確認日の最安値を仮Stop
# ・1R / 1.5R / 2R価格を計算
# ・下落停止 / 反発開始を別々にR設計
# ・R計算不可ケースを分離
#
# v1.5.1
# ・1R率 = 1R / Entry × 100 を追加
# ・下落停止 / 反発開始それぞれの1R率を診断
# ・最小 / 中央値 / 平均 / 最大を表示
# ・1R率の分布を研究用区分で表示
# ・1R率による除外はまだ行わない
#
# v1.5.2
# ・㉚ / ㉛ の1R率診断にコピー用テキストを追加
# ・Streamlit標準のコピーアイコンから診断結果を一括コピー可能
# ・研究計算・イベント判定・R設計はv1.5.1から変更しない
#
# 重要
# v1.5.2でも「R幅の診断」まで。
# -1R / +1.5R / +2R の到達判定、勝率、期待値、
# 売買判断はまだ行わない。
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# ============================================================
# Streamlit
# ============================================================

st.set_page_config(
    page_title="GOOG・NVDA BB研究",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# 定数
# ============================================================

APP_VERSION = "1.5.2"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125
LOW_BANDWIDTH_ZONE = 0.20

# 最初のBB下限タッチを0日目
# 0・1・2・3営業日目を固定観察
LOWER_EVENT_OBSERVATION_DAYS = 3


# ============================================================
# 株価データ
# ============================================================

@st.cache_data(ttl=3600)
def get_stock_data(ticker: str, period: str) -> pd.DataFrame:

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


def classify_bandwidth_direction(row) -> str:

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


def classify_squeeze_state(row) -> str:

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


def classify_lower_band_event(row) -> str:

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


def classify_downside_expansion(row) -> str:

    if bool(row["Downside_Expansion_Close_Below"]):
        return "低BW→下方向拡大・BB下で終値"

    if bool(row["Downside_Expansion_Reclaim"]):
        return "低BW→下方向拡大・BB内復帰"

    if bool(row["Downside_Expansion_Candidate"]):
        return "低BW→下方向拡大候補"

    return "該当なし"


# ============================================================
# 下落停止条件
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

    df["Decline_Stop_Combo"] = (
        df["Higher_Low"]
        & df["Close_Up"]
    )

    return df


# ============================================================
# 反発開始条件
# ============================================================

def calculate_rebound_start_conditions(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Prev_High"] = df["High"].shift(1)

    df["Close_Above_Prev_High"] = (
        df["Prev_High"].notna()
        & (df["Close"] > df["Prev_High"])
    )

    return df


# ============================================================
# v1.3互換・直近タッチ追跡
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


def classify_decline_stop(row) -> str:

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
# 固定BB下限イベント
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

    df[
        "Fixed_Window_Decline_Stop_Candidate"
    ] = (
        df["Fixed_Event_Window"]
        & df["Decline_Stop_Combo"]
    )

    df[
        "Fixed_Window_Rebound_Start_Candidate"
    ] = (
        df["Fixed_Event_Window"]
        & df["Close_Above_Prev_High"]
    )

    return df


# ============================================================
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
# イベント最初のシグナル
# ============================================================

def calculate_first_signal_per_event(
    data: pd.DataFrame,
    candidate_column: str,
    output_column: str,
) -> pd.DataFrame:

    df = data.copy()

    flags = [False] * len(df)
    seen_event_ids = set()

    for position in range(len(df)):

        event_id = (
            df.iloc[position][
                "BB_Event_ID"
            ]
        )

        candidate = bool(
            df.iloc[position][
                candidate_column
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

    df[output_column] = flags

    return df


def calculate_first_decline_stop_per_event(
    data: pd.DataFrame,
) -> pd.DataFrame:

    return calculate_first_signal_per_event(
        data,
        "Fixed_Window_Decline_Stop_Candidate",
        "First_Decline_Stop_In_Event",
    )


def calculate_first_rebound_start_per_event(
    data: pd.DataFrame,
) -> pd.DataFrame:

    return calculate_first_signal_per_event(
        data,
        "Fixed_Window_Rebound_Start_Candidate",
        "First_Rebound_Start_In_Event",
    )


# ============================================================
# 最初のシグナル確認時BB状態
# ============================================================

def calculate_first_signal_bb_state(
    data: pd.DataFrame,
    signal_column: str,
    output_column: str,
) -> pd.DataFrame:

    df = data.copy()

    states = []

    for position in range(len(df)):

        row = df.iloc[position]

        if not bool(
            row[signal_column]
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

    df[output_column] = states

    return df


def calculate_first_stop_bb_state(
    data: pd.DataFrame,
) -> pd.DataFrame:

    return calculate_first_signal_bb_state(
        data,
        "First_Decline_Stop_In_Event",
        "First_Stop_BB_State",
    )


def calculate_first_rebound_bb_state(
    data: pd.DataFrame,
) -> pd.DataFrame:

    return calculate_first_signal_bb_state(
        data,
        "First_Rebound_Start_In_Event",
        "First_Rebound_BB_State",
    )


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
# v1.5
# R設計
#
# シグナル確認日は終値確定後にしか分からない。
# そのため同日終値では買わず、
# 次の株価データ行の始値を仮Entryとする。
#
# 仮Stop:
# BBイベント開始日からシグナル確認日までの
# Lowの最小値。
#
# 未来の安値は使わない。
# ============================================================

def calculate_r_design(
    data: pd.DataFrame,
    signal_column: str,
    prefix: str,
) -> pd.DataFrame:

    df = data.copy()

    signal_date_col = (
        f"{prefix}_Signal_Date"
    )

    entry_date_col = (
        f"{prefix}_Entry_Date"
    )

    entry_price_col = (
        f"{prefix}_Entry_Price"
    )

    stop_price_col = (
        f"{prefix}_Stop_Price"
    )

    risk_col = (
        f"{prefix}_Risk_1R"
    )

    risk_percent_col = (
        f"{prefix}_Risk_1R_Percent"
    )

    target_15_col = (
        f"{prefix}_Target_1_5R"
    )

    target_20_col = (
        f"{prefix}_Target_2R"
    )

    valid_col = (
        f"{prefix}_R_Valid"
    )

    status_col = (
        f"{prefix}_R_Status"
    )

    df[signal_date_col] = pd.NaT
    df[entry_date_col] = pd.NaT

    df[entry_price_col] = np.nan
    df[stop_price_col] = np.nan
    df[risk_col] = np.nan
    df[risk_percent_col] = np.nan
    df[target_15_col] = np.nan
    df[target_20_col] = np.nan

    df[valid_col] = False
    df[status_col] = "対象外"

    signal_positions = np.where(
        df[
            signal_column
        ].to_numpy(dtype=bool)
    )[0]

    for position in signal_positions:

        event_id = (
            df.iloc[position][
                "BB_Event_ID"
            ]
        )

        signal_date = (
            df.index[position]
        )

        df.at[
            signal_date,
            signal_date_col,
        ] = signal_date

        if pd.isna(event_id):

            df.at[
                signal_date,
                status_col,
            ] = "イベントIDなし"

            continue

        event_id_int = int(
            event_id
        )

        # イベント開始～シグナル確認日だけを使用
        stop_mask = (
            (df["BB_Event_ID"] == event_id_int)
            & (df.index <= signal_date)
        )

        stop_price = (
            df.loc[
                stop_mask,
                "Low",
            ]
            .min()
        )

        df.at[
            signal_date,
            stop_price_col,
        ] = stop_price

        # 次営業日データ
        next_position = (
            position + 1
        )

        if next_position >= len(df):

            df.at[
                signal_date,
                status_col,
            ] = "翌営業日データなし"

            continue

        entry_date = (
            df.index[
                next_position
            ]
        )

        entry_price = (
            df.iloc[
                next_position
            ][
                "Open"
            ]
        )

        df.at[
            signal_date,
            entry_date_col,
        ] = entry_date

        df.at[
            signal_date,
            entry_price_col,
        ] = entry_price

        if (
            pd.isna(stop_price)
            or pd.isna(entry_price)
        ):

            df.at[
                signal_date,
                status_col,
            ] = "価格データ不足"

            continue

        risk_1r = (
            float(entry_price)
            - float(stop_price)
        )

        # ギャップダウン等でEntryがStop以下なら
        # 現在のR定義では有効なロング設計にならない
        if risk_1r <= 0:

            df.at[
                signal_date,
                status_col,
            ] = "R計算不可（Entry≦Stop）"

            continue

        risk_1r_percent = (
            risk_1r
            / float(entry_price)
            * 100
        )

        target_15 = (
            float(entry_price)
            + 1.5 * risk_1r
        )

        target_20 = (
            float(entry_price)
            + 2.0 * risk_1r
        )

        df.at[
            signal_date,
            risk_col,
        ] = risk_1r

        df.at[
            signal_date,
            risk_percent_col,
        ] = risk_1r_percent

        df.at[
            signal_date,
            target_15_col,
        ] = target_15

        df.at[
            signal_date,
            target_20_col,
        ] = target_20

        df.at[
            signal_date,
            valid_col,
        ] = True

        df.at[
            signal_date,
            status_col,
        ] = "R計算可能"

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

    df = calculate_rebound_start_conditions(
        df
    )

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

    df = calculate_fixed_bb_event_units(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    df = calculate_event_completion(
        df,
        LOWER_EVENT_OBSERVATION_DAYS,
    )

    df = calculate_first_decline_stop_per_event(
        df
    )

    df = calculate_first_rebound_start_per_event(
        df
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

    # v1.5
    df = calculate_r_design(
        df,
        "First_Decline_Stop_In_Event",
        "Stop",
    )

    df = calculate_r_design(
        df,
        "First_Rebound_Start_In_Event",
        "Rebound",
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


def yes_no(value) -> str:

    return (
        "はい"
        if bool(value)
        else "いいえ"
    )


def format_event_id(value) -> str:

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
    "下落停止 vs 反発開始 ＋ 1R率診断版"
)

st.info(
    "v1.5.2ではv1.5.1の研究計算をそのまま維持し、"
    "㉚・㉛の1R率診断にコピー用表示を追加します。"
    "極端に小さい1Rがどの程度あるかを確認する段階で、"
    "1R率による除外条件はまだ設定しません。"
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
    "v1.5では、-1R・+1.5R・+2Rの"
    "どれに先に到達したかはまだ判定しません。"
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
# ㉜ 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "㉜ 現在の研究段階"
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
    "【v1.5 実装】シグナル確認後の次営業日始値＝仮Entry"
)

st.write(
    "【v1.5 検証中】イベント開始～確認日の最安値＝仮Stop"
)

st.write(
    "【正常動作確認済み】v1.5 1R / 1.5R / 2R価格計算"
)

st.write(
    "【v1.5.1 実装】1R率 ＝ 1R ÷ Entry × 100"
)

st.write(
    "【v1.5.1 診断】1R率の最小・中央値・平均・最大・分布"
)

st.write(
    "【v1.5.2 実装】㉚・㉛の診断結果を一括コピー"
)

st.write(
    "【未採用】1R率による除外条件"
)

st.write(
    "【未検証】このR設計に利益上の優位性があるか"
)

st.write(
    "【未実装】-1R / +1.5R / +2R の先着判定"
)

st.write(
    "【未実装】同一日のStop・Target両方到達時の処理"
)

st.write(
    "【未実装】最大保有期間"
)

st.write(
    "【未実装】コスト・スリッページ"
)

st.write(
    "【未実装】イベント単位Rバックテスト"
)


# ============================================================
# 最終説明
# ============================================================

st.divider()

st.warning(
    "重要：v1.5.2で表示する1R率は『診断値』です。"
    "1R・1.5R・2Rも引き続き『価格設計』です。"
    "勝率や期待値ではありません。"
)

st.info(
    "シグナルは当日の終値確定後に判定するため、"
    "仮Entryには次営業日の始値を使用します。"
    "仮Stopはシグナル確認時点までに分かっている"
    "安値だけを使用し、未来の安値は使いません。"
)

st.info(
    "v1.5.2でも1R率が小さいイベントは削除しません。"
    "まずGOOG / NVDAそれぞれの分布を確認してから、"
    "除外条件が必要かを判断します。"
)

st.caption(
    "このプログラムは研究・検証用です。"
    "売買シグナルとして正式採用したものではありません。"
)
