# Olist E-Commerce Marketplace: Weekly Business Review (WBR)

An enterprise-grade Data Engineering and Analytics pipeline built on the Brazilian E-Commerce Public Dataset by Olist, deployed on **Supabase PostgreSQL** and orchestrated via **Python 3.10**.

---

## 1. Project Architecture & Repository Layout

```
olist-weekly-review/
├── certs/
│   └── prod-ca-2021.crt          # Official Supabase Root 2021 CA certificate (SSL validation)
├── charts/                       # Generated business visualizations (300 DPI PNG)
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_delivery_delay_vs_review_score.png
│   ├── 03_repeat_purchase_rate.png
│   └── 04_top_categories_and_rolling_orders.png
├── data/
│   └── raw/                      # 9 Olist CSV source datasets
├── report/                       # Executive deliverables
│   ├── vp_executive_memo.md      # One-page executive memorandum for leadership
│   └── olist_weekly_business_review.pdf # Executive 5-page PDF report
├── sql/                          # Modular PostgreSQL transformation & analysis scripts
│   ├── 01_create_staging.sql     # Staging transformations (Cleaned tables)
│   ├── 02_create_mart.sql        # Analysis mart builder (1-to-1 order grain)
│   ├── 03_data_quality_checks.sql# Part B Data Quality test suite (6 checks)
│   ├── 04_monthly_revenue.sql    # Part C1: Monthly GMV & MoM growth (LAG)
│   ├── 05_top_categories_by_state.sql # Part C2: Top categories by state (DENSE_RANK)
│   ├── 06_rolling_7_day_orders.sql    # Part C3: 7-day rolling daily order avg
│   ├── 07_repeat_purchase_rate.sql    # Part C4: Customer retention & repeat rate
│   └── 08_delivery_delay_vs_reviews.sql# Part C5: Delivery delay vs review scores
├── src/                          # Reusable Python modules
│   ├── db.py                     # Safe SQLAlchemy connection pool & SSL config
│   ├── test_connection.py        # Read-only Supabase connectivity test
│   ├── pipeline.py               # Main ELT pipeline orchestrator
│   ├── data_quality.py           # Standalone / integrated DQ test runner
│   ├── generate_visualizations.py# Visual analytics generator (Matplotlib)
│   └── generate_pdf_report.py    # Executive 5-page PDF report compiler
├── .env.example                  # Environment variable reference template
├── .gitignore                    # Excludes .env, caches, and virtual environments
└── requirements.txt              # Pinned Python package dependencies
```

---

## 2. Environment Setup & Windows Configuration

### Prerequisites
- Python 3.10+
- Active Supabase PostgreSQL database project

### Dependencies
Install the required packages. Note: This project uses **`pg8000`** (a 100% pure-Python PostgreSQL DB-API driver) rather than native `psycopg2` binaries, ensuring full compatibility with Windows Application Control / AppLocker environments:

```powershell
pip install -r requirements.txt
```

### Credentials Configuration
Copy `.env.example` to `.env` in the project root:

```powershell
Copy-Item .env.example .env
```

Populate your `.env` with discrete Supabase parameters:
```env
DB_HOST=db.[YOUR-PROJECT-REF].supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_SSLMODE=require
```
*(Note: `.env` is strictly excluded from version control via `.gitignore`)*.

---

## 3. How to Run Each Phase

### Step 1: Verify Database Connectivity (Read-Only)
Inspects PostgreSQL engine version, schema catalog, and existing table row counts:
```powershell
python src/test_connection.py
```

### Step 2: Run the End-to-End ELT Pipeline (Part A & B)
Executes pre-flight CSV validation, candidate staging build, candidate mart build, and the integrated Data Quality suite inside an atomic transaction:
```powershell
python src/pipeline.py
```

### Step 3: Run Standalone Data Quality Checks (Part B)
Executes the 6 quality checks against live data without modifying tables:
```powershell
python src/data_quality.py
```

### Step 4: Run Analytical SQL Queries (Part C)
All queries in `sql/` can be executed directly in the Supabase SQL Editor or tested via Python:
```powershell
python -c "from src.db import get_engine; from sqlalchemy import text; import pandas as pd; print(pd.read_sql(text(open('sql/04_monthly_revenue.sql').read()), get_engine().connect()).head())"
```

### Step 5: Regenerate Visualizations & PDF Report (Part D)
Generate publication-quality charts and compile the executive 5-page PDF report:
```powershell
python src/generate_visualizations.py
python src/generate_pdf_report.py
```
Output files:
- Visualizations: `charts/*.png`
- Executive Memo: `report/vp_executive_memo.md`
- Multi-page PDF Report: `report/olist_weekly_business_review.pdf`

---

## 4. Key Analytical Findings & Business Summary

| Core Dimension | Metric / Metric Finding | Business Interpretation |
| :--- | :---: | :--- |
| **North Star GMV** | **R$ 13.22M Total GMV** | Scaled from pilot (Sep 2016) to peak of R$ 993k/mo (May 2018), stabilizing in Q3 2018. |
| **Buyer Retention** | **3.04% Repeat Purchase Rate** | 92,102 out of 94,990 eligible buyers (96.96%) purchased once and never returned (leaky bucket). |
| **Delivery Reliability** | **92.20% On-Time Delivery Rate** | Overall logistics performance is high, but tail delay severity is extreme (+11.8 days overdue). |
| **Detractor Attribution** | **36.60% of 1-Star Orders Were Late** | Late orders arrived an average of **+12.36 days past promise date** (21.25 days total transit time). |
| **Causation Nuance** | **63.40% of 1-Star Orders Were On-Time** | Proves delivery delay is not the sole cause; product quality, missing parts, and seller misrepresentation drive the remaining detractor volume. |

---

## 5. Security & Safety Principles
- **Idempotency**: All pipeline operations use candidate temporary table validation and atomic transaction swaps. Reruns produce identical results without duplicating data.
- **Credential Hygiene**: Password credentials are URL-encoded in memory, masked in logs, and never committed to Git.
- **Zero Cascading Drops**: Tables are safely preserved using `CREATE TABLE IF NOT EXISTS` and `TRUNCATE` inside transactions.
