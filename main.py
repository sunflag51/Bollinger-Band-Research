import math
import streamlit as st
from stop_research_core import run_research, VERSION

st.set_page_config(page_title="GOOG・NVDA Stop設計研究", page_icon="📊", layout="wide")
st.title("📊 GOOG・NVDA Stop設計研究")
st.caption(
    f"v{VERSION}｜4方式の共通イベント母集団でStop設計を比較します。"
    "既存v5.3は変更しません。"
)

with st.sidebar:
    st.header("研究条件")
    commission = st.number_input("片道手数料 (%)", 0.0, 5.0, 0.10, 0.01) / 100
    slippage = st.number_input("片道Slippage (%)", 0.0, 5.0, 0.10, 0.01) / 100
    run = st.button("研究を実行", type="primary", use_container_width=True)


def section(n, title, df, open_=False):
    with st.expander(f"【{n} {title}】", expanded=open_):
        if df is None or df.empty:
            st.info("該当データなし")
            return
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("右上のコピーボタンで、そのままChatGPTへ貼り付けできます。")
        st.code(f"【{n} {title}】\n" + df.to_csv(index=False), language=None)


def split_copy_section(n, title, df, rows_per_part=40, open_=False):
    """長い明細を複数のコピーボタンに分割して表示する。"""
    with st.expander(f"【{n} {title}】", expanded=open_):
        if df is None or df.empty:
            st.info("該当データなし")
            return

        total_rows = len(df)
        total_parts = math.ceil(total_rows / rows_per_part)

        st.info(
            f"明細 {total_rows} 行を、1回 {rows_per_part} 行以下・全 {total_parts} 分割で表示します。"
            "下の各ブロック右上のコピーボタンを順番に使ってください。"
        )

        for part_index in range(total_parts):
            start = part_index * rows_per_part
            end = min(start + rows_per_part, total_rows)
            part = df.iloc[start:end].copy()
            part_no = part_index + 1
            label = f"【{n}-{part_no}/{total_parts} {title}｜{start + 1}～{end}行】"

            st.markdown(f"**{label}**")
            st.dataframe(part, use_container_width=True, hide_index=True)
            st.caption(
                f"このブロックは {start + 1}～{end} 行です。"
                "右上のコピーボタンで、この部分だけコピーできます。"
            )
            st.code(label + "\n" + part.to_csv(index=False), language=None)


st.info(
    "【重要】成績比較は、価格構造 / ATR×1 / ATR×1.5 / ATR×2 の4方式すべてが"
    "設計可能な同一イベントだけを使用します。除外イベントは別に監査します。"
)

if run:
    with st.spinner("GOOG / NVDAの共通母集団を作成し、Stop方式を比較しています..."):
        r = run_research(commission, slippage)

    if r.get("error"):
        st.error(r["error"])
        st.stop()

    st.success("計算完了")

    section(1, "研究仕様", r["spec"], True)
    section(2, "母集団監査", r["audit"], True)
    section(3, "共通母集団からの除外イベント監査", r["excluded"], True)
    section(4, "1R幅・ATR換算比較", r["risk"], True)
    section(5, "Stop方式別20営業日Net R", r["summary20"], True)
    section(6, "Stop方式別5・10・20営業日比較", r["summary"], False)
    section(7, "前5年選択→現5年固定検証", r["validation"], True)
    section(8, "価格構造Stopとのペア比較", r["paired"], True)
    section(9, "年別20営業日Net R", r["yearly"], False)
    split_copy_section(10, "20営業日イベント明細", r["detail"], rows_per_part=40, open_=False)

    st.warning(
        "【未採用】画面上で最良に見えたATR倍率を、そのまま売買ルールにはしません。"
        "7番は前5年だけで選び、現5年で固定確認する診断です。"
    )
else:
    st.write("比較: 価格構造 / ATR×1 / ATR×1.5 / ATR×2")
    st.write("前5年: 2016-10-01～2021-09-30｜現5年: 2021-10-01～2026-09-30")
