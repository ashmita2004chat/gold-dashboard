import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================
# App config
# =========================
st.set_page_config(
    page_title="Gold Dashboard (HS 7108)",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Styling (gold theme)
# =========================
APP_CSS = """
<style>
:root{
  --bg1:#f6f1e8;
  --bg2:#eef3ff;
  --card:#ffffff;
  --text:#0f172a;
  --muted:#64748b;
  --accent:#b8860b; /* darkgoldenrod */
  --accent2:#8b5a2b; /* brown */
  --border:rgba(15,23,42,.08);
  --shadow: 0 10px 30px rgba(15, 23, 42, 0.10);
}
.stApp{
  background: radial-gradient(1200px 600px at 15% 15%, var(--bg1) 0%, rgba(255,255,255,0) 60%),
              radial-gradient(900px 500px at 95% 10%, var(--bg2) 0%, rgba(255,255,255,0) 55%),
              linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #0b1220 0%, #0b1220 55%, #070b14 100%);
  border-right: 1px solid rgba(255,255,255,.06);
}
section[data-testid="stSidebar"] *{
  color: rgba(255,255,255,.92) !important;
}
.sidebar-title{
  font-weight:800;
  letter-spacing: .3px;
  font-size: 22px;
  margin: 2px 0 6px 0;
}
.sidebar-sub{
  color: rgba(255,255,255,.70) !important;
  font-size: 12.5px;
  margin-bottom: 10px;
}
.badge{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(184,134,11,.35);
  background: rgba(184,134,11,.14);
  color: rgba(255,255,255,.92) !important;
  font-size: 12px;
  font-weight: 700;
}
.header-wrap{
  background: rgba(255,255,255,.78);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 18px 20px;
  margin: 4px 0 14px 0;
  backdrop-filter: blur(10px);
}

/* --- Hero header enhancements --- */
.header-wrap.hero{ position: relative; overflow: hidden; }
.header-wrap.hero::before{
  content: "";
  position: absolute;
  top: -80px;
  right: -90px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle at 30% 30%, rgba(184,134,11,.38) 0%, rgba(184,134,11,0) 70%);
  transform: rotate(10deg);
  pointer-events: none;
}
.header-wrap.hero::after{
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 4px;
  background: linear-gradient(90deg, rgba(184,134,11,0), rgba(184,134,11,.55), rgba(139,90,43,.45), rgba(184,134,11,0));
  opacity: .95;
  pointer-events: none;
}
.hero-row{ display:flex; justify-content:space-between; align-items:flex-start; gap:14px; position:relative; z-index:2; }
.hero-left{ display:flex; gap:14px; align-items:flex-start; }
.hero-right{ display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
.hero-icon{
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: linear-gradient(135deg, rgba(184,134,11,.18), rgba(139,90,43,.10));
  border: 1px solid rgba(184,134,11,.26);
  box-shadow: 0 10px 26px rgba(15,23,42,0.08);
}
.hero-icon svg{ width: 34px; height: 34px; }
.hero-art{
  position:absolute;
  right: 16px;
  bottom: -8px;
  width: 190px;
  opacity: .18;
  pointer-events:none;
  z-index:1;
}
.hero-art svg{ width: 100%; height: auto; }
.h1{
  font-size: 38px;
  line-height: 1.08;
  font-weight: 900;
  color: var(--text);
  margin: 0;
}
.hsub{
  margin-top: 6px;
  font-size: 14px;
  color: var(--muted);
  font-weight: 600;
}
.kpi{
  background: rgba(255,255,255,.86);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
  padding: 14px 14px;
  display:flex;
  gap: 12px;
  align-items:center;
  min-height: 84px;
}
.kpi .ico{
  width:44px;
  height:44px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(184,134,11,.14);
  border: 1px solid rgba(184,134,11,.25);
  font-size: 22px;
}
.kpi .lbl{
  font-size: 12.5px;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 2px;
}
.kpi .val{
  font-size: 22px;
  font-weight: 900;
  color: var(--text);
  line-height: 1.05;
}
.kpi .sub{
  font-size: 12.5px;
  color: var(--muted);
  font-weight: 650;
  margin-top: 3px;
}
.small-note{
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 600;
}
hr.soft{
  border: none;
  border-top: 1px solid rgba(15,23,42,.08);
  margin: 10px 0 14px 0;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# =========================
# Files
# =========================
PROD_FILE = "Production of Gold.xlsx"
TRADE_FILE = "Gold(7108).xlsx"
JEWELLERY_FILE = "7113-Gold Jewellery.xlsx"
JEWELLERY_CODES = {"711319", "711320"}
PRICE_FILE = "Gold_price_averages_with_countries.xlsx"

HS6_PAGES = [
    ("Trade — 7108 (Total)", None),
    ("710811 — GOLD (POWDER FORM)", "710811"),
    ("710812 — GOLD UNWROUGHT (BARS)", "710812"),
    ("710813 — GOLD (OTHER SEMI-MANUFACTURED FORMS)", "710813"),
    ("710820 — GOLD MONETARY", "710820"),
    ("711319 — Articles of Gold Jewellery & Parts Thereof", "711319"),
    ("711320 — Gold Jewellery Clad with Precious Metal", "711320"),
]


# =========================
# Hero visuals (inline SVG)
# =========================
GOLD_ICON_SVG = """
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" fill="none">
  <defs>
    <linearGradient id="goldGrad" x1="14" y1="14" x2="50" y2="50" gradientUnits="userSpaceOnUse">
      <stop stop-color="#F5D26B"/>
      <stop offset="0.55" stop-color="#B8860B"/>
      <stop offset="1" stop-color="#8B5A2B"/>
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="22" fill="url(#goldGrad)" opacity="0.95"/>
  <circle cx="32" cy="32" r="17" stroke="rgba(255,255,255,0.55)" stroke-width="2"/>
  <text x="32" y="39" text-anchor="middle" font-size="18" font-weight="800" fill="#0f172a" font-family="ui-sans-serif, system-ui">Au</text>
</svg>
"""

GOLD_ART_SVG = """
<svg viewBox="0 0 240 120" xmlns="http://www.w3.org/2000/svg" fill="none">
  <defs>
    <linearGradient id="bar" x1="20" y1="20" x2="220" y2="100" demonstrateUnits="userSpaceOnUse">
      <stop stop-color="#F6E08B"/>
      <stop offset="0.55" stop-color="#B8860B"/>
      <stop offset="1" stop-color="#8B5A2B"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="rgba(255,255,255,0)"/>
      <stop offset="0.5" stop-color="rgba(255,255,255,0.55)"/>
      <stop offset="1" stop-color="rgba(255,255,255,0)"/>
    </linearGradient>
  </defs>
  <g opacity="0.95">
    <path d="M36 38 L76 20 H210 L196 82 H52 Z" fill="url(#bar)"/>
    <path d="M76 20 L196 82" stroke="rgba(255,255,255,0.35)" stroke-width="3"/>
    <path d="M56 60 L190 60" stroke="url(#shine)" stroke-width="8" opacity="0.55"/>
    <path d="M52 82 L196 82" stroke="rgba(15,23,42,0.20)" stroke-width="3"/>
    <path d="M76 20 H210" stroke="rgba(15,23,42,0.16)" stroke-width="3"/>
  </g>
</svg>
"""

# =========================
# Helpers
# =========================
def resolve_file(filename: str) -> Path:
    candidates = [
        Path(filename),
        Path("/mnt/data") / filename,
        Path("/content") / filename,
        Path.cwd() / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]  # default

def _detect_year_header_row(df_raw: pd.DataFrame) -> int | None:
    for i in range(min(len(df_raw), 80)):
        row = df_raw.iloc[i].tolist()
        years = []
        for v in row:
            if isinstance(v, (int, float)) and not pd.isna(v):
                iv = int(v)
                if 1900 <= iv <= 2100:
                    years.append(iv)
            elif isinstance(v, str):
                m = re.fullmatch(r"\s*(\d{4})\s*", v)
                if m:
                    years.append(int(m.group(1)))
        if len(set(years)) >= 8:
            return i
    return None

def _fmt_num(x: float, decimals: int = 1) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    try:
        return f"{x:,.{decimals}f}"
    except Exception:
        return "—"

def _fmt_pct(x: float, decimals: int = 1) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:+.{decimals}f}%"

def _trade_unit_label(unit: str) -> str:
    return {"USD (Absolute)": "USD", "USD Mn": "USD Mn", "USD Bn": "USD Bn"}.get(unit, unit)

def _scale_trade_thousand(val_thousand: float, unit: str) -> tuple[float, str]:
    """
    Base is USD thousand (as exported by ITC Trade Map files).
    """
    if val_thousand is None or (isinstance(val_thousand, float) and np.isnan(val_thousand)):
        return (np.nan, "")
    if unit == "USD (Absolute)":
        return (val_thousand * 1.0, "USD")
    if unit == "USD Mn":
        return (val_thousand / 1000.0, "USD Mn")
    if unit == "USD Bn":
        return (val_thousand / 1_000_000.0, "USD Bn")
    return (val_thousand / 1_000_000.0, "USD Bn")

def _yoy(series: pd.Series, year: int) -> float:
    prev = year - 1
    if year not in series.index or prev not in series.index:
        return np.nan
    a = series.loc[prev]
    b = series.loc[year]
    if a is None or b is None or pd.isna(a) or pd.isna(b) or a == 0:
        return np.nan
    return (b / a - 1.0) * 100.0

def _cagr(series: pd.Series, start_year: int, end_year: int) -> float:
    if start_year not in series.index or end_year not in series.index:
        return np.nan
    start = series.loc[start_year]
    end = series.loc[end_year]
    n = end_year - start_year
    if n <= 0 or pd.isna(start) or pd.isna(end) or start <= 0 or end <= 0:
        return np.nan
    return (end / start) ** (1.0 / n) - 1.0

def _kpi_card(icon: str, label: str, value: str, sub: str = "") -> None:
    # Auto-shrink long values (e.g., USD absolute) so they don't overflow the card
    v = "" if value is None else str(value)
    digits = len(re.sub(r"[^0-9]", "", v))
    # Conservative thresholds to keep cards stable on different screens
    if digits >= 13 or len(v) >= 16:
        val_style = "font-size:18px; line-height:1.05; word-break:break-word;"
    elif digits >= 10 or len(v) >= 13:
        val_style = "font-size:20px; line-height:1.05; word-break:break-word;"
    else:
        val_style = "font-size:22px; line-height:1.05; word-break:break-word;"

    st.markdown(
        f"""
        <div class="kpi">
          <div class="ico">{icon}</div>
          <div>
            <div class="lbl">{label}</div>
            <div class="val" style="{val_style}">{v}</div>
            <div class="sub">{sub}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# =========================
# Chart label helpers
# =========================
def _add_line_point_labels(fig, fmt: str = "{:,.2f}"):
    """Add value labels on *all* points of each scatter/line trace (safe for numpy arrays)."""
    for tr in getattr(fig, "data", []) or []:
        if not hasattr(tr, "y") or tr.y is None:
            continue
        try:
            yvals = list(tr.y)
        except Exception:
            yvals = [tr.y]

        if len(yvals) == 0:
            continue

        txt = []
        for v in yvals:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                txt.append("")
            else:
                try:
                    txt.append(fmt.format(float(v)))
                except Exception:
                    txt.append(str(v))

        tr.text = txt
        tr.textposition = "top center"
        mode = getattr(tr, "mode", "") or ""
        if "text" not in mode:
            tr.mode = (mode + "+text") if mode else "lines+text"

def _add_bar_labels(fig, orientation: str = "h", fmt: str = "{:,.2f}"):
    """Add value labels to Plotly bar traces (safe for numpy arrays)."""
    for tr in getattr(fig, "data", []) or []:
        # Extract values safely (avoid truth-value checks on numpy arrays)
        if orientation == "h":
            arr = getattr(tr, "x", None)
        else:
            arr = getattr(tr, "y", None)

        if arr is None:
            continue

        try:
            vals = list(arr)
        except Exception:
            vals = [arr]

        txt = []
        for v in vals:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                txt.append("")
            else:
                try:
                    txt.append(fmt.format(float(v)))
                except Exception:
                    txt.append(str(v))

        tr.text = txt
        tr.textposition = "outside"
        tr.cliponaxis = False


def load_production_long(path: str) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None, sheet_name=0)
    hdr = _detect_year_header_row(raw)
    if hdr is None:
        raise ValueError("Could not detect year header row in the production sheet.")
    header_row = raw.iloc[hdr].tolist()
    year_cols = []
    idxs = []
    for j, v in enumerate(header_row):
        year = None
        if isinstance(v, (int, float)) and not pd.isna(v):
            iv = int(v)
            if 1900 <= iv <= 2100:
                year = iv
        elif isinstance(v, str):
            m = re.fullmatch(r"\s*(\d{4})\s*", v)
            if m:
                year = int(m.group(1))
        if year is not None:
            year_cols.append(year)
            idxs.append(j)

    region = None
    recs = []
    for i in range(hdr + 1, len(raw)):
        name = raw.iat[i, 0]
        if pd.isna(name):
            continue
        name = str(name).strip()
        if not name:
            continue

        vals = [raw.iat[i, j] for j in idxs]
        if all(pd.isna(v) for v in vals):
            region = name
            continue

        for yr, j in zip(year_cols, idxs):
            v = raw.iat[i, j]
            v = pd.to_numeric(v, errors="coerce")
            if pd.isna(v):
                continue
            recs.append({"region": region or "Unknown", "country": name, "year": int(yr), "tonnes": float(v)})

    df = pd.DataFrame(recs)
    df["country"] = df["country"].str.replace(r"\s+", " ", regex=True).str.strip()
    return df

def _tidy_trade_sheet(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(columns={df.columns[0]: "partner"})
    year_map = {}
    for c in df.columns[1:]:
        m = re.search(r"(19|20)\d{2}", str(c))
        if m:
            year_map[c] = int(m.group(0))
    keep = ["partner"] + list(year_map.keys())
    df = df[keep].rename(columns=year_map)
    for yr in year_map.values():
        df[yr] = pd.to_numeric(df[yr], errors="coerce")
    df["partner"] = df["partner"].astype(str).str.strip()
    df = df[df["partner"].str.lower() != "nan"]
    return df

@st.cache_data(show_spinner=False)
def load_trade_total(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    imp = _tidy_trade_sheet(pd.read_excel(path, sheet_name="Imports(7108)"))
    exp = _tidy_trade_sheet(pd.read_excel(path, sheet_name="Exports(7108)"))
    return imp, exp

@st.cache_data(show_spinner=False)
def load_trade_hs6(path: str, sheet_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)

    def find_row(pattern: str) -> int | None:
        for i in range(len(raw)):
            v = raw.iat[i, 0]
            if isinstance(v, str) and re.search(pattern, v, re.I):
                return i
        return None

    imp_row = find_row(r"^Importers$") or find_row(r"Importers")
    exp_row = find_row(r"^Exporters$") or find_row(r"Exporters")

    if imp_row is None or exp_row is None:
        raise ValueError(f"Could not find Importers/Exporters blocks in sheet '{sheet_name}'.")

    def parse_block(start_row: int) -> pd.DataFrame:
        header = raw.iloc[start_row].tolist()
        idxs, years = [], []
        for j, c in enumerate(header):
            if j == 0:
                continue
            if c is None or (isinstance(c, float) and pd.isna(c)):
                continue
            m = re.search(r"(19|20)\d{2}", str(c))
            if m:
                years.append(int(m.group(0)))
                idxs.append(j)

        recs = []
        for i in range(start_row + 1, len(raw)):
            name = raw.iat[i, 0]
            if pd.isna(name):
                vals = [raw.iat[i, j] for j in idxs]
                if all(pd.isna(v) for v in vals):
                    break
                continue
            name = str(name).strip()
            if not name:
                continue
            vals = [raw.iat[i, j] for j in idxs]
            if all(pd.isna(v) for v in vals):
                break
            rec = {"partner": name}
            for yr, j in zip(years, idxs):
                rec[yr] = pd.to_numeric(raw.iat[i, j], errors="coerce")
            recs.append(rec)

        return pd.DataFrame(recs)

    imp = parse_block(imp_row)
    exp = parse_block(exp_row)
    return imp, exp

# =========================
# Gold prices (per troy ounce) — workbook loader
# =========================
@st.cache_data(show_spinner=False)
def load_gold_prices(path: str) -> dict[str, pd.DataFrame]:
    """
    Reads Gold_price_averages_with_countries.xlsx which contains:
      - Currency_Country_Map (currency -> mapped country/region)
      - Yearly_Avg / Quarterly_Avg / Monthly_Avg (wide blocks with header rows)
    Returns a dict with keys: map, yearly, quarterly, monthly (all in long format).
    """
    map_df = pd.read_excel(path, sheet_name="Currency_Country_Map")

    map2 = (
        map_df.rename(
            columns={
                "Currency Code": "currency_code",
                "Currency Name": "currency_name",
                "Country/Region (mapped)": "mapped_country",
            }
        )
        .copy()
    )

    def _parse_sheet(sheet_name: str, freq: str) -> pd.DataFrame:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None)

        # Find the row/col where "COUNTRY" appears (this is the header row for country names)
        country_row = None
        country_col = None
        for i in range(len(raw)):
            row = raw.iloc[i].astype(str).str.strip()
            mask = row.eq("COUNTRY")
            if mask.any():
                country_row = i
                country_col = int(np.where(mask.values)[0][0])
                break

        if country_row is None or country_col is None:
            raise ValueError(f"Could not find COUNTRY header in sheet: {sheet_name}")

        currency_row = country_row - 1
        data_cols = [c for c in raw.columns if c > country_col]

        currency_codes = raw.iloc[currency_row, data_cols].astype(str).str.strip()
        country_names = raw.iloc[country_row, data_cols].astype(str).str.strip()

        # Build wide (date + currency columns)
        df_wide = raw.iloc[country_row + 1 :, [country_col] + data_cols].copy()
        df_wide.columns = ["date"] + currency_codes.tolist()
        df_wide["date"] = pd.to_datetime(df_wide["date"], errors="coerce")
        df_wide = df_wide.dropna(subset=["date"])

        for c in currency_codes.tolist():
            df_wide[c] = pd.to_numeric(df_wide[c], errors="coerce")

        df_long = (
            df_wide.melt(id_vars=["date"], var_name="currency_code", value_name="price")
            .dropna(subset=["price"])
            .copy()
        )
        df_long["currency_code"] = df_long["currency_code"].astype(str).str.strip()

        # Merge mapping, and keep fallback country name from the sheet
        cn_map = pd.DataFrame(
            {"currency_code": currency_codes.tolist(), "country_name_sheet": country_names.tolist()}
        )
        df_long = df_long.merge(map2, on="currency_code", how="left").merge(cn_map, on="currency_code", how="left")
        df_long["mapped_country"] = df_long["mapped_country"].fillna(df_long["country_name_sheet"])

        # Period label + YoY and period-on-period %
        df_long = df_long.sort_values(["currency_code", "date"])
        if freq == "Y":
            lag = 1
            df_long["period_label"] = df_long["date"].dt.year.astype(int).astype(str)
        elif freq == "Q":
            lag = 4
            df_long["period_label"] = df_long["date"].dt.to_period("Q").astype(str)
        else:
            lag = 12
            df_long["period_label"] = df_long["date"].dt.to_period("M").astype(str)

        df_long["pct_change"] = df_long.groupby("currency_code")["price"].pct_change() * 100
        df_long["yoy_pct"] = df_long.groupby("currency_code")["price"].pct_change(lag) * 100

        return df_long

    yearly = _parse_sheet("Yearly_Avg", "Y")
    quarterly = _parse_sheet("Quarterly_Avg", "Q")
    monthly = _parse_sheet("Monthly_Avg", "M")

    return {"map": map_df, "yearly": yearly, "quarterly": quarterly, "monthly": monthly}


def _calc_cagr(last: float | None, prev: float | None, years: float) -> float | None:
    if last is None or prev is None:
        return None
    try:
        last = float(last)
        prev = float(prev)
    except Exception:
        return None
    if prev <= 0 or last <= 0:
        return None
    return (last / prev) ** (1 / years) - 1


def show_gold_prices() -> None:
    price_path = resolve_file(PRICE_FILE)
    if not price_path.exists():
        st.error(f"Missing {PRICE_FILE}. Place it in the working folder, /mnt/data, or /content.")
        return


    prices = load_gold_prices(str(price_path))

    # Hero header (match Production style)
    try:
        _yrs = prices["yearly"]["date"].dt.year.dropna().astype(int)
        _miny = int(_yrs.min()) if len(_yrs) else None
        _maxy = int(_yrs.max()) if len(_yrs) else None
    except Exception:
        _miny, _maxy = None, None

    _badge = f"{_miny}–{_maxy}" if (_miny is not None and _maxy is not None) else ""
    _badge_html = f"<div class='badge'>{_badge}</div>" if _badge else ""

    st.markdown(
        f"""
        <div class="header-wrap hero">
          <div class="hero-row">
            <div class="hero-left">
              <div class="hero-icon">{GOLD_ICON_SVG}</div>
              <div>
                <div class="h1">Gold Prices</div>
                <div class="hsub">Average gold price per <b>troy ounce</b> in local currencies • Yearly/Quarterly/Monthly</div>
              </div>
            </div>
            <div class="hero-right">
              {_badge_html}
            </div>
          </div>
          <div class="hero-art">{GOLD_ART_SVG}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Overview", "Compare Countries", "YoY Movers", "Download & Mapping"])

    with tabs[0]:
        kpi_slot = st.empty()


        freq_label = st.radio("Frequency", ["Yearly", "Quarterly", "Monthly"], horizontal=True, key="gp_freq")
        key = freq_label.lower()
        df = prices[key].copy()

        # Country/Currency picker (mapped country name + currency code)
        opts = (
            df[["mapped_country", "currency_code", "currency_name"]]
            .drop_duplicates()
            .sort_values(["mapped_country", "currency_code"])
            .reset_index(drop=True)
        )
        opts["label"] = opts["mapped_country"].fillna(opts["currency_code"]) + " (" + opts["currency_code"] + ")"

        default_pos = 0
        if "USD" in opts["currency_code"].values:
            default_pos = int(opts.index[opts["currency_code"] == "USD"][0])

        sel = st.selectbox("Country / Currency", opts["label"].tolist(), index=default_pos, key="gp_country")
        sel_code = opts.loc[opts["label"] == sel, "currency_code"].iloc[0]

        dfc = df[df["currency_code"] == sel_code].sort_values("date").copy()
        if dfc.empty:
            st.warning("No data available for the selected currency.")
            return

        # --- Period range filters (avoid showing raw dates in the UI) ---
        if freq_label == "Yearly":
            years = sorted(dfc["date"].dt.year.dropna().astype(int).unique().tolist())
            if not years:
                st.warning("No year values found in the data.")
                return
            y0, y1 = st.select_slider(
                "Year range",
                options=years,
                value=(years[0], years[-1]),
                key="gp_range_year",
            )
            dfc = dfc[(dfc["date"].dt.year >= y0) & (dfc["date"].dt.year <= y1)].copy()
        elif freq_label == "Quarterly":
            dfc["_per"] = dfc["date"].dt.to_period("Q")
            per_list = sorted(dfc["_per"].dropna().unique().tolist())
            labels = [str(p) for p in per_list]
            if not labels:
                st.warning("No quarterly values found in the data.")
                return
            p0_lbl, p1_lbl = st.select_slider(
                "Quarter range",
                options=labels,
                value=(labels[0], labels[-1]),
                key="gp_range_q",
            )
            p0, p1 = pd.Period(p0_lbl, freq="Q"), pd.Period(p1_lbl, freq="Q")
            dfc = dfc[(dfc["_per"] >= p0) & (dfc["_per"] <= p1)].copy()
        else:
            dfc["_per"] = dfc["date"].dt.to_period("M")
            per_list = sorted(dfc["_per"].dropna().unique().tolist())
            labels = [str(p) for p in per_list]
            if not labels:
                st.warning("No monthly values found in the data.")
                return
            p0_lbl, p1_lbl = st.select_slider(
                "Month range",
                options=labels,
                value=(labels[0], labels[-1]),
                key="gp_range_m",
            )
            p0, p1 = pd.Period(p0_lbl, freq="M"), pd.Period(p1_lbl, freq="M")
            dfc = dfc[(dfc["_per"] >= p0) & (dfc["_per"] <= p1)].copy()
        if dfc.empty:
            st.warning("No data in the selected range.")
            return

        latest = dfc.iloc[-1]
        latest_price = float(latest["price"])
        latest_yoy = float(latest["yoy_pct"]) if pd.notna(latest["yoy_pct"]) else None

        # KPI windows by frequency
        if freq_label == "Yearly":
            lag_5y, years_5y, vol_window = 5, 5, 5
        elif freq_label == "Quarterly":
            lag_5y, years_5y, vol_window = 20, 5, 8
        else:
            lag_5y, years_5y, vol_window = 60, 5, 12

        prev_5y = None
        if len(dfc) > lag_5y:
            prev_5y_val = dfc["price"].iloc[-(lag_5y + 1)]
            if pd.notna(prev_5y_val):
                prev_5y = float(prev_5y_val)

        cagr_5y = _calc_cagr(latest_price, prev_5y, years_5y)
        vol = (dfc["price"].pct_change().tail(vol_window).std() * 100) if len(dfc) > 3 else None
        peak = dfc["price"].tail(vol_window).max()
        low = dfc["price"].tail(vol_window).min()

        latest_dt = latest["date"]

        # Implied FX (local currency per 1 USD) using the USD gold price as the bridge
        usd_price = None
        try:
            usd_match = df[(df["currency_code"] == "USD") & (df["date"] == latest_dt)]["price"]
            if (not usd_match.empty) and pd.notna(usd_match.iloc[0]):
                usd_price = float(usd_match.iloc[0])
        except Exception:
            usd_price = None

        implied_fx = None
        if sel_code == "USD":
            implied_fx = 1.0
        elif usd_price is not None and usd_price != 0:
            implied_fx = latest_price / usd_price

        range_abs = (float(peak) - float(low)) if pd.notna(peak) and pd.notna(low) else None
        range_pct = ((float(peak) / float(low) - 1) * 100) if pd.notna(peak) and pd.notna(low) and float(low) != 0 else None


        with kpi_slot.container():
            # KPI cards
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                _kpi_card("🟡", "Latest avg price", f"{_fmt_num(latest_price, 2)} {sel_code}", f"As of {latest['period_label']}")
            with r1c2:
                _kpi_card("📈", "YoY change", f"{_fmt_num(latest_yoy, 2)}%", "vs same period last year")
            with r1c3:
                _kpi_card(
                    "⏳",
                    "5Y CAGR (annualized)",
                    f"{_fmt_num((cagr_5y * 100) if cagr_5y is not None else None, 2)}%",
                    "latest vs 5Y ago",
                )

            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1:
                _kpi_card("💱", "Implied FX", f"{_fmt_num(implied_fx, 4)} {sel_code}/USD", "via USD gold price")
            with r2c2:
                _kpi_card("🌪️", "Recent volatility", f"{_fmt_num(vol, 2)}%", f"Std dev over last {vol_window} periods")
            with r2c3:
                _kpi_card(
                    "📏",
                    "Recent range",
                    f"{_fmt_num(range_abs, 2)} {sel_code}",
                    f"{_fmt_num(range_pct, 2)}% peak–low over last {vol_window} periods",
                )

            tabs = st.tabs(["Overview", "Compare Countries", "YoY Movers", "Download & Mapping"])

            # --- Overview ---

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dfc["date"],
                y=dfc["price"],
                mode="lines",
                name=f"Price ({sel_code}/oz)",
                line=dict(color="#b8860b", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dfc["date"],
                y=dfc["yoy_pct"],
                mode="lines",
                name="YoY %",
                yaxis="y2",
                line=dict(color="#8b5a2b", width=2),
            )
        )

        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=40, b=10),
            template="plotly_white",
            yaxis=dict(title=f"Price ({sel_code} per oz)"),
            yaxis2=dict(title="YoY %", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        if show_labels:
            # Ensure markers + text are visible on both traces
            for tr in getattr(fig, "data", []) or []:
                mode = getattr(tr, "mode", "") or ""
                if "markers" not in mode:
                    tr.mode = (mode + "+markers") if mode else "lines+markers"
            _add_line_point_labels(fig, fmt="{:,.2f}")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Note: Prices are in local currency per troy ounce; cross-country differences reflect both gold price movements and FX."
        )

    # --- Compare Countries ---

    # --- Compare Countries ---
    with tabs[1]:
        snap_opt = (
            df[["date", "period_label"]]
            .dropna(subset=["date", "period_label"])
            .drop_duplicates()
            .sort_values("date")
            .reset_index(drop=True)
        )
        snap_labels = snap_opt["period_label"].astype(str).tolist()
        snap_lbl = st.selectbox("Snapshot period", snap_labels, index=len(snap_labels) - 1, key="gp_snap_lbl")
        snap = snap_opt.loc[snap_opt["period_label"].astype(str) == str(snap_lbl), "date"].iloc[-1]

        snap_df = df[df["date"] == snap].dropna(subset=["price"]).copy()

        # Safety: ensure one row per currency (prevents any accidental duplicates after mapping joins)
        snap_df = (
            snap_df.sort_values(["currency_code", "date"])
                  .drop_duplicates(subset=["currency_code"], keep="last")
        )

        snap_df["label"] = snap_df["mapped_country"].fillna(snap_df["currency_code"]) + " (" + snap_df["currency_code"] + ")"

        available_n = int(snap_df["currency_code"].nunique())
        if available_n == 0:
            st.info("No data available for the selected snapshot period.")
        else:
            min_n = 5 if available_n >= 5 else 1
            default_n = min(10, available_n)
            topn = st.slider("Top N", min_n, available_n, default_n, 1, key="gp_topn")

            top_df = snap_df.sort_values("price", ascending=False).head(topn).copy()
            top_df = top_df.reset_index(drop=True)
            top_df["rank"] = top_df.index + 1

            # Plot (exactly Top N)
            plot_df = top_df.sort_values("price", ascending=False).copy()
            fig2 = px.bar(
                plot_df,
                x="price",
                y="label",
                orientation="h",
                text="price" if show_labels else None,
            )
            fig2.update_traces(
                marker_color="#b8860b",
                texttemplate="%{text:,.0f}" if show_labels else None,
                textposition="outside" if show_labels else "none",
                cliponaxis=False,
            )
            fig2.update_layout(
                height=max(420, 34 * len(plot_df) + 220),
                margin=dict(l=10, r=10, t=30, b=10),
                template="plotly_white",
            )
            fig2.update_yaxes(title="", automargin=True, autorange="reversed")
            fig2.update_xaxes(title="Avg price (local currency per oz)")

            st.plotly_chart(fig2, use_container_width=True)

            # Table (exactly Top N)
            view_df = top_df[["rank", "mapped_country", "currency_code", "currency_name", "price", "yoy_pct"]].rename(
                columns={"price": "avg_price", "yoy_pct": "yoy_pct (%)"}
            )
            st.dataframe(view_df, use_container_width=True)
            st.caption(f"Showing top {len(top_df)} of {available_n} currencies for snapshot: {snap_lbl}.")

    # --- YoY Movers ---
    with tabs[2]:
        snap_opt2 = (
            df[["date", "period_label"]]
            .dropna(subset=["date", "period_label"])
            .drop_duplicates()
            .sort_values("date")
            .reset_index(drop=True)
        )
        snap_labels2 = snap_opt2["period_label"].astype(str).tolist()
        snap2_lbl = st.selectbox("Snapshot period (for movers)", snap_labels2, index=len(snap_labels2) - 1, key="gp_movers_snap_lbl")
        snap2 = snap_opt2.loc[snap_opt2["period_label"].astype(str) == str(snap2_lbl), "date"].iloc[-1]

        mov = df[df["date"] == snap2].dropna(subset=["yoy_pct"]).copy()
        mov["label"] = mov["mapped_country"].fillna(mov["currency_code"]) + " (" + mov["currency_code"] + ")"

        gain = mov.sort_values("yoy_pct", ascending=False).head(10)
        loss = mov.sort_values("yoy_pct", ascending=True).head(10)

        cA, cB = st.columns(2)
        with cA:
            st.markdown("### Top YoY Gainers")
            st.dataframe(
                gain[["label", "yoy_pct", "price"]].rename(
                    columns={"label": "country (currency)", "yoy_pct": "yoy %", "price": "avg price"}
                ),
                use_container_width=True,
            )
        with cB:
            st.markdown("### Top YoY Losers")
            st.dataframe(
                loss[["label", "yoy_pct", "price"]].rename(
                    columns={"label": "country (currency)", "yoy_pct": "yoy %", "price": "avg price"}
                ),
                use_container_width=True,
            )

    # --- Download & Mapping ---
    with tabs[3]:
        st.markdown("### Download: Gold price time series (long format)")
        dld = df.drop(columns=["country_name_sheet"], errors="ignore").copy()
        st.dataframe(dld.head(200), use_container_width=True, height=240)
        st.download_button(
            "⬇️ Download price data (CSV)",
            data=dld.to_csv(index=False).encode("utf-8"),
            file_name=f"gold_prices_{key}.csv",
            mime="text/csv",
            key="gp_dl_data",
        )

        st.markdown("### Currency ↔ Country mapping")
        st.dataframe(prices["map"], use_container_width=True)
        st.download_button(
            "⬇️ Download mapping (CSV)",
            data=prices["map"].to_csv(index=False).encode("utf-8"),
            file_name="currency_country_map.csv",
            mime="text/csv",
            key="gp_dl_map",
        )


# =========================
# Sidebar
# =========================
st.sidebar.markdown('<div class="sidebar-title">GOLD • HS 7108</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-sub">Production + ITC Trade (2005–2024)</div>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="badge">Professional UI</span> <span class="badge">Year-wise</span>', unsafe_allow_html=True)
st.sidebar.markdown("<br/>", unsafe_allow_html=True)

_jew_ok = resolve_file(JEWELLERY_FILE).exists()
nav_items = ["Production", "Gold Prices"] + [p[0] for p in HS6_PAGES if (_jew_ok or p[1] not in JEWELLERY_CODES)]
page = st.sidebar.radio("Navigation", nav_items, index=0, key="nav_main")

st.sidebar.markdown("<hr class='soft'/>", unsafe_allow_html=True)
prod_unit = st.sidebar.radio("Production unit (scaling only)", ["Tonnes (t)", "Kilo-tonnes (kt)"], index=0, key="prod_unit")

st.sidebar.markdown("<hr class='soft'/>", unsafe_allow_html=True)
trade_unit = st.sidebar.radio(
    "Trade value display unit (base: USD thousand)",
    ["USD Bn", "USD Mn", "USD (Absolute)"],
    index=0,
    key="trade_unit",
)

show_labels = st.sidebar.checkbox("Show data labels on charts", value=False, key="show_labels")

st.sidebar.markdown("<div class='small-note'>Tip: Place files in the working folder or /content.</div>", unsafe_allow_html=True)

# =========================
# Data load (shared)
# =========================
PROD_PATH = resolve_file(PROD_FILE)
TRADE_PATH = resolve_file(TRADE_FILE)

if not PROD_PATH.exists() or not TRADE_PATH.exists():
    st.error(
        "Missing files. Please ensure these files are present in the same folder (or /content): "
        f"'{PROD_FILE}' and '{TRADE_FILE}'."
    )
    st.stop()

prod_long = load_production_long(str(PROD_PATH))
trade_imp_total, trade_exp_total = load_trade_total(str(TRADE_PATH))

# =========================
# Production page (kept stable)
# =========================
def show_production():
    years = sorted(prod_long["year"].unique())
    miny, maxy = min(years), max(years)

    unit_label = "t" if prod_unit.startswith("Tonnes") else "kt"
    scale = 1.0 if unit_label == "t" else 1 / 1000.0

    st.markdown(
        f"""
        <div class="header-wrap hero">
          <div class="hero-row">
            <div class="hero-left">
              <div class="hero-icon">{GOLD_ICON_SVG}</div>
              <div>
                <div class="h1">Gold Production</div>
                <div class="hsub">Gold mine production ({unit_label}) • overview, regions & country insights• Source: World Gold Council</div>
              </div>
            </div>
            <div class="hero-right">
              <div class="badge">{miny}–{maxy}</div>
            </div>
          </div>
          <div class="hero-art">{GOLD_ART_SVG}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Overview", "Regions", "Countries", "Download"])

    with tabs[0]:
        c1, c2 = st.columns([1.2, 2.0])
        with c1:
            sel_year = st.selectbox("Select year (drives KPIs & rankings)", years, index=len(years) - 1, key="prod_year")
        with c2:
            st.markdown(f"<div class='small-note'><b>Unit:</b> {unit_label} &nbsp;&nbsp;•&nbsp;&nbsp; Tip: Use tabs for different views.</div>", unsafe_allow_html=True)

        dfy = prod_long.copy()
        is_global = dfy["country"].str.contains("Global Total", case=False, na=False)
        global_series = (
            dfy[is_global]
            .groupby("year", as_index=False)["tonnes"]
            .sum()
            .sort_values("year")
        )
        if global_series.empty:
            global_series = dfy.groupby("year", as_index=False)["tonnes"].sum().sort_values("year")

        latest = dfy[dfy["year"] == sel_year].copy()
        latest["tonnes_scaled"] = latest["tonnes"] * scale

        mask_excl = latest["country"].str.contains(r"Sub-?total|Global Total|Other", case=False, na=False)
        latest_c = latest[~mask_excl & latest["tonnes"].notna()].copy()
        top = latest_c.sort_values("tonnes", ascending=False).head(1)
        top_name = top["country"].iloc[0] if len(top) else "—"
        top_val = top["tonnes_scaled"].iloc[0] if len(top) else np.nan
        global_total = float(global_series.loc[global_series["year"] == sel_year, "tonnes"].sum()) * scale

        s_global = global_series.set_index("year")["tonnes"]
        global_yoy = _yoy(s_global, sel_year)

        k1, k2, k3, k4 = st.columns([1.2, 1, 1, 1.2])
        with k1:
            _kpi_card("🏆", f"Top Producer ({sel_year})", f"{top_name}", sub="")
        with k2:
            _kpi_card("⛏️", f"Top Output ({sel_year})", f"{_fmt_num(top_val, 1)} {unit_label}", sub="")
        with k3:
            _kpi_card("🔁", f"Global YoY ({sel_year})", f"{_fmt_pct(global_yoy)}", sub="vs previous year")
        with k4:
            _kpi_card("📈", f"Global Total ({sel_year})", f"{_fmt_num(global_total, 1)} {unit_label}", sub="")

        g = global_series.copy()
        g["value"] = g["tonnes"] * scale
        fig = px.line(g, x="year", y="value", markers=True, title=f"Global Total Production ({unit_label})")
        fig.update_traces(line=dict(color="#B8860B", width=3))
        fig.add_vline(x=sel_year, line_dash="dot", line_width=2, line_color="rgba(15,23,42,.40)")
        fig.update_layout(template="plotly_white", height=360, margin=dict(l=10, r=10, t=60, b=10))
        fig.update_yaxes(title=unit_label)
        if show_labels:
            _add_line_point_labels(fig, fmt="{:,.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        sel_year = st.selectbox("Select year", years, index=len(years) - 1, key="prod_regions_year")
        df = prod_long.copy()
        df = df[~df["country"].str.contains(r"Sub-?total|Global Total", case=False, na=False)]
        reg_year = df.groupby(["region", "year"], as_index=False)["tonnes"].sum()
        reg_year["value"] = reg_year["tonnes"] * scale

        st.markdown("<div class='small-note'>Region trend is always year-wise. The selected year only marks the reference line.</div>", unsafe_allow_html=True)
        fig = px.line(reg_year, x="year", y="value", color="region", markers=True, title="Region trend (year-wise)")
        fig.add_vline(x=sel_year, line_dash="dot", line_width=2, line_color="rgba(15,23,42,.35)")
        fig.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=10, t=60, b=10), legend_title_text="")
        fig.update_yaxes(title=unit_label)
        if show_labels:
            _add_line_point_labels(fig, fmt="{:,.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        sel_year = st.selectbox("Select year (for ranking)", years, index=len(years) - 1, key="prod_countries_year")
        n = st.slider("Top N producers (selected year)", 5, 30, 10, key="prod_countries_topn")
        df = prod_long.copy()
        df = df[~df["country"].str.contains(r"Sub-?total|Global Total|Other", case=False, na=False)]
        dfy = df[df["year"] == sel_year].copy()
        dfy["value"] = dfy["tonnes"] * scale
        totals = dfy.groupby("country", as_index=False)["value"].sum().sort_values("value", ascending=False)
        topc_desc = totals.head(n).copy()
        others_val = float(totals["value"].sum() - topc_desc["value"].sum())

        # Plot data: Top N + Others (Others = sum of all remaining countries)
        plot_df = topc_desc.copy()
        if others_val > 0:
            plot_df = pd.concat(
                [plot_df, pd.DataFrame([{"country": "Others", "value": others_val}])],
                ignore_index=True,
            )

        plot_df_plot = plot_df.sort_values("value", ascending=True)

        fig1 = px.bar(plot_df_plot, x="value", y="country", orientation="h", title=f"Top Producers • {sel_year}")
        fig1.update_traces(marker_color="#B8860B")
        fig1.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=10, t=60, b=10))
        fig1.update_xaxes(title=f"{unit_label}")
        fig1.update_yaxes(title="")
        if show_labels:
            _add_bar_labels(fig1, orientation="h", fmt="{:,.1f}")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Data table + download (Top N + Others) ---
        st.markdown("### Data (Top N + Others)")
        tbl = topc_desc.copy()
        if others_val > 0:
            tbl = pd.concat(
                [tbl, pd.DataFrame([{"country": "Others", "value": others_val}])],
                ignore_index=True,
            )
        tbl = tbl.rename(columns={"value": f"value ({unit_label})"})
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        csv = tbl.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download (Top N + Others) CSV",
            data=csv,
            file_name=f"gold_top_producers_{sel_year}_top{n}.csv",
            mime="text/csv",
        )

        country = st.selectbox("Select country", sorted(df["country"].unique()), index=0, key="prod_country_pick")
        cser = df[df["country"] == country].groupby("year", as_index=False)["tonnes"].sum()
        cser["value"] = cser["tonnes"] * scale

        fig2 = px.line(cser, x="year", y="value", markers=True, title="Country Trend (year-wise)")
        fig2.update_traces(line=dict(color="#8B5A2B", width=3))
        fig2.update_layout(template="plotly_white", height=360, margin=dict(l=10, r=10, t=60, b=10))
        fig2.update_yaxes(title=unit_label)
        if show_labels:
            _add_line_point_labels(fig2, fmt="{:,.1f}")
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[3]:
        # Download with year range filter
        out = prod_long.copy()
        out["tonnes_scaled"] = out["tonnes"] * scale

        prod_years = sorted(out["year"].dropna().unique().tolist())
        if prod_years:
            d1, d2 = st.columns(2)
            with d1:
                start_year = st.selectbox("Start year", prod_years, index=0, key="prod_dl_start_year")
            with d2:
                end_year = st.selectbox("End year", prod_years, index=len(prod_years) - 1, key="prod_dl_end_year")

            if start_year > end_year:
                start_year, end_year = end_year, start_year

            out_f = out[(out["year"] >= start_year) & (out["year"] <= end_year)].copy()
            st.caption(f"Download range: {start_year}–{end_year} • Rows: {len(out_f):,}")
        else:
            out_f = out.copy()

        # --- Download table: remove tonnes_scaled, add kilotonnes + YoY growth ---
        out_dl = out_f.copy()
        if "tonnes" in out_dl.columns:
            out_dl["kilotonnes"] = out_dl["tonnes"] / 1000.0
            out_dl = out_dl.sort_values(["region", "country", "year"])
            out_dl["yoy_growth_pct"] = (
                out_dl.groupby(["region", "country"])["tonnes"]
                .pct_change()
                .multiply(100.0)
            )

        # Keep a clean, download-friendly schema
        cols = [c for c in ["region", "country", "year", "tonnes", "kilotonnes", "yoy_growth_pct"] if c in out_dl.columns]
        out_dl = out_dl[cols]

        st.dataframe(out_dl.head(200), use_container_width=True, height=320)
        csv = out_dl.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download production (long) CSV",
            data=csv,
            file_name="gold_production_long.csv",
            mime="text/csv",
        )

# =========================
# Trade page renderer (KPI cards restored)
# =========================
def _get_years_from_trade(df_wide: pd.DataFrame) -> list[int]:
    years = [c for c in df_wide.columns if isinstance(c, int)]
    return sorted(years)

def _world_series(df_wide: pd.DataFrame) -> pd.Series:
    years = _get_years_from_trade(df_wide)
    s = df_wide.loc[df_wide["partner"].str.lower() == "world", years]
    if s.empty:
        return pd.Series(index=years, dtype=float)
    return s.iloc[0]

def show_trade(title: str, imp_wide: pd.DataFrame, exp_wide: pd.DataFrame, page_key: str):
    years = _get_years_from_trade(exp_wide)
    miny, maxy = min(years), max(years)

    st.markdown(
        f"""
        <div class="header-wrap hero">
          <div class="hero-row">
            <div class="hero-left">
              <div class="hero-icon">{GOLD_ICON_SVG}</div>
              <div>
                <div class="h1">{title}</div>
                <div class="hsub">ITC Trade Map • values ({trade_unit}) • base data: USD thousand</div>
              </div>
            </div>
            <div class="hero-right">
              <div class="badge">{miny}–{maxy}</div>
            </div>
          </div>
          <div class="hero-art">{GOLD_ART_SVG}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.6, 1.0])
    with c1:
        snap_year = st.selectbox("Snapshot year", years, index=len(years) - 1, key=f"{page_key}_year")
    with c2:
        partner_mode = st.selectbox("Partner ranking based on", ["Exports", "Imports"], index=0, key=f"{page_key}_mode")
    with c3:
        top_n = st.slider("Top N countries", 5, 30, 10, key=f"{page_key}_topn")
    with c4:
        metric = st.radio("Metric", ["Value", "Share of World (%)"], index=0, key=f"{page_key}_metric")


    # Re-usable context line shown above each section/tab so users don't lose track after scrolling
    ctx = (
        f"<div class='small-note'>"
        f"<b>Snapshot year:</b> {snap_year} &nbsp; • &nbsp; "
        f"<b>Partner ranking:</b> {partner_mode} &nbsp; • &nbsp; "
        f"<b>Top N:</b> {top_n} &nbsp; • &nbsp; "
        f"<b>Display unit:</b> {_trade_unit_label(trade_unit)} (base: USD thousand)"
        f"</div>"
    )

    world_exp = _world_series(exp_wide)
    world_imp = _world_series(imp_wide)

    exp_val = float(world_exp.get(snap_year, np.nan))
    imp_val = float(world_imp.get(snap_year, np.nan))
    bal_val = exp_val - imp_val if not (np.isnan(exp_val) or np.isnan(imp_val)) else np.nan

    exp_disp, exp_unit_lbl = _scale_trade_thousand(exp_val, trade_unit)
    exp_unit_lbl = exp_unit_lbl or _trade_unit_label(trade_unit)
    imp_disp, _ = _scale_trade_thousand(imp_val, trade_unit)
    bal_disp, _ = _scale_trade_thousand(bal_val, trade_unit)

    exp_yoy = _yoy(world_exp, snap_year)
    imp_yoy = _yoy(world_imp, snap_year)
    exp_cagr = _cagr(world_exp, years[0], snap_year)
    imp_cagr = _cagr(world_imp, years[0], snap_year)

    df_rank_src = exp_wide if partner_mode == "Exports" else imp_wide
    rank = df_rank_src[["partner", snap_year]].copy().rename(columns={snap_year: "value_thousand"})
    rank["value_thousand"] = pd.to_numeric(rank["value_thousand"], errors="coerce")
    rank = rank[rank["partner"].str.lower() != "world"].dropna(subset=["value_thousand"]).sort_values("value_thousand", ascending=False)

    top_partner = rank["partner"].iloc[0] if len(rank) else "—"
    top_partner_val = float(rank["value_thousand"].iloc[0]) if len(rank) else np.nan
    top_partner_disp, _ = _scale_trade_thousand(top_partner_val, trade_unit)

    # Trade pages (Total + HS6) are easiest to consume with consistent subtabs
    tabs = st.tabs(["Overview", "Countries", "Country trend", "Download"])

    # ----- Overview -----
    with tabs[0]:
        st.markdown(f"## Overview • {snap_year}")
        st.markdown(ctx, unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns([1, 1, 1, 1, 1])
        with k1:
            _kpi_card("📤", f"Exports ({snap_year})", f"{_fmt_num(exp_disp, 2)} {exp_unit_lbl}", sub=f"YoY: {_fmt_pct(exp_yoy)}")
        with k2:
            _kpi_card("📥", f"Imports ({snap_year})", f"{_fmt_num(imp_disp, 2)} {exp_unit_lbl}", sub=f"YoY: {_fmt_pct(imp_yoy)}")
        with k3:
            _kpi_card(
                "⚖️",
                f"Trade Balance ({snap_year})",
                f"{_fmt_num(bal_disp, 2)} {exp_unit_lbl}",
                sub=("Surplus" if bal_val > 0 else "Deficit" if bal_val < 0 else ""),
            )
        with k4:
            _kpi_card("📈", f"CAGR Exports ({years[0]}–{snap_year})", f"{_fmt_pct(exp_cagr * 100)}", sub="")
        with k5:
            _kpi_card("📉", f"CAGR Imports ({years[0]}–{snap_year})", f"{_fmt_pct(imp_cagr * 100)}", sub="")

        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

        st.markdown(f"### Global trade trend • {years[0]}–{maxy}")
        df_world = pd.DataFrame({
            "year": years,
            "Exports_th": [world_exp.get(y, np.nan) for y in years],
            "Imports_th": [world_imp.get(y, np.nan) for y in years],
        })
        df_world["Exports"], _ = zip(*df_world["Exports_th"].apply(lambda v: _scale_trade_thousand(v, trade_unit)))
        df_world["Imports"], _ = zip(*df_world["Imports_th"].apply(lambda v: _scale_trade_thousand(v, trade_unit)))
        df_world["Balance"] = df_world["Exports"] - df_world["Imports"]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_world["year"],
                y=df_world["Exports"],
                mode="lines+markers",
                name="Exports",
                line=dict(color="#B8860B", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_world["year"],
                y=df_world["Imports"],
                mode="lines+markers",
                name="Imports",
                line=dict(color="#8B5A2B", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_world["year"],
                y=df_world["Balance"],
                mode="lines",
                name="Trade Balance",
                line=dict(color="rgba(15,23,42,.55)", width=2, dash="dot"),
                yaxis="y2",
            )
        )
        fig.add_vline(x=snap_year, line_dash="dot", line_width=2, line_color="rgba(15,23,42,.35)")
        fig.update_layout(
            template="plotly_white",
            height=420,
            margin=dict(l=10, r=10, t=60, b=10),
            title=f"Global trade trend ({exp_unit_lbl})",
            legend_title_text="",
            yaxis=dict(title=exp_unit_lbl),
            yaxis2=dict(title="Balance", overlaying="y", side="right", showgrid=False),
        )
        if show_labels:
            _add_line_point_labels(fig, fmt="{:,.2f}")
        st.plotly_chart(fig, use_container_width=True)

    # ----- Partners -----
    with tabs[1]:
        # Big, explicit header so users don't need to scroll up to remember what they're viewing
        st.markdown(f"## Countries • {partner_mode} • {snap_year}")
        st.markdown(ctx, unsafe_allow_html=True)

        # World total (base: USD thousand) for share computations
        world_total_th = exp_val if partner_mode == "Exports" else imp_val
        # Fallback: if World is missing/zero for a year, use sum of partner rows (ex-World)
        if (
            world_total_th is None
            or (isinstance(world_total_th, float) and np.isnan(world_total_th))
            or world_total_th == 0
        ):
            world_total_th = float(rank["value_thousand"].sum())

        rank_top = rank.head(top_n).copy()
        top_sum_th = float(rank_top["value_thousand"].sum())
        # Others must represent ALL remaining countries + any unallocated gap so that Total matches World
        others_th = float(max(0.0, float(world_total_th) - top_sum_th))

        # Build plot data: Top N + Others
        plot_df = rank_top[["partner", "value_thousand"]].copy()
        if others_th > 0:
            plot_df = pd.concat(
                [plot_df, pd.DataFrame([{"partner": "Others", "value_thousand": others_th}])],
                ignore_index=True,
            )

        # Always compute BOTH: value (scaled) and share (%)
        plot_df["value"], _ = zip(*plot_df["value_thousand"].apply(lambda v: _scale_trade_thousand(v, trade_unit)))
        if world_total_th is None or (isinstance(world_total_th, float) and np.isnan(world_total_th)) or world_total_th == 0:
            plot_df["share_pct"] = np.nan
        else:
            plot_df["share_pct"] = (plot_df["value_thousand"] / float(world_total_th)) * 100.0

        x_col = "value" if metric == "Value" else "share_pct"
        x_title = exp_unit_lbl if metric == "Value" else "Share of World (%)"
        lbl_fmt = "{:,.2f}" if metric == "Value" else "{:,.2f}%"

        plot_df_plot = plot_df.sort_values(x_col, ascending=True)

        fig2 = px.bar(plot_df_plot, x=x_col, y="partner", orientation="h", title=f"Top {top_n} countries + Others")
        fig2.update_traces(marker_color="#B8860B" if partner_mode == "Exports" else "#8B5A2B")
        fig2.update_layout(template="plotly_white", height=520, margin=dict(l=10, r=10, t=60, b=10))
        fig2.update_xaxes(title=x_title)
        fig2.update_yaxes(title="")
        if show_labels:
            _add_bar_labels(fig2, orientation="h", fmt=lbl_fmt)
        st.plotly_chart(fig2, use_container_width=True)        # --- Data section: Top N + Others (includes any unallocated gap so Total matches World) ---
        st.markdown("### Data (Top N + Others)")

        value_col = f"value ({exp_unit_lbl})"
        tbl = plot_df.copy()
        tbl = tbl[["partner", "value", "share_pct"]].rename(
            columns={
                "value": value_col,
                "share_pct": "share_of_world_pct",
            }
        )

        # Add Total row (World) below Others so the snapshot always ties out
        total_val, _ = _scale_trade_thousand(world_total_th, trade_unit)
        total_row = pd.DataFrame(
            [
                {
                    "partner": "Total",
                    value_col: total_val,
                    "share_of_world_pct": 100.0 if (world_total_th is not None and not (isinstance(world_total_th, float) and np.isnan(world_total_th)) and world_total_th != 0) else np.nan,
                }
            ]
        )
        tbl = pd.concat([tbl, total_row], ignore_index=True)

        # Clean display (remove extra decimals) + bold Total row
        tbl_disp = tbl.copy()
        for _c in [value_col, "share_of_world_pct"]:
            if _c in tbl_disp.columns:
                tbl_disp[_c] = pd.to_numeric(tbl_disp[_c], errors="coerce").round(2)

        def _bold_total_row(row):
            is_total = str(row.get("partner", "")).strip().lower() == "total"
            return ["font-weight: 800" if is_total else ""] * len(row)

        try:
            sty = (
                tbl_disp.style
                .apply(_bold_total_row, axis=1)
                .format({value_col: "{:,.2f}", "share_of_world_pct": "{:,.2f}"})
            )
            # Hide index when supported
            if hasattr(sty, "hide"):
                sty = sty.hide(axis="index")
            st.dataframe(sty, use_container_width=True)
        except Exception:
            st.dataframe(tbl_disp, use_container_width=True, hide_index=True)

        csv = tbl_disp.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download (Top N + Others) CSV",
            data=csv,
            file_name=f"{page_key}_countries_{partner_mode.lower()}_{snap_year}_top{top_n}.csv",
            mime="text/csv",
        )
    # ----- Country trend -----
    with tabs[2]:
        st.markdown(f"## Country trend • {partner_mode} • {snap_year}")
        st.markdown(ctx, unsafe_allow_html=True)

        default_partner = top_partner if top_partner != "—" else (rank["partner"].iloc[0] if len(rank) else "World")
        partner_opts = rank["partner"].head(50).tolist()
        partner_idx = partner_opts.index(default_partner) if default_partner in partner_opts else 0
        partner = st.selectbox("Select country", partner_opts, index=partner_idx, key=f"{page_key}_partner")

        df_src = exp_wide if partner_mode == "Exports" else imp_wide
        partner_row = df_src[df_src["partner"].str.lower() == str(partner).lower()]
        if partner_row.empty:
            st.info("No data available for the selected country.")
        else:
            s = partner_row.iloc[0][years]
            df_tr = pd.DataFrame({"year": years, "value_th": pd.to_numeric(s.values, errors="coerce")})
            df_tr["value"], _ = zip(*df_tr["value_th"].apply(lambda v: _scale_trade_thousand(v, trade_unit)))

            # Share of World (%) uses world totals (base: USD thousand) by year
            world_series = world_exp if partner_mode == "Exports" else world_imp
            df_tr["world_th"] = [world_series.get(y, np.nan) for y in years]
            df_tr["share_pct"] = np.where(
                (df_tr["world_th"].notna()) & (df_tr["world_th"] != 0),
                (df_tr["value_th"] / df_tr["world_th"]) * 100.0,
                np.nan,
            )

            y_col = "value" if metric == "Value" else "share_pct"
            y_title = exp_unit_lbl if metric == "Value" else "Share of World (%)"
            lbl_fmt = "{:,.2f}" if metric == "Value" else "{:,.2f}%"

            fig3 = px.line(df_tr, x="year", y=y_col, markers=True, title=f"Country trend • {partner_mode}: {partner}")
            fig3.update_traces(line=dict(color="#B8860B" if partner_mode == "Exports" else "#8B5A2B", width=3))
            fig3.update_layout(template="plotly_white", height=380, margin=dict(l=10, r=10, t=60, b=10))
            fig3.update_yaxes(title=y_title)
            if show_labels:
                _add_line_point_labels(fig3, fmt=lbl_fmt)
            st.plotly_chart(fig3, use_container_width=True)


    # ----- Download -----
    with tabs[3]:
        st.markdown("## Download")
        st.markdown(ctx, unsafe_allow_html=True)

        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
        st.markdown("### Download (year range)")

        d1, d2 = st.columns(2)
        with d1:
            dl_start_year = st.selectbox("Start year", years, index=0, key=f"{page_key}_dl_start_year")
        with d2:
            dl_end_year = st.selectbox("End year", years, index=len(years) - 1, key=f"{page_key}_dl_end_year")

        if dl_start_year > dl_end_year:
            dl_start_year, dl_end_year = dl_end_year, dl_start_year

        sel_years = [y for y in years if dl_start_year <= y <= dl_end_year]

        # --- Wide -> Long (Exports + Imports) ---
        exp_long = exp_wide[["partner"] + sel_years].melt(
            id_vars="partner", var_name="year", value_name="exports_thousand"
        )
        imp_long = imp_wide[["partner"] + sel_years].melt(
            id_vars="partner", var_name="year", value_name="imports_thousand"
        )

        dl = exp_long.merge(imp_long, on=["partner", "year"], how="outer")
        dl["year"] = dl["year"].astype(int)

        dl["exports_thousand"] = pd.to_numeric(dl["exports_thousand"], errors="coerce")
        dl["imports_thousand"] = pd.to_numeric(dl["imports_thousand"], errors="coerce")
        dl["balance_thousand"] = dl["exports_thousand"] - dl["imports_thousand"]

        # --- YoY growth (%) by partner ---
        dl = dl.sort_values(["partner", "year"])
        dl["yoy_exports_pct"] = dl.groupby("partner")["exports_thousand"].pct_change() * 100.0
        dl["yoy_imports_pct"] = dl.groupby("partner")["imports_thousand"].pct_change() * 100.0

        # --- Scale to display unit (base is USD thousand) ---
        def _scaled_val(v):
            return _scale_trade_thousand(v, trade_unit)[0]

        dl["exports"] = dl["exports_thousand"].apply(_scaled_val)
        dl["imports"] = dl["imports_thousand"].apply(_scaled_val)
        dl["balance"] = dl["balance_thousand"].apply(_scaled_val)

        unit_lbl = _trade_unit_label(trade_unit)

        # --- Required columns only ---
        out_cols = [
            "partner", "year",
            "exports", "imports", "balance",
            "yoy_exports_pct", "yoy_imports_pct",
        ]
        dl_out = dl[out_cols].copy()

        st.caption(
            f"Download range: {dl_start_year}–{dl_end_year} • Rows: {len(dl_out):,} • "
            f"Unit: {unit_lbl} (base: USD thousand)"
        )
        st.dataframe(dl_out.head(500), use_container_width=True, height=420)

        csv = dl_out.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download trade (Exports+Imports+Balance + YoY) CSV",
            data=csv,
            file_name=f"{page_key}_trade_{dl_start_year}_{dl_end_year}.csv",
            mime="text/csv",
        )

# =========================
# Routing
# =========================
if page == "Production":
    show_production()
elif page == "Gold Prices":
    show_gold_prices()
else:
    if page == "Trade — 7108 (Total)":
        show_trade("Trade — 7108 (Total)", trade_imp_total, trade_exp_total, page_key="trade_total")
    else:
        sheet_code = None
        for label, code in HS6_PAGES:
            if label == page:
                sheet_code = code
                break
        if sheet_code is None:
            st.error("Unknown page.")
        else:
            trade_path_use = TRADE_PATH
            if sheet_code in JEWELLERY_CODES:
                trade_path_use = resolve_file(JEWELLERY_FILE)
            if not trade_path_use.exists():
                st.error(f"Missing data file for {sheet_code}: {trade_path_use.name}. Place it in the working folder or /content.")
            else:
                imp_w, exp_w = load_trade_hs6(str(trade_path_use), sheet_code)
                show_trade(f"Trade — {sheet_code}", imp_w, exp_w, page_key=f"trade_{sheet_code}")
