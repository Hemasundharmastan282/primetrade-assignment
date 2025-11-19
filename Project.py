import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURATION & FILE PATHS ---
# Using raw strings (r"...") for robust file path handling on Windows.
TRADER_DATA_FILE = r"C:\Users\khema\OneDrive\Desktop\primetrade.ai\historical_data.csv"
SENTIMENT_DATA_FILE = r"C:\Users\khema\OneDrive\Desktop\primetrade.ai\fear_greed_index.csv"

# Defining key column names based on dataset inspection.
COL_TIME = 'Timestamp IST'
COL_ACCOUNT = 'Account'
COL_PNL = 'Closed PnL'
COL_LEVERAGE = 'leverage' # Handled gracefully if missing.

# DATA LOADING AND CLEANING

try:
    df_trader = pd.read_csv(TRADER_DATA_FILE)
    df_sentiment = pd.read_csv(SENTIMENT_DATA_FILE)
except FileNotFoundError as e:
    print(f"Error loading file: {e.filename}. Please ensure files are in the correct path.")
    exit()

# --- Sentiment Data Cleanup ---
# Standardizing column names (stripping whitespace and ensuring lowercase date/classification)
df_sentiment.columns = df_sentiment.columns.str.strip()
df_sentiment.rename(columns={'date': 'Trade_Date', 'classification': 'Classification'}, inplace=True)
df_sentiment['Trade_Date'] = pd.to_datetime(df_sentiment['Trade_Date']).dt.normalize()
df_sentiment = df_sentiment[['Trade_Date', 'Classification']]

# --- Trader Data Cleanup ---
df_trader.columns = df_trader.columns.str.strip()

# Convert time column using day-first format (DD-MM-YYYY) and normalize to day
df_trader['time_dt'] = pd.to_datetime(df_trader[COL_TIME], dayfirst=True)
df_trader['Trade_Date'] = df_trader['time_dt'].dt.normalize()

# Handle missing 'leverage' column (substituting 0.0 if not present)
if COL_LEVERAGE not in df_trader.columns:
    df_trader[COL_LEVERAGE] = 0.0

# Convert critical financial columns to numeric, setting errors to NaN
cols_to_numeric = ['Execution Price', 'Size USD', COL_PNL, COL_LEVERAGE]
for col in cols_to_numeric:
    if col in df_trader.columns:
        df_trader[col] = pd.to_numeric(df_trader[col], errors='coerce')

# Calculate profitability metric and remove transactions with missing PnL
df_trader['is_win'] = df_trader[COL_PNL] > 0
df_trader.dropna(subset=[COL_PNL], inplace=True)


# AGGREGATION AND MERGING

# Aggregate transactional data to daily performance per account
daily_performance = df_trader.groupby([COL_ACCOUNT, 'Trade_Date']).agg(
    Daily_PnL=(COL_PNL, 'sum'),
    Num_Trades=(COL_ACCOUNT, 'size'),
    Avg_Leverage=(COL_LEVERAGE, 'mean'),
    Num_Wins=('is_win', 'sum')
).reset_index()

daily_performance.rename(columns={COL_ACCOUNT: 'account'}, inplace=True)
daily_performance['Win_Rate'] = (daily_performance['Num_Wins'] / daily_performance['Num_Trades']) * 100

# Merge trading performance with sentiment data
merged_df = pd.merge(
    daily_performance,
    df_sentiment,
    on='Trade_Date',
    how='left'
)
merged_df.dropna(subset=['Classification'], inplace=True)

# CORE PERFORMANCE ANALYSIS

# Exit if no overlap is found
if len(merged_df) == 0:
    print("FATAL MERGE FAILURE: No overlapping dates found between the two datasets.")
    exit()

print("\n--- Overall Performance Metrics by Sentiment ---")

# A. Overall Performance Comparison
sentiment_analysis = merged_df.groupby('Classification').agg(
    Median_Daily_PnL=('Daily_PnL', 'median'),
    Mean_Daily_PnL=('Daily_PnL', 'mean'),
    Mean_Win_Rate=('Win_Rate', 'mean'),
    Avg_Leverage_Used=('Avg_Leverage', 'mean')
).reset_index()

print(sentiment_analysis.set_index('Classification').round(2))

# B. Contrarian vs. Herd Behavior Analysis
avg_pnl_by_account = merged_df.groupby('account')['Daily_PnL'].mean()
merged_df = merged_df.merge(avg_pnl_by_account.rename('Overall_Avg_PnL'), on='account')

sentiment_pivot = merged_df.pivot_table(
    index='account',
    columns='Classification',
    values='Daily_PnL',
    aggfunc='mean'
).dropna()

sentiment_pivot['PnL_Diff_Fear_Minus_Greed'] = sentiment_pivot.get('Fear', 0) - sentiment_pivot.get('Greed', 0)

# Top Contrarian Traders (Fear > Greed PnL)
top_contrarians = sentiment_pivot.sort_values(by='PnL_Diff_Fear_Minus_Greed', ascending=False).head(5)
print("\n--- Top 5 Contrarian Traders (Better in Fear) ---")
print(top_contrarians[['Fear', 'Greed', 'PnL_Diff_Fear_Minus_Greed']].round(2))

# Top Herd Traders (Greed > Fear PnL)
top_herd = sentiment_pivot.sort_values(by='PnL_Diff_Fear_Minus_Greed', ascending=True).head(5)
print("\n--- Top 5 Herd Traders (Worse in Fear) ---")
print(top_herd[['Fear', 'Greed', 'PnL_Diff_Fear_Minus_Greed']].round(2))


# VISUALIZATION

sns.set_style("whitegrid")
plt.figure(figsize=(14, 6))

full_palette = {
    'Extreme Fear': 'darkred',
    'Fear': 'firebrick',
    'Neutral': 'gray',
    'Greed': 'forestgreen',
    'Extreme Greed': 'darkgreen'
}

# --- Plot 1: Daily PnL Distribution ---
plt.subplot(1, 2, 1)
sns.boxplot(x='Classification', y='Daily_PnL', data=merged_df,
            palette=full_palette,
            showfliers=False)
plt.title('Daily PnL by Market Sentiment (Outliers Excluded)')
plt.xlabel('Market Sentiment')
plt.ylabel('Daily Closed PnL (USD)')

# --- Plot 2: Win Rate Distribution ---
plt.subplot(1, 2, 2)
sns.boxplot(x='Classification', y='Win_Rate', data=merged_df,
            palette=full_palette)
plt.title('Daily Win Rate (%) by Market Sentiment')
plt.xlabel('Market Sentiment')
plt.ylabel('Daily Win Rate (%)')

plt.tight_layout()
plt.show()

print("\nAnalysis complete. Tables and charts generated.")