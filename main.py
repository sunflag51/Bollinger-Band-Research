import streamlit as st
from research_core import APP_VERSION, V34_WARMUP_CALENDAR_DAYS, build_v360_current_results

st.set_page_config(page_title="GOOG・NVDA BB研究", page_icon="📊", layout="wide")
st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ v3.6.1 相場環境・レジーム診断")
st.info("v3.6.1では売買条件を変更しません。シグナル確定日に既に分かっているBandWidth・過去125日のBandWidth位置・BandWidth方向・過去20日ボラティリティを記録し、前5年/現5年とTarget先着/Stop先着の環境差を診断します。")
st.write("【固定評価期間】前5年=2016-10-01～2021-09-30 ｜ 現5年=2021-10-01～2026-09-30")
st.write("【重要】v3.6の環境指標は診断用です。売買フィルターにはまだ使用しません。")

st.subheader("研究用コスト設定")
c1,c2=st.columns(2)
with c1:
    cp=st.number_input("売買手数料率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v360_commission")
with c2:
    sp=st.number_input("スリッページ率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v360_slippage")

with st.spinner("固定5年検証とv3.6環境診断を読み込んでいます。初回だけ時間がかかります..."):
    (windows,v34_audit,v34_net,v34_diff,v34_rec,v35_exit,v35_path,v35_risk,v35_diff,v35_audit,
     v36_env,v36_outcome,v36_diff,v36_audit)=build_v360_current_results(cp/100.0,sp/100.0)
st.success("v3.6.1 相場環境・レジーム診断の読み込み完了")
st.caption(f"前5年: {windows['前5年'][0].date()} ～ {windows['前5年'][1].date()} ｜ 現5年: {windows['現5年'][0].date()} ～ {windows['現5年'][1].date()} ｜ ウォームアップ: {V34_WARMUP_CALENDAR_DAYS}暦日")

def copy_text(title,frame,float_format=None,date_format=None):
    if frame is None or frame.empty:return f"【{title}】\n表示対象がありません。"
    kw={"index":False}
    if float_format:kw["float_format"]=float_format
    if date_format:kw["date_format"]=date_format
    return f"【{title}】\n"+frame.to_csv(**kw).rstrip()

def show(num,title,df,expanded=False,ff="%.4f"):
    with st.expander(f"{num} {title}",expanded=expanded):
        st.dataframe(df.round(4) if df is not None else df,use_container_width=True,hide_index=True)
        st.code(copy_text(f"{num} {title}",df,float_format=ff),language=None)

st.subheader("📋 v3.6 結果・コピー欄")
st.caption("番号選択ボタンはありません。欄を開くだけです。")
show(142,"v3.6 相場環境・母集団監査",v36_audit,True,None)
show(139,"v3.6 前5年 vs 現5年・シグナル時点環境比較",v36_env)
show(140,"v3.6 Target先着 / Stop先着・シグナル時点環境比較",v36_outcome)
show(141,"v3.6 前5年→現5年・環境差",v36_diff)

st.divider();st.subheader("📚 v3.5 原因分解・保存結果")
show(138,"v3.5 原因分解・母集団監査",v35_audit,False,None)
show(134,"v3.5 20日2R・決済構造比較",v35_exit)
show(135,"v3.5 20営業日・MFE / MAE価格経路比較",v35_path)
show(136,"v3.5 1R率分布・前5年 vs 現5年",v35_risk)
show(137,"v3.5 原因分解・前5年→現5年差",v35_diff)

st.divider();st.subheader("📚 v3.4.1 固定5年検証・保存結果")
show(133,"v3.4.1 時間方向検証・最終監査",v34_rec,False,None)
show(130,"v3.4.1 固定5年窓・監査サマリー",v34_audit,False,None)
show(131,"v3.4.1 前5年 vs 現5年・2Rコスト後Net R比較",v34_net)
show(132,"v3.4.1 20日保有・2R・前5年→現5年差",v34_diff)

st.divider();st.subheader("v3.6.1の研究上の扱い")
st.write("【検証中】現5年で深い下方向の振れが増えた背景に、BandWidthの位置・収縮/拡大・直前20日ボラティリティの環境差があるかを記述的に確認します。")
st.write("【未採用】Squeeze/BandWidth/ボラティリティを売買フィルターにすること。結果を見て閾値を最適化すること。Stop幅を変更すること。")
st.warning("この画面のTarget/Stop別比較は原因候補を探す診断です。結果を知った後の分類なので、そのまま未来の売買条件として使うことはできません。")
