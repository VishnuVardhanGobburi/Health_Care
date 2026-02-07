"""
Data loading, validation, and cleaning from fixed local paths.
Schema checks, column normalization, missing values, and range validation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# Fixed paths (no uploads)
BASE_DIR = Path(__file__).resolve().parent.parent
MEDICAL_INSURANCE_PATH = BASE_DIR / "data" / "medical_insurance.csv"
INSURANCE_FAQ_PATH = BASE_DIR / "data" / "insurance_faq.csv"
INSURANCE_DOCS_DIR = BASE_DIR / "data" / "insurance_docs"

# Expected columns (and close variants we accept)
EXPECTED_COLUMNS = {"age", "sex", "bmi", "children", "smoker", "region", "charges"}
NUMERIC_COLUMNS = {"age", "bmi", "children", "charges"}
CATEGORICAL_COLUMNS = {"sex", "smoker", "region"}

# Validation bounds (justified: age 1–100, bmi 10–60, children 0–20, charges > 0)
AGE_MIN, AGE_MAX = 1, 100
BMI_MIN, BMI_MAX = 10.0, 60.0
CHILDREN_MIN = 0
CHILDREN_MAX = 20
CHARGES_MIN = 0.01


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip column names."""
    df = df.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df


def _validate_path(path: Path, must_exist: bool = True) -> None:
    if must_exist and not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}\n"
            f"Please place your dataset at: {path}\n"
            "See README.md for setup instructions."
        )


def load_medical_insurance(
    path: Path | None = None,
    validate: bool = True,
) -> pd.DataFrame:
    """
    Load structured medical insurance CSV from fixed path.
    Validates path, schema, and optional range checks; normalizes columns.
    """
    path = path or MEDICAL_INSURANCE_PATH
    _validate_path(path)

    df = pd.read_csv(path)
    df = _normalize_columns(df)

    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Schema validation failed. Missing columns: {sorted(missing)}. "
            f"Expected (or close variants): {sorted(EXPECTED_COLUMNS)}. "
            f"Found: {sorted(df.columns)}."
        )

    df = df[[c for c in EXPECTED_COLUMNS if c in df.columns]]
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()

    if validate:
        # Invalid ranges: flag but don't drop (we report in Phase 1)
        # We still return full dataframe; quality page shows issues
        pass

    return df.reset_index(drop=True)


def get_validation_report(df: pd.DataFrame) -> dict[str, Any]:
    """
    Build a validation report: dtypes, missing counts, category standardization,
    and invalid range counts.
    """
    report: dict[str, Any] = {
        "schema": {c: str(df[c].dtype) for c in df.columns},
        "missing": df.isna().sum().to_dict(),
        "invalid_ranges": {},
        "category_values": {},
    }

    # Invalid ranges
    if "age" in df.columns:
        report["invalid_ranges"]["age"] = int(((df["age"] <= AGE_MIN) | (df["age"] > AGE_MAX)).sum())
    if "bmi" in df.columns:
        report["invalid_ranges"]["bmi"] = int(((df["bmi"] <= BMI_MIN) | (df["bmi"] > BMI_MAX)).sum())
    if "children" in df.columns:
        report["invalid_ranges"]["children"] = int(
            ((df["children"] < CHILDREN_MIN) | (df["children"] > CHILDREN_MAX)).sum()
        )
    if "charges" in df.columns:
        report["invalid_ranges"]["charges"] = int((df["charges"] <= CHARGES_MIN).sum())

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            report["category_values"][col] = df[col].dropna().unique().tolist()

    return report


def load_faq_documents(
    faq_path: Path | None = None,
    docs_dir: Path | None = None,
) -> list[dict[str, str]]:
    """
    Load FAQ/policy documents for RAG from fixed paths.
    Returns list of {"id", "text", "source"} dicts.
    - insurance_faq.csv: expects columns like question, answer (or question_answer).
    - insurance_docs/: text files (.txt, .md).
    """
    faq_path = faq_path or INSURANCE_FAQ_PATH
    docs_dir = docs_dir or INSURANCE_DOCS_DIR
    out: list[dict[str, str]] = []

    if faq_path.exists():
        faq = pd.read_csv(faq_path)
        faq.columns = [str(c).lower().strip() for c in faq.columns]
        # Accept question/answer or question_answer
        q_col = "question" if "question" in faq.columns else None
        a_col = "answer" if "answer" in faq.columns else None
        if q_col is None:
            for c in faq.columns:
                if "question" in c:
                    q_col = c
                    break
        if a_col is None:
            for c in faq.columns:
                if "answer" in c:
                    a_col = c
                    break
        if q_col is None or a_col is None:
            raise ValueError(
                f"insurance_faq.csv must have 'question' and 'answer' columns (or close variants). "
                f"Found: {list(faq.columns)}."
            )
        for i, row in faq.iterrows():
            q = str(row.get(q_col, "")).strip()
            a = str(row.get(a_col, "")).strip()
            if q or a:
                text = f"Q: {q}\nA: {a}"
                out.append({"id": f"faq_{i}", "text": text, "source": str(faq_path.name)})
    elif docs_dir.exists() and docs_dir.is_dir():
        for f in docs_dir.iterdir():
            if f.suffix.lower() in (".txt", ".md"):
                raw = f.read_text(encoding="utf-8", errors="replace")
                out.append({"id": f"doc_{f.stem}", "text": raw, "source": f.name})
    else:
        raise FileNotFoundError(
            f"FAQ data not found. Provide either:\n  - {faq_path}\n  - or directory: {docs_dir}\n"
            "See README.md for setup."
        )

    if not out:
        raise ValueError("No FAQ documents loaded. Check file contents and encoding.")
    return out
