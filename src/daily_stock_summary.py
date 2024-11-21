import os
import pandas as pd
import talib
from datetime import datetime
from typing import List

class DailyStockSummaryGenerator:
    def __init__(self, data_dir: str, output_directory: str) -> None:
        self.data_directory = data_dir
        self.output_directory = output_directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def generate_daily_summary(self, symbols: List[str], summary_date = None) -> None:
        daily_summary = []
        if summary_date:
            today = summary_date.strftime("%Y-%m-%d")
        else:
            today = datetime.now().strftime("%Y-%m-%d")
        for symbol in symbols:
            file_path = os.path.join(self.data_directory, f"{symbol}.csv")
            if not os.path.exists(file_path):
                print(f"Data file for {symbol} not found. Skipping...")
                continue

            stock_data = pd.read_csv(file_path, index_col="Date", parse_dates=["Date"])
            if stock_data.empty:
                print(f"No data for {symbol}. Skipping...")
                continue

            # Ensure the data is sorted by date
            stock_data.sort_index(ascending=True, inplace=True)

            # Get the latest available data
            try:
                latest_data = stock_data.loc[today]
            except KeyError:
                print(f"No data available for {symbol} on {today}. Skipping...")
                continue

            # Append the data to the list
            daily_summary.append(latest_data)

        # Create a DataFrame from the summary list
        summary_df = pd.DataFrame(daily_summary).set_index("ID")
        summary_df.fillna("N/A", inplace=True)


        # Save the summary to a CSV file
        output_file_path = os.path.join(self.output_directory, f"daily_stock_summary_{today}.xlsx")
        summary_df.to_excel(output_file_path, index=True)
        print(f"Daily stock summary saved to {output_file_path}")

