import streamlit as st
from research_core import APP_VERSION, V34_WARMUP_CALENDAR_DAYS, build_v370_current_results

st.set_page_config(page_title="GOOG・NVDA BB研究", page_icon="📊", layout="wide")
st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ v3.7.0 下落トレンド・下落速度診断")
st.info("v3.7.0では売買条件を変更しません。シグナル確定日までに分かる5日/20日騰落率、MA50/MA200乖離、MA200方向、直近5日の下落日数を記録し、前5年/現5年とTarget先着/Stop先着を比較します。")
st.write("【固定評価期間】前5年=2016-10-01～2021-09-30 ｜ 現5年=2021-10-01～2026-09-30")
st.write("【重要】v3.7の指標は診断用です。移動平均や下落速度を売買フィルターにはまだ使用しません。")

st.subheader("研究用コスト設定")
c1,c2=st.columns(2)
with c1: cp=st.number_input("売買手数料率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v370_commission")
with c2: sp=st.number_input("スリッページ率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v370_slippage")

with st.spinner("固定5年検証とv3.7診断を読み込んでいます。初回だけ時間がかかります..."):
    (windows,v34_audit,v34_net,v34_diff,v34_rec,v35_exit,v35_path,v35_risk,v35_diff,v35_audit,
     v36_env,v36_outcome,v36_diff,v36_audit,v37_state,v37_outcome,v37_diff,v37_audit)=build_v370_current_results(cp/100.0,sp/100.0)
st.success("v3.7.0 下落トレンド・下落速度診断の読み込み完了")
st.caption(f"前5年: {windows['前5年'][0].date()} ～ {windows['前5年'][1].date()} ｜ 現5年: {windows['現5年'][0].date()} ～ {windows['現5年'][1].date()} ｜ ウォームアップ: {V34_WARMUP_CALENDAR_DAYS}暦日")

def copy_text(title,frame,float_format=None):
    if frame is None or frame.empty:return f"【{title}】\n表示対象がありません。"
    kw={"index":False}
    if float_format:kw["float_format"]=float_format
    return f"【{title}】\n"+frame.to_csv(**kw).rstrip()

def show(num,title,df,expanded=False,ff="%.4f"):
    with st.expander(f"{num} {title}",expanded=expanded):
        st.dataframe(df.round(4) if df is not None else df,use_container_width=True,hide_index=True)
        st.code(copy_text(f"{num} {title}",df,float_format=ff),language=None)

st.subheader("📋 v3.7 結果・コピー欄")
st.caption("番号選択ボタンはありません。欄を開くだけです。")
show(146,"v3.7 下落トレンド・下落速度・母集団監査",v37_audit,True,None)
show(143,"v3.7 前5年 vs 現5年・シグナル時点下落状態",v37_state)
show(144,"v3.7 Target先着 / Stop先着・シグナル時点下落状態",v37_outcome)
show(145,"v3.7 前5年→現5年・下落状態差",v37_diff)

st.divider();st.subheader("📚 v3.6 相場環境・保存結果")
show(142,"v3.6 相場環境・母集団監査",v36_audit,False,None)
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

st.divider();st.subheader("v3.7.0の研究上の扱い")
st.write("【検証中】現5年の深い下方向の振れとStop先着増加に、シグナル前の下落速度・長期トレンド位置・長期トレンド方向が関係するかを記述的に確認します。")
st.write("【未採用】MA50/MA200、下落率、下落日数を売買フィルターにすること。閾値の最適化。Stop幅の変更。")
st.warning("Target/Stop別比較は原因候補を探す診断です。結果を知った後の分類なので、そのまま未来の売買条件にはできません。")
