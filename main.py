# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.3
#
# v1.1 から継続
# ・125営業日 BandWidth 正規化
# ・公式Squeeze基準の確認
# ・研究用「低BandWidthゾーン」
# ・BandWidth 収縮 / 拡大分類
# ・Squeezeからの拡大開始候補
# ・過去の状態一覧
#
# v1.2 追加内容
# ・BB下限タッチ判定
# ・日中BB下限下抜け判定
# ・下抜け後の終値BB内復帰判定
# ・BB下限より下での終値確定判定
# ・低BandWidthから下方向へ拡大開始候補
# ・過去30営業日のBB下限状態一覧
# ・各状態の発生件数
#
# v1.3 追加内容
# ・前日安値を割らない判定
# ・安値切り上げ判定
# ・前日終値より上昇判定
# ・陽線判定
# ・安値切り上げ＋終値上昇の複合条件
# ・BB下限イベント後3営業日以内の追跡
# ・下落停止候補の分類
# ・下落停止候補の発生件数
# ・下落停止候補の過去一覧
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

APP_VERSION = "1.3"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125

# 研究用の低BandWidthゾーン
LOW_BANDWIDTH_ZONE = 0.20

# ------------------------------------------------------------
# v1.3
# BB下限イベント後を何営業日追跡するか
#
# 3営業日は研究用の仮設定。
# 最適値として正式採用したものではない。
# ------------------------------------------------------------

LOWER_EVENT_LOOKBACK_DAYS = 3


# ============================================================
# 株価データ取得
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
# BandWidthの方向分類
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
# v1.2
# BB下限イベント判定
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
# v1.2
# BB下限状態の文字分類
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
# 低BandWidthから下方向へ拡大開始候補
# ============================================================

def calculate_downside_expansion(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Prev_Low_BandWidth_Zone"] = (
        df["Low_BandWidth_Zone"]
        .shift(1)
        .fillna(False)
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
# v1.2
# 下方向拡大状態の文字分類
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
# 下落停止の基本条件
# ============================================================

def calculate_decline_stop_conditions(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    # 前日の値
    df["Prev_Low"] = df["Low"].shift(1)
    df["Prev_Close"] = df["Close"].shift(1)

    # --------------------------------------------------------
    # 前日安値を割らない
    #
    # 同値も含む
    # --------------------------------------------------------

    df["No_Lower_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] >= df["Prev_Low"])
    )

    # --------------------------------------------------------
    # 安値切り上げ
    #
    # 前日安値より明確に高い
    # --------------------------------------------------------

    df["Higher_Low"] = (
        df["Prev_Low"].notna()
        & (df["Low"] > df["Prev_Low"])
    )

    # --------------------------------------------------------
    # 前日終値より上昇
    # --------------------------------------------------------

    df["Close_Up"] = (
        df["Prev_Close"].notna()
        & (df["Close"] > df["Prev_Close"])
    )

    # --------------------------------------------------------
    # 陽線
    # --------------------------------------------------------

    df["Bullish_Candle"] = (
        df["Close"] > df["Open"]
    )

    # --------------------------------------------------------
    # 複合条件
    #
    # 安値切り上げ ＋ 前日終値より上昇
    #
    # 研究用の下落停止候補
    # --------------------------------------------------------

    df["Decline_Stop_Combo"] = (
        df["Higher_Low"]
        & df["Close_Up"]
    )

    return df


# ============================================================
# v1.3
# BB下限イベント後の追跡
# ============================================================

def calculate_lower_event_window(
    data: pd.DataFrame,
    lookback_days: int = 3,
) -> pd.DataFrame:

    df = data.copy()

    # --------------------------------------------------------
    # 当日を含む直近3営業日以内に
    # BB下限タッチがあったか
    #
    # 例：
    # 今日タッチ       → 0日前
    # 昨日タッチ       → 1営業日前
    # 2営業日前タッチ  → 2営業日前
    # 3営業日前タッチ  → 3営業日前
    # --------------------------------------------------------

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
            .shift(days_ago)
            .fillna(False)
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
# BB下限付近での下落停止候補
# ============================================================

def calculate_decline_stop_candidates(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    # --------------------------------------------------------
    # 単独条件のうち、
    # BB下限イベント後3営業日以内に発生
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BB内復帰
    #
    # v1.2の条件をそのまま利用
    # --------------------------------------------------------

    df["Recent_Event_Reclaim"] = (
        df["Recent_BB_Lower_Event"]
        & df["BB_Lower_Reclaim"]
    )

    # --------------------------------------------------------
    # 複合下落停止候補
    #
    # BB下限タッチから3営業日以内
    # ＋ 安値切り上げ
    # ＋ 前日終値より上昇
    # --------------------------------------------------------

    df["Decline_Stop_Candidate"] = (
        df["Recent_BB_Lower_Event"]
        & df["Decline_Stop_Combo"]
    )

    # --------------------------------------------------------
    # 確認項目数
    #
    # 売買スコアではない。
    # 条件が何個同時に出ているかを研究するため。
    # --------------------------------------------------------

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
# 下落停止状態の文字分類
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
    df = calculate_bandwidth(df)

    # 3. BB下限との距離
    df = calculate_lower_band_distance(df)

    # 4. BandWidth状態
    df = calculate_bandwidth_state(
        df,
        SQUEEZE_LOOKBACK,
    )

    # 5. BandWidth方向
    df["BandWidth_Direction"] = df.apply(
        classify_bandwidth_direction,
        axis=1,
    )

    # 6. Squeeze状態
    df["Squeeze_State"] = df.apply(
        classify_squeeze_state,
        axis=1,
    )

    # 7. v1.2 BB下限イベント
    df = calculate_lower_band_events(df)

    df["Lower_Band_Event"] = df.apply(
        classify_lower_band_event,
        axis=1,
    )

    # 8. v1.2 下方向拡大
    df = calculate_downside_expansion(df)

    df["Downside_Expansion_State"] = df.apply(
        classify_downside_expansion,
        axis=1,
    )

    # 9. v1.3 下落停止基本条件
    df = calculate_decline_stop_conditions(df)

    # 10. v1.3 BB下限イベント後追跡
    df = calculate_lower_event_window(
        df,
        LOWER_EVENT_LOOKBACK_DAYS,
    )

    # 11. v1.3 下落停止候補
    df = calculate_decline_stop_candidates(df)

    df["Decline_Stop_State"] = df.apply(
        classify_decline_stop,
        axis=1,
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


# ============================================================
# タイトル
# ============================================================

st.title(
    "📊 GOOG・NVDA BB下限研究"
)

st.caption(
    f"Version {APP_VERSION} ｜ "
    "下落停止候補研究版"
)

st.info(
    "現在は研究段階です。"
    "BB下限、スクイーズ、BandWidth、"
    "下方向拡大に加えて、"
    "BB下限付近で下落が止まり始めた可能性を"
    "複数条件に分けて研究します。"
    "まだ買い・売り判断は行いません。"
)


# ============================================================
# 銘柄
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

period = period_map[period_label]


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
latest_date = valid_df.index[-1]


# ============================================================
# 最新状態
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
# BB下限との位置関係
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
# スクイーズ状態
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
        "公式Squeeze基準："
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
# 正規化BandWidth
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
        "0％に近いほど、"
        "過去125営業日の最低BandWidthに近く、"
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
    "正規化BandWidthが20％以下という分類は、"
    "GOOG・NVDAの比較研究のための仮分類です。"
    "正式な売買条件ではありません。"
)


# ============================================================
# BandWidth変化
# ============================================================

st.subheader(
    "⑥ BandWidth変化"
)

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "前日比",
        f"{format_number(latest['BandWidth_Change_1D'])}",
    )


with col2:

    st.metric(
        "3営業日前比",
        f"{format_number(latest['BandWidth_Change_3D'])}",
    )


with col3:

    st.metric(
        "5営業日前比",
        f"{format_number(latest['BandWidth_Change_5D'])}",
    )


st.write(
    "現在の方向分類：",
    direction_state,
)


# ============================================================
# BB下限イベント
# ============================================================

st.subheader(
    "⑦ BB下限イベント"
)

st.write(
    "現在のBB下限状態：",
    latest["Lower_Band_Event"],
)


event_col1, event_col2 = st.columns(2)


with event_col1:

    st.write(
        "BB下限タッチ：",
        yes_no(latest["BB_Lower_Touch"]),
    )

    st.write(
        "日中BB下限下抜け：",
        yes_no(latest["BB_Lower_Intraday_Break"]),
    )


with event_col2:

    st.write(
        "下抜け後、終値でBB内復帰：",
        yes_no(latest["BB_Lower_Reclaim"]),
    )

    st.write(
        "BB下限より下で終値：",
        yes_no(latest["BB_Lower_Close_Below"]),
    )


if bool(latest["BB_Lower_Reclaim"]):

    st.info(
        "研究上の注目状態："
        "日中はBB下限を下抜けしましたが、"
        "終値ではBB内へ戻っています。"
    )


if bool(latest["BB_Lower_Close_Below"]):

    st.warning(
        "研究上の注目状態："
        "終値がBB下限より下です。"
        "反転とは決めず、"
        "下方向への継続可能性も含めて研究します。"
    )


# ============================================================
# 下方向拡大
# ============================================================

st.subheader(
    "⑧ 低BandWidthからの下方向拡大"
)

downside_state = latest[
    "Downside_Expansion_State"
]

st.write(
    "現在の分類：",
    downside_state,
)


if bool(
    latest["Downside_Expansion_Close_Below"]
):

    st.warning(
        "前日は低BandWidthゾーンで、"
        "BandWidthが拡大し、"
        "価格はBB下限方向へ動き、"
        "終値もBB下限より下です。"
        "下方向への拡大候補として記録します。"
    )


elif bool(
    latest["Downside_Expansion_Reclaim"]
):

    st.info(
        "前日は低BandWidthゾーンで、"
        "BandWidthが拡大しました。"
        "日中はBB下限を下抜けしましたが、"
        "終値ではBB内へ復帰しました。"
        "下抜け失敗候補として記録します。"
    )


elif bool(
    latest["Downside_Expansion_Candidate"]
):

    st.info(
        "前日は低BandWidthゾーンで、"
        "BandWidthが拡大し、"
        "当日安値がBB下限に到達しています。"
        "下方向への拡大開始候補です。"
    )


else:

    st.write(
        "現在は研究用の"
        "『低BandWidthから下方向拡大』"
        "条件には該当していません。"
    )


st.caption(
    "この分類は研究用です。"
    "買い・売りシグナルではありません。"
)


# ============================================================
# v1.3 下落停止候補
# ============================================================

st.subheader(
    "⑨ 下落停止候補"
)

st.write(
    "現在の研究分類：",
    latest["Decline_Stop_State"],
)

st.write(
    "直近のBB下限タッチ：",
    format_days_since_touch(
        latest["Days_Since_BB_Lower_Touch"]
    ),
)


stop_col1, stop_col2 = st.columns(2)


with stop_col1:

    st.write(
        "前日安値を割らない：",
        yes_no(latest["No_Lower_Low"]),
    )

    st.write(
        "安値切り上げ：",
        yes_no(latest["Higher_Low"]),
    )

    st.write(
        "前日終値より上昇：",
        yes_no(latest["Close_Up"]),
    )


with stop_col2:

    st.write(
        "陽線：",
        yes_no(latest["Bullish_Candle"]),
    )

    st.write(
        "当日のBB内復帰：",
        yes_no(latest["BB_Lower_Reclaim"]),
    )

    st.write(
        "安値切り上げ＋終値上昇：",
        yes_no(latest["Decline_Stop_Combo"]),
    )


st.metric(
    "確認項目数",
    f"{int(latest['Decline_Stop_Condition_Count'])} / 4",
)


if bool(
    latest["Decline_Stop_Candidate"]
):

    st.info(
        "【研究分類：下落停止候補】"
        "直近3営業日以内にBB下限タッチがあり、"
        "現在は安値切り上げと"
        "前日終値より上昇が同時に確認されています。"
    )

else:

    if bool(
        latest["Recent_BB_Lower_Event"]
    ):

        st.write(
            "直近3営業日以内にBB下限イベントはありますが、"
            "研究用の複合下落停止条件は"
            "まだ成立していません。"
        )

    else:

        st.write(
            "直近3営業日以内に"
            "BB下限タッチがないため、"
            "現在はBB下限後の下落停止研究対象ではありません。"
        )


st.caption(
    "3営業日は研究用の仮設定です。"
    "また『安値切り上げ＋終値上昇』も"
    "まだ正式なエントリー条件ではありません。"
)


# ============================================================
# チャート
# ============================================================

st.divider()

st.subheader(
    "⑩ 株価とボリンジャーバンド"
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
# BandWidthチャート
# ============================================================

st.subheader(
    "⑪ BandWidth"
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
# 正規化BandWidthチャート
# ============================================================

st.subheader(
    "⑫ 正規化BandWidth"
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
# 最新30営業日の状態
# ============================================================

st.subheader(
    "⑬ 最新30営業日の状態確認"
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
            "BandWidth_Direction",
            "Squeeze_State",
            "Lower_Band_Event",
            "Downside_Expansion_State",
            "Higher_Low",
            "Close_Up",
            "Bullish_Candle",
            "Decline_Stop_State",
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

        "BandWidth_Direction":
            "BW方向",

        "Squeeze_State":
            "スクイーズ状態",

        "Lower_Band_Event":
            "BB下限イベント",

        "Downside_Expansion_State":
            "下方向拡大状態",

        "Higher_Low":
            "安値切上",

        "Close_Up":
            "終値上昇",

        "Bullish_Candle":
            "陽線",

        "Decline_Stop_State":
            "下落停止状態",
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
# v1.2までの研究用集計
# ============================================================

st.subheader(
    "⑭ 現在取得している期間の基本分類件数"
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


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "判定可能日",
            f"{total_count}日",
        )

    with col2:

        st.metric(
            "公式Squeeze基準日",
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


    st.metric(
        "低BW→下方向拡大候補",
        f"{downside_count}日",
    )


# ============================================================
# v1.3 下落停止条件集計
# ============================================================

st.subheader(
    "⑮ 下落停止条件の発生件数"
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

    decline_stop_count = int(
        research_df[
            "Decline_Stop_Candidate"
        ].sum()
    )


    col1, col2, col3 = st.columns(3)

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


    col4, col5, col6 = st.columns(3)

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
        "BB下限後・下落停止候補",
        f"{decline_stop_count}日",
    )


    st.caption(
        "単独条件の件数は市場全体での発生件数です。"
        "『BB下限後・下落停止候補』は、"
        "BB下限タッチから3営業日以内という条件を"
        "追加した研究用分類です。"
    )


# ============================================================
# v1.3
# 下落停止候補だけ抽出
# ============================================================

st.subheader(
    "⑯ BB下限後の下落停止候補一覧"
)


decline_stop_df = valid_df[
    valid_df[
        "Decline_Stop_Candidate"
    ]
].copy()


if decline_stop_df.empty:

    st.info(
        "選択した期間には"
        "現在の研究条件に該当する"
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


    decline_display = decline_display.rename(
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

            "Decline_Stop_State":
                "下落停止状態",
        }
    )


    decline_numeric_columns = [
        "始値",
        "終値",
        "安値",
        "BB下限",
        "BBタッチから営業日",
        "BandWidth %",
        "正規化BW %",
    ]


    decline_display[
        decline_numeric_columns
    ] = (
        decline_display[
            decline_numeric_columns
        ]
        .round(2)
    )


    st.dataframe(
        decline_display,
        use_container_width=True,
    )


    st.caption(
        "この一覧は『成功した反発』の一覧ではありません。"
        "現在定義している下落停止候補が"
        "発生した日だけを抽出しています。"
    )


# ============================================================
# BB下限注目イベント
# ============================================================

st.subheader(
    "⑰ BB下限の注目イベント"
)


event_df = valid_df[
    (
        valid_df["BB_Lower_Touch"]
        | valid_df["Downside_Expansion_Candidate"]
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


    event_display = event_display.rename(
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
        }
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
# 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "⑱ 現在の研究段階"
)


st.write(
    "【実装済み】GOOG / NVDA 切り替え"
)

st.write(
    "【実装済み】株価取得"
)

st.write(
    "【実装済み】20日・2標準偏差BB"
)

st.write(
    "【実装済み】BandWidth"
)

st.write(
    "【実装済み】BB下限との距離"
)

st.write(
    "【実装済み】125営業日BandWidth最低・最高"
)

st.write(
    "【実装済み】正規化BandWidth"
)

st.write(
    "【実装済み】公式Squeeze基準表示"
)

st.write(
    "【研究分類】低BandWidthゾーン"
)

st.write(
    "【実装済み】BandWidth収縮・拡大分類"
)

st.write(
    "【研究分類】低BandWidthからの拡大開始候補"
)

st.write(
    "【v1.2 実装済み】BB下限タッチ"
)

st.write(
    "【v1.2 実装済み】日中BB下限下抜け"
)

st.write(
    "【v1.2 実装済み】下抜け後BB内復帰"
)

st.write(
    "【v1.2 実装済み】BB下限より下で終値"
)

st.write(
    "【v1.2 研究分類】低BandWidthから下方向拡大"
)

st.write(
    "【v1.3 実装済み】前日安値を割らない"
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
    "【v1.3 研究分類】BB下限イベント後3営業日追跡"
)

st.write(
    "【v1.3 研究分類】下落停止候補"
)

st.write(
    "【未検証】下落停止候補をエントリー条件として使うこと"
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
    "【未実装】過去実績バックテスト"
)


# ============================================================
# 重要説明
# ============================================================

st.divider()

st.warning(
    "重要："
    "v1.3の『下落停止候補』は、"
    "BB下限タッチから3営業日以内に"
    "安値切り上げと終値上昇が"
    "同時に発生したケースを抽出する"
    "研究用の仮条件です。"
    "利益が出ることはまだ検証していません。"
    "買いシグナルとして正式採用したものではありません。"
)


st.caption(
    "このプログラムは研究・検証用です。"
    "表示された状態は将来の株価上昇・下落を"
    "保証するものではありません。"
)
