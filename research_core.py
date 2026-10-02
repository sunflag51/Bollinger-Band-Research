# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 4.0.0
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
# v2.0
# ・v1.9の意思決定結果を「なぜ差が出たか」に分解
# ・方針Bが見送ったイベントで、方針Aなら何Rだったかを集計
# ・反発待ち0/1/2/3営業日ごとに、A/BのR損益と差を集計
# ・B>A / A>B / 同じ の結果グループ別に平均R差を集計
# ・比較不可イベントを理由別に集計
# ・新しい売買条件は追加せず、v1.9の原因分解だけを行う
#
# v2.1
# ・下落停止シグナル確定時点で既に観測できた情報だけを比較
# ・方針BのEntryを「同日反発」と「後日反発」に分離
# ・同日反発を除外し、後日反発 vs 反発未確認・見送りを比較
# ・BB位置、BandWidth、価格反応などの数値特徴を比較
# ・BB状態、Squeeze、BandWidth方向などのカテゴリ/真偽特徴を比較
# ・未来情報を新しいEntry条件として使用せず、事前情報の記述統計だけを行う
#
# v2.2
# ・v2.1で「反発未確認・見送り」となったイベントだけを追跡
# ・固定イベント day0～day3 の終了後に、Close > Prev_High がいつ初めて成立したかを診断
# ・固定窓終了後1/2/3/5/10/20営業日以内の反発確認件数を表示
# ・day3で見送る設計が結果に強く依存していないかを確認
# ・固定窓終了後の反発は新しいEntry条件には使わず、観察窓感度の診断だけを行う
# v2.2.2: イベントID再照合を廃止し、イベント開始日＋固定3営業日から終了位置を直接決定
# v2.2.3: v1.6準備ループの valid_df 変数上書きを修正し、v2.2追跡は全日足 df を直接使用
#
# v2.3
# ・v2.2で固定窓終了後に反発確認した見送りイベントを研究対象化
# ・方針C = day3後も最大5日 / 10日待ち、初回反発確認後の翌営業日OpenでEntry
# ・方針CのStop = 元イベントday0から遅い反発確認日までの最安値
# ・1.5R / 2R、保有5 / 10 / 20営業日のR損益を既存ロジックで評価
# ・反発までに新規BBイベントが発生したケースを別集計
# ・方針Cは研究候補であり、正式売買ルールには採用しない
#
# v2.4
# ・v2.3で「反発までに新規BBイベントあり」となったケースのイベント連結を診断
# ・元イベント → 新規BBイベント → 遅い反発確認日の関係を明示
# ・遅い反発が新規BBイベント側の既存「最初の反発開始」と同一かを確認
# ・同一シグナルを元イベント由来と新イベント由来で二重計上しないための診断を追加
# ・同じEntry日でもStop起点が異なる場合のR設計差を表示
# ・新しいEntry条件は追加せず、イベント定義と二重計上だけを検証
#
# v2.6
# ・v2.5.1までの全機能を維持
# ・完了したBB下限イベントを「1イベント=1行」の独立イベント台帳へ統一
# ・固定day0～day3内の下落停止/反発開始だけを、そのイベント自身のシグナルとして記録
# ・固定窓後の遅い反発は元イベントへ追加せず、新しいBBイベントがあれば別IDとして扱う
# ・各イベントに20営業日・2Rの下落停止/反発開始R結果を横並びで記録
# ・イベントID重複、欠落、台帳行数を監査し、二重計上がないことを確認
# ・旧方針Cは診断履歴として残すが、独立イベント台帳の正式研究母集団には混ぜない
#
# v2.5.1
# ・新しいBB下限イベントが発生したら、旧イベントの追跡を終了して新イベントへリセット
# ・新イベントありは新イベント側の既存Rebound R設計を使用
# ・新イベントなしは旧イベントの遅い反発R設計を継続使用
# ・元イベントと新イベントの同一反発シグナルを1取引として扱い、二重計上を除去
# ・リセット後の1.5R / 2R、5 / 10 / 20営業日R損益を再計算
# ・v2.3旧イベント基準とv2.5リセット基準の20日2R差をイベント別に表示
# ・リセット方式は研究候補であり、正式売買ルールには採用しない
#
# v2.7
# ・v2.6までの全機能を維持
# ・Stop/Target到達日のOpenが価格水準を飛び越えたギャップを実約定差としてR損益へ反映
# ・StopギャップはOpen約定で-1Rを超える損失、TargetギャップはOpen約定で+Target Rを超える利益として計算
# ・日中にStop/Targetへ到達した場合は従来どおり設定水準で約定したものとして扱う
# ・期間末決済は従来どおり期間末Closeを使用
# ・旧ルールベースRとギャップ反映Rを並べ、差が出たイベントを個別表示
#
# v2.8
# ・v2.7までの全機能を維持
# ・EntryとExitの両方へ研究用スリッページ率を反映
# ・EntryとExitの両方へ研究用売買手数料率を反映
# ・ギャップ反映後のGross Rと、コスト控除後Net Rを同じ1R基準で比較
# ・手数料率 / スリッページ率は画面から変更可能
# ・20営業日・2Rについてイベント別のコストRとNet Rを表示
# ・コスト設定は研究仮定であり、特定証券会社の実コストを意味しない
#
# v2.9
# ・v2.8までの全機能を維持
# ・完了BBイベント母集団をイベント開始日順に前半 / 後半へ固定分割
# ・奇数件の場合は前半をfloor(N/2)、残りを後半とする
# ・シグナルごとに境界を作り直さず、共通の独立イベント母集団で同じ境界を使用
# ・5 / 10 / 20営業日・2RのNet Rを前半 / 後半で比較
# ・20営業日・2Rは前半→後半の差も表示
# ・過去5年全体を既に研究に使っているため、後半を真の未使用OOSとは呼ばない
# ・時系列安定性の診断であり、正式な売買条件の採用判定ではない
#
# v3.0
# ・v2.9までの全機能を維持
# ・GOOGとNVDAを同じ期間・同じBBイベント定義・同じEntry / Stop / Targetで同時計算
# ・v2.7のギャップ約定、v2.8の手数料・スリッページも両銘柄へ同じ設定で適用
# ・5 / 10 / 20営業日・2RのNet Rを銘柄別・シグナル別に並列比較
# ・各銘柄の独立イベント台帳行数、重複、シグナル数、R計算可能数を監査
# ・GOOGで見た結果を理由にNVDA側の条件を変更しない
# ・銘柄横断の再現性診断であり、正式な売買条件の採用判定ではない
#
# v3.4.1
# ・v3.3までの売買条件・コスト条件を固定したまま、時間方向の別5年間検証を追加
# ・評価窓を日付定数で完全固定し、実行日や最新データ日で母集団が動かないよう修正
# ・前5年 = 2016-10-01～2021-09-30、現5年 = 2021-10-01～2026-09-30
# ・各5年窓の前に400暦日のウォームアップを取得し、BB20日・BandWidth125日を評価開始前に計算
# ・ウォームアップ日は指標計算だけに使い、BBイベントID・Entry・損益の評価母集団には含めない
# ・GOOG / NVDA、下落停止 / 反発開始、5 / 10 / 20営業日、2R、ギャップ、コスト条件を変更しない
# ・前5年の結果を見て条件を変更せず、現5年との再現性だけを診断
# ・前5年は「未使用過去期間による時間方向の外部検証」であり、将来データによる前向きOOSではない
#
# 重要
# v3.0は日足ベースの研究用ネットR損益＋時系列安定性＋銘柄横断診断まで。
# 板・出来高・部分約定・税金・為替コストなどはまだ含めない。
# 正式な売買ルールはまだ確定しない。
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# v3.4.2
# ・研究条件・結果番号129～133はv3.4.1から変更しない
# ・Streamlitの再実行対策として、主要な計算結果をst.cache_dataへ保存
# ・固定5年検証はディスクキャッシュを使用し、同じ条件では再計算しない
# ・クイックコピーは選択だけで表示し、従来の「表示ボタン」を廃止して再実行回数を削減
# ・プログラムを main.py（画面）と research_core.py（研究計算）へ分割
#
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

APP_VERSION = "4.0.0"

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

# v2.2 固定イベント終了後の反発確認追跡
# 1営業日後 = 元イベントの day4
V22_POST_WINDOW_HORIZONS = [1, 2, 3, 5, 10, 20]
V22_MAX_FOLLOW_DAYS = 20

# v2.3 遅い反発を待つ研究用上限
V23_WAIT_LIMITS = [5, 10]


# ============================================================
# 株価データ
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
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
# v3.4.1 固定日付範囲の株価データ取得
# ============================================================

@st.cache_data(persist="disk", show_spinner=False)
def get_stock_data_range(
    ticker: str,
    start_date,
    end_date,
) -> pd.DataFrame:
    """start_date以上、end_date以下を取得する。yfinanceのendは排他的なので+1日する。"""
    try:
        start_ts = pd.Timestamp(start_date).normalize()
        end_ts = pd.Timestamp(end_date).normalize()
        if end_ts < start_ts:
            return pd.DataFrame()

        data = yf.download(
            ticker,
            start=start_ts.strftime("%Y-%m-%d"),
            end=(end_ts + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=False,
            progress=False,
            multi_level_index=False,
        )
        if data is None or data.empty:
            return pd.DataFrame()

        data = data.copy()
        if getattr(data.index, "tz", None) is not None:
            data.index = data.index.tz_localize(None)
        data.index = pd.to_datetime(data.index).normalize()

        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for column in required_columns:
            if column not in data.columns:
                return pd.DataFrame()
            data[column] = pd.to_numeric(data[column], errors="coerce")

        data = data.dropna(subset=["Open", "High", "Low", "Close"])
        return data.sort_index()

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
# v2.7
# ギャップ時の実約定差を反映したR損益
#
# first-hit判定では、Stop/TargetをOpenで飛び越えた場合に
# Observed_Hit_Priceへその日のOpenを既に保存している。
# v1.7は決済Rを常に-1R / +Target Rへ固定していたが、
# v2.7ではObserved_Hit_Priceを実約定価格としてR損益へ反映する。
#
# 注意：これは日足Openで約定できたという研究上の仮定。
# 手数料・スリッページ・板状況はまだ含めない。
# ============================================================

def calculate_gap_aware_r_pnl_results(
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
    results["Gap_Execution_Type"] = ""
    results["Gap_Price_Difference"] = np.nan

    for idx, row in results.iterrows():
        outcome = row.get("Outcome", "")
        target_price = row.get("Target_Price", np.nan)
        stop_price = row.get("Stop_Price", np.nan)
        entry_price = row.get("Entry_Price", np.nan)
        risk_1r = row.get("Risk_1R", np.nan)
        observed_hit = row.get("Observed_Hit_Price", np.nan)
        entry_date = row.get("Entry_Date", pd.NaT)
        horizon = row.get("Horizon", np.nan)

        if (
            outcome in ["Target先着", "Stop先着"]
            and pd.notna(entry_price)
            and pd.notna(risk_1r)
            and float(risk_1r) > 0
        ):
            if outcome == "Target先着":
                level_price = target_price
                normal_type = "Target決済"
            else:
                level_price = stop_price
                normal_type = "Stop決済"

            if pd.isna(level_price):
                results.at[idx, "Exit_Type"] = "決済価格計算不可"
                results.at[idx, "R_PnL_Status"] = "Stop/Target価格なし"
                continue

            # first-hitでOpenギャップならObserved_Hit_Price=Open、
            # 日中到達ならObserved_Hit_Price=設定水準。
            exit_price = (
                float(observed_hit)
                if pd.notna(observed_hit)
                else float(level_price)
            )

            price_diff = exit_price - float(level_price)
            tolerance = max(1e-10, abs(float(level_price)) * 1e-10)

            if outcome == "Stop先着" and exit_price < float(stop_price) - tolerance:
                gap_type = "Stopギャップ"
                exit_type = "StopギャップOpen決済"
            elif outcome == "Target先着" and exit_price > float(target_price) + tolerance:
                gap_type = "Targetギャップ"
                exit_type = "TargetギャップOpen決済"
            else:
                gap_type = "価格水準決済"
                exit_type = normal_type

            realized_r = (
                exit_price - float(entry_price)
            ) / float(risk_1r)

            results.at[idx, "Exit_Type"] = exit_type
            results.at[idx, "Exit_Date"] = row.get("Outcome_Date", pd.NaT)
            results.at[idx, "Exit_Price"] = exit_price
            results.at[idx, "Realized_R"] = float(realized_r)
            results.at[idx, "R_PnL_Valid"] = True
            results.at[idx, "R_PnL_Status"] = "ギャップ反映R損益計算可能"
            results.at[idx, "Gap_Execution_Type"] = gap_type
            results.at[idx, "Gap_Price_Difference"] = float(price_diff)
            continue

        if outcome == "同日両方到達・順序不明":
            results.at[idx, "Exit_Type"] = "順序不明"
            results.at[idx, "R_PnL_Status"] = "同日両方到達・順序不明"
            results.at[idx, "Gap_Execution_Type"] = "判定対象外"
            continue

        if outcome == "将来データ不足":
            results.at[idx, "Exit_Type"] = "データ不足"
            results.at[idx, "R_PnL_Status"] = "将来データ不足"
            results.at[idx, "Gap_Execution_Type"] = "判定対象外"
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

            exit_position = int(entry_position) + int(horizon) - 1
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
                float(exit_close) - float(entry_price)
            ) / float(risk_1r)
            results.at[idx, "Exit_Type"] = "期間末終値決済"
            results.at[idx, "Exit_Date"] = exit_date
            results.at[idx, "Exit_Price"] = float(exit_close)
            results.at[idx, "Realized_R"] = float(realized_r)
            results.at[idx, "R_PnL_Valid"] = True
            results.at[idx, "R_PnL_Status"] = "ギャップ反映R損益計算可能"
            results.at[idx, "Gap_Execution_Type"] = "期間末決済"
            results.at[idx, "Gap_Price_Difference"] = 0.0
            continue

        results.at[idx, "Exit_Type"] = "その他"
        results.at[idx, "R_PnL_Status"] = "未定義結果"

    return results


def build_v27_gap_comparison_summary(
    legacy_results: pd.DataFrame,
    gap_results: pd.DataFrame,
    signal_label: str,
) -> pd.DataFrame:
    rows = []
    if legacy_results is None or gap_results is None or legacy_results.empty or gap_results.empty:
        return pd.DataFrame()

    for horizon in FIRST_HIT_HORIZONS:
        old = legacy_results[pd.to_numeric(legacy_results["Horizon"], errors="coerce").eq(horizon)].copy()
        new = gap_results[pd.to_numeric(gap_results["Horizon"], errors="coerce").eq(horizon)].copy()

        old_valid = old[old["R_PnL_Valid"].eq(True)].copy()
        new_valid = new[new["R_PnL_Valid"].eq(True)].copy()
        old_r = pd.to_numeric(old_valid["Realized_R"], errors="coerce").dropna()
        new_r = pd.to_numeric(new_valid["Realized_R"], errors="coerce").dropna()

        stop_gap = int((new["Gap_Execution_Type"] == "Stopギャップ").sum())
        target_gap = int((new["Gap_Execution_Type"] == "Targetギャップ").sum())

        old_total = float(old_r.sum()) if not old_r.empty else np.nan
        new_total = float(new_r.sum()) if not new_r.empty else np.nan
        old_mean = float(old_r.mean()) if not old_r.empty else np.nan
        new_mean = float(new_r.mean()) if not new_r.empty else np.nan
        old_median = float(old_r.median()) if not old_r.empty else np.nan
        new_median = float(new_r.median()) if not new_r.empty else np.nan

        rows.append({
            "シグナル": signal_label,
            "保有期間": f"{horizon}営業日",
            "対象": len(new),
            "R損益計算可能": len(new_r),
            "Stopギャップ": stop_gap,
            "Targetギャップ": target_gap,
            "ギャップ合計": stop_gap + target_gap,
            "旧合計R": old_total,
            "ギャップ反映合計R": new_total,
            "合計R差": new_total - old_total if pd.notna(old_total) and pd.notna(new_total) else np.nan,
            "旧平均R": old_mean,
            "ギャップ反映平均R": new_mean,
            "平均R差": new_mean - old_mean if pd.notna(old_mean) and pd.notna(new_mean) else np.nan,
            "旧中央値R": old_median,
            "ギャップ反映中央値R": new_median,
        })

    return pd.DataFrame(rows)


def build_v27_gap_changed_detail(
    legacy_results: pd.DataFrame,
    gap_results: pd.DataFrame,
    signal_label: str,
    horizon: int = 20,
) -> pd.DataFrame:
    if legacy_results is None or gap_results is None or legacy_results.empty or gap_results.empty:
        return pd.DataFrame()

    old = legacy_results[pd.to_numeric(legacy_results["Horizon"], errors="coerce").eq(horizon)].copy()
    new = gap_results[pd.to_numeric(gap_results["Horizon"], errors="coerce").eq(horizon)].copy()

    old = old[["BB_Event_ID", "Realized_R", "Exit_Type", "Exit_Price"]].rename(columns={
        "Realized_R": "旧実現R",
        "Exit_Type": "旧決済",
        "Exit_Price": "旧決済価格",
    })
    new = new[[
        "BB_Event_ID", "Signal_Date", "Entry_Date", "Entry_Price", "Stop_Price",
        "Target_Price", "Outcome_Date", "Observed_Hit_Price", "Gap_Execution_Type",
        "Exit_Type", "Exit_Price", "Realized_R", "Risk_1R_Percent"
    ]].rename(columns={
        "Exit_Type": "ギャップ反映決済",
        "Exit_Price": "ギャップ反映決済価格",
        "Realized_R": "ギャップ反映実現R",
    })

    merged = new.merge(old, on="BB_Event_ID", how="left", validate="one_to_one")
    merged["R差"] = pd.to_numeric(merged["ギャップ反映実現R"], errors="coerce") - pd.to_numeric(merged["旧実現R"], errors="coerce")
    changed = merged[
        pd.to_numeric(merged["R差"], errors="coerce").abs().gt(1e-10)
    ].copy()

    if changed.empty:
        return pd.DataFrame(columns=[
            "シグナル", "イベントID", "シグナル日", "Entry日", "Entry価格", "1R率_%",
            "到達日", "ギャップ種別", "Stop", "Target", "観測Open/到達価格",
            "旧決済価格", "ギャップ反映決済価格", "旧実現R", "ギャップ反映実現R", "R差"
        ])

    changed.insert(0, "シグナル", signal_label)
    changed = changed.rename(columns={
        "BB_Event_ID": "イベントID",
        "Signal_Date": "シグナル日",
        "Entry_Date": "Entry日",
        "Entry_Price": "Entry価格",
        "Risk_1R_Percent": "1R率_%",
        "Outcome_Date": "到達日",
        "Gap_Execution_Type": "ギャップ種別",
        "Stop_Price": "Stop",
        "Target_Price": "Target",
        "Observed_Hit_Price": "観測Open/到達価格",
    })
    return changed[[
        "シグナル", "イベントID", "シグナル日", "Entry日", "Entry価格", "1R率_%",
        "到達日", "ギャップ種別", "Stop", "Target", "観測Open/到達価格",
        "旧決済価格", "ギャップ反映決済価格", "旧実現R", "ギャップ反映実現R", "R差"
    ]].sort_values(["シグナル", "イベントID"]).reset_index(drop=True)


# ============================================================
# v2.8
# 手数料・スリッページ反映後のNet R損益
#
# Gross Rはv2.7のギャップ反映Rをそのまま使用する。
# Net Rでは、買いEntryをスリッページ分だけ高く、
# 売りExitをスリッページ分だけ安くしたうえで、
# Entry / Exit双方の約定金額に手数料を課す。
#
# Net Rの分母は、従来から使っている計画時点のRisk_1R。
# これにより「元の1Rに対してコストが何Rを消費したか」を比較できる。
# ============================================================

def calculate_v28_net_cost_results(
    gap_results: pd.DataFrame,
    commission_rate: float,
    slippage_rate: float,
) -> pd.DataFrame:
    if gap_results is None or gap_results.empty:
        return pd.DataFrame()

    results = gap_results.copy()
    commission_rate = max(0.0, float(commission_rate))
    slippage_rate = max(0.0, float(slippage_rate))

    new_columns = {
        "Gross_Realized_R": np.nan,
        "Entry_Execution_Price": np.nan,
        "Exit_Execution_Price": np.nan,
        "Entry_Commission": np.nan,
        "Exit_Commission": np.nan,
        "Total_Commission": np.nan,
        "Slippage_Cost": np.nan,
        "Total_Cost_Amount": np.nan,
        "Cost_R": np.nan,
        "Net_PnL_Amount_Per_Share": np.nan,
        "Net_Realized_R": np.nan,
        "Net_R_Valid": False,
        "Net_R_Status": "計算不可",
    }
    for column, default in new_columns.items():
        results[column] = default

    for idx, row in results.iterrows():
        gross_valid = bool(row.get("R_PnL_Valid", False))
        raw_entry = pd.to_numeric(pd.Series([row.get("Entry_Price", np.nan)]), errors="coerce").iloc[0]
        raw_exit = pd.to_numeric(pd.Series([row.get("Exit_Price", np.nan)]), errors="coerce").iloc[0]
        risk_1r = pd.to_numeric(pd.Series([row.get("Risk_1R", np.nan)]), errors="coerce").iloc[0]
        gross_r = pd.to_numeric(pd.Series([row.get("Realized_R", np.nan)]), errors="coerce").iloc[0]

        if (
            not gross_valid
            or pd.isna(raw_entry)
            or pd.isna(raw_exit)
            or pd.isna(risk_1r)
            or float(risk_1r) <= 0
            or pd.isna(gross_r)
        ):
            results.at[idx, "Net_R_Status"] = row.get("R_PnL_Status", "計算不可")
            continue

        raw_entry = float(raw_entry)
        raw_exit = float(raw_exit)
        risk_1r = float(risk_1r)
        gross_r = float(gross_r)

        entry_execution = raw_entry * (1.0 + slippage_rate)
        exit_execution = raw_exit * (1.0 - slippage_rate)

        entry_commission = entry_execution * commission_rate
        exit_commission = exit_execution * commission_rate
        total_commission = entry_commission + exit_commission

        entry_slippage_cost = entry_execution - raw_entry
        exit_slippage_cost = raw_exit - exit_execution
        slippage_cost = entry_slippage_cost + exit_slippage_cost

        gross_pnl_amount = raw_exit - raw_entry
        net_pnl_amount = (
            exit_execution
            - entry_execution
            - entry_commission
            - exit_commission
        )
        total_cost_amount = gross_pnl_amount - net_pnl_amount
        cost_r = total_cost_amount / risk_1r
        net_r = net_pnl_amount / risk_1r

        results.at[idx, "Gross_Realized_R"] = gross_r
        results.at[idx, "Entry_Execution_Price"] = entry_execution
        results.at[idx, "Exit_Execution_Price"] = exit_execution
        results.at[idx, "Entry_Commission"] = entry_commission
        results.at[idx, "Exit_Commission"] = exit_commission
        results.at[idx, "Total_Commission"] = total_commission
        results.at[idx, "Slippage_Cost"] = slippage_cost
        results.at[idx, "Total_Cost_Amount"] = total_cost_amount
        results.at[idx, "Cost_R"] = cost_r
        results.at[idx, "Net_PnL_Amount_Per_Share"] = net_pnl_amount
        results.at[idx, "Net_Realized_R"] = net_r
        results.at[idx, "Net_R_Valid"] = True
        results.at[idx, "Net_R_Status"] = "コスト反映Net R計算可能"

    return results


def build_v28_cost_comparison_summary(
    net_results: pd.DataFrame,
    signal_label: str,
    commission_rate: float,
    slippage_rate: float,
) -> pd.DataFrame:
    if net_results is None or net_results.empty:
        return pd.DataFrame()

    rows = []
    for horizon in FIRST_HIT_HORIZONS:
        part = net_results[
            pd.to_numeric(net_results["Horizon"], errors="coerce").eq(horizon)
        ].copy()
        valid = part[part["Net_R_Valid"].eq(True)].copy()

        gross_r = pd.to_numeric(valid["Gross_Realized_R"], errors="coerce").dropna()
        net_r = pd.to_numeric(valid["Net_Realized_R"], errors="coerce").dropna()
        cost_r = pd.to_numeric(valid["Cost_R"], errors="coerce").dropna()

        gross_total = float(gross_r.sum()) if not gross_r.empty else np.nan
        net_total = float(net_r.sum()) if not net_r.empty else np.nan
        gross_mean = float(gross_r.mean()) if not gross_r.empty else np.nan
        net_mean = float(net_r.mean()) if not net_r.empty else np.nan
        gross_median = float(gross_r.median()) if not gross_r.empty else np.nan
        net_median = float(net_r.median()) if not net_r.empty else np.nan

        rows.append({
            "シグナル": signal_label,
            "保有期間": f"{horizon}営業日",
            "手数料_片道_%": commission_rate * 100.0,
            "スリッページ_片道_%": slippage_rate * 100.0,
            "R損益計算可能": len(net_r),
            "Gross合計R": gross_total,
            "Net合計R": net_total,
            "コスト合計R": float(cost_r.sum()) if not cost_r.empty else np.nan,
            "合計R差": net_total - gross_total if pd.notna(net_total) and pd.notna(gross_total) else np.nan,
            "Gross平均R": gross_mean,
            "Net平均R": net_mean,
            "平均R差": net_mean - gross_mean if pd.notna(net_mean) and pd.notna(gross_mean) else np.nan,
            "Gross中央値R": gross_median,
            "Net中央値R": net_median,
            "GrossプラスR": int((gross_r > 0).sum()),
            "NetプラスR": int((net_r > 0).sum()),
            "NetマイナスR": int((net_r < 0).sum()),
            "NetゼロR": int((net_r.abs() <= 1e-12).sum()),
        })

    return pd.DataFrame(rows)


def build_v28_cost_detail(
    net_results: pd.DataFrame,
    signal_label: str,
    horizon: int = 20,
) -> pd.DataFrame:
    if net_results is None or net_results.empty:
        return pd.DataFrame()

    part = net_results[
        pd.to_numeric(net_results["Horizon"], errors="coerce").eq(horizon)
        & net_results["Net_R_Valid"].eq(True)
    ].copy()
    if part.empty:
        return pd.DataFrame()

    detail = pd.DataFrame({
        "シグナル": signal_label,
        "イベントID": part["BB_Event_ID"].values,
        "Entry日": part["Entry_Date"].values,
        "Exit日": part["Exit_Date"].values,
        "決済種別": part["Exit_Type"].values,
        "Entry元価格": pd.to_numeric(part["Entry_Price"], errors="coerce").values,
        "Entryコスト反映価格": pd.to_numeric(part["Entry_Execution_Price"], errors="coerce").values,
        "Exit元価格": pd.to_numeric(part["Exit_Price"], errors="coerce").values,
        "Exitコスト反映価格": pd.to_numeric(part["Exit_Execution_Price"], errors="coerce").values,
        "1R率_%": pd.to_numeric(part["Risk_1R_Percent"], errors="coerce").values,
        "手数料合計_1株": pd.to_numeric(part["Total_Commission"], errors="coerce").values,
        "スリッページ合計_1株": pd.to_numeric(part["Slippage_Cost"], errors="coerce").values,
        "コストR": pd.to_numeric(part["Cost_R"], errors="coerce").values,
        "Gross実現R": pd.to_numeric(part["Gross_Realized_R"], errors="coerce").values,
        "Net実現R": pd.to_numeric(part["Net_Realized_R"], errors="coerce").values,
    })
    detail["R差"] = detail["Net実現R"] - detail["Gross実現R"]
    return detail.sort_values(["シグナル", "イベントID"]).reset_index(drop=True)


# ============================================================
# v2.9
# 独立BBイベント母集団の固定時系列分割
#
# 重要:
# ・分割境界はシグナル成績を見て決めない。
# ・v2.6の独立イベント台帳をイベント開始日順に並べ、
#   前半=floor(N/2)、後半=残り と機械的に分ける。
# ・下落停止 / 反発開始で別々の境界を作らない。
# ============================================================

def build_v29_time_split_master(ledger: pd.DataFrame):
    if ledger is None or ledger.empty:
        return pd.DataFrame(), pd.DataFrame()

    master = ledger[["イベントID", "イベント開始日"]].copy()
    master["イベントID"] = pd.to_numeric(master["イベントID"], errors="coerce")
    master["イベント開始日"] = pd.to_datetime(master["イベント開始日"], errors="coerce")
    master = (
        master.dropna(subset=["イベントID", "イベント開始日"])
        .drop_duplicates(subset=["イベントID"], keep="first")
        .sort_values(["イベント開始日", "イベントID"])
        .reset_index(drop=True)
    )
    if master.empty:
        return master, pd.DataFrame()

    master["イベントID"] = master["イベントID"].astype(int)
    total = len(master)
    first_count = total // 2
    master["時系列区分"] = "後半"
    if first_count > 0:
        master.loc[: first_count - 1, "時系列区分"] = "前半"

    audit_rows = []
    for label in ["前半", "後半"]:
        part = master[master["時系列区分"].eq(label)].copy()
        if part.empty:
            audit_rows.append({
                "時系列区分": label,
                "母集団イベント数": 0,
                "最初のイベントID": np.nan,
                "最後のイベントID": np.nan,
                "開始日": pd.NaT,
                "終了日": pd.NaT,
            })
        else:
            audit_rows.append({
                "時系列区分": label,
                "母集団イベント数": len(part),
                "最初のイベントID": int(part.iloc[0]["イベントID"]),
                "最後のイベントID": int(part.iloc[-1]["イベントID"]),
                "開始日": part["イベント開始日"].min(),
                "終了日": part["イベント開始日"].max(),
            })

    audit = pd.DataFrame(audit_rows)
    audit["全イベント数"] = total
    audit["分割方式"] = "イベント開始日順・前半=floor(N/2)・後半=残り"
    return master, audit


def build_v29_time_split_net_summary(
    net_results: pd.DataFrame,
    split_master: pd.DataFrame,
    signal_label: str,
) -> pd.DataFrame:
    if (
        net_results is None or net_results.empty
        or split_master is None or split_master.empty
    ):
        return pd.DataFrame()

    work = net_results.copy()
    work["BB_Event_ID"] = pd.to_numeric(work["BB_Event_ID"], errors="coerce")
    split = split_master[["イベントID", "時系列区分"]].copy()
    split["イベントID"] = pd.to_numeric(split["イベントID"], errors="coerce")
    work = work.merge(
        split,
        left_on="BB_Event_ID",
        right_on="イベントID",
        how="left",
        validate="many_to_one",
    )

    rows = []
    for horizon in FIRST_HIT_HORIZONS:
        horizon_part = work[
            pd.to_numeric(work["Horizon"], errors="coerce").eq(horizon)
        ].copy()
        for period_label in ["前半", "後半"]:
            part = horizon_part[horizon_part["時系列区分"].eq(period_label)].copy()
            valid = part[part["Net_R_Valid"].eq(True)].copy()
            net_r = pd.to_numeric(valid["Net_Realized_R"], errors="coerce").dropna()
            gross_r = pd.to_numeric(valid["Gross_Realized_R"], errors="coerce").dropna()
            cost_r = pd.to_numeric(valid["Cost_R"], errors="coerce").dropna()
            population_count = int(split_master["時系列区分"].eq(period_label).sum())

            rows.append({
                "シグナル": signal_label,
                "保有期間": f"{horizon}営業日",
                "時系列区分": period_label,
                "母集団イベント": population_count,
                "シグナル対象": len(part),
                "Net_R計算可能": len(net_r),
                "Gross合計R": float(gross_r.sum()) if not gross_r.empty else np.nan,
                "Net合計R": float(net_r.sum()) if not net_r.empty else np.nan,
                "コスト合計R": float(cost_r.sum()) if not cost_r.empty else np.nan,
                "Net平均R": float(net_r.mean()) if not net_r.empty else np.nan,
                "Net中央値R": float(net_r.median()) if not net_r.empty else np.nan,
                "NetプラスR": int((net_r > 0).sum()),
                "NetマイナスR": int((net_r < 0).sum()),
                "NetゼロR": int((net_r.abs() <= 1e-12).sum()),
            })

    return pd.DataFrame(rows)


def build_v29_20d_difference(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty:
        return pd.DataFrame()

    part = summary[summary["保有期間"].eq("20営業日")].copy()
    rows = []
    for signal_label in ["下落停止", "反発開始"]:
        signal = part[part["シグナル"].eq(signal_label)].copy()
        early = signal[signal["時系列区分"].eq("前半")]
        late = signal[signal["時系列区分"].eq("後半")]
        if early.empty or late.empty:
            continue
        e = early.iloc[0]
        l = late.iloc[0]
        rows.append({
            "シグナル": signal_label,
            "前半_Net_R計算可能": int(e["Net_R計算可能"]),
            "後半_Net_R計算可能": int(l["Net_R計算可能"]),
            "前半_Net合計R": e["Net合計R"],
            "後半_Net合計R": l["Net合計R"],
            "前半_Net平均R": e["Net平均R"],
            "後半_Net平均R": l["Net平均R"],
            "平均R差_後半-前半": (
                float(l["Net平均R"]) - float(e["Net平均R"])
                if pd.notna(l["Net平均R"]) and pd.notna(e["Net平均R"]) else np.nan
            ),
            "前半_Net中央値R": e["Net中央値R"],
            "後半_Net中央値R": l["Net中央値R"],
            "前半_プラスR": int(e["NetプラスR"]),
            "後半_プラスR": int(l["NetプラスR"]),
            "前半_マイナスR": int(e["NetマイナスR"]),
            "後半_マイナスR": int(l["NetマイナスR"]),
        })
    return pd.DataFrame(rows)


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
# v2.0
# v1.9 意思決定差の原因分解
# ============================================================

def build_v20_skip_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    if results is None or results.empty:
        return pd.DataFrame()

    rows = []

    for horizon in FIRST_HIT_HORIZONS:
        part = results[
            (results["Horizon"] == int(horizon))
            & (~results["Policy_B_Has_Rebound"])
        ].copy()

        if part.empty:
            continue

        a_valid = part[part["Policy_A_R_Valid"].eq(True)].copy()
        a_r = pd.to_numeric(a_valid["Policy_A_R"], errors="coerce").dropna()

        rows.append(
            {
                "保有期間": f"{horizon}営業日",
                "方針B見送り": len(part),
                "方針A_R計算可能": len(a_r),
                "方針A合計R": float(a_r.sum()) if not a_r.empty else np.nan,
                "方針A平均R": float(a_r.mean()) if not a_r.empty else np.nan,
                "方針A中央値R": float(a_r.median()) if not a_r.empty else np.nan,
                "方針AプラスR": int((a_r > 0).sum()),
                "方針AマイナスR": int((a_r < 0).sum()),
                "方針AゼロR": int(np.isclose(a_r, 0.0).sum()),
                "方針A_Target決済": int((part["Policy_A_Exit_Type"] == "Target決済").sum()),
                "方針A_Stop決済": int((part["Policy_A_Exit_Type"] == "Stop決済").sum()),
                "方針A_期間末決済": int((part["Policy_A_Exit_Type"] == "期間末終値決済").sum()),
                "方針A_比較不可": int((~part["Policy_A_R_Valid"].eq(True)).sum()),
            }
        )

    return pd.DataFrame(rows)


def build_v20_wait_day_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    if results is None or results.empty:
        return pd.DataFrame()

    rows = []

    for horizon in FIRST_HIT_HORIZONS:
        entered = results[
            (results["Horizon"] == int(horizon))
            & results["Policy_B_Has_Rebound"]
        ].copy()

        if entered.empty:
            continue

        waits = pd.to_numeric(
            entered["Wait_Rebound_Days_From_Stop"],
            errors="coerce",
        )
        entered = entered[waits.notna()].copy()
        entered["Wait_Days_Int"] = pd.to_numeric(
            entered["Wait_Rebound_Days_From_Stop"], errors="coerce"
        ).astype(int)

        for wait_days in sorted(entered["Wait_Days_Int"].unique()):
            group = entered[entered["Wait_Days_Int"] == int(wait_days)].copy()
            valid = group[group["Decision_Comparison_Valid"]].copy()

            a_r = pd.to_numeric(valid["Policy_A_R"], errors="coerce").dropna()
            b_r = pd.to_numeric(valid["Policy_B_Trade_R"], errors="coerce").dropna()
            diff = pd.to_numeric(
                valid["Decision_R_Difference_B_Minus_A"], errors="coerce"
            ).dropna()

            rows.append(
                {
                    "保有期間": f"{horizon}営業日",
                    "待ち営業日": int(wait_days),
                    "方針B_Entry": len(group),
                    "比較可能": len(valid),
                    "方針A平均R": float(a_r.mean()) if not a_r.empty else np.nan,
                    "方針B平均R": float(b_r.mean()) if not b_r.empty else np.nan,
                    "平均R差_B-A": float(diff.mean()) if not diff.empty else np.nan,
                    "中央値R差_B-A": float(diff.median()) if not diff.empty else np.nan,
                    "方針Bが高い": int((valid["Decision_Result"] == "方針Bが高い").sum()),
                    "方針Aが高い": int((valid["Decision_Result"] == "方針Aが高い").sum()),
                    "同じ": int((valid["Decision_Result"] == "同じ").sum()),
                    "比較不可": int((~group["Decision_Comparison_Valid"]).sum()),
                }
            )

    return pd.DataFrame(rows)


def build_v20_difference_group_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    if results is None or results.empty:
        return pd.DataFrame()

    rows = []
    group_order = ["方針Bが高い", "方針Aが高い", "同じ"]

    for horizon in FIRST_HIT_HORIZONS:
        part = results[
            (results["Horizon"] == int(horizon))
            & results["Decision_Comparison_Valid"]
        ].copy()

        for group_name in group_order:
            group = part[part["Decision_Result"] == group_name].copy()
            if group.empty:
                continue

            a_r = pd.to_numeric(group["Policy_A_R"], errors="coerce").dropna()
            b_r = pd.to_numeric(group["Policy_B_Opportunity_R"], errors="coerce").dropna()
            diff = pd.to_numeric(
                group["Decision_R_Difference_B_Minus_A"], errors="coerce"
            ).dropna()

            rows.append(
                {
                    "保有期間": f"{horizon}営業日",
                    "結果グループ": group_name,
                    "イベント数": len(group),
                    "方針B_Entry": int(group["Policy_B_Has_Rebound"].sum()),
                    "方針B_見送り": int((~group["Policy_B_Has_Rebound"]).sum()),
                    "方針A平均R": float(a_r.mean()) if not a_r.empty else np.nan,
                    "方針B機会平均R": float(b_r.mean()) if not b_r.empty else np.nan,
                    "平均R差_B-A": float(diff.mean()) if not diff.empty else np.nan,
                    "中央値R差_B-A": float(diff.median()) if not diff.empty else np.nan,
                }
            )

    return pd.DataFrame(rows)


def v20_unavailable_reason(row: pd.Series) -> str:

    if bool(row.get("Decision_Comparison_Valid", False)):
        return "比較可能"

    if not bool(row.get("Stop_R_Valid", False)):
        status = row.get("Stop_R_Status", "")
        return f"方針A_R設計不可: {status}"

    if not bool(row.get("Policy_A_R_Valid", False)):
        status = row.get("Policy_A_R_Status", "")
        if pd.isna(status) or str(status).strip() == "":
            status = "結果なし"
        return f"方針A_R損益不可: {status}"

    has_rebound = bool(row.get("Policy_B_Has_Rebound", False))
    if not has_rebound:
        return "見送りは比較可能のはず・要確認"

    if not bool(row.get("WaitRebound_R_Valid", False)):
        status = row.get("WaitRebound_R_Status", "")
        return f"方針B_R設計不可: {status}"

    if not bool(row.get("Policy_B_Trade_R_Valid", False)):
        status = row.get("Policy_B_Trade_R_Status", "")
        if pd.isna(status) or str(status).strip() == "":
            status = "結果なし"
        return f"方針B_R損益不可: {status}"

    return "理由未分類・要確認"


def build_v20_unavailable_summary(
    results: pd.DataFrame,
) -> pd.DataFrame:

    if results is None or results.empty:
        return pd.DataFrame()

    rows = []

    for horizon in FIRST_HIT_HORIZONS:
        part = results[results["Horizon"] == int(horizon)].copy()
        unavailable = part[~part["Decision_Comparison_Valid"]].copy()

        if unavailable.empty:
            rows.append(
                {
                    "保有期間": f"{horizon}営業日",
                    "比較不可理由": "なし",
                    "件数": 0,
                    "イベントID": "",
                }
            )
            continue

        unavailable["Unavailable_Reason"] = unavailable.apply(
            v20_unavailable_reason,
            axis=1,
        )

        for reason, group in unavailable.groupby("Unavailable_Reason", dropna=False):
            ids = ",".join(
                str(int(x))
                for x in pd.to_numeric(group["BB_Event_ID"], errors="coerce").dropna()
            )
            rows.append(
                {
                    "保有期間": f"{horizon}営業日",
                    "比較不可理由": str(reason),
                    "件数": len(group),
                    "イベントID": ids,
                }
            )

    return pd.DataFrame(rows)


def make_v20_copy_text(title: str, df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + df.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.1
# 下落停止シグナル時点の事前情報比較
# ============================================================

V21_NUMERIC_FEATURES = [
    ("イベント開始からの日数", "Days_From_BB_Event_Start"),
    ("終値-BB下限距離_%", "Lower_Distance_Close"),
    ("安値-BB下限距離_%", "Lower_Distance_Low"),
    ("BandWidth_%", "BandWidth"),
    ("正規化BandWidth_0to1", "Normalized_BandWidth"),
    ("BandWidth変化_1D", "BandWidth_Change_1D"),
    ("BandWidth変化_3D", "BandWidth_Change_3D"),
    ("BandWidth変化_5D", "BandWidth_Change_5D"),
    ("終値-BB中央距離_%", "V21_Close_vs_BB_Middle_Pct"),
    ("終値-前日高値距離_%", "V21_Close_vs_Prev_High_Pct"),
    ("終値前日比_%", "V21_Close_vs_Prev_Close_Pct"),
    ("安値前日比_%", "V21_Low_vs_Prev_Low_Pct"),
    ("ローソク実体_%", "V21_Candle_Body_Pct"),
    ("日中レンジ内終値位置_%", "V21_Close_Location_In_Range_Pct"),
]

V21_BOOLEAN_FEATURES = [
    ("BB下限を下抜け後にBB内復帰", "BB_Lower_Reclaim"),
    ("BB下限より下で終値", "BB_Lower_Close_Below"),
    ("陽線", "Bullish_Candle"),
    ("低BandWidthゾーン", "Low_BandWidth_Zone"),
    ("公式Squeeze基準", "Official_Squeeze"),
    ("前日が低BandWidthゾーン", "Prev_Low_BandWidth_Zone"),
    ("低BWから下方向拡大候補", "Downside_Expansion_Candidate"),
]

V21_CATEGORY_FEATURES = [
    ("下落停止時BB状態", "First_Stop_BB_State"),
    ("BandWidth方向", "BandWidth_Direction"),
    ("Squeeze状態", "Squeeze_State"),
    ("下方向拡大状態", "Downside_Expansion_State"),
]


def build_v21_signal_dataset(
    stop_rows: pd.DataFrame,
    wait_rebound_rows: pd.DataFrame,
) -> pd.DataFrame:
    """Completed eventの最初の下落停止行だけを1イベント1行にする。

    説明変数はすべて下落停止シグナル日の終値確定時点までの値。
    結果ラベルだけが、その後固定イベント終了まで反発条件が出たかを表す。
    """

    if stop_rows is None or stop_rows.empty:
        return pd.DataFrame()

    base = stop_rows.copy()
    base = base.dropna(subset=["BB_Event_ID"]).copy()
    base["BB_Event_ID"] = base["BB_Event_ID"].astype(int)
    base["V21_Stop_Signal_Date"] = base.index

    wait_map = {}
    if wait_rebound_rows is not None and not wait_rebound_rows.empty:
        for idx, row in wait_rebound_rows.iterrows():
            event_id = row.get("BB_Event_ID", np.nan)
            if pd.isna(event_id):
                continue
            wait_map[int(event_id)] = {
                "date": idx,
                "days": row.get("Wait_Rebound_Days_From_Stop", np.nan),
            }

    groups = []
    rebound_dates = []
    wait_days_list = []

    for _, row in base.iterrows():
        event_id = int(row["BB_Event_ID"])
        info = wait_map.get(event_id)

        if info is None:
            groups.append("反発未確認・見送り")
            rebound_dates.append(pd.NaT)
            wait_days_list.append(np.nan)
            continue

        wait_days = pd.to_numeric(pd.Series([info["days"]]), errors="coerce").iloc[0]
        rebound_dates.append(info["date"])
        wait_days_list.append(wait_days)

        if pd.notna(wait_days) and int(wait_days) == 0:
            groups.append("同日反発確認")
        else:
            groups.append("後日反発確認")

    base["V21_Outcome_Group"] = groups
    base["V21_Rebound_Confirm_Date"] = rebound_dates
    base["V21_Wait_Days"] = wait_days_list

    def pct(numerator, denominator):
        num = pd.to_numeric(numerator, errors="coerce")
        den = pd.to_numeric(denominator, errors="coerce")
        return np.where(den != 0, num / den * 100.0, np.nan)

    base["V21_Close_vs_BB_Middle_Pct"] = pct(
        base["Close"] - base["BB_Middle"], base["BB_Middle"]
    )
    base["V21_Close_vs_Prev_High_Pct"] = pct(
        base["Close"] - base["Prev_High"], base["Prev_High"]
    )
    base["V21_Close_vs_Prev_Close_Pct"] = pct(
        base["Close"] - base["Prev_Close"], base["Prev_Close"]
    )
    base["V21_Low_vs_Prev_Low_Pct"] = pct(
        base["Low"] - base["Prev_Low"], base["Prev_Low"]
    )
    base["V21_Candle_Body_Pct"] = pct(
        base["Close"] - base["Open"], base["Open"]
    )

    daily_range = pd.to_numeric(base["High"], errors="coerce") - pd.to_numeric(
        base["Low"], errors="coerce"
    )
    base["V21_Close_Location_In_Range_Pct"] = np.where(
        daily_range > 0,
        (
            pd.to_numeric(base["Close"], errors="coerce")
            - pd.to_numeric(base["Low"], errors="coerce")
        )
        / daily_range
        * 100.0,
        np.nan,
    )

    return base.sort_values("BB_Event_ID").reset_index(drop=True)


def build_v21_group_count_summary(signal_df: pd.DataFrame) -> pd.DataFrame:
    if signal_df is None or signal_df.empty:
        return pd.DataFrame()

    order = ["同日反発確認", "後日反発確認", "反発未確認・見送り"]
    total = len(signal_df)
    rows = []

    for group in order:
        count = int((signal_df["V21_Outcome_Group"] == group).sum())
        rows.append(
            {
                "結果グループ": group,
                "イベント数": count,
                "全下落停止に占める割合_%": (count / total * 100.0) if total else np.nan,
            }
        )

    return pd.DataFrame(rows)


def build_v21_numeric_summary(signal_df: pd.DataFrame) -> pd.DataFrame:
    """同日反発を除外し、後日反発6件 vs 見送り12件を記述比較する。"""

    if signal_df is None or signal_df.empty:
        return pd.DataFrame()

    later = signal_df[signal_df["V21_Outcome_Group"] == "後日反発確認"].copy()
    skip = signal_df[signal_df["V21_Outcome_Group"] == "反発未確認・見送り"].copy()

    rows = []
    for label, col in V21_NUMERIC_FEATURES:
        if col not in signal_df.columns:
            continue

        a = pd.to_numeric(later[col], errors="coerce").dropna()
        b = pd.to_numeric(skip[col], errors="coerce").dropna()

        rows.append(
            {
                "事前情報": label,
                "後日反発_n": len(a),
                "後日反発_平均": float(a.mean()) if not a.empty else np.nan,
                "後日反発_中央値": float(a.median()) if not a.empty else np.nan,
                "見送り_n": len(b),
                "見送り_平均": float(b.mean()) if not b.empty else np.nan,
                "見送り_中央値": float(b.median()) if not b.empty else np.nan,
                "平均差_後日反発-見送り": (
                    float(a.mean() - b.mean()) if (not a.empty and not b.empty) else np.nan
                ),
            }
        )

    return pd.DataFrame(rows)


def build_v21_boolean_summary(signal_df: pd.DataFrame) -> pd.DataFrame:
    if signal_df is None or signal_df.empty:
        return pd.DataFrame()

    later = signal_df[signal_df["V21_Outcome_Group"] == "後日反発確認"].copy()
    skip = signal_df[signal_df["V21_Outcome_Group"] == "反発未確認・見送り"].copy()

    rows = []
    for label, col in V21_BOOLEAN_FEATURES:
        if col not in signal_df.columns:
            continue

        later_true = int(later[col].eq(True).sum())
        skip_true = int(skip[col].eq(True).sum())
        later_n = len(later)
        skip_n = len(skip)
        later_rate = later_true / later_n * 100.0 if later_n else np.nan
        skip_rate = skip_true / skip_n * 100.0 if skip_n else np.nan

        rows.append(
            {
                "事前情報": label,
                "後日反発_該当": later_true,
                "後日反発_n": later_n,
                "後日反発_該当率_%": later_rate,
                "見送り_該当": skip_true,
                "見送り_n": skip_n,
                "見送り_該当率_%": skip_rate,
                "該当率差_後日反発-見送り_pp": (
                    later_rate - skip_rate
                    if pd.notna(later_rate) and pd.notna(skip_rate)
                    else np.nan
                ),
            }
        )

    return pd.DataFrame(rows)


def build_v21_category_summary(signal_df: pd.DataFrame) -> pd.DataFrame:
    if signal_df is None or signal_df.empty:
        return pd.DataFrame()

    core = signal_df[
        signal_df["V21_Outcome_Group"].isin(["後日反発確認", "反発未確認・見送り"])
    ].copy()

    later_n = int((core["V21_Outcome_Group"] == "後日反発確認").sum())
    skip_n = int((core["V21_Outcome_Group"] == "反発未確認・見送り").sum())
    rows = []

    for feature_label, col in V21_CATEGORY_FEATURES:
        if col not in core.columns:
            continue

        categories = [str(x) for x in core[col].dropna().astype(str).unique()]
        categories = sorted(categories)

        for category in categories:
            later_count = int(
                (
                    (core["V21_Outcome_Group"] == "後日反発確認")
                    & (core[col].astype(str) == category)
                ).sum()
            )
            skip_count = int(
                (
                    (core["V21_Outcome_Group"] == "反発未確認・見送り")
                    & (core[col].astype(str) == category)
                ).sum()
            )
            later_rate = later_count / later_n * 100.0 if later_n else np.nan
            skip_rate = skip_count / skip_n * 100.0 if skip_n else np.nan

            rows.append(
                {
                    "事前情報": feature_label,
                    "状態": category,
                    "後日反発_件数": later_count,
                    "後日反発_割合_%": later_rate,
                    "見送り_件数": skip_count,
                    "見送り_割合_%": skip_rate,
                    "割合差_後日反発-見送り_pp": (
                        later_rate - skip_rate
                        if pd.notna(later_rate) and pd.notna(skip_rate)
                        else np.nan
                    ),
                }
            )

    return pd.DataFrame(rows)


def make_v21_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.2
# 固定イベント終了後の反発確認追跡
# ============================================================

def build_v22_post_window_rebound_tracking(
    data: pd.DataFrame,
    signal_df: pd.DataFrame,
    max_follow_days: int = 20,
) -> pd.DataFrame:
    """v2.1で見送りとなったイベントを、固定イベント終了後だけ追跡する。

    反発条件は既存と同じ Close > Prev_High。
    v2.2.3では全日足data上で、イベント開始日の実データ位置を
    day0として observation_days=3 行先を固定窓終了位置にする。
    """

    if data is None or data.empty or signal_df is None or signal_df.empty:
        return pd.DataFrame()

    skip = signal_df[
        signal_df["V21_Outcome_Group"] == "反発未確認・見送り"
    ].copy()

    if skip.empty:
        return pd.DataFrame()

    max_follow_days = max(1, int(max_follow_days))
    row_count = len(data)
    rows = []

    # 日付型・timezone差に左右されず、同じ取引日を実データ上で探す。
    index_timestamps = pd.to_datetime(pd.Index(data.index), errors="coerce")

    def resolve_position(date_value):
        ts = pd.to_datetime(date_value, errors="coerce")
        if pd.isna(ts):
            return None
        target_date = ts.date()
        for pos, idx_ts in enumerate(index_timestamps):
            if pd.notna(idx_ts) and idx_ts.date() == target_date:
                return int(pos)
        return None

    for _, signal_row in skip.iterrows():
        event_id_value = signal_row.get("BB_Event_ID", np.nan)
        if pd.isna(event_id_value):
            continue

        event_id = int(event_id_value)
        stop_date = pd.to_datetime(
            signal_row.get("V21_Stop_Signal_Date", pd.NaT),
            errors="coerce",
        )
        event_start_date = pd.to_datetime(
            signal_row.get("BB_Event_Start_Date", pd.NaT),
            errors="coerce",
        )

        # v2.2.3: 全日足dataを前提に固定窓位置を直接決定。
        # 固定イベントは day0～day3。BB_Event_ID の再照合ではなく、
        # イベント開始日の実データ位置 + 3営業日を終了位置とする。
        start_position = resolve_position(event_start_date)
        if start_position is None:
            rows.append(
                {
                    "BB_Event_ID": event_id,
                    "V22_Event_Start_Date": event_start_date,
                    "V22_Stop_Signal_Date": stop_date,
                    "V22_Event_End_Date": pd.NaT,
                    "V22_First_Rebound_Date": pd.NaT,
                    "V22_Days_After_Event_End": np.nan,
                    "V22_Days_From_Event_Start": np.nan,
                    "V22_Days_From_Stop": np.nan,
                    "V22_Available_Follow_Days": 0,
                    "V22_20D_Status": "イベント開始位置取得不可",
                    "V22_New_BB_Event_Before_Rebound": np.nan,
                    "V22_New_BB_Event_Count_To_Check_End": np.nan,
                }
            )
            continue

        end_position = start_position + LOWER_EVENT_OBSERVATION_DAYS
        if end_position >= row_count:
            rows.append(
                {
                    "BB_Event_ID": event_id,
                    "V22_Event_Start_Date": event_start_date,
                    "V22_Stop_Signal_Date": stop_date,
                    "V22_Event_End_Date": pd.NaT,
                    "V22_First_Rebound_Date": pd.NaT,
                    "V22_Days_After_Event_End": np.nan,
                    "V22_Days_From_Event_Start": np.nan,
                    "V22_Days_From_Stop": np.nan,
                    "V22_Available_Follow_Days": 0,
                    "V22_20D_Status": "固定イベント未完了",
                    "V22_New_BB_Event_Before_Rebound": np.nan,
                    "V22_New_BB_Event_Count_To_Check_End": np.nan,
                }
            )
            continue

        event_end_date = data.index[end_position]
        available_follow_days = max(0, row_count - end_position - 1)
        search_days = min(max_follow_days, available_follow_days)
        search_end_position = end_position + search_days

        rebound_position = None
        for position in range(end_position + 1, search_end_position + 1):
            if bool(data.iloc[position].get("Close_Above_Prev_High", False)):
                rebound_position = int(position)
                break

        first_rebound_date = pd.NaT
        days_after_end = np.nan
        days_from_event_start = np.nan
        days_from_stop = np.nan

        if rebound_position is not None:
            first_rebound_date = data.index[rebound_position]
            days_after_end = int(rebound_position - end_position)
            days_from_event_start = int(rebound_position - start_position)

            stop_position = resolve_position(stop_date)
            if stop_position is not None:
                days_from_stop = int(rebound_position - stop_position)

            status = "固定窓終了後20営業日以内に反発確認"
            count_end_position = rebound_position
        else:
            if available_follow_days >= max_follow_days:
                status = "固定窓終了後20営業日以内に反発なし"
            else:
                status = "追跡データ不足・反発未確認"
            count_end_position = search_end_position

        if count_end_position >= end_position + 1:
            follow_slice = data.iloc[end_position + 1 : count_end_position + 1]
            new_event_count = int(
                follow_slice.get(
                    "New_BB_Lower_Event",
                    pd.Series(False, index=follow_slice.index),
                ).eq(True).sum()
            )
        else:
            new_event_count = 0

        rows.append(
            {
                "BB_Event_ID": event_id,
                "V22_Event_Start_Date": event_start_date,
                "V22_Stop_Signal_Date": stop_date,
                "V22_Event_End_Date": event_end_date,
                "V22_First_Rebound_Date": first_rebound_date,
                "V22_Days_After_Event_End": days_after_end,
                "V22_Days_From_Event_Start": days_from_event_start,
                "V22_Days_From_Stop": days_from_stop,
                "V22_Available_Follow_Days": int(
                    min(max_follow_days, available_follow_days)
                ),
                "V22_20D_Status": status,
                "V22_New_BB_Event_Before_Rebound": bool(new_event_count > 0),
                "V22_New_BB_Event_Count_To_Check_End": new_event_count,
            }
        )

    return pd.DataFrame(rows).sort_values("BB_Event_ID").reset_index(drop=True)

def build_v22_horizon_summary(
    tracking_df: pd.DataFrame,
    horizons=None,
) -> pd.DataFrame:
    """固定イベント終了後N営業日以内の反発確認を集計する。"""

    if tracking_df is None or tracking_df.empty:
        return pd.DataFrame()

    if horizons is None:
        horizons = V22_POST_WINDOW_HORIZONS

    rows = []
    total = len(tracking_df)

    for horizon in horizons:
        horizon = int(horizon)
        confirmed_mask = (
            pd.to_numeric(
                tracking_df["V22_Days_After_Event_End"], errors="coerce"
            ).le(horizon)
        )
        confirmed = int(confirmed_mask.sum())

        full_observation_mask = pd.to_numeric(
            tracking_df["V22_Available_Follow_Days"], errors="coerce"
        ).ge(horizon)

        # 早期に反発を確認済みなら、その後のデータが不足していても
        # 「N日以内に反発した」こと自体は確定している。
        determinable_mask = confirmed_mask | full_observation_mask
        determinable = int(determinable_mask.sum())
        no_rebound = int((determinable_mask & ~confirmed_mask).sum())
        insufficient = int(total - determinable)

        rows.append(
            {
                "固定窓終了後追跡": f"{horizon}営業日以内",
                "見送りイベント": total,
                "判定可能": determinable,
                "期間内反発確認": confirmed,
                "期間内反発なし": no_rebound,
                "将来データ不足": insufficient,
                "判定可能中の反発確認率_%": (
                    confirmed / determinable * 100.0 if determinable else np.nan
                ),
            }
        )

    return pd.DataFrame(rows)


def build_v22_timing_summary(tracking_df: pd.DataFrame) -> pd.DataFrame:
    """20営業日以内に確認した反発の初回タイミングを正確な日数別に表示する。"""

    if tracking_df is None or tracking_df.empty:
        return pd.DataFrame()

    confirmed = tracking_df.dropna(
        subset=["V22_Days_After_Event_End"]
    ).copy()

    rows = []
    for day in range(1, V22_MAX_FOLLOW_DAYS + 1):
        count = int(
            pd.to_numeric(
                confirmed["V22_Days_After_Event_End"], errors="coerce"
            ).eq(day).sum()
        )
        if count == 0:
            continue

        event_ids = ",".join(
            str(int(x))
            for x in pd.to_numeric(
                confirmed.loc[
                    pd.to_numeric(
                        confirmed["V22_Days_After_Event_End"], errors="coerce"
                    ).eq(day),
                    "BB_Event_ID",
                ],
                errors="coerce",
            ).dropna()
        )
        rows.append(
            {
                "固定窓終了後営業日": day,
                "元イベント基準day": day + LOWER_EVENT_OBSERVATION_DAYS,
                "初回反発確認件数": count,
                "イベントID": event_ids,
            }
        )

    no_confirm = tracking_df[
        tracking_df["V22_Days_After_Event_End"].isna()
    ].copy()
    if not no_confirm.empty:
        ids = ",".join(
            str(int(x))
            for x in pd.to_numeric(no_confirm["BB_Event_ID"], errors="coerce").dropna()
        )
        rows.append(
            {
                "固定窓終了後営業日": np.nan,
                "元イベント基準day": np.nan,
                "初回反発確認件数": len(no_confirm),
                "イベントID": ids,
            }
        )

    return pd.DataFrame(rows)


def make_v22_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.3
# 固定窓終了後の遅い反発を待ってEntryする方針C
# ============================================================

def build_v23_late_rebound_r_design(
    data: pd.DataFrame,
    tracking_df: pd.DataFrame,
) -> pd.DataFrame:
    """v2.2追跡で確認した固定窓後の初回反発からR設計を作る。

    Entry: 反発確認日の翌営業日Open
    Stop : 元BBイベントday0から反発確認日までのLow最小値
    未来の価格はStop計算に使わない。
    """

    if data is None or data.empty or tracking_df is None or tracking_df.empty:
        return pd.DataFrame()

    index_ts = pd.to_datetime(pd.Index(data.index), errors="coerce")

    def resolve_position(date_value):
        ts = pd.to_datetime(date_value, errors="coerce")
        if pd.isna(ts):
            return None
        target = ts.date()
        for pos, idx_ts in enumerate(index_ts):
            if pd.notna(idx_ts) and idx_ts.date() == target:
                return int(pos)
        return None

    rows = []

    for _, tr in tracking_df.iterrows():
        event_id_value = tr.get("BB_Event_ID", np.nan)
        if pd.isna(event_id_value):
            continue

        event_id = int(event_id_value)
        start_date = pd.to_datetime(tr.get("V22_Event_Start_Date", pd.NaT), errors="coerce")
        event_end_date = pd.to_datetime(tr.get("V22_Event_End_Date", pd.NaT), errors="coerce")
        signal_date = pd.to_datetime(tr.get("V22_First_Rebound_Date", pd.NaT), errors="coerce")
        days_after_end = pd.to_numeric(
            pd.Series([tr.get("V22_Days_After_Event_End", np.nan)]), errors="coerce"
        ).iloc[0]
        new_bb = tr.get("V22_New_BB_Event_Before_Rebound", np.nan)
        new_bb_count = tr.get("V22_New_BB_Event_Count_To_Check_End", np.nan)

        base = {
            "BB_Event_ID": event_id,
            "V23_Event_Start_Date": start_date,
            "V23_Event_End_Date": event_end_date,
            "V23Late_Signal_Date": signal_date,
            "V23_Days_After_Event_End": days_after_end,
            "V23_New_BB_Event_Before_Rebound": new_bb,
            "V23_New_BB_Event_Count": new_bb_count,
            "V23Late_Entry_Date": pd.NaT,
            "V23Late_Entry_Price": np.nan,
            "V23Late_Stop_Price": np.nan,
            "V23Late_Risk_1R": np.nan,
            "V23Late_Risk_1R_Percent": np.nan,
            "V23Late_Target_1_5R": np.nan,
            "V23Late_Target_2R": np.nan,
            "V23Late_R_Valid": False,
            "V23Late_R_Status": "反発未確認",
        }

        if pd.isna(signal_date):
            rows.append(base)
            continue

        start_pos = resolve_position(start_date)
        signal_pos = resolve_position(signal_date)

        if start_pos is None or signal_pos is None or signal_pos < start_pos:
            base["V23Late_R_Status"] = "日付位置取得不可"
            rows.append(base)
            continue

        stop_price = pd.to_numeric(
            data.iloc[start_pos : signal_pos + 1]["Low"], errors="coerce"
        ).min()
        base["V23Late_Stop_Price"] = stop_price

        entry_pos = signal_pos + 1
        if entry_pos >= len(data):
            base["V23Late_R_Status"] = "翌営業日データなし"
            rows.append(base)
            continue

        entry_date = data.index[entry_pos]
        entry_price = pd.to_numeric(
            pd.Series([data.iloc[entry_pos]["Open"]]), errors="coerce"
        ).iloc[0]
        base["V23Late_Entry_Date"] = entry_date
        base["V23Late_Entry_Price"] = entry_price

        if pd.isna(stop_price) or pd.isna(entry_price):
            base["V23Late_R_Status"] = "価格データ不足"
            rows.append(base)
            continue

        risk = float(entry_price) - float(stop_price)
        if risk <= 0:
            base["V23Late_R_Status"] = "R計算不可（Entry≦Stop）"
            rows.append(base)
            continue

        risk_pct = risk / float(entry_price) * 100.0
        base["V23Late_Risk_1R"] = risk
        base["V23Late_Risk_1R_Percent"] = risk_pct
        base["V23Late_Target_1_5R"] = float(entry_price) + 1.5 * risk
        base["V23Late_Target_2R"] = float(entry_price) + 2.0 * risk
        base["V23Late_R_Valid"] = True
        base["V23Late_R_Status"] = "R計算可能"
        rows.append(base)

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    # calculate_first_hit_results はindexをSignal_Dateとして記録するため、
    # 反発確認日をindexにする。同一日複数イベントでも計算自体は可能だが、
    # 元データ照合はEntry_Dateで行うため未来情報は混ざらない。
    result = result.sort_values(["V23Late_Signal_Date", "BB_Event_ID"]).copy()
    result.index = pd.to_datetime(result["V23Late_Signal_Date"], errors="coerce")
    return result


def build_v23_policy_summary(
    tracking_df: pd.DataFrame,
    design_df: pd.DataFrame,
    pnl_df: pd.DataFrame,
    wait_limit: int,
    target_r: float,
) -> pd.DataFrame:
    """方針Cの機会平均R。待機上限まで反発なしは0R見送り。"""

    if tracking_df is None or tracking_df.empty:
        return pd.DataFrame()

    wait_limit = int(wait_limit)
    days = pd.to_numeric(tracking_df["V22_Days_After_Event_End"], errors="coerce")
    eligible_ids = set(
        pd.to_numeric(
            tracking_df.loc[days.le(wait_limit), "BB_Event_ID"], errors="coerce"
        ).dropna().astype(int).tolist()
    )
    all_ids = set(
        pd.to_numeric(tracking_df["BB_Event_ID"], errors="coerce")
        .dropna().astype(int).tolist()
    )
    skipped_ids = all_ids - eligible_ids

    design_valid_ids = set()
    if design_df is not None and not design_df.empty:
        d = design_df.copy()
        d_ids = pd.to_numeric(d["BB_Event_ID"], errors="coerce")
        d_valid = d["V23Late_R_Valid"].eq(True) & d_ids.isin(eligible_ids)
        design_valid_ids = set(d_ids[d_valid].dropna().astype(int).tolist())

    rows = []
    for horizon in FIRST_HIT_HORIZONS:
        part = pd.DataFrame()
        if pnl_df is not None and not pnl_df.empty:
            part = pnl_df[
                (pnl_df["Horizon"] == int(horizon))
                & np.isclose(pd.to_numeric(pnl_df["Target_R"], errors="coerce"), float(target_r))
                & pd.to_numeric(pnl_df["BB_Event_ID"], errors="coerce").isin(eligible_ids)
            ].copy()

        valid = part[part.get("R_PnL_Valid", False).eq(True)].copy() if not part.empty else pd.DataFrame()
        realized = (
            pd.to_numeric(valid["Realized_R"], errors="coerce").dropna()
            if not valid.empty else pd.Series(dtype=float)
        )

        # 見送りは0R。Entry対象なのにR結果が計算不能なら機会平均から除外し、比較不可に残す。
        opportunity_values = [0.0] * len(skipped_ids) + realized.tolist()
        opportunity = pd.Series(opportunity_values, dtype=float)
        unavailable = len(all_ids) - len(skipped_ids) - len(realized)

        rows.append({
            "待機上限": f"固定窓後{wait_limit}営業日",
            "保有期間": f"{horizon}営業日",
            "Target": f"+{target_r:g}R",
            "元見送りイベント": len(all_ids),
            "反発確認→Entry対象": len(eligible_ids),
            "見送り継続": len(skipped_ids),
            "R設計可能": len(design_valid_ids),
            "R損益計算可能": len(realized),
            "機会平均R": float(opportunity.mean()) if not opportunity.empty else np.nan,
            "Entry取引平均R": float(realized.mean()) if not realized.empty else np.nan,
            "Entry取引中央値R": float(realized.median()) if not realized.empty else np.nan,
            "Entry取引合計R": float(realized.sum()) if not realized.empty else np.nan,
            "Target決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "Target決済").sum()) if not part.empty else 0,
            "Stop決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "Stop決済").sum()) if not part.empty else 0,
            "期間末決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "期間末終値決済").sum()) if not part.empty else 0,
            "比較不可": int(max(0, unavailable)),
        })

    return pd.DataFrame(rows)


def build_v23_new_bb_split_summary(
    design_df: pd.DataFrame,
    pnl_df: pd.DataFrame,
    wait_limit: int,
    target_r: float,
    horizon: int = 20,
) -> pd.DataFrame:
    """遅い反発までに新規BBイベントを挟んだかでR結果を分ける。"""

    if design_df is None or design_df.empty:
        return pd.DataFrame()

    d = design_df.copy()
    days = pd.to_numeric(d["V23_Days_After_Event_End"], errors="coerce")
    d = d[days.le(int(wait_limit))].copy()
    if d.empty:
        return pd.DataFrame()

    p = pd.DataFrame()
    if pnl_df is not None and not pnl_df.empty:
        p = pnl_df[
            (pnl_df["Horizon"] == int(horizon))
            & np.isclose(pd.to_numeric(pnl_df["Target_R"], errors="coerce"), float(target_r))
        ][["BB_Event_ID", "Exit_Type", "Realized_R", "R_PnL_Valid"]].copy()
        p["BB_Event_ID"] = pd.to_numeric(p["BB_Event_ID"], errors="coerce").astype("Int64")

    d["BB_Event_ID"] = pd.to_numeric(d["BB_Event_ID"], errors="coerce").astype("Int64")
    if not p.empty:
        d = d.merge(p, on="BB_Event_ID", how="left", validate="one_to_one")
    else:
        d["Exit_Type"] = ""
        d["Realized_R"] = np.nan
        d["R_PnL_Valid"] = False

    d["新規BBイベント"] = np.where(
        d["V23_New_BB_Event_Before_Rebound"].eq(True), "あり", "なし"
    )

    rows = []
    for label in ["なし", "あり"]:
        g = d[d["新規BBイベント"] == label].copy()
        if g.empty:
            continue
        valid = g[g["R_PnL_Valid"].eq(True)].copy()
        r = pd.to_numeric(valid["Realized_R"], errors="coerce").dropna()
        rows.append({
            "反発までに新規BBイベント": label,
            "Entry対象": len(g),
            "R損益計算可能": len(r),
            "平均R": float(r.mean()) if not r.empty else np.nan,
            "中央値R": float(r.median()) if not r.empty else np.nan,
            "合計R": float(r.sum()) if not r.empty else np.nan,
            "Target決済": int((g["Exit_Type"] == "Target決済").sum()),
            "Stop決済": int((g["Exit_Type"] == "Stop決済").sum()),
            "期間末決済": int((g["Exit_Type"] == "期間末終値決済").sum()),
            "比較不可": int((~g["R_PnL_Valid"].eq(True)).sum()),
        })
    return pd.DataFrame(rows)


def make_v23_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.4
# 元見送りイベントと、その後に始まった新規BBイベントの連結診断
# ============================================================

def build_v24_event_linkage(
    data: pd.DataFrame,
    tracking_df: pd.DataFrame,
    design_df: pd.DataFrame,
) -> pd.DataFrame:
    """元イベント → 新規BBイベント → 遅い反発の関係を1行ずつ作る。

    新規BBイベントが複数ある場合は、遅い反発日の行が属しているイベントを
    優先して「連結先」とする。反発日が固定窓外なら、反発前の最新新規イベントを
    連結先にする。これによりイベントIDの二重計上を診断する。
    """

    if data is None or data.empty or tracking_df is None or tracking_df.empty:
        return pd.DataFrame()

    index_ts = pd.to_datetime(pd.Index(data.index), errors="coerce")

    def resolve_position(date_value):
        ts = pd.to_datetime(date_value, errors="coerce")
        if pd.isna(ts):
            return None
        target = ts.date()
        for pos, idx_ts in enumerate(index_ts):
            if pd.notna(idx_ts) and idx_ts.date() == target:
                return int(pos)
        return None

    design_map = {}
    if design_df is not None and not design_df.empty:
        for _, r in design_df.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                design_map[int(eid)] = r

    rows = []

    for _, tr in tracking_df.iterrows():
        source_id_value = pd.to_numeric(
            pd.Series([tr.get("BB_Event_ID")]), errors="coerce"
        ).iloc[0]
        if pd.isna(source_id_value):
            continue
        source_id = int(source_id_value)

        source_start = pd.to_datetime(tr.get("V22_Event_Start_Date", pd.NaT), errors="coerce")
        source_end = pd.to_datetime(tr.get("V22_Event_End_Date", pd.NaT), errors="coerce")
        late_rebound = pd.to_datetime(tr.get("V22_First_Rebound_Date", pd.NaT), errors="coerce")

        end_pos = resolve_position(source_end)
        rebound_pos = resolve_position(late_rebound)

        new_event_starts = []
        if end_pos is not None and rebound_pos is not None and rebound_pos > end_pos:
            for pos in range(end_pos + 1, rebound_pos + 1):
                if bool(data.iloc[pos].get("New_BB_Lower_Event", False)):
                    eid = pd.to_numeric(
                        pd.Series([data.iloc[pos].get("BB_Event_ID", np.nan)]),
                        errors="coerce",
                    ).iloc[0]
                    if pd.notna(eid):
                        new_event_starts.append((int(eid), int(pos), data.index[pos]))

        new_ids = [x[0] for x in new_event_starts]
        linked_id = None
        linked_start_pos = None
        linked_start_date = pd.NaT

        # 反発日の行が新規イベント固定窓に属していれば、そのイベントを優先。
        if rebound_pos is not None:
            rebound_event_id = pd.to_numeric(
                pd.Series([data.iloc[rebound_pos].get("BB_Event_ID", np.nan)]),
                errors="coerce",
            ).iloc[0]
            if pd.notna(rebound_event_id) and int(rebound_event_id) in new_ids:
                linked_id = int(rebound_event_id)
                for eid, pos, dt in new_event_starts:
                    if eid == linked_id:
                        linked_start_pos = pos
                        linked_start_date = dt
                        break

        # 固定窓外で反発した場合は、反発前に始まった最新イベントを連結先にする。
        if linked_id is None and new_event_starts:
            linked_id, linked_start_pos, linked_start_date = new_event_starts[-1]

        linked_end_date = pd.NaT
        linked_complete = False
        linked_stop_date = pd.NaT
        linked_stop_day = np.nan
        linked_rebound_date = pd.NaT
        linked_rebound_day = np.nan
        linked_relation = "新規BBイベントなし"
        late_is_first_rebound = False
        late_inside_linked_window = False
        linked_rebound_entry_date = pd.NaT
        linked_rebound_entry_price = np.nan
        linked_rebound_stop_price = np.nan
        linked_rebound_r_pct = np.nan
        linked_rebound_r_valid = False
        linked_rebound_r_status = "対象外"

        if linked_id is not None:
            event_rows = data[
                pd.to_numeric(data["BB_Event_ID"], errors="coerce").eq(linked_id)
            ].copy()
            if not event_rows.empty:
                linked_end_values = pd.to_datetime(
                    event_rows.get("Event_End_Date", pd.Series(dtype="datetime64[ns]")),
                    errors="coerce",
                ).dropna()
                if not linked_end_values.empty:
                    linked_end_date = linked_end_values.iloc[0]
                linked_complete = bool(
                    event_rows.get(
                        "Event_Observation_Complete", pd.Series(False, index=event_rows.index)
                    ).eq(True).any()
                )

                stop_rows = event_rows[
                    event_rows.get(
                        "First_Decline_Stop_In_Event", pd.Series(False, index=event_rows.index)
                    ).eq(True)
                ]
                rebound_rows = event_rows[
                    event_rows.get(
                        "First_Rebound_Start_In_Event", pd.Series(False, index=event_rows.index)
                    ).eq(True)
                ]

                if not stop_rows.empty:
                    linked_stop_date = stop_rows.index[0]
                    linked_stop_day = pd.to_numeric(
                        pd.Series([stop_rows.iloc[0].get("Days_From_BB_Event_Start", np.nan)]),
                        errors="coerce",
                    ).iloc[0]
                if not rebound_rows.empty:
                    rr = rebound_rows.iloc[0]
                    linked_rebound_date = rebound_rows.index[0]
                    linked_rebound_day = pd.to_numeric(
                        pd.Series([rr.get("Days_From_BB_Event_Start", np.nan)]),
                        errors="coerce",
                    ).iloc[0]
                    linked_rebound_entry_date = pd.to_datetime(
                        rr.get("Rebound_Entry_Date", pd.NaT), errors="coerce"
                    )
                    linked_rebound_entry_price = rr.get("Rebound_Entry_Price", np.nan)
                    linked_rebound_stop_price = rr.get("Rebound_Stop_Price", np.nan)
                    linked_rebound_r_pct = rr.get("Rebound_Risk_1R_Percent", np.nan)
                    linked_rebound_r_valid = bool(rr.get("Rebound_R_Valid", False))
                    linked_rebound_r_status = rr.get("Rebound_R_Status", "")

                has_stop = not stop_rows.empty
                has_rebound = not rebound_rows.empty
                if has_stop and has_rebound:
                    if linked_rebound_day > linked_stop_day:
                        linked_relation = "両方確認・反発が後"
                    elif linked_rebound_day == linked_stop_day:
                        linked_relation = "両方確認・同日"
                    else:
                        linked_relation = "両方確認・反発が先"
                elif has_stop:
                    linked_relation = "下落停止のみ"
                elif has_rebound:
                    linked_relation = "反発開始のみ"
                else:
                    linked_relation = "両方なし"

                if pd.notna(late_rebound) and pd.notna(linked_rebound_date):
                    late_is_first_rebound = (
                        pd.Timestamp(late_rebound).date()
                        == pd.Timestamp(linked_rebound_date).date()
                    )

            if linked_start_pos is not None and rebound_pos is not None:
                late_inside_linked_window = bool(
                    0 <= rebound_pos - linked_start_pos <= LOWER_EVENT_OBSERVATION_DAYS
                )

        old_design = design_map.get(source_id)
        old_entry_date = pd.NaT
        old_entry_price = np.nan
        old_stop_price = np.nan
        old_r_pct = np.nan
        if old_design is not None:
            old_entry_date = pd.to_datetime(
                old_design.get("V23Late_Entry_Date", pd.NaT), errors="coerce"
            )
            old_entry_price = old_design.get("V23Late_Entry_Price", np.nan)
            old_stop_price = old_design.get("V23Late_Stop_Price", np.nan)
            old_r_pct = old_design.get("V23Late_Risk_1R_Percent", np.nan)

        same_entry_date = False
        if pd.notna(old_entry_date) and pd.notna(linked_rebound_entry_date):
            same_entry_date = (
                pd.Timestamp(old_entry_date).date()
                == pd.Timestamp(linked_rebound_entry_date).date()
            )

        same_entry_price = False
        if pd.notna(old_entry_price) and pd.notna(linked_rebound_entry_price):
            same_entry_price = bool(
                np.isclose(float(old_entry_price), float(linked_rebound_entry_price))
            )

        same_stop_price = False
        if pd.notna(old_stop_price) and pd.notna(linked_rebound_stop_price):
            same_stop_price = bool(
                np.isclose(float(old_stop_price), float(linked_rebound_stop_price))
            )

        rows.append({
            "元イベントID": source_id,
            "元イベント開始日": source_start,
            "元固定窓終了日": source_end,
            "遅い反発確認日": late_rebound,
            "新規BBイベント数": len(new_event_starts),
            "新規BBイベントID一覧": ",".join(str(x) for x in new_ids),
            "連結先イベントID": linked_id if linked_id is not None else np.nan,
            "連結先イベント開始日": linked_start_date,
            "連結先イベント終了日": linked_end_date,
            "連結先観察完了": linked_complete if linked_id is not None else np.nan,
            "連結先下落停止日": linked_stop_date,
            "連結先下落停止day": linked_stop_day,
            "連結先最初の反発日": linked_rebound_date,
            "連結先反発day": linked_rebound_day,
            "連結先シグナル関係": linked_relation,
            "遅い反発は連結先固定窓内": late_inside_linked_window if linked_id is not None else np.nan,
            "遅い反発=連結先最初の反発": late_is_first_rebound if linked_id is not None else np.nan,
            "v2.3_Entry日": old_entry_date,
            "連結先Rebound_Entry日": linked_rebound_entry_date,
            "Entry日同一": same_entry_date if linked_id is not None else np.nan,
            "v2.3_Entry価格": old_entry_price,
            "連結先Rebound_Entry価格": linked_rebound_entry_price,
            "Entry価格同一": same_entry_price if linked_id is not None else np.nan,
            "v2.3_Stop価格": old_stop_price,
            "連結先Rebound_Stop価格": linked_rebound_stop_price,
            "Stop価格同一": same_stop_price if linked_id is not None else np.nan,
            "v2.3_1R率_%": old_r_pct,
            "連結先Rebound_1R率_%": linked_rebound_r_pct,
            "連結先Rebound_R設計可能": linked_rebound_r_valid if linked_id is not None else np.nan,
            "連結先Rebound_R状態": linked_rebound_r_status if linked_id is not None else "対象外",
        })

    return pd.DataFrame(rows).sort_values("元イベントID").reset_index(drop=True)


def build_v24_linkage_summary(linkage_df: pd.DataFrame) -> pd.DataFrame:
    if linkage_df is None or linkage_df.empty:
        return pd.DataFrame()

    has_new = pd.to_numeric(linkage_df["新規BBイベント数"], errors="coerce").gt(0)
    linked = linkage_df[has_new].copy()

    def true_count(column):
        if linked.empty or column not in linked.columns:
            return 0
        return int(linked[column].eq(True).sum())

    rows = [
        {"診断項目": "元見送りイベント", "件数": len(linkage_df)},
        {"診断項目": "反発まで新規BBイベントなし", "件数": int((~has_new).sum())},
        {"診断項目": "反発まで新規BBイベントあり", "件数": int(has_new.sum())},
        {"診断項目": "遅い反発が連結先の固定窓内", "件数": true_count("遅い反発は連結先固定窓内")},
        {"診断項目": "遅い反発=連結先の最初の反発", "件数": true_count("遅い反発=連結先最初の反発")},
        {"診断項目": "v2.3と連結先ReboundのEntry日が同一", "件数": true_count("Entry日同一")},
        {"診断項目": "v2.3と連結先ReboundのEntry価格が同一", "件数": true_count("Entry価格同一")},
        {"診断項目": "v2.3と連結先ReboundのStop価格が同一", "件数": true_count("Stop価格同一")},
    ]
    return pd.DataFrame(rows)


def make_v24_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.5
# 新BBイベント発生時リセット方式
# ============================================================

def build_v25_reset_r_design(
    data: pd.DataFrame,
    linkage_df: pd.DataFrame,
    v23_design_df: pd.DataFrame,
) -> pd.DataFrame:
    """v2.4の連結結果を使い、重複しない実効イベント単位のR設計を作る。

    ・新規BBイベントなし:
      元イベントの遅い反発(v2.3)をそのまま使う。
    ・新規BBイベントあり:
      旧イベントの延長としては数えず、連結先の新イベントで最初に確認された
      Reboundシグナルと、その新イベントday0起点のR設計へ置き換える。

    これにより、同じ反発日を「旧イベントの遅い反発」と「新イベントの反発」の
    2件として数えない。
    """

    if data is None or data.empty or linkage_df is None or linkage_df.empty:
        return pd.DataFrame()

    v23_map = {}
    if v23_design_df is not None and not v23_design_df.empty:
        for _, r in v23_design_df.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                v23_map[int(eid)] = r

    rows = []

    for _, link in linkage_df.iterrows():
        source_val = pd.to_numeric(pd.Series([link.get("元イベントID")]), errors="coerce").iloc[0]
        if pd.isna(source_val):
            continue
        source_id = int(source_val)

        new_count = pd.to_numeric(
            pd.Series([link.get("新規BBイベント数", 0)]), errors="coerce"
        ).iloc[0]
        has_new = bool(pd.notna(new_count) and float(new_count) > 0)

        effective_id = source_id
        mode = "新イベントなし・遅い反発継続"
        signal_date = pd.NaT
        entry_date = pd.NaT
        entry_price = np.nan
        stop_price = np.nan
        risk = np.nan
        risk_pct = np.nan
        target15 = np.nan
        target20 = np.nan
        valid = False
        status = "R設計対象なし"
        source_start = pd.to_datetime(link.get("元イベント開始日", pd.NaT), errors="coerce")
        effective_start = source_start

        if has_new:
            linked_val = pd.to_numeric(
                pd.Series([link.get("連結先イベントID")]), errors="coerce"
            ).iloc[0]
            if pd.notna(linked_val):
                effective_id = int(linked_val)
                mode = "新BBイベントへリセット"
                effective_start = pd.to_datetime(
                    link.get("連結先イベント開始日", pd.NaT), errors="coerce"
                )

                event_rows = data[
                    pd.to_numeric(data["BB_Event_ID"], errors="coerce").eq(effective_id)
                ].copy()
                rebound_rows = event_rows[
                    event_rows.get(
                        "First_Rebound_Start_In_Event",
                        pd.Series(False, index=event_rows.index),
                    ).eq(True)
                ]

                if not rebound_rows.empty:
                    rr = rebound_rows.iloc[0]
                    signal_date = pd.to_datetime(rebound_rows.index[0], errors="coerce")
                    entry_date = pd.to_datetime(rr.get("Rebound_Entry_Date", pd.NaT), errors="coerce")
                    entry_price = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Entry_Price", np.nan)]), errors="coerce"
                    ).iloc[0]
                    stop_price = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Stop_Price", np.nan)]), errors="coerce"
                    ).iloc[0]
                    risk = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Risk_1R", np.nan)]), errors="coerce"
                    ).iloc[0]
                    risk_pct = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Risk_1R_Percent", np.nan)]), errors="coerce"
                    ).iloc[0]
                    target15 = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Target_1_5R", np.nan)]), errors="coerce"
                    ).iloc[0]
                    target20 = pd.to_numeric(
                        pd.Series([rr.get("Rebound_Target_2R", np.nan)]), errors="coerce"
                    ).iloc[0]
                    valid = bool(rr.get("Rebound_R_Valid", False))
                    status = str(rr.get("Rebound_R_Status", ""))
                else:
                    status = "新イベント側の固定窓内反発なし"
            else:
                mode = "新イベント連結不可"
                status = "連結先イベントIDなし"
        else:
            old = v23_map.get(source_id)
            if old is not None:
                signal_date = pd.to_datetime(old.get("V23Late_Signal_Date", pd.NaT), errors="coerce")
                entry_date = pd.to_datetime(old.get("V23Late_Entry_Date", pd.NaT), errors="coerce")
                entry_price = pd.to_numeric(
                    pd.Series([old.get("V23Late_Entry_Price", np.nan)]), errors="coerce"
                ).iloc[0]
                stop_price = pd.to_numeric(
                    pd.Series([old.get("V23Late_Stop_Price", np.nan)]), errors="coerce"
                ).iloc[0]
                risk = pd.to_numeric(
                    pd.Series([old.get("V23Late_Risk_1R", np.nan)]), errors="coerce"
                ).iloc[0]
                risk_pct = pd.to_numeric(
                    pd.Series([old.get("V23Late_Risk_1R_Percent", np.nan)]), errors="coerce"
                ).iloc[0]
                target15 = pd.to_numeric(
                    pd.Series([old.get("V23Late_Target_1_5R", np.nan)]), errors="coerce"
                ).iloc[0]
                target20 = pd.to_numeric(
                    pd.Series([old.get("V23Late_Target_2R", np.nan)]), errors="coerce"
                ).iloc[0]
                valid = bool(old.get("V23Late_R_Valid", False))
                status = str(old.get("V23Late_R_Status", ""))
            else:
                status = "v2.3遅い反発R設計なし"

        # 念のため、R値がある場合はTargetを再計算して定義を統一する。
        if valid and pd.notna(entry_price) and pd.notna(stop_price):
            risk = float(entry_price) - float(stop_price)
            if risk > 0:
                risk_pct = risk / float(entry_price) * 100.0
                target15 = float(entry_price) + 1.5 * risk
                target20 = float(entry_price) + 2.0 * risk
            else:
                valid = False
                status = "R計算不可（Entry≦Stop）"

        rows.append({
            "BB_Event_ID": effective_id,
            "V25_Source_Event_ID": source_id,
            "V25_Effective_Event_ID": effective_id,
            "V25_Mode": mode,
            "V25_Source_Event_Start_Date": source_start,
            "V25_Effective_Event_Start_Date": effective_start,
            "V25Reset_Signal_Date": signal_date,
            "V25Reset_Entry_Date": entry_date,
            "V25Reset_Entry_Price": entry_price,
            "V25Reset_Stop_Price": stop_price,
            "V25Reset_Risk_1R": risk,
            "V25Reset_Risk_1R_Percent": risk_pct,
            "V25Reset_Target_1_5R": target15,
            "V25Reset_Target_2R": target20,
            "V25Reset_R_Valid": valid,
            "V25Reset_R_Status": status,
            "V25_Old_Late_Rebound_Date": pd.to_datetime(
                link.get("遅い反発確認日", pd.NaT), errors="coerce"
            ),
            "V25_Linked_Event_ID": pd.to_numeric(
                pd.Series([link.get("連結先イベントID", np.nan)]), errors="coerce"
            ).iloc[0],
        })

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    # 実効イベントID + シグナル日が同じものは1取引だけ残す。
    # 元イベントの遅い反発と新イベント反発の二重計上を防ぐ安全装置。
    result = result.sort_values(
        ["V25Reset_Signal_Date", "V25_Effective_Event_ID", "V25_Source_Event_ID"]
    ).copy()
    result["V25_Duplicate_Key"] = (
        result["V25_Effective_Event_ID"].astype(str)
        + "|"
        + pd.to_datetime(result["V25Reset_Signal_Date"], errors="coerce").astype(str)
    )
    result["V25_Duplicate_Count"] = result.groupby("V25_Duplicate_Key")[
        "V25_Duplicate_Key"
    ].transform("size")
    result = result.drop_duplicates(subset=["V25_Duplicate_Key"], keep="first").copy()
    result.index = pd.to_datetime(result["V25Reset_Signal_Date"], errors="coerce")
    return result


def build_v25_reset_summary(
    design_df: pd.DataFrame,
    pnl_df: pd.DataFrame,
    target_r: float,
) -> pd.DataFrame:
    if design_df is None or design_df.empty:
        return pd.DataFrame()

    reset_count = int(design_df["V25_Mode"].eq("新BBイベントへリセット").sum())
    carry_count = int(design_df["V25_Mode"].eq("新イベントなし・遅い反発継続").sum())
    valid_design_count = int(design_df["V25Reset_R_Valid"].eq(True).sum())

    rows = []
    for horizon in FIRST_HIT_HORIZONS:
        part = pd.DataFrame()
        if pnl_df is not None and not pnl_df.empty:
            part = pnl_df[
                (pd.to_numeric(pnl_df["Horizon"], errors="coerce") == int(horizon))
                & np.isclose(
                    pd.to_numeric(pnl_df["Target_R"], errors="coerce"),
                    float(target_r),
                )
            ].copy()

        valid = part[part.get("R_PnL_Valid", False).eq(True)].copy() if not part.empty else pd.DataFrame()
        r = (
            pd.to_numeric(valid["Realized_R"], errors="coerce").dropna()
            if not valid.empty else pd.Series(dtype=float)
        )

        rows.append({
            "保有期間": f"{horizon}営業日",
            "Target": f"+{target_r:g}R",
            "元見送りイベント": int(design_df["V25_Source_Event_ID"].nunique()),
            "重複除去後の実効イベント": int(design_df["V25_Effective_Event_ID"].nunique()),
            "新イベントへリセット": reset_count,
            "新イベントなし・遅い反発": carry_count,
            "R設計可能": valid_design_count,
            "R損益計算可能": len(r),
            "平均R": float(r.mean()) if not r.empty else np.nan,
            "中央値R": float(r.median()) if not r.empty else np.nan,
            "合計R": float(r.sum()) if not r.empty else np.nan,
            "Target決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "Target決済").sum()) if not part.empty else 0,
            "Stop決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "Stop決済").sum()) if not part.empty else 0,
            "期間末決済": int((part.get("Exit_Type", pd.Series(dtype=str)) == "期間末終値決済").sum()) if not part.empty else 0,
            "比較不可": int(len(design_df) - len(r)),
        })

    return pd.DataFrame(rows)


def build_v25_compare_v23_v25(
    v23_design_df: pd.DataFrame,
    v23_pnl_df: pd.DataFrame,
    v25_design_df: pd.DataFrame,
    v25_pnl_df: pd.DataFrame,
    horizon: int = 20,
    target_r: float = 2.0,
) -> pd.DataFrame:
    """元見送りイベント単位でv2.3旧基準とv2.5リセット基準を比較する。"""

    if v25_design_df is None or v25_design_df.empty:
        return pd.DataFrame()

    old_design = {}
    if v23_design_df is not None and not v23_design_df.empty:
        for _, r in v23_design_df.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                old_design[int(eid)] = r

    old_pnl = {}
    if v23_pnl_df is not None and not v23_pnl_df.empty:
        part = v23_pnl_df[
            (pd.to_numeric(v23_pnl_df["Horizon"], errors="coerce") == int(horizon))
            & np.isclose(pd.to_numeric(v23_pnl_df["Target_R"], errors="coerce"), float(target_r))
        ]
        for _, r in part.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                old_pnl[int(eid)] = r

    new_pnl = {}
    if v25_pnl_df is not None and not v25_pnl_df.empty:
        part = v25_pnl_df[
            (pd.to_numeric(v25_pnl_df["Horizon"], errors="coerce") == int(horizon))
            & np.isclose(pd.to_numeric(v25_pnl_df["Target_R"], errors="coerce"), float(target_r))
        ]
        for _, r in part.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                new_pnl[int(eid)] = r

    rows = []
    for _, nd in v25_design_df.iterrows():
        source_id = int(nd["V25_Source_Event_ID"])
        effective_id = int(nd["V25_Effective_Event_ID"])
        od = old_design.get(source_id)
        op = old_pnl.get(source_id)
        npnl = new_pnl.get(effective_id)

        old_stop = od.get("V23Late_Stop_Price", np.nan) if od is not None else np.nan
        old_r_pct = od.get("V23Late_Risk_1R_Percent", np.nan) if od is not None else np.nan
        old_realized = op.get("Realized_R", np.nan) if op is not None else np.nan
        old_exit = op.get("Exit_Type", "") if op is not None else ""
        new_realized = npnl.get("Realized_R", np.nan) if npnl is not None else np.nan
        new_exit = npnl.get("Exit_Type", "") if npnl is not None else ""

        diff = np.nan
        if pd.notna(old_realized) and pd.notna(new_realized):
            diff = float(new_realized) - float(old_realized)

        rows.append({
            "元イベントID": source_id,
            "v2.5実効イベントID": effective_id,
            "扱い": nd.get("V25_Mode", ""),
            "シグナル日": nd.get("V25Reset_Signal_Date", pd.NaT),
            "Entry日": nd.get("V25Reset_Entry_Date", pd.NaT),
            "v2.3_Stop": old_stop,
            "v2.5_Stop": nd.get("V25Reset_Stop_Price", np.nan),
            "v2.3_1R率_%": old_r_pct,
            "v2.5_1R率_%": nd.get("V25Reset_Risk_1R_Percent", np.nan),
            "v2.3_決済": old_exit,
            "v2.3_実現R": old_realized,
            "v2.5_決済": new_exit,
            "v2.5_実現R": new_realized,
            "R差_v2.5-v2.3": diff,
        })

    return pd.DataFrame(rows).sort_values("元イベントID").reset_index(drop=True)


def make_v25_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# v2.6
# 独立BBイベント台帳
# ============================================================

def build_v26_event_ledger(
    data: pd.DataFrame,
    completed_event_start_df: pd.DataFrame,
    stop_pnl_20_2r: pd.DataFrame,
    rebound_pnl_20_2r: pd.DataFrame,
) -> pd.DataFrame:
    """完了BBイベントを1イベント=1行で整理する。

    固定day0～day3のイベント境界を唯一のイベント境界として使う。
    固定窓後の遅い反発は元イベントへ追加しない。新しいBB下限タッチが
    起きた場合は、その新しいBB_Event_IDの独立イベントとしてのみ扱う。
    """
    if (
        data is None or data.empty
        or completed_event_start_df is None or completed_event_start_df.empty
    ):
        return pd.DataFrame()

    def pnl_map(frame):
        result = {}
        if frame is None or frame.empty:
            return result
        w = frame.copy()
        if "Horizon" in w.columns:
            w = w[pd.to_numeric(w["Horizon"], errors="coerce").eq(20)]
        if "Target_R" in w.columns:
            w = w[np.isclose(pd.to_numeric(w["Target_R"], errors="coerce"), 2.0)]
        for _, r in w.iterrows():
            eid = pd.to_numeric(pd.Series([r.get("BB_Event_ID")]), errors="coerce").iloc[0]
            if pd.notna(eid):
                result[int(eid)] = r
        return result

    stop_map = pnl_map(stop_pnl_20_2r)
    rebound_map = pnl_map(rebound_pnl_20_2r)
    rows = []

    starts = completed_event_start_df.copy().sort_index()
    for start_date, start_row in starts.iterrows():
        eid_val = pd.to_numeric(pd.Series([start_row.get("BB_Event_ID")]), errors="coerce").iloc[0]
        if pd.isna(eid_val):
            continue
        eid = int(eid_val)

        event_rows = data[
            pd.to_numeric(data["BB_Event_ID"], errors="coerce").eq(eid)
        ].copy()
        if event_rows.empty:
            continue

        stop_rows = event_rows[event_rows["First_Decline_Stop_In_Event"].eq(True)]
        rebound_rows = event_rows[event_rows["First_Rebound_Start_In_Event"].eq(True)]
        stop_row = stop_rows.iloc[0] if not stop_rows.empty else None
        rebound_row = rebound_rows.iloc[0] if not rebound_rows.empty else None
        stop_date = stop_rows.index[0] if not stop_rows.empty else pd.NaT
        rebound_date = rebound_rows.index[0] if not rebound_rows.empty else pd.NaT

        has_stop = stop_row is not None
        has_rebound = rebound_row is not None
        if has_stop and has_rebound:
            if pd.Timestamp(stop_date) == pd.Timestamp(rebound_date):
                event_type = "両方確認・同日"
            elif pd.Timestamp(stop_date) < pd.Timestamp(rebound_date):
                event_type = "両方確認・反発が後"
            else:
                event_type = "両方確認・反発が先"
        elif has_stop:
            event_type = "下落停止のみ"
        elif has_rebound:
            event_type = "反発開始のみ"
        else:
            event_type = "両方未確認"

        sp = stop_map.get(eid)
        rp = rebound_map.get(eid)

        rows.append({
            "イベントID": eid,
            "イベント開始日": pd.to_datetime(start_date, errors="coerce"),
            "固定窓終了日": pd.to_datetime(start_row.get("Event_End_Date", pd.NaT), errors="coerce"),
            "イベント種別": event_type,
            "下落停止確認": has_stop,
            "下落停止day": (
                pd.to_numeric(pd.Series([stop_row.get("Days_From_BB_Event_Start")]), errors="coerce").iloc[0]
                if has_stop else np.nan
            ),
            "下落停止日": pd.to_datetime(stop_date, errors="coerce"),
            "反発開始確認": has_rebound,
            "反発開始day": (
                pd.to_numeric(pd.Series([rebound_row.get("Days_From_BB_Event_Start")]), errors="coerce").iloc[0]
                if has_rebound else np.nan
            ),
            "反発開始日": pd.to_datetime(rebound_date, errors="coerce"),
            "開始日終値": pd.to_numeric(pd.Series([start_row.get("Close")]), errors="coerce").iloc[0],
            "開始日BB下限": pd.to_numeric(pd.Series([start_row.get("BB_Lower")]), errors="coerce").iloc[0],
            "開始日BandWidth_%": pd.to_numeric(pd.Series([start_row.get("BandWidth")]), errors="coerce").iloc[0],
            "下落停止_20日2R決済": sp.get("Exit_Type", "") if sp is not None else "シグナルなし",
            "下落停止_20日2R実現R": sp.get("Realized_R", np.nan) if sp is not None else np.nan,
            "下落停止_20日2R状態": sp.get("R_PnL_Status", "シグナルなし") if sp is not None else "シグナルなし",
            "反発開始_20日2R決済": rp.get("Exit_Type", "") if rp is not None else "シグナルなし",
            "反発開始_20日2R実現R": rp.get("Realized_R", np.nan) if rp is not None else np.nan,
            "反発開始_20日2R状態": rp.get("R_PnL_Status", "シグナルなし") if rp is not None else "シグナルなし",
        })

    ledger = pd.DataFrame(rows)
    if ledger.empty:
        return ledger
    return ledger.sort_values(["イベント開始日", "イベントID"]).reset_index(drop=True)


def build_v26_audit_summary(
    ledger: pd.DataFrame,
    completed_event_start_df: pd.DataFrame,
) -> pd.DataFrame:
    completed_count = 0 if completed_event_start_df is None else len(completed_event_start_df)
    ledger_count = 0 if ledger is None else len(ledger)
    unique_count = 0 if ledger is None or ledger.empty else int(ledger["イベントID"].nunique())
    duplicate_rows = max(0, ledger_count - unique_count)

    expected_ids = set()
    if completed_event_start_df is not None and not completed_event_start_df.empty:
        expected_ids = set(
            pd.to_numeric(completed_event_start_df["BB_Event_ID"], errors="coerce")
            .dropna().astype(int).tolist()
        )
    actual_ids = set() if ledger is None or ledger.empty else set(ledger["イベントID"].astype(int).tolist())
    missing_ids = sorted(expected_ids - actual_ids)
    extra_ids = sorted(actual_ids - expected_ids)

    rows = [
        {"監査項目": "観察完了BBイベント", "値": completed_count, "状態": "基準"},
        {"監査項目": "独立イベント台帳行数", "値": ledger_count, "状態": "OK" if ledger_count == completed_count else "要確認"},
        {"監査項目": "ユニークイベントID", "値": unique_count, "状態": "OK" if unique_count == ledger_count else "要確認"},
        {"監査項目": "重複イベントID行", "値": duplicate_rows, "状態": "OK" if duplicate_rows == 0 else "要確認"},
        {"監査項目": "台帳に欠落した完了イベントID", "値": len(missing_ids), "状態": "OK" if not missing_ids else "要確認"},
        {"監査項目": "完了母集団外の余分なイベントID", "値": len(extra_ids), "状態": "OK" if not extra_ids else "要確認"},
    ]
    return pd.DataFrame(rows)


def build_v26_event_type_summary(ledger: pd.DataFrame) -> pd.DataFrame:
    if ledger is None or ledger.empty:
        return pd.DataFrame()
    order = [
        "両方確認・同日",
        "両方確認・反発が後",
        "両方確認・反発が先",
        "下落停止のみ",
        "反発開始のみ",
        "両方未確認",
    ]
    total = len(ledger)
    rows = []
    for label in order:
        count = int(ledger["イベント種別"].eq(label).sum())
        if count == 0:
            continue
        rows.append({
            "イベント種別": label,
            "件数": count,
            "割合_%": count / total * 100.0 if total else np.nan,
        })
    return pd.DataFrame(rows)


def build_v26_20d_2r_summary(ledger: pd.DataFrame) -> pd.DataFrame:
    if ledger is None or ledger.empty:
        return pd.DataFrame()
    rows = []
    for label, prefix, signal_col in [
        ("下落停止", "下落停止", "下落停止確認"),
        ("反発開始", "反発開始", "反発開始確認"),
    ]:
        w = ledger[ledger[signal_col].eq(True)].copy()
        realized = pd.to_numeric(w[f"{prefix}_20日2R実現R"], errors="coerce")
        valid = realized.notna()
        exits = w[f"{prefix}_20日2R決済"].astype(str)
        vals = realized[valid]
        rows.append({
            "シグナル": label,
            "確認イベント": len(w),
            "R損益計算可能": int(valid.sum()),
            "Target決済": int(exits.eq("Target決済").sum()),
            "Stop決済": int(exits.eq("Stop決済").sum()),
            "期間末決済": int(exits.eq("期間末終値決済").sum()),
            "順序不明": int(exits.eq("順序不明").sum()),
            "データ不足": int(exits.eq("データ不足").sum()),
            "合計R": float(vals.sum()) if not vals.empty else np.nan,
            "平均R": float(vals.mean()) if not vals.empty else np.nan,
            "中央値R": float(vals.median()) if not vals.empty else np.nan,
        })
    return pd.DataFrame(rows)


def make_v26_copy_text(title: str, data: pd.DataFrame) -> str:
    if data is None or data.empty:
        return title + "\n対象イベントなし"
    return title + "\n" + data.to_csv(index=False, float_format="%.4f").rstrip()


# ============================================================
# 全データ準備
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
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
# v3.0
# GOOG / NVDA 同一ルール・同一コスト銘柄横断診断
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def build_v30_ticker_bundle(
    ticker_symbol: str,
    prepared_data: pd.DataFrame,
    commission_rate: float,
    slippage_rate: float,
):
    """v2.6～v2.8の正式研究計算を1銘柄分まとめて再実行する。"""
    if prepared_data is None or prepared_data.empty:
        return None

    data = prepared_data.copy()
    valid = data.dropna(
        subset=["BB_Middle", "BB_Upper", "BB_Lower", "BandWidth"]
    ).copy()
    if valid.empty:
        return None

    event_starts = valid[valid["New_BB_Lower_Event"].eq(True)].copy()
    completed_starts = event_starts[
        event_starts["Event_Observation_Complete"].eq(True)
    ].copy()

    completed_ids = set(
        pd.to_numeric(completed_starts["BB_Event_ID"], errors="coerce")
        .dropna().astype(int).tolist()
    )
    completed_mask = (
        pd.to_numeric(valid["BB_Event_ID"], errors="coerce")
        .fillna(-1).astype(int).isin(completed_ids)
    )
    first_stop = valid[
        completed_mask & valid["First_Decline_Stop_In_Event"].eq(True)
    ].copy()
    first_rebound = valid[
        completed_mask & valid["First_Rebound_Start_In_Event"].eq(True)
    ].copy()

    signal_valid = {
        "Stop": first_stop[first_stop["Stop_R_Valid"].eq(True)].copy(),
        "Rebound": first_rebound[first_rebound["Rebound_R_Valid"].eq(True)].copy(),
    }

    first_hit_sets = {}
    legacy_sets = {}
    gap_sets = {}
    net_sets = {}

    for prefix_name in ["Stop", "Rebound"]:
        result_parts = []
        for horizon in FIRST_HIT_HORIZONS:
            part = calculate_first_hit_results(
                data,
                signal_valid[prefix_name],
                prefix_name,
                2.0,
                horizon,
            )
            if part is not None and not part.empty:
                result_parts.append(part)
        combined = (
            pd.concat(result_parts, ignore_index=True)
            if result_parts else pd.DataFrame()
        )
        first_hit_sets[prefix_name] = combined
        legacy_sets[prefix_name] = calculate_r_pnl_results(data, combined)
        gap_sets[prefix_name] = calculate_gap_aware_r_pnl_results(data, combined)
        net_sets[prefix_name] = calculate_v28_net_cost_results(
            gap_sets[prefix_name],
            commission_rate=commission_rate,
            slippage_rate=slippage_rate,
        )

    ledger = build_v26_event_ledger(
        data,
        completed_starts,
        legacy_sets["Stop"],
        legacy_sets["Rebound"],
    )

    return {
        "ticker": ticker_symbol,
        "data": data,
        "valid": valid,
        "completed_starts": completed_starts,
        "first_stop": first_stop,
        "first_rebound": first_rebound,
        "signal_valid": signal_valid,
        "ledger": ledger,
        "net_sets": net_sets,
    }


def build_v30_cross_ticker_audit(bundles: dict, period_label: str) -> pd.DataFrame:
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            rows.append({
                "銘柄": ticker_symbol,
                "期間設定": period_label,
                "データ開始日": pd.NaT,
                "データ終了日": pd.NaT,
                "観察完了BBイベント": 0,
                "独立台帳行数": 0,
                "ユニークイベントID": 0,
                "重複イベントID行": 0,
                "下落停止確認": 0,
                "下落停止R計算可能": 0,
                "反発開始確認": 0,
                "反発開始R計算可能": 0,
                "監査": "データなし",
            })
            continue

        valid = bundle["valid"]
        ledger = bundle["ledger"]
        completed_count = len(bundle["completed_starts"])
        ledger_count = len(ledger)
        unique_count = (
            int(pd.to_numeric(ledger["イベントID"], errors="coerce").nunique())
            if not ledger.empty else 0
        )
        duplicate_count = max(0, ledger_count - unique_count)
        audit_ok = (
            completed_count == ledger_count == unique_count
            and duplicate_count == 0
        )
        rows.append({
            "銘柄": ticker_symbol,
            "期間設定": period_label,
            "データ開始日": valid.index.min(),
            "データ終了日": valid.index.max(),
            "観察完了BBイベント": completed_count,
            "独立台帳行数": ledger_count,
            "ユニークイベントID": unique_count,
            "重複イベントID行": duplicate_count,
            "下落停止確認": len(bundle["first_stop"]),
            "下落停止R計算可能": len(bundle["signal_valid"]["Stop"]),
            "反発開始確認": len(bundle["first_rebound"]),
            "反発開始R計算可能": len(bundle["signal_valid"]["Rebound"]),
            "監査": "OK" if audit_ok else "要確認",
        })
    return pd.DataFrame(rows)


def build_v30_cross_ticker_net_summary(bundles: dict) -> pd.DataFrame:
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            continue
        completed_count = len(bundle["completed_starts"])
        for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
            results = bundle["net_sets"].get(prefix_name, pd.DataFrame())
            if results is None or results.empty:
                continue
            for horizon in FIRST_HIT_HORIZONS:
                part = results[
                    pd.to_numeric(results["Horizon"], errors="coerce").eq(horizon)
                ].copy()
                valid = part[part["Net_R_Valid"].eq(True)].copy()
                gross_r = pd.to_numeric(valid["Gross_Realized_R"], errors="coerce").dropna()
                net_r = pd.to_numeric(valid["Net_Realized_R"], errors="coerce").dropna()
                cost_r = pd.to_numeric(valid["Cost_R"], errors="coerce").dropna()
                rows.append({
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "保有期間": f"{horizon}営業日",
                    "観察完了BBイベント": completed_count,
                    "シグナル対象": len(part),
                    "Net_R計算可能": len(net_r),
                    "Gross合計R": float(gross_r.sum()) if not gross_r.empty else np.nan,
                    "Net合計R": float(net_r.sum()) if not net_r.empty else np.nan,
                    "コスト合計R": float(cost_r.sum()) if not cost_r.empty else np.nan,
                    "Net平均R": float(net_r.mean()) if not net_r.empty else np.nan,
                    "Net中央値R": float(net_r.median()) if not net_r.empty else np.nan,
                    "NetプラスR": int((net_r > 0).sum()),
                    "NetマイナスR": int((net_r < 0).sum()),
                    "NetゼロR": int((net_r.abs() <= 1e-12).sum()),
                })
    return pd.DataFrame(rows)


def build_v30_20d_cross_ticker(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty:
        return pd.DataFrame()
    part = summary[summary["保有期間"].eq("20営業日")].copy()
    return part.reset_index(drop=True)


def build_v30_ticker_difference(summary_20d: pd.DataFrame) -> pd.DataFrame:
    """NVDA-GOOGの差を記述するだけ。優劣判定や採用判定には使わない。"""
    if summary_20d is None or summary_20d.empty:
        return pd.DataFrame()
    rows = []
    for signal_label in ["下落停止", "反発開始"]:
        signal = summary_20d[summary_20d["シグナル"].eq(signal_label)]
        goog = signal[signal["銘柄"].eq("GOOG")]
        nvda = signal[signal["銘柄"].eq("NVDA")]
        if goog.empty or nvda.empty:
            continue
        g = goog.iloc[0]
        n = nvda.iloc[0]
        rows.append({
            "シグナル": signal_label,
            "GOOG_Net_R計算可能": int(g["Net_R計算可能"]),
            "NVDA_Net_R計算可能": int(n["Net_R計算可能"]),
            "GOOG_Net合計R": g["Net合計R"],
            "NVDA_Net合計R": n["Net合計R"],
            "GOOG_Net平均R": g["Net平均R"],
            "NVDA_Net平均R": n["Net平均R"],
            "平均R差_NVDA-GOOG": (
                float(n["Net平均R"]) - float(g["Net平均R"])
                if pd.notna(n["Net平均R"]) and pd.notna(g["Net平均R"])
                else np.nan
            ),
            "GOOG_Net中央値R": g["Net中央値R"],
            "NVDA_Net中央値R": n["Net中央値R"],
        })
    return pd.DataFrame(rows)


# ============================================================
# v3.1
# GOOG / NVDA 20日2R 損益構造分解
# ============================================================

def _v31_exit_bucket(exit_type: str) -> str:
    """v2.7以降の決済種別を、後付け条件なしの固定5区分へ整理する。"""
    value = str(exit_type or "")
    mapping = {
        "Target決済": "Target通常",
        "TargetギャップOpen決済": "Targetギャップ",
        "Stop決済": "Stop通常",
        "StopギャップOpen決済": "Stopギャップ",
        "期間末終値決済": "期間末",
    }
    return mapping.get(value, "その他")


def build_v31_20d_structure(bundles: dict) -> pd.DataFrame:
    """20日・2RのNet R計算可能行を決済構造別に分解する。"""
    rows = []
    bucket_order = ["Target通常", "Targetギャップ", "Stop通常", "Stopギャップ", "期間末"]
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            continue
        for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
            results = bundle["net_sets"].get(prefix_name, pd.DataFrame())
            if results is None or results.empty:
                continue
            part = results[
                pd.to_numeric(results["Horizon"], errors="coerce").eq(20)
                & results["Net_R_Valid"].eq(True)
            ].copy()
            if part.empty:
                continue
            part["v31区分"] = part["Exit_Type"].map(_v31_exit_bucket)
            total_n = len(part)
            for bucket in bucket_order:
                g = part[part["v31区分"].eq(bucket)].copy()
                if g.empty:
                    count = 0
                    gross_total = 0.0
                    net_total = 0.0
                    cost_total = 0.0
                    net_avg = np.nan
                    net_median = np.nan
                else:
                    gross = pd.to_numeric(g["Gross_Realized_R"], errors="coerce").dropna()
                    net = pd.to_numeric(g["Net_Realized_R"], errors="coerce").dropna()
                    cost = pd.to_numeric(g["Cost_R"], errors="coerce").dropna()
                    count = len(net)
                    gross_total = float(gross.sum())
                    net_total = float(net.sum())
                    cost_total = float(cost.sum())
                    net_avg = float(net.mean()) if not net.empty else np.nan
                    net_median = float(net.median()) if not net.empty else np.nan
                rows.append({
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "決済構造": bucket,
                    "件数": count,
                    "全R計算可能件数": total_n,
                    "件数比率_%": (count / total_n * 100.0) if total_n else np.nan,
                    "Gross合計R": gross_total,
                    "Net合計R": net_total,
                    "コスト合計R": cost_total,
                    "Net平均R": net_avg,
                    "Net中央値R": net_median,
                })
    return pd.DataFrame(rows)


def build_v31_cross_ticker_structure_difference(structure: pd.DataFrame) -> pd.DataFrame:
    """同じ決済構造についてNVDA-GOOG差を記述する。採用判定には使わない。"""
    if structure is None or structure.empty:
        return pd.DataFrame()
    rows = []
    bucket_order = ["Target通常", "Targetギャップ", "Stop通常", "Stopギャップ", "期間末"]
    for signal_label in ["下落停止", "反発開始"]:
        for bucket in bucket_order:
            part = structure[
                structure["シグナル"].eq(signal_label)
                & structure["決済構造"].eq(bucket)
            ]
            goog = part[part["銘柄"].eq("GOOG")]
            nvda = part[part["銘柄"].eq("NVDA")]
            if goog.empty or nvda.empty:
                continue
            g = goog.iloc[0]
            n = nvda.iloc[0]
            g_avg = pd.to_numeric(pd.Series([g["Net平均R"]]), errors="coerce").iloc[0]
            n_avg = pd.to_numeric(pd.Series([n["Net平均R"]]), errors="coerce").iloc[0]
            rows.append({
                "シグナル": signal_label,
                "決済構造": bucket,
                "GOOG件数": int(g["件数"]),
                "NVDA件数": int(n["件数"]),
                "GOOG件数比率_%": g["件数比率_%"],
                "NVDA件数比率_%": n["件数比率_%"],
                "GOOG_Net合計R": g["Net合計R"],
                "NVDA_Net合計R": n["Net合計R"],
                "Net合計R差_NVDA-GOOG": float(n["Net合計R"]) - float(g["Net合計R"]),
                "GOOG_Net平均R": g_avg,
                "NVDA_Net平均R": n_avg,
                "Net平均R差_NVDA-GOOG": (
                    float(n_avg) - float(g_avg)
                    if pd.notna(g_avg) and pd.notna(n_avg) else np.nan
                ),
            })
    return pd.DataFrame(rows)


def build_v31_reconciliation_audit(
    structure: pd.DataFrame,
    v30_20d_summary: pd.DataFrame,
) -> pd.DataFrame:
    """v3.1の5区分合計がv3.0の20日2Rと一致するか監査する。"""
    if structure is None or structure.empty or v30_20d_summary is None or v30_20d_summary.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        for signal_label in ["下落停止", "反発開始"]:
            s = structure[
                structure["銘柄"].eq(ticker_symbol)
                & structure["シグナル"].eq(signal_label)
            ]
            base = v30_20d_summary[
                v30_20d_summary["銘柄"].eq(ticker_symbol)
                & v30_20d_summary["シグナル"].eq(signal_label)
            ]
            if s.empty or base.empty:
                continue
            b = base.iloc[0]
            v31_n = int(pd.to_numeric(s["件数"], errors="coerce").fillna(0).sum())
            v31_net = float(pd.to_numeric(s["Net合計R"], errors="coerce").fillna(0).sum())
            v30_n = int(b["Net_R計算可能"])
            v30_net = float(b["Net合計R"])
            n_ok = v31_n == v30_n
            r_ok = abs(v31_net - v30_net) <= 1e-8
            rows.append({
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "v3.0_Net_R計算可能": v30_n,
                "v3.1_5区分件数合計": v31_n,
                "件数差": v31_n - v30_n,
                "v3.0_Net合計R": v30_net,
                "v3.1_5区分Net合計R": v31_net,
                "Net合計R差": v31_net - v30_net,
                "監査": "OK" if n_ok and r_ok else "要確認",
            })
    return pd.DataFrame(rows)



# ============================================================
# v3.2
# GOOG / NVDA 20営業日 MFE / MAE 価格経路診断
#
# MFE = Entry後20営業日の最高値が、計画時点1Rに対して何R上へ進んだか。
# MAE = Entry後20営業日の最安値が、計画時点1Rに対して何R下へ進んだか（正の不利幅）。
#
# 重要：このv3.2の主診断は「20営業日の固定観察窓」を最後まで見る。
# 実際のStop / Target決済後の値動きも含むため、売買損益ではなく価格経路の原因診断。
# これにより「Stopが先だったが、その後20日内に2Rへ戻った」ケースも識別する。
# ============================================================

def build_v32_path_detail(bundles: dict, horizon: int = 20) -> pd.DataFrame:
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            continue
        data = bundle["data"]
        for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
            signals = bundle["signal_valid"].get(prefix_name, pd.DataFrame())
            if signals is None or signals.empty:
                continue

            net20 = bundle["net_sets"].get(prefix_name, pd.DataFrame())
            if net20 is None:
                net20 = pd.DataFrame()
            if not net20.empty:
                net20 = net20[pd.to_numeric(net20["Horizon"], errors="coerce").eq(horizon)].copy()
                net20["BB_Event_ID_num"] = pd.to_numeric(net20["BB_Event_ID"], errors="coerce")

            entry_date_col = f"{prefix_name}_Entry_Date"
            entry_price_col = f"{prefix_name}_Entry_Price"
            risk_col = f"{prefix_name}_Risk_1R"
            risk_pct_col = f"{prefix_name}_Risk_1R_Percent"

            for signal_date, row in signals.iterrows():
                event_id = pd.to_numeric(pd.Series([row.get("BB_Event_ID", np.nan)]), errors="coerce").iloc[0]
                entry_date = pd.to_datetime(row.get(entry_date_col, pd.NaT), errors="coerce")
                entry_price = pd.to_numeric(pd.Series([row.get(entry_price_col, np.nan)]), errors="coerce").iloc[0]
                risk_1r = pd.to_numeric(pd.Series([row.get(risk_col, np.nan)]), errors="coerce").iloc[0]
                risk_pct = pd.to_numeric(pd.Series([row.get(risk_pct_col, np.nan)]), errors="coerce").iloc[0]

                base = {
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "イベントID": int(event_id) if pd.notna(event_id) else np.nan,
                    "シグナル日": signal_date,
                    "Entry日": entry_date,
                    "Entry価格": entry_price,
                    "1R": risk_1r,
                    "1R率_%": risk_pct,
                    "観察窓": f"{horizon}営業日",
                    "観察可能日数": 0,
                    "20日観察完了": False,
                    "MFE_R": np.nan,
                    "MAE_R": np.nan,
                    "20日終値_R": np.nan,
                    "MFE日": pd.NaT,
                    "MAE日": pd.NaT,
                    "0.5R到達": False,
                    "1R到達": False,
                    "1.5R到達": False,
                    "2R到達": False,
                    "MAE1R以上": False,
                    "2R先着結果": "照合なし",
                    "決済種別": "",
                    "Net実現R": np.nan,
                }

                if pd.isna(entry_date) or pd.isna(entry_price) or pd.isna(risk_1r) or float(risk_1r) <= 0:
                    rows.append(base)
                    continue
                try:
                    entry_pos = data.index.get_loc(entry_date)
                except KeyError:
                    rows.append(base)
                    continue
                if not isinstance(entry_pos, (int, np.integer)):
                    rows.append(base)
                    continue

                available = min(int(horizon), len(data) - int(entry_pos))
                base["観察可能日数"] = int(max(0, available))

                # 既存20日2Rのfirst-hit / Net結果をイベントIDで照合する。
                if pd.notna(event_id) and not net20.empty:
                    match = net20[net20["BB_Event_ID_num"].eq(float(event_id))]
                    if len(match) == 1:
                        rr = match.iloc[0]
                        base["2R先着結果"] = rr.get("Outcome", "")
                        base["決済種別"] = rr.get("Exit_Type", "")
                        if bool(rr.get("Net_R_Valid", False)):
                            base["Net実現R"] = pd.to_numeric(
                                pd.Series([rr.get("Net_Realized_R", np.nan)]), errors="coerce"
                            ).iloc[0]

                # 固定20営業日が全部そろわないイベントは、MFE/MAE本体集計へ入れない。
                if available < int(horizon):
                    rows.append(base)
                    continue

                window = data.iloc[int(entry_pos): int(entry_pos) + int(horizon)].copy()
                highs = pd.to_numeric(window["High"], errors="coerce")
                lows = pd.to_numeric(window["Low"], errors="coerce")
                closes = pd.to_numeric(window["Close"], errors="coerce")
                if highs.isna().any() or lows.isna().any() or closes.isna().any():
                    rows.append(base)
                    continue

                max_high = float(highs.max())
                min_low = float(lows.min())
                mfe_r = (max_high - float(entry_price)) / float(risk_1r)
                mae_r = (float(entry_price) - min_low) / float(risk_1r)
                close20_r = (float(closes.iloc[-1]) - float(entry_price)) / float(risk_1r)

                base.update({
                    "20日観察完了": True,
                    "MFE_R": float(mfe_r),
                    "MAE_R": float(mae_r),
                    "20日終値_R": float(close20_r),
                    "MFE日": highs.idxmax(),
                    "MAE日": lows.idxmin(),
                    "0.5R到達": bool(mfe_r >= 0.5),
                    "1R到達": bool(mfe_r >= 1.0),
                    "1.5R到達": bool(mfe_r >= 1.5),
                    "2R到達": bool(mfe_r >= 2.0),
                    "MAE1R以上": bool(mae_r >= 1.0),
                })
                rows.append(base)

    return pd.DataFrame(rows)


def build_v32_path_summary(detail: pd.DataFrame) -> pd.DataFrame:
    if detail is None or detail.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        for signal_label in ["下落停止", "反発開始"]:
            all_part = detail[
                detail["銘柄"].eq(ticker_symbol) & detail["シグナル"].eq(signal_label)
            ].copy()
            part = all_part[all_part["20日観察完了"].eq(True)].copy()
            if all_part.empty:
                continue
            n = len(part)
            mfe = pd.to_numeric(part["MFE_R"], errors="coerce").dropna()
            mae = pd.to_numeric(part["MAE_R"], errors="coerce").dropna()
            close20 = pd.to_numeric(part["20日終値_R"], errors="coerce").dropna()
            row = {
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "R有効シグナル": len(all_part),
                "20日観察完了": n,
                "20日観察未完了": len(all_part) - n,
                "MFE平均R": float(mfe.mean()) if not mfe.empty else np.nan,
                "MFE中央値R": float(mfe.median()) if not mfe.empty else np.nan,
                "MAE平均R": float(mae.mean()) if not mae.empty else np.nan,
                "MAE中央値R": float(mae.median()) if not mae.empty else np.nan,
                "20日終値平均R": float(close20.mean()) if not close20.empty else np.nan,
                "20日終値中央値R": float(close20.median()) if not close20.empty else np.nan,
            }
            for label, col in [("0.5R", "0.5R到達"), ("1R", "1R到達"), ("1.5R", "1.5R到達"), ("2R", "2R到達")]:
                count = int(part[col].eq(True).sum()) if n else 0
                row[f"MFE{label}以上_件数"] = count
                row[f"MFE{label}以上_%"] = count / n * 100.0 if n else np.nan
            mae1_count = int(part["MAE1R以上"].eq(True).sum()) if n else 0
            row["MAE1R以上_件数"] = mae1_count
            row["MAE1R以上_%"] = mae1_count / n * 100.0 if n else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def build_v32_threshold_difference(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty:
        return pd.DataFrame()
    rows = []
    for signal_label in ["下落停止", "反発開始"]:
        part = summary[summary["シグナル"].eq(signal_label)]
        goog = part[part["銘柄"].eq("GOOG")]
        nvda = part[part["銘柄"].eq("NVDA")]
        if goog.empty or nvda.empty:
            continue
        g, n = goog.iloc[0], nvda.iloc[0]
        row = {
            "シグナル": signal_label,
            "GOOG_20日観察完了": int(g["20日観察完了"]),
            "NVDA_20日観察完了": int(n["20日観察完了"]),
            "GOOG_MFE平均R": g["MFE平均R"],
            "NVDA_MFE平均R": n["MFE平均R"],
            "MFE平均R差_NVDA-GOOG": float(n["MFE平均R"]) - float(g["MFE平均R"]),
            "GOOG_MAE平均R": g["MAE平均R"],
            "NVDA_MAE平均R": n["MAE平均R"],
            "MAE平均R差_NVDA-GOOG": float(n["MAE平均R"]) - float(g["MAE平均R"]),
        }
        for label in ["0.5R", "1R", "1.5R", "2R"]:
            gc = f"MFE{label}以上_%"
            row[f"GOOG_MFE{label}以上_%"] = g[gc]
            row[f"NVDA_MFE{label}以上_%"] = n[gc]
            row[f"差_{label}_NVDA-GOOG_ポイント"] = float(n[gc]) - float(g[gc])
        rows.append(row)
    return pd.DataFrame(rows)


def build_v32_first_hit_vs_path(detail: pd.DataFrame) -> pd.DataFrame:
    """20日固定窓で2Rに触れたかと、2RがStopより先だったかを分ける。"""
    if detail is None or detail.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        for signal_label in ["下落停止", "反発開始"]:
            part = detail[
                detail["銘柄"].eq(ticker_symbol)
                & detail["シグナル"].eq(signal_label)
                & detail["20日観察完了"].eq(True)
            ].copy()
            if part.empty:
                continue
            n = len(part)
            touched = part["2R到達"].eq(True)
            first_target = part["2R先着結果"].eq("Target先着")
            stop_first = part["2R先着結果"].eq("Stop先着")
            ambiguous = part["2R先着結果"].eq("同日両方到達・順序不明")
            late_after_stop = touched & stop_first
            rows.append({
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "20日観察完了": n,
                "20日内2R到達_順序不問": int(touched.sum()),
                "20日内2R到達_順序不問_%": float(touched.mean() * 100.0),
                "2RがStopより先_Target先着": int(first_target.sum()),
                "Target先着_%": float(first_target.mean() * 100.0),
                "Stop先着後に20日内2R到達": int(late_after_stop.sum()),
                "Stop先着後に20日内2R到達_%": float(late_after_stop.mean() * 100.0),
                "同日両方到達_順序不明": int(ambiguous.sum()),
                "2R到達だがTarget先着でない": int((touched & ~first_target).sum()),
            })
    return pd.DataFrame(rows)


def build_v32_audit(detail: pd.DataFrame, bundles: dict, horizon: int = 20) -> pd.DataFrame:
    if detail is None or detail.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            continue
        for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
            expected = len(bundle["signal_valid"].get(prefix_name, pd.DataFrame()))
            part = detail[
                detail["銘柄"].eq(ticker_symbol) & detail["シグナル"].eq(signal_label)
            ].copy()
            ids = pd.to_numeric(part["イベントID"], errors="coerce")
            unique_n = int(ids.dropna().nunique())
            duplicate_n = max(0, len(part) - unique_n)
            complete_n = int(part["20日観察完了"].eq(True).sum())
            incomplete_n = len(part) - complete_n
            ok = len(part) == expected and unique_n == expected and duplicate_n == 0 and complete_n + incomplete_n == expected
            rows.append({
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "R有効シグナル期待件数": expected,
                "v3.2経路行数": len(part),
                "ユニークイベントID": unique_n,
                "重複イベントID行": duplicate_n,
                f"{horizon}日観察完了": complete_n,
                f"{horizon}日観察未完了": incomplete_n,
                "監査": "OK" if ok else "要確認",
            })
    return pd.DataFrame(rows)



# ============================================================
# v3.3
# Stop先着 → その後20営業日内2R到達・価格経路分解
#
# v3.2で確認した「Stopが先だったが、その後20日内に2Rへ到達」ケースを
# 売買ルールを変更せず独立グループとして診断する。
# 主目的は、Stopを少し割っただけで戻ったのか、さらに大きく下落してから
# 戻ったのかを、計画時点1Rで正規化して確認すること。
# ============================================================

def build_v33_stop_recovery_detail(bundles: dict, horizon: int = 20) -> pd.DataFrame:
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        bundle = bundles.get(ticker_symbol)
        if not bundle:
            continue
        data = bundle["data"]
        net = bundle["net_sets"].get("Stop", pd.DataFrame())
        if net is None or net.empty:
            continue
        part = net[
            pd.to_numeric(net["Horizon"], errors="coerce").eq(horizon)
            & net["Outcome"].eq("Stop先着")
        ].copy()

        for _, row in part.iterrows():
            entry_date = pd.to_datetime(row.get("Entry_Date", pd.NaT), errors="coerce")
            stop_date = pd.to_datetime(row.get("Outcome_Date", pd.NaT), errors="coerce")
            entry_price = pd.to_numeric(pd.Series([row.get("Entry_Price", np.nan)]), errors="coerce").iloc[0]
            stop_price = pd.to_numeric(pd.Series([row.get("Stop_Price", np.nan)]), errors="coerce").iloc[0]
            target_price = pd.to_numeric(pd.Series([row.get("Target_Price", np.nan)]), errors="coerce").iloc[0]
            risk_1r = pd.to_numeric(pd.Series([row.get("Risk_1R", np.nan)]), errors="coerce").iloc[0]
            risk_pct = pd.to_numeric(pd.Series([row.get("Risk_1R_Percent", np.nan)]), errors="coerce").iloc[0]
            stop_day = pd.to_numeric(pd.Series([row.get("Outcome_Day", np.nan)]), errors="coerce").iloc[0]
            observed_hit = pd.to_numeric(pd.Series([row.get("Observed_Hit_Price", np.nan)]), errors="coerce").iloc[0]
            gross_stop_r = pd.to_numeric(pd.Series([row.get("Gross_Realized_R", np.nan)]), errors="coerce").iloc[0]
            exit_type = str(row.get("Exit_Type", ""))
            event_id = pd.to_numeric(pd.Series([row.get("BB_Event_ID", np.nan)]), errors="coerce").iloc[0]
            signal_date = pd.to_datetime(row.get("Signal_Date", pd.NaT), errors="coerce")

            base = {
                "銘柄": ticker_symbol,
                "イベントID": int(event_id) if pd.notna(event_id) else np.nan,
                "シグナル日": signal_date,
                "Entry日": entry_date,
                "Entry価格": entry_price,
                "Stop価格": stop_price,
                "2R価格": target_price,
                "1R": risk_1r,
                "1R率_%": risk_pct,
                "Stop到達日": stop_date,
                "Stop到達営業日": int(stop_day) if pd.notna(stop_day) else np.nan,
                "Stop約定種別": exit_type,
                "Stop観測約定価格": observed_hit,
                "Stop時Gross_R": gross_stop_r,
                "20日観察完了": False,
                "Stop先着後20日内2R到達": False,
                "2R初回到達日": pd.NaT,
                "2R初回到達営業日": np.nan,
                "Stop→2R営業日差": np.nan,
                "2R到達前確定MAE_R": np.nan,
                "2R到達前確定Stop超過幅_R": np.nan,
                "2R到達日まで最大MAE_R_日内順序不明": np.nan,
                "2R到達日までStop超過最大幅_R_日内順序不明": np.nan,
                "20日最大MAE_R": np.nan,
                "20日最大Stop超過幅_R": np.nan,
                "20日MFE_R": np.nan,
                "20日終値_R": np.nan,
            }

            if (
                pd.isna(entry_date) or pd.isna(entry_price) or pd.isna(stop_price)
                or pd.isna(target_price) or pd.isna(risk_1r) or float(risk_1r) <= 0
            ):
                rows.append(base)
                continue
            try:
                entry_pos = data.index.get_loc(entry_date)
            except KeyError:
                rows.append(base)
                continue
            if not isinstance(entry_pos, (int, np.integer)):
                rows.append(base)
                continue

            available = min(int(horizon), len(data) - int(entry_pos))
            if available < int(horizon):
                rows.append(base)
                continue

            window = data.iloc[int(entry_pos): int(entry_pos) + int(horizon)].copy()
            highs = pd.to_numeric(window["High"], errors="coerce")
            lows = pd.to_numeric(window["Low"], errors="coerce")
            closes = pd.to_numeric(window["Close"], errors="coerce")
            opens = pd.to_numeric(window["Open"], errors="coerce")
            if highs.isna().any() or lows.isna().any() or closes.isna().any() or opens.isna().any():
                rows.append(base)
                continue

            base["20日観察完了"] = True
            max_high = float(highs.max())
            min_low = float(lows.min())
            mae20 = (float(entry_price) - min_low) / float(risk_1r)
            mfe20 = (max_high - float(entry_price)) / float(risk_1r)
            base["20日最大MAE_R"] = float(mae20)
            base["20日最大Stop超過幅_R"] = float(max(0.0, mae20 - 1.0))
            base["20日MFE_R"] = float(mfe20)
            base["20日終値_R"] = float((float(closes.iloc[-1]) - float(entry_price)) / float(risk_1r))

            # Stop先着は既存first-hitで確定済み。ここではその後の固定20日窓で
            # 2Rへ初めて触れた営業日を探す。Open>=2Rなら寄り付き到達、
            # それ以外はHigh>=2Rを日中到達として扱う。
            target_pos = None
            for rel_pos in range(len(window)):
                if float(opens.iloc[rel_pos]) >= float(target_price) or float(highs.iloc[rel_pos]) >= float(target_price):
                    target_pos = rel_pos
                    break

            if target_pos is not None:
                target_day = int(target_pos) + 1
                # first-hitでStop先着が確定しているため、2R到達はStopと同日以降になる。
                if pd.isna(stop_day) or target_day >= int(stop_day):
                    base["Stop先着後20日内2R到達"] = True
                    base["2R初回到達日"] = window.index[int(target_pos)]
                    base["2R初回到達営業日"] = target_day
                    if pd.notna(stop_day):
                        base["Stop→2R営業日差"] = target_day - int(stop_day)
                    # 2R到達日のLowはTarget到達の前か後か日足では分からない。
                    # そのため、Target到達より前だと確定できる情報（前日までのLowと、
                    # 既に確定しているStop約定価格）から「確定MAE」を別計算する。
                    guaranteed_prices = []
                    if int(target_pos) > 0:
                        guaranteed_prices.append(float(lows.iloc[: int(target_pos)].min()))
                    if pd.notna(observed_hit):
                        guaranteed_prices.append(float(observed_hit))
                    else:
                        guaranteed_prices.append(float(stop_price))
                    guaranteed_min = min(guaranteed_prices)
                    guaranteed_mae = (float(entry_price) - guaranteed_min) / float(risk_1r)
                    base["2R到達前確定MAE_R"] = float(guaranteed_mae)
                    base["2R到達前確定Stop超過幅_R"] = float(max(0.0, guaranteed_mae - 1.0))

                    lows_to_target_day = lows.iloc[: int(target_pos) + 1]
                    min_to_target_day = float(lows_to_target_day.min())
                    mae_to_target_day = (float(entry_price) - min_to_target_day) / float(risk_1r)
                    base["2R到達日まで最大MAE_R_日内順序不明"] = float(mae_to_target_day)
                    base["2R到達日までStop超過最大幅_R_日内順序不明"] = float(max(0.0, mae_to_target_day - 1.0))

            rows.append(base)

    return pd.DataFrame(rows)


def build_v33_group_summary(detail: pd.DataFrame) -> pd.DataFrame:
    if detail is None or detail.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        complete = detail[
            detail["銘柄"].eq(ticker_symbol) & detail["20日観察完了"].eq(True)
        ].copy()
        if complete.empty:
            continue
        for recovered, label in [
            (True, "Stop先着→20日内2R到達"),
            (False, "Stop先着→20日内2R未到達"),
        ]:
            part = complete[complete["Stop先着後20日内2R到達"].eq(recovered)].copy()
            n = len(part)
            if n == 0:
                continue
            def num(col):
                return pd.to_numeric(part[col], errors="coerce").dropna()
            risk_pct = num("1R率_%")
            stop_day = num("Stop到達営業日")
            mae20 = num("20日最大MAE_R")
            stop_over20 = num("20日最大Stop超過幅_R")
            mfe20 = num("20日MFE_R")
            close20 = num("20日終値_R")
            target_day = num("2R初回到達営業日")
            gap_days = num("Stop→2R営業日差")
            mae_to_target = num("2R到達前確定MAE_R")
            over_to_target = num("2R到達前確定Stop超過幅_R")
            rows.append({
                "銘柄": ticker_symbol,
                "グループ": label,
                "件数": n,
                "Stop先着全体に占める_%": n / len(complete) * 100.0,
                "1R率中央値_%": float(risk_pct.median()) if not risk_pct.empty else np.nan,
                "Stop到達営業日中央値": float(stop_day.median()) if not stop_day.empty else np.nan,
                "2R初回到達営業日中央値": float(target_day.median()) if not target_day.empty else np.nan,
                "Stop→2R営業日差中央値": float(gap_days.median()) if not gap_days.empty else np.nan,
                "2R到達前確定MAE中央値_R": float(mae_to_target.median()) if not mae_to_target.empty else np.nan,
                "2R到達前確定MAE最大_R": float(mae_to_target.max()) if not mae_to_target.empty else np.nan,
                "2R到達前確定Stop超過幅中央値_R": float(over_to_target.median()) if not over_to_target.empty else np.nan,
                "2R到達前確定Stop超過幅最大_R": float(over_to_target.max()) if not over_to_target.empty else np.nan,
                "20日最大MAE中央値_R": float(mae20.median()) if not mae20.empty else np.nan,
                "20日最大Stop超過幅中央値_R": float(stop_over20.median()) if not stop_over20.empty else np.nan,
                "20日MFE中央値_R": float(mfe20.median()) if not mfe20.empty else np.nan,
                "20日終値中央値_R": float(close20.median()) if not close20.empty else np.nan,
            })
    return pd.DataFrame(rows)


def build_v33_audit(detail: pd.DataFrame, v32_detail: pd.DataFrame) -> pd.DataFrame:
    if detail is None or detail.empty or v32_detail is None or v32_detail.empty:
        return pd.DataFrame()
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        expected_part = v32_detail[
            v32_detail["銘柄"].eq(ticker_symbol)
            & v32_detail["シグナル"].eq("下落停止")
            & v32_detail["20日観察完了"].eq(True)
            & v32_detail["2R先着結果"].eq("Stop先着")
        ].copy()
        expected_stop = len(expected_part)
        expected_recovered = int(
            (expected_part["2R到達"].eq(True)).sum()
        )

        part = detail[
            detail["銘柄"].eq(ticker_symbol) & detail["20日観察完了"].eq(True)
        ].copy()
        ids = pd.to_numeric(part["イベントID"], errors="coerce")
        unique_n = int(ids.dropna().nunique())
        duplicate_n = max(0, len(part) - unique_n)
        recovered_n = int(part["Stop先着後20日内2R到達"].eq(True).sum())
        not_recovered_n = int(part["Stop先着後20日内2R到達"].eq(False).sum())
        ok = (
            len(part) == expected_stop
            and recovered_n == expected_recovered
            and recovered_n + not_recovered_n == len(part)
            and duplicate_n == 0
        )
        rows.append({
            "銘柄": ticker_symbol,
            "v3.2_20日完了Stop先着": expected_stop,
            "v3.3_Stop先着経路行数": len(part),
            "件数差": len(part) - expected_stop,
            "v3.2_Stop先着後2R到達": expected_recovered,
            "v3.3_Stop先着後2R到達": recovered_n,
            "2R到達件数差": recovered_n - expected_recovered,
            "v3.3_Stop先着後2R未到達": not_recovered_n,
            "ユニークイベントID": unique_n,
            "重複イベントID行": duplicate_n,
            "監査": "OK" if ok else "要確認",
        })
    return pd.DataFrame(rows)

# ============================================================
# タイトル
# ============================================================

# ============================================================
# v3.4.1
# 固定ルール・別5年間による時間方向検証
# ============================================================

V34_WARMUP_CALENDAR_DAYS = 400

# v3.4.1: 検証窓を完全固定する。実行日・最新株価日では動かさない。
V34_PRIOR_START = pd.Timestamp("2016-10-01")
V34_PRIOR_END = pd.Timestamp("2021-09-30")
V34_CURRENT_START = pd.Timestamp("2021-10-01")
V34_CURRENT_END = pd.Timestamp("2026-09-30")


@st.cache_data(persist="disk", show_spinner=False)
def prepare_data_fixed_window(
    ticker_symbol: str,
    evaluation_start,
    evaluation_end,
    warmup_calendar_days: int = V34_WARMUP_CALENDAR_DAYS,
) -> pd.DataFrame:
    """
    評価開始前のウォームアップでBB / BandWidth等を計算し、
    評価窓へ入ってからBBイベントIDを新規に開始する。
    ウォームアップ日はイベント件数・Entry・損益へ含めない。
    """
    eval_start = pd.Timestamp(evaluation_start).normalize()
    eval_end = pd.Timestamp(evaluation_end).normalize()
    warmup_start = eval_start - pd.Timedelta(days=int(warmup_calendar_days))

    raw = get_stock_data_range(ticker_symbol, warmup_start, eval_end)
    if raw is None or raw.empty:
        return pd.DataFrame()

    # 事前情報として使える指標・前日比較はウォームアップ込みで計算する。
    df = calculate_bollinger_bands(raw, BB_PERIOD, BB_STD)
    df = calculate_bandwidth(df)
    df = calculate_lower_band_distance(df)
    df = calculate_bandwidth_state(df, SQUEEZE_LOOKBACK)
    df["BandWidth_Direction"] = df.apply(classify_bandwidth_direction, axis=1)
    df["Squeeze_State"] = df.apply(classify_squeeze_state, axis=1)
    df = calculate_lower_band_events(df)
    df["Lower_Band_Event"] = df.apply(classify_lower_band_event, axis=1)
    df = calculate_downside_expansion(df)
    df["Downside_Expansion_State"] = df.apply(classify_downside_expansion, axis=1)
    df = calculate_decline_stop_conditions(df)
    df = calculate_rebound_start_conditions(df)

    # ここで評価窓へ切る。イベントIDは評価窓の外から持ち込まない。
    df = df.loc[(df.index >= eval_start) & (df.index <= eval_end)].copy()
    if df.empty:
        return pd.DataFrame()

    df = calculate_lower_event_window(df, LOWER_EVENT_OBSERVATION_DAYS)
    df = calculate_decline_stop_candidates(df)
    df["Decline_Stop_State"] = df.apply(classify_decline_stop, axis=1)
    df = calculate_fixed_bb_event_units(df, LOWER_EVENT_OBSERVATION_DAYS)
    df = calculate_event_completion(df, LOWER_EVENT_OBSERVATION_DAYS)
    df = calculate_first_decline_stop_per_event(df)
    df = calculate_first_rebound_start_per_event(df)
    df = calculate_first_stop_bb_state(df)
    df = calculate_first_rebound_bb_state(df)
    df = calculate_event_results(df)
    df = calculate_r_design(df, "First_Decline_Stop_In_Event", "Stop")
    df = calculate_r_design(df, "First_Rebound_Start_In_Event", "Rebound")
    df = calculate_wait_rebound_after_stop(df)
    df = calculate_r_design(df, "Wait_Rebound_After_Stop", "WaitRebound")
    return df


def build_v34_windows(latest_date=None):
    """v3.4.1固定窓。latest_dateは後方互換のため受け取るが使用しない。"""
    return {
        "前5年": (V34_PRIOR_START, V34_PRIOR_END),
        "現5年": (V34_CURRENT_START, V34_CURRENT_END),
    }


def build_v34_audit(period_bundles: dict, windows: dict) -> pd.DataFrame:
    rows = []
    prior_start, prior_end = windows.get("前5年", (pd.NaT, pd.NaT))
    current_start, current_end = windows.get("現5年", (pd.NaT, pd.NaT))
    overlap = not (
        pd.isna(prior_end) or pd.isna(current_start) or prior_end < current_start
    )

    for period_name in ["前5年", "現5年"]:
        req_start, req_end = windows.get(period_name, (pd.NaT, pd.NaT))
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                rows.append({
                    "期間": period_name,
                    "銘柄": ticker_symbol,
                    "評価開始日": req_start,
                    "評価終了日": req_end,
                    "実データ開始日": pd.NaT,
                    "実データ終了日": pd.NaT,
                    "観察完了BBイベント": 0,
                    "独立台帳行数": 0,
                    "ユニークイベントID": 0,
                    "重複イベントID行": 0,
                    "下落停止R計算可能": 0,
                    "反発開始R計算可能": 0,
                    "期間重複": "なし" if not overlap else "あり",
                    "監査": "データなし",
                })
                continue

            data = bundle.get("data", pd.DataFrame())
            ledger = bundle.get("ledger", pd.DataFrame())
            completed_count = len(bundle.get("completed_starts", pd.DataFrame()))
            ledger_count = len(ledger)
            unique_count = (
                int(pd.to_numeric(ledger["イベントID"], errors="coerce").nunique())
                if ledger is not None and not ledger.empty else 0
            )
            duplicate_count = max(0, ledger_count - unique_count)
            actual_start = data.index.min() if data is not None and not data.empty else pd.NaT
            actual_end = data.index.max() if data is not None and not data.empty else pd.NaT
            date_ok = (
                pd.notna(actual_start) and pd.notna(actual_end)
                and actual_start >= pd.Timestamp(req_start)
                and actual_end <= pd.Timestamp(req_end)
            )
            audit_ok = (
                date_ok
                and not overlap
                and completed_count == ledger_count == unique_count
                and duplicate_count == 0
            )
            rows.append({
                "期間": period_name,
                "銘柄": ticker_symbol,
                "評価開始日": req_start,
                "評価終了日": req_end,
                "実データ開始日": actual_start,
                "実データ終了日": actual_end,
                "観察完了BBイベント": completed_count,
                "独立台帳行数": ledger_count,
                "ユニークイベントID": unique_count,
                "重複イベントID行": duplicate_count,
                "下落停止R計算可能": len(bundle.get("signal_valid", {}).get("Stop", pd.DataFrame())),
                "反発開始R計算可能": len(bundle.get("signal_valid", {}).get("Rebound", pd.DataFrame())),
                "期間重複": "なし" if not overlap else "あり",
                "監査": "OK" if audit_ok else "要確認",
            })
    return pd.DataFrame(rows)


def build_v34_net_summary(period_bundles: dict) -> pd.DataFrame:
    rows = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            completed_count = len(bundle.get("completed_starts", pd.DataFrame()))
            for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                results = bundle.get("net_sets", {}).get(prefix_name, pd.DataFrame())
                if results is None or results.empty:
                    continue
                for horizon in FIRST_HIT_HORIZONS:
                    part = results[
                        pd.to_numeric(results["Horizon"], errors="coerce").eq(horizon)
                    ].copy()
                    valid = part[part["Net_R_Valid"].eq(True)].copy()
                    gross_r = pd.to_numeric(valid["Gross_Realized_R"], errors="coerce").dropna()
                    net_r = pd.to_numeric(valid["Net_Realized_R"], errors="coerce").dropna()
                    cost_r = pd.to_numeric(valid["Cost_R"], errors="coerce").dropna()
                    rows.append({
                        "期間": period_name,
                        "銘柄": ticker_symbol,
                        "シグナル": signal_label,
                        "保有期間": f"{horizon}営業日",
                        "観察完了BBイベント": completed_count,
                        "シグナル対象": len(part),
                        "Net_R計算可能": len(net_r),
                        "Gross合計R": float(gross_r.sum()) if not gross_r.empty else np.nan,
                        "Net合計R": float(net_r.sum()) if not net_r.empty else np.nan,
                        "コスト合計R": float(cost_r.sum()) if not cost_r.empty else np.nan,
                        "Net平均R": float(net_r.mean()) if not net_r.empty else np.nan,
                        "Net中央値R": float(net_r.median()) if not net_r.empty else np.nan,
                        "NetプラスR": int((net_r > 0).sum()),
                        "NetマイナスR": int((net_r < 0).sum()),
                        "NetゼロR": int((net_r.abs() <= 1e-12).sum()),
                    })
    return pd.DataFrame(rows)


def build_v34_20d_difference(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty:
        return pd.DataFrame()
    rows = []
    part = summary[summary["保有期間"].eq("20営業日")].copy()
    for ticker_symbol in ["GOOG", "NVDA"]:
        for signal_label in ["下落停止", "反発開始"]:
            g = part[(part["銘柄"].eq(ticker_symbol)) & (part["シグナル"].eq(signal_label))]
            prior = g[g["期間"].eq("前5年")]
            current = g[g["期間"].eq("現5年")]
            if prior.empty or current.empty:
                continue
            a = prior.iloc[0]
            b = current.iloc[0]
            rows.append({
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "前5年_Net_R計算可能": int(a["Net_R計算可能"]),
                "現5年_Net_R計算可能": int(b["Net_R計算可能"]),
                "前5年_Net合計R": a["Net合計R"],
                "現5年_Net合計R": b["Net合計R"],
                "前5年_Net平均R": a["Net平均R"],
                "現5年_Net平均R": b["Net平均R"],
                "平均R差_現5年-前5年": (
                    float(b["Net平均R"]) - float(a["Net平均R"])
                    if pd.notna(a["Net平均R"]) and pd.notna(b["Net平均R"])
                    else np.nan
                ),
                "前5年_Net中央値R": a["Net中央値R"],
                "現5年_Net中央値R": b["Net中央値R"],
                "前5年_プラスR": int(a["NetプラスR"]),
                "前5年_マイナスR": int(a["NetマイナスR"]),
                "現5年_プラスR": int(b["NetプラスR"]),
                "現5年_マイナスR": int(b["NetマイナスR"]),
            })
    return pd.DataFrame(rows)


def build_v34_reconciliation(audit: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    """
    v3.4.1最終監査。
    130番の母集団件数と131番の全6集計行が同じ母集団を参照していることまで確認する。
    """
    rows = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            a = audit[(audit["期間"].eq(period_name)) & (audit["銘柄"].eq(ticker_symbol))]
            s = summary[(summary["期間"].eq(period_name)) & (summary["銘柄"].eq(ticker_symbol))].copy()

            expected_rows = 2 * len(FIRST_HIT_HORIZONS)
            actual_rows = len(s)
            audit_status = a.iloc[0]["監査"] if not a.empty else "データなし"
            audit_completed = int(a.iloc[0]["観察完了BBイベント"]) if not a.empty else 0
            audit_stop_r = int(a.iloc[0]["下落停止R計算可能"]) if not a.empty else 0
            audit_rebound_r = int(a.iloc[0]["反発開始R計算可能"]) if not a.empty else 0

            if s.empty:
                summary_min = 0
                summary_max = 0
                mother_match = False
                combo_unique = 0
                signal_count_match = False
            else:
                summary_counts = pd.to_numeric(
                    s["観察完了BBイベント"], errors="coerce"
                ).dropna()
                summary_min = int(summary_counts.min()) if not summary_counts.empty else 0
                summary_max = int(summary_counts.max()) if not summary_counts.empty else 0
                mother_match = (
                    len(summary_counts) == actual_rows
                    and summary_min == audit_completed
                    and summary_max == audit_completed
                )

                combo_unique = int(
                    s[["シグナル", "保有期間"]].drop_duplicates().shape[0]
                )
                stop_counts = pd.to_numeric(
                    s.loc[s["シグナル"].eq("下落停止"), "シグナル対象"],
                    errors="coerce",
                ).dropna()
                rebound_counts = pd.to_numeric(
                    s.loc[s["シグナル"].eq("反発開始"), "シグナル対象"],
                    errors="coerce",
                ).dropna()
                signal_count_match = (
                    len(stop_counts) == len(FIRST_HIT_HORIZONS)
                    and len(rebound_counts) == len(FIRST_HIT_HORIZONS)
                    and bool((stop_counts == audit_stop_r).all())
                    and bool((rebound_counts == audit_rebound_r).all())
                )

            row_count_ok = actual_rows == expected_rows
            combo_ok = combo_unique == expected_rows
            final_ok = (
                audit_status == "OK"
                and row_count_ok
                and combo_ok
                and mother_match
                and signal_count_match
            )

            rows.append({
                "期間": period_name,
                "銘柄": ticker_symbol,
                "監査サマリー": audit_status,
                "130_観察完了BBイベント": audit_completed,
                "131_母集団件数最小": summary_min,
                "131_母集団件数最大": summary_max,
                "母集団件数一致": "OK" if mother_match else "要確認",
                "130_下落停止R計算可能": audit_stop_r,
                "130_反発開始R計算可能": audit_rebound_r,
                "131_シグナル対象件数一致": "OK" if signal_count_match else "要確認",
                "期待集計行数": expected_rows,
                "実集計行数": actual_rows,
                "集計行数差": actual_rows - expected_rows,
                "シグナル×保有期間ユニーク数": combo_unique,
                "最終監査": "OK" if final_ok else "要確認",
            })
    return pd.DataFrame(rows)


@st.cache_data(persist="disk", show_spinner=False)
def build_v342_cached_time_validation(
    commission_rate: float,
    slippage_rate: float,
):
    """
    v3.4.2 runtime optimization.
    v3.4.1の固定5年検証を条件ごと丸ごとキャッシュする。
    売買条件・期間・集計式は変更しない。
    """
    windows = build_v34_windows()
    period_bundles = {"前5年": {}, "現5年": {}}

    for period_name in ["前5年", "現5年"]:
        eval_start, eval_end = windows[period_name]
        for ticker_symbol in ["GOOG", "NVDA"]:
            prepared = prepare_data_fixed_window(
                ticker_symbol,
                eval_start,
                eval_end,
                V34_WARMUP_CALENDAR_DAYS,
            )
            period_bundles[period_name][ticker_symbol] = build_v30_ticker_bundle(
                ticker_symbol,
                prepared,
                commission_rate,
                slippage_rate,
            )

    audit = build_v34_audit(period_bundles, windows)
    net_summary = build_v34_net_summary(period_bundles)
    difference_20d = build_v34_20d_difference(net_summary)
    reconciliation = build_v34_reconciliation(audit, net_summary)
    return period_bundles, windows, audit, net_summary, difference_20d, reconciliation




# ============================================================
# v3.4.3 軽量サマリーキャッシュ
# ============================================================

@st.cache_data(persist="disk", show_spinner=False)
def build_v343_current_results(
    commission_rate: float,
    slippage_rate: float,
):
    """
    固定5年検証の画面表示に必要な小さい表だけを返す。
    大きな period_bundles を main.py 側へ返さないことで、
    Streamlit の再実行・シリアライズ・メモリ負荷を下げる。
    売買条件と集計式は v3.4.1 / v3.4.2 から変更しない。
    """
    windows = build_v34_windows()
    period_bundles = {"前5年": {}, "現5年": {}}

    for period_name in ["前5年", "現5年"]:
        eval_start, eval_end = windows[period_name]
        for ticker_symbol in ["GOOG", "NVDA"]:
            prepared = prepare_data_fixed_window(
                ticker_symbol,
                eval_start,
                eval_end,
                V34_WARMUP_CALENDAR_DAYS,
            )
            period_bundles[period_name][ticker_symbol] = build_v30_ticker_bundle(
                ticker_symbol,
                prepared,
                commission_rate,
                slippage_rate,
            )

    audit = build_v34_audit(period_bundles, windows)
    net_summary = build_v34_net_summary(period_bundles)
    difference_20d = build_v34_20d_difference(net_summary)
    reconciliation = build_v34_reconciliation(audit, net_summary)

    # main.py へは必要な小さい結果だけ返す。
    return windows, audit, net_summary, difference_20d, reconciliation

# ============================================================
# v3.5.0
# 前5年 vs 現5年・20日価格経路 / 決済構造の原因分解
#
# 目的:
# ・v3.4.1で確認した前5年→現5年の成績悪化について、売買条件を変更せず原因を分解する。
# ・20日2Rの Target先着 / Stop先着 / 期間内未到達 の比率を比較する。
# ・固定20営業日の MFE / MAE / 20日終値R を比較する。
# ・計画時点1R率の分布を比較する。
# ・ここでは新しいフィルター、Stop幅変更、銘柄専用条件を採用しない。
# ============================================================


def build_v35_exit_structure(period_bundles: dict) -> pd.DataFrame:
    """20日・2Rの先着/未到達構造を、前5年と現5年で同じ定義のまま集計する。"""
    rows = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                results = bundle.get("net_sets", {}).get(prefix_name, pd.DataFrame())
                if results is None or results.empty:
                    continue
                part = results[pd.to_numeric(results["Horizon"], errors="coerce").eq(20)].copy()
                n = len(part)
                outcome = part["Outcome"].fillna("").astype(str)
                target_n = int(outcome.eq("Target先着").sum())
                stop_n = int(outcome.eq("Stop先着").sum())
                timeout_n = int(outcome.eq("期間内未到達").sum())
                ambiguous_n = int(outcome.eq("同日両方到達・順序不明").sum())
                insufficient_n = int(outcome.eq("将来データ不足").sum())
                net_valid_n = int(part["Net_R_Valid"].eq(True).sum()) if "Net_R_Valid" in part.columns else 0
                rows.append({
                    "期間": period_name,
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "20日対象": n,
                    "Target先着": target_n,
                    "Target先着_%": target_n / n * 100.0 if n else np.nan,
                    "Stop先着": stop_n,
                    "Stop先着_%": stop_n / n * 100.0 if n else np.nan,
                    "期間内未到達": timeout_n,
                    "期間内未到達_%": timeout_n / n * 100.0 if n else np.nan,
                    "同日両方_順序不明": ambiguous_n,
                    "将来データ不足": insufficient_n,
                    "Net_R計算可能": net_valid_n,
                })
    return pd.DataFrame(rows)


def build_v35_path_summary(period_bundles: dict, horizon: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    """固定20営業日の価格経路を最後まで観察し、MFE/MAEを期間別に集計する。"""
    detail_parts = []
    summary_rows = []
    for period_name in ["前5年", "現5年"]:
        bundles = period_bundles.get(period_name, {})
        detail = build_v32_path_detail(bundles, horizon=horizon)
        if detail is None or detail.empty:
            continue
        detail = detail.copy()
        detail.insert(0, "期間", period_name)
        detail_parts.append(detail)

        for ticker_symbol in ["GOOG", "NVDA"]:
            for signal_label in ["下落停止", "反発開始"]:
                all_part = detail[
                    detail["銘柄"].eq(ticker_symbol)
                    & detail["シグナル"].eq(signal_label)
                ].copy()
                if all_part.empty:
                    continue
                part = all_part[all_part["20日観察完了"].eq(True)].copy()
                n = len(part)
                mfe = pd.to_numeric(part["MFE_R"], errors="coerce").dropna()
                mae = pd.to_numeric(part["MAE_R"], errors="coerce").dropna()
                close20 = pd.to_numeric(part["20日終値_R"], errors="coerce").dropna()
                touch2 = int(part["2R到達"].eq(True).sum()) if n else 0
                mae1 = int(part["MAE1R以上"].eq(True).sum()) if n else 0
                summary_rows.append({
                    "期間": period_name,
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "R有効シグナル": len(all_part),
                    "20日観察完了": n,
                    "20日観察未完了": len(all_part) - n,
                    "MFE平均R": float(mfe.mean()) if not mfe.empty else np.nan,
                    "MFE中央値R": float(mfe.median()) if not mfe.empty else np.nan,
                    "20日内2R到達": touch2,
                    "20日内2R到達_%": touch2 / n * 100.0 if n else np.nan,
                    "MAE平均R": float(mae.mean()) if not mae.empty else np.nan,
                    "MAE中央値R": float(mae.median()) if not mae.empty else np.nan,
                    "MAE1R以上": mae1,
                    "MAE1R以上_%": mae1 / n * 100.0 if n else np.nan,
                    "20日終値平均R": float(close20.mean()) if not close20.empty else np.nan,
                    "20日終値中央値R": float(close20.median()) if not close20.empty else np.nan,
                })

    detail_all = pd.concat(detail_parts, ignore_index=True) if detail_parts else pd.DataFrame()
    return detail_all, pd.DataFrame(summary_rows)


def build_v35_risk_summary(period_bundles: dict) -> pd.DataFrame:
    """Entry時点で固定された1R幅を、後の結果を使わず期間別に記述する。"""
    rows = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                signals = bundle.get("signal_valid", {}).get(prefix_name, pd.DataFrame())
                if signals is None:
                    signals = pd.DataFrame()
                risk_col = f"{prefix_name}_Risk_1R_Percent"
                if signals.empty or risk_col not in signals.columns:
                    risk = pd.Series(dtype=float)
                else:
                    risk = pd.to_numeric(signals[risk_col], errors="coerce").dropna()
                rows.append({
                    "期間": period_name,
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "R有効シグナル": len(signals),
                    "1R率計算可能": len(risk),
                    "1R率平均_%": float(risk.mean()) if not risk.empty else np.nan,
                    "1R率中央値_%": float(risk.median()) if not risk.empty else np.nan,
                    "1R率25%点_%": float(risk.quantile(0.25)) if not risk.empty else np.nan,
                    "1R率75%点_%": float(risk.quantile(0.75)) if not risk.empty else np.nan,
                    "1R率最小_%": float(risk.min()) if not risk.empty else np.nan,
                    "1R率最大_%": float(risk.max()) if not risk.empty else np.nan,
                    "1R率1%未満": int((risk < 1.0).sum()) if not risk.empty else 0,
                    "1R率1%未満_%": float((risk < 1.0).mean() * 100.0) if not risk.empty else np.nan,
                })
    return pd.DataFrame(rows)


def build_v35_period_difference(
    exit_summary: pd.DataFrame,
    path_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
) -> pd.DataFrame:
    """原因分解の主要指標を4組に圧縮し、前5年→現5年の差を直接表示する。"""
    rows = []
    for ticker_symbol in ["GOOG", "NVDA"]:
        for signal_label in ["下落停止", "反発開始"]:
            def one(df, period):
                g = df[
                    df["期間"].eq(period)
                    & df["銘柄"].eq(ticker_symbol)
                    & df["シグナル"].eq(signal_label)
                ]
                return None if g.empty else g.iloc[0]

            ep = one(exit_summary, "前5年")
            ec = one(exit_summary, "現5年")
            pp = one(path_summary, "前5年")
            pc = one(path_summary, "現5年")
            rp = one(risk_summary, "前5年")
            rc = one(risk_summary, "現5年")
            if any(x is None for x in [ep, ec, pp, pc, rp, rc]):
                continue

            def diff(current, prior, key):
                a = pd.to_numeric(pd.Series([prior.get(key, np.nan)]), errors="coerce").iloc[0]
                b = pd.to_numeric(pd.Series([current.get(key, np.nan)]), errors="coerce").iloc[0]
                return float(b - a) if pd.notna(a) and pd.notna(b) else np.nan

            rows.append({
                "銘柄": ticker_symbol,
                "シグナル": signal_label,
                "前5年_Target先着_%": ep["Target先着_%"],
                "現5年_Target先着_%": ec["Target先着_%"],
                "Target先着差_ポイント": diff(ec, ep, "Target先着_%"),
                "前5年_Stop先着_%": ep["Stop先着_%"],
                "現5年_Stop先着_%": ec["Stop先着_%"],
                "Stop先着差_ポイント": diff(ec, ep, "Stop先着_%"),
                "前5年_MFE中央値R": pp["MFE中央値R"],
                "現5年_MFE中央値R": pc["MFE中央値R"],
                "MFE中央値差_R": diff(pc, pp, "MFE中央値R"),
                "前5年_MAE中央値R": pp["MAE中央値R"],
                "現5年_MAE中央値R": pc["MAE中央値R"],
                "MAE中央値差_R": diff(pc, pp, "MAE中央値R"),
                "前5年_20日終値中央値R": pp["20日終値中央値R"],
                "現5年_20日終値中央値R": pc["20日終値中央値R"],
                "20日終値中央値差_R": diff(pc, pp, "20日終値中央値R"),
                "前5年_1R率中央値_%": rp["1R率中央値_%"],
                "現5年_1R率中央値_%": rc["1R率中央値_%"],
                "1R率中央値差_ポイント": diff(rc, rp, "1R率中央値_%"),
            })
    return pd.DataFrame(rows)


def build_v35_reconciliation(
    period_bundles: dict,
    exit_summary: pd.DataFrame,
    path_detail: pd.DataFrame,
    risk_summary: pd.DataFrame,
) -> pd.DataFrame:
    """v3.5の各原因分解表が同じR有効シグナル母集団から始まっているか監査する。"""
    rows = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            for prefix_name, signal_label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                expected = len(bundle.get("signal_valid", {}).get(prefix_name, pd.DataFrame()))
                e = exit_summary[
                    exit_summary["期間"].eq(period_name)
                    & exit_summary["銘柄"].eq(ticker_symbol)
                    & exit_summary["シグナル"].eq(signal_label)
                ]
                p = path_detail[
                    path_detail["期間"].eq(period_name)
                    & path_detail["銘柄"].eq(ticker_symbol)
                    & path_detail["シグナル"].eq(signal_label)
                ] if path_detail is not None and not path_detail.empty else pd.DataFrame()
                r = risk_summary[
                    risk_summary["期間"].eq(period_name)
                    & risk_summary["銘柄"].eq(ticker_symbol)
                    & risk_summary["シグナル"].eq(signal_label)
                ]

                exit_n = int(e.iloc[0]["20日対象"]) if len(e) == 1 else -1
                path_n = len(p)
                path_complete = int(p["20日観察完了"].eq(True).sum()) if not p.empty else 0
                risk_n = int(r.iloc[0]["R有効シグナル"]) if len(r) == 1 else -1
                unique_event = (
                    int(pd.to_numeric(p["イベントID"], errors="coerce").nunique())
                    if not p.empty else 0
                )
                ok = (
                    len(e) == 1
                    and len(r) == 1
                    and expected == exit_n == path_n == risk_n == unique_event
                    and 0 <= path_complete <= expected
                )
                rows.append({
                    "期間": period_name,
                    "銘柄": ticker_symbol,
                    "シグナル": signal_label,
                    "R有効シグナル": expected,
                    "134_20日対象": exit_n,
                    "135_価格経路行数": path_n,
                    "135_20日観察完了": path_complete,
                    "136_1R率母集団": risk_n,
                    "ユニークイベントID": unique_event,
                    "母集団一致": "OK" if ok else "要確認",
                })
    return pd.DataFrame(rows)


@st.cache_data(persist="disk", show_spinner=False)
def build_v350_current_results(
    commission_rate: float,
    slippage_rate: float,
):
    """
    v3.4.1の固定ルール・固定2つの5年窓をそのまま再利用し、
    v3.5の原因分解表まで一度に作る。main.pyへは小さい表だけ返す。
    """
    windows = build_v34_windows()
    period_bundles = {"前5年": {}, "現5年": {}}

    for period_name in ["前5年", "現5年"]:
        eval_start, eval_end = windows[period_name]
        for ticker_symbol in ["GOOG", "NVDA"]:
            prepared = prepare_data_fixed_window(
                ticker_symbol,
                eval_start,
                eval_end,
                V34_WARMUP_CALENDAR_DAYS,
            )
            period_bundles[period_name][ticker_symbol] = build_v30_ticker_bundle(
                ticker_symbol,
                prepared,
                commission_rate,
                slippage_rate,
            )

    audit = build_v34_audit(period_bundles, windows)
    net_summary = build_v34_net_summary(period_bundles)
    difference_20d = build_v34_20d_difference(net_summary)
    reconciliation = build_v34_reconciliation(audit, net_summary)

    exit_summary = build_v35_exit_structure(period_bundles)
    path_detail, path_summary = build_v35_path_summary(period_bundles, horizon=20)
    risk_summary = build_v35_risk_summary(period_bundles)
    period_difference = build_v35_period_difference(exit_summary, path_summary, risk_summary)
    v35_audit = build_v35_reconciliation(
        period_bundles, exit_summary, path_detail, risk_summary
    )

    return (
        windows,
        audit,
        net_summary,
        difference_20d,
        reconciliation,
        exit_summary,
        path_summary,
        risk_summary,
        period_difference,
        v35_audit,
    )


# ============================================================
# v3.6.1 相場環境・レジーム診断
# 売買条件は変更せず、シグナル確定日に既に分かっている情報だけを記録する。
# ============================================================

def _v36_signal_environment(period_bundles: dict) -> pd.DataFrame:
    parts = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            data = bundle.get("data", pd.DataFrame())
            for prefix, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                sig = bundle.get("signal_valid", {}).get(prefix, pd.DataFrame()).copy()
                if sig.empty:
                    continue

                # v3.6.1修正:
                # pandas.mergeは元のDatetimeIndexをRangeIndexへ変える。
                # v3.6.0はmerge後のindexでVolを参照したため全件NaNになっていた。
                # 必ずmerge前にシグナル日を列として保存する。
                sig["_Signal_Date_v361"] = pd.to_datetime(sig.index).values

                # 20日2Rの実現結果は分類ラベルとしてのみ後から結合する。
                out = bundle.get("net_sets", {}).get(prefix, pd.DataFrame()).copy()
                if not out.empty:
                    out = out[pd.to_numeric(out["Horizon"], errors="coerce").eq(20)].copy()
                    out = out[["BB_Event_ID", "Outcome"]].drop_duplicates("BB_Event_ID")
                    sig = sig.merge(out, on="BB_Event_ID", how="left", validate="one_to_one")
                else:
                    sig["Outcome"] = np.nan

                # 過去20営業日の終値リターン標準偏差。シグナル日までの情報のみ。
                if "HistVol_20D_Pct" not in data.columns:
                    close = pd.to_numeric(data["Close"], errors="coerce")
                    histvol = close.pct_change().rolling(20, min_periods=20).std(ddof=0) * np.sqrt(252) * 100.0
                    hv_map = pd.Series(histvol.values, index=pd.to_datetime(data.index))
                else:
                    hv_map = pd.Series(
                        pd.to_numeric(data["HistVol_20D_Pct"], errors="coerce").values,
                        index=pd.to_datetime(data.index),
                    )
                sig["HistVol_20D_Pct"] = pd.to_datetime(sig["_Signal_Date_v361"]).map(hv_map)
                sig.drop(columns=["_Signal_Date_v361"], inplace=True)
                sig["期間"] = period_name
                sig["銘柄"] = ticker_symbol
                sig["シグナル"] = label
                parts.append(sig)
    return pd.concat(parts, ignore_index=False) if parts else pd.DataFrame()


def build_v36_environment_summary(env: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if env is None or env.empty:
        return pd.DataFrame()
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            for signal in ["下落停止", "反発開始"]:
                p = env[(env["期間"] == period) & (env["銘柄"] == ticker) & (env["シグナル"] == signal)].copy()
                if p.empty:
                    continue
                bw = pd.to_numeric(p["BandWidth"], errors="coerce")
                nbw = pd.to_numeric(p["Normalized_BandWidth"], errors="coerce")
                hv = pd.to_numeric(p["HistVol_20D_Pct"], errors="coerce")
                direction = p["BandWidth_Direction"].fillna("判定不可").astype(str)
                rows.append({
                    "期間": period, "銘柄": ticker, "シグナル": signal, "対象": len(p),
                    "BandWidth中央値_%": bw.median(),
                    "正規化BandWidth中央値": nbw.median(),
                    "低BandWidth帯_%": (nbw.le(0.25).mean() * 100.0) if nbw.notna().any() else np.nan,
                    "高BandWidth帯_%": (nbw.ge(0.75).mean() * 100.0) if nbw.notna().any() else np.nan,
                    "BW収縮中_%": (direction.eq("収縮中").mean() * 100.0),
                    "BW拡大中_%": (direction.eq("拡大中").mean() * 100.0),
                    "過去20日年率Vol中央値_%": hv.median(),
                })
    return pd.DataFrame(rows)


def build_v36_outcome_environment(env: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if env is None or env.empty:
        return pd.DataFrame()
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            for signal in ["下落停止", "反発開始"]:
                base = env[(env["期間"] == period) & (env["銘柄"] == ticker) & (env["シグナル"] == signal)].copy()
                for outcome in ["Target先着", "Stop先着", "期間内未到達"]:
                    p = base[base["Outcome"].fillna("").astype(str).eq(outcome)].copy()
                    if p.empty:
                        continue
                    nbw = pd.to_numeric(p["Normalized_BandWidth"], errors="coerce")
                    hv = pd.to_numeric(p["HistVol_20D_Pct"], errors="coerce")
                    bw = pd.to_numeric(p["BandWidth"], errors="coerce")
                    direction = p["BandWidth_Direction"].fillna("判定不可").astype(str)
                    rows.append({
                        "期間": period, "銘柄": ticker, "シグナル": signal, "20日結果": outcome, "件数": len(p),
                        "BandWidth中央値_%": bw.median(),
                        "正規化BandWidth中央値": nbw.median(),
                        "低BandWidth帯_%": nbw.le(0.25).mean() * 100.0 if nbw.notna().any() else np.nan,
                        "BW収縮中_%": direction.eq("収縮中").mean() * 100.0,
                        "BW拡大中_%": direction.eq("拡大中").mean() * 100.0,
                        "過去20日年率Vol中央値_%": hv.median(),
                    })
    return pd.DataFrame(rows)


def build_v36_period_difference(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if summary is None or summary.empty:
        return pd.DataFrame()
    metrics = ["BandWidth中央値_%", "正規化BandWidth中央値", "低BandWidth帯_%", "高BandWidth帯_%", "BW収縮中_%", "BW拡大中_%", "過去20日年率Vol中央値_%"]
    for ticker in ["GOOG", "NVDA"]:
        for signal in ["下落停止", "反発開始"]:
            a = summary[(summary["期間"] == "前5年") & (summary["銘柄"] == ticker) & (summary["シグナル"] == signal)]
            b = summary[(summary["期間"] == "現5年") & (summary["銘柄"] == ticker) & (summary["シグナル"] == signal)]
            if len(a) != 1 or len(b) != 1:
                continue
            row = {"銘柄": ticker, "シグナル": signal}
            for m in metrics:
                av = pd.to_numeric(pd.Series([a.iloc[0][m]]), errors="coerce").iloc[0]
                bv = pd.to_numeric(pd.Series([b.iloc[0][m]]), errors="coerce").iloc[0]
                row[f"前5年_{m}"] = av
                row[f"現5年_{m}"] = bv
                row[f"差_現-前_{m}"] = bv - av if pd.notna(av) and pd.notna(bv) else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def build_v36_audit(period_bundles: dict, env: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period, {}).get(ticker)
            if not bundle:
                continue
            for prefix, signal in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                expected = len(bundle.get("signal_valid", {}).get(prefix, pd.DataFrame()))
                p = env[(env["期間"] == period) & (env["銘柄"] == ticker) & (env["シグナル"] == signal)].copy()
                unique = pd.to_numeric(p.get("BB_Event_ID"), errors="coerce").nunique() if not p.empty else 0
                bw_n = pd.to_numeric(p.get("Normalized_BandWidth"), errors="coerce").notna().sum() if not p.empty else 0
                hv_n = pd.to_numeric(p.get("HistVol_20D_Pct"), errors="coerce").notna().sum() if not p.empty else 0
                rows.append({"期間": period, "銘柄": ticker, "シグナル": signal, "R有効シグナル": expected,
                             "v3.6環境行数": len(p), "ユニークイベントID": int(unique),
                             "正規化BW計算可能": int(bw_n), "過去20日Vol計算可能": int(hv_n),
                             "母集団一致": "OK" if expected == len(p) == unique else "要確認"})
    return pd.DataFrame(rows)


@st.cache_data(persist="disk", show_spinner=False)
def build_v360_current_results(commission_rate: float, slippage_rate: float):
    windows = build_v34_windows()
    period_bundles = {"前5年": {}, "現5年": {}}
    for period_name in ["前5年", "現5年"]:
        eval_start, eval_end = windows[period_name]
        for ticker_symbol in ["GOOG", "NVDA"]:
            prepared = prepare_data_fixed_window(ticker_symbol, eval_start, eval_end, V34_WARMUP_CALENDAR_DAYS)
            period_bundles[period_name][ticker_symbol] = build_v30_ticker_bundle(ticker_symbol, prepared, commission_rate, slippage_rate)

    # v3.4/v3.5保存結果
    audit = build_v34_audit(period_bundles, windows)
    net_summary = build_v34_net_summary(period_bundles)
    difference_20d = build_v34_20d_difference(net_summary)
    reconciliation = build_v34_reconciliation(audit, net_summary)
    exit_summary = build_v35_exit_structure(period_bundles)
    path_detail, path_summary = build_v35_path_summary(period_bundles, horizon=20)
    risk_summary = build_v35_risk_summary(period_bundles)
    period_difference = build_v35_period_difference(exit_summary, path_summary, risk_summary)
    v35_audit = build_v35_reconciliation(period_bundles, exit_summary, path_detail, risk_summary)

    env = _v36_signal_environment(period_bundles)
    env_summary = build_v36_environment_summary(env)
    outcome_env = build_v36_outcome_environment(env)
    env_difference = build_v36_period_difference(env_summary)
    v36_audit = build_v36_audit(period_bundles, env)
    return (windows, audit, net_summary, difference_20d, reconciliation,
            exit_summary, path_summary, risk_summary, period_difference, v35_audit,
            env_summary, outcome_env, env_difference, v36_audit)

# ============================================================
# v3.7.0 下落トレンド・下落速度診断
# 売買条件は変更せず、シグナル確定日までの価格履歴だけを記録する。
# ============================================================

def _v37_price_state(period_bundles: dict) -> pd.DataFrame:
    parts = []
    for period_name in ["前5年", "現5年"]:
        for ticker_symbol in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period_name, {}).get(ticker_symbol)
            if not bundle:
                continue
            data = bundle.get("data", pd.DataFrame()).copy()
            if data.empty:
                continue
            close = pd.to_numeric(data["Close"], errors="coerce")
            ret1 = close.pct_change()
            ma50 = close.rolling(50, min_periods=50).mean()
            ma200 = close.rolling(200, min_periods=200).mean()
            metrics = pd.DataFrame(index=pd.to_datetime(data.index))
            metrics["Return_5D_Pct"] = close.pct_change(5).values * 100.0
            metrics["Return_20D_Pct"] = close.pct_change(20).values * 100.0
            metrics["Close_vs_MA50_Pct"] = ((close / ma50 - 1.0) * 100.0).values
            metrics["Close_vs_MA200_Pct"] = ((close / ma200 - 1.0) * 100.0).values
            metrics["MA200_20D_Change_Pct"] = ((ma200 / ma200.shift(20) - 1.0) * 100.0).values
            # 直近5営業日の下落日数。シグナル日を含み、その日の終値までで確定する。
            metrics["Down_Days_Last5"] = ret1.lt(0).rolling(5, min_periods=5).sum().values

            for prefix, label in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                sig = bundle.get("signal_valid", {}).get(prefix, pd.DataFrame()).copy()
                if sig.empty:
                    continue
                sig["_Signal_Date_v37"] = pd.to_datetime(sig.index).values
                out = bundle.get("net_sets", {}).get(prefix, pd.DataFrame()).copy()
                if not out.empty:
                    out = out[pd.to_numeric(out["Horizon"], errors="coerce").eq(20)].copy()
                    out = out[["BB_Event_ID", "Outcome"]].drop_duplicates("BB_Event_ID")
                    sig = sig.merge(out, on="BB_Event_ID", how="left", validate="one_to_one")
                else:
                    sig["Outcome"] = np.nan
                for col in metrics.columns:
                    mp = pd.Series(metrics[col].values, index=metrics.index)
                    sig[col] = pd.to_datetime(sig["_Signal_Date_v37"]).map(mp)
                sig.drop(columns=["_Signal_Date_v37"], inplace=True)
                sig["期間"] = period_name
                sig["銘柄"] = ticker_symbol
                sig["シグナル"] = label
                parts.append(sig)
    return pd.concat(parts, ignore_index=False) if parts else pd.DataFrame()


def build_v37_state_summary(state: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if state is None or state.empty:
        return pd.DataFrame()
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            for signal in ["下落停止", "反発開始"]:
                p = state[(state["期間"] == period) & (state["銘柄"] == ticker) & (state["シグナル"] == signal)].copy()
                if p.empty:
                    continue
                def med(c): return pd.to_numeric(p[c], errors="coerce").median()
                ma200d = pd.to_numeric(p["Close_vs_MA200_Pct"], errors="coerce")
                slope = pd.to_numeric(p["MA200_20D_Change_Pct"], errors="coerce")
                rows.append({
                    "期間": period, "銘柄": ticker, "シグナル": signal, "対象": len(p),
                    "5日騰落率中央値_%": med("Return_5D_Pct"),
                    "20日騰落率中央値_%": med("Return_20D_Pct"),
                    "MA50乖離中央値_%": med("Close_vs_MA50_Pct"),
                    "MA200乖離中央値_%": med("Close_vs_MA200_Pct"),
                    "MA200下_%": ma200d.lt(0).mean() * 100.0 if ma200d.notna().any() else np.nan,
                    "MA200_20日変化中央値_%": med("MA200_20D_Change_Pct"),
                    "MA200下降中_%": slope.lt(0).mean() * 100.0 if slope.notna().any() else np.nan,
                    "直近5日下落日数中央値": med("Down_Days_Last5"),
                })
    return pd.DataFrame(rows)


def build_v37_outcome_state(state: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if state is None or state.empty:
        return pd.DataFrame()
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            for signal in ["下落停止", "反発開始"]:
                base = state[(state["期間"] == period) & (state["銘柄"] == ticker) & (state["シグナル"] == signal)].copy()
                for outcome in ["Target先着", "Stop先着", "期間内未到達"]:
                    p = base[base["Outcome"].fillna("").astype(str).eq(outcome)].copy()
                    if p.empty:
                        continue
                    def med(c): return pd.to_numeric(p[c], errors="coerce").median()
                    ma200d = pd.to_numeric(p["Close_vs_MA200_Pct"], errors="coerce")
                    slope = pd.to_numeric(p["MA200_20D_Change_Pct"], errors="coerce")
                    rows.append({
                        "期間": period, "銘柄": ticker, "シグナル": signal, "20日結果": outcome, "件数": len(p),
                        "5日騰落率中央値_%": med("Return_5D_Pct"),
                        "20日騰落率中央値_%": med("Return_20D_Pct"),
                        "MA50乖離中央値_%": med("Close_vs_MA50_Pct"),
                        "MA200乖離中央値_%": med("Close_vs_MA200_Pct"),
                        "MA200下_%": ma200d.lt(0).mean() * 100.0 if ma200d.notna().any() else np.nan,
                        "MA200_20日変化中央値_%": med("MA200_20D_Change_Pct"),
                        "MA200下降中_%": slope.lt(0).mean() * 100.0 if slope.notna().any() else np.nan,
                        "直近5日下落日数中央値": med("Down_Days_Last5"),
                    })
    return pd.DataFrame(rows)


def build_v37_period_difference(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if summary is None or summary.empty:
        return pd.DataFrame()
    metrics = ["5日騰落率中央値_%", "20日騰落率中央値_%", "MA50乖離中央値_%", "MA200乖離中央値_%", "MA200下_%", "MA200_20日変化中央値_%", "MA200下降中_%", "直近5日下落日数中央値"]
    for ticker in ["GOOG", "NVDA"]:
        for signal in ["下落停止", "反発開始"]:
            a = summary[(summary["期間"] == "前5年") & (summary["銘柄"] == ticker) & (summary["シグナル"] == signal)]
            b = summary[(summary["期間"] == "現5年") & (summary["銘柄"] == ticker) & (summary["シグナル"] == signal)]
            if len(a) != 1 or len(b) != 1:
                continue
            row = {"銘柄": ticker, "シグナル": signal}
            for m in metrics:
                av = pd.to_numeric(pd.Series([a.iloc[0][m]]), errors="coerce").iloc[0]
                bv = pd.to_numeric(pd.Series([b.iloc[0][m]]), errors="coerce").iloc[0]
                row[f"前5年_{m}"] = av; row[f"現5年_{m}"] = bv
                row[f"差_現-前_{m}"] = bv - av if pd.notna(av) and pd.notna(bv) else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def build_v37_audit(period_bundles: dict, state: pd.DataFrame) -> pd.DataFrame:
    rows = []
    required = ["Return_5D_Pct", "Return_20D_Pct", "Close_vs_MA50_Pct", "Close_vs_MA200_Pct", "MA200_20D_Change_Pct", "Down_Days_Last5"]
    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            bundle = period_bundles.get(period, {}).get(ticker)
            if not bundle: continue
            for prefix, signal in [("Stop", "下落停止"), ("Rebound", "反発開始")]:
                expected = len(bundle.get("signal_valid", {}).get(prefix, pd.DataFrame()))
                p = state[(state["期間"] == period) & (state["銘柄"] == ticker) & (state["シグナル"] == signal)].copy()
                unique = pd.to_numeric(p.get("BB_Event_ID"), errors="coerce").nunique() if not p.empty else 0
                counts = {c: int(pd.to_numeric(p.get(c), errors="coerce").notna().sum()) if not p.empty else 0 for c in required}
                rows.append({
                    "期間": period, "銘柄": ticker, "シグナル": signal, "R有効シグナル": expected,
                    "v3.7状態行数": len(p), "ユニークイベントID": int(unique),
                    "5日騰落率計算可能": counts["Return_5D_Pct"], "20日騰落率計算可能": counts["Return_20D_Pct"],
                    "MA50計算可能": counts["Close_vs_MA50_Pct"], "MA200計算可能": counts["Close_vs_MA200_Pct"],
                    "MA200傾き計算可能": counts["MA200_20D_Change_Pct"], "直近5日下落日数計算可能": counts["Down_Days_Last5"],
                    "母集団一致": "OK" if expected == len(p) == unique else "要確認",
                })
    return pd.DataFrame(rows)



# ============================================================
# v3.8.0 分布・複合条件の再現性診断
# 前5年の「特徴量分布だけ」から固定境界を作り、現5年へそのまま適用する。
# Target/Stop結果を使って境界を最適化しない。
# ============================================================

def _v38_feature_frame(env: pd.DataFrame, state: pd.DataFrame) -> pd.DataFrame:
    keys = ["期間", "銘柄", "シグナル", "BB_Event_ID"]
    ecols = keys + ["Outcome", "BandWidth", "HistVol_20D_Pct"]
    scols = keys + ["Return_20D_Pct", "Close_vs_MA50_Pct"]
    e = env[[c for c in ecols if c in env.columns]].copy()
    s = state[[c for c in scols if c in state.columns]].copy()
    # Outcomeはv3.6側を正とし、特徴量だけを1イベント1行で結合する。
    return e.merge(s, on=keys, how="inner", validate="one_to_one")


def _v38_prior_quartile_edges(x: pd.Series):
    x = pd.to_numeric(x, errors="coerce").dropna()
    if x.empty:
        return None
    q = x.quantile([0.25, 0.50, 0.75]).to_numpy(dtype=float)
    if len(set(q.tolist())) < 3:
        return None
    return [-np.inf, q[0], q[1], q[2], np.inf]


def build_v38_quartile_distribution(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        ("BandWidth", "BandWidth"),
        ("HistVol_20D_Pct", "20日Vol"),
        ("Return_20D_Pct", "20日騰落率"),
        ("Close_vs_MA50_Pct", "MA50乖離"),
    ]
    labels = ["Q1", "Q2", "Q3", "Q4"]
    for ticker in ["GOOG", "NVDA"]:
        for signal in ["下落停止", "反発開始"]:
            prior = features[(features["期間"]=="前5年") & (features["銘柄"]==ticker) & (features["シグナル"]==signal)]
            for col, name in specs:
                edges = _v38_prior_quartile_edges(prior[col])
                if edges is None: continue
                for period in ["前5年", "現5年"]:
                    p = features[(features["期間"]==period) & (features["銘柄"]==ticker) & (features["シグナル"]==signal)].copy()
                    vals = pd.to_numeric(p[col], errors="coerce")
                    p["_bin"] = pd.cut(vals, bins=edges, labels=labels, include_lowest=True)
                    for b in labels:
                        z = p[p["_bin"].astype(str)==b].copy()
                        resolved = z[z["Outcome"].isin(["Target先着","Stop先着"])].copy()
                        nt = int(resolved["Outcome"].eq("Target先着").sum())
                        ns = int(resolved["Outcome"].eq("Stop先着").sum())
                        nr = nt + ns
                        rows.append({
                            "期間":period,"銘柄":ticker,"シグナル":signal,"指標":name,"前5年固定帯":b,
                            "帯内件数":len(z),"Target先着":nt,"Stop先着":ns,"判定済件数":nr,
                            "Target率_%":nt/nr*100.0 if nr else np.nan,
                            "Stop率_%":ns/nr*100.0 if nr else np.nan,
                            "前5年Q1上限":edges[1],"前5年中央値":edges[2],"前5年Q3上限":edges[3],
                        })
    return pd.DataFrame(rows)


def build_v38_quartile_repro(qdist: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if qdist is None or qdist.empty: return pd.DataFrame()
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            for metric in ["BandWidth","20日Vol","20日騰落率","MA50乖離"]:
                for b in ["Q1","Q2","Q3","Q4"]:
                    a=qdist[(qdist["期間"]=="前5年")&(qdist["銘柄"]==ticker)&(qdist["シグナル"]==signal)&(qdist["指標"]==metric)&(qdist["前5年固定帯"]==b)]
                    c=qdist[(qdist["期間"]=="現5年")&(qdist["銘柄"]==ticker)&(qdist["シグナル"]==signal)&(qdist["指標"]==metric)&(qdist["前5年固定帯"]==b)]
                    if len(a)!=1 or len(c)!=1: continue
                    av=a.iloc[0]["Target率_%"]; cv=c.iloc[0]["Target率_%"]
                    rows.append({"銘柄":ticker,"シグナル":signal,"指標":metric,"前5年固定帯":b,
                                 "前5年_判定済件数":a.iloc[0]["判定済件数"],"現5年_判定済件数":c.iloc[0]["判定済件数"],
                                 "前5年_Target率_%":av,"現5年_Target率_%":cv,
                                 "Target率差_現-前_pt":cv-av if pd.notna(av) and pd.notna(cv) else np.nan})
    return pd.DataFrame(rows)


def build_v38_composite(features: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    pairs=[("HistVol_20D_Pct","20日Vol","Return_20D_Pct","20日騰落率"),
           ("BandWidth","BandWidth","Close_vs_MA50_Pct","MA50乖離")]
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            prior=features[(features["期間"]=="前5年")&(features["銘柄"]==ticker)&(features["シグナル"]==signal)]
            for c1,n1,c2,n2 in pairs:
                m1=pd.to_numeric(prior[c1],errors="coerce").median(); m2=pd.to_numeric(prior[c2],errors="coerce").median()
                if pd.isna(m1) or pd.isna(m2): continue
                for period in ["前5年","現5年"]:
                    p=features[(features["期間"]==period)&(features["銘柄"]==ticker)&(features["シグナル"]==signal)].copy()
                    v1=pd.to_numeric(p[c1],errors="coerce"); v2=pd.to_numeric(p[c2],errors="coerce")
                    p["_cell"]=np.where(v1.isna()|v2.isna(),np.nan,
                        np.where(v1<=m1,"低","高")+pd.Series(np.where(v2<=m2,"低","高"),index=p.index))
                    for cell in ["低低","低高","高低","高高"]:
                        z=p[p["_cell"]==cell]; r=z[z["Outcome"].isin(["Target先着","Stop先着"])]
                        nt=int(r["Outcome"].eq("Target先着").sum()); ns=int(r["Outcome"].eq("Stop先着").sum()); nr=nt+ns
                        rows.append({"期間":period,"銘柄":ticker,"シグナル":signal,"組合せ":f"{n1}×{n2}",
                                     "前5年中央値セル":cell,"帯内件数":len(z),"判定済件数":nr,"Target先着":nt,"Stop先着":ns,
                                     "Target率_%":nt/nr*100.0 if nr else np.nan,"Stop率_%":ns/nr*100.0 if nr else np.nan,
                                     f"{n1}_前5年中央値":m1,f"{n2}_前5年中央値":m2})
    return pd.DataFrame(rows)


def build_v38_audit(features: pd.DataFrame, qdist: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for period in ["前5年","現5年"]:
        for ticker in ["GOOG","NVDA"]:
            for signal in ["下落停止","反発開始"]:
                p=features[(features["期間"]==period)&(features["銘柄"]==ticker)&(features["シグナル"]==signal)]
                unique=pd.to_numeric(p.get("BB_Event_ID"),errors="coerce").nunique() if not p.empty else 0
                row={"期間":period,"銘柄":ticker,"シグナル":signal,"v3.8結合行数":len(p),"ユニークイベントID":int(unique)}
                for col,name in [("BandWidth","BandWidth"),("HistVol_20D_Pct","20日Vol"),("Return_20D_Pct","20日騰落率"),("Close_vs_MA50_Pct","MA50乖離")]:
                    row[f"{name}計算可能"]=int(pd.to_numeric(p.get(col),errors="coerce").notna().sum()) if not p.empty else 0
                # 各指標のQ1-Q4合計が、その指標の計算可能件数と一致するか。
                checks=[]
                for name in ["BandWidth","20日Vol","20日騰落率","MA50乖離"]:
                    z=qdist[(qdist["期間"]==period)&(qdist["銘柄"]==ticker)&(qdist["シグナル"]==signal)&(qdist["指標"]==name)]
                    checks.append(int(z["帯内件数"].sum())==row[f"{name}計算可能"] if not z.empty else False)
                row["分位帯合計一致"]="OK" if all(checks) else "要確認"
                row["母集団一致"]="OK" if len(p)==unique else "要確認"
                rows.append(row)
    return pd.DataFrame(rows)

@st.cache_data(persist="disk", show_spinner=False)
def build_v380_current_results(commission_rate: float, slippage_rate: float):
    windows = build_v34_windows()
    period_bundles = {"前5年": {}, "現5年": {}}
    for period_name in ["前5年", "現5年"]:
        eval_start, eval_end = windows[period_name]
        for ticker_symbol in ["GOOG", "NVDA"]:
            prepared = prepare_data_fixed_window(ticker_symbol, eval_start, eval_end, V34_WARMUP_CALENDAR_DAYS)
            period_bundles[period_name][ticker_symbol] = build_v30_ticker_bundle(ticker_symbol, prepared, commission_rate, slippage_rate)

    audit = build_v34_audit(period_bundles, windows)
    net_summary = build_v34_net_summary(period_bundles)
    difference_20d = build_v34_20d_difference(net_summary)
    reconciliation = build_v34_reconciliation(audit, net_summary)
    exit_summary = build_v35_exit_structure(period_bundles)
    path_detail, path_summary = build_v35_path_summary(period_bundles, horizon=20)
    risk_summary = build_v35_risk_summary(period_bundles)
    period_difference = build_v35_period_difference(exit_summary, path_summary, risk_summary)
    v35_audit = build_v35_reconciliation(period_bundles, exit_summary, path_detail, risk_summary)
    env = _v36_signal_environment(period_bundles)
    env_summary = build_v36_environment_summary(env)
    outcome_env = build_v36_outcome_environment(env)
    env_difference = build_v36_period_difference(env_summary)
    v36_audit = build_v36_audit(period_bundles, env)

    state = _v37_price_state(period_bundles)
    state_summary = build_v37_state_summary(state)
    outcome_state = build_v37_outcome_state(state)
    state_difference = build_v37_period_difference(state_summary)
    v37_audit = build_v37_audit(period_bundles, state)
    features = _v38_feature_frame(env, state)
    v38_qdist = build_v38_quartile_distribution(features)
    v38_repro = build_v38_quartile_repro(v38_qdist)
    v38_combo = build_v38_composite(features)
    v38_audit = build_v38_audit(features, v38_qdist)
    return (windows, audit, net_summary, difference_20d, reconciliation,
            exit_summary, path_summary, risk_summary, period_difference, v35_audit,
            env_summary, outcome_env, env_difference, v36_audit,
            state_summary, outcome_state, state_difference, v37_audit,
            v38_qdist, v38_repro, v38_combo, v38_audit)

# ============================================================
# v3.9.0 ウォークフォワード再現性検証
# 売買条件は固定したまま、時間を1年ずつ前へ進めて20日2R Net Rの再現性を確認する。
# 各テスト年の判定に未来年は使わない。過去累積は比較基準としてのみ表示する。
# ============================================================

def _v39_event_results(period_bundles: dict) -> pd.DataFrame:
    parts=[]
    for period in ["前5年","現5年"]:
        for ticker in ["GOOG","NVDA"]:
            b=period_bundles.get(period,{}).get(ticker)
            if not b: continue
            for prefix,label in [("Stop","下落停止"),("Rebound","反発開始")]:
                sig=b.get("signal_valid",{}).get(prefix,pd.DataFrame()).copy()
                out=b.get("net_sets",{}).get(prefix,pd.DataFrame()).copy()
                if sig.empty or out.empty: continue
                date_map=pd.Series(pd.to_datetime(sig.index).values,index=pd.to_numeric(sig["BB_Event_ID"],errors="coerce"))
                out=out[pd.to_numeric(out["Horizon"],errors="coerce").eq(20)].copy()
                out["Signal_Date"]=pd.to_numeric(out["BB_Event_ID"],errors="coerce").map(date_map)
                out["期間"]=period; out["銘柄"]=ticker; out["シグナル"]=label
                parts.append(out)
    return pd.concat(parts,ignore_index=True) if parts else pd.DataFrame()


def _v39_test_year(d):
    d=pd.Timestamp(d)
    # 固定研究窓の年度: 10/1～翌9/30
    y=d.year if d.month>=10 else d.year-1
    return f"{y}-{y+1}"


def build_v39_yearly_summary(events: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if events is None or events.empty:return pd.DataFrame()
    e=events.copy(); e["Signal_Date"]=pd.to_datetime(e["Signal_Date"],errors="coerce"); e=e[e["Signal_Date"].notna()].copy()
    e["テスト年"]=e["Signal_Date"].map(_v39_test_year)
    for ticker in ["GOOG","NVDA"]:
      for signal in ["下落停止","反発開始"]:
        p=e[(e["銘柄"]==ticker)&(e["シグナル"]==signal)].copy()
        for yr in sorted(p["テスト年"].dropna().unique()):
            z=p[p["テスト年"]==yr].copy(); valid=z[z["Net_R_Valid"].eq(True)].copy() if "Net_R_Valid" in z else pd.DataFrame()
            nr=pd.to_numeric(valid.get("Net_Realized_R"),errors="coerce").dropna()
            resolved=z[z["Outcome"].isin(["Target先着","Stop先着"])]
            nt=int(resolved["Outcome"].eq("Target先着").sum()); ns=int(resolved["Outcome"].eq("Stop先着").sum()); nres=nt+ns
            rows.append({"テスト年":yr,"銘柄":ticker,"シグナル":signal,"20日イベント":len(z),"Net_R計算可能":len(nr),
                         "Target先着":nt,"Stop先着":ns,"Target率_%":nt/nres*100 if nres else np.nan,
                         "Net_R合計":nr.sum() if len(nr) else np.nan,"Net_R平均":nr.mean() if len(nr) else np.nan,
                         "Net_R中央値":nr.median() if len(nr) else np.nan,"プラスR件数":int((nr>0).sum()),"マイナスR件数":int((nr<0).sum())})
    return pd.DataFrame(rows)


def build_v39_expanding_comparison(events: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if events is None or events.empty:return pd.DataFrame()
    e=events.copy(); e["Signal_Date"]=pd.to_datetime(e["Signal_Date"],errors="coerce"); e=e[e["Signal_Date"].notna()].copy(); e["テスト年"]=e["Signal_Date"].map(_v39_test_year)
    for ticker in ["GOOG","NVDA"]:
      for signal in ["下落停止","反発開始"]:
        p=e[(e["銘柄"]==ticker)&(e["シグナル"]==signal)].sort_values("Signal_Date")
        years=sorted(p["テスト年"].unique())
        for i,yr in enumerate(years):
            if i<2: continue  # 最低2年度を過去参照として確保
            test=p[p["テスト年"]==yr]; cutoff=test["Signal_Date"].min(); train=p[p["Signal_Date"]<cutoff]
            tr=train[train["Net_R_Valid"].eq(True)]; te=test[test["Net_R_Valid"].eq(True)]
            trr=pd.to_numeric(tr["Net_Realized_R"],errors="coerce").dropna(); ter=pd.to_numeric(te["Net_Realized_R"],errors="coerce").dropna()
            rows.append({"テスト年":yr,"銘柄":ticker,"シグナル":signal,"過去累積イベント":len(train),"過去累積Net_R件数":len(trr),
                         "過去累積Net_R平均":trr.mean() if len(trr) else np.nan,"過去累積Net_R中央値":trr.median() if len(trr) else np.nan,
                         "次1年イベント":len(test),"次1年Net_R件数":len(ter),"次1年Net_R平均":ter.mean() if len(ter) else np.nan,
                         "次1年Net_R中央値":ter.median() if len(ter) else np.nan,
                         "平均R方向一致":"OK" if len(trr) and len(ter) and np.sign(trr.mean())==np.sign(ter.mean()) else "不一致"})
    return pd.DataFrame(rows)


def build_v39_consistency(expanding: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if expanding is None or expanding.empty:return pd.DataFrame()
    for ticker in ["GOOG","NVDA"]:
      for signal in ["下落停止","反発開始"]:
        p=expanding[(expanding["銘柄"]==ticker)&(expanding["シグナル"]==signal)].copy()
        vals=pd.to_numeric(p["次1年Net_R平均"],errors="coerce").dropna()
        rows.append({"銘柄":ticker,"シグナル":signal,"検証年数":len(vals),"次1年平均Rプラス年":int((vals>0).sum()),"次1年平均Rマイナス年":int((vals<0).sum()),
                     "プラス年率_%":((vals>0).mean()*100 if len(vals) else np.nan),"次1年平均Rの中央値":vals.median() if len(vals) else np.nan,
                     "過去→次年_平均R方向一致年":int(p["平均R方向一致"].eq("OK").sum()),"方向一致率_%":p["平均R方向一致"].eq("OK").mean()*100 if len(p) else np.nan})
    return pd.DataFrame(rows)


def build_v39_audit(events: pd.DataFrame, yearly: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if events is None or events.empty:return pd.DataFrame()
    for ticker in ["GOOG","NVDA"]:
      for signal in ["下落停止","反発開始"]:
        p=events[(events["銘柄"]==ticker)&(events["シグナル"]==signal)].copy(); y=yearly[(yearly["銘柄"]==ticker)&(yearly["シグナル"]==signal)]
        unique=p[["期間","BB_Event_ID"]].drop_duplicates().shape[0]
        rows.append({"銘柄":ticker,"シグナル":signal,"結合イベント":len(p),"ユニークイベントID":int(unique),"Signal_Date計算可能":int(pd.to_datetime(p["Signal_Date"],errors="coerce").notna().sum()),
                     "年別イベント合計":int(pd.to_numeric(y["20日イベント"],errors="coerce").sum()) if not y.empty else 0,
                     "テスト年度数":int(y["テスト年"].nunique()) if not y.empty else 0,
                     "母集団一致":"OK" if len(p)==unique==int(pd.to_numeric(y["20日イベント"],errors="coerce").sum()) else "要確認"})
    return pd.DataFrame(rows)

@st.cache_data(persist="disk", show_spinner=False)
def build_v390_current_results(commission_rate: float, slippage_rate: float):
    base=build_v380_current_results(commission_rate,slippage_rate)
    windows=build_v34_windows(); period_bundles={"前5年":{},"現5年":{}}
    for period_name in ["前5年","現5年"]:
        eval_start,eval_end=windows[period_name]
        for ticker in ["GOOG","NVDA"]:
            prepared=prepare_data_fixed_window(ticker,eval_start,eval_end,V34_WARMUP_CALENDAR_DAYS)
            period_bundles[period_name][ticker]=build_v30_ticker_bundle(ticker,prepared,commission_rate,slippage_rate)
    events=_v39_event_results(period_bundles)
    yearly=build_v39_yearly_summary(events)
    expanding=build_v39_expanding_comparison(events)
    consistency=build_v39_consistency(expanding)
    audit=build_v39_audit(events,yearly)
    return base+(yearly,expanding,consistency,audit)


# ============================================================
# v4.0.0 利益の頑健性・少数大勝ち依存診断
# 売買条件は変更しない。
# v3.9と同じ20日・2R・Net Rを使い、利益が少数の大勝ちイベントへ
# どの程度集中しているかを診断する。
# ============================================================

def _v40_valid_r(events: pd.DataFrame) -> pd.DataFrame:
    if events is None or events.empty:
        return pd.DataFrame()
    x=events.copy()
    if "Net_R_Valid" in x.columns:
        x=x[x["Net_R_Valid"].eq(True)].copy()
    x["Net_R"]=pd.to_numeric(x.get("Net_Realized_R"),errors="coerce")
    x=x[x["Net_R"].notna()].copy()
    x["Signal_Date"]=pd.to_datetime(x.get("Signal_Date"),errors="coerce")
    x["テスト年"]=x["Signal_Date"].map(_v39_test_year)
    return x


def _v40_stats(z: pd.DataFrame) -> dict:
    r=pd.to_numeric(z.get("Net_R"),errors="coerce").dropna()
    pos=r[r>0]; neg=r[r<0]
    gross_profit=float(pos.sum()) if len(pos) else 0.0
    gross_loss=float(-neg.sum()) if len(neg) else 0.0
    payoff=(float(pos.mean())/abs(float(neg.mean()))) if len(pos) and len(neg) and float(neg.mean())!=0 else np.nan
    pf=(gross_profit/gross_loss) if gross_loss>0 else (np.inf if gross_profit>0 else np.nan)
    desc=r.sort_values(ascending=False)
    top1=float(desc.iloc[:1].sum()) if len(desc) else 0.0
    top3=float(desc.iloc[:min(3,len(desc))].sum()) if len(desc) else 0.0
    k10=max(1,int(np.ceil(len(desc)*0.10))) if len(desc) else 0
    top10=float(desc.iloc[:k10].sum()) if k10 else 0.0
    return {
        "Net_R件数":int(len(r)),"Net_R合計":float(r.sum()) if len(r) else np.nan,
        "Net_R平均":float(r.mean()) if len(r) else np.nan,"Net_R中央値":float(r.median()) if len(r) else np.nan,
        "プラスR件数":int((r>0).sum()),"マイナスR件数":int((r<0).sum()),"ゼロR件数":int((r==0).sum()),
        "勝ち平均R":float(pos.mean()) if len(pos) else np.nan,"負け平均R":float(neg.mean()) if len(neg) else np.nan,
        "Payoff比":payoff,"Profit_Factor":pf,
        "Gross_Profit_R":gross_profit,"Gross_Loss_R":gross_loss,
        "最大利益R":float(r.max()) if len(r) else np.nan,"最大損失R":float(r.min()) if len(r) else np.nan,
        "上位10%件数":k10,
        "最大1件_総利益寄与_%":top1/gross_profit*100.0 if gross_profit>0 else np.nan,
        "上位3件_総利益寄与_%":top3/gross_profit*100.0 if gross_profit>0 else np.nan,
        "上位10%_総利益寄与_%":top10/gross_profit*100.0 if gross_profit>0 else np.nan,
    }


def build_v40_profit_structure(events: pd.DataFrame) -> pd.DataFrame:
    x=_v40_valid_r(events); rows=[]
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            z=x[(x["銘柄"]==ticker)&(x["シグナル"]==signal)].copy()
            rows.append({"銘柄":ticker,"シグナル":signal,**_v40_stats(z)})
    return pd.DataFrame(rows)


def build_v40_removal_sensitivity(events: pd.DataFrame) -> pd.DataFrame:
    x=_v40_valid_r(events); rows=[]
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            z=x[(x["銘柄"]==ticker)&(x["シグナル"]==signal)].copy().sort_values("Net_R",ascending=False)
            n=len(z); k10=max(1,int(np.ceil(n*0.10))) if n else 0
            cases=[("基準・除外なし",0),("最大利益1件を除外",min(1,n)),("利益上位3件を除外",min(3,n)),("利益上位10%を除外",min(k10,n))]
            base_total=float(z["Net_R"].sum()) if n else np.nan
            for label,k in cases:
                keep=z.iloc[k:].copy() if k else z.copy()
                r=pd.to_numeric(keep["Net_R"],errors="coerce").dropna()
                rows.append({"銘柄":ticker,"シグナル":signal,"診断":label,"除外件数":k,"残存件数":len(r),
                             "Net_R合計":r.sum() if len(r) else np.nan,"Net_R平均":r.mean() if len(r) else np.nan,
                             "Net_R中央値":r.median() if len(r) else np.nan,"プラスR件数":int((r>0).sum()),"マイナスR件数":int((r<0).sum()),
                             "基準合計Rとの差":(r.sum()-base_total) if len(r) and pd.notna(base_total) else np.nan})
    return pd.DataFrame(rows)


def build_v40_period_robustness(events: pd.DataFrame) -> pd.DataFrame:
    x=_v40_valid_r(events); rows=[]
    for period in ["前5年","現5年"]:
        for ticker in ["GOOG","NVDA"]:
            for signal in ["下落停止","反発開始"]:
                z=x[(x["期間"]==period)&(x["銘柄"]==ticker)&(x["シグナル"]==signal)].copy().sort_values("Net_R",ascending=False)
                n=len(z); k10=max(1,int(np.ceil(n*0.10))) if n else 0
                base=_v40_stats(z)
                r1=z.iloc[min(1,n):]["Net_R"] if n else pd.Series(dtype=float)
                r3=z.iloc[min(3,n):]["Net_R"] if n else pd.Series(dtype=float)
                r10=z.iloc[min(k10,n):]["Net_R"] if n else pd.Series(dtype=float)
                rows.append({"期間":period,"銘柄":ticker,"シグナル":signal,"Net_R件数":n,
                             "基準合計R":base["Net_R合計"],"基準平均R":base["Net_R平均"],"基準中央値R":base["Net_R中央値"],
                             "最大1件除外_合計R":r1.sum() if len(r1) else np.nan,"最大1件除外_平均R":r1.mean() if len(r1) else np.nan,
                             "上位3件除外_合計R":r3.sum() if len(r3) else np.nan,"上位3件除外_平均R":r3.mean() if len(r3) else np.nan,
                             "上位10%除外件数":k10,"上位10%除外_合計R":r10.sum() if len(r10) else np.nan,"上位10%除外_平均R":r10.mean() if len(r10) else np.nan,
                             "最大1件_総利益寄与_%":base["最大1件_総利益寄与_%"],"上位3件_総利益寄与_%":base["上位3件_総利益寄与_%"],
                             "上位10%_総利益寄与_%":base["上位10%_総利益寄与_%"]})
    return pd.DataFrame(rows)


def build_v40_yearly_robustness(events: pd.DataFrame) -> pd.DataFrame:
    x=_v40_valid_r(events); rows=[]
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            p=x[(x["銘柄"]==ticker)&(x["シグナル"]==signal)].copy()
            for yr in sorted(p["テスト年"].dropna().unique()):
                z=p[p["テスト年"]==yr].sort_values("Net_R",ascending=False).copy(); n=len(z)
                r=z["Net_R"]; r1=z.iloc[min(1,n):]["Net_R"] if n else pd.Series(dtype=float)
                rows.append({"テスト年":yr,"銘柄":ticker,"シグナル":signal,"Net_R件数":n,
                             "基準合計R":r.sum() if n else np.nan,"基準平均R":r.mean() if n else np.nan,"基準中央値R":r.median() if n else np.nan,
                             "最大利益R":r.max() if n else np.nan,"最大1件除外_合計R":r1.sum() if len(r1) else np.nan,
                             "最大1件除外_平均R":r1.mean() if len(r1) else np.nan,
                             "最大1件除外後も合計プラス":"YES" if len(r1) and r1.sum()>0 else "NO"})
    return pd.DataFrame(rows)


def build_v40_audit(events: pd.DataFrame, sensitivity: pd.DataFrame, period_robust: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    x=_v40_valid_r(events)
    for ticker in ["GOOG","NVDA"]:
        for signal in ["下落停止","反発開始"]:
            raw=events[(events["銘柄"]==ticker)&(events["シグナル"]==signal)].copy()
            z=x[(x["銘柄"]==ticker)&(x["シグナル"]==signal)].copy()
            unique=raw[["期間","BB_Event_ID"]].drop_duplicates().shape[0]
            base=sensitivity[(sensitivity["銘柄"]==ticker)&(sensitivity["シグナル"]==signal)&(sensitivity["診断"]=="基準・除外なし")]
            pr=period_robust[(period_robust["銘柄"]==ticker)&(period_robust["シグナル"]==signal)]
            sign_count=int((z["Net_R"]>0).sum()+(z["Net_R"]<0).sum()+(z["Net_R"]==0).sum())
            checks=[len(raw)==unique, sign_count==len(z), len(base)==1 and int(base.iloc[0]["残存件数"])==len(z), int(pr["Net_R件数"].sum())==len(z)]
            rows.append({"銘柄":ticker,"シグナル":signal,"20日イベント":len(raw),"ユニークイベントID":int(unique),
                         "Net_R計算可能":len(z),"符号件数合計":sign_count,"感度分析基準件数":int(base.iloc[0]["残存件数"]) if len(base)==1 else np.nan,
                         "前5年+現5年件数":int(pr["Net_R件数"].sum()) if not pr.empty else 0,"母集団一致":"OK" if all(checks) else "要確認"})
    return pd.DataFrame(rows)


@st.cache_data(persist="disk", show_spinner=False)
def build_v400_current_results(commission_rate: float, slippage_rate: float):
    base=build_v390_current_results(commission_rate,slippage_rate)
    windows=build_v34_windows(); period_bundles={"前5年":{},"現5年":{}}
    for period_name in ["前5年","現5年"]:
        eval_start,eval_end=windows[period_name]
        for ticker in ["GOOG","NVDA"]:
            prepared=prepare_data_fixed_window(ticker,eval_start,eval_end,V34_WARMUP_CALENDAR_DAYS)
            period_bundles[period_name][ticker]=build_v30_ticker_bundle(ticker,prepared,commission_rate,slippage_rate)
    events=_v39_event_results(period_bundles)
    structure=build_v40_profit_structure(events)
    sensitivity=build_v40_removal_sensitivity(events)
    period_robust=build_v40_period_robustness(events)
    yearly_robust=build_v40_yearly_robustness(events)
    audit=build_v40_audit(events,sensitivity,period_robust)
    return base+(structure,sensitivity,period_robust,yearly_robust,audit)
