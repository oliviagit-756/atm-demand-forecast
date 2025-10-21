import streamlit as st 
import pandas as pd
import plotly.express as px
import json
import numpy as np

# Import Prophet serialization utilities (you must have 'prophet' installed)
try:
    from prophet import Prophet
    from prophet.serialize import model_from_json
except ImportError:
    st.error("Prophet library not found. Please run: pip install prophet")
    # Define placeholder class/function if Prophet is not installed
    class Prophet: pass
    def model_from_json(x): return None

# --- Configuration Constants ---
ATM_TO_FORECAST = 'ATM_0007'
MODEL_FILE = 'prophet_model_atm_0044.json' # NOTE: File ATM ID (0044) does not match ATM_TO_FORECAST (0007)
STOCKING_THRESHOLD = 20000 
FORECAST_PERIOD = 7
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# --- A. Function to Load the Model ---
@st.cache_resource # Use this decorator to load the model only once
def load_trained_model(filename):
    """Loads the Prophet model from a JSON file."""
    try:
        with open(filename, 'r') as fin:
            model_json = json.load(fin)
        m = model_from_json(model_json)
        return m
    except FileNotFoundError:
        st.error(f"⚠️ Error: Model file '{filename}' not found. Please ensure your model is trained and saved as JSON.")
        st.info("Using mock data for demonstration purposes.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# --- B. Data Loading and Mocking Functions ---

def mock_load_data():
    """
    Creates mock daily_demand DataFrame (needed for the heatmap and plot history)
    *** You must replace this function with your actual data loading and aggregation code. ***
    """
    # Create mock daily_demand for the heatmap and historical plot
    start_date = pd.to_datetime('2023-01-01')
    dates = pd.date_range(start_date, periods=365, freq='D')
    atms = [f'ATM_00{i}' for i in range(1, 10)]
    
    mock_data = {
        'Date': np.tile(dates, len(atms)),
        'ATM_ID': np.repeat(atms, len(dates)),
        'y': np.random.randint(10000, 70000, size=len(dates) * len(atms))
    }
    daily_demand_mock = pd.DataFrame(mock_data)
    daily_demand_mock['Day_of_Week'] = daily_demand_mock['Date'].dt.day_name()
    
    return daily_demand_mock

def mock_predict(daily_demand_df):
    """Creates mock forecast data when the real model is unavailable."""
    atm_data_mock = daily_demand_df[daily_demand_df['ATM_ID'] == ATM_TO_FORECAST].copy()
    atm_data_mock = atm_data_mock.rename(columns={'Date': 'ds'})

    future_dates = pd.date_range(atm_data_mock['ds'].max() + pd.Timedelta(days=1), periods=FORECAST_PERIOD)
    forecast_mock_future = pd.DataFrame({
        'ds': future_dates,
        'yhat': np.random.randint(40000, 80000, size=FORECAST_PERIOD),
        'yhat_lower': np.random.randint(30000, 40000, size=FORECAST_PERIOD),
        'yhat_upper': np.random.randint(80000, 90000, size=FORECAST_PERIOD)
    })
    
    # Create full mock forecast (history + future) for the plot
    history = atm_data_mock.rename(columns={'ds': 'ds', 'y': 'yhat'})
    history['yhat_lower'] = history['yhat'] * 0.9 
    history['yhat_upper'] = history['yhat'] * 1.1 
    
    full_forecast_mock = pd.concat([history[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], forecast_mock_future], ignore_index=True)
    
    return full_forecast_mock


# =========================================================================
# === MAIN STREAMLIT APPLICATION LOGIC ======================================
# =========================================================================

# Load the trained model and the required data
m = load_trained_model(MODEL_FILE)
daily_demand = mock_load_data() # Load data (or mock data) needed for the heatmap

if m is not None:
    # --- Actual Prediction (If Model Exists) ---
    st.sidebar.success(f"✅ Prophet Model Loaded successfully from {MODEL_FILE}.")
    
    # 1. Create Future Dates (7 Days)
    future = m.make_future_dataframe(periods=FORECAST_PERIOD, freq='D', include_history=False)
    
    # 2. Add future regressors (Crucial: Must match training features)
    # If you added 'Holiday_Flag', 'is_Payday_Start', etc. as regressors, 
    # you MUST add these columns to the 'future' DataFrame, even if they are all 0.
    future['Holiday_Flag'] = 0 
    # Note: If your model used other regressors (Location_Type, etc.), 
    # you must add those columns to 'future' before prediction!
    
    # 3. Predict the future (7 days)
    forecast_future = m.predict(future)
    
    # 4. Generate the full forecast (history + future) for plotting
    full_future = m.make_future_dataframe(periods=FORECAST_PERIOD, freq='D')
    # Again, add regressors for full_future too
    full_future['Holiday_Flag'] = 0 
    full_forecast_df = m.predict(full_future)

else:
    # --- Mock Prediction (If Model is Missing) ---
    st.sidebar.warning("❌ Cannot generate real forecast. Showing mock data.")
    full_forecast_df = mock_predict(daily_demand)
    forecast_future = full_forecast_df.tail(FORECAST_PERIOD)

# --- Dashboard Layout ---
st.set_page_config(layout="wide")
st.title('💰 ATM Cash Demand Forecast Dashboard')
st.header(f'Predicted Demand for {ATM_TO_FORECAST}')

# Use Streamlit columns for cleaner layout
col1, col2 = st.columns([1, 2])

with col1:
    # Display the next 7 days prediction table
    forecast_table = forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(FORECAST_PERIOD)
    forecast_table.columns = ['Date', 'Predicted Demand ($)', 'Lower Bound', 'Upper Bound']
    st.subheader(f"{FORECAST_PERIOD}-Day Forecast (Next Stocking)")
    
    # Dataframe display
    st.dataframe(
        forecast_table.style.format({'Predicted Demand ($)': '${:,.0f}', 'Lower Bound': '${:,.0f}', 'Upper Bound': '${:,.0f}'}),
        hide_index=True,
        use_container_width=True
    )
    
    # CASH ALERT Logic
    max_pred = forecast_table['Predicted Demand ($)'].max()

    if max_pred > STOCKING_THRESHOLD:
        st.error(f"🚨 **CASH ALERT!** ATM {ATM_TO_FORECAST} is predicted to need a maximum of **${max_pred:,.0f}**. This exceeds the standard stocking threshold.")
    else:
        st.success(f"✅ Demand for ATM {ATM_TO_FORECAST} is within safe limits (Max ${max_pred:,.0f}).")
        
    st.markdown(f"*(Stocking Threshold: **${STOCKING_THRESHOLD:,.0f}**)*")

with col2:
    st.subheader("Historical Fit and 7-Day Forecast Trend")
    
    if m is not None:
        # Use Prophet's built-in plot if the real model is loaded
        fig = m.plot(full_forecast_df)
        st.pyplot(fig) 
    else:
        # Create a simple Plotly plot using mock data if the model failed to load
        fig_mock = px.line(full_forecast_df, x='ds', y='yhat', 
                           title=f'Historical (Mock) and Forecast Trend for {ATM_TO_FORECAST}')
        fig_mock.update_traces(name='Predicted Demand')
        fig_mock.add_scatter(x=full_forecast_df['ds'], y=full_forecast_df['yhat_lower'], 
                             fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', name='Lower Bound', showlegend=False)
        fig_mock.add_scatter(x=full_forecast_df['ds'], y=full_forecast_df['yhat_upper'], 
                             fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', name='Upper Bound', showlegend=False)
        st.plotly_chart(fig_mock, use_container_width=True)


# --- Heatmap Visualization (Fleet-wide Operational View) ---
st.markdown("---")
st.subheader("ATM Fleet Weekly Demand Heatmap (Operational View)")

# Calculate Weekly Average Demand across ALL ATMs
weekly_avg = daily_demand.groupby(['ATM_ID', 'Day_of_Week'])['y'].mean().reset_index()

# Define the order of days for the heatmap
weekly_avg['Day_of_Week'] = pd.Categorical(weekly_avg['Day_of_Week'], categories=DAY_ORDER, ordered=True)
weekly_avg = weekly_avg.sort_values('Day_of_Week')

heatmap_fig = px.density_heatmap(
    weekly_avg,
    x='Day_of_Week',
    y='ATM_ID',
    z='y',
    histfunc='avg',
    color_continuous_scale='Reds',
    title='Average Demand by Day and ATM',
    height=500
)
heatmap_fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':DAY_ORDER})
st.plotly_chart(heatmap_fig, use_container_width=True)
