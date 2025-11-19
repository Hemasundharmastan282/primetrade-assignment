 Trader Performance and Market Sentiment Analysis

 Project Overview

This project analyzes the relationship between the Bitcoin Market Sentiment (Fear & Greed Index) and the realized trading performance of accounts on the  decentralized exchange. The objective is to quantify how market emotion affects profitability and to identify hidden patterns that can be translated into smarter trading strategies.

The analysis is executed via a single Python script, Project.py.

 Methodology

The analysis followed a four-step data science process:

Data Ingestion & Cleaning: Loaded and cleaned the transactional Historical Trader Data and the daily Sentiment Dataset. Handled column renaming, date format inconsistencies (DD-MM-YYYY), and missing data (e.g., substituting missing leverage with 0.0).

Aggregation: Grouped the transactional data by Account and Trade_Date to calculate daily performance metrics: total Daily PnL, Num Trades, Avg Leverage, and Win Rate.

Merging: Joined the daily performance data with the daily sentiment classification (Fear, Greed, Neutral, etc.) on the Trade_Date column.

Performance Analysis: Calculated mean and median PnL/Win Rate across each sentiment classification and performed a segmentation to identify Contrarian vs. Herd traders.

 Key Findings

1. Sentiment and Overall Profitability

Analysis shows that aggregate performance is often contrarian to market sentiment, driven by high returns during periods of panic.

Classification

Mean Daily PnL

Median Daily PnL

Mean Win Rate (%)

Fear

$5,328.82

$107.89

36.40

Greed

$3,318.10

$158.21

34.36

Highest Mean PnL was achieved during Fear periods, indicating the highest profitability comes from successfully buying dips or taking short positions into a euphoric market.

The large difference between Mean and Median PnL highlights that a small number of traders drive the majority of the profits during volatile swings.

2. Behavioral Segmentation (Contrarian Alpha)

By calculating the difference in PnL performance during Fear vs. Greed, we identified profitable contrarian behavior.

Top Contrarian Trader Example: Account 0x0833...9012 was, on average, $130,434.95 more profitable on Fear days than on Greed days.

Top Herd Trader Example: Account 0x7274...afbd lost $7,277.47 on Fear days but earned $75,599.22 on Greed days, suggesting significant exposure to panic-driven losses.

 Actionable Trading Strategies

Adopt a 'Buy the Panic' Strategy: Use Fear/Extreme Fear sentiment as a signal to initiate long positions. The data validates the profitability of contrarian moves during market capitulation.

De-Risk During Euphoria: When sentiment enters Greed/Extreme Greed, traders should reduce position sizing and lower leverage, as the overall return potential decreases while risk remains high.

Model Alpha from Contrarians: The trade parameters of the identified Top Contrarian Traders should be extracted and used as features to train automated trading models.

 Setup and Execution

Dependencies

This script requires the following Python libraries:

pandas
numpy
matplotlib
seaborn


How to Run

Place the historical_data.csv and fear_greed_index.csv files into the same directory as Project.py.

Ensure Python and the dependencies are installed.

Execute the script from your terminal:

python Project.py


The script will print the analysis tables to the console and display the PnL and Win Rate box plots.
