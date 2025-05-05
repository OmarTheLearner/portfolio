# ESG Funds Analytics

This project analyzes the performance of ESG (Environmental, Social, and Governance) funds with respect to major stock indices (Dow Jones, S&P 500) and various industry sectors. The analysis includes the comparison of ESG funds with traditional indices, as well as deeper insights into sectoral investment allocations and carbon emissions, helping to understand when ESG funds outperform or underperform and the reasons behind it.

## Overview

The project is based on two datasets:

1. **factsheet.csv**: Contains data about two ESG funds (Narcissus Core Equity Sustainability Fund and Pietro Advisory Sustainable Large Cap ETF), their sectoral allocations, carbon emissions, and other relevant metrics.
2. **performance.csv**: Contains performance data for the major indices (Dow Jones, S&P) and the ESG funds.

The project aims to answer the following questions:
- **When do ESG funds outperform and underperform?**
- **What factors contribute to the performance trends of ESG funds?**
- **Any other related insights from sectoral performance and fund metrics?**

## Dataset

1. **factsheet.csv**:
   - Includes data about ESG funds, major indices, and sectors (e.g., energy, utilities, healthcare, etc.).
   - Key columns include:
     - **Carbon Emissions (Fossil Fuel Reserve Emissions and Carbon to Value Invested)**
     - **P/E Ratio**
     - **Sector Allocations**: Percentage investment in each sector.

2. **performance.csv**:
   - Contains the performance data of ESG funds and indices.
   - Key columns include:
     - **Performance Metrics**: Annual returns for ESG funds, indices, and sectors.

## Analysis

The analysis will include:
- **Outperformance vs. underperformance**: Compare ESG funds' performance against major indices.
- **Sector-based analysis**: Analyze the performance of ESG funds in different industry sectors.
- **Carbon Emissions and Financial Performance**: Investigate correlations between carbon emissions, sectoral exposure, and financial returns.

## Tools & Technologies

- Python
- Pandas (for data manipulation)
- Matplotlib & Seaborn (for visualization)

