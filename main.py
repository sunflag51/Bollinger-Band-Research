import streamlit as st
from stop_research_core import run_research, VERSION

st.set_page_config(page_title="GOOG・NVDA Stop設計研究",page_icon="📊",layout="wide")
st.title("📊 GOOG・NVDA Stop設計研究")
st.caption(f"v{VERSION}｜既存v5.3は変更せず、Stop設計だけを独立検証します。")

with st.sidebar:
    st.header("研究条件")
    commission=st.number_input("片道手数料 (%)",0.0,5.0,0.10,0.01)/100
    slippage=st.number_input("片道Slippage (%)",0.0,5.0,0.10,0.01)/100
    run=st.button("研究を実行",type="primary",use_container_width=True)

def section(n,title,df,open_=False):
    with st.expander(f"【{n} {title}】",expanded=open_):
        if df is None or df.empty:
            st.info("該当データなし")
        else:
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.text_area("コピー用CSV",df.to_csv(index=False),height=180,key=f"s{n}")

st.info("【重要】v5.3の凍結AI・2026-10-01以降の前向き検証には、この研究結果を混ぜません。")

if run:
    with st.spinner("GOOG / NVDAのStop方式を比較しています..."):
        r=run_research(commission,slippage)
    if r.get("error"):
        st.error(r["error"]); st.stop()
    st.success("計算完了")
    section(1,"研究仕様",r["spec"],True)
    section(2,"母集団監査",r["audit"],True)
    section(3,"1R幅・ATR換算比較",r["risk"],True)
    section(4,"Stop方式別20営業日Net R",r["summary20"],True)
    section(5,"Stop方式別5・10・20営業日比較",r["summary"],False)
    section(6,"前5年選択→現5年固定検証",r["validation"],True)
    section(7,"価格構造Stopとのペア比較",r["paired"],True)
    section(8,"年別20営業日Net R",r["yearly"],False)
    section(9,"20営業日イベント明細",r["detail"],False)
    st.warning("【未採用】画面上で最良に見えたATR倍率を、そのまま売買ルールにはしません。")
else:
    st.write("比較: 価格構造 / ATR×1 / ATR×1.5 / ATR×2")
    st.write("前5年: 2016-10-01～2021-09-30｜現5年: 2021-10-01～2026-09-30")
