import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import talib
from datetime import datetime
from typing import List

class RSRateManager:
    def __init__(self, data_dir: str, output_directory: str, n_values: list, n_day_sort: list) -> None:
        self.data_dir = data_dir
        self.output_directory = output_directory
        self.n_values = n_values
        self.n_day_sort = n_day_sort
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory {self.data_dir} not found.")

    def _load_daily_summary(self, date: str) -> pd.DataFrame:
        summary_file = os.path.join(self.output_directory, f"daily_stock_summary_{date}.xlsx")
        if not os.path.exists(summary_file):
            raise FileNotFoundError(f"Daily summary file for {date} not found.")
        return pd.read_excel(summary_file, index_col='ID')

    def calculate_daily_rs_rate(self, summary_data: pd.DataFrame) -> pd.DataFrame:
        for n in self.n_values:
            for ma_type in ['', 'E']:
                column_name = f'RS {n}{ma_type}MA'
                if column_name not in summary_data.columns:
                    print(f"Column '{column_name}' not found in daily data.")
                    continue
                summary_data[f'{ma_type}RS_rank_{n}'] = summary_data[column_name].rank(ascending=True, method='min')
                
                # Normalize using MinMaxScaler
                scaler = MinMaxScaler(feature_range=(0, 100))
                summary_data[f'{ma_type}RS_rate_{n}'] = scaler.fit_transform(summary_data[[f'{ma_type}RS_rank_{n}']])
                summary_data.drop(columns=[f'{ma_type}RS_rank_{n}'], inplace=True)
        summary_data.fillna(0, inplace=True)
        return summary_data

    def update_daily_rs_rate_and_max_min(self, date: datetime, symbols: List[str]) -> None:


        # Step 1: Load the daily summary data
        summary_data = self._load_daily_summary(date)

        # Step 2: Calculate the daily RS rate
        summary_data = self.calculate_daily_rs_rate(summary_data)

        # Step 3: Iterate through each symbol and update both RS rate and max/min
        MA_type_list = ['', 'E']
        maxmin_columns = []
        for n_day in self.n_day_sort:
            for n_MA in self.n_values:
                for MA_type in MA_type_list:
                    maxmin_columns.append(f'RS {n_MA}{MA_type}MA {n_day}MAX')
                    maxmin_columns.append(f'RS {n_MA}{MA_type}MA {n_day}MIN')
                    maxmin_columns.append(f'RS {n_MA}{MA_type}MA is {n_day}MAX')
                    maxmin_columns.append(f'RS {n_MA}{MA_type}MA is {n_day}MIN')
        summary_data[maxmin_columns] = 0
        date = date.strftime('%Y-%m-%d')
        for symbol in symbols:
            file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            if not os.path.exists(file_path):
                print(f"Data file for {symbol} not found. Skipping...")
                continue

            # Step 3: Load stock data
            stock_data = pd.read_csv(file_path, index_col="Date", parse_dates=["Date"])
            original_index = stock_data.index
            stock_data.index = list(map(lambda x: x.strftime('%Y-%m-%d'), original_index))
            
            if stock_data.empty:
                print(f"No data for {symbol}. Skipping...")
                continue

            # Step 4: Update RS rate for the specific symbol
            for n in self.n_values:
                for ma_type in ['', 'E']:
                    column_name = f'RS {n}{ma_type}MA'
                    rs_rate_column = f'{ma_type}RS_rate_{n}'
                    if column_name in stock_data.columns and rs_rate_column in summary_data.columns and symbol in summary_data.index:
                        stock_data.loc[date, rs_rate_column] = summary_data.loc[symbol, rs_rate_column]
            print(f"Updated {rs_rate_column} for {symbol} on {date}")

            # Step 5: Update RS max/min values
            for n_day in self.n_day_sort:
                for n_MA in self.n_values:
                    for MA_type in MA_type_list:
                        column_name = f'{MA_type}RS_rate_{n_MA}'
                        if column_name in stock_data.columns:
                            try:
                                stock_data[f'RS {n_MA}{MA_type}MA {n_day}MAX'] = talib.MAX(stock_data[column_name], timeperiod=n_day)
                                stock_data[f'RS {n_MA}{MA_type}MA {n_day}MIN'] = talib.MIN(stock_data[column_name], timeperiod=n_day)
                                stock_data[f'RS {n_MA}{MA_type}MA is {n_day}MAX'] = stock_data[column_name].round(1) >= stock_data[f'RS {n_MA}{MA_type}MA {n_day}MAX'].round(1)
                                stock_data[f'RS {n_MA}{MA_type}MA is {n_day}MIN'] = stock_data[column_name].round(1) <= stock_data[f'RS {n_MA}{MA_type}MA {n_day}MIN'].round(1)
                            except Exception as e:
                                print(f"Error occurred when calculating max/min for {column_name} in {symbol}. Error: {e}")

            # Step 6: Update the summary data for the current symbol
            try:
                summary_data.loc[symbol, maxmin_columns] = stock_data.loc[date, maxmin_columns]
            except KeyError:
                print(f"No data available for {symbol} on {date}. Skipping...")

            # Step 7: Save updated stock data
            stock_data.index = original_index
            stock_data.to_csv(file_path, encoding='utf-8-sig', index=True)


        # Step 8: Save updated summary data
        summary_data.to_excel(os.path.join(self.output_directory, f"daily_stock_summary_{date}_with_rs_rate_and_maxmin.xlsx"), index=True)
        print("RS rate and max/min update completed successfully.")

# Example usage
if __name__ == "__main__":
    data_directory = "path_to_data"
    output_directory = "path_to_output"
    n_values = [10, 20, 50, 100, 250]
    n_day_sort = [10, 20, 50, 250]
    rs_manager = RSRateManager(data_dir=data_directory, output_directory=output_directory, n_values=n_values, n_day_sort=n_day_sort)

    # Update RS rates and max/min values for a specific date
    target_date = "2024-11-19"
    symbols_list = ["2330.TW", "2317.TW", "1101.TW"]
    rs_manager.update_daily_rs_rate_and_max_min(date=target_date, symbols=symbols_list)
