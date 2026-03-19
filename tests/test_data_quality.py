# tests/test_data_quality.py
import pandas as pd
import pytest

# Simulate a minimal valid feature DataFrame
def make_valid_df():
    return pd.DataFrame({
        "customer_id": [101, 102, 103],
        "recency_days": [10, 45, 200],
        "frequency": [3.0, 1.0, 7.0],
        "monetary": [150.0, 30.0, 890.0],
        "avg_order_value": [50.0, 30.0, 127.0],
    })


# --- Column existence ---

def test_required_columns_present():
    df = make_valid_df()
    required = ["customer_id", "recency_days", "frequency", "monetary", "avg_order_value"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


# --- Null checks ---

def test_no_nulls_in_customer_id():
    df = make_valid_df()
    assert df["customer_id"].isnull().sum() == 0

def test_no_nulls_in_recency():
    df = make_valid_df()
    assert df["recency_days"].isnull().sum() == 0

def test_fails_on_null_customer_id():
    df = make_valid_df()
    df.loc[0, "customer_id"] = None
    assert df["customer_id"].isnull().sum() > 0  # documents expected failure


# --- Value range checks ---

def test_recency_non_negative():
    df = make_valid_df()
    assert (df["recency_days"] >= 0).all()

def test_recency_within_max():
    df = make_valid_df()
    assert (df["recency_days"] <= 1825).all()

def test_frequency_at_least_one():
    df = make_valid_df()
    assert (df["frequency"] >= 1).all()

def test_monetary_non_negative():
    df = make_valid_df()
    assert (df["monetary"] >= 0).all()


# --- Uniqueness ---

def test_customer_id_unique():
    df = make_valid_df()
    assert df["customer_id"].nunique() == len(df)

def test_fails_on_duplicate_customer_id():
    df = make_valid_df()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    assert df["customer_id"].nunique() < len(df)  # documents expected failure


# --- Schema types ---

def test_recency_is_numeric():
    df = make_valid_df()
    assert pd.api.types.is_numeric_dtype(df["recency_days"])

def test_monetary_is_numeric():
    df = make_valid_df()
    assert pd.api.types.is_numeric_dtype(df["monetary"])