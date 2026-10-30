from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "Breast_Cancer.csv"

COLUMN_ALIASES = {
    "age": "age",
    "race": "race",
    "marital_status": "marital_status",
    "t_stage": "t_stage",
    "n_stage": "n_stage",
    "6th_stage": "sixth_stage",
    "sixth_stage": "sixth_stage",
    "differentiate": "differentiate",
    "differentiation": "differentiate",
    "grade": "grade",
    "a_stage": "a_stage",
    "tumor_size": "tumor_size",
    "estrogen_status": "estrogen_status",
    "progesterone_status": "progesterone_status",
    "regional_node_examined": "regional_node_examined",
    "reginol_node_positive": "regional_node_positive",
    "regional_node_positive": "regional_node_positive",
    "survival_months": "survival_months",
    "status": "status",
}

REQUIRED_COLUMNS = [
    "age",
    "race",
    "marital_status",
    "t_stage",
    "n_stage",
    "sixth_stage",
    "differentiate",
    "grade",
    "a_stage",
    "tumor_size",
    "estrogen_status",
    "progesterone_status",
    "regional_node_examined",
    "regional_node_positive",
    "survival_months",
    "status",
]

NUMERIC_COLUMNS = [
    "age",
    "tumor_size",
    "regional_node_examined",
    "regional_node_positive",
    "survival_months",
]
SOURCE_COLUMN_NAMES = {
    "age": "Age",
    "race": "Race",
    "marital_status": "Marital Status",
    "t_stage": "T Stage",
    "n_stage": "N Stage",
    "sixth_stage": "6th Stage",
    "differentiate": "differentiate",
    "grade": "Grade",
    "a_stage": "A Stage",
    "tumor_size": "Tumor Size",
    "estrogen_status": "Estrogen Status",
    "progesterone_status": "Progesterone Status",
    "regional_node_examined": "Regional Node Examined",
    "regional_node_positive": "Reginol Node Positive",
    "survival_months": "Survival Months",
    "status": "Status",
}
STAGE_ORDER = ["IA", "IB", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IV"]
STATUS_COLORS = {"Alive": "#168b78", "Dead": "#d95878"}
PALETTE = ["#d95878", "#168b78", "#6174c8", "#e5a24c", "#7562a8", "#4aa6b8"]


st.set_page_config(
    page_title="Breast Cancer Cohort Explorer",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --ink: #172d42; --muted: #68798b; --pink: #c94f70; --teal: #168b78; }
      html, body, [class*="css"] { font-family: Inter, 'Segoe UI', sans-serif; }
      [data-testid="stAppViewContainer"] { background: #f4f7fa; }
      [data-testid="stHeader"] { background: rgba(244,247,250,.86); }
      [data-testid="stSidebar"] { background: #fbfcfd; border-right: 1px solid #e5ebf0; }
      [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
      .block-container { max-width: 1480px; padding: 1.7rem 2.4rem 3.2rem; }
      h1, h2, h3 { color: var(--ink); font-family: Inter, 'Segoe UI', sans-serif; letter-spacing: -.035em; }
      h1 { font-weight: 800; }
      p, li { color: #526579; }
      [data-testid="stMetric"] { background: #fff; border: 1px solid #e7edf2; border-radius: 16px; padding: 1rem 1.1rem; box-shadow: 0 4px 16px rgba(25,48,69,.035); }
      [data-testid="stMetricLabel"] { color: #718194; font-size: .82rem; font-weight: 600; }
      [data-testid="stMetricValue"] { color: #183149; font-family: Inter, 'Segoe UI', sans-serif; font-size: 1.8rem; font-weight: 800; }
      div[data-testid="stTabs"] button { font-weight: 600; }
      div[data-testid="stTabs"] button[aria-selected="true"] { color: #bf4668; }
      .hero { background: linear-gradient(118deg, #19374d 0%, #24465d 57%, #365064 100%); border-radius: 22px; padding: 1.65rem 2rem; color: #fff; margin: .25rem 0 1.3rem; box-shadow: 0 12px 32px rgba(28,55,76,.15); position: relative; overflow: hidden; }
      .hero:after { content: '✳'; position: absolute; right: 2rem; top: -.7rem; font-size: 8rem; line-height: 1; color: rgba(255,255,255,.07); }
      .hero-kicker { color: #f1a8ba; text-transform: uppercase; font-size: .73rem; letter-spacing: .16em; font-weight: 700; margin: 0 0 .4rem; }
      .hero h1 { color: #fff; font-size: clamp(1.7rem, 3vw, 2.35rem); margin: 0; }
      .hero p { color: #d9e4ec; margin: .45rem 0 0; max-width: 850px; font-size: .96rem; }
      .section-label { color: #c84e70; font-size: .72rem; text-transform: uppercase; letter-spacing: .14em; font-weight: 700; margin-bottom: .15rem; }
      .insight { background: #fff; border-left: 4px solid #d95878; border-radius: 11px; padding: .85rem 1rem; color: #43566a; box-shadow: 0 3px 12px rgba(25,48,69,.035); margin: .45rem 0 1rem; }
      .muted-note { color: #778798; font-size: .82rem; }
      .source-line { color: #778798; font-size: .78rem; border-top: 1px solid #e5ebf0; padding-top: 1rem; margin-top: 2rem; }
      .stDownloadButton button { border-radius: 9px; font-weight: 600; }
      @media (max-width: 800px) { .block-container { padding: 1rem 1rem 2.5rem; } .hero { padding: 1.35rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_default_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def standardize_data(raw: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for column in raw.columns:
        key = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
        if key in COLUMN_ALIASES:
            rename[column] = COLUMN_ALIASES[key]
    df = raw.rename(columns=rename).copy()
    # Some published copies combine differentiation and grade in one field.
    # Split that label so the app presents the same two fields as the notebook.
    if "differentiate" not in df.columns and "grade" in df.columns:
        grade_text = df["grade"].astype("string").str.strip()
        df["differentiate"] = grade_text.str.extract(
            r"(Poorly differentiated|Moderately differentiated|Well differentiated|Undifferentiated)",
            flags=re.IGNORECASE,
            expand=False,
        )
    if "grade" in df.columns:
        grade_text = df["grade"].astype("string").str.strip()
        roman_grade = grade_text.str.extract(r"Grade\s*(IV|III|II|I)\b", flags=re.IGNORECASE, expand=False)
        roman_map = {"I": "1", "II": "2", "III": "3", "IV": "4"}
        parsed_roman = roman_grade.str.upper().map(roman_map)
        parsed_numeric = grade_text.str.extract(r"\b([1-4])\b", expand=False)
        df["grade"] = parsed_roman.fillna(parsed_numeric).fillna(grade_text)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    for column in REQUIRED_COLUMNS:
        if column not in NUMERIC_COLUMNS:
            df[column] = df[column].astype("string").str.strip()
    df["status"] = df["status"].str.title()
    df["sixth_stage"] = df["sixth_stage"].str.upper()
    return df


def display_label(column: str) -> str:
    labels = {
        "sixth_stage": "6th stage",
        "a_stage": "Summary stage",
        "differentiate": "Differentiation",
        "regional_node_positive": "Positive regional nodes",
        "regional_node_examined": "Regional nodes examined",
        "node_positive_share": "Positive nodes / examined",
        "survival_months": "Observed months",
        "tumor_size": "Tumor size (dataset units)",
        "estrogen_status": "Estrogen receptor",
        "progesterone_status": "Progesterone receptor",
        "marital_status": "Marital status",
        "t_stage": "T stage",
        "n_stage": "N stage",
    }
    return labels.get(column, column.replace("_", " ").title())


def make_chart(fig, height: int = 360):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=16, r=16, t=28, b=16),
        font=dict(family="Inter, Segoe UI, sans-serif", color="#40566b", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        hoverlabel=dict(bgcolor="#19374d", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e5ebf0")
    fig.update_yaxes(gridcolor="#edf1f4", zeroline=False)
    return fig


def sorted_stages(values) -> list[str]:
    present = set(values.dropna().astype(str))
    return [stage for stage in STAGE_ORDER if stage in present] + sorted(present - set(STAGE_ORDER))


def format_number(value, digits: int = 1) -> str:
    return "—" if pd.isna(value) else f"{value:,.{digits}f}"


st.sidebar.markdown("### ✳ Cohort controls")
st.sidebar.caption("Use the filters to explore a subset of records. Every view below updates together.")
if st.sidebar.button("Reset filters", use_container_width=True):
    for key in [
        "f_age", "f_tumor", "f_status", "f_stage", "f_race", "f_er", "f_pr",
        "f_t", "f_n", "f_summary", "f_grade", "f_diff", "f_marital",
    ]:
        st.session_state.pop(key, None)
    st.rerun()

uploaded_file = st.sidebar.file_uploader(
    "Use another cohort CSV (optional)", type=["csv"], help="Expected columns are the 16 fields used in the notebook."
)

try:
    if uploaded_file is not None:
        raw_data = pd.read_csv(uploaded_file)
        data_label = uploaded_file.name
    elif DATA_PATH.exists():
        raw_data = read_default_data(str(DATA_PATH))
        data_label = "Bundled SEER cohort"
    else:
        raw_data = None
        data_label = ""
    if raw_data is None:
        st.title("Breast Cancer Cohort Explorer")
        st.warning("The project CSV is not available yet. Add `data/Breast_Cancer.csv` or upload a cohort CSV in the sidebar.")
        st.stop()
    data = standardize_data(raw_data)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"I couldn't read this dataset: {error}")
    st.stop()

age_min = int(data["age"].min())
age_max = int(data["age"].max())
tumor_min = int(data["tumor_size"].min())
tumor_max = int(data["tumor_size"].max())

age_range = st.sidebar.slider("Age at diagnosis", age_min, age_max, (age_min, age_max), key="f_age")
tumor_range = st.sidebar.slider("Tumor size", tumor_min, tumor_max, (tumor_min, tumor_max), key="f_tumor")
status_options = sorted(data["status"].dropna().unique().tolist())
stage_options = sorted_stages(data["sixth_stage"])
race_options = sorted(data["race"].dropna().unique().tolist())
er_options = sorted(data["estrogen_status"].dropna().unique().tolist())
pr_options = sorted(data["progesterone_status"].dropna().unique().tolist())

selected_status = st.sidebar.multiselect("Vital status", status_options, default=status_options, key="f_status")
selected_stage = st.sidebar.multiselect("6th stage", stage_options, default=stage_options, key="f_stage")
selected_race = st.sidebar.multiselect("Race", race_options, default=race_options, key="f_race")
selected_er = st.sidebar.multiselect("Estrogen receptor", er_options, default=er_options, key="f_er")
selected_pr = st.sidebar.multiselect("Progesterone receptor", pr_options, default=pr_options, key="f_pr")

with st.sidebar.expander("More clinical & demographic filters"):
    t_options = sorted(data["t_stage"].dropna().unique().tolist())
    n_options = sorted(data["n_stage"].dropna().unique().tolist())
    summary_options = sorted(data["a_stage"].dropna().unique().tolist())
    grade_options = sorted(data["grade"].dropna().unique().tolist())
    diff_options = sorted(data["differentiate"].dropna().unique().tolist())
    marital_options = sorted(data["marital_status"].dropna().unique().tolist())
    selected_t = st.multiselect("T stage", t_options, default=t_options, key="f_t")
    selected_n = st.multiselect("N stage", n_options, default=n_options, key="f_n")
    selected_summary = st.multiselect("Summary stage", summary_options, default=summary_options, key="f_summary")
    selected_grade = st.multiselect("Grade", grade_options, default=grade_options, key="f_grade")
    selected_diff = st.multiselect("Differentiation", diff_options, default=diff_options, key="f_diff")
    selected_marital = st.multiselect("Marital status", marital_options, default=marital_options, key="f_marital")

filtered = data[
    data["age"].between(*age_range)
    & data["tumor_size"].between(*tumor_range)
    & data["status"].isin(selected_status)
    & data["sixth_stage"].isin(selected_stage)
    & data["race"].isin(selected_race)
    & data["estrogen_status"].isin(selected_er)
    & data["progesterone_status"].isin(selected_pr)
    & data["t_stage"].isin(selected_t)
    & data["n_stage"].isin(selected_n)
    & data["a_stage"].isin(selected_summary)
    & data["grade"].isin(selected_grade)
    & data["differentiate"].isin(selected_diff)
    & data["marital_status"].isin(selected_marital)
].copy()

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Clinical cohort · descriptive explorer</div>
      <h1>Breast Cancer Cohort Explorer</h1>
      <p>Explore demographics, tumor and nodal characteristics, receptor status, and recorded vital status across this historical SEER-derived cohort.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

source_note = "The notebook’s source cohort covers female patients diagnosed in 2006–2010. This dashboard describes the supplied records; it does not estimate an individual prognosis."
st.caption(f"{len(filtered):,} of {len(data):,} records · Data: {data_label} · {source_note}")

if filtered.empty:
    st.info("No records match these filters. Broaden one or more selections in the sidebar.")
    st.stop()

total = len(filtered)
alive_count = int((filtered["status"] == "Alive").sum())
dead_count = int((filtered["status"] == "Dead").sum())
alive_share = alive_count / total if total else 0
median_observed = filtered["survival_months"].median()
median_tumor = filtered["tumor_size"].median()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Records in view", f"{total:,}", help="Number of records after applying all sidebar filters.")
kpi2.metric("Alive at recorded status", f"{alive_share:.1%}", f"{alive_count:,} records", help="Observed vital-status share in this filtered dataset, not a population survival estimate.")
kpi3.metric("Median recorded months", f"{median_observed:.0f}", help="Median value of Survival Months across both Alive and Dead records.")
kpi4.metric("Median tumor size", f"{median_tumor:.0f}", help="Original dataset units are retained; the notebook does not specify units.")

overview_tab, tumor_tab, outcome_tab, people_tab, records_tab = st.tabs(
    ["Overview", "Tumor & nodes", "Status & receptors", "Demographics", "Records & quality"]
)

with overview_tab:
    st.markdown('<div class="section-label">Cohort snapshot</div>', unsafe_allow_html=True)
    st.subheader("Who is represented, and what was recorded?")
    col_a, col_b = st.columns([1, 1.35], gap="large")
    with col_a:
        status_counts = filtered["status"].value_counts().reindex(["Alive", "Dead"]).dropna().rename_axis("Status").reset_index(name="Records")
        fig = px.pie(
            status_counts,
            names="Status",
            values="Records",
            hole=.66,
            color="Status",
            color_discrete_map=STATUS_COLORS,
            hover_data={"Records": ":,", "Status": True},
        )
        fig.update_traces(textposition="outside", texttemplate="%{label}<br>%{percent}", showlegend=False)
        fig.add_annotation(text=f"{total:,}<br><span style='font-size:11px'>records</span>", x=.5, y=.5, showarrow=False, font=dict(size=19, color="#19374d"))
        st.plotly_chart(make_chart(fig, 325), use_container_width=True)
        st.markdown(
            f'<div class="insight"><b>{alive_count:,} alive</b> and <b>{dead_count:,} dead</b> records in the current view. Vital status is the recorded endpoint in this file.</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        stage_counts = filtered["sixth_stage"].value_counts().reindex(sorted_stages(filtered["sixth_stage"])).rename_axis("6th stage").reset_index(name="Records")
        fig = px.bar(stage_counts, x="Records", y="6th stage", orientation="h", color="6th stage", color_discrete_sequence=PALETTE, text="Records")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, yaxis=dict(categoryorder="array", categoryarray=sorted_stages(filtered["sixth_stage"]), autorange="reversed"))
        st.plotly_chart(make_chart(fig, 360), use_container_width=True)
        st.markdown('<div class="muted-note">Stage categories follow the sixth-edition stage field provided by the notebook.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Distribution</div>', unsafe_allow_html=True)
    st.subheader("Age and tumor size")
    col_c, col_d = st.columns(2, gap="large")
    with col_c:
        fig = px.histogram(filtered, x="age", color="status", barmode="overlay", opacity=.8, nbins=25, color_discrete_map=STATUS_COLORS, marginal="box", labels={"age": "Age at diagnosis", "count": "Records", "status": "Vital status"})
        st.plotly_chart(make_chart(fig, 360), use_container_width=True)
    with col_d:
        fig = px.histogram(filtered, x="tumor_size", color="status", barmode="overlay", opacity=.8, nbins=28, color_discrete_map=STATUS_COLORS, labels={"tumor_size": "Tumor size (dataset units)", "count": "Records", "status": "Vital status"})
        st.plotly_chart(make_chart(fig, 360), use_container_width=True)

with tumor_tab:
    st.markdown('<div class="section-label">Tumor burden & nodal involvement</div>', unsafe_allow_html=True)
    st.subheader("Tumor and regional lymph node patterns")
    left, right = st.columns([1.45, 1], gap="large")
    with left:
        plot_data = filtered.dropna(subset=["tumor_size", "regional_node_positive"])
        fig = px.scatter(
            plot_data,
            x="tumor_size",
            y="regional_node_positive",
            color="status",
            symbol="status",
            hover_data=["age", "sixth_stage", "regional_node_examined", "survival_months"],
            color_discrete_map=STATUS_COLORS,
            opacity=.65,
            labels={"tumor_size": "Tumor size (dataset units)", "regional_node_positive": "Positive regional nodes", "status": "Vital status", "age": "Age", "sixth_stage": "6th stage", "regional_node_examined": "Nodes examined", "survival_months": "Recorded months"},
        )
        st.plotly_chart(make_chart(fig, 420), use_container_width=True)
    with right:
        node_summary = filtered.groupby("status", dropna=False).agg(
            median_positive_nodes=("regional_node_positive", "median"),
            median_examined_nodes=("regional_node_examined", "median"),
        ).reset_index()
        node_summary = node_summary.rename(columns={"median_positive_nodes": "Median positive nodes", "median_examined_nodes": "Median examined nodes"})
        fig = px.bar(node_summary, x="status", y=["Median positive nodes", "Median examined nodes"], barmode="group", color_discrete_sequence=["#d95878", "#6174c8"], labels={"status": "Vital status", "value": "Median node count", "variable": "Measure"})
        st.plotly_chart(make_chart(fig, 420), use_container_width=True)
        st.caption("Medians summarize records in each status group; they are descriptive and unadjusted.")

    stage_status = filtered.groupby(["sixth_stage", "status"], observed=False).size().rename("Records").reset_index()
    stage_status["Share within stage"] = stage_status["Records"] / stage_status.groupby("sixth_stage")["Records"].transform("sum")
    fig = px.bar(stage_status, x="sixth_stage", y="Share within stage", color="status", barmode="group", color_discrete_map=STATUS_COLORS, category_orders={"sixth_stage": sorted_stages(filtered["sixth_stage"])}, hover_data={"Records": True, "Share within stage": ":.1%"}, labels={"sixth_stage": "6th stage", "status": "Vital status"})
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(make_chart(fig, 370), use_container_width=True)

with outcome_tab:
    st.markdown('<div class="section-label">Recorded outcome & receptors</div>', unsafe_allow_html=True)
    st.subheader("Observed follow-up and receptor status")
    st.info("Survival Months is a recorded duration. Records marked Alive may be right-censored at last follow-up, so these charts are not Kaplan–Meier estimates or individual survival predictions.")

    col_e, col_f = st.columns(2, gap="large")
    with col_e:
        fig = px.box(filtered, x="status", y="survival_months", color="status", points="outliers", color_discrete_map=STATUS_COLORS, labels={"status": "Vital status", "survival_months": "Recorded months"})
        st.plotly_chart(make_chart(fig, 390), use_container_width=True)
    with col_f:
        followup = filtered.groupby("status", observed=False)["survival_months"].agg(["median", "mean", "count"]).reset_index()
        fig = px.bar(followup, x="status", y="median", color="status", text="count", color_discrete_map=STATUS_COLORS, labels={"status": "Vital status", "median": "Median recorded months", "count": "Records"})
        fig.update_traces(texttemplate="n = %{text:,}", textposition="outside", cliponaxis=False, showlegend=False)
        st.plotly_chart(make_chart(fig, 390), use_container_width=True)

    receptor_fields = [("estrogen_status", "Estrogen receptor"), ("progesterone_status", "Progesterone receptor")]
    receptor_data = []
    for field, title in receptor_fields:
        group = filtered.groupby(field, dropna=False)["status"].agg(records="size", dead=lambda values: (values == "Dead").sum()).reset_index()
        group["Observed dead share"] = group["dead"] / group["records"]
        group["Receptor"] = title
        group = group.rename(columns={field: "Result"})
        receptor_data.append(group)
    receptor_summary = pd.concat(receptor_data, ignore_index=True)
    fig = px.bar(receptor_summary, x="Receptor", y="Observed dead share", color="Result", barmode="group", text="records", color_discrete_sequence=["#6174c8", "#e5a24c"], hover_data={"records": ":,", "dead": ":,", "Observed dead share": ":.1%"}, labels={"Observed dead share": "Dead records / records in group"})
    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(texttemplate="n=%{text:,}", textposition="outside", cliponaxis=False)
    st.plotly_chart(make_chart(fig, 380), use_container_width=True)
    st.caption("Shares are computed within each receptor group in the selected cohort. They are unadjusted associations, not treatment effects.")

with people_tab:
    st.markdown('<div class="section-label">Demographic profile</div>', unsafe_allow_html=True)
    st.subheader("Age, race, and marital status")
    col_g, col_h = st.columns(2, gap="large")
    with col_g:
        fig = px.histogram(filtered, x="age", color="race", barmode="group", nbins=24, color_discrete_sequence=PALETTE, labels={"age": "Age at diagnosis", "count": "Records", "race": "Race"})
        st.plotly_chart(make_chart(fig, 380), use_container_width=True)
    with col_h:
        marital = filtered["marital_status"].value_counts().rename_axis("Marital status").reset_index(name="Records").sort_values("Records")
        fig = px.bar(marital, x="Records", y="Marital status", orientation="h", color="Marital status", color_discrete_sequence=PALETTE, text="Records")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False)
        st.plotly_chart(make_chart(fig, 380), use_container_width=True)
    age_status = filtered.groupby("status", observed=False)["age"].agg(["median", "mean", "count"]).reset_index()
    st.dataframe(age_status.rename(columns={"status": "Vital status", "median": "Median age", "mean": "Mean age", "count": "Records"}), hide_index=True, use_container_width=True)

with records_tab:
    st.markdown('<div class="section-label">Dataset details</div>', unsafe_allow_html=True)
    st.subheader("Filtered records and data quality")
    missing_count = int(filtered[REQUIRED_COLUMNS].isna().sum().sum())
    quality_a, quality_b, quality_c = st.columns(3)
    quality_a.metric("Fields", len(REQUIRED_COLUMNS))
    quality_b.metric("Missing cells in view", f"{missing_count:,}")
    quality_c.metric("Rows excluded by filters", f"{len(data) - len(filtered):,}")

    export_data = filtered[REQUIRED_COLUMNS].copy()
    export_data.columns = [SOURCE_COLUMN_NAMES[column] for column in REQUIRED_COLUMNS]
    st.download_button("Download filtered records", export_data.to_csv(index=False).encode("utf-8"), "breast_cancer_filtered.csv", "text/csv")
    st.dataframe(filtered[REQUIRED_COLUMNS], use_container_width=True, hide_index=True, height=460)

    with st.expander("Field guide"):
        field_guide = pd.DataFrame(
            [
                ("Age", "Age at diagnosis, in years."),
                ("Race / Marital Status", "Recorded demographic categories."),
                ("T Stage / N Stage / 6th Stage", "Tumor, regional node, and combined sixth-edition stage fields."),
                ("Differentiate / Grade", "Recorded differentiation and grade categories."),
                ("A Stage", "Summary stage field; values in this file are Regional or Distant."),
                ("Tumor Size", "Tumor size as stored in the source file; units are not specified in the notebook."),
                ("Estrogen / Progesterone Status", "Recorded receptor status categories."),
                ("Regional Node Examined / Reginol Node Positive", "Examined and positive regional lymph-node counts; source spelling is preserved in the CSV."),
                ("Survival Months / Status", "Recorded months and vital status (Alive or Dead) at the dataset endpoint."),
            ],
            columns=["Field", "Description"],
        )
        st.dataframe(field_guide, hide_index=True, use_container_width=True)

st.markdown(
    '<div class="source-line">Source cohort: SEER Breast Cancer Data, deposited by Jing Teng and shared via <a href="https://zenodo.org/records/5120960" target="_blank">Zenodo record 5120960</a> (DOI: 10.5281/zenodo.5120960). Historical records diagnosed 2006–2010. Descriptive educational analysis only; this dashboard is not a clinical decision tool.</div>',
    unsafe_allow_html=True,
)
