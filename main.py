# ============================================================
# GOOG / NVDA
# Bollinger Band Lower-Band Research Program
#
# Version : 3.0
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
# 重要
# v3.0は日足ベースの研究用ネットR損益＋時系列安定性＋銘柄横断診断まで。
# 板・出来高・部分約定・税金・為替コストなどはまだ含めない。
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

APP_VERSION = "3.0"

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
# タイトル
# ============================================================

st.title(
    "📊 GOOG・NVDA BB下限研究"
)

st.caption(
    f"Version {APP_VERSION} ｜ "
    "GOOG / NVDA 同一ルール・銘柄横断診断版"
)

st.info(
    "v3.0ではv2.9までの研究結果をすべて維持し、"
    "GOOGとNVDAを同じ期間・同じEntry / Stop / Target / ギャップ / コスト条件で同時計算します。"
    "5・10・20営業日、2RのNet Rを銘柄別に分離して比較し、"
    "GOOGで研究してきた条件が別銘柄でもどのように振る舞うかを診断します。条件は変更しません。"
)

# v2.5.1: 実際の結果は後段で計算されるため、ここに空の表示場所だけ作り、
# 計算完了後にこの位置へ番号選択・コピー欄を描画する。
quick_copy_top_placeholder = st.empty()


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
    "【次段階候補】同じルールを変更せず別銘柄NVDAへ適用し、銘柄をまたいだ再現性を確認します。"
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
# v3.0 番号選択・クイックコピー
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
}

with quick_copy_top_placeholder.container():
    st.divider()
    st.subheader("📋 番号で結果をすぐコピー")
    st.caption(
        "長いページを探す必要はありません。番号を選んでボタンを押すと、その結果だけをコピー欄に表示します。"
    )
    quick_copy_choice = st.selectbox(
        "結果番号を選択",
        options=list(quick_copy_results.keys()),
        index=list(quick_copy_results.keys()).index("107 v3.0 GOOG / NVDA 同一ルール・監査サマリー"),
        key="quick_copy_choice_v30",
    )

    if st.button(
        "選択した結果のコピー欄を表示",
        use_container_width=True,
        key="quick_copy_button_v30",
    ):
        st.session_state["quick_copy_selected_title_v30"] = quick_copy_choice
        st.session_state["quick_copy_selected_text_v30"] = quick_copy_results[quick_copy_choice]

    if st.session_state.get("quick_copy_selected_text_v30"):
        st.success(
            f"表示中：{st.session_state.get('quick_copy_selected_title_v30', '')}"
        )
        st.caption("下のコピー欄の右上にあるコピーアイコンを押すと全文をコピーできます。")
        st.code(
            st.session_state["quick_copy_selected_text_v30"],
            language=None,
        )



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
    "【未実装】R期待値・最大ドローダウン等を含む本格バックテスト"
)


# ============================================================
# 最終説明
# ============================================================

st.divider()

st.warning(
    "重要：Target先着率や平均Rだけで正式な売買ルールは決めません。"
    "同日順序不明・期間内未到達・将来データ不足を分離し、"
    "v3.0では研究用の手数料・スリッページと固定時系列分割を維持し、GOOG / NVDAを同一ルールで銘柄横断診断します。"
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
