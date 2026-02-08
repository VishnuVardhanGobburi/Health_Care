"""High-Charge Risk Estimator — exploratory binary classification for high-charge tail."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

from src.data import load_medical_insurance


FEATURE_COLS = ["age", "bmi", "region", "smoker", "children_cat"]
NUMERIC_COLS = ["age", "bmi"]
CAT_COLS = ["region", "smoker", "children_cat"]
RANDOM_STATE = 42
TEST_SIZE = 0.2
PERCENTILE_THRESHOLD = 95  # high-charge = above 95th percentile of charges


@st.cache_data
def _load_and_prepare():
    df = load_medical_insurance()
    threshold = float(df["charges"].quantile(0.95))
    df = df.copy()
    df["HIGH_CHARGE"] = (df["charges"] > threshold).astype(int)
    df["children_cat"] = df["children"].clip(upper=4).astype(int)  # 4+ as single category
    return df, threshold


@st.cache_data
def _get_train_test(df: pd.DataFrame, threshold: float):
    y = df["HIGH_CHARGE"]
    X = df[FEATURE_COLS]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    return X_train, X_test, y_train, y_test


def _fit_models(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series):
    preprocess = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_COLS),
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), CAT_COLS),
        ],
        remainder="passthrough",
    )
    pipe_lr = Pipeline([
        ("preprocess", preprocess),
        ("clf", LogisticRegression(class_weight="balanced", random_state=RANDOM_STATE, max_iter=1000)),
    ])
    pipe_rf = Pipeline([
        ("preprocess", preprocess),
        ("clf", RandomForestClassifier(random_state=RANDOM_STATE, max_depth=8, n_estimators=100)),
    ])
    pipe_lr.fit(X_train, y_train)
    pipe_rf.fit(X_train, y_train)
    ref_proba_lr = pipe_lr.predict_proba(X_test)[:, 1]
    ref_proba_rf = pipe_rf.predict_proba(X_test)[:, 1]
    return pipe_lr, pipe_rf, ref_proba_lr, ref_proba_rf


@st.cache_resource
def _get_fitted_models():
    df, _ = _load_and_prepare()
    X_train, X_test, y_train, y_test = _get_train_test(df, float(df["charges"].quantile(0.95)))
    pipe_lr, pipe_rf, ref_lr, ref_rf = _fit_models(X_train, y_train, X_test, y_test)
    return pipe_lr, pipe_rf, ref_lr, ref_rf, X_test, y_test


def _get_feature_names(pipe: Pipeline):
    ct = pipe.named_steps["preprocess"]
    names = ct.get_feature_names_out()
    return [n.replace("num__", "").replace("cat__", "").replace("_", " ") for n in names]


def _coef_bars(pipe: Pipeline, title: str):
    lr = pipe.named_steps["clf"]
    names = _get_feature_names(pipe)
    coef = lr.coef_[0]
    idx = np.argsort(np.abs(coef))[-15:][::-1]
    names = [names[i] for i in idx]
    coef = coef[idx]
    fig = go.Figure(go.Bar(y=names, x=coef, orientation="h"))
    fig.update_layout(
        title=title,
        xaxis_title="Coefficient magnitude (directional association)",
        yaxis_title="",
        margin=dict(l=180),
        height=400,
    )
    return fig


def _importance_bars(pipe: Pipeline, X_test: pd.DataFrame, y_test: pd.Series, title: str):
    from sklearn.inspection import permutation_importance
    rf = pipe.named_steps["clf"]
    preprocess = pipe.named_steps["preprocess"]
    X_enc = preprocess.transform(X_test)
    names = _get_feature_names(pipe)
    perm = permutation_importance(rf, X_enc, y_test, n_repeats=10, random_state=RANDOM_STATE)
    imp = perm.importances_mean
    idx = np.argsort(imp)[-15:][::-1]
    names = [names[i] for i in idx]
    imp = imp[idx]
    fig = go.Figure(go.Bar(y=names, x=imp, orientation="h"))
    fig.update_layout(
        title=title,
        xaxis_title="Permutation importance (test set)",
        yaxis_title="",
        margin=dict(l=180),
        height=400,
    )
    return fig


def render():
    st.title("High-Charge Risk Estimator")
    st.markdown(
        "This page provides an exploratory estimate of the likelihood that a claim "
        "falls into the high-charge tail of the distribution and it is intended for "
        "risk awareness and monitoring."
    )

    try:
        df, threshold = _load_and_prepare()
    except Exception as e:
        st.error(str(e))
        return

    st.metric("High-charge threshold (95th percentile)", f"${threshold:,.0f}")

    pipe_lr, pipe_rf, ref_proba_lr, ref_proba_rf, X_test, y_test = _get_fitted_models()

    # Model evaluation
    st.subheader("Model evaluation")
    st.caption("Metrics are evaluated on the test set (80/20 stratified split).")
    pred_lr = pipe_lr.predict(X_test)
    proba_lr = pipe_lr.predict_proba(X_test)[:, 1]
    pred_rf = pipe_rf.predict(X_test)
    proba_rf = pipe_rf.predict_proba(X_test)[:, 1]
    eval_df = pd.DataFrame({
        "Metric": ["ROC-AUC", "F1 (high-charge)", "Precision", "Recall"],
        "Logistic Regression": [
            roc_auc_score(y_test, proba_lr),
            f1_score(y_test, pred_lr, pos_label=1),
            precision_score(y_test, pred_lr, pos_label=1, zero_division=0),
            recall_score(y_test, pred_lr, pos_label=1, zero_division=0),
        ],
        "Random Forest": [
            roc_auc_score(y_test, proba_rf),
            f1_score(y_test, pred_rf, pos_label=1),
            precision_score(y_test, pred_rf, pos_label=1, zero_division=0),
            recall_score(y_test, pred_rf, pos_label=1, zero_division=0),
        ],
    })
    st.dataframe(eval_df, use_container_width=True, hide_index=True)
    st.markdown("Both models show strong separation ability, driven by clear risk signals in the data (notably smoking status, age, and BMI). Logistic Regression prioritizes recall, capturing nearly all high-charge claims but with more false positives. Random Forest provides a more balanced trade-off, achieving higher precision and a stronger F1 score.")

    model_choice = st.selectbox(
        "Choose model for prediction:",
        ["Logistic Regression", "Random Forest"],
    )
    pipe = pipe_lr if model_choice == "Logistic Regression" else pipe_rf
    ref_proba = ref_proba_lr if model_choice == "Logistic Regression" else ref_proba_rf

    with st.form("risk_form"):
        st.subheader("Claim profile")
        age = st.slider("Age", 0, 100, 30, key="age")
        if age < 1 or age > 100:
            st.caption("Note: Age outside 1–100 may be unusual for this dataset.")
        region = st.selectbox("Region", ["northeast", "northwest", "southeast", "southwest"], key="region")
        smoker = st.radio("Smoker", ["Yes", "No"], key="smoker")
        children_sel = st.selectbox("Children", [0, 1, 2, 3, "more than 3"], key="children")
        children_val = 4 if children_sel == "more than 3" else int(children_sel)
        bmi = st.number_input("BMI", min_value=5.0, max_value=80.0, value=28.0, step=0.5, key="bmi", help="Typical range in this dataset is approximately 10–60")
        if bmi < 10 or bmi > 60:
            st.caption("Note: BMI outside 10–60 is outside the typical range for this dataset.")
        submitted = st.form_submit_button("Predict Risk")

    if submitted:
        row = pd.DataFrame([{
            "age": age,
            "bmi": bmi,
            "region": region,
            "smoker": smoker.lower(),
            "children_cat": children_val,
        }])
        proba = float(pipe.predict_proba(row)[0, 1])
        risk_pct = (ref_proba < proba).mean() * 100
        if risk_pct >= 95:
            risk_level = "High Risk"
        elif risk_pct >= 50:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"
        st.subheader("Prediction result")
        st.metric("Risk level", risk_level)
        st.metric("Risk percentile", f"{risk_pct:.0f}th percentile")
        st.metric("Predicted probability (high-charge)", f"{proba:.2%}")
        st.markdown(
            "Risk levels are defined using percentiles of the predicted risk score, "
            "indicating how this claim compares to others in the dataset."
        )

    st.subheader("What drives this prediction?")
    if model_choice == "Logistic Regression":
        st.plotly_chart(_coef_bars(pipe, "Top coefficients (Logistic Regression)"), use_container_width=True)
    else:
        st.plotly_chart(_importance_bars(pipe, X_test, y_test, "Top features (Random Forest, permutation importance)"), use_container_width=True)


if __name__ in ("__main__", "__page__"):
    render()
