# ============================================================
# GOOG / NVDA BB研究
# Version 3.5.0 - 軽量メイン画面
#
# 目的:
# ・v3.4.1の固定ルール / 固定5年窓を変更しない
# ・前5年→現5年の成績悪化を、決済構造・MFE/MAE・1R率で原因分解する
# ・結果番号のselectbox/buttonを使わず、expanderだけで結果を開閉する
# ・研究計算は research_core.py、画面は main.py に分離する
# ・同じ条件の結果は st.cache_data(persist="disk") で再利用する
# ============================================================

import streamlit as st
from research_core import (
    APP_VERSION,
    V34_WARMUP_CALENDAR_DAYS,
    build_v350_current_results,
)

st.set_page_config(
    page_title="GOOG・NVDA BB研究",
    page_icon="📊",
    layout="wide",
)

st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ v3.5 原因分解 / 軽量メイン")

st.info(
    "v3.5では売買条件を変更していません。"
    "v3.4.1で確認した『前5年→現5年の成績悪化』について、"
    "20日2Rの決済構造、MFE/MAE、1R率の違いを分解します。"
)

st.write(
    "【固定評価期間】前5年=2016-10-01～2021-09-30 ｜ "
    "現5年=2021-10-01～2026-09-30"
)
st.write(
    "【未変更】BBイベント、下落停止、反発開始、翌営業日Open Entry、"
    "現在の1R Stop、2R Target、ギャップ約定、手数料・スリッページの計算条件。"
)

st.subheader("研究用コスト設定")
col1, col2 = st.columns(2)
with col1:
    commission_percent = st.number_input(
        "売買手数料率（片道・%）",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f",
        key="v350_commission_percent",
    )
with col2:
    slippage_percent = st.number_input(
        "スリッページ率（片道・%）",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f",
        key="v350_slippage_percent",
    )

commission_rate = float(commission_percent) / 100.0
slippage_rate = float(slippage_percent) / 100.0

with st.spinner("固定5年検証とv3.5原因分解を読み込んでいます。初回だけ計算に時間がかかります..."):
    (
        v34_windows,
        v34_audit,
        v34_net_summary,
        v34_20d_difference,
        v34_reconciliation,
        v35_exit_summary,
        v35_path_summary,
        v35_risk_summary,
        v35_period_difference,
        v35_audit,
    ) = build_v350_current_results(commission_rate, slippage_rate)

st.success("v3.5 原因分解の読み込み完了")
st.caption(
    "前5年: "
    f"{v34_windows['前5年'][0].date()} ～ {v34_windows['前5年'][1].date()} ｜ "
    "現5年: "
    f"{v34_windows['現5年'][0].date()} ～ {v34_windows['現5年'][1].date()} ｜ "
    f"ウォームアップ: {V34_WARMUP_CALENDAR_DAYS}暦日"
)


def copy_text(title, frame, float_format=None, date_format=None):
    if frame is None or frame.empty:
        return f"【{title}】\n表示対象がありません。"
    kwargs = {"index": False}
    if float_format is not None:
        kwargs["float_format"] = float_format
    if date_format is not None:
        kwargs["date_format"] = date_format
    return f"【{title}】\n" + frame.to_csv(**kwargs).rstrip()


st.subheader("📋 v3.5 結果・コピー欄")
st.caption(
    "結果番号の選択ボタンはありません。必要な番号の欄を開くだけです。"
    "開閉では研究計算をやり直しません。"
)

# 最初は監査を確認する。
with st.expander("138 v3.5 原因分解・母集団監査", expanded=True):
    st.dataframe(v35_audit, use_container_width=True, hide_index=True)
    st.code(
        copy_text("138 v3.5 原因分解・母集団監査", v35_audit),
        language=None,
    )

with st.expander("134 v3.5 20日2R・決済構造比較", expanded=False):
    st.dataframe(v35_exit_summary.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "134 v3.5 20日2R・決済構造比較",
            v35_exit_summary,
            float_format="%.4f",
        ),
        language=None,
    )

with st.expander("135 v3.5 20営業日・MFE / MAE価格経路比較", expanded=False):
    st.dataframe(v35_path_summary.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "135 v3.5 20営業日・MFE / MAE価格経路比較",
            v35_path_summary,
            float_format="%.4f",
        ),
        language=None,
    )

with st.expander("136 v3.5 1R率分布・前5年 vs 現5年", expanded=False):
    st.dataframe(v35_risk_summary.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "136 v3.5 1R率分布・前5年 vs 現5年",
            v35_risk_summary,
            float_format="%.4f",
        ),
        language=None,
    )

with st.expander("137 v3.5 原因分解・前5年→現5年差", expanded=False):
    st.dataframe(v35_period_difference.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "137 v3.5 原因分解・前5年→現5年差",
            v35_period_difference,
            float_format="%.4f",
        ),
        language=None,
    )

st.divider()
st.subheader("📚 v3.4.1 固定5年検証・保存結果")
st.caption("130～133も同じ画面に残しています。番号選択は不要です。")

with st.expander("133 v3.4.1 時間方向検証・最終監査", expanded=False):
    st.dataframe(v34_reconciliation, use_container_width=True, hide_index=True)
    st.code(copy_text("133 v3.4.1 時間方向検証・最終監査", v34_reconciliation), language=None)

with st.expander("130 v3.4.1 固定5年窓・監査サマリー", expanded=False):
    st.dataframe(v34_audit, use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "130 v3.4.1 固定5年窓・監査サマリー",
            v34_audit,
            date_format="%Y-%m-%d",
        ),
        language=None,
    )

with st.expander("131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較", expanded=False):
    st.dataframe(v34_net_summary.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "131 v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較",
            v34_net_summary,
            float_format="%.4f",
        ),
        language=None,
    )

with st.expander("132 v3.4.1 20日保有・2R・前5年→現5年差", expanded=False):
    st.dataframe(v34_20d_difference.round(4), use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "132 v3.4.1 20日保有・2R・前5年→現5年差",
            v34_20d_difference,
            float_format="%.4f",
        ),
        language=None,
    )

st.divider()
st.subheader("v3.5の研究上の扱い")
st.write(
    "【検証中】前5年→現5年の悪化が、Target減少・Stop増加、MFE低下、MAE増加、"
    "または1R幅の変化のどこから来ているかを分解します。"
)
st.write(
    "【未採用】この結果を見ただけでStop幅を変更したり、1R率フィルター、"
    "GOOG/NVDA専用条件、BandWidth条件を追加したりしません。"
)
st.write(
    "【軽量化継続】main.pyは表示だけを担当し、研究計算はresearch_core.pyへ分離しています。"
    "同じコスト条件の結果はディスクキャッシュを再利用します。"
)
st.warning(
    "Streamlit Cloudのサーバー再作成・再デプロイ時にはローカルディスクキャッシュが失われる場合があります。"
    "その場合のみ固定期間データを再取得・再計算します。"
)
