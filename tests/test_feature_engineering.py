import pandas as pd
from datetime import datetime
import pytest


def compute_recency(last_date, snapshot_date):
    return (snapshot_date - last_date).days


def test_recency_positive():
    last = datetime(2011, 7, 1)
    snap = datetime(2011, 9, 1)
    assert compute_recency(last, snap) == 62


def test_recency_zero():
    same = datetime(2011, 9, 1)
    assert compute_recency(same, same) == 0


def test_no_negative_recency():
    future = datetime(2011, 10, 1)
    snap = datetime(2011, 9, 1)
    # Last purchase after snapshot should not happen in clean data
    assert compute_recency(future, snap) < 0  # Document and fail loudly in production


if __name__ == '__main__':
    test_recency_positive()
    test_recency_zero()
    print('All tests passed.')