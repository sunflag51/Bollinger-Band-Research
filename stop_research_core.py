import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

VERSION="1.0.0"
PRIOR=(pd.Timestamp("2016-10-01"),pd.Timestamp("2021-09-30"))
CURRENT=(pd.Timestamp("2021-10-01"),pd.Timestamp("2026-09-30"))
METHODS=["価格構造","ATR×1","ATR×1.5","ATR×2"]
MULT={"ATR×1":1.0,"ATR×1.5":1.5,"ATR×2":2.0}
HORIZONS=[5,10,20]

@st.cache_data(ttl=3600,show_spinner=False)
def get_data(ticker,start,end):
    try:
        d=yf.download(ticker,start=start.strftime("%Y-%m-%d"),
            end=(end+pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1d",auto_adjust=False,progress=False,multi_level_index=False)
    except Exception:
        return pd.DataFrame()
    if d is None or d.empty:return pd.DataFrame()
    if isinstance(d.columns,pd.MultiIndex):d.columns=d.columns.get_level_values(0)
    if getattr(d.index,"tz",None) is not None:d.index=d.index.tz_localize(None)
    d.index=pd.to_datetime(d.index).normalize()
    for c in ["Open","High","Low","Close"]:
        if c not in d:return pd.DataFrame()
        d[c]=pd.to_numeric(d[c],errors="coerce")
    return d.dropna(subset=["Open","High","Low","Close"]).sort_index()

def indicators(d):
    x=d.copy()
    m=x.Close.rolling(20).mean(); s=x.Close.rolling(20).std(ddof=0)
    x["BB_Lower"]=m-2*s
    pc=x.Close.shift(1)
    tr=pd.concat([x.High-x.Low,(x.High-pc).abs(),(x.Low-pc).abs()],axis=1).max(axis=1)
    x["ATR14"]=tr.ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    x["PrevLow"]=x.Low.shift(1);x["PrevClose"]=x.Close.shift(1);x["PrevHigh"]=x.High.shift(1)
    x["Decline"]=(x.Low>x.PrevLow)&(x.Close>x.PrevClose)
    x["Rebound"]=x.Close>x.PrevHigh
    x["Touch"]=x.BB_Lower.notna()&(x.Low<=x.BB_Lower)
    return x

def events(x,start,end):
    rows=[];p=0;eid=0
    while p<len(x):
        dt=x.index[p]
        if dt<start:p+=1;continue
        if dt>end:break
        if bool(x.iloc[p].Touch):
            if p+3>=len(x) or x.index[p+3]>end:break
            eid+=1;w=x.iloc[p:p+4]
            a=w[w.Decline.fillna(False)];b=w[w.Rebound.fillna(False)]
            rows.append({"Event":eid,"Day0":dt,"StartPos":p,
                "下落停止":a.index[0] if len(a) else pd.NaT,
                "反発開始":b.index[0] if len(b) else pd.NaT})
            p+=4
        else:p+=1
    return pd.DataFrame(rows)

def designs(ticker,period,x,ev):
    rows=[]
    for _,e in ev.iterrows():
        for sig in ["下落停止","反発開始"]:
            sd=e[sig]
            if pd.isna(sd):continue
            sp=x.index.get_indexer([sd])[0]
            if sp<0 or sp+1>=len(x):continue
            ep=sp+1; entry=float(x.iloc[ep].Open); atr=float(x.iloc[sp].ATR14)
            struct=float(x.iloc[int(e.StartPos):sp+1].Low.min())
            for method in METHODS:
                if method=="価格構造":stop=struct
                else:
                    if not np.isfinite(atr):continue
                    stop=entry-MULT[method]*atr
                R=entry-stop
                if R<=0:continue
                rows.append({"期間":period,"銘柄":ticker,"Event":int(e.Event),"Day0":e.Day0,
                    "シグナル":sig,"シグナル日":sd,"Entry日":x.index[ep],"EntryPos":ep,
                    "Entry":entry,"Stop方式":method,"ATR":atr,"Stop":stop,"1R":R,
                    "1R_%":R/entry*100,"価格構造R_ATR":(entry-struct)/atr if atr>0 else np.nan})
    return pd.DataFrame(rows)

def netr(entry,exit_,R,comm,slip):
    buy=entry*(1+slip);sell=exit_*(1-slip)
    return (sell-buy-buy*comm-sell*comm)/R

def outcome(x,d,h,comm,slip):
    ep=int(d.EntryPos);entry=float(d.Entry);stop=float(d.Stop);R=float(d["1R"]);target=entry+2*R
    last=min(ep+h-1,len(x)-1);mfe=0.;mae=0.
    for dt,b in x.iloc[ep:last+1].iterrows():
        op,hi,lo=float(b.Open),float(b.High),float(b.Low)
        mfe=max(mfe,(hi-entry)/R);mae=max(mae,(entry-lo)/R)
        if op<=stop:return ["Stop先着",dt,"Gap Open Stop",(op-entry)/R,netr(entry,op,R,comm,slip),mfe,mae]
        if op>=target:return ["Target先着",dt,"Gap Open Target",(op-entry)/R,netr(entry,op,R,comm,slip),mfe,mae]
        hs,ht=lo<=stop,hi>=target
        if hs and ht:return ["同日両方到達・順序不明",dt,"順序不明",np.nan,np.nan,mfe,mae]
        if hs:return ["Stop先着",dt,"Stop価格",-1.,netr(entry,stop,R,comm,slip),mfe,mae]
        if ht:return ["Target先着",dt,"Target価格",2.,netr(entry,target,R,comm,slip),mfe,mae]
    if ep+h-1>=len(x):return ["将来データ不足・未決着",pd.NaT,"データ不足",np.nan,np.nan,mfe,mae]
    dt=x.index[ep+h-1];close=float(x.iloc[ep+h-1].Close)
    return ["期間内未到達",dt,"期間末Close",(close-entry)/R,netr(entry,close,R,comm,slip),mfe,mae]

def make_outcomes(x,ds,comm,slip):
    rows=[]
    for _,d in ds.iterrows():
        for h in HORIZONS:
            z=outcome(x,d,h,comm,slip)
            q=d.to_dict();q.update({"Horizon":h,"評価期間":f"{h}営業日","結果":z[0],"結果日":z[1],
                "決済方法":z[2],"Gross_R":z[3],"Net_R":z[4],"MFE_R":z[5],"MAE_R":z[6]});rows.append(q)
    return pd.DataFrame(rows)

def summarize(o):
    rows=[]
    for k,g in o.groupby(["期間","銘柄","シグナル","Stop方式","Horizon"]):
        v=g[pd.to_numeric(g.Net_R,errors="coerce").notna()]
        n=pd.to_numeric(v.Net_R,errors="coerce")
        rows.append({"期間":k[0],"銘柄":k[1],"シグナル":k[2],"Stop方式":k[3],"評価期間":f"{k[4]}営業日",
            "Horizon":k[4],"件数":len(g),"Net_R計算可能":len(v),"Target先着":int((g.結果=="Target先着").sum()),
            "Stop先着":int((g.結果=="Stop先着").sum()),"期間内未到達":int((g.結果=="期間内未到達").sum()),
            "順序不明":int((g.結果=="同日両方到達・順序不明").sum()),"データ不足":int((g.結果=="将来データ不足・未決着").sum()),
            "Net合計R":n.sum() if len(n) else np.nan,"Net平均R":n.mean() if len(n) else np.nan,
            "Net中央値R":n.median() if len(n) else np.nan,"平均MFE_R":g.MFE_R.mean(),"平均MAE_R":g.MAE_R.mean()})
    return pd.DataFrame(rows)

def audit(evmap,ds):
    rows=[]
    for period in evmap:
        for ticker,ev in evmap[period].items():
            for sig in ["下落停止","反発開始"]:
                n=int(ev[sig].notna().sum())
                q=ds[(ds.期間==period)&(ds.銘柄==ticker)&(ds.シグナル==sig)]
                c=q.groupby("Stop方式").Event.nunique().to_dict() if len(q) else {}
                row={"期間":period,"銘柄":ticker,"完了BBイベント":len(ev),"シグナル":sig,"シグナル件数":n}
                for m in METHODS:row[m+"_設計件数"]=int(c.get(m,0))
                row["4方式件数一致"]="OK" if n and all(c.get(m,0)==n for m in METHODS) else ("該当なし" if n==0 else "要確認")
                rows.append(row)
    return pd.DataFrame(rows)

def risk_summary(ds):
    rows=[]
    for k,g in ds.groupby(["期間","銘柄","シグナル","Stop方式"]):
        rows.append({"期間":k[0],"銘柄":k[1],"シグナル":k[2],"Stop方式":k[3],"件数":len(g),
            "1R_%中央値":g["1R_%"].median(),"1R_%平均":g["1R_%"].mean(),
            "1R_%最小":g["1R_%"].min(),"1R_%最大":g["1R_%"].max(),
            "価格構造R_ATR中央値":g["価格構造R_ATR"].median()})
    return pd.DataFrame(rows)

def validation(s20):
    rows=[]
    for t in ["GOOG","NVDA"]:
        for sig in ["下落停止","反発開始"]:
            p=s20[(s20.期間=="前5年")&(s20.銘柄==t)&(s20.シグナル==sig)].dropna(subset=["Net平均R"])
            if p.empty:continue
            best=p.sort_values("Net平均R",ascending=False).iloc[0];m=best.Stop方式
            c=s20[(s20.期間=="現5年")&(s20.銘柄==t)&(s20.シグナル==sig)&(s20.Stop方式==m)]
            sc=s20[(s20.期間=="現5年")&(s20.銘柄==t)&(s20.シグナル==sig)&(s20.Stop方式=="価格構造")]
            rows.append({"銘柄":t,"シグナル":sig,"前5年だけで選択したStop":m,"前5年_選択Stop平均NetR":best["Net平均R"],
                "現5年_選択Stop平均NetR":c.iloc[0]["Net平均R"] if len(c) else np.nan,
                "現5年_価格構造平均NetR":sc.iloc[0]["Net平均R"] if len(sc) else np.nan,
                "現5年_選択Stop-価格構造":(c.iloc[0]["Net平均R"]-sc.iloc[0]["Net平均R"]) if len(c) and len(sc) else np.nan})
    return pd.DataFrame(rows)

def paired(o):
    x=o[o.Horizon==20];rows=[];ids=["期間","銘柄","シグナル","Event"]
    for period in ["前5年","現5年"]:
      for t in ["GOOG","NVDA"]:
       for sig in ["下落停止","反発開始"]:
        b=x[(x.期間==period)&(x.銘柄==t)&(x.シグナル==sig)&(x.Stop方式=="価格構造")][ids+["結果","Net_R"]].rename(columns={"結果":"構造結果","Net_R":"構造NetR"})
        for m in ["ATR×1","ATR×1.5","ATR×2"]:
            a=x[(x.期間==period)&(x.銘柄==t)&(x.シグナル==sig)&(x.Stop方式==m)][ids+["結果","Net_R"]].rename(columns={"結果":"ATR結果","Net_R":"ATRNetR"})
            p=b.merge(a,on=ids)
            if p.empty:continue
            v=p[p.構造NetR.notna()&p.ATRNetR.notna()].copy();diff=v.ATRNetR-v.構造NetR
            rows.append({"期間":period,"銘柄":t,"シグナル":sig,"比較Stop":m,"ペア件数":len(p),
                "構造Stop→ATRでは非Stop":int(((p.構造結果=="Stop先着")&(p.ATR結果!="Stop先着")).sum()),
                "ATR-構造_平均NetR差":diff.mean() if len(diff) else np.nan,
                "ATRが高い件数":int((diff>0).sum()),"構造が高い件数":int((diff<0).sum())})
    return pd.DataFrame(rows)

def yearly(o):
    x=o[(o.Horizon==20)&o.Net_R.notna()].copy();x["年"]=pd.to_datetime(x.Entry日).dt.year;rows=[]
    for k,g in x.groupby(["期間","年","銘柄","シグナル","Stop方式"]):
        rows.append({"期間":k[0],"年":int(k[1]),"銘柄":k[2],"シグナル":k[3],"Stop方式":k[4],"件数":len(g),
            "Net合計R":g.Net_R.sum(),"Net平均R":g.Net_R.mean(),"Net中央値R":g.Net_R.median(),
            "Target先着":int((g.結果=="Target先着").sum()),"Stop先着":int((g.結果=="Stop先着").sum())})
    return pd.DataFrame(rows)

def spec(comm,slip):
    return pd.DataFrame([
      ["Version",VERSION],["目的","Stop設計を独立研究。既存v5.3は変更しない"],
      ["前5年","2016-10-01～2021-09-30"],["現5年","2021-10-01～2026-09-30"],
      ["BB","20日 ±2σ / Low<=BB下限でDay0"],["イベント","Day0～Day3固定・再タッチ延長なし"],
      ["下落停止","Higher Low & Close Up"],["反発開始","Close > Prev High"],
      ["Entry","シグナル翌営業日Open"],["Stop","価格構造 / ATR×1 / ATR×1.5 / ATR×2"],
      ["ATR","Wilder ATR14・シグナル日まで"],["Target","+2R"],["評価","5 / 10 / 20営業日"],
      ["片道手数料",f"{comm*100:.3f}%"],["片道Slippage",f"{slip*100:.3f}%"],
      ["Gap","水準をOpenで飛び越えた場合はOpen約定"],["同日Stop+Target","順序不明・Net R除外"]
    ],columns=["項目","設定"])

@st.cache_data(ttl=3600,show_spinner=False)
def run_research(comm=0.001,slip=0.001):
    periods={"前5年":PRIOR,"現5年":CURRENT};all_d=[];all_o=[];evmap={"前5年":{},"現5年":{}}
    for pn,(start,end) in periods.items():
      for ticker in ["GOOG","NVDA"]:
        raw=get_data(ticker,start-pd.Timedelta(days=400),end+pd.Timedelta(days=45))
        if raw.empty:return {"error":f"{ticker} の株価データを取得できませんでした。"}
        x=indicators(raw);ev=events(x,start,end);evmap[pn][ticker]=ev
        ds=designs(ticker,pn,x,ev);o=make_outcomes(x,ds,comm,slip)
        all_d.append(ds);all_o.append(o)
    ds=pd.concat(all_d,ignore_index=True);o=pd.concat(all_o,ignore_index=True)
    s=summarize(o);s20=s[s.Horizon==20].copy()
    detail=o[o.Horizon==20][["期間","銘柄","Event","Day0","シグナル","シグナル日","Entry日","Entry","Stop方式","ATR","Stop","1R","1R_%","結果","結果日","決済方法","Gross_R","Net_R","MFE_R","MAE_R"]].copy()
    return {"error":None,"spec":spec(comm,slip),"audit":audit(evmap,ds),"risk":risk_summary(ds),
      "summary20":s20.drop(columns=["Horizon"]),"summary":s.drop(columns=["Horizon"]),
      "validation":validation(s20),"paired":paired(o),"yearly":yearly(o),"detail":detail}
