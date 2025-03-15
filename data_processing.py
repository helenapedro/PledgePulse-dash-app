# data_processing.py
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def load_and_preprocess_data(pledges_path, payments_path):
    try:
        # Load JSON data directly from URLs
        pledges_df = pd.read_json(pledges_path)
        payments_df = pd.read_json(payments_path)

        print("Pledges DataFrame Columns:", pledges_df.columns)
        print("Payments DataFrame Columns:", payments_df.columns)

        # Determine the appropriate 'pledge_date' column
        if 'pledge_created_at' in pledges_df.columns:
            pledge_date_column = 'pledge_created_at'
        elif 'pledge_starts_at' in pledges_df.columns:
            pledge_date_column = 'pledge_starts_at'
        elif 'pledge_ended_at' in pledges_df.columns:
            pledge_date_column = 'pledge_ended_at'
        else:
            raise ValueError("No suitable pledge date column found (pledge_created_at, pledge_starts_at, or pledge_ended_at)")

        # Rename the selected column to 'pledge_date'
        pledges_df.rename(columns={pledge_date_column: 'pledge_date'}, inplace=True)

        # **Create 'year' column here**
        pledges_df['year'] = pledges_df['pledge_date'].dt.year

        # Validate columns
        required_columns = ['pledge_id', 'pledge_date', 'contribution_amount', 'year']  # Added 'year'
        for col in required_columns:
            if col not in pledges_df.columns:
                raise ValueError(f"Missing column in pledges dataset: {col}")


        # --- Data Cleaning and Type Conversions ---
        # Convert pledge_date and payment_date to datetime
        pledges_df['pledge_date'] = pd.to_datetime(pledges_df['pledge_date'], errors='coerce')

        # Attempt to convert payment_platform to string before datetime conversion
        payments_df['date'] = payments_df['date'].astype(str)
        payments_df['date'] = pd.to_datetime(payments_df['date'], errors='coerce')

        # Convert pledge and payment amounts to numeric
        pledges_df['contribution_amount'] = pd.to_numeric(pledges_df['contribution_amount'], errors='coerce')
        payments_df['amount'] = pd.to_numeric(payments_df['amount'], errors='coerce')

        # Drop rows with missing critical data
        pledges_df.dropna(subset=['pledge_id'], inplace=True)
        payments_df.dropna(subset=['pledge_id'], inplace=True)

        # Ensure 'pledge_id' has consistent data type
        pledges_df['pledge_id'] = pledges_df['pledge_id'].astype(str)
        payments_df['pledge_id'] = payments_df['pledge_id'].astype(str)

        # --- Data Joining ---
        # Perform a left join to keep all pledges
        combined_df = pd.merge(
            pledges_df,
            payments_df,
            left_on='pledge_id',   #specify the column for merging in both df
            right_on = 'pledge_id',
            how='left',
            suffixes=('_pledge', '_payment')
        )

        # **Print the columns of the merged DataFrame**
        print("Combined DataFrame Columns:", combined_df.columns)  # ADDED

        if 'amount' not in combined_df.columns:  # Changed to 'amount'
            raise ValueError("Could not find 'amount' column after merge. Check merge operation.")


        combined_df.payment_amount_column = 'amount' #changed to 'amount'
        return combined_df

    except Exception as e:
        print(f"An error occurred while processing data: {e}")
        raise


def create_visualizations(df):
    figures = {}

    # 1. Pledge Trend Over Time
    pledges_over_time = df.groupby(df['pledge_date'].dt.to_period('M'))['contribution_amount'].sum().reset_index()
    pledges_over_time['pledge_date'] = pledges_over_time['pledge_date'].dt.to_timestamp()  # Convert period to timestamp
    fig_pledge_trend = px.line(pledges_over_time, x='pledge_date', y='contribution_amount',
                                title='Pledge Amount Trend Over Time')
    figures['pledge_trend'] = fig_pledge_trend

    # 2. Pledge Amount Distribution
    fig_pledge_dist = px.histogram(df, x='contribution_amount', title='Pledge Amount Distribution')
    figures['pledge_distribution'] = fig_pledge_dist

    # 3. Pledge Fulfillment Rate Over Time
    # Group by month and calculate pledge and payment sums
    monthly_data = df.groupby(df['pledge_date'].dt.to_period('M')).agg({
        'contribution_amount': 'sum',
        'amount': 'sum' #Changed to 'amount'
    }).reset_index()
    monthly_data['pledge_date'] = monthly_data['pledge_date'].dt.to_timestamp()
    monthly_data['fulfillment_rate'] = (monthly_data['amount'] / monthly_data['contribution_amount']) * 100 #Changed to 'amount'

    fig_fulfillment_rate = px.line(monthly_data, x='pledge_date', y='fulfillment_rate',
                                 title='Pledge Fulfillment Rate Over Time')
    figures['fulfillment_rate'] = fig_fulfillment_rate

    # 4. Pledge vs. Payment Scatter Plot
    fig_pledge_payment_scatter = px.scatter(df, x='contribution_amount', y='amount', #Changed to 'amount'
                                           title='Pledge Amount vs. Payment Amount',
                                           hover_data=['pledge_id'])  # add pledge_id to the hover data
    figures['pledge_payment_scatter'] = fig_pledge_payment_scatter

    # 5. Breakdown by Year
    df['year'] = df['pledge_date'].dt.year
    year_data = df.groupby('year')['contribution_amount'].sum().reset_index()
    fig_breakdown_year = px.bar(year_data, x='year', y='contribution_amount', title='Pledges by Year')
    figures['by_year'] = fig_breakdown_year

    # 6. Use Subplots for comparing metrics
    fig_subplots = make_subplots(rows=2, cols=2, subplot_titles=('Pledge Trend', 'Pledge Amount Distribution', 'Fulfillment Rate', 'Pledge vs Payment'))
    fig_subplots.add_trace(fig_pledge_trend['data'][0], row=1, col=1)
    fig_subplots.add_trace(fig_pledge_dist['data'][0], row=1, col=2)
    fig_subplots.add_trace(fig_fulfillment_rate['data'][0], row=2, col=1)
    fig_subplots.add_trace(fig_pledge_payment_scatter['data'][0], row=2, col=2)
    fig_subplots.update_layout(title_text="Combined Metrics")
    figures['subplots'] = fig_subplots

    return figures


if __name__ == '__main__':
    pledges_url = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-pledges.json'
    payments_url = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-payments.json'

    try:
        df = load_and_preprocess_data(pledges_url, payments_url)
        print("Data loaded and preprocessed successfully.")
        print(df.head())  # Display the first few rows of the combined DataFrame
    except Exception as e:
        print(f"Error: {e}")