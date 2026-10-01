# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.9
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
#
# v1.6
# ・R計算可能イベントについてEntry後の先着判定を追加
# ・-1R Stop vs +1.5R Target を判定
# ・-1R Stop vs +2R Target を判定
# ・Entry日を1営業日目として 5 / 10 / 20営業日を比較
# ・同一日にStopとTargetへ到達した場合は「順序不明」として分離
# ・期間末で必要日数が足りない未決着イベントは「将来データ不足」として分離
# ・1R率による除外は行わない
#
# v1.7
# ・v1.6の先着判定を維持
# ・Target先着 = +Target R、Stop先着 = -1R としてR損益化
# ・期間内未到達は5 / 10 / 20営業日目の終値で期間末決済
# ・期間末決済R = (期間末終値 - Entry) / 1R
# ・同日両方到達・順序不明はR損益から除外して別枠維持
# ・将来データ不足もR損益から除外して別枠維持
# ・全件と「1R率1%以上」の参考診断を並べる
# ・1R率1%以上は正式フィルターではない
#
# v1.8
# ・下落停止と反発開始の「同じBB下限イベント」だけを1対1で比較
# ・同じTarget・同じ保有期間で、両方式のR損益差を計算
# ・差 = 反発開始R - 下落停止R
# ・反発開始が高い / 下落停止が高い / 同じ / 比較不可を集計
# ・ペア内のStop側1R率が最小の1イベントを特定し、影響を参考診断
# ・最小1Rイベント除外は正式フィルターではない
#
# v1.9
# ・意思決定の起点を「下落停止シグナル確認時点」に固定
# ・方針A = 下落停止確認後、次営業日始値でEntry
# ・方針B = 下落停止確認後から固定イベント終了まで反発開始を待つ
# ・方針Bは反発開始を確認できた場合だけ次営業日始値でEntry
# ・反発開始を確認できなければ「見送り = 0R機会」として残す
# ・反発開始が下落停止より前に出ただけのケースは、方針Bの確認には使わない
# ・方針Bの待ち日数、Entry件数、見送り件数、機会平均Rを表示
# ・将来「両方出たイベント」だけを後から選ぶペア比較の選別問題を避ける
#
# 重要
# v1.9も「コスト前のルールベースR損益・意思決定比較」まで。
# 手数料・スリッページ・ギャップ時の実約定差はまだ含めない。
# 正式な売買ルールはまだ確定しない。
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

APP_VERSION = "1.9"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125
LOW_BANDWIDTH_ZONE = 0.20

# 最初のBB下限タッチを0日目
# 0・1・2・3営業日目を固定観察
LOWER_EVENT_OBSERVATION_DAYS = 3

# v1.6
# Entry日を1営業日目として比較する研究用保有期間
FIRST_HIT_HORIZONS = [5, 10, 20]


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
# v1.6
# R先着判定
#
# Entry日を1営業日目として、指定営業日数の範囲で
# Stop(-1R) と Target(+1.5R / +2R) のどちらへ
# 先に到達したかを日足OHLCで判定する。
#
# 同一日のOpenがどちらかの水準を既に超えている場合は、
# 寄り付きで到達した側を先着とする。
# OpenがStopとTargetの間にあり、その日のHigh/Lowが
# 両方の水準へ届いた場合、日足だけでは順序が分からないため
# 「同日両方到達・順序不明」として分離する。
# ============================================================

def calculate_first_hit_results(
    data: pd.DataFrame,
    signal_rows: pd.DataFrame,
    prefix: str,
    target_r: float,
    horizon: int,
) -> pd.DataFrame:

    result_rows = []

    if signal_rows is None or signal_rows.empty:
        return pd.DataFrame()

    entry_date_col = f"{prefix}_Entry_Date"
    entry_price_col = f"{prefix}_Entry_Price"
    stop_price_col = f"{prefix}_Stop_Price"
    risk_col = f"{prefix}_Risk_1R"
    risk_percent_col = f"{prefix}_Risk_1R_Percent"
    valid_col = f"{prefix}_R_Valid"

    for signal_date, row in signal_rows.iterrows():

        if not bool(row.get(valid_col, False)):
            continue

        entry_date = row.get(entry_date_col, pd.NaT)
        entry_price = row.get(entry_price_col, np.nan)
        stop_price = row.get(stop_price_col, np.nan)
        risk_1r = row.get(risk_col, np.nan)
        risk_percent = row.get(risk_percent_col, np.nan)

        if (
            pd.isna(entry_date)
            or pd.isna(entry_price)
            or pd.isna(stop_price)
            or pd.isna(risk_1r)
        ):
            continue

        target_price = (
            float(entry_price)
            + float(target_r) * float(risk_1r)
        )

        try:
            entry_position = data.index.get_loc(entry_date)
        except KeyError:
            continue

        if not isinstance(entry_position, (int, np.integer)):
            # 日足Indexは一意である前提。万一重複した場合は
            # 誤判定を避けるためこのイベントを飛ばす。
            continue

        last_position = min(
            int(entry_position) + int(horizon) - 1,
            len(data) - 1,
        )

        available_days = (
            last_position
            - int(entry_position)
            + 1
        )

        outcome = None
        outcome_date = pd.NaT
        outcome_day = np.nan
        hit_price = np.nan

        for position in range(
            int(entry_position),
            last_position + 1,
        ):

            day_row = data.iloc[position]

            day_open = float(day_row["Open"])
            day_high = float(day_row["High"])
            day_low = float(day_row["Low"])

            current_date = data.index[position]
            day_number = (
                position
                - int(entry_position)
                + 1
            )

            # 前営業日からのギャップはOpenが最初に観測される価格。
            if day_open <= float(stop_price):
                outcome = "Stop先着"
                outcome_date = current_date
                outcome_day = day_number
                hit_price = day_open
                break

            if day_open >= float(target_price):
                outcome = "Target先着"
                outcome_date = current_date
                outcome_day = day_number
                hit_price = day_open
                break

            stop_hit = (
                day_low <= float(stop_price)
            )

            target_hit = (
                day_high >= float(target_price)
            )

            if stop_hit and target_hit:
                outcome = "同日両方到達・順序不明"
                outcome_date = current_date
                outcome_day = day_number
                break

            if stop_hit:
                outcome = "Stop先着"
                outcome_date = current_date
                outcome_day = day_number
                hit_price = float(stop_price)
                break

            if target_hit:
                outcome = "Target先着"
                outcome_date = current_date
                outcome_day = day_number
                hit_price = float(target_price)
                break

        if outcome is None:
            if available_days >= int(horizon):
                outcome = "期間内未到達"
            else:
                outcome = "将来データ不足"

        result_rows.append(
            {
                "BB_Event_ID": int(row["BB_Event_ID"]),
                "Signal_Date": signal_date,
                "Entry_Date": entry_date,
                "Entry_Price": float(entry_price),
                "Stop_Price": float(stop_price),
                "Risk_1R": float(risk_1r),
                "Risk_1R_Percent": float(risk_percent)
                    if not pd.isna(risk_percent) else np.nan,
                "Target_R": float(target_r),
                "Target_Price": float(target_price),
                "Horizon": int(horizon),
                "Available_Days": int(available_days),
                "Outcome": outcome,
                "Outcome_Date": outcome_date,
                "Outcome_Day": outcome_day,
                "Observed_Hit_Price": hit_price,
            }
        )

    return pd.DataFrame(result_rows)


def build_first_hit_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    outcome_order = [
        "Target先着",
        "Stop先着",
        "同日両方到達・順序不明",
        "期間内未到達",
        "将来データ不足",
    ]

    rows = []

    for horizon in FIRST_HIT_HORIZONS:

        horizon_df = results[
            results["Horizon"] == horizon
        ].copy()

        total = len(horizon_df)

        row = {
            "保有期間": f"{horizon}営業日",
            "対象": total,
        }

        for outcome in outcome_order:
            count = int(
                (horizon_df["Outcome"] == outcome).sum()
            )
            row[outcome] = count
            row[f"{outcome} %"] = (
                count / total * 100
                if total > 0
                else np.nan
            )

        rows.append(row)

    return pd.DataFrame(rows)


def make_first_hit_copy_text(
    title: str,
    summary_df: pd.DataFrame,
) -> str:

    lines = [title]

    if summary_df.empty:
        lines.append("対象イベントなし")
        return "\n".join(lines)

    lines.append(
        "保有期間,対象,Target先着,Stop先着,同日両方到達・順序不明,期間内未到達,将来データ不足"
    )

    for _, row in summary_df.iterrows():
        lines.append(
            f"{row['保有期間']},"
            f"{int(row['対象'])},"
            f"{int(row['Target先着'])},"
            f"{int(row['Stop先着'])},"
            f"{int(row['同日両方到達・順序不明'])},"
            f"{int(row['期間内未到達'])},"
            f"{int(row['将来データ不足'])}"
        )

    return "\n".join(lines)



# ============================================================
# v1.7
# R損益計算
#
# Target先着 -> +Target R
# Stop先着   -> -1R
# 期間内未到達 -> 指定保有期間の最終営業日終値で決済し、
#                 (Exit Close - Entry) / 1R を計算
# 同日両方到達・順序不明 / 将来データ不足はR損益計算から除外。
#
# 注意：Target / Stop先着時は設定した価格水準で決済した
# ルールベースRとして扱う。ギャップによる実約定差、
# 手数料、スリッページはまだ反映しない。
# ============================================================

def calculate_r_pnl_results(
    data: pd.DataFrame,
    first_hit_results: pd.DataFrame,
) -> pd.DataFrame:

    if first_hit_results is None or first_hit_results.empty:
        return pd.DataFrame()

    results = first_hit_results.copy()

    results["Exit_Type"] = ""
    results["Exit_Date"] = pd.NaT
    results["Exit_Price"] = np.nan
    results["Realized_R"] = np.nan
    results["R_PnL_Valid"] = False
    results["R_PnL_Status"] = "計算不可"

    for idx, row in results.iterrows():

        outcome = row.get("Outcome", "")
        target_r = row.get("Target_R", np.nan)
        target_price = row.get("Target_Price", np.nan)
        stop_price = row.get("Stop_Price", np.nan)
        entry_price = row.get("Entry_Price", np.nan)
        risk_1r = row.get("Risk_1R", np.nan)
        entry_date = row.get("Entry_Date", pd.NaT)
        horizon = row.get("Horizon", np.nan)

        if outcome == "Target先着":
            results.at[idx, "Exit_Type"] = "Target決済"
            results.at[idx, "Exit_Date"] = row.get(
                "Outcome_Date", pd.NaT
            )
            results.at[idx, "Exit_Price"] = float(target_price)
            results.at[idx, "Realized_R"] = float(target_r)
            results.at[idx, "R_PnL_Valid"] = True
            results.at[idx, "R_PnL_Status"] = "R損益計算可能"
            continue

        if outcome == "Stop先着":
            results.at[idx, "Exit_Type"] = "Stop決済"
            results.at[idx, "Exit_Date"] = row.get(
                "Outcome_Date", pd.NaT
            )
            results.at[idx, "Exit_Price"] = float(stop_price)
            results.at[idx, "Realized_R"] = -1.0
            results.at[idx, "R_PnL_Valid"] = True
            results.at[idx, "R_PnL_Status"] = "R損益計算可能"
            continue

        if outcome == "同日両方到達・順序不明":
            results.at[idx, "Exit_Type"] = "順序不明"
            results.at[idx, "R_PnL_Status"] = "同日両方到達・順序不明"
            continue

        if outcome == "将来データ不足":
            results.at[idx, "Exit_Type"] = "データ不足"
            results.at[idx, "R_PnL_Status"] = "将来データ不足"
            continue

        if outcome == "期間内未到達":

            if (
                pd.isna(entry_date)
                or pd.isna(entry_price)
                or pd.isna(risk_1r)
                or pd.isna(horizon)
                or float(risk_1r) <= 0
            ):
                results.at[idx, "Exit_Type"] = "期間末決済不可"
                results.at[idx, "R_PnL_Status"] = "期間末価格計算不可"
                continue

            try:
                entry_position = data.index.get_loc(entry_date)
            except KeyError:
                results.at[idx, "Exit_Type"] = "期間末決済不可"
                results.at[idx, "R_PnL_Status"] = "Entry日なし"
                continue

            if not isinstance(entry_position, (int, np.integer)):
                results.at[idx, "Exit_Type"] = "期間末決済不可"
                results.at[idx, "R_PnL_Status"] = "Entry日重複"
                continue

            exit_position = (
                int(entry_position)
                + int(horizon)
                - 1
            )

            if exit_position >= len(data):
                results.at[idx, "Exit_Type"] = "データ不足"
                results.at[idx, "R_PnL_Status"] = "将来データ不足"
                continue

            exit_date = data.index[exit_position]
            exit_close = pd.to_numeric(
                pd.Series([data.iloc[exit_position]["Close"]]),
                errors="coerce",
            ).iloc[0]

            if pd.isna(exit_close):
                results.at[idx, "Exit_Type"] = "期間末決済不可"
                results.at[idx, "R_PnL_Status"] = "期間末終値なし"
                continue

            realized_r = (
                float(exit_close)
                - float(entry_price)
            ) / float(risk_1r)

            results.at[idx, "Exit_Type"] = "期間末終値決済"
            results.at[idx, "Exit_Date"] = exit_date
            results.at[idx, "Exit_Price"] = float(exit_close)
            results.at[idx, "Realized_R"] = float(realized_r)
            results.at[idx, "R_PnL_Valid"] = True
            results.at[idx, "R_PnL_Status"] = "R損益計算可能"
            continue

        results.at[idx, "Exit_Type"] = "その他"
        results.at[idx, "R_PnL_Status"] = "未定義結果"

    return results


def build_r_pnl_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    if results is None or results.empty:
        return pd.DataFrame()

    for horizon in FIRST_HIT_HORIZONS:

        horizon_df = results[
            results["Horizon"] == horizon
        ].copy()

        total = len(horizon_df)

        valid_df = horizon_df[
            horizon_df["R_PnL_Valid"]
        ].copy()

        realized = pd.to_numeric(
            valid_df["Realized_R"],
            errors="coerce",
        ).dropna()

        row = {
            "保有期間": f"{horizon}営業日",
            "対象": total,
            "R損益計算可能": len(realized),
            "Target決済": int(
                (horizon_df["Exit_Type"] == "Target決済").sum()
            ),
            "Stop決済": int(
                (horizon_df["Exit_Type"] == "Stop決済").sum()
            ),
            "期間末終値決済": int(
                (horizon_df["Exit_Type"] == "期間末終値決済").sum()
            ),
            "順序不明": int(
                (horizon_df["Exit_Type"] == "順序不明").sum()
            ),
            "データ不足": int(
                (horizon_df["Exit_Type"] == "データ不足").sum()
            ),
            "合計R": (
                float(realized.sum())
                if not realized.empty else np.nan
            ),
            "平均R": (
                float(realized.mean())
                if not realized.empty else np.nan
            ),
            "中央値R": (
                float(realized.median())
                if not realized.empty else np.nan
            ),
            "プラスR": int((realized > 0).sum()),
            "マイナスR": int((realized < 0).sum()),
            "ゼロR": int(np.isclose(realized, 0.0).sum()),
        }

        rows.append(row)

    return pd.DataFrame(rows)


def make_r_pnl_copy_text(
    title: str,
    summary_df: pd.DataFrame,
) -> str:

    lines = [title]

    if summary_df is None or summary_df.empty:
        lines.append("対象イベントなし")
        return "\n".join(lines)

    lines.append(
        "保有期間,対象,R損益計算可能,Target決済,Stop決済,期間末終値決済,順序不明,データ不足,合計R,平均R,中央値R,プラスR,マイナスR,ゼロR"
    )

    for _, row in summary_df.iterrows():

        def fmt(value):
            if pd.isna(value):
                return ""
            return f"{float(value):.4f}"

        lines.append(
            f"{row['保有期間']},"
            f"{int(row['対象'])},"
            f"{int(row['R損益計算可能'])},"
            f"{int(row['Target決済'])},"
            f"{int(row['Stop決済'])},"
            f"{int(row['期間末終値決済'])},"
            f"{int(row['順序不明'])},"
            f"{int(row['データ不足'])},"
            f"{fmt(row['合計R'])},"
            f"{fmt(row['平均R'])},"
            f"{fmt(row['中央値R'])},"
            f"{int(row['プラスR'])},"
            f"{int(row['マイナスR'])},"
            f"{int(row['ゼロR'])}"
        )

    return "\n".join(lines)

# ============================================================
# v1.8
# 同一BB下限イベント・ペア比較
#
# 下落停止と反発開始の両方でR設計できた同じイベントを、
# 同じTarget・同じ保有期間で1対1比較する。
#
# 差 = 反発開始R - 下落停止R
# 正なら反発開始側、負なら下落停止側のR損益が高い。
# 同日順序不明や将来データ不足など、どちらか一方でも
# R損益計算不可ならペア差は計算せず「比較不可」とする。
# ============================================================

def build_paired_r_results(
    stop_results: pd.DataFrame,
    rebound_results: pd.DataFrame,
) -> pd.DataFrame:

    if (
        stop_results is None
        or rebound_results is None
        or stop_results.empty
        or rebound_results.empty
    ):
        return pd.DataFrame()

    stop_cols = [
        "BB_Event_ID",
        "Horizon",
        "Target_R",
        "Signal_Date",
        "Entry_Date",
        "Entry_Price",
        "Stop_Price",
        "Risk_1R",
        "Risk_1R_Percent",
        "Exit_Type",
        "Exit_Date",
        "Exit_Price",
        "Realized_R",
        "R_PnL_Valid",
        "R_PnL_Status",
    ]

    rebound_cols = stop_cols.copy()

    stop_part = stop_results[stop_cols].copy()
    rebound_part = rebound_results[rebound_cols].copy()

    paired = stop_part.merge(
        rebound_part,
        on=["BB_Event_ID", "Horizon", "Target_R"],
        how="inner",
        suffixes=("_Stop", "_Rebound"),
        validate="one_to_one",
    )

    if paired.empty:
        return paired

    stop_valid = paired["R_PnL_Valid_Stop"].fillna(False).astype(bool)
    rebound_valid = paired["R_PnL_Valid_Rebound"].fillna(False).astype(bool)

    paired["Pair_R_Valid"] = stop_valid & rebound_valid
    paired["R_Difference_Rebound_Minus_Stop"] = np.nan
    paired["Pair_Result"] = "比較不可"

    valid_mask = paired["Pair_R_Valid"]

    paired.loc[
        valid_mask,
        "R_Difference_Rebound_Minus_Stop",
    ] = (
        pd.to_numeric(
            paired.loc[valid_mask, "Realized_R_Rebound"],
            errors="coerce",
        )
        - pd.to_numeric(
            paired.loc[valid_mask, "Realized_R_Stop"],
            errors="coerce",
        )
    )

    diff = pd.to_numeric(
        paired["R_Difference_Rebound_Minus_Stop"],
        errors="coerce",
    )

    paired.loc[
        valid_mask & (diff > 1e-12),
        "Pair_Result",
    ] = "反発開始が高い"

    paired.loc[
        valid_mask & (diff < -1e-12),
        "Pair_Result",
    ] = "下落停止が高い"

    paired.loc[
        valid_mask & np.isclose(diff, 0.0, atol=1e-12, rtol=0.0),
        "Pair_Result",
    ] = "同じ"

    return paired.sort_values(
        ["Horizon", "BB_Event_ID"]
    ).reset_index(drop=True)


def build_paired_r_summary(
    paired_results: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    if paired_results is None or paired_results.empty:
        return pd.DataFrame()

    for horizon in FIRST_HIT_HORIZONS:

        part = paired_results[
            paired_results["Horizon"] == horizon
        ].copy()

        valid = part[
            part["Pair_R_Valid"]
        ].copy()

        stop_r = pd.to_numeric(
            valid["Realized_R_Stop"],
            errors="coerce",
        )

        rebound_r = pd.to_numeric(
            valid["Realized_R_Rebound"],
            errors="coerce",
        )

        diff = pd.to_numeric(
            valid["R_Difference_Rebound_Minus_Stop"],
            errors="coerce",
        ).dropna()

        rows.append(
            {
                "保有期間": f"{horizon}営業日",
                "同一イベント": len(part),
                "ペア比較可能": len(diff),
                "下落停止平均R": (
                    float(stop_r.mean())
                    if len(diff) > 0 else np.nan
                ),
                "反発開始平均R": (
                    float(rebound_r.mean())
                    if len(diff) > 0 else np.nan
                ),
                "平均R差_反発-下落": (
                    float(diff.mean())
                    if not diff.empty else np.nan
                ),
                "中央値R差_反発-下落": (
                    float(diff.median())
                    if not diff.empty else np.nan
                ),
                "反発開始が高い": int(
                    (valid["Pair_Result"] == "反発開始が高い").sum()
                ),
                "下落停止が高い": int(
                    (valid["Pair_Result"] == "下落停止が高い").sum()
                ),
                "同じ": int(
                    (valid["Pair_Result"] == "同じ").sum()
                ),
                "比較不可": int(
                    (~part["Pair_R_Valid"]).sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def make_paired_r_copy_text(
    title: str,
    summary_df: pd.DataFrame,
) -> str:

    lines = [title]

    if summary_df is None or summary_df.empty:
        lines.append("対象ペアイベントなし")
        return "\n".join(lines)

    lines.append(
        "保有期間,同一イベント,ペア比較可能,下落停止平均R,反発開始平均R,平均R差_反発-下落,中央値R差_反発-下落,反発開始が高い,下落停止が高い,同じ,比較不可"
    )

    def fmt(value):
        if pd.isna(value):
            return ""
        return f"{float(value):.4f}"

    for _, row in summary_df.iterrows():
        lines.append(
            f"{row['保有期間']},"
            f"{int(row['同一イベント'])},"
            f"{int(row['ペア比較可能'])},"
            f"{fmt(row['下落停止平均R'])},"
            f"{fmt(row['反発開始平均R'])},"
            f"{fmt(row['平均R差_反発-下落'])},"
            f"{fmt(row['中央値R差_反発-下落'])},"
            f"{int(row['反発開始が高い'])},"
            f"{int(row['下落停止が高い'])},"
            f"{int(row['同じ'])},"
            f"{int(row['比較不可'])}"
        )

    return "\n".join(lines)


def get_min_stop_risk_event_id(
    paired_results: pd.DataFrame,
):

    if paired_results is None or paired_results.empty:
        return None

    base = (
        paired_results
        .sort_values(["Horizon", "BB_Event_ID"])
        .drop_duplicates(subset=["BB_Event_ID"])
        .copy()
    )

    base["Risk_1R_Percent_Stop"] = pd.to_numeric(
        base["Risk_1R_Percent_Stop"],
        errors="coerce",
    )

    base = base.dropna(
        subset=["Risk_1R_Percent_Stop"]
    )

    if base.empty:
        return None

    idx = base["Risk_1R_Percent_Stop"].idxmin()

    return int(base.loc[idx, "BB_Event_ID"])


# ============================================================
# v1.9
# 下落停止時点を起点にした「反発待ち」方針
#
# 方針A:
#   First_Decline_Stop_In_Event の翌営業日始値でEntry。
#   既存Stop方式をそのまま使う。
#
# 方針B:
#   下落停止シグナル日から固定イベント終了日まで、
#   Close > Prev_High（反発開始候補）を待つ。
#   同じ日に両条件が成立していれば待ち0営業日。
#   下落停止より前に反発開始条件が出ていても、それだけでは採用しない。
#   期間内に確認できなければ見送り（0R機会）。
# ============================================================

def calculate_wait_rebound_after_stop(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Wait_Rebound_After_Stop"] = False
    df["Wait_Rebound_Days_From_Stop"] = np.nan
    df["Wait_Rebound_Stop_Signal_Date"] = pd.NaT

    stop_positions = np.where(
        df["First_Decline_Stop_In_Event"].to_numpy(dtype=bool)
    )[0]

    for stop_position in stop_positions:

        event_id = df.iloc[stop_position]["BB_Event_ID"]
        if pd.isna(event_id):
            continue

        event_id_int = int(event_id)

        event_positions = np.where(
            (df["BB_Event_ID"].fillna(-1).astype(int).to_numpy() == event_id_int)
        )[0]

        # 下落停止を確認した日以降だけを探索する。
        # これにより、下落停止より前に出た反発条件を未来の意思決定に流用しない。
        eligible_positions = [
            int(pos)
            for pos in event_positions
            if int(pos) >= int(stop_position)
            and bool(df.iloc[int(pos)]["Fixed_Window_Rebound_Start_Candidate"])
        ]

        if not eligible_positions:
            continue

        rebound_position = eligible_positions[0]
        rebound_date = df.index[rebound_position]
        stop_date = df.index[stop_position]

        df.at[rebound_date, "Wait_Rebound_After_Stop"] = True
        df.at[
            rebound_date,
            "Wait_Rebound_Days_From_Stop",
        ] = int(rebound_position - stop_position)
        df.at[
            rebound_date,
            "Wait_Rebound_Stop_Signal_Date",
        ] = stop_date

    return df


def build_v19_decision_results(
    opportunity_rows: pd.DataFrame,
    policy_a_results: pd.DataFrame,
    policy_b_signal_rows: pd.DataFrame,
    policy_b_results: pd.DataFrame,
    horizon: int,
    target_r: float,
) -> pd.DataFrame:

    if opportunity_rows is None or opportunity_rows.empty:
        return pd.DataFrame()

    base = opportunity_rows.copy()
    base = base.dropna(subset=["BB_Event_ID"])
    base["BB_Event_ID"] = base["BB_Event_ID"].astype(int)

    base = base[
        [
            "BB_Event_ID",
            "Stop_Signal_Date",
            "Stop_Entry_Date",
            "Stop_Entry_Price",
            "Stop_Stop_Price",
            "Stop_Risk_1R",
            "Stop_Risk_1R_Percent",
            "Stop_R_Valid",
            "Stop_R_Status",
        ]
    ].copy()

    # 方針A（下落停止ですぐEntry）のR結果
    if policy_a_results is not None and not policy_a_results.empty:
        a = policy_a_results[
            (policy_a_results["Horizon"] == int(horizon))
            & np.isclose(
                pd.to_numeric(policy_a_results["Target_R"], errors="coerce"),
                float(target_r),
            )
        ][
            [
                "BB_Event_ID",
                "Exit_Type",
                "Realized_R",
                "R_PnL_Valid",
                "R_PnL_Status",
            ]
        ].copy()

        a["BB_Event_ID"] = a["BB_Event_ID"].astype(int)
        a = a.rename(
            columns={
                "Exit_Type": "Policy_A_Exit_Type",
                "Realized_R": "Policy_A_R",
                "R_PnL_Valid": "Policy_A_R_Valid",
                "R_PnL_Status": "Policy_A_R_Status",
            }
        )
        base = base.merge(a, on="BB_Event_ID", how="left", validate="one_to_one")
    else:
        base["Policy_A_Exit_Type"] = ""
        base["Policy_A_R"] = np.nan
        base["Policy_A_R_Valid"] = False
        base["Policy_A_R_Status"] = "結果なし"

    # 方針Bのシグナル有無。見送りも母集団から消さない。
    b_signal = pd.DataFrame()
    if policy_b_signal_rows is not None and not policy_b_signal_rows.empty:
        b_signal = policy_b_signal_rows.dropna(subset=["BB_Event_ID"]).copy()
        b_signal["BB_Event_ID"] = b_signal["BB_Event_ID"].astype(int)
        b_signal = b_signal[
            [
                "BB_Event_ID",
                "WaitRebound_Signal_Date",
                "WaitRebound_Entry_Date",
                "WaitRebound_Entry_Price",
                "WaitRebound_Stop_Price",
                "WaitRebound_Risk_1R",
                "WaitRebound_Risk_1R_Percent",
                "WaitRebound_R_Valid",
                "WaitRebound_R_Status",
                "Wait_Rebound_Days_From_Stop",
            ]
        ].copy()

    if not b_signal.empty:
        base = base.merge(b_signal, on="BB_Event_ID", how="left", validate="one_to_one")
    else:
        for col in [
            "WaitRebound_Signal_Date",
            "WaitRebound_Entry_Date",
            "WaitRebound_Entry_Price",
            "WaitRebound_Stop_Price",
            "WaitRebound_Risk_1R",
            "WaitRebound_Risk_1R_Percent",
            "Wait_Rebound_Days_From_Stop",
        ]:
            base[col] = np.nan
        base["WaitRebound_R_Valid"] = False
        base["WaitRebound_R_Status"] = "反発未確認"

    base["Policy_B_Has_Rebound"] = base["WaitRebound_Signal_Date"].notna()
    base["Policy_B_Action"] = np.where(
        base["Policy_B_Has_Rebound"],
        "反発確認→Entry",
        "見送り",
    )

    # 方針BでEntryしたケースのR結果
    if policy_b_results is not None and not policy_b_results.empty:
        b = policy_b_results[
            (policy_b_results["Horizon"] == int(horizon))
            & np.isclose(
                pd.to_numeric(policy_b_results["Target_R"], errors="coerce"),
                float(target_r),
            )
        ][
            [
                "BB_Event_ID",
                "Exit_Type",
                "Realized_R",
                "R_PnL_Valid",
                "R_PnL_Status",
            ]
        ].copy()
        b["BB_Event_ID"] = b["BB_Event_ID"].astype(int)
        b = b.rename(
            columns={
                "Exit_Type": "Policy_B_Exit_Type",
                "Realized_R": "Policy_B_Trade_R",
                "R_PnL_Valid": "Policy_B_Trade_R_Valid",
                "R_PnL_Status": "Policy_B_Trade_R_Status",
            }
        )
        base = base.merge(b, on="BB_Event_ID", how="left", validate="one_to_one")
    else:
        base["Policy_B_Exit_Type"] = ""
        base["Policy_B_Trade_R"] = np.nan
        base["Policy_B_Trade_R_Valid"] = False
        base["Policy_B_Trade_R_Status"] = "結果なし"

    # 見送りは「取引損益」ではなく、意思決定機会として0Rとする。
    # EntryしたのにR結果が不明なケースは0Rにせず比較不可のまま残す。
    base["Policy_B_Opportunity_R"] = np.nan
    skip_mask = ~base["Policy_B_Has_Rebound"]
    base.loc[skip_mask, "Policy_B_Opportunity_R"] = 0.0

    b_trade_valid = (
        base["Policy_B_Trade_R_Valid"].eq(True)
        if "Policy_B_Trade_R_Valid" in base.columns
        else pd.Series(False, index=base.index)
    )
    base.loc[
        base["Policy_B_Has_Rebound"] & b_trade_valid,
        "Policy_B_Opportunity_R",
    ] = pd.to_numeric(
        base.loc[
            base["Policy_B_Has_Rebound"] & b_trade_valid,
            "Policy_B_Trade_R",
        ],
        errors="coerce",
    )

    a_valid = base["Policy_A_R_Valid"].eq(True)
    b_decision_valid = skip_mask | (
        base["Policy_B_Has_Rebound"] & b_trade_valid
    )

    base["Decision_Comparison_Valid"] = a_valid & b_decision_valid
    base["Decision_R_Difference_B_Minus_A"] = np.nan

    valid_mask = base["Decision_Comparison_Valid"]
    base.loc[
        valid_mask,
        "Decision_R_Difference_B_Minus_A",
    ] = (
        pd.to_numeric(base.loc[valid_mask, "Policy_B_Opportunity_R"], errors="coerce")
        - pd.to_numeric(base.loc[valid_mask, "Policy_A_R"], errors="coerce")
    )

    diff = pd.to_numeric(base["Decision_R_Difference_B_Minus_A"], errors="coerce")
    base["Decision_Result"] = "比較不可"
    base.loc[valid_mask & (diff > 1e-12), "Decision_Result"] = "方針Bが高い"
    base.loc[valid_mask & (diff < -1e-12), "Decision_Result"] = "方針Aが高い"
    base.loc[
        valid_mask & np.isclose(diff, 0.0, atol=1e-12, rtol=0.0),
        "Decision_Result",
    ] = "同じ"

    base["Horizon"] = int(horizon)
    base["Target_R"] = float(target_r)

    return base.sort_values("BB_Event_ID").reset_index(drop=True)


def build_v19_decision_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    if results is None or results.empty:
        return pd.DataFrame()

    rows = []

    for horizon in FIRST_HIT_HORIZONS:
        part = results[results["Horizon"] == int(horizon)].copy()
        if part.empty:
            continue

        valid = part[part["Decision_Comparison_Valid"]].copy()
        entered = part[part["Policy_B_Has_Rebound"]].copy()
        entered_valid = entered[
            entered["Policy_B_Trade_R_Valid"].eq(True)
        ].copy()

        a_r = pd.to_numeric(valid["Policy_A_R"], errors="coerce").dropna()
        b_opp_r = pd.to_numeric(valid["Policy_B_Opportunity_R"], errors="coerce").dropna()
        b_trade_r = pd.to_numeric(entered_valid["Policy_B_Trade_R"], errors="coerce").dropna()
        diff = pd.to_numeric(
            valid["Decision_R_Difference_B_Minus_A"], errors="coerce"
        ).dropna()
        waits = pd.to_numeric(
            entered["Wait_Rebound_Days_From_Stop"], errors="coerce"
        ).dropna()

        rows.append(
            {
                "保有期間": f"{horizon}営業日",
                "意思決定機会": len(part),
                "比較可能": len(valid),
                "方針A平均R": float(a_r.mean()) if not a_r.empty else np.nan,
                "方針B機会平均R": float(b_opp_r.mean()) if not b_opp_r.empty else np.nan,
                "平均R差_B-A": float(diff.mean()) if not diff.empty else np.nan,
                "中央値R差_B-A": float(diff.median()) if not diff.empty else np.nan,
                "方針B_Entry": int(part["Policy_B_Has_Rebound"].sum()),
                "方針B_見送り": int((~part["Policy_B_Has_Rebound"]).sum()),
                "方針B_Entry取引平均R": float(b_trade_r.mean()) if not b_trade_r.empty else np.nan,
                "平均待ち営業日": float(waits.mean()) if not waits.empty else np.nan,
                "方針Bが高い": int((valid["Decision_Result"] == "方針Bが高い").sum()),
                "方針Aが高い": int((valid["Decision_Result"] == "方針Aが高い").sum()),
                "同じ": int((valid["Decision_Result"] == "同じ").sum()),
                "比較不可": int((~part["Decision_Comparison_Valid"]).sum()),
            }
        )

    return pd.DataFrame(rows)


def make_v19_decision_copy_text(
    title: str,
    summary_df: pd.DataFrame,
) -> str:

    lines = [title]

    if summary_df is None or summary_df.empty:
        lines.append("対象イベントなし")
        return "\n".join(lines)

    lines.append(
        "保有期間,意思決定機会,比較可能,方針A平均R,方針B機会平均R,平均R差_B-A,中央値R差_B-A,方針B_Entry,方針B_見送り,方針B_Entry取引平均R,平均待ち営業日,方針Bが高い,方針Aが高い,同じ,比較不可"
    )

    def fmt(value):
        if pd.isna(value):
            return ""
        return f"{float(value):.4f}"

    for _, row in summary_df.iterrows():
        lines.append(
            f"{row['保有期間']},"
            f"{int(row['意思決定機会'])},"
            f"{int(row['比較可能'])},"
            f"{fmt(row['方針A平均R'])},"
            f"{fmt(row['方針B機会平均R'])},"
            f"{fmt(row['平均R差_B-A'])},"
            f"{fmt(row['中央値R差_B-A'])},"
            f"{int(row['方針B_Entry'])},"
            f"{int(row['方針B_見送り'])},"
            f"{fmt(row['方針B_Entry取引平均R'])},"
            f"{fmt(row['平均待ち営業日'])},"
            f"{int(row['方針Bが高い'])},"
            f"{int(row['方針Aが高い'])},"
            f"{int(row['同じ'])},"
            f"{int(row['比較不可'])}"
        )

    return "\n".join(lines)


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

    # v1.9: 下落停止を確認した時点から反発開始を待つ方針B
    df = calculate_wait_rebound_after_stop(
        df
    )

    df = calculate_r_design(
        df,
        "Wait_Rebound_After_Stop",
        "WaitRebound",
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
    "下落停止時点からの意思決定比較版"
)

st.info(
    "v1.9ではv1.8までの研究結果を維持したまま、"
    "意思決定の起点を下落停止シグナル確認時点に固定します。"
    "方針Aは下落停止後すぐEntry、方針Bは同じ固定イベント内で反発開始を待ち、"
    "確認できなければ見送り0R機会として残します。"
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

for prefix_name, valid_df in [
    ("Stop", stop_r_valid),
    ("Rebound", rebound_r_valid),
]:

    for target_r in [1.5, 2.0]:

        result_parts = []

        for horizon in FIRST_HIT_HORIZONS:

            part = calculate_first_hit_results(
                df,
                valid_df,
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
    "【未実装】コスト・スリッページを含む約定損益"
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
    "コストや実際の約定条件もまだ含めていません。"
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

st.caption(
    "このプログラムは研究・検証用です。"
    "売買シグナルとして正式採用したものではありません。"
)
