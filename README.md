

# Airline Route Profitability & Optimization System

## Project Overview

This project presents a data-driven system for analyzing airline route performance and supporting strategic decision-making. It integrates exploratory data analysis, business logic, and machine learning to classify airline routes into actionable categories.

The system is designed to answer a key business question:

**Which airline routes should be expanded, maintained, optimized, or discontinued?**

By combining financial, operational, and demand-based features, the project simulates real-world airline decision-making and demonstrates how data science can be used to optimize network performance.

---

## Business Objective

Airlines operate in a highly competitive environment where route-level profitability is critical. Poorly performing routes can lead to significant losses, while high-performing routes present opportunities for expansion.

The objective of this project is to:

- Evaluate route-level financial performance  
- Identify inefficiencies in cost and pricing  
- Classify routes into strategic decision categories  
- Build predictive models to automate decision-making  
- Provide insights for improving airline network efficiency  

---

## Dataset Description

The dataset contains 7,974 route-level observations with 33 variables, including:

### Operational Features
- Flight Hours  
- Aircraft Type & Capacity  
- Load Factor  
- Route Category  

### Demand Features
- Passenger Count  
- Demand Level  
- Seasonality  

### Revenue Components
- Ticket Revenue  
- Ancillary Revenue  
- Total Revenue  

### Cost Components
- Fuel Cost  
- Maintenance Cost  
- Crew Cost  
- Sales & Distribution Cost  
- Overhead Costs  

### Financial Outputs
- Total Cost  
- Profit  
- Profit Margin  

Each row represents a single route instance, enabling detailed analysis at a granular level.

---

## Data Validation & Preprocessing

Before analysis and modeling:

- No duplicate records were found  
- Profit consistency was verified (Profit = Revenue - Cost)  
- Load factor values were validated (between 0 and 1)  
- Passenger counts did not exceed aircraft capacity  
- Missing values were handled using targeted imputation  

---

## Exploratory Data Analysis

### Profit vs Load Factor

![Profit vs Load Factor](images/profit_vs_load.png)

Higher load factors generally lead to higher profitability, although cost structure plays a significant role in determining final outcomes.

---

### Profit vs Flight Duration

![Profit vs Flight Duration](images/profit_vs_duration.png)

Mid-range flights tend to be more profitable, while long-haul routes often face higher operational costs.

---

### Profit Distribution

![Profit Distribution](images/profit_distribution.png)

The distribution shows a mix of profitable and loss-making routes, with a small subset generating very high profits.

---

### Cost Structure Analysis

![Cost Breakdown](images/cost_breakdown.png)

Fuel cost is the largest expense, followed by sales distribution and overhead costs, indicating the importance of both operational efficiency and pricing strategy.

---

## Route Decision Engine

A rule-based classification system was built using:

- Profit  
- Profit Margin  
- Load Factor  

Each route is categorized into:

| Category   | Description |
|------------|------------|
| Expand     | High-performing routes with strong demand |
| Maintain   | Stable routes with consistent performance |
| Optimize   | Profitable but inefficient routes |
| Drop       | Loss-making routes |

---

### Route Decision Distribution

![Route Decision Distribution](images/decision_distribution.png)

A large portion of routes require optimization, while a significant number are loss-making. Only a small subset qualifies for expansion.

---

## Machine Learning Models

Three models were developed to predict route decisions:

### Model 1: With Revenue Variables
- Uses full financial and operational data  
- Accuracy: ~88%  

---

### Model 2: Without Revenue Variables
- Uses operational and cost features only  
- Accuracy: ~84%  

---

### Model 3: Pre-Operational Model
- Uses only demand and route features  
- Accuracy: ~72%  

---

## Model Comparison

![Model Comparison](images/model_comparison.png)

Model performance decreases as financial information is removed, but remains reasonably strong, indicating that decisions can be predicted early.

---

## Confusion Matrix

![Confusion Matrix](images/confusion_matrix.png)

The model performs well across all categories, with particularly strong results for identifying loss-making and optimization routes.

---

## Feature Importance

![Feature Importance](images/feature_importance.png)

Key drivers of route decisions include:

- Load Factor  
- Ticket Revenue  
- Flight Hours  
- Passenger Volume  

Without revenue variables, cost and operational factors become more dominant.

---

## Business Insights

### 1. Optimization Opportunity
A large portion of routes are profitable but inefficient, indicating strong potential for improvement.

### 2. Structural Losses
Many routes consistently generate losses and may need to be discontinued or redesigned.

### 3. Limited Expansion Opportunities
Only a small percentage of routes qualify for expansion, suggesting profitability is concentrated.

### 4. Dynamic Route Behavior
Route performance varies over time, indicating that decisions should be dynamic rather than static.

### 5. Strategic Implication
Airline decision-making should incorporate both current performance and future projections.

---

## System Design Perspective

The project separates modeling into three levels:

1. Full financial model (post-performance analysis)  
2. Operational model (without revenue)  
3. Pre-operational model (early-stage prediction)  

This reflects real-world decision-making workflows.

---

## Limitations

- The dataset is simulated and may not capture full real-world complexity  
- External factors such as competition and weather are not included  
- Time-based dynamics are simplified  

---

## Conclusion

This project demonstrates how data science can support business decision-making by combining:

- Exploratory data analysis  
- Business rule-based systems  
- Machine learning models  

The results show that route profitability depends on multiple factors, including demand, cost structure, and operational efficiency.

Importantly, the project highlights that meaningful decisions can be predicted even before full financial outcomes are available, making it valuable for strategic planning.

---

## Author

Chetan  
MSc Modeling, Data & Predictions (University of Alberta)
