# Feature Store + Training Pipeline
### Customer Churn Prediction · Databricks Free Edition · MLflow 3 · XGBoost
 
> Predicts whether a customer will purchase again in the next 90 days using RFM features derived from transactional data — built end-to-end on a free, serverless stack.
 
---
 
## Why this project
 
Most data engineering portfolios stop at the Gold layer. This project continues past it: from a Delta table to a registered, versioned ML model in Unity Catalog — covering the feature-to-model handoff that ML engineer interviews focus on.
 
---

## Dataset Source

Dataset --- UCI Online Retail II
Source -- https://archive.ics.uci.edu/dataset/502/online+retail+ii

---
 
## Architecture
 
```
Raw XLSX
    │
    ▼
[Bronze Layer]  ──  Delta table · raw ingestion · no transformations
    │
    ▼
[Silver Layer]  ──  Cleaned · nulls dropped · returns filtered · revenue computed
    │
    ▼
[Gold Layer]    ──  Customer-level aggregation · total orders · total revenue · last purchase date
    │
    ▼
[Feature Table] ──  Mosaic AI Feature Engineering · RFM features · Unity Catalog · primary key: customer_id
    │                   recency_days · frequency · monetary · avg_order_value
    │
    ├──── [Label Table] ──  Purchased in next 90 days? (binary) · point-in-time split
    │
    ▼
[Training Set]  ──  FeatureLookup join · training-serving consistency guaranteed
    │
    ▼
[XGBoost Model] ──  MLflow 3 tracked · params + metrics + feature importance logged
    │
    ▼
[Model Registry]──  Unity Catalog · versioned · aliased (Staging / Production)
    │
    ▼
[Batch Inference]── fe.score_batch · features retrieved automatically · predictions → Delta table
```
 
**Data quality gate:** Great Expectations suite runs before training and aborts the run if feature data fails structural or range checks.
 
---
 
## Stack
 
| Layer | Tool | Why |
|---|---|---|
| Compute | Databricks Free Edition (serverless) | No cluster config, no cost, Unity Catalog included |
| Storage | Delta Lake + Unity Catalog Volumes | ACID transactions, lineage, replaces DBFS |
| Feature store | Mosaic AI Feature Engineering | Embeds feature retrieval in the model artifact |
| Experiment tracking | MLflow 3 | Native Databricks integration, model registry |
| Model | XGBoost | Handles class imbalance via `scale_pos_weight`, interpretable |
| Data validation | Great Expectations | Quality gate before training, not after |
| CI | GitHub Actions | Validates feature logic in pure Python on every push |
 
---
 
## Key design decisions
 
**Point-in-time snapshot to prevent label leakage**
Features are computed from transactions strictly *before* `2011-09-01`. Labels are computed from transactions *after* that date. Mixing the two windows would inflate model performance and produce a model that fails in production.
 
**FeatureLookup over manual joins**
`fe.log_model(training_set=training_set)` embeds the feature retrieval logic inside the model artifact. At inference time, `fe.score_batch` reconstructs the same join automatically — no application-side feature engineering required. This eliminates training-serving skew.
 
**scale_pos_weight for class imbalance**
The dataset is naturally imbalanced (~70% non-returning customers). Rather than oversampling (which inflates training set size without adding signal), XGBoost's `scale_pos_weight = negatives / positives` adjusts the loss function directly.
 
**Volumes instead of DBFS**
Databricks Free Edition does not support the legacy `dbfs:/` path. All file I/O uses Unity Catalog Volumes at `/Volumes/workspace/ml_project/...`.
 
---
 
## Results
 
| Metric | Value |
|---|---|
| ROC-AUC (holdout) | ~0.82 |
| Feature importance rank | recency_days > monetary > frequency > avg_order_value |
| Training set size | ~3,400 customers |
| Class split (train) | ~70% no-purchase / 30% purchase |
 
---
 
## Reproduce
 
```bash
# 1. Clone and install
git clone https://github.com/<your-handle>/churn-prediction-mlproject
pip install -r requirements.txt
 
# 2. Run notebooks in order inside Databricks Free Edition
notebooks/01_ingest_bronze_gold.py
notebooks/02_build_feature_table.py
notebooks/03_validate_features.py
notebooks/04_train_model.py
notebooks/05_batch_inference.py
```
 
All notebooks are idempotent — re-running after a compute quota reset produces the same result.
 
---
 
## What I would do differently at production scale
 
- **Online feature store** — serve low-latency features via Redis or DynamoDB for real-time inference instead of batch scoring
- **Kafka-triggered feature updates** — recompute RFM incrementally on each transaction event rather than on a daily schedule
- **Model monitoring** — add Evidently AI to detect feature drift and trigger automatic retraining when RFM distributions shift
- **Canary deployment** — promote model versions from Staging to Production alias only after an A/B evaluation against the incumbent model on a held-out time window
- **Unity Catalog lineage** — tag the feature table with upstream Gold table lineage so any schema change triggers a downstream alert
 
---
 
*Stack versions: Databricks Free Edition (2025) · MLflow 3 · XGBoost 2.x · Great Expectations 1.x · Python 3.11*
