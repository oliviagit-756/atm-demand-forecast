import streamlit as st
import pandas as pd
import json
from prophet.serialize import model_from_json
from prophet import Prophet 

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
        st.error(f"Error: Model file '{filename}' not found. Please ensure your model is trained and saved.")
        return None

# --- B. Load Model and Run Streamlit App ---
MODEL_FILE = 'prophet_model_atm_0044.json'
ATM_TO_FORECAST = 'ATM_0044' # Keep this consistent

# Load the model
m = load_trained_model(MODEL_FILE)

if m is not None:
    st.title('💰 ATM Cash Demand Forecast Dashboard')
    st.header(f'Predicted Demand for {ATM_TO_FORECAST}')

    # 1. Create Future Dates (7 Days)
    future = m.make_future_dataframe(periods=7, freq='D', include_history=False)
    
    # 2. Add future regressors (Crucial: Must match training features)
    # If you added 'Holiday_Flag', 'is_Payday_Start', etc. as regressors, 
    # you MUST add these columns to the 'future' DataFrame, even if they are all 0.
    future['Holiday_Flag'] = 0 
    # ... add other regressor columns here ...

    # 3. Predict and Display (Use the Streamlit code from the previous response)
    forecast = m.predict(future)
    
    # ... (Your Streamlit visualization code goes here) ...