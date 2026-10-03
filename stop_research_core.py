import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

VERSION = "1.1.1"

PRIOR = (pd.Timestamp("2016-10-01"), pd.Timestamp("2021-09-30"))
CURRENT = (pd.Timestamp("2021-10-01"), pd.Timestamp("2026-09-30"))
METHODS = ["価格構造", "ATR×1", "ATR×1.5", "ATR×2"]
MULT = {"ATR×1": 1.0, "ATR×1.5": 1.5, "ATR×2": 2.0}
HORIZONS = [5, 10, 20]

@st.cache_data(ttl=3600, show_spinner=False)
def get_data(ticker, start, end):
    try:
        d = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=(end + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=False,
            progress=False,
            multi_level_index=False,
        )
    except Exception:
        return pd.DataFrame()

    if d is None or d.empty:
        return pd.DataFrame()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    if getattr(d.index, "tz", None) is not None:
        d.index = d.index.tz_localize(None)
    d.index = pd.to_datetime(d.index).normalize()

    for c in ["Open", "High", "Low", "Close"]:
        if c not in d.columns:
            return pd.DataFrame()
        d[c] = pd.to_numeric(d[c], errors="coerce")

    return d.dropna(subset=["Open", "High", "Low", "Close"]).sort_index()

def indicators(d):
    x = d.copy()
    middle = x["Close"].rolling(20).mean()
    std = x["Close"].rolling(20).std(ddof=0)
    x["BB_Lower"] = middle - 2.0 * std

    prev_close = x["Close"].shift(1)
    tr = pd.concat(
        [
            x["High"] - x["Low"],
            (x["High"] - prev_close).abs(),
            (x["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    x["ATR14"] = tr.ewm(
        alpha=1.0 / 14.0,
        adjust=False,
        min_periods=14,
    ).mean()

    x["PrevLow"] = x["Low"].shift(1)
    x["PrevClose"] = x["Close"].shift(1)
    x["PrevHigh"] = x["High"].shift(1)

    x["Decline"] = (x["Low"] > x["PrevLow"]) & (x["Close"] > x["PrevClose"])
    x["Rebound"] = x["Close"] > x["PrevHigh"]
    x["Touch"] = x["BB_Lower"].notna() & (x["Low"] <= x["BB_Lower"])
    return x

def events(x, start, end):
    rows = []
    p = 0
    eid = 0

    while p < len(x):
        dt = x.index[p]

        if dt < start:
            p += 1
            continue
        if dt > end:
            break

        if bool(x.iloc[p]["Touch"]):
            if p + 3 >= len(x) or x.index[p + 3] > end:
                break

            eid += 1
            w = x.iloc[p:p + 4]
            decline = w[w["Decline"].fillna(False)]
            rebound = w[w["Rebound"].fillna(False)]

            rows.append(
                {
                    "Event": eid,
                    "Day0": dt,
                    "StartPos": p,
                    "下落停止": decline.index[0] if len(decline) else pd.NaT,
                    "反発開始": rebound.index[0] if len(rebound) else pd.NaT,
                }
            )
            p += 4
        else:
            p += 1

    return pd.DataFrame(rows)

def build_design_records(ticker, period, x, ev):
    valid_rows = []
    attempt_rows = []

    for _, e in ev.iterrows():
        start_pos = int(e["StartPos"])

        for sig in ["下落停止", "反発開始"]:
            sd = e[sig]
            if pd.isna(sd):
                continue

            loc = x.index.get_indexer([pd.Timestamp(sd)])
            if len(loc) == 0 or loc[0] < 0:
                continue

            sp = int(loc[0])

            if sp + 1 >= len(x):
                for method in METHODS:
                    attempt_rows.append(
                        {
                            "期間": period,
                            "銘柄": ticker,
                            "Event": int(e["Event"]),
                            "Day0": e["Day0"],
                            "シグナル": sig,
                            "シグナル日": sd,
                            "Stop方式": method,
                            "設計可能": False,
                            "除外理由": "Entry翌営業日なし",
                            "Entry": np.nan,
                            "Stop": np.nan,
                            "1R": np.nan,
                        }
                    )
                continue

            ep = sp + 1
            entry = float(x.iloc[ep]["Open"])
            atr = float(x.iloc[sp]["ATR14"]) if pd.notna(x.iloc[sp]["ATR14"]) else np.nan
            struct = float(x.iloc[start_pos:sp + 1]["Low"].min())

            for method in METHODS:
                if method == "価格構造":
                    stop = struct
                    if not np.isfinite(stop):
                        reason = "価格構造Stop欠損"
                    elif entry <= stop:
                        reason = "Entry<=価格構造Stop"
                    else:
                        reason = ""
                else:
                    if not np.isfinite(atr) or atr <= 0:
                        stop = np.nan
                        reason = "ATR14計算不可"
                    else:
                        stop = entry - MULT[method] * atr
                        reason = "" if entry > stop else "Entry<=ATR Stop"

                R = entry - stop if np.isfinite(stop) else np.nan
                possible = bool(np.isfinite(R) and R > 0 and reason == "")

                attempt_rows.append(
                    {
                        "期間": period,
                        "銘柄": ticker,
                        "Event": int(e["Event"]),
                        "Day0": e["Day0"],
                        "シグナル": sig,
                        "シグナル日": sd,
                        "Stop方式": method,
                        "設計可能": possible,
                        "除外理由": reason,
                        "Entry": entry,
                        "Stop": stop,
                        "1R": R,
                    }
                )

                if possible:
                    valid_rows.append(
                        {
                            "期間": period,
                            "銘柄": ticker,
                            "Event": int(e["Event"]),
                            "Day0": e["Day0"],
                            "シグナル": sig,
                            "シグナル日": sd,
                            "Entry日": x.index[ep],
                            "EntryPos": ep,
                            "Entry": entry,
                            "Stop方式": method,
                            "ATR": atr,
                            "Stop": stop,
                            "1R": R,
                            "1R_%": R / entry * 100.0,
                            "価格構造Stop": struct,
                            "価格構造R_ATR": (
                                (entry - struct) / atr
                                if np.isfinite(atr) and atr > 0 else np.nan
                            ),
                        }
                    )

    return pd.DataFrame(valid_rows), pd.DataFrame(attempt_rows)

def common_population_filter(designs, attempts):
    if attempts.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    keys = ["期間", "銘柄", "シグナル", "Event"]

    possible = (
        attempts.groupby(keys)["設計可能"]
        .agg(["sum", "count"])
        .reset_index()
    )
    possible["共通比較対象"] = (
        (possible["sum"] == len(METHODS)) &
        (possible["count"] == len(METHODS))
    )

    common_keys = possible[possible["共通比較対象"]][keys].copy()

    common_designs = designs.merge(
        common_keys.assign(共通比較対象=True),
        on=keys,
        how="inner",
    )

    excluded_keys = possible[~possible["共通比較対象"]][keys].copy()

    if excluded_keys.empty:
        excluded = pd.DataFrame()
    else:
        excluded = attempts.merge(
            excluded_keys.assign(共通比較対象=False),
            on=keys,
            how="inner",
        )
        excluded = excluded[
            [
                "期間", "銘柄", "Event", "Day0", "シグナル", "シグナル日",
                "Stop方式", "設計可能", "除外理由", "Entry", "Stop", "1R",
                "共通比較対象",
            ]
        ].sort_values(
            ["期間", "銘柄", "シグナル", "Event", "Stop方式"]
        )

    return common_designs, excluded, possible

def netr(entry, exit_, R, comm, slip):
    buy = entry * (1.0 + slip)
    sell = exit_ * (1.0 - slip)
    return (sell - buy - buy * comm - sell * comm) / R

def outcome(x, d, h, comm, slip):
    ep = int(d["EntryPos"])
    entry = float(d["Entry"])
    stop = float(d["Stop"])
    R = float(d["1R"])
    target = entry + 2.0 * R

    last = min(ep + h - 1, len(x) - 1)
    mfe = 0.0
    mae = 0.0

    for dt, b in x.iloc[ep:last + 1].iterrows():
        op = float(b["Open"])
        hi = float(b["High"])
        lo = float(b["Low"])

        mfe = max(mfe, (hi - entry) / R)
        mae = max(mae, (entry - lo) / R)

        if op <= stop:
            return [
                "Stop先着", dt, "Gap Open Stop",
                (op - entry) / R,
                netr(entry, op, R, comm, slip),
                mfe, mae,
            ]

        if op >= target:
            return [
                "Target先着", dt, "Gap Open Target",
                (op - entry) / R,
                netr(entry, op, R, comm, slip),
                mfe, mae,
            ]

        hs = lo <= stop
        ht = hi >= target

        if hs and ht:
            return [
                "同日両方到達・順序不明", dt, "順序不明",
                np.nan, np.nan, mfe, mae,
            ]

        if hs:
            return [
                "Stop先着", dt, "Stop価格",
                -1.0,
                netr(entry, stop, R, comm, slip),
                mfe, mae,
            ]

        if ht:
            return [
                "Target先着", dt, "Target価格",
                2.0,
                netr(entry, target, R, comm, slip),
                mfe, mae,
            ]

    if ep + h - 1 >= len(x):
        return [
            "将来データ不足・未決着", pd.NaT, "データ不足",
            np.nan, np.nan, mfe, mae,
        ]

    dt = x.index[ep + h - 1]
    close = float(x.iloc[ep + h - 1]["Close"])

    return [
        "期間内未到達", dt, "期間末Close",
        (close - entry) / R,
        netr(entry, close, R, comm, slip),
        mfe, mae,
    ]

def make_outcomes(x, ds, comm, slip):
    rows = []

    for _, d in ds.iterrows():
        for h in HORIZONS:
            z = outcome(x, d, h, comm, slip)
            q = d.to_dict()
            q.update(
                {
                    "Horizon": h,
                    "評価期間": f"{h}営業日",
                    "結果": z[0],
                    "結果日": z[1],
                    "決済方法": z[2],
                    "Gross_R": z[3],
                    "Net_R": z[4],
                    "MFE_R": z[5],
                    "MAE_R": z[6],
                }
            )
            rows.append(q)

    return pd.DataFrame(rows)

def summarize(o):
    rows = []

    for k, g in o.groupby(
        ["期間", "銘柄", "シグナル", "Stop方式", "Horizon"]
    ):
        v = g[pd.to_numeric(g["Net_R"], errors="coerce").notna()]
        n = pd.to_numeric(v["Net_R"], errors="coerce")

        rows.append(
            {
                "期間": k[0],
                "銘柄": k[1],
                "シグナル": k[2],
                "Stop方式": k[3],
                "評価期間": f"{k[4]}営業日",
                "Horizon": k[4],
                "共通母集団件数": len(g),
                "Net_R計算可能": len(v),
                "Target先着": int((g["結果"] == "Target先着").sum()),
                "Stop先着": int((g["結果"] == "Stop先着").sum()),
                "期間内未到達": int((g["結果"] == "期間内未到達").sum()),
                "順序不明": int((g["結果"] == "同日両方到達・順序不明").sum()),
                "データ不足": int((g["結果"] == "将来データ不足・未決着").sum()),
                "Net合計R": n.sum() if len(n) else np.nan,
                "Net平均R": n.mean() if len(n) else np.nan,
                "Net中央値R": n.median() if len(n) else np.nan,
                "平均MFE_R": g["MFE_R"].mean(),
                "平均MAE_R": g["MAE_R"].mean(),
            }
        )

    return pd.DataFrame(rows)

def audit(evmap, attempts, common_status):
    rows = []

    for period in evmap:
        for ticker, ev in evmap[period].items():
            for sig in ["下落停止", "反発開始"]:
                signal_count = int(ev[sig].notna().sum())

                a = attempts[
                    (attempts["期間"] == period) &
                    (attempts["銘柄"] == ticker) &
                    (attempts["シグナル"] == sig)
                ]

                s = common_status[
                    (common_status["期間"] == period) &
                    (common_status["銘柄"] == ticker) &
                    (common_status["シグナル"] == sig)
                ]

                common_count = int(s["共通比較対象"].sum()) if len(s) else 0

                row = {
                    "期間": period,
                    "銘柄": ticker,
                    "完了BBイベント": len(ev),
                    "シグナル": sig,
                    "元シグナル件数": signal_count,
                }

                for m in METHODS:
                    q = a[a["Stop方式"] == m]
                    row[m + "_設計可能"] = int(q["設計可能"].sum()) if len(q) else 0

                row["4方式共通比較件数"] = common_count
                row["共通母集団除外件数"] = signal_count - common_count

                common_method_counts = []
                for m in METHODS:
                    q = a[a["Stop方式"] == m].merge(
                        s[s["共通比較対象"]][
                            ["期間", "銘柄", "シグナル", "Event"]
                        ],
                        on=["期間", "銘柄", "シグナル", "Event"],
                        how="inner",
                    )
                    common_method_counts.append(len(q))

                row["共通母集団4方式一致"] = (
                    "OK"
                    if all(v == common_count for v in common_method_counts)
                    else "要確認"
                )

                rows.append(row)

    return pd.DataFrame(rows)

def risk_summary(ds):
    rows = []

    for k, g in ds.groupby(["期間", "銘柄", "シグナル", "Stop方式"]):
        rows.append(
            {
                "期間": k[0],
                "銘柄": k[1],
                "シグナル": k[2],
                "Stop方式": k[3],
                "共通母集団件数": len(g),
                "1R_%中央値": g["1R_%"].median(),
                "1R_%平均": g["1R_%"].mean(),
                "1R_%最小": g["1R_%"].min(),
                "1R_%最大": g["1R_%"].max(),
                "価格構造R_ATR中央値": g["価格構造R_ATR"].median(),
            }
        )

    return pd.DataFrame(rows)

def validation(s20):
    rows = []

    for ticker in ["GOOG", "NVDA"]:
        for sig in ["下落停止", "反発開始"]:
            p = s20[
                (s20["期間"] == "前5年") &
                (s20["銘柄"] == ticker) &
                (s20["シグナル"] == sig)
            ].dropna(subset=["Net平均R"])

            if p.empty:
                continue

            best = p.sort_values(
                ["Net平均R", "Stop方式"],
                ascending=[False, True],
            ).iloc[0]

            method = best["Stop方式"]

            c = s20[
                (s20["期間"] == "現5年") &
                (s20["銘柄"] == ticker) &
                (s20["シグナル"] == sig) &
                (s20["Stop方式"] == method)
            ]

            sc = s20[
                (s20["期間"] == "現5年") &
                (s20["銘柄"] == ticker) &
                (s20["シグナル"] == sig) &
                (s20["Stop方式"] == "価格構造")
            ]

            rows.append(
                {
                    "銘柄": ticker,
                    "シグナル": sig,
                    "前5年だけで選択したStop": method,
                    "前5年_選択Stop平均NetR": best["Net平均R"],
                    "現5年_選択Stop平均NetR": (
                        c.iloc[0]["Net平均R"] if len(c) else np.nan
                    ),
                    "現5年_価格構造平均NetR": (
                        sc.iloc[0]["Net平均R"] if len(sc) else np.nan
                    ),
                    "現5年_選択Stop-価格構造": (
                        c.iloc[0]["Net平均R"] - sc.iloc[0]["Net平均R"]
                        if len(c) and len(sc) else np.nan
                    ),
                }
            )

    return pd.DataFrame(rows)

def paired(o):
    x = o[o["Horizon"] == 20].copy()
    rows = []
    ids = ["期間", "銘柄", "シグナル", "Event"]

    for period in ["前5年", "現5年"]:
        for ticker in ["GOOG", "NVDA"]:
            for sig in ["下落停止", "反発開始"]:
                b = x[
                    (x["期間"] == period) &
                    (x["銘柄"] == ticker) &
                    (x["シグナル"] == sig) &
                    (x["Stop方式"] == "価格構造")
                ][ids + ["結果", "Net_R"]].rename(
                    columns={"結果": "構造結果", "Net_R": "構造NetR"}
                )

                for method in ["ATR×1", "ATR×1.5", "ATR×2"]:
                    a = x[
                        (x["期間"] == period) &
                        (x["銘柄"] == ticker) &
                        (x["シグナル"] == sig) &
                        (x["Stop方式"] == method)
                    ][ids + ["結果", "Net_R"]].rename(
                        columns={"結果": "ATR結果", "Net_R": "ATRNetR"}
                    )

                    p = b.merge(a, on=ids, how="inner")

                    if p.empty:
                        continue

                    v = p[
                        pd.to_numeric(p["構造NetR"], errors="coerce").notna() &
                        pd.to_numeric(p["ATRNetR"], errors="coerce").notna()
                    ].copy()

                    diff = (
                        pd.to_numeric(v["ATRNetR"], errors="coerce") -
                        pd.to_numeric(v["構造NetR"], errors="coerce")
                    )

                    rows.append(
                        {
                            "期間": period,
                            "銘柄": ticker,
                            "シグナル": sig,
                            "比較Stop": method,
                            "共通ペア件数": len(p),
                            "両方NetR計算可能": len(v),
                            "構造Stop→ATRでは非Stop": int(
                                (
                                    (p["構造結果"] == "Stop先着") &
                                    (p["ATR結果"] != "Stop先着")
                                ).sum()
                            ),
                            "構造非Stop→ATRではStop": int(
                                (
                                    (p["構造結果"] != "Stop先着") &
                                    (p["ATR結果"] == "Stop先着")
                                ).sum()
                            ),
                            "ATR-構造_平均NetR差": (
                                diff.mean() if len(diff) else np.nan
                            ),
                            "ATRが高い件数": int((diff > 0).sum()),
                            "構造が高い件数": int((diff < 0).sum()),
                        }
                    )

    return pd.DataFrame(rows)

def yearly(o):
    x = o[
        (o["Horizon"] == 20) &
        pd.to_numeric(o["Net_R"], errors="coerce").notna()
    ].copy()

    if x.empty:
        return pd.DataFrame()

    x["年"] = pd.to_datetime(x["Entry日"]).dt.year
    rows = []

    for k, g in x.groupby(
        ["期間", "年", "銘柄", "シグナル", "Stop方式"]
    ):
        rows.append(
            {
                "期間": k[0],
                "年": int(k[1]),
                "銘柄": k[2],
                "シグナル": k[3],
                "Stop方式": k[4],
                "件数": len(g),
                "Net合計R": g["Net_R"].sum(),
                "Net平均R": g["Net_R"].mean(),
                "Net中央値R": g["Net_R"].median(),
                "Target先着": int((g["結果"] == "Target先着").sum()),
                "Stop先着": int((g["結果"] == "Stop先着").sum()),
            }
        )

    return pd.DataFrame(rows)

def spec(comm, slip):
    return pd.DataFrame(
        [
            ["Version", VERSION],
            ["目的", "Stop設計を独立研究。既存v5.3は変更しない"],
            ["比較母集団", "4方式すべて設計可能な同一イベントだけ"],
            ["除外処理", "除外イベントを別監査表へ保存"],
            ["前5年", "2016-10-01～2021-09-30"],
            ["現5年", "2021-10-01～2026-09-30"],
            ["BB", "20日 ±2σ / Low<=BB下限でDay0"],
            ["イベント", "Day0～Day3固定・再タッチ延長なし"],
            ["下落停止", "Higher Low & Close Up"],
            ["反発開始", "Close > Prev High"],
            ["Entry", "シグナル翌営業日Open"],
            ["Stop", "価格構造 / ATR×1 / ATR×1.5 / ATR×2"],
            ["ATR", "Wilder ATR14・シグナル日まで"],
            ["Target", "+2R"],
            ["評価", "5 / 10 / 20営業日"],
            ["片道手数料", f"{comm * 100:.3f}%"],
            ["片道Slippage", f"{slip * 100:.3f}%"],
            ["Gap", "水準をOpenで飛び越えた場合はOpen約定"],
            ["同日Stop+Target", "順序不明・Net R除外"],
        ],
        columns=["項目", "設定"],
    )

@st.cache_data(ttl=3600, show_spinner=False)
def run_research(comm=0.001, slip=0.001):
    periods = {"前5年": PRIOR, "現5年": CURRENT}

    all_valid_designs = []
    all_attempts = []
    data_map = {}
    evmap = {"前5年": {}, "現5年": {}}

    for pn, (start, end) in periods.items():
        for ticker in ["GOOG", "NVDA"]:
            raw = get_data(
                ticker,
                start - pd.Timedelta(days=400),
                end + pd.Timedelta(days=45),
            )

            if raw.empty:
                return {"error": f"{ticker} の株価データを取得できませんでした。"}

            x = indicators(raw)
            data_map[(pn, ticker)] = x

            ev = events(x, start, end)
            evmap[pn][ticker] = ev

            valid, attempts = build_design_records(
                ticker, pn, x, ev
            )

            all_valid_designs.append(valid)
            all_attempts.append(attempts)

    valid_designs = (
        pd.concat(all_valid_designs, ignore_index=True)
        if all_valid_designs else pd.DataFrame()
    )

    attempts = (
        pd.concat(all_attempts, ignore_index=True)
        if all_attempts else pd.DataFrame()
    )

    common_designs, excluded, common_status = common_population_filter(
        valid_designs, attempts
    )

    all_outcomes = []

    for (pn, ticker), x in data_map.items():
        ds = common_designs[
            (common_designs["期間"] == pn) &
            (common_designs["銘柄"] == ticker)
        ]

        if not ds.empty:
            all_outcomes.append(
                make_outcomes(x, ds, comm, slip)
            )

    outcomes = (
        pd.concat(all_outcomes, ignore_index=True)
        if all_outcomes else pd.DataFrame()
    )

    if outcomes.empty:
        return {"error": "共通比較母集団の損益計算結果がありません。"}

    summary = summarize(outcomes)
    summary20 = summary[summary["Horizon"] == 20].copy()

    detail_cols = [
        "期間", "銘柄", "Event", "Day0", "シグナル", "シグナル日",
        "Entry日", "Entry", "Stop方式", "ATR", "Stop", "1R", "1R_%",
        "共通比較対象", "結果", "結果日", "決済方法",
        "Gross_R", "Net_R", "MFE_R", "MAE_R",
    ]

    detail = outcomes[
        outcomes["Horizon"] == 20
    ][detail_cols].copy()

    return {
        "error": None,
        "spec": spec(comm, slip),
        "audit": audit(evmap, attempts, common_status),
        "excluded": excluded,
        "risk": risk_summary(common_designs),
        "summary20": summary20.drop(columns=["Horizon"]),
        "summary": summary.drop(columns=["Horizon"]),
        "validation": validation(summary20),
        "paired": paired(outcomes),
        "yearly": yearly(outcomes),
        "detail": detail,
    }
