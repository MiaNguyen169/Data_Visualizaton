import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
import textwrap
import plotly.express as px


st.set_page_config(
    page_title = "PISA Dashboard",
    layout = "wide",
)

st.title("Why are PISA scores falling?")
st.caption("PISA 2006-2025. 15-year-old students. source: PISA 2025 volume I, Annex B1")

#Load data
DATA_DIR = Path(__file__).parent / "Data_exploration"


@st.cache_data
def load_data():
    science_long = pd.read_csv(DATA_DIR / "science_long.csv")
    oecd = pd.read_csv(DATA_DIR / "science_oecd_averages.csv")
    merged = pd.read_csv(DATA_DIR / "merged_pisa_data.csv")
    inequality_oecd = pd.read_csv(DATA_DIR / "inequality_oecd.csv")
    relationship = pd.read_csv(
        DATA_DIR / "resource_science_relationship_clean.csv"
    ) 
    return science_long, oecd, merged, inequality_oecd, relationship

science_long, oecd, merged, inequality_oecd, relationship = load_data()

#sidebar selection
st.sidebar.header("Filter")
all_countries = sorted(merged["Country"].unique())

selected = st.sidebar.multiselect (
    "Select countries (max 4)",
    options = all_countries,
    default = ["Australia", "Canada", "Finland", "Germany"],
    max_selections = 4
)

# Pallet 
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
OECD_COLOR = "#8a8983"

if "colors" not in st.session_state:
    st.session_state["colors"] = {}

colors = st.session_state["colors"]

# Free colours of countries that were removed
for country in list(colors):
    if country not in selected:
        del colors[country]

# Give new countries the first unused colour
for country in selected:
    if country not in colors:
        used = set(colors.values())
        colors[country] = next(c for c in PALETTE if c not in used)
        
        
# KPI Line
oecd23 = oecd[oecd["Country"] == "OECD average-23"].iloc[0]

both = merged.dropna(subset=["2018", "2025"])
n_lower = (both["2025"] < both["2018"]).sum()

col1, col2, col3 = st.columns(3)

col1.metric(
    "OECD average science, 2025",
    f"{oecd23['2025']:.0f}",
    f"{oecd23['2025'] - oecd23['2006']:+.0f} since 2006"
)
col2.metric(
    "Change since 2022",
    f"{oecd23['2025'] - oecd23['2022']:+.0f} points"
)
col3.metric(
    "Systems scoring lower than in 2018",
    f"{n_lower} of {len(both)}"
)

# Tab and Line chart in overview 
tab_trend, tab_q1, tab_q2, tab_q3, tab_appendix = st.tabs([
    "Trend", "Question01 - AI", "Question02 - Teaching", "Question03 - Economic factors", "Appendix"
])

with tab_trend:
    show_all = st.checkbox("Show all countries in background")

    fig = go.Figure()
    years = [2006, 2009, 2012, 2015, 2018, 2022, 2025]

    # Background: every country in light grey
    if show_all:
        for country, d in science_long.groupby("Country"):
            fig.add_trace(go.Scatter(
                x=d["Year"], y=d["Science_Score"],
                mode="lines",
                line=dict(color="#d3d1c7", width=1),
                hoverinfo="skip",
                showlegend=False
            ))

    # OECD average as the reference line
    fig.add_trace(go.Scatter(
        x=years,
        y=[oecd23[str(y)] for y in years],
        mode="lines+markers",
        name="OECD average (23)",
        line=dict(color=OECD_COLOR, width=3)
    ))

    # Selected countries
    for country in selected:
        d = science_long[science_long["Country"] == country]
        fig.add_trace(go.Scatter(
            x=d["Year"], y=d["Science_Score"],
            mode="lines+markers",
            name=country,
            line=dict(color=colors[country], width=2),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="Mean science score by PISA cycle",
        xaxis=dict(tickvals=years, title="PISA cycle"),
        yaxis=dict(title="Mean science score"),
        hovermode="x unified",
        height=480
    )

    st.plotly_chart(fig, width="stretch")
    st.caption("Source: PISA 2025, Annex B1, Table I.B1.2a.36")

with tab_q2:
    st.header("Has the Quality of Teaching Declined?")
    st.write("Exploring changes in reported teacher support between 2015 and 2025 and its association with science performance.")

  
    teacher_data = pd.read_csv(DATA_DIR / "teacher_support_clean.csv")
    science_data = pd.read_csv(DATA_DIR / "science_performance_clean.csv")

    # First Visualisation: Changes in Teacher Support
    st.subheader("Changes in Teacher Support (2015–2025)")

    # Countries sorted by change in teacher support
    teacher_sorted = teacher_data.sort_values("Change")

    # five largest decreases and increases
    largest_decreases = teacher_sorted.head(5)["Country"].tolist()
    largest_increases = teacher_sorted.tail(5)["Country"].tolist()

    default_countries = largest_decreases + largest_increases

    # countries
    teacher_countries = sorted(teacher_data["Country"].unique())

    # choose countries
    selected_teacher_countries = st.multiselect(
        "Select countries to compare:",
        options=teacher_countries,
        default=default_countries,
        key="teacher_support_countries"
    )

    # country filter
    teacher_filtered = teacher_data[
        teacher_data["Country"].isin(selected_teacher_countries)
    ]

    teacher_filtered = teacher_filtered.sort_values("Change")

    # teacher support bar chart
    fig_teacher = px.bar(
        teacher_filtered,
        x="Change",
        y="Country",
        orientation="h",
        color="Change",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title=None,
        labels={
            "Change": "Change in Mean Teacher Support Index",
            "Country": "Country"
        },
        hover_data={
            "Mean_Index_2015": ":.3f",
            "Mean_Index_2025": ":.3f",
            "Change": ":.3f"
        }
    )

    fig_teacher.update_layout(
        template="plotly_dark",
        height=550,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=20, t=20, b=20)
    )

    # Display
    st.plotly_chart(fig_teacher, use_container_width=True)

    st.caption(
        "Between 2015 and 2025, reported teacher support increased "
        "in 38 countries and decreased in 26 countries. "
        "Teacher support is based on students' reports and does not "
        "represent overall teaching quality."
    )

    # Second Visualisation: Teacher Support and Science Performance
    st.divider()

    st.subheader("Teacher Support and Science Performance")

    st.write(
        "This visualisation compares the association between teacher support "
        "and science performance before and after accounting for "
        "students' and schools' socioeconomic characteristics."
    )

    # countries
    science_countries = sorted(science_data["Country"].unique())

    # Interactive  
    with st.expander("Highlight countries", expanded=False):

        select_all_science = st.checkbox(
            "Select All Countries",
            value=False
        )

        if select_all_science:
            selected_science_countries = science_countries
        else:
            selected_science_countries = st.multiselect(
                "Select countries to highlight:",
                options=science_countries,
                default=[],
                key="science_performance_countries"
            )

    # filter by countries
    science_highlighted = science_data[
        science_data["Country"].isin(selected_science_countries)
    ]

    # scatter plot
    fig_science = px.scatter(
        science_data,
        x="Score_Before",
        y="Score_After",
        hover_name="Country",
        hover_data={
            "Score_Before": ":.2f",
            "Score_After": ":.2f",
            "Explained_Variance": ":.2f"
        },
        title=None,
        labels={
            "Score_Before": "Before Socioeconomic Adjustment (Score Points)",
            "Score_After": "After Socioeconomic Adjustment (Score Points)",
            "Explained_Variance": "Explained Variance (%)"
        }
    )

    # display all countries 
    fig_science.update_traces(
        marker=dict(
            size=9,
            color="lightgrey",
            opacity=0.7
        )
    )

    # highlighted selected countries in orange
    if not science_highlighted.empty:

        fig_highlight = px.scatter(
            science_highlighted,
            x="Score_Before",
            y="Score_After",
            hover_name="Country",
            hover_data={
                "Score_Before": ":.2f",
                "Score_After": ":.2f",
                "Explained_Variance": ":.2f"
            }
        )

        fig_highlight.update_traces(
            marker=dict(
                size=14,
                color="orange",
                opacity=1
            )
        )

        for trace in fig_highlight.data:
            fig_science.add_trace(trace)

    # reference line 
    fig_science.add_shape(
        type="line",
        x0=-15,
        y0=-15,
        x1=20,
        y1=20,
        line=dict(
            color="red",
            dash="dash",
            width=2
        )
    )

    # formatting
    fig_science.update_layout(
        template="plotly_dark",
        height=550,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig_science, use_container_width=True)

    st.caption(
        "Each point represents a country. "
        "The red dashed line shows where estimates before and after "
        "socioeconomic adjustment are equal. Points above the line "
        "have higher adjusted estimates, while points below have lower estimates. "
        "These associations do not establish causation. "
        "Source: PISA 2025, Annex B1, Table I.B1.4.117."
    )
# Question 3
   
with tab_q3:
    st.header("Do economic factors explain lower science scores?")

    # ---------- Chart 1: resource gap vs science 2025 (main chart) ----------
    gap = merged.dropna(subset=["Socioeconomic_Gap_2025", "2025"]).copy()
    gap["Caution"] = (
        gap["Disadvantaged_2025_Caution"].astype(bool)
        | gap["Advantaged_2025_Caution"].astype(bool)
    )

    x = gap["Socioeconomic_Gap_2025"]
    y = gap["2025"]
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)

    fig = go.Figure()

    # All countries in grey
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="markers",
        name="Other countries",
        marker=dict(
            color="#b4b2a9",
            size=9,
            symbol=np.where(gap["Caution"], "circle-open", "circle")
        ),
        customdata=gap["Country"],
        hovertemplate="%{customdata}<br>Gap: %{x:.1f} pp<br>Science: %{y:.0f}<extra></extra>"
    ))

    # Selected countries in their own colour, with a label
    for country in selected:
        row = gap[gap["Country"] == country]
        if row.empty:
            continue
        fig.add_trace(go.Scatter(
            x=row["Socioeconomic_Gap_2025"], y=row["2025"],
            mode="markers+text",
            name=country,
            text=[country],
            textposition="top center",
            marker=dict(color=colors[country], size=13),
            hovertemplate=country + "<br>Gap: %{x:.1f} pp<br>Science: %{y:.0f}<extra></extra>"
        ))

    fig.add_trace(go.Scatter(
        x=x_line, y=m * x_line + b,
        mode="lines",
        name="Linear trend",
        line=dict(color= "#C65A49", width=2),
        hoverinfo="skip"
    ))

    r = x.corr(y)
    rho = x.corr(y, method="spearman")
    fig.add_annotation(
        xref="paper", yref="paper", x=0.01, y=0.99,
        text=f"Pearson r = {r:.2f}<br>Spearman = {rho:.2f}<br>n = {len(gap)}",
        showarrow=False, align="left"
    )

    fig.update_layout(
        title="Bigger resource gap between school types, lower science scores",
        xaxis_title="Digital resource shortage gap, disadvantaged − advantaged (pp)",
        yaxis_title="Mean science score (2025)",
        height=520
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Hollow circles: value flagged for caution by PISA. "
        "Source: PISA 2025, Annex B1, Tables I.B1.4.7 and I.B1.2a.36"
    )

    # ---------- Chart 2: disadvantaged vs advantaged schools ----------
    bar_data = merged[merged["Country"].isin(selected)].copy()
    bar_data = pd.concat([bar_data, inequality_oecd])
    bar_data = bar_data.dropna(subset=["Disadvantaged_2025", "Advantaged_2025"])

    fig = go.Figure()
    for col, label, color in [
        ("Disadvantaged_2025", "Disadvantaged schools", "#C65A49"),
        ("Advantaged_2025", "Advantaged schools", "#348C87"),
    ]:
        flagged = bar_data[col + "_Caution"].astype(bool)
        fig.add_trace(go.Bar(
            x=bar_data["Country"],
            y=bar_data[col],
            name=label,
            showlegend=False,
            marker=dict(
                color=color,
                # overlay: draw white stripes on top of the bar colour
                pattern=dict(
                    shape=np.where(flagged, "/", ""),
                    fgcolor="white",
                    fillmode="overlay"
                )
            ),
            text=bar_data[col].round(1),
            textposition="outside",
            hovertemplate="%{x}<br>" + label + ": %{y:.1f}%<extra></extra>"
        ))

        # Legend-only entry without stripes
        fig.add_trace(go.Bar(
            x=[None], y=[None], name=label, marker_color=color
        ))

    fig.add_trace(go.Bar(
        x=[None], y=[None],
        name="PISA caution flag",
        marker=dict(
            color="#b4b2a9",
            pattern=dict(shape="/", fgcolor="white", fillmode="overlay")
        )
    ))

    fig.update_layout(
        title="Digital resource shortages by school type (2025)",
        yaxis_title="Students in schools reporting shortages (%)",
        barmode="group",
        height=450
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Hatched bars: flagged for caution by PISA. Source: Table I.B1.4.7")

    # ---------- Chart 3: resource correlations, r vs partial r ----------
    resource_categories = [
        "Shortage of material resources",
        "Digital devices",
        "School's preparedness for digital learning",
        "Study help at school"
    ]
    corr = relationship[
        relationship["Resource_Category"].isin(resource_categories)
    ].copy()
    corr["Absolute_R"] = corr["Science_Correlation"].abs()
    corr = corr.nlargest(10, "Absolute_R").sort_values("Science_Correlation")
    corr["Label"] = corr["Resource_Indicator"].apply(
        lambda s: "<br>".join(textwrap.wrap(s, width=55))
    )
    fig = go.Figure()

    # Partial r first: in horizontal grouped bars Plotly draws the
    # first trace at the bottom, so r ends up on top like the notebook
    fig.add_trace(go.Bar(
        y=corr["Label"], x=corr["Science_Partial_Correlation"],
        orientation="h", name="Partial r (controlling for GDP per capita)",
        marker_color=np.where(corr["Significant_Partial_R"], "#3B82B8", "#A9C9E3"),
        text=corr["Science_Partial_Correlation"],
        texttemplate="%{text:+.2f}",
        textposition="outside",
        hovertemplate="Partial r = %{x:.2f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=corr["Label"], x=corr["Science_Correlation"],
        orientation="h", name="r",
        marker_color="#B8C2CC",
        text=corr["Science_Correlation"],
        texttemplate="%{text:+.2f}",
        textposition="outside",
        hovertemplate="r = %{x:.2f}<extra></extra>"
    ))

    # Legend-only entry for non-significant partial r
    fig.add_trace(go.Bar(
        x=[None], y=[None],
        name="Partial r, not significant (p ≥ 0.05)",
        marker_color="#A9C9E3"
    ))

    # Vertical line at 0
    fig.add_vline(x=0, line_color="#8a8983", line_width=1.5)

    fig.update_layout(
        title="Resource correlations shrink after accounting for GDP",
        xaxis=dict(
            title="Correlation with science (OECD countries)",
            range=[-1, 1],
            showline=True,          # x-axis line at the bottom
            linecolor="#8a8983",
            dtick=0.25
        ),
        barmode="group",
        height=750,
        legend=dict(traceorder="reversed")
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Source: PISA 2025, Annex B1, Table I.B1.4.187")
    
    # ---------- Chart 4: change vs change (appendix) ----------
    with st.expander("Appendix: change in shortages vs change in science (2022–2025)"):
        change = merged.dropna(
            subset=["Digital_Lack_Change", "Science_Change_2022_2025"]
        ).copy()

        drop_outliers = st.checkbox("Exclude Uzbekistan and Albania (outliers)")
        if drop_outliers:
            change = change[~change["Country"].isin(["Uzbekistan", "Albania"])]
            
        x = change["Digital_Lack_Change"]
        y = change["Science_Change_2022_2025"]

        # Linear trend
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers",
            name="Countries",
            marker=dict(color="#3B82B8", size=9),
            customdata=change["Country"],
            hovertemplate="%{customdata}<br>Shortage change: %{x:.1f} pp<br>Score change: %{y:.0f}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=x_line, y=m * x_line + b,
            mode="lines",
            name="Linear trend",
            line=dict(color="#C65A49", width=2),
            hoverinfo="skip"
        ))
        fig.add_hline(y=0, line_color="#b4b2a9")
        fig.add_vline(x=0, line_color="#b4b2a9")
        fig.add_annotation(
            xref="paper", yref="paper", x=0.01, y=0.99,
            text=(
                f"Pearson r = {x.corr(y):.2f}<br>"
                f"Spearman = {x.corr(y, method='spearman'):.2f}<br>"
                f"n = {len(change)}"
            ),
            showarrow=False, align="left"
        )
        fig.update_layout(
            xaxis_title="Change in digital resource shortages (pp)",
            yaxis_title="Change in mean science score",
            height=450
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("The correlation depends on a few outliers: tick the box to see r drop.")
        
