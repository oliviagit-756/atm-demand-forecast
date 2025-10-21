# ATM Cash Demand Forecasting & Operational Simulator

This project uses the Prophet time series library to forecast cash withdrawal demand for a specific ATM (ATM_0044) and provides an interactive Streamlit dashboard that allows bank operations managers to simulate stocking strategies based on their chosen risk tolerance.

## Key Features

Prophet Forecasting: Models daily cash demand using historical data, holidays, and engineered features (Payday indicators, Location Type).

Operational Risk Simulator (Unique Feature): A Streamlit sidebar slider allows users to adjust their risk tolerance:

Low Risk: Stocks up to the yhat_upper bound (maximizing coverage, minimizing stockout risk).

High Risk: Stocks close to the yhat_lower bound (minimizing cash holding costs).

Cost Metrics: Calculates estimated Holding Cost and Stockout Risk Cost based on the chosen stocking strategy.

Fleet-Wide Heatmap: Provides a strategic overview of average demand across the entire ATM fleet by day of the week.

Setup and Installation

1. Clone the repository

git clone <your-repo-link>
cd <your-repo-name>


2. Install Dependencies

You must have Python installed. Use the provided requirements.txt file to install all necessary libraries:

pip install -r requirements.txt


3. Data File (Placeholder)

This project assumes your aggregated, clean data is available as atm_data.csv in the root directory.
