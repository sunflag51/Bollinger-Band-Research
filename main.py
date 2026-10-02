import streamlit as st
from research_core import APP_VERSION, V34_WARMUP_CALENDAR_DAYS, build_v420_current_results

st.set_page_config(page_title="GOOG・NVDA BB研究", page_icon="📊", layout="wide")
st.title("📊 GOOG・NVDA BB下限研究")
st.caption(f"Version {APP_VERSION} ｜ v4.2.0 時間劣化の直接Bootstrap検証")
st.info("v4.2.0では売買条件を変更しません。v4.1までと同じ20日・2R・Net Rを使い、現5年平均R－前5年平均Rの差を直接Bootstrapし、3年・5年ローリング窓で時間劣化の形を診断します。")
st.write("【固定全期間】2016-10-01～2026-09-30 ｜ 前5年/現5年の固定窓も維持")
st.write("【重要】差Bootstrapは「現5年平均R－前5年平均R」を再標本化する診断です。マイナスは現5年の方が弱いことを示しますが、将来利益を保証・予測するものではありません。")

st.subheader("研究用コスト設定")
c1,c2=st.columns(2)
with c1: cp=st.number_input("売買手数料率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v420_commission")
with c2: sp=st.number_input("スリッページ率（片道・%）",0.0,5.0,0.10,0.01,format="%.2f",key="v420_slippage")

with st.spinner("固定10年結果とv4.2時間劣化診断を読み込んでいます。初回だけ時間がかかります..."):
    results=build_v420_current_results(cp/100.0,sp/100.0)
    (windows,v34_audit,v34_net,v34_diff,v34_rec,v35_exit,v35_path,v35_risk,v35_diff,v35_audit,
     v36_env,v36_outcome,v36_diff,v36_audit,v37_state,v37_outcome,v37_diff,v37_audit,
     v38_qdist,v38_repro,v38_combo,v38_audit,v39_yearly,v39_expanding,v39_consistency,v39_audit,
     v40_structure,v40_sensitivity,v40_period,v40_yearly,v40_audit,
     v41_event_boot,v41_period_boot,v41_year_boot,v41_loo,v41_loo_summary,v41_audit,
     v42_event_diff,v42_year_diff,v42_rolling3,v42_rolling5,v42_audit)=results
st.success("v4.2.0 時間劣化の直接Bootstrap検証の読み込み完了")
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

st.subheader("📋 v4.2 結果・コピー欄")
st.caption("番号選択ボタンはありません。最初は171番の監査を確認します。")
show(171,"v4.2 時間劣化・母集団監査",v42_audit,True,None)
show(167,"v4.2 前5年→現5年・平均R差イベントBootstrap",v42_event_diff)
show(168,"v4.2 前5年→現5年・平均R差年Block Bootstrap",v42_year_diff)
show(169,"v4.2 3年ローリング・時間推移",v42_rolling3)
show(170,"v4.2 5年ローリング・時間推移",v42_rolling5)

st.divider();st.subheader("📚 v4.1 統計的不確実性・保存結果")
st.caption("v4.1の再標本化結果をそのまま保存表示します。")
show(165,"v4.1 再標本化・母集団監査",v41_audit,True,None)
show(161,"v4.1 固定10年・イベントBootstrap",v41_event_boot)
show(162,"v4.1 前5年 vs 現5年・イベントBootstrap",v41_period_boot)
show(163,"v4.1 固定10年・年Block Bootstrap",v41_year_boot)
show(164,"v4.1 1年除外・Leave-One-Year-Out",v41_loo)
show(166,"v4.1 1年除外・頑健性サマリー",v41_loo_summary)

st.divider();st.subheader("📚 v4.0 利益頑健性・保存結果")
show(160,"v4.0 利益頑健性・母集団監査",v40_audit,False,None)
show(156,"v4.0 固定10年・利益構造と集中度",v40_structure)
show(157,"v4.0 大勝ちイベント除外・感度分析",v40_sensitivity)
show(158,"v4.0 前5年 vs 現5年・大勝ち依存比較",v40_period)
show(159,"v4.0 1年ごと・最大利益1件除外診断",v40_yearly)

st.divider();st.subheader("📚 v3.9 ウォークフォワード・保存結果")
show(155,"v3.9 ウォークフォワード・母集団監査",v39_audit,False,None)
show(152,"v3.9 1年ごと・固定ルール20日2R結果",v39_yearly)
show(153,"v3.9 過去累積→次1年・再現性比較",v39_expanding)
show(154,"v3.9 次1年・方向安定性サマリー",v39_consistency)

st.divider();st.subheader("📚 v3.8 分布・複合条件・保存結果")
show(151,"v3.8 分布・複合条件・母集団監査",v38_audit,False,None)
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

st.divider();st.subheader("v4.2.0の研究上の扱い")
st.write("【検証中】167番はイベント単位、168番は年単位のまとまりを残して『現5年平均R－前5年平均R』を直接Bootstrapします。")
st.write("【重要】差がマイナスなら現5年の平均Rが前5年より低いことを意味します。『現5年が弱い割合』は将来の下落確率ではなく、観測済み標本の再標本化結果です。")
st.write("【重要】169番の3年ローリングは変化時期を見やすくしますが窓が短く、イベント数も少なくなるため変動が大きくなります。170番の5年ローリングはより平滑ですが、隣接窓が多くの同じイベントを共有します。")
st.write("【重要】ローリング窓は独立したOOS検証ではありません。時間劣化が徐々に進んだか、特定時期に集中したかを記述する診断です。")
st.write("【未採用】新しいEntry条件、時間フィルター、AI導入、GOOG/NVDA専用の救済条件。")
st.warning("年Block差Bootstrapは各5年程度しか年ブロックがなく、NVDA下落停止の現5年はイベントが存在する年度がさらに少ないため、割合を過度に精密な確率として扱いません。")
