# Flipkart_Electronics_Products_Analysis

This is a complete end-to-end data analytics project where I scraped all electronics products listings from **Flipkart** using Python, cleaned and transformed the data in **Power BI**, and created a fully interactive dashboard to analyze brand performance, hardware specs, pricing, ratings and product categories.

The goal? To turn raw e-commerce data into actionable insights and develop a real-world data analytics portfolio project.

---

## 🧰 Tech Stack

| Tool            | Use Case                                  |
|-----------------|--------------------------------------------|
| Python          | Web scraping with `Playwright` |
| pandas          | Structuring and saving the data (CSV)      |
| Power BI        | Data cleaning, modeling, dashboard visuals |
| Power Query     | Data transformation in Power BI            |
| DAX             | KPIs and Top-N logic                       |

---

## 📁 Files in This Repository

FLIPKART_ALL_ELECTRONICS_PRODUCTS_ANALYSIS/
├── All_products_data.py # Python code for scraping Flipkart mobiles
├── products_table.sql # Create table in sql.
├── Flipkart All Electronics Products Dashboard.pdf # PDF of the interactive dashboard
├── README.md # You're reading it.

---

## 🧪 Project Features

### 1. Web Scraping with Python
- Extracted real electronics products listing data from Flipkart pages.
- Captured:
  - product_type
  - Title
  - specifications
  - star_rating
  - ratings_count
  - review_count
  - original_price
  - discounted_price
  - discount_percentage
  - image_url


### 2. Power BI Data Cleaning for Smartphones and Laptops
- Separated composite specs into individual columns (e.g., "8 GB RAM | 128 GB ROM").
- Removed unwanted symbols like "GB", "mAh", "₹".
- Created custom column `Price_Category`:
  - **Budget** (< ₹10,000)
  - **Mid-Range** (₹10K–₹25K)
  - **Expensive** (> ₹25K)

### 3. Dashboard Components
- ✅ KPI Cards (Brands, Revenue, Avg. Price, Units Sold)
- ✅ Top 10 Brands by Revenue
- ✅ Top 10 Models Listed by Brand
- ✅ Top 5 Brands by Units Sold
- ✅ Price Distribution by Category (Pie Chart)
- ✅ Slicers for: Brand, Category, Model ,RAM, ROM, Battery, Processor, Brand, Price_Category
 
---

## 🎯 What I Learned

- Structured web scraping with Python + Playwright
- Cleaning messy e-commerce specs in Power Query
- Creating meaningful KPIs and visuals using DAX
- Designing an interactive dashboard with filters
- Applying real-world business thinking in analytics

---

## 📸 Dashboard Preview

> Click to view  pdf of the dashboard:


---
