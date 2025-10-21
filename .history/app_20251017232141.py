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
# Use Prophet's built-in plot for a quick visualization of historical vs. forecast
fig = m.plot(forecast)
st.subheader("Historical Fit and 7-Day Forecast")
st.pyplot(fig) # Use st.pyplot for matplotlib/Prophet plots
# Calculate Weekly Average Demand across ALL ATMs
daily_demand['Day_of_Week'] = daily_demand['Date'].dt.day_name()
weekly_avg = daily_demand.groupby(['ATM_ID', 'Day_of_Week'])['y'].mean().reset_index()

# Define the order of days for the heatmap
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_avg['Day_of_Week'] = pd.Categorical(weekly_avg['Day_of_Week'], categories=day_order, ordered=True)
weekly_avg = weekly_avg.sort_values('Day_of_Week')

st.subheader("ATM Fleet Weekly Demand Heatmap (Operational View)")
heatmap_fig = px.density_heatmap(
    weekly_avg,
    x='Day_of_Week',
    y='ATM_ID',
    z='y',
    histfunc='avg',
    color_continuous_scale='Reds',
    title='Average Demand by Day and ATM'
)
st.plotly_chart(heatmap_fig)
# Define a stocking threshold (e.g., 20,000 currency units)
STOCKING_THRESHOLD = 20000

# Check the max predicted demand for the next 7 days
max_pred = forecast_table['Predicted Demand ($)'].max()

if max_pred > STOCKING_THRESHOLD:
    st.error(f"🚨 **CASH ALERT!** ATM {ATM_TO_FORECAST} is predicted to need a maximum of **${max_pred:,.0f}**. This exceeds the standard stocking threshold of ${STOCKING_THRESHOLD:,.0f}.")
else:
    st.success(f"✅ Demand for ATM {ATM_TO_FORECAST} is within safe limits.")