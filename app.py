"""
StudentPulse — Student Performance Analytics Dashboard
Main Streamlit Application
Developer: Daniel Richard Xavier
Repository: https://github.com/drx2k06/miniproject7.git
"""

from __future__ import annotations
import os
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_validation import (
    load_dataset,
    inspect_dataframe,
    detect_column_roles,
    validate_dataset,
    clean_dataset,
)
from src.analytics import (
    calculate_overview_metrics,
    flag_academic_support,
    get_subject_statistics,
    get_attendance_correlation,
    get_tier_distribution,
    filter_dataset,
    categorize_performance,
    ETHICAL_DISCLAIMER,
    CORRELATION_DISCLAIMER,
)

# Set page configuration
st.set_page_config(
    page_title="StudentPulse — Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# App Title & Header
st.title("🎓 StudentPulse — Student Performance Analytics")
st.caption("A Dockerized interactive analytics dashboard for academic evaluation, attendance tracking, and early student support.")
st.markdown(
    """
    <div style="background-color: #f0f2f6; padding: 8px 16px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #1f77b4;">
        <strong>Project Developer:</strong> Daniel Richard Xavier &nbsp;|&nbsp; 
        <strong>Framework:</strong> Streamlit, Pandas, Plotly &nbsp;|&nbsp; 
        <strong>Deployment:</strong> Containerized via Docker &amp; Compose
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Data Source Selection
st.sidebar.header("📁 Data Source & Ingestion")

data_mode = st.sidebar.radio(
    "Choose Data Source:",
    options=["Sample Dataset (Fictional)", "Upload Custom CSV"],
    index=0,
    help="Select the bundled synthetic dataset or upload your institution's CSV file.",
)

raw_df: pd.DataFrame | None = None
data_source_label = ""
is_sample_data = False

if data_mode == "Sample Dataset (Fictional)":
    is_sample_data = True
    data_source_label = "Fictional Sample Academic Dataset (data/sample_students.csv)"
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_students.csv")
    if os.path.exists(sample_path):
        raw_df, err = load_dataset(sample_path)
        if err:
            st.sidebar.error(f"Failed to load sample dataset: {err}")
    else:
        st.sidebar.error("Sample dataset file not found at 'data/sample_students.csv'.")
else:
    is_sample_data = False
    uploaded_file = st.sidebar.file_uploader(
        "Upload Student Academic CSV",
        type=["csv"],
        help="Upload a standard CSV file with headers. Required: at least one numeric marks/score column.",
    )
    if uploaded_file is not None:
        raw_df, err = load_dataset(uploaded_file)
        if err:
            st.sidebar.error(f"Upload error: {err}")
        else:
            data_source_label = f"Uploaded File: {uploaded_file.name}"
    else:
        st.info("👋 Welcome! Please upload a CSV file in the sidebar, or switch to 'Sample Dataset (Fictional)' to explore immediately.")
        st.stop()

if raw_df is None or raw_df.empty:
    st.warning("⚠️ No valid data loaded. Please provide a valid CSV dataset.")
    st.stop()

# Inspect dataset
inspection = inspect_dataframe(raw_df)
auto_roles = detect_column_roles(raw_df)

# Sidebar: Column Mapping
st.sidebar.subheader("⚙️ Column Mapping")
st.sidebar.caption("Map CSV columns to analytical roles. Detected defaults are pre-selected.")

available_cols = ["-- None / Not Applicable --"] + list(raw_df.columns)

def get_col_index(candidate: str | None) -> int:
    if candidate and candidate in available_cols:
        return available_cols.index(candidate)
    return 0

selected_id = st.sidebar.selectbox(
    "Student ID / Roll No:",
    options=available_cols,
    index=get_col_index(auto_roles.get("student_id")),
    help="Unique student identifier used for distinct student counts.",
)

selected_name = st.sidebar.selectbox(
    "Student Name (Optional):",
    options=available_cols,
    index=get_col_index(auto_roles.get("student_name")),
    help="Student name for reporting and tables.",
)

selected_marks = st.sidebar.selectbox(
    "Marks / Score Column (Required):",
    options=available_cols,
    index=get_col_index(auto_roles.get("marks")),
    help="Numeric column containing marks, scores, or percentage.",
)

selected_attendance = st.sidebar.selectbox(
    "Attendance Column (Optional):",
    options=available_cols,
    index=get_col_index(auto_roles.get("attendance")),
    help="Numeric column containing attendance percentage or count.",
)

selected_subject = st.sidebar.selectbox(
    "Subject / Course (Optional):",
    options=available_cols,
    index=get_col_index(auto_roles.get("subject")),
    help="Categorical column containing subject or course names.",
)

selected_semester = st.sidebar.selectbox(
    "Semester / Term (Optional):",
    options=available_cols,
    index=get_col_index(auto_roles.get("semester")),
    help="Categorical column containing semester or term labels.",
)

selected_class = st.sidebar.selectbox(
    "Class / Section (Optional):",
    options=available_cols,
    index=get_col_index(auto_roles.get("class_section")),
    help="Categorical column containing class, branch, or section labels.",
)

# Convert selection to clean dictionary
role_mapping = {
    "student_id": selected_id if selected_id != "-- None / Not Applicable --" else None,
    "student_name": selected_name if selected_name != "-- None / Not Applicable --" else None,
    "marks": selected_marks if selected_marks != "-- None / Not Applicable --" else None,
    "attendance": selected_attendance if selected_attendance != "-- None / Not Applicable --" else None,
    "subject": selected_subject if selected_subject != "-- None / Not Applicable --" else None,
    "semester": selected_semester if selected_semester != "-- None / Not Applicable --" else None,
    "class_section": selected_class if selected_class != "-- None / Not Applicable --" else None,
}

# Validation
validation_report = validate_dataset(raw_df, role_mapping)

if not validation_report["is_valid"]:
    st.error("### ❌ Dataset Validation Failed")
    for error_msg in validation_report["errors"]:
        st.error(f"- {error_msg}")
    st.info("💡 Adjust the column mapping in the sidebar to match your dataset structure.")
    st.stop()

# Sidebar: Configurable Thresholds
st.sidebar.subheader("🎯 Academic Thresholds")
pass_threshold = st.sidebar.slider(
    "Minimum Passing Score:",
    min_value=0.0,
    max_value=100.0,
    value=40.0,
    step=1.0,
    help="Marks threshold required to pass a subject/course.",
)

score_warning_threshold = st.sidebar.slider(
    "Academic Review Score Threshold:",
    min_value=0.0,
    max_value=100.0,
    value=45.0,
    step=1.0,
    help="Students scoring below this threshold are flagged for peer tutoring or academic review.",
)

attendance_warning_threshold = 75.0
if role_mapping.get("attendance"):
    attendance_warning_threshold = st.sidebar.slider(
        "Attendance Warning Threshold (%):",
        min_value=0.0,
        max_value=100.0,
        value=75.0,
        step=1.0,
        help="Students below this attendance percentage are flagged for attendance counseling.",
    )

# Sidebar: Interactive Filters
st.sidebar.subheader("🔍 Interactive Filters")
active_filters: dict = {"role_mapping": role_mapping}

# Filter: Subjects
if role_mapping.get("subject"):
    unique_subjects = sorted([str(x) for x in raw_df[role_mapping["subject"]].dropna().unique()])
    selected_subjs = st.sidebar.multiselect(
        "Filter by Subject:",
        options=unique_subjects,
        default=unique_subjects,
    )
    active_filters["subjects"] = selected_subjs

# Filter: Semesters
if role_mapping.get("semester"):
    unique_sems = sorted([str(x) for x in raw_df[role_mapping["semester"]].dropna().unique()])
    selected_sems = st.sidebar.multiselect(
        "Filter by Semester:",
        options=unique_sems,
        default=unique_sems,
    )
    active_filters["semesters"] = selected_sems

# Filter: Classes
if role_mapping.get("class_section"):
    unique_classes = sorted([str(x) for x in raw_df[role_mapping["class_section"]].dropna().unique()])
    selected_cls = st.sidebar.multiselect(
        "Filter by Class/Section:",
        options=unique_classes,
        default=unique_classes,
    )
    active_filters["classes"] = selected_cls

# Filter: Marks Range
if role_mapping.get("marks"):
    numeric_marks = pd.to_numeric(raw_df[role_mapping["marks"]], errors="coerce").dropna()
    if not numeric_marks.empty:
        min_mark_val = float(numeric_marks.min())
        max_mark_val = float(numeric_marks.max())
        if min_mark_val < max_mark_val:
            selected_mark_range = st.sidebar.slider(
                "Filter Marks Range:",
                min_value=round(min_mark_val, 1),
                max_value=round(max_mark_val, 1),
                value=(round(min_mark_val, 1), round(max_mark_val, 1)),
            )
            active_filters["marks_range"] = selected_mark_range

# Filter: Attendance Range
if role_mapping.get("attendance"):
    numeric_att = pd.to_numeric(raw_df[role_mapping["attendance"]], errors="coerce").dropna()
    if not numeric_att.empty:
        min_att_val = float(numeric_att.min())
        max_att_val = float(numeric_att.max())
        if min_att_val < max_att_val:
            selected_att_range = st.sidebar.slider(
                "Filter Attendance Range (%):",
                min_value=round(min_att_val, 1),
                max_value=round(max_att_val, 1),
                value=(round(min_att_val, 1), round(max_att_val, 1)),
            )
            active_filters["attendance_range"] = selected_att_range

# Apply filters
filtered_df = filter_dataset(raw_df, active_filters)

# Calculate dynamic overview metrics
metrics = calculate_overview_metrics(
    df=filtered_df,
    marks_col=role_mapping.get("marks"),
    attendance_col=role_mapping.get("attendance"),
    student_id_col=role_mapping.get("student_id"),
    pass_threshold=pass_threshold,
    score_support_threshold=score_warning_threshold,
    attendance_support_threshold=attendance_warning_threshold,
)

# Flag support records for active data
flagged_df = flag_academic_support(
    df=filtered_df,
    marks_col=role_mapping.get("marks"),
    attendance_col=role_mapping.get("attendance"),
    student_id_col=role_mapping.get("student_id"),
    score_threshold=score_warning_threshold,
    attendance_threshold=attendance_warning_threshold,
)

# Provenance notification banner
if is_sample_data:
    st.info(
        "ℹ️ **Illustrative Sample Data Active:** You are currently exploring the bundled synthetic dataset "
        "(`data/sample_students.csv`). All student records, marks, and attendance figures are entirely fictitious "
        "and provided strictly for software demonstration. You may upload institutional CSV data anytime via the sidebar."
    )
else:
    st.success(f"📊 **Custom Dataset Active:** {data_source_label} ({len(filtered_df)} records displayed of {len(raw_df)} total).")

# Display warnings if present
if validation_report["warnings"]:
    with st.expander("⚠️ Data Quality Notices & Warnings", expanded=False):
        for w in validation_report["warnings"]:
            st.write(f"- {w}")

# Navigation Tabs
tab_overview, tab_analytics, tab_support, tab_explorer, tab_guide = st.tabs([
    "📈 Overview & Key Metrics",
    "📊 Interactive Analytics",
    "🚩 Academic Support Alerts",
    "🔍 Data Explorer & Quality",
    "📖 System Architecture & Viva Guide",
])

# -------------------------------------------------------------
# TAB 1: OVERVIEW & KEY METRICS
# -------------------------------------------------------------
with tab_overview:
    st.subheader("Key Performance Indicators (KPIs)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Students",
            value=metrics["total_students"],
            help="Count of unique student identifiers (or total records if identifier is unmapped).",
        )
    
    with col2:
        avg_score_str = f"{metrics['average_score']:.1f}" if metrics["average_score"] is not None else "N/A"
        st.metric(
            label="Overall Average Score",
            value=avg_score_str,
            help="Mean score computed across all valid marks in filtered records.",
        )
        
    with col3:
        avg_att_str = f"{metrics['average_attendance']:.1f}%" if metrics["average_attendance"] is not None else "N/A"
        st.metric(
            label="Average Attendance",
            value=avg_att_str,
            help="Mean attendance percentage across all valid records.",
        )
        
    with col4:
        pass_rate_str = f"{metrics['pass_percentage']:.1f}%" if metrics["pass_percentage"] is not None else "N/A"
        st.metric(
            label="Pass Percentage",
            value=pass_rate_str,
            delta=f"Threshold: {pass_threshold:.0f}",
            help=f"Percentage of records meeting or exceeding the passing threshold of {pass_threshold:.0f}.",
        )
        
    with col5:
        support_cnt = metrics["support_needed_count"]
        support_pct = metrics["support_needed_percentage"]
        st.metric(
            label="Academic Review Flags",
            value=support_cnt,
            delta=f"{support_pct:.1f}% flagged",
            delta_color="inverse",
            help="Count and percentage of students meeting configured score or attendance review criteria.",
        )

    st.markdown("---")
    
    # Overview Summary Cards
    col_sum1, col_sum2 = st.columns(2)
    with col_sum1:
        st.markdown("#### 📋 Cohort Summary")
        summary_rows = [
            f"- **Active Records in View:** {metrics['total_records']} rows",
            f"- **Unique Student Cohort:** {metrics['total_students']} students",
            f"- **Score Range:** {metrics['min_score']} (Min) to {metrics['max_score']} (Max)" if metrics['min_score'] is not None else "- **Score Range:** N/A",
            f"- **Median Score:** {metrics['median_score']}" if metrics['median_score'] is not None else "- **Median Score:** N/A",
            f"- **Passing Records:** {metrics['passed_records']} / {metrics['total_records']}",
        ]
        st.markdown("\n".join(summary_rows))
        
    with col_sum2:
        st.markdown("#### 🎯 Configured Policy Bounds")
        policy_rows = [
            f"- **Passing Grade Standard:** Marks >= `{pass_threshold:.1f}`",
            f"- **Academic Counseling Trigger:** Marks < `{score_warning_threshold:.1f}`",
            f"- **Attendance Warning Trigger:** Attendance < `{attendance_warning_threshold:.1f}%`" if role_mapping.get("attendance") else "- **Attendance Warning Trigger:** Attendance column not mapped",
            f"- **Support Heuristic Policy:** Rule-based flags to enable proactive teacher assistance before final exams.",
        ]
        st.markdown("\n".join(policy_rows))

# -------------------------------------------------------------
# TAB 2: INTERACTIVE ANALYTICS
# -------------------------------------------------------------
with tab_analytics:
    st.subheader("Interactive Visual Analytics")
    
    if filtered_df.empty:
        st.warning("No records match the active filter criteria. Adjust the sidebar filters to view charts.")
    else:
        marks_col = role_mapping.get("marks")
        att_col = role_mapping.get("attendance")
        subj_col = role_mapping.get("subject")
        sem_col = role_mapping.get("semester")
        cls_col = role_mapping.get("class_section")

        # Row 1: Score Distribution & Academic Performance Tiers
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("##### 📊 Academic Score Distribution")
            if marks_col:
                valid_scores = pd.to_numeric(filtered_df[marks_col], errors="coerce").dropna()
                fig_hist = px.histogram(
                    filtered_df,
                    x=marks_col,
                    nbins=12,
                    marginal="box",
                    color_discrete_sequence=["#1f77b4"],
                    title="Distribution of Student Marks",
                    labels={marks_col: "Marks / Score"},
                )
                if metrics["average_score"] is not None:
                    fig_hist.add_vline(
                        x=metrics["average_score"],
                        line_dash="dash",
                        line_color="crimson",
                        annotation_text=f"Mean: {metrics['average_score']:.1f}",
                    )
                if pass_threshold is not None:
                    fig_hist.add_vline(
                        x=pass_threshold,
                        line_dash="dot",
                        line_color="green",
                        annotation_text=f"Pass: {pass_threshold:.0f}",
                    )
                fig_hist.update_layout(bargap=0.05, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Marks column is not available.")

        with chart_col2:
            st.markdown("##### 🏆 Academic Tier Breakdown")
            if marks_col:
                tier_df = get_tier_distribution(filtered_df, marks_col)
                fig_pie = px.pie(
                    tier_df,
                    names="Tier",
                    values="Count",
                    hole=0.45,
                    title="Student Performance Categories",
                    color="Tier",
                    color_discrete_map={
                        "Distinction (>= 75%)": "#2ca02c",
                        "First Class (60–74%)": "#1f77b4",
                        "Second Class (50–59%)": "#ff7f0e",
                        "Pass Class (40–49%)": "#aec7e8",
                        "Remedial (< 40%)": "#d62728",
                    },
                )
                fig_pie.update_traces(textinfo="percent+label")
                fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_pie, use_container_width=True)

        # Row 2: Subject-wise Performance & Attendance vs Marks Scatter
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            st.markdown("##### 📚 Subject-wise Average Performance")
            if subj_col and marks_col:
                subj_stats = get_subject_statistics(filtered_df, subj_col, marks_col)
                if not subj_stats.empty:
                    fig_subj = px.bar(
                        subj_stats,
                        x="Subject",
                        y="Average_Marks",
                        color="Average_Marks",
                        color_continuous_scale="Viridis",
                        title="Average Marks by Subject",
                        text="Average_Marks",
                        hover_data=["Min_Marks", "Max_Marks", "Record_Count"],
                    )
                    fig_subj.update_traces(textposition="outside")
                    fig_subj.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_subj, use_container_width=True)
                else:
                    st.info("No subject-wise records available.")
            else:
                st.info("Subject column is not mapped. Map a Subject column in the sidebar to view course comparisons.")

        with chart_col4:
            st.markdown("##### 📈 Attendance vs. Academic Marks")
            if att_col and marks_col:
                corr_info = get_attendance_correlation(filtered_df, marks_col, att_col)
                
                scatter_kwargs = {
                    "data_frame": filtered_df,
                    "x": att_col,
                    "y": marks_col,
                    "color": "Support_Reason" if "Support_Reason" in flagged_df.columns else None,
                    "title": f"Attendance vs. Marks (r = {corr_info['correlation'] if corr_info['correlation'] is not None else 'N/A'})",
                    "labels": {att_col: "Attendance (%)", marks_col: "Marks"},
                    "hover_data": [role_mapping.get("student_id")] if role_mapping.get("student_id") else None,
                }
                
                # Check if trendline can be drawn
                fig_scatter = px.scatter(
                    flagged_df,
                    x=att_col,
                    y=marks_col,
                    color="Support_Reason",
                    hover_name=role_mapping.get("student_name") or role_mapping.get("student_id"),
                    title=f"Attendance vs. Marks (r = {corr_info['correlation'] if corr_info['correlation'] is not None else 'N/A'})",
                    color_discrete_map={
                        "Satisfactory": "#2ca02c",
                        f"Low Marks (<{score_warning_threshold})": "#ff7f0e",
                        f"Low Attendance (<{attendance_warning_threshold}%)": "#9467bd",
                        f"Low Marks (<{score_warning_threshold}) & Low Attendance (<{attendance_warning_threshold}%)": "#d62728",
                    },
                )
                
                # Add threshold reference lines
                fig_scatter.add_hline(
                    y=score_warning_threshold,
                    line_dash="dot",
                    line_color="crimson",
                    annotation_text=f"Score Alert: {score_warning_threshold:.0f}",
                )
                fig_scatter.add_vline(
                    x=attendance_warning_threshold,
                    line_dash="dot",
                    line_color="purple",
                    annotation_text=f"Attendance Alert: {attendance_warning_threshold:.0f}%",
                )
                fig_scatter.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.caption(f"ℹ️ **Correlation Disclaimer:** {corr_info['disclaimer']}")
            else:
                st.info("Attendance column is not mapped. Map an Attendance column in the sidebar to view correlation charts.")

        # Row 3: Semester & Class Cohort Comparisons
        if sem_col or cls_col:
            chart_col5, chart_col6 = st.columns(2)
            
            with chart_col5:
                if sem_col and marks_col:
                    st.markdown("##### 🗓️ Semester-wise Score Distribution")
                    fig_sem = px.box(
                        filtered_df,
                        x=sem_col,
                        y=marks_col,
                        color=sem_col,
                        title="Score Distribution across Semesters",
                        points="all",
                    )
                    fig_sem.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
                    st.plotly_chart(fig_sem, use_container_width=True)
                else:
                    st.info("Semester column not mapped.")

            with chart_col6:
                if cls_col and marks_col:
                    st.markdown("##### 👥 Class / Section Performance Comparison")
                    fig_cls = px.box(
                        filtered_df,
                        x=cls_col,
                        y=marks_col,
                        color=cls_col,
                        title="Score Distribution across Classes/Sections",
                        points="all",
                    )
                    fig_cls.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
                    st.plotly_chart(fig_cls, use_container_width=True)
                else:
                    st.info("Class/Section column not mapped.")

# -------------------------------------------------------------
# TAB 3: ACADEMIC SUPPORT ALERTS
# -------------------------------------------------------------
with tab_support:
    st.subheader("🚩 Academic Support & Early Mentoring Indicators")
    st.markdown(
        f"""
        > **Ethical & Pedagogical Statement:**  
        > {ETHICAL_DISCLAIMER}
        """
    )
    
    # Filter flagged records
    support_records = flagged_df[flagged_df["Needs_Support"]]
    
    col_sup1, col_sup2, col_sup3 = st.columns(3)
    with col_sup1:
        st.metric("Total Flagged Records", len(support_records))
    with col_sup2:
        student_id_c = role_mapping.get("student_id")
        flagged_students_count = support_records[student_id_c].nunique() if student_id_c and student_id_c in support_records.columns else len(support_records)
        st.metric("Unique Students Requiring Outreach", flagged_students_count)
    with col_sup3:
        pass_remedial_count = metrics["failed_records"]
        st.metric("Records Below Pass Mark", pass_remedial_count)
        
    st.markdown("---")
    
    if support_records.empty:
        st.success("🎉 Excellent! No student records in the current view breach the configured review thresholds.")
    else:
        st.markdown("#### 📋 Flagged Records for Faculty Mentorship")
        
        # Select columns to display
        display_cols = []
        for role in ["student_id", "student_name", "class_section", "semester", "subject", "marks", "attendance"]:
            col_name = role_mapping.get(role)
            if col_name and col_name in support_records.columns and col_name not in display_cols:
                display_cols.append(col_name)
        display_cols.extend(["Support_Reason"])
        
        st.dataframe(
            support_records[display_cols],
            use_container_width=True,
            hide_index=True,
        )
        
        # Download flagged list
        csv_buffer = io.StringIO()
        support_records[display_cols].to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Academic Support Outreach CSV",
            data=csv_buffer.getvalue(),
            file_name="studentpulse_academic_support_list.csv",
            mime="text/csv",
            help="Download the filtered list of students flagged for mentoring follow-up.",
        )

# -------------------------------------------------------------
# TAB 4: DATA EXPLORER & QUALITY
# -------------------------------------------------------------
with tab_explorer:
    st.subheader("🔍 Dataset Inspection, Quality Audit & Export")
    
    st.markdown("#### 📑 Active Filtered Dataset")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        csv_export = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Current Filtered View (CSV)",
            data=csv_export,
            file_name="studentpulse_filtered_data.csv",
            mime="text/csv",
        )
        
    with col_exp2:
        # Non-destructive data cleaning option
        if st.button("🧹 Generate & Preview Cleaned Dataset Copy"):
            cleaned_copy, clean_log = clean_dataset(
                df=raw_df,
                role_mapping=role_mapping,
                drop_duplicates=True,
                clip_ranges=True,
                impute_missing_numeric=False,
            )
            st.session_state["cleaned_df"] = cleaned_copy
            st.session_state["clean_log"] = clean_log
            st.success("Cleaned copy generated successfully!")

    if "cleaned_df" in st.session_state and "clean_log" in st.session_state:
        with st.expander("✨ Cleaned Copy & Transformation Audit Log", expanded=True):
            st.markdown("**Transformations Performed (Original dataset preserved untouched):**")
            for entry in st.session_state["clean_log"]:
                st.write(f"- {entry}")
            st.dataframe(st.session_state["cleaned_df"].head(10), use_container_width=True)
            
            cleaned_csv_buf = st.session_state["cleaned_df"].to_csv(index=False)
            st.download_button(
                label="📥 Download Cleaned Dataset (CSV)",
                data=cleaned_csv_buf,
                file_name="studentpulse_cleaned_dataset.csv",
                mime="text/csv",
            )

    st.markdown("---")
    st.markdown("#### 📊 Summary Statistics & Quality Audit")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown("##### Descriptive Statistics (`describe()`)")
        st.dataframe(filtered_df.describe().round(2), use_container_width=True)
        
    with col_stat2:
        st.markdown("##### Missing & Duplicate Values Report")
        missing_df = pd.DataFrame([
            {"Column": col, "Missing Count": meta["count"], "Missing (%)": f"{meta['percentage']}%"}
            for col, meta in inspection["missing_per_column"].items()
        ])
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
        st.write(f"- **Total Missing Cells in Raw Data:** {inspection['missing_total']}")
        st.write(f"- **Exact Duplicate Rows Detected:** {inspection['duplicate_rows']}")

# -------------------------------------------------------------
# TAB 5: SYSTEM ARCHITECTURE & VIVA GUIDE
# -------------------------------------------------------------
with tab_guide:
    st.subheader("📖 System Architecture & Viva Defense Reference")
    
    st.markdown(
        """
        ### 1. Project Abstract & Objectives
        **StudentPulse** is a lightweight, responsive academic analytics application built with **Streamlit**, **Pandas**, and **Plotly**, packaged inside an isolated **Docker** container. It allows educators and departmental heads to dynamically inspect student performance, subject mastery, and attendance trends without requiring local Python environments or complex database configuration.

        ### 2. Core Architectural Principles
        - **Decoupled Architecture:** Analytical math and validation logic are isolated in `src/analytics.py` and `src/data_validation.py`, allowing complete independent testing using `pytest`.
        - **Non-Destructive Processing:** Ingestion and cleaning functions never alter or corrupt the user's raw uploaded dataset in-place.
        - **Defensive Data Handling:** Automated column role heuristics adapt to varying institutional CSV formats (marks, scores, attendance rates, roll numbers).
        - **Transparent Heuristics:** No opaque machine learning claims or biased predictions. Support triggers are explicit, configurable pedagogical rules.

        ### 3. Docker Containerization Concepts (Viva Essentials)
        - **Image vs. Container:** The Dockerfile specifies an immutable blueprint (the image). A container is a lightweight, running instance of that image with its own filesystem and isolated network namespace.
        - **Port Mapping (`-p 8501:8501`):** Maps port 8501 on the host machine to port 8501 inside the container, directing browser traffic to Streamlit's webserver.
        - **Base Image:** Built on `python:3.11-slim` for minimal container footprint, reduced attack surface, and rapid startup.
        - **Health Check Endpoint (`/_stcore/health`):** Streamlit provides a native lightweight health status endpoint polled by Docker daemon to verify service readiness.

        ### 4. Technical Credits & Repository
        - **Developer:** Daniel Richard Xavier
        - **Repository:** [https://github.com/drx2k06/miniproject7.git](https://github.com/drx2k06/miniproject7.git)
        - **License:** Open Academic Mini-Project
        """
    )
