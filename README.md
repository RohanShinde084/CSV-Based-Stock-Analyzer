# CSV-Based-Stock-Analyzer

> A Streamlit dashboard for fast CSV-based stock analysis, visualization, and simple trend prediction.

## 🚀 Overview

`CSV-Based-Stock-Analyzer` is a lightweight data-driven stock analysis app built with Streamlit. It transforms your stock CSV files into interactive charts, indicators, and prediction visualizations so you can explore price action, momentum, and trend signals with ease.

## ✨ Key Features

- Upload any stock CSV file with a date column and price data
- Interactive price chart with:
  - Line, area, and candlestick charting
  - Moving averages (5, 10, 20, 50, 100)
  - Optional Bollinger Bands
  - Volume overlay when available
- Built-in RSI indicator with buy/hold/sell signal guidance
- Returns distribution histogram for volatility insight
- Linear regression-based price prediction for a future horizon
- Theme color selection for a personalized dashboard style

## 📁 Supported Data Format

The app works best with a CSV file containing:

- A date column (`Date`, `date`, or similar)
- One or more price columns such as `Close`, `Open`, `High`, `Low`
- Optional `Volume` column for volume display

### Recommended CSV columns

- `Date` / `date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

## 🧠 What the App Does

1. Reads and validates the uploaded CSV file
2. Detects the date column automatically
3. Builds an interactive chart for the selected price series
4. Computes technical indicators:
   - Moving averages
   - Bollinger Bands
   - RSI (Relative Strength Index)
5. Displays summary metrics such as latest price and RSI signal
6. Generates a future price projection using linear regression

## 💻 Installation

Install Python dependencies before running the app:

```bash
pip install streamlit pandas plotly scikit-learn numpy
```

## ▶️ Run the App

Launch the dashboard with:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## 🧩 How to Use

1. Open the app in your browser after starting Streamlit
2. Upload your stock CSV in the sidebar
3. Choose the price column to analyze
4. Select the chart type and enable options like volume and Bollinger Bands
5. Adjust prediction horizon and RSI window
6. Review the dashboard metrics and charts

## 📊 Built-In Dashboard Sections

- **Uploaded Data Preview**: Quick look at the imported CSV rows
- **Price Chart**: Visual representation of the selected price series
- **Prediction Line**: Linear regression forecast for the selected horizon
- **RSI Panel**: Momentum indicator with support/resistance levels
- **Returns Histogram**: Distribution of daily returns
- **Data Snapshot**: Recent values and RSI history

## 🛠️ Customization

- Change the app theme color using sidebar buttons
- Adjust prediction days from 7 to 90
- Tune RSI calculation window from 5 to 50 periods
- Use different moving average periods for trend analysis

## 📌 Notes

- The app only analyzes data from uploaded CSV files
- Ensure your CSV dates are parseable by pandas
- Prediction is a simple linear trend model and should not be used as financial advice

## 📂 Project Files

- `app.py` — main Streamlit dashboard implementation
- `README.md` — project documentation

## 🌟 Future Improvements

- Add more technical indicators (MACD, SMA crossover, ATR)
- Support multiple stocks / OHLC resampling
- Add download/export for charts and analysis results
- Improve prediction using advanced time-series models

---

Built with Streamlit, Plotly, pandas, NumPy, and scikit-learn.