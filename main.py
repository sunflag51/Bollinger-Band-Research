# ============================================================
# GOOG / NVDA BB研究
# Version 3.4.3 - 軽量メイン画面
#
# 目的:
# ・131等の結果番号を選ぶ操作を廃止し、選択による再実行をなくす
# ・現在の時間方向検証 130～133 だけを通常起動で計算/表示する
# ・研究計算本体は research_core.py に分離する
# ・固定5年検証結果は st.cache_data(persist="disk") で再利用する
# ============================================================

import streamlit as st
from research_core import (
    APP_VERSION,
    V34_WARMUP_CALENDAR_DAYS,
    build_v343_current_results,
)

st.set_page_config(
    page_title="GOOG・NVDA BB研究",
    page_icon="📊",
    layout="wide",
)

st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ 軽量メイン / 固定5年時間方向検証")

st.info(
    "v3.4.3では131などの『結果番号選択』を廃止しました。"
    "130～133は開閉式のコピー欄として最初から用意され、"
    "開閉してもPython側の研究計算を再実行しません。"
)

st.write(
    "【売買条件】v3.4.1までの条件を変更していません。"
    "前5年=2016-10-01～2021-09-30、現5年=2021-10-01～2026-09-30を固定します。"
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
        key="v343_commission_percent",
    )
with col2:
    slippage_percent = st.number_input(
        "スリッページ率（片道・%）",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01,
        format="%.2f",
        key="v343_slippage_percent",
    )

commission_rate = float(commission_percent) / 100.0
slippage_rate = float(slippage_percent) / 100.0

with st.spinner("固定5年検証を読み込んでいます。初回だけ計算に時間がかかります..."):
    (
        v34_windows,
        v34_audit,
        v34_net_summary,
        v34_20d_difference,
        v34_reconciliation,
    ) = build_v343_current_results(commission_rate, slippage_rate)

st.success("固定5年検証の読み込み完了")
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


# 重要: expanderの開閉はブラウザ側の表示操作で、結果番号selectboxを置かない。
st.subheader("📋 現在の検証結果・コピー欄")
st.caption("番号を選択する必要はありません。必要な番号を開いて右上のコピーアイコンを押してください。")

with st.expander("133 v3.4.1 時間方向検証・最終監査", expanded=True):
    st.dataframe(v34_reconciliation, use_container_width=True, hide_index=True)
    st.code(
        copy_text(
            "133 v3.4.1 時間方向検証・最終監査",
            v34_reconciliation,
        ),
        language=None,
    )

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
st.subheader("v3.4.3の構成")
st.write(
    "【軽量化】通常起動のmain.pyは現在の130～133だけを表示します。"
    "v1～v3.3の過去研究画面を毎回描画しないため、iPhoneからの操作負荷を下げます。"
)
st.write(
    "【計算分離】研究計算はresearch_core.pyにあります。"
    "main.pyは表示だけを担当します。"
)
st.write(
    "【データ再利用】固定5年の株価データと検証結果はStreamlitのディスクキャッシュを利用します。"
    "同じコスト条件なら通常の再実行では再計算を避けます。"
)
st.warning(
    "Streamlit Cloudのサーバー自体が再作成・再デプロイされた場合、ローカルディスクキャッシュが失われる可能性があります。"
    "その場合だけ固定5年データを再取得・再計算します。"
)
st.info(
    "過去の研究コードは削除していません。v3.4.2の旧画面はlegacy_main_v3_4_2.pyとして保存用に分離しています。"
)
