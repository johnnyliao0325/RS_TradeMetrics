import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class RSRateCalculator:
    def __init__(self, data_dir: str, output_directory: str) -> None:
        self.data_dir = data_dir
        self.output_directory = output_directory
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory {self.data_dir} not found.")

    def initialize_historical_rs_rate(self, stock_symbols: list, n_values: list) -> None:
        """
        Initialize the historical RS rate for all given stocks with different N values.
        """
        for symbol in stock_symbols:
            file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            if os.path.exists(file_path):
                stock_data = pd.read_csv(file_path, index_col='Date', parse_dates=['Date'])
                stock_data = self._calculate_historical_rs_rate(stock_data, n_values)
                stock_data.to_csv(file_path, encoding='utf-8-sig')
                print(f"Initialized RS rates for {symbol} successfully.")
            else:
                print(f"File for {symbol} not found. Skipping.")

    def update_daily_rs_rate(self, date: str, n_values: list) -> pd.DataFrame:
        """
        Calculate the RS rate for all stocks for a given date using different N values.
        """
        daily_summary_file = os.path.join(self.output_directory, f"daily_stock_summary_{date}.xlsx")
        if not os.path.exists(daily_summary_file):
            raise FileNotFoundError(f"Daily summary file for {date} not found.")

        # Load daily summary data
        daily_data = pd.read_excel(daily_summary_file, index_col='ID')
        for n in n_values:
            for ma_type in ['', 'E']:
                column_name = f'RS {n}{ma_type}MA'
                if column_name not in daily_data.columns:
                    print(f"Column '{column_name}' not found in daily data.")
                daily_data[f'{ma_type}RS_rank_{n}'] = daily_data[column_name].rank(ascending=True, method='min')
            
                # 使用排名來進行正規化
                scaler = MinMaxScaler(feature_range=(0, 100))
                daily_data[f'{ma_type}RS_rate_{n}'] = scaler.fit_transform(daily_data[[f'{ma_type}RS_rank_{n}']])
                
                # 刪除中間生成的 RS 排名列
                daily_data.drop(columns=[f'{ma_type}RS_rank_{n}'], inplace=True)
        daily_data = daily_data.fillna(0)
        # Save updated daily summary with RS rates
        output_file = os.path.join(self.output_directory, f"daily_stock_summary_{date}_with_rs_rate.xlsx")
        daily_data.to_excel(output_file, encoding='utf-8-sig')
        print(f"Daily RS rates for {date} calculated and saved successfully.")

        # update daily rs rate to every stock csv
        for symbol in daily_data.index:
            file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            if os.path.exists(file_path):
                stock_data = pd.read_csv(file_path, index_col='Date', parse_dates=['Date'])
                for n in n_values:
                    for ma_type in ['', 'E']:
                        column_name = f'RS {n}{ma_type}MA'
                        if column_name not in stock_data.columns:
                            print(f"Column '{column_name}' not found in stock data.")
                        stock_data.loc[date, f'{ma_type}RS_rate_{n}'] = daily_data.loc[symbol, f'{ma_type}RS_rate_{n}']
                stock_data.to_csv(file_path, encoding='utf-8-sig')
                print(f"Updated RS rates for {symbol} successfully.")
            else:
                print(f"File for {symbol} not found. Skipping.")

        return daily_data

    def _calculate_historical_rs_rate(self, stock_data: pd.DataFrame, n_values: list) -> pd.DataFrame:
        """
        Calculate RS rate for historical data of a single stock.
        """
        for n in n_values:
            for ma_type in ['', 'E']:
                column_name = f'RS {n}{ma_type}MA'
                if column_name not in stock_data.columns:
                    print(f"Column '{column_name}' not found in stock data for RS rate calculation.")
                scaler = MinMaxScaler(feature_range=(0, 100))
                stock_data[f'{ma_type}RS_rank_{n}'] = stock_data[column_name].rank(ascending=True, method='min')
            
                # 使用排名來進行正規化
                scaler = MinMaxScaler(feature_range=(0, 100))
                stock_data[f'{ma_type}RS_rate_{n}'] = scaler.fit_transform(stock_data[[f'{ma_type}RS_rank_{n}']])
                
                # 刪除中間生成的 RS 排名列
                stock_data.drop(columns=[f'{ma_type}RS_rank_{n}'], inplace=True)
        return stock_data

    def _calculate_daily_rs_rate(self, rs_values: pd.Series) -> pd.Series:
        """
        Calculate RS rate for a given day's RS values using MinMaxScaler.
        """
        scaler = MinMaxScaler(feature_range=(0, 100))
        rs_values_reshaped = rs_values.values.reshape(-1, 1)
        rs_rate = scaler.fit_transform(rs_values_reshaped).flatten()
        return rs_rate

# Example usage
if __name__ == "__main__":
    data_directory = "path_to_data"
    rs_calculator = RSRateCalculator(data_dir=data_directory)

    # Initialize historical RS rates
    stock_list = ["2330.TW", "2317.TW", "1101.TW"]
    n_list = [10, 20, 50, 100, 250]
    rs_calculator.initialize_historical_rs_rate(stock_symbols=stock_list, n_values=n_list)

    # Calculate daily RS rates for a specific date
    target_date = "2024-11-19"
    daily_rs_data = rs_calculator.calculate_daily_rs_rate(date=target_date, n_values=n_list)