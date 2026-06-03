import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="CSV Stock Analyzer", page_icon="📊")

if 'theme_color' not in st.session_state:
    st.session_state['theme_color'] = '#1f77b4'  # default blue

def set_color(color):
    st.session_state['theme_color'] = color

st.markdown(f"<h1 style='color:{st.session_state['theme_color']}'>📊 CSV-Based Stock Analyzer</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Please upload a CSV file (required)", type=["csv"])
    st.markdown("---")
    st.header("Theme")
    cols = st.columns(5)
    palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for c, col in enumerate(cols):
        with col:
            if st.button('', key=f'c{c}', on_click=set_color, args=(palette[c],)):
                pass
            # small colored box label
            st.markdown(f"<div style='background:{palette[c]};height:24px;border-radius:4px'></div>", unsafe_allow_html=True)
    st.markdown("---")
    pred_days = st.slider("Prediction Days", min_value=7, max_value=90, value=30)
    rsi_window = st.number_input("RSI Window", min_value=5, max_value=50, value=14)

st.info("This app analyzes only CSV data. Upload a CSV containing a date column and price column (e.g., Close).")

if uploaded_file is None:
    st.warning("Please upload a CSV to proceed. The app works only with uploaded CSV data.")
    st.stop()

# Read CSV
try:
    data = pd.read_csv(uploaded_file)
except Exception:
    st.error("Could not read the uploaded CSV. Ensure it's a valid CSV file.")
    st.stop()

# Detect date column
date_col_candidates = [c for c in data.columns if 'date' in c.lower()]
if date_col_candidates:
    date_col = date_col_candidates[0]
else:
    date_col = data.columns[0]

try:
    data[date_col] = pd.to_datetime(data[date_col])
    data = data.set_index(date_col).sort_index()
except Exception:
    st.error("Couldn't parse the date column. Please ensure your CSV has a parseable date column.")
    st.stop()

# Drop duplicate dates in index (common with messy CSVs)
if data.index.duplicated().any():
    data = data[~data.index.duplicated(keep='first')]

st.subheader("Uploaded Data Preview")
st.dataframe(data.head())

price_columns = list(data.columns)
if not price_columns:
    st.error("No columns found in CSV.")
    st.stop()

default_idx = price_columns.index('Close') if 'Close' in price_columns else 0
price_col = st.selectbox("Select Price Column", options=price_columns, index=default_idx)

price = data[price_col].dropna()
if price.empty:
    st.error("Selected price column contains no data.")
    st.stop()

# Chart options (depend on loaded data)
with st.sidebar:
    st.markdown("---")
    st.header("Chart Options")
    chart_opts = ["Line", "Area"]
    if all(col in data.columns for col in ["Open", "High", "Low", "Close"]):
        chart_opts.append("Candlestick")
    show_volume_default = True if 'Volume' in data.columns else False
    chart_type = st.selectbox("Chart Type", options=chart_opts, index=0)
    ma_windows = st.multiselect("Moving Averages (periods)", options=[5, 10, 20, 50, 100], default=[20, 50])
    show_bollinger = st.checkbox("Show Bollinger Bands")
    show_volume = st.checkbox("Show Volume", value=show_volume_default)
    show_returns_hist = st.checkbox("Show Returns Histogram")

# Ensure price index is unique to avoid reindex errors later
if price.index.duplicated().any():
    price = price[~price.index.duplicated(keep='first')]

# Layout
st.markdown("---")
col_main, col_side = st.columns([3, 1])

with col_main:
    # build charts, optionally with volume subplot
    if show_volume:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    else:
        fig = make_subplots(rows=1, cols=1)

    # Price chart type
    if chart_type == 'Candlestick' and all(c in data.columns for c in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlestick'), row=1, col=1)
    else:
        mode = 'lines'
        fill = 'tozeroy' if chart_type == 'Area' else None
        fig.add_trace(go.Scatter(x=price.index, y=price.values, name="Price", mode=mode, fill=fill, line=dict(color=st.session_state['theme_color'], width=2)), row=1, col=1)

    # Prediction
    data = data.loc[price.index]
    data['Days'] = np.arange(len(data))
    X = data[['Days']]
    y = data[price_col]

    if len(data) < 10:
        st.warning("Not enough rows for reliable prediction (need at least 10).")
    else:
        model = LinearRegression()
        model.fit(X, y)
        future_days = np.arange(len(data), len(data) + pred_days).reshape(-1, 1)
        prediction = model.predict(future_days)
        last_date = data.index[-1]
        future_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=pred_days, freq='B')
        future_series = pd.Series(prediction.flatten(), index=future_index)
        fig.add_trace(go.Scatter(x=future_series.index, y=future_series.values, name='Predicted', mode='lines', line=dict(color='rgba(0,0,0,0.2)', dash='dash')), row=1, col=1)

    # moving averages
    for ma in ma_windows:
        try:
            ma = int(ma)
            ma_series = price.rolling(ma).mean()
            fig.add_trace(go.Scatter(x=ma_series.index, y=ma_series.values, name=f'MA{ma}', mode='lines', line=dict(width=1)), row=1, col=1)
        except Exception:
            pass

    # Bollinger Bands
    if show_bollinger:
        m = price.rolling(20).mean()
        s = price.rolling(20).std()
        upper = m + (s * 2)
        lower = m - (s * 2)
        fig.add_trace(go.Scatter(x=upper.index, y=upper.values, name='Upper BB', line=dict(color='rgba(0,0,0,0.15)'), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=lower.index, y=lower.values, name='Lower BB', line=dict(color='rgba(0,0,0,0.15)'), fill='tonexty', fillcolor='rgba(0,0,0,0.05)', showlegend=False), row=1, col=1)

    # volume subplot
    if show_volume and 'Volume' in data.columns:
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='gray'), row=2, col=1)

    fig.update_layout(title=f"Price & {pred_days}-day Prediction", plot_bgcolor='white', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    st.plotly_chart(fig, use_container_width=True)

    # RSI subplot
    delta = price.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    window = int(rsi_window)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color=st.session_state['theme_color'])))
    rsi_fig.add_hline(y=70, line_dash='dash', line_color='red')
    rsi_fig.add_hline(y=30, line_dash='dash', line_color='green')
    rsi_fig.update_layout(title='RSI', plot_bgcolor='white')
    st.plotly_chart(rsi_fig, use_container_width=True)

    # Returns histogram
    if show_returns_hist:
        returns = price.pct_change().dropna()
        hist_fig = go.Figure()
        hist_fig.add_trace(go.Histogram(x=returns.values, nbinsx=50, marker_color=st.session_state['theme_color']))
        hist_fig.update_layout(title='Returns Distribution', xaxis_title='Daily Return', yaxis_title='Count', plot_bgcolor='white')
        st.plotly_chart(hist_fig, use_container_width=True)

with col_side:
    st.metric('Latest Price', f"{price.iloc[-1]:.2f}")
    latest_rsi = data['RSI'].iloc[-1]
    if pd.isna(latest_rsi):
        st.info(f"Not enough data to compute RSI (need {window} periods)")
    else:
        st.metric('Latest RSI', f"{latest_rsi:.2f}")
        if latest_rsi < 30:
            st.success('BUY')
        elif latest_rsi > 70:
            st.error('SELL')
        else:
            st.warning('HOLD')

    if 'future_series' in locals():
        predicted_end = future_series.iloc[-1]
        pct_change = (predicted_end - price.iloc[-1]) / price.iloc[-1] * 100
        st.metric(f"{pred_days}-day Predicted", f"{predicted_end:.2f}", f"{pct_change:.2f}%")

st.markdown("---")
st.subheader('Data Snapshot')
st.dataframe(data[[price_col, 'RSI']].tail(50))

st.caption('Theme colors change when you click a color box in the sidebar. All analysis is driven from the uploaded CSV.')





