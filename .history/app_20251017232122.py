import streamlit as st 
import plotly.express as px
st.set_page_config(layout = "wide")
st.title(' ATM CASH DEMAND FORECAST DASHBOARD')
st.header(f'Predicted Demand for {ATM_TO_FORECAST}')
# Display the next 7 days prediction
forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)
forecast_table.columns = ['Date', 'Predicted Demand ($)', 'Lower Bound', 'Upper Bound']
st.dataframe(
    forecast_table.style.format({'Predicted Demand ($)': '${:,.0f}'}),
    hide_index=True
)