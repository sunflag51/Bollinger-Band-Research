# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 1.1
#
# v1.1 追加内容
# ・125営業日 BandWidth 正規化
# ・公式Squeeze基準の確認
# ・研究用「低BandWidthゾーン」
# ・BandWidth 収縮 / 拡大分類
# ・Squeezeからの拡大開始候補
# ・過去の状態一覧
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

APP_VERSION = "1.1"

BB_PERIOD = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 125

# ------------------------------------------------------------
# 研究用の低BandWidthゾーン
#
# 0.00 = 過去125営業日の最低BandWidth
# 1.00 = 過去125営業日の最高BandWidth
#
# 0.20以下を「低BandWidthゾーン」として表示する。
#
# これはBollinger公式のSqueeze定義ではない。
# 今後GOOG/NVDAの過去実績を比較するための研究用分類。
# ------------------------------------------------------------

LOW_BANDWIDTH_ZONE = 0.20


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

    # Bollinger公式のpopulation standard deviationに合わせる
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

    # --------------------------------------------------------
    # 過去125営業日のBandWidth最低・最高
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 正規化BandWidth
    #
    # 0 = 125日最低
    # 1 = 125日最高
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BandWidth変化
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 公式Squeeze
    #
    # 現在のBandWidthが125期間最低値
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 研究用 低BandWidthゾーン
    #
    # 公式Squeezeとは別物
    # --------------------------------------------------------

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

    # 1日・3日・5日すべて縮小
    if (
        change_1d < 0
        and change_3d < 0
        and change_5d < 0
    ):
        return "収縮中"

    # 1日・3日・5日すべて拡大
    if (
        change_1d > 0
        and change_3d > 0
        and change_5d > 0
    ):
        return "拡大中"

    # 5日では縮小していたが、
    # 直近1日で拡大
    if (
        change_5d < 0
        and change_1d > 0
    ):
        return "拡大開始候補"

    # 5日では拡大していたが、
    # 直近1日で縮小
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

    df = calculate_bandwidth(df)

    df = calculate_lower_band_distance(df)

    df = calculate_bandwidth_state(
        df,
        SQUEEZE_LOOKBACK,
    )

    df["BandWidth_Direction"] = df.apply(
        classify_bandwidth_direction,
        axis=1,
    )

    df["Squeeze_State"] = df.apply(
        classify_squeeze_state,
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


# ============================================================
# タイトル
# ============================================================

st.title(
    "📊 GOOG・NVDA BB下限研究"
)

st.caption(
    f"Version {APP_VERSION} ｜ "
    "スクイーズ状態分類版"
)

st.info(
    "現在は研究段階です。"
    "スクイーズやBandWidthの状態を分類し、"
    "GOOG・NVDAの実際の値動きと一致しているか"
    "確認するためのプログラムです。"
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
# BB下限
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
# Squeeze
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
    "John Bollinger公式のSqueeze定義そのものではありません。"
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
# チャート
# ============================================================

st.divider()

st.subheader(
    "⑦ 株価とボリンジャーバンド"
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
    "⑧ BandWidth"
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
    "⑨ 正規化BandWidth"
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
# 過去状態一覧
# ============================================================

st.subheader(
    "⑩ 最新30営業日の状態確認"
)


display_df = (
    valid_df[
        [
            "Close",
            "BB_Lower",
            "Lower_Distance_Close",
            "BandWidth",
            "Normalized_BandWidth",
            "BandWidth_Direction",
            "Squeeze_State",
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
    }
)


numeric_columns = [
    "終値",
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
# 研究用集計
# ============================================================

st.subheader(
    "⑪ 現在取得している期間の分類件数"
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


    st.caption(
        "件数は売買成績ではありません。"
        "現段階では各状態がどの程度発生するかを"
        "確認するための数字です。"
    )


# ============================================================
# 現在の研究段階
# ============================================================

st.divider()

st.subheader(
    "⑫ 現在の研究段階"
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
    "【未実装】BB下限からの下落停止判定"
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
    "『公式Squeeze基準』と"
    "『研究用 低BandWidthゾーン』は別物です。"
    "研究用ゾーンは今後GOOG・NVDAの"
    "過去実績を比較するための仮分類であり、"
    "売買条件として正式採用したものではありません。"
)


st.caption(
    "このプログラムは研究・検証用です。"
    "表示された状態は将来の株価上昇・下落を"
    "保証するものではありません。"
)
