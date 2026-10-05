import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Student Assessment Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Professional CSS ----------
st.markdown("""
<style>

/* =========================
   MAIN APP
========================= */
.stApp {
    background: #0B1220;
    color: #E5E7EB;
}

/* =========================
   SIDEBAR
========================= */
[data-testid="stSidebar"] {
    background: #0F172A;
    border-right: 1px solid #1E293B;
}

[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

/* =========================
   MAIN TITLE
========================= */
.main-title {
    font-size: 32px;
    font-weight: 800;
    color: #60A5FA;
    margin-bottom: 0;
}

/* =========================
   SUB TITLE
========================= */
.sub-title {
    color: #94A3B8;
    font-size: 15px;
    margin-top: 2px;
    margin-bottom: 20px;
}

/* =========================
   KPI CARDS
========================= */
.kpi {
    background: #1E293B;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    border: 1px solid #334155;
}

/* KPI LABEL */
.kpi-label {
    color: #94A3B8;
    font-size: 13px;
    font-weight: 600;
}

/* KPI VALUE */
.kpi-value {
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 800;
    margin-top: 4px;
}

/* =========================
   SECTION TITLES
========================= */
.section {
    color: #60A5FA;
    font-size: 20px;
    font-weight: 750;
    margin: 22px 0 8px;
}

/* =========================
   FOOTER
========================= */
.footer {
    text-align: center;
    color: #64748B;
    font-size: 12px;
    padding: 22px 0 8px;
}

/* =========================
   STREAMLIT BUTTON
========================= */
.stButton > button {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
}

.stButton > button:hover {
    background: #3B82F6;
}

/* =========================
   SELECTBOX / MULTISELECT
========================= */
div[data-baseweb="select"] > div {
    background-color: #1E293B;
    border-color: #334155;
    color: #F8FAFC;
}

/* =========================
   DATAFRAME
========================= */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

/* =========================
   SCROLLBAR
========================= */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0B1220;
}

::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

</style>

""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    assessments = pd.read_csv("assessments.csv")
    courses = pd.read_csv("courses.csv")
    assessments["score"] = pd.to_numeric(assessments["score"], errors="coerce")
    assessments["attendance_pct"] = pd.to_numeric(
        assessments["attendance_pct"], errors="coerce"
    )
    merged = assessments.merge(courses, on="course_id", how="left")
    merged["Result"] = merged["score"].apply(lambda x: "Pass" if x >= 50 else "Fail")
    month_order = ["Jan", "Feb", "Mar"]
    merged["month"] = pd.Categorical(
        merged["month"], categories=month_order, ordered=True
    )
    return merged

df = load_data()

# ---------- Sidebar ----------
st.sidebar.markdown("## 🎓 Dashboard Filters")
st.sidebar.markdown("---")

batches = st.sidebar.multiselect(
    "Batch",
    sorted(df["batch"].dropna().unique()),
    default=sorted(df["batch"].dropna().unique())
)

departments = st.sidebar.multiselect(
    "Department",
    sorted(df["department"].dropna().unique()),
    default=sorted(df["department"].dropna().unique())
)

months = st.sidebar.multiselect(
    "Month",
    ["Jan", "Feb", "Mar"],
    default=["Jan", "Feb", "Mar"]
)

filtered = df[
    df["batch"].isin(batches)
    & df["department"].isin(departments)
    & df["month"].astype(str).isin(months)
].copy()

# ---------- Header ----------
st.markdown(
    '<div class="main-title">🎓 Student Assessment Performance Dashboard</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Student Performance | Scores | Attendance | Pass Rate | Course Analytics</div>',
    unsafe_allow_html=True
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------- KPI calculations ----------
assessment_count = len(filtered)
avg_score = filtered["score"].mean()
pass_rate = (filtered["score"].ge(50).mean()) * 100
avg_attendance = filtered["attendance_pct"].mean()

# ---------- KPI cards ----------
c1, c2, c3, c4 = st.columns(4)

for col, label, value in [
    (c1, "Assessment Count", f"{assessment_count:,}"),
    (c2, "Average Score", f"{avg_score:.1f}"),
    (c3, "Pass Rate", f"{pass_rate:.2f}%"),
    (c4, "Avg Attendance", f"{avg_attendance:.1f}%"),
]:
    col.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True
    )

# ---------- Department analysis ----------
st.markdown('<div class="section">📊 Department Performance</div>', unsafe_allow_html=True)
left, right = st.columns(2)

dept_avg = (
    filtered.groupby("department", as_index=False)["score"]
    .mean()
    .sort_values("score", ascending=False)
)

with left:
    fig = px.bar(
        dept_avg,
        x="department",
        y="score",
        text_auto=".1f",
        title="Average Score by Department",
        labels={"score": "Average Score", "department": "Department"}
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20,r=20,t=55,b=20),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_yaxes(range=[0,100])
    st.plotly_chart(fig, use_container_width=True)

dept_pass = (
    filtered.assign(Pass=filtered["score"] >= 50)
    .groupby("department")["Pass"].mean()
    .mul(100)
    .reset_index(name="pass_rate")
)

with right:
    fig = px.bar(
        dept_pass,
        x="department",
        y="pass_rate",
        text_auto=".1f",
        title="Pass Rate by Department",
        labels={"pass_rate": "Pass Rate (%)", "department": "Department"}
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20,r=20,t=55,b=20),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_yaxes(range=[0,100])
    st.plotly_chart(fig, use_container_width=True)

# ---------- Monthly trend ----------
st.markdown('<div class="section">📈 Monthly Performance Trend</div>', unsafe_allow_html=True)

monthly = (
    filtered.groupby("month", observed=False, as_index=False)["score"]
    .mean()
    .sort_values("month")
)

fig = px.line(
    monthly,
    x="month",
    y="score",
    markers=True,
    text=monthly["score"].round(1),
    title="Monthly Average Score (Jan → Feb → Mar)",
    labels={"score": "Average Score", "month": "Month"}
)
fig.update_traces(textposition="top center")
fig.update_layout(
    height=360,
    margin=dict(l=20,r=20,t=55,b=20),
    plot_bgcolor="white",
    paper_bgcolor="white"
)
fig.update_yaxes(range=[0,100])
st.plotly_chart(fig, use_container_width=True)

# ---------- Course + batch ----------
st.markdown('<div class="section">📚 Course & Batch Analysis</div>', unsafe_allow_html=True)
left, right = st.columns(2)

course_avg = (
    filtered.groupby(["course", "department"], as_index=False)["score"]
    .mean()
    .sort_values("score", ascending=False)
)

with left:
    fig = px.bar(
        course_avg,
        x="course",
        y="score",
        color="department",
        text_auto=".1f",
        title="Average Score by Course",
        labels={"score":"Average Score", "course":"Course"}
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20,r=20,t=55,b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="Department"
    )
    fig.update_yaxes(range=[0,100])
    st.plotly_chart(fig, use_container_width=True)

batch_avg = (
    filtered.groupby("batch", as_index=False)["score"]
    .mean()
    .sort_values("score", ascending=False)
)

with right:
    fig = px.bar(
        batch_avg,
        x="batch",
        y="score",
        text_auto=".1f",
        title="Average Score by Batch",
        labels={"score":"Average Score", "batch":"Batch"}
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20,r=20,t=55,b=20),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_yaxes(range=[0,100])
    st.plotly_chart(fig, use_container_width=True)

# ---------- Data table ----------
st.markdown('<div class="section">📋 Assessment Details</div>', unsafe_allow_html=True)

display_cols = [
    "assessment_id", "month", "course", "department",
    "batch", "score", "attendance_pct", "Result"
]
st.dataframe(
    filtered[display_cols].sort_values(["month","assessment_id"]),
    use_container_width=True,
    hide_index=True
)

# ---------- Download ----------
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_assessment_data.csv",
    mime="text/csv"
)

st.markdown(
    '<div class="footer">Built with Python • Streamlit • Pandas • Plotly | Student Assessment Analytics</div>',
    unsafe_allow_html=True
)
