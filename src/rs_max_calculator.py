import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from typing import List
import talib


class RSRateMaxMinUpdater:
    def __init__(self, data_dir: str, n_values: list, n_day_sort: list) -> None:
        self.data_directory = data_dir
        self.n_values = n_values
        self.n_day_sort = n_day_sort
        if not os.path.exists(self.data_directory):
            raise FileNotFoundError(f"Data directory {self.data_directory} not found.")

    def update_rs_rate_max_min(self, symbols: List[str]) -> None:
        """
        Update RS rate and ERS rate to check if they are the max or min in the recent N days.
        """
        MA_type_list = ['', 'E']
        for symbol in symbols:
            file_path = os.path.join(self.data_directory, f"{symbol}.csv")
            if not os.path.exists(file_path):
                print(f"Data file for {symbol} not found. Skipping...")
                continue
            stock_data = pd.read_csv(file_path, index_col="Date", parse_dates=["Date"])
            if stock_data.empty:
                print(f"No data for {symbol}. Skipping...")
                continue
            for n_day in self.n_day_sort:
                for n_MA in self.n_values:
                    for MA_type in MA_type_list:
                        column_name = f'{MA_type}RS_rate_{n_MA}'
                        if stock_data[column_name].empty:
                            
                            print(f"Column '{column_name}' has missing values in {symbol}. Skipping...")
                            continue
                        if column_name in stock_data.columns:
                            # 計算最近 N 天的最大值和最小值
                            try:
                                stock_data[f'RS {n_MA}{MA_type}MA {n_day}MAX'] = talib.MAX(stock_data[column_name], timeperiod=n_day)
                                stock_data[f'RS {n_MA}{MA_type}MA {n_day}MIN'] = talib.MIN(stock_data[column_name], timeperiod=n_day)
                                stock_data[f'RS {n_MA}{MA_type}MA is {n_day}MAX'] = stock_data[column_name].round(1) >= stock_data[f'RS {n_MA}{MA_type}MA {n_day}MAX'].round(1)
                                stock_data[f'RS {n_MA}{MA_type}MA is {n_day}MIN'] = stock_data[column_name].round(1) <= stock_data[f'RS {n_MA}{MA_type}MA {n_day}MIN'].round(1)
                            except Exception as e:
                                print(f"Error occurred when calculating max/min for {column_name} in {symbol}. Error: {e}")
                            
                        else:
                            print(f"Column '{column_name}' not found in {symbol}.")
            
            # 寫回原始的 CSV 文件
            stock_data.to_csv(file_path, encoding='utf-8-sig')
        
        print("RS rate max/min update completed successfully.")