# BDA Assignments — Weekly Business Review (E-commerce Marketplace)

**Student Name:** Sanjayakumar Jeyakumar  
**Roll No:** 46  
**Reg No:** 127003227  
**Topic:** Olist E-commerce Marketplace Weekly Review  
**Date:** October 10, 2026  

---

### 1. Introduction

This report analyzes the Brazilian Olist e-commerce dataset covering orders from late 2016 to mid 2018. During this time, total marketplace sales reached **R$ 13.22 Million**, peaking at **R$ 992.8k** in May 2018. 

However, looking closely at the data shows two big problems:
1. **Very few repeat customers:** Only **3.04%** of customers ever bought more than once. Out of 94,990 eligible buyers, 92,102 (96.96%) placed just one order and never came back.
2. **Delivery delays cause bad reviews:** Even though 92.20% of orders were delivered on time, **36.60% of 1-star reviews were late**. When late, orders were delayed by an average of **12.36 days**.

---

### 2. Data Quality Checks

Before running the analysis, we tested the database tables using automated SQL checks:
- **Critical Checks (Passed):** No duplicate order IDs, no null order IDs, no orders delivered before purchase date, no invalid review scores, and all customer IDs matched customer records.
- **Warning Check (300 Rows):** 300 orders had small payment total differences between item prices and recorded payments. These were kept because vouchers, discounts, and credit card installments explain the differences.

---

### 3. Main Metric and Supporting Metrics

| Metric Type | Metric Name | Value | Why It Matters |
| :--- | :--- | :---: | :--- |
| **Main Metric** | **Total Sales (GMV)** | **R$ 13.22M** | Total price of all items sold, excluding delivery charges and cancelled orders. |
| **Supporting** | **Repeat Purchase Rate** | **3.04%** | Shows if customers come back to buy again. Currently, 97% churn after one order. |
| **Supporting** | **On-Time Delivery Rate** | **92.20%** | Percentage of orders delivered by the estimated promise date. |
| **Supporting** | **Average Delay (When Late)** | **+11.8 days** | How many days late delayed orders arrive. Late orders hurt customer trust. |
| **Supporting** | **Average Review Score** | **4.09 / 5.0** | Average rating given by customers across all reviews. |

---

### 4. Delivery Delays and Customer Reviews

Comparing delivery times with review ratings shows:
- **1-Star Reviews (9,380 orders):** 36.60% arrived late. Total delivery took 21.25 days on average, and late orders were delayed by 12.36 days.
- **5-Star Reviews (56,810 orders):** Only 1.86% arrived late. Total delivery took just 10.63 days.

**Important Note on Causes:**  
Delivery delays are a major reason for bad reviews, but not the only reason. In fact, **63.40% of 1-star reviews arrived on time**. Customer feedback shows that broken products, wrong items sent by sellers, and missing parts also cause many 1-star reviews. Therefore, fixing delivery delays helps, but sellers must also be checked for product quality.

---

### 5. Sales Trends and Top Categories

- **Monthly Sales:** Sales started slowly in late 2016 with 295 test orders (R$ 44.7k). November 2016 had 0 orders due to a system break. Sales grew rapidly in 2017, peaking during Black Friday in November 2017 (R$ 977.7k), and reached R$ 992.8k in May 2018 before leveling off.
- **Top Categories & States:** São Paulo (SP) generates more than 35% of all orders, followed by Rio de Janeiro (RJ) and Minas Gerais (MG). The top categories by sales are `health_beauty` (R$ 1.26M), `watches_gifts` (R$ 1.21M), and `bed_bath_table` (R$ 1.04M).
- **Daily Orders:** Orders averaged around 150–200 per day in 2017–2018, with a peak of 1,141 orders on Black Friday 2017.

---

### 6. Suggestions

1. **Give More Realistic Delivery Dates:** Add extra buffer days to delivery estimates so customers do not consider orders late when minor delays occur.
2. **Enforce 48-Hour Seller Shipping:** Require sellers to pack and hand over packages within 2 days, and open local shipping centers in São Paulo and Rio de Janeiro.
3. **Send 14-Day Follow-Up Coupons:** Email customers 14 days after their order arrives with a 10% discount on popular items (like health and beauty products) to get them to buy a second time.

---

### 7. Limitations

- **Seller vs. Courier Time:** The dataset does not separate how much time the seller took to pack from how long the delivery truck took to drive.
- **No Marketing Costs:** We do not have data on advertising costs, so we cannot calculate customer acquisition cost (CAC).
- **No Return or Refund Records:** The dataset does not show product returns or warranty claims after delivery.
- **No Website Browsing Data:** We cannot see how many people visited the website or abandoned their carts.
