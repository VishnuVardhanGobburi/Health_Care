"""Anomalies: Flag, Don't Delete."""
import streamlit as st
import pandas as pd

from src.data import load_medical_insurance
from src.anomaly import flag_anomalies_charges
from src.viz import anomaly_scatter, anomaly_histogram_overlay


@st.cache_data
def _load_data():
    return load_medical_insurance()


def _smoker_label(s: pd.Series) -> pd.Series:
    """Normalize to Yes/No for display."""
    return s.astype(str).str.lower().str.strip().map(
        lambda x: "Yes" if x in ("yes", "true", "1") else "No"
    )


def _bmi_bucket(bmi: float) -> str:
    if pd.isna(bmi):
        return "Unknown"
    if bmi < 25:
        return "<25"
    if bmi < 30:
        return "25–29.9"
    if bmi < 35:
        return "30–34.9"
    return "35+"


def render():
    st.title("High-Charge Claim Review")
    st.markdown(
        "The purpose of this page is to identify and flag these high-charge claims for review. These records often represent legitimate but extreme cases and can be important for understanding risk and monitoring cost drivers.")
    try:
        df = _load_data()
    except Exception as e:
        st.error(str(e))
        return
    method = st.radio("Anomaly rule", ["percentile", "iqr"], format_func=lambda x: "Above 95th Percentile (percentile)" if x == "percentile" else "IQR upper fence", horizontal=True)
    if method == "percentile":
        p = st.slider("Percentile threshold", 90, 99, 95)
        mask, flagged = flag_anomalies_charges(df, method="percentile", percentile=float(p))
    else:
        mask, flagged = flag_anomalies_charges(df, method="iqr", iqr_mult=1.5)

    st.subheader("Scatter: flagged vs typical")
    st.plotly_chart(anomaly_scatter(df, mask, x_col="age", y_col="charges"), use_container_width=True)
    #st.subheader("Histogram with anomaly overlay")
    #st.plotly_chart(anomaly_histogram_overlay(df, mask, col="charges"), use_container_width=True)

    # Age cutoff: median age of full dataset (simple and explainable)
    age_cutoff = float(df["age"].median())
    n_flagged = len(flagged)
    if n_flagged == 0:
        st.info("No records are currently flagged for the selected rule.")
        # st.markdown(
        #     "**Why we keep anomalies:** Deleting them would bias summaries and hide operational risk. "
        #     "Insurers can use these flags for manual review, case management, or monitoring dashboards."
        # )
        return

    st.subheader("Flagged Claims Review Summary")
    flagged_copy = flagged.copy()
    flagged_copy["smoker_label"] = _smoker_label(flagged_copy["smoker"])

    # Build summary dataframes
    smoker_counts = flagged_copy["smoker_label"].value_counts().reindex(["Yes", "No"], fill_value=0)
    smoker_pct = (100 * smoker_counts / n_flagged).round(1)
    df_smoker = pd.DataFrame({"Smoking": smoker_counts.index, "Count": smoker_counts.values, "% of flagged": smoker_pct.values})

    below = (flagged_copy["age"] < age_cutoff).sum()
    above = (flagged_copy["age"] >= age_cutoff).sum()
    df_age = pd.DataFrame({
        "Category": [f"Age < {age_cutoff:.0f}", f"Age ≥ {age_cutoff:.0f}"],
        "Count": [below, above],
        "% of flagged": [round(100 * below / n_flagged, 1), round(100 * above / n_flagged, 1)]
    })

    flagged_copy["bmi_bucket"] = flagged_copy["bmi"].map(_bmi_bucket)
    bmi_order = ["<25", "25–29.9", "30–34.9", "35+"]
    bmi_counts = flagged_copy["bmi_bucket"].value_counts().reindex(bmi_order, fill_value=0)
    bmi_pct = (100 * bmi_counts / n_flagged).round(1)
    df_bmi = pd.DataFrame({"BMI": bmi_counts.index, "Count": bmi_counts.values, "% of flagged": bmi_pct.values})

    region_counts = flagged_copy["region"].astype(str).str.strip().value_counts()
    region_pct = (100 * region_counts / n_flagged).round(1)
    df_region = pd.DataFrame({"Region": region_counts.index, "Count": region_counts.values, "% of flagged": region_pct.values})

    children_counts = flagged_copy["children"].astype(int).value_counts().sort_index()
    children_pct = (100 * children_counts / n_flagged).round(1)
    df_children = pd.DataFrame({"Children": children_counts.index, "Count": children_counts.values, "% of flagged": children_pct.values})

    # Row 1: Smoking, Age, BMI
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        st.caption("Smoking status (flagged subset)")
        st.dataframe(df_smoker, use_container_width=True, hide_index=True)
    with r1_c2:
        st.caption(f"Age (cutoff = {age_cutoff:.0f}, median age of full dataset)")
        st.dataframe(df_age, use_container_width=True, hide_index=True)
    with r1_c3:
        st.caption("BMI category")
        st.dataframe(df_bmi, use_container_width=True, hide_index=True)

    # Row 2: Region, Children
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        st.caption("Region")
        st.dataframe(df_region, use_container_width=True, hide_index=True)
    with r2_c2:
        st.caption("Number of children")
        st.dataframe(df_children, use_container_width=True, hide_index=True)

    # PART B — Unexpected flagged records for review (at least 2 low-risk conditions)
    st.subheader("Records to Review: Unexpected Profiles")
    smoker_no = (flagged_copy["smoker_label"] == "No").astype(int)
    age_below = (flagged_copy["age"] < age_cutoff).astype(int)
    bmi_below_30 = (flagged_copy["bmi"] < 30).astype(int)
    condition_count = smoker_no + age_below + bmi_below_30
    review_mask = condition_count >= 2
    review_cases = flagged_copy.loc[review_mask].copy()
    review_cases = review_cases.sort_values("charges", ascending=False).head(25)
    display_cols = [c for c in review_cases.columns if c not in ("smoker_label", "bmi_bucket", "reason", "anomaly_rule")]
    if review_cases.empty:
        st.info(
            "No flagged records meet the unexpected profile criteria in this dataset. "
            "Criteria: at least two of the following must hold — non-smoker; age below median (age < {:.0f}); BMI < 30.".format(age_cutoff)
        )
    else:
        st.dataframe(review_cases[display_cols], use_container_width=True, hide_index=True)
        st.markdown("These flagged records matched the review criteria (at least two of: non-smoker; age below median; BMI &lt; 30).")

    # st.markdown(
    #     "**Why we keep anomalies:** Deleting them would bias summaries and hide operational risk. "
    #     "Insurers can use these flags for manual review, case management, or monitoring dashboards."
    # )


if __name__ in ("__main__", "__page__"):
    render()
