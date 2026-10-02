import streamlit as st
from research_core import APP_VERSION, V34_WARMUP_CALENDAR_DAYS, build_v380_current_results

st.set_page_config(page_title="GOOG・NVDA BB研究", page_icon="📊", layout="wide")
st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ v3.8.0 分布・複合条件の再現性診断")
st.info("v3.8.0では売買条件を変更しません。前5年の特徴量分布だけで固定した分位帯・中央値セルを現5年へそのまま適用し、Target/Stop構造が再現するかを確認します。")
st.write("【固定評価期間】前5年=2016-10-01～2021-09-30 ｜ 現5年=2021-10-01～2026-09-30")
st.write("【重要】Target/Stop結果を使って境界値を最適化しません。v3.8の区分は診断用で、まだ売買フィルターには使用しません。")

st.subheader("研究用コスト設定")
c1,c2=st.columns(2)
with c1: cp=st.number_input("売買手数料率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v380_commission")
with c2: sp=st.number_input("スリッページ率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v380_slippage")

with st.spinner("固定5年検証とv3.8診断を読み込んでいます。初回だけ時間がかかります..."):
    (windows,v34_audit,v34_net,v34_diff,v34_rec,v35_exit,v35_path,v35_risk,v35_diff,v35_audit,
     v36_env,v36_outcome,v36_diff,v36_audit,v37_state,v37_outcome,v37_diff,v37_audit,
     v38_qdist,v38_repro,v38_combo,v38_audit)=build_v380_current_results(cp/100.0,sp/100.0)
st.success("v3.8.0 分布・複合条件の再現性診断の読み込み完了")
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

st.subheader("📋 v3.8 結果・コピー欄")
st.caption("番号選択ボタンはありません。欄を開くだけです。最初は151番の監査を確認します。")
show(151,"v3.8 分布・複合条件・母集団監査",v38_audit,True,None)
show(147,"v3.8 前5年固定4分位・Target / Stop分布",v38_qdist)
show(148,"v3.8 前5年→現5年・4分位再現性",v38_repro)
show(149,"v3.8 前5年固定中央値・2指標組合せ",v38_combo)

st.divider();st.subheader("📚 v3.7 下落状態・保存結果")
show(146,"v3.7 下落トレンド・下落速度・母集団監査",v37_audit,False,None)
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

st.divider();st.subheader("v3.8.0の研究上の扱い")
st.write("【検証中】BandWidth・20日Vol・20日騰落率・MA50乖離について、前5年の分布で固定したQ1～Q4を現5年へ適用し、結果構造の再現性を確認します。")
st.write("【検証中】20日Vol×20日騰落率、BandWidth×MA50乖離を、前5年中央値で固定した4セルに分けて粗い複合関係を確認します。")
st.write("【未採用】分位帯・複合セルを売買条件にすること。Target/Stopを見ながら閾値を最適化すること。AI導入。")
st.warning("各セルの件数は小さくなります。高いTarget率が1つ見つかっても、それだけでは採用しません。前5年→現5年、GOOG→NVDAでの再現性を優先します。")
