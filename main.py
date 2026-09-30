# ============================================================
# GOOG / NVDA
# Bollinger Band Research Program
#
# Version : 1.0
#
# 目的
# ・GOOG / NVDA の株価取得
# ・ボリンジャーバンド計算
# ・BandWidth 計算
# ・BB下限との位置関係を確認
# ・スクイーズ研究の基礎データを確認
#
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

APP_VERSION = "1.0"

BB_PERIOD = 20
BB_STD = 2.0

# John Bollinger の Squeeze 研究を参考に、
# 125営業日の BandWidth 最小値を確認するために使用
SQUEEZE_LOOKBACK = 125


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

        # 必要列を確認
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

        # 数値化
        for column in required_columns:
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
# ボリンジャーバンド計算
# ============================================================

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2.0,
) -> pd.DataFrame:

    df = data.copy()

    # 中央線
    df["BB_Middle"] = (
        df["Close"]
        .rolling(window=period)
        .mean()
    )

    # 標準偏差
    df["BB_Std"] = (
        df["Close"]
        .rolling(window=period)
        .std(ddof=0)
    )

    # 上側バンド
    df["BB_Upper"] = (
        df["BB_Middle"]
        + std_multiplier * df["BB_Std"]
    )

    # 下側バンド
    df["BB_Lower"] = (
        df["BB_Middle"]
        - std_multiplier * df["BB_Std"]
    )

    return df


# ============================================================
# BandWidth 計算
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

    # 終値がBB下限から何％離れているか
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

    # 当日安値がBB下限から何％離れているか
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

    # 125営業日の最小BandWidth
    df["BandWidth_Min_125"] = (
        df["BandWidth"]
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .min()
    )

    # 125営業日の最大BandWidth
    df["BandWidth_Max_125"] = (
        df["BandWidth"]
        .rolling(
            window=lookback,
            min_periods=lookback,
        )
        .max()
    )

    # 直前日との差
    df["BandWidth_Change"] = (
        df["BandWidth"]
        - df["BandWidth"].shift(1)
    )

    # 5日前との差
    df["BandWidth_Change_5D"] = (
        df["BandWidth"]
        - df["BandWidth"].shift(5)
    )

    return df


# ============================================================
# データ処理まとめ
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

    df = calculate_bandwidth(df)

    df = calculate_lower_band_distance(df)

    df = calculate_bandwidth_state(
        df,
        SQUEEZE_LOOKBACK,
    )

    return df


# ============================================================
# 表示用関数
# ============================================================

def format_number(
    value,
    digits=2,
):

    if pd.isna(value):
        return "計算不可"

    return f"{value:,.{digits}f}"


# ============================================================
# タイトル
# ============================================================

st.title("📊 GOOG・NVDA BB下限研究")

st.caption(
    f"Version {APP_VERSION} ｜ "
    "ボリンジャーバンド・BandWidth 基礎確認版"
)

st.info(
    "現在は研究の第1段階です。"
    "この画面は売買を指示するものではなく、"
    "GOOG・NVDAのBB下限とボラティリティ状態を"
    "正しく確認するための画面です。"
)


# ============================================================
# 銘柄選択
# ============================================================

st.subheader("① 銘柄を選択")

ticker = st.radio(
    "研究する銘柄",
    options=[
        "GOOG",
        "NVDA",
    ],
    horizontal=True,
)


# ============================================================
# 取得期間
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


# ============================================================
# データ取得失敗
# ============================================================

if df.empty:

    st.error(
        f"{ticker} の株価データを取得できませんでした。"
    )

    st.warning(
        "Yahoo Finance側の一時的な通信エラーの可能性があります。"
        "少し時間を置いて再読み込みしてください。"
    )

    st.stop()


# ============================================================
# BB計算済みデータだけ使用
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
        "十分な株価データがありません。"
    )

    st.stop()


# ============================================================
# 最新データ
# ============================================================

latest = valid_df.iloc[-1]

latest_date = valid_df.index[-1]

previous = (
    valid_df.iloc[-2]
    if len(valid_df) >= 2
    else latest
)


# ============================================================
# 最新状態
# ============================================================

st.divider()

st.subheader(
    f"② {ticker} 最新状態"
)

st.write(
    "データ日：",
    latest_date.strftime("%Y年%m月%d日"),
)


# ============================================================
# 主要数値
# ============================================================

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
        "終値はBB下限から1％以内にあります。"
        "研究上の『BB下限付近』候補です。"
    )

else:

    st.success(
        "現在の終値はBB下限から"
        "1％より離れています。"
    )


if low_distance <= 0:

    st.warning(
        "当日の安値はBB下限に到達、"
        "またはBB下限を下回っています。"
    )

else:

    st.write(
        "当日の安値はBB下限より上です。"
    )


st.caption(
    "注意：1％は現在の正式な売買条件ではありません。"
    "BB下限との距離を確認するための仮の研究表示です。"
)


# ============================================================
# BandWidth 方向
# ============================================================

st.subheader(
    "④ BandWidth の状態"
)

bandwidth_change = latest[
    "BandWidth_Change"
]

bandwidth_change_5d = latest[
    "BandWidth_Change_5D"
]


if pd.notna(bandwidth_change):

    if bandwidth_change > 0:

        st.write(
            "前日比：BandWidth は拡大しています。"
        )

    elif bandwidth_change < 0:

        st.write(
            "前日比：BandWidth は縮小しています。"
        )

    else:

        st.write(
            "前日比：BandWidth はほぼ変化していません。"
        )


if pd.notna(bandwidth_change_5d):

    if bandwidth_change_5d > 0:

        st.write(
            "5営業日前との比較："
            "BandWidth は拡大方向です。"
        )

    elif bandwidth_change_5d < 0:

        st.write(
            "5営業日前との比較："
            "BandWidth は縮小方向です。"
        )

    else:

        st.write(
            "5営業日前との比較："
            "BandWidth はほぼ同水準です。"
        )


# ============================================================
# 125営業日 Squeeze 候補確認
# ============================================================

st.subheader(
    "⑤ スクイーズ研究用確認"
)

bw_min_125 = latest[
    "BandWidth_Min_125"
]


if pd.isna(bw_min_125):

    st.info(
        "125営業日のスクイーズ判定に必要な"
        "データがまだ不足しています。"
    )

else:

    distance_from_min = (
        (
            latest["BandWidth"]
            - bw_min_125
        )
        / bw_min_125
        * 100
        if bw_min_125 != 0
        else np.nan
    )

    st.write(
        "現在のBandWidth：",
        f"{format_number(latest['BandWidth'])}%",
    )

    st.write(
        "過去125営業日の最小BandWidth：",
        f"{format_number(bw_min_125)}%",
    )

    st.write(
        "125営業日最小値との差：",
        f"{format_number(distance_from_min)}%",
    )

    if (
        pd.notna(distance_from_min)
        and distance_from_min <= 0.01
    ):

        st.warning(
            "現在のBandWidthは、"
            "過去125営業日の最小水準です。"
            "スクイーズ研究候補として記録できます。"
        )

    else:

        st.info(
            "現在は過去125営業日の"
            "BandWidth最小値そのものではありません。"
        )


st.caption(
    "現段階ではスクイーズを売買シグナルには使用しません。"
    "まずGOOG・NVDAで実際の状態を確認します。"
)


# ============================================================
# 株価 + Bollinger Bands チャート
# ============================================================

st.divider()

st.subheader(
    "⑥ 株価とボリンジャーバンド"
)

chart_days = st.slider(
    "チャート表示営業日数",
    min_value=60,
    max_value=min(
        500,
        len(valid_df),
    ),
    value=min(
        250,
        len(valid_df),
    ),
    step=10,
)


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
# BandWidth チャート
# ============================================================

st.subheader(
    "⑦ BandWidth"
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
# 最新20営業日データ
# ============================================================

st.subheader(
    "⑧ 最新20営業日の確認"
)

display_df = (
    valid_df[
        [
            "Close",
            "BB_Upper",
            "BB_Middle",
            "BB_Lower",
            "BandWidth",
            "Lower_Distance_Close",
            "Lower_Distance_Low",
        ]
    ]
    .tail(20)
    .copy()
)

display_df.columns = [
    "終値",
    "BB上限",
    "BB中央線",
    "BB下限",
    "BandWidth %",
    "終値→BB下限 %",
    "安値→BB下限 %",
]

display_df = display_df.round(2)

st.dataframe(
    display_df,
    use_container_width=True,
)


# ============================================================
# 現段階の研究状態
# ============================================================

st.divider()

st.subheader(
    "⑨ 現在の研究段階"
)

st.write(
    "【実装済み】GOOG / NVDA 切り替え"
)

st.write(
    "【実装済み】株価データ取得"
)

st.write(
    "【実装済み】20日ボリンジャーバンド"
)

st.write(
    "【実装済み】BandWidth"
)

st.write(
    "【実装済み】BB下限との距離"
)

st.write(
    "【実装済み】BandWidth 縮小・拡大確認"
)

st.write(
    "【研究表示】125営業日BandWidth最小水準"
)

st.write(
    "【未実装】正式なスクイーズ分類"
)

st.write(
    "【未実装】BB下限からの下落停止判定"
)

st.write(
    "【未実装】反発開始判定"
)

st.write(
    "【未実装】1R 損切り"
)

st.write(
    "【未実装】1.5R / 2R 到達検証"
)

st.write(
    "【未実装】過去実績バックテスト"
)


# ============================================================
# 注意
# ============================================================

st.divider()

st.caption(
    "このプログラムは研究・検証用です。"
    "表示された情報だけで将来の株価上昇・下落を"
    "保証するものではありません。"
)
