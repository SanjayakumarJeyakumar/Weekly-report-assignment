# BDA Assignment: Olist E-Commerce Weekly Business Review

**Student Name:** Sanjayakumar Jeyakumar  
**Roll No:** 46  
**Course:** Big Data Analytics (BDA)  
**Database:** PostgreSQL (Supabase)  
**Language:** Python 3.10  

---

## Project Overview

This project analyzes the Brazilian E-Commerce public dataset provided by Olist. The assignment covers:
1. Building an ELT pipeline to process raw transactional data into clean staging tables and an analytical mart (`mart_order_summary`).
2. Running data quality checks for referential integrity, duplicate records, and invalid values.
3. Conducting SQL analysis on revenue growth, customer retention, top categories, and delivery performance.
4. Generating visualizations and a 5-page PDF report.

---

## Project Structure

```
olist-weekly-review/
├── charts/                       # Generated analysis charts
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_delivery_delay_vs_review_score.png
│   ├── 03_repeat_purchase_rate.png
│   └── 04_top_categories_and_rolling_orders.png
├── data/
│   └── raw/                      # Olist CSV dataset files
├── report/
│   └── olist_weekly_business_review.pdf # 5-page assignment report
├── sql/                          # SQL transformation and analysis queries
│   ├── 01_create_staging.sql
│   ├── 02_create_mart.sql
│   ├── 03_data_quality_checks.sql
│   ├── 04_monthly_revenue.sql
│   ├── 05_top_categories_by_state.sql
│   ├── 06_rolling_7_day_orders.sql
│   ├── 07_repeat_purchase_rate.sql
│   └── 08_delivery_delay_vs_reviews.sql
├── src/                          # Python scripts
│   ├── db.py                     # Database connection helper
│   ├── test_connection.py        # Connection test script
│   ├── pipeline.py               # Data pipeline script
│   ├── data_quality.py           # Data quality check runner
│   ├── generate_visualizations.py# Matplotlib chart generator
│   └── generate_pdf_report.py    # ReportLab PDF generator
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## Setup & Execution

### 1. Install Dependencies
```
pip install -r requirements.txt
```

### 2. Configure Database Credentials
Create a `.env` file from `.env.example` with your Supabase credentials:
```
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_SSLMODE=require
```

### 3. Run Pipeline and Generate Deliverables
- **Test database connection:**
  ```
  python src/test_connection.py
  ```

- **Run pipeline and data quality checks:**
  ```
  python src/pipeline.py
  ```

- **Generate charts:**
  ```
  python src/generate_visualizations.py
  ```

- **Generate PDF report:**
  ```
  python src/generate_pdf_report.py
  ```

---

## Summary of Findings

- **Total GMV Revenue:** R$ 13.22M across the operational period, peaking in November 2017 (Black Friday) and May 2018.
- **Repeat Purchase Rate:** 3.04% of customers placed more than one order, showing low retention and high reliance on new customer acquisition.
- **Delivery Reliability:** 92.20% of orders were delivered on time. However, late orders experienced an average delay of +11.8 days.
- **Impact on Customer Reviews:** While late delivery is a strong driver of 1-star reviews (36.6% of 1-star reviews had delayed delivery with an average delay of +12.3 days), 63.4% of 1-star reviews occurred on on-time orders, indicating issues related to product quality or expectations.
